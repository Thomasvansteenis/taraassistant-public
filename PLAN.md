# Plan: Home Assistant Add-on for Tara Assistant

## Overview

Convert the existing Tara Assistant Docker application into a Home Assistant add-on that can be installed directly from a custom add-on repository. The add-on will integrate natively with HA's Supervisor API (auto-discovering the HA URL and token), present its UI via Ingress (embedded in the HA sidebar), and expose configuration through the HA add-on options UI.

## Architecture Decisions

### Add-on structure: Subdirectory inside this repo
Create a `homeassistant-addon/tara-assistant/` directory containing all add-on files. This keeps the add-on alongside the main project and allows the repo to double as an add-on repository (HA Supervisor recursively searches for `config.yaml`).

### Base image: HA Alpine base (`ghcr.io/home-assistant/{arch}-base`)
Use the official HA base images via `build.yaml` + `ARG BUILD_FROM`. This gives us bashio, S6, and proper labeling out of the box. Alpine is lighter than Debian slim. Python 3.11+ will be installed via `apk`.

### Init system: `init: false` (simple CMD)
Tara Assistant runs a single process (uvicorn). No need for S6 process supervision. A simple `run.sh` entrypoint is sufficient.

### HA connection: Auto-discovery via Supervisor API
Set `homeassistant_api: true` in `config.yaml`. Use `SUPERVISOR_TOKEN` env var and `http://supervisor/core` as the HA URL. Users never need to paste a token or URL.

### UI access: Ingress (primary) + optional direct port
Enable Ingress so the UI appears in the HA sidebar. Also expose port 8000 as `null` (disabled by default) for users who want direct access.

### Configuration: HA options UI replaces setup wizard
AI provider settings (API keys, model names, thresholds) are configured through the HA add-on Configuration tab. The existing setup wizard is bypassed when running as an add-on since HA connection is auto-discovered and other settings come from `/data/options.json`.

### Data persistence: `/data` directory
All persistent data (pattern DB, entity cache, encrypted config) goes to `/data`, which HA automatically persists across restarts and upgrades.

---

## Implementation Steps

### Step 1: Create add-on repository structure

Create the directory layout:

```
homeassistant-addon/
  repository.yaml
  tara-assistant/
    config.yaml
    Dockerfile
    build.yaml
    run.sh
    DOCS.md
    CHANGELOG.md
    translations/
      en.yaml
```

Also add `repository.yaml` at the repo root (HA needs this to recognize the repo as an add-on repository).

**Files to create:**

- **`repository.yaml`** (repo root): Repository metadata (name, URL, maintainer)
- **`homeassistant-addon/tara-assistant/config.yaml`**: Add-on metadata with:
  - `name`, `version`, `slug`, `description`, `arch` (amd64, aarch64, armv7)
  - `homeassistant_api: true` for Supervisor token access
  - `ingress: true`, `ingress_port: 8000`, `panel_icon: mdi:robot`
  - `options` + `schema` for AI provider config (provider selection, API keys, models, thresholds)
  - `ports: {"8000/tcp": null}` (optional direct access, disabled by default)
  - `map: ["share:rw"]` for optional shared data
  - `watchdog` pointing to the health endpoint via Ingress

### Step 2: Create the add-on Dockerfile

**File: `homeassistant-addon/tara-assistant/Dockerfile`**

- `ARG BUILD_FROM` / `FROM $BUILD_FROM` (Alpine-based HA image)
- Install Python 3.11, pip, and system deps (`apk add python3 py3-pip curl`)
- Copy and install `requirements.txt`
- Copy `app/` and `scripts.yaml`
- Copy `run.sh` as entrypoint
- `CMD ["/run.sh"]`

### Step 3: Create `build.yaml` for multi-arch support

**File: `homeassistant-addon/tara-assistant/build.yaml`**

Map architectures to HA base images:
- `amd64`: `ghcr.io/home-assistant/amd64-base-python:3.11`
- `aarch64`: `ghcr.io/home-assistant/aarch64-base-python:3.11`
- `armv7`: `ghcr.io/home-assistant/armv7-base-python:3.11`

### Step 4: Create `run.sh` entrypoint

**File: `homeassistant-addon/tara-assistant/run.sh`**

This script:
1. Reads config from `/data/options.json` (via bashio or direct JSON)
2. Sets environment variables for the app (`AI_PROVIDER`, API keys, models, etc.)
3. Auto-discovers HA connection: `HA_URL=http://supervisor/core`, `HA_TOKEN=$SUPERVISOR_TOKEN`
4. Creates `/data/app_data` if needed and symlinks `/app/data` -> `/data/app_data` for persistence
5. Handles Ingress path: reads `INGRESS_ENTRY` or sets a default
6. Starts uvicorn on port 8000

### Step 5: Modify `app/config.py` to support add-on mode

**File to modify: `app/config.py`**

Add add-on awareness:
- Detect add-on mode by checking for `SUPERVISOR_TOKEN` env var
- When in add-on mode, read settings from environment variables (set by `run.sh` from options.json) rather than encrypted storage
- `ha_url` defaults to `http://supervisor/core` when `SUPERVISOR_TOKEN` is present
- `ha_token` defaults to `SUPERVISOR_TOKEN` value

This is a small change: in `get_settings()`, add a check before the encrypted storage path. If `SUPERVISOR_TOKEN` is set, load from env vars directly (which `run.sh` will have populated).

### Step 6: Modify `app/main.py` for Ingress compatibility

**File to modify: `app/main.py`**

- Read `INGRESS_PATH` or `X-Ingress-Path` header to set FastAPI's `root_path`
- Add middleware that reads `X-Ingress-Path` from each request and ensures URLs in HTML responses work correctly
- Ensure all static asset paths and API calls in the served HTML use relative URLs (audit the HTML templates in `app/main.py` and `app/setup/templates.py`)

### Step 7: Modify `app/middleware/setup_redirect.py` to skip in add-on mode

**File to modify: `app/middleware/setup_redirect.py`**

When running as an add-on (detected via `SUPERVISOR_TOKEN`), the setup wizard redirect should be bypassed since configuration comes from the HA options UI. The `is_configured()` check should return `True` when add-on env vars are properly set.

This is handled naturally if Step 5 is done correctly -- `is_configured()` calls `ConfigStorage.exists()`, but we should also make `is_configured()` return `True` when `SUPERVISOR_TOKEN` is present and required config (ai_provider + corresponding API key) is set via env vars.

### Step 8: Create translations file

**File: `homeassistant-addon/tara-assistant/translations/en.yaml`**

Provide human-readable labels and descriptions for all configuration options so they display nicely in the HA UI.

### Step 9: Create documentation

**File: `homeassistant-addon/tara-assistant/DOCS.md`**

Brief documentation covering:
- What Tara Assistant does
- How to add the repository to HA
- How to configure AI provider settings
- How Ingress works (click "Open Web UI")

**File: `homeassistant-addon/tara-assistant/CHANGELOG.md`**

Initial changelog entry.

### Step 10: Update `app/setup/storage.py` data path for add-on mode

**File to modify: `app/setup/storage.py`**

The `CONFIG_DIR` is hardcoded to `Path("data")` (relative). In add-on mode, persistent storage is at `/data`. Add a check: if `SUPERVISOR_TOKEN` is set, use `/data/app_data` as the config directory instead of the relative `data` path. This ensures the encrypted config (if still used as a fallback) persists across container rebuilds.

Similarly update `app/patterns/database.py` if it has a hardcoded DB path.

### Step 11: Audit HTML templates for relative URLs

**Files to audit: `app/main.py` (inline HTML), `app/setup/templates.py`**

Ensure all `<link>`, `<script>`, `<a>`, `<form>`, and `fetch()` calls use relative paths (no leading `/` without the Ingress base path). This is critical for Ingress to work. If absolute paths are used, prepend the `X-Ingress-Path` value or switch to relative URLs.

---

## Files Summary

### New files to create:
| File | Purpose |
|------|---------|
| `repository.yaml` (repo root) | HA add-on repository metadata |
| `homeassistant-addon/tara-assistant/config.yaml` | Add-on configuration & schema |
| `homeassistant-addon/tara-assistant/Dockerfile` | Add-on container build |
| `homeassistant-addon/tara-assistant/build.yaml` | Multi-arch base image mapping |
| `homeassistant-addon/tara-assistant/run.sh` | Entrypoint script |
| `homeassistant-addon/tara-assistant/translations/en.yaml` | UI labels/descriptions |
| `homeassistant-addon/tara-assistant/DOCS.md` | User documentation |
| `homeassistant-addon/tara-assistant/CHANGELOG.md` | Version history |

### Existing files to modify:
| File | Change |
|------|--------|
| `app/config.py` | Add add-on mode detection (SUPERVISOR_TOKEN), load from env vars |
| `app/main.py` | Add Ingress path support (root_path / middleware) |
| `app/middleware/setup_redirect.py` | Bypass setup wizard in add-on mode |
| `app/setup/storage.py` | Use `/data/app_data` path in add-on mode |
| `app/patterns/database.py` | Use persistent `/data` path in add-on mode |

---

## Risk Assessment

- **Ingress path rewriting**: The biggest technical challenge. The app serves HTML with inline `fetch()` calls and form actions. All must use relative URLs or respect the Ingress base path. Requires careful auditing of `app/main.py` (~2700 lines) and `app/setup/templates.py` (~65k lines).
- **Encryption key stability**: The `EncryptionManager` derives keys from MAC address + hostname. In a Docker container, these are stable across restarts but change on container recreation. Since add-on mode primarily reads config from env vars (not encrypted storage), this is low risk.
- **Alpine vs Debian dependencies**: The existing app uses `python:3.11-slim` (Debian). Moving to Alpine may require adjusting some pip installs (e.g., compiling `cryptography` from source or using Alpine packages). The HA Python base images should handle this.
