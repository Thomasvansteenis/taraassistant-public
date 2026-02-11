#!/usr/bin/env bashio

bashio::log.info "Starting Tara Assistant add-on..."

# ------------------------------------------------------------------
# Read configuration from Home Assistant add-on options
# ------------------------------------------------------------------
export AI_PROVIDER=$(bashio::config 'ai_provider')
export OPENAI_API_KEY=$(bashio::config 'openai_api_key')
export OPENAI_MODEL=$(bashio::config 'openai_model')
export ANTHROPIC_API_KEY=$(bashio::config 'anthropic_api_key')
export ANTHROPIC_MODEL=$(bashio::config 'anthropic_model')
export OLLAMA_HOST=$(bashio::config 'ollama_host')
export OLLAMA_MODEL=$(bashio::config 'ollama_model')
export GOOGLE_API_KEY=$(bashio::config 'google_api_key')
export GOOGLE_MODEL=$(bashio::config 'google_model')
export OPENAI_COMPATIBLE_HOST=$(bashio::config 'openai_compatible_host')
export OPENAI_COMPATIBLE_API_KEY=$(bashio::config 'openai_compatible_api_key')
export OPENAI_COMPATIBLE_MODEL=$(bashio::config 'openai_compatible_model')
export GUARDRAILS_THRESHOLD=$(bashio::config 'guardrails_threshold')
export MAX_TOKENS_PER_RESPONSE=$(bashio::config 'max_tokens_per_response')
export REQUESTS_PER_MINUTE=$(bashio::config 'requests_per_minute')

# ------------------------------------------------------------------
# Auto-discover Home Assistant via Supervisor API
# ------------------------------------------------------------------
export HA_URL="http://supervisor/core"
export HA_TOKEN="${SUPERVISOR_TOKEN}"

bashio::log.info "AI Provider: ${AI_PROVIDER}"
bashio::log.info "Home Assistant URL: ${HA_URL}"
bashio::log.info "Guardrails threshold: ${GUARDRAILS_THRESHOLD}"

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
bashio::log.info "Starting uvicorn on port 8000..."
cd /app
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
