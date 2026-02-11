# Tara Assistant - Home Assistant Add-on

AI-powered assistant that observes your household patterns and suggests Home Assistant automations. No configuration of routines needed — Tara learns by watching.

## How it works

1. **Observes** your device usage patterns from Home Assistant history
2. **Detects** recurring routines (e.g. "lights on at sunset every day")
3. **Suggests** automations as editable YAML — you approve before anything is created
4. **Executes** simple commands directly ("turn off the living room lights")

## Installation

1. Add this repository URL to your Home Assistant add-on store:
   **Settings > Add-ons > Add-on Store > ⋮ (menu) > Repositories**
2. Find "Tara Assistant" in the store and click **Install**
3. Go to the **Configuration** tab and set your AI provider and API key
4. Click **Start**
5. Open the Web UI from the sidebar (Tara Assistant)

## Configuration

### AI Provider

Choose one of the supported providers:

- **OpenAI** — Requires an API key from [platform.openai.com](https://platform.openai.com)
- **Anthropic** — Requires an API key from [console.anthropic.com](https://console.anthropic.com)
- **Google** — Requires an API key from [aistudio.google.com](https://aistudio.google.com)
- **Ollama** — Free, local AI. Run Ollama on your network and point the host setting to it
- **OpenAI-Compatible** — Any server implementing the OpenAI API (LM Studio, vLLM, llama.cpp)

### Home Assistant Connection

The add-on **automatically connects** to your Home Assistant instance using the Supervisor API. No token or URL configuration is needed.

### Safety Guardrails

The guardrails threshold (0–100) controls how cautious Tara is with sensitive actions like locks, security systems, and climate extremes. Set to 0 to disable, or higher for stricter safety checks.

## Local / Development Install

If installing from a local clone of the repository, run the build preparation
script first to copy the application code into the add-on build context:

```bash
./homeassistant-addon/build.sh
```

Then copy `homeassistant-addon/tara-assistant/` to `/addons/tara-assistant/` on
your Home Assistant machine and install from the local add-ons store.

## Support

Report issues at the [GitHub repository](https://github.com/TaraHome/taraassistant-public/issues).
