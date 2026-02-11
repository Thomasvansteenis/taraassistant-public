#!/usr/bin/env bash
set -eo pipefail

# ------------------------------------------------------------------
# Logging helpers
# ------------------------------------------------------------------
log_info()  { echo "[$(date '+%H:%M:%S')] INFO: $*"; }
log_error() { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; }

log_info "Starting Tara Assistant add-on..."

# ------------------------------------------------------------------
# Read configuration from /data/options.json
# (always mounted by the Supervisor, no API token needed)
# ------------------------------------------------------------------
OPTIONS="/data/options.json"
if [ ! -f "${OPTIONS}" ]; then
    log_error "Options file not found at ${OPTIONS}"
    exit 1
fi

export AI_PROVIDER=$(jq -r '.ai_provider // "openai"' "${OPTIONS}")
export OPENAI_API_KEY=$(jq -r '.openai_api_key // ""' "${OPTIONS}")
export OPENAI_MODEL=$(jq -r '.openai_model // "gpt-4o"' "${OPTIONS}")
export ANTHROPIC_API_KEY=$(jq -r '.anthropic_api_key // ""' "${OPTIONS}")
export ANTHROPIC_MODEL=$(jq -r '.anthropic_model // ""' "${OPTIONS}")
export OLLAMA_HOST=$(jq -r '.ollama_host // ""' "${OPTIONS}")
export OLLAMA_MODEL=$(jq -r '.ollama_model // "llama3.1"' "${OPTIONS}")
export GOOGLE_API_KEY=$(jq -r '.google_api_key // ""' "${OPTIONS}")
export GOOGLE_MODEL=$(jq -r '.google_model // ""' "${OPTIONS}")
export OPENAI_COMPATIBLE_HOST=$(jq -r '.openai_compatible_host // ""' "${OPTIONS}")
export OPENAI_COMPATIBLE_API_KEY=$(jq -r '.openai_compatible_api_key // ""' "${OPTIONS}")
export OPENAI_COMPATIBLE_MODEL=$(jq -r '.openai_compatible_model // ""' "${OPTIONS}")
export GUARDRAILS_THRESHOLD=$(jq -r '.guardrails_threshold // 70' "${OPTIONS}")
export MAX_TOKENS_PER_RESPONSE=$(jq -r '.max_tokens_per_response // 4096' "${OPTIONS}")
export REQUESTS_PER_MINUTE=$(jq -r '.requests_per_minute // 20' "${OPTIONS}")

# ------------------------------------------------------------------
# Auto-discover Home Assistant via Supervisor API
# ------------------------------------------------------------------
export HA_URL="http://supervisor/core"
export HA_TOKEN="${SUPERVISOR_TOKEN:-}"

if [ -z "${HA_TOKEN}" ]; then
    log_error "SUPERVISOR_TOKEN is not set — Home Assistant API calls will fail."
    log_error "This is expected when init: false is used. The app will start but HA control won't work."
fi

log_info "AI Provider: ${AI_PROVIDER}"
log_info "Home Assistant URL: ${HA_URL}"
log_info "Guardrails threshold: ${GUARDRAILS_THRESHOLD}"

# ------------------------------------------------------------------
# Set up persistent data directory
# ------------------------------------------------------------------
mkdir -p /data/app_data

# Symlink so the app finds its data directory at the expected path
if [ ! -L /app/data ]; then
    rm -rf /app/data
    ln -s /data/app_data /app/data
fi

# ------------------------------------------------------------------
# Mark that we are running as a Home Assistant add-on
# ------------------------------------------------------------------
export HASSIO_ADDON=true

# ------------------------------------------------------------------
# Start the application
# ------------------------------------------------------------------
log_info "Starting uvicorn on port 8000..."
cd /app
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
