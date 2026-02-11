"""Credential validation for AI providers and Home Assistant."""
import logging
from typing import List, Optional, Tuple

import httpx

from app.setup.models import AIProvider

logger = logging.getLogger(__name__)


class ProviderValidator:
    """Validates AI provider credentials and retrieves available models."""

    TIMEOUT = 15.0  # seconds

    @staticmethod
    async def validate_openai(api_key: str) -> Tuple[bool, List[str], Optional[str]]:
        """Validate OpenAI API key and return available models.

        Args:
            api_key: OpenAI API key to validate.

        Returns:
            Tuple of (valid, models, error_message).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=ProviderValidator.TIMEOUT
                )

                if response.status_code == 401:
                    return False, [], "Invalid API key"

                if response.status_code == 429:
                    return False, [], "Rate limited - please try again later"

                response.raise_for_status()
                data = response.json()

                # Filter to chat-capable models
                chat_models = [
                    m["id"] for m in data.get("data", [])
                    if any(prefix in m["id"] for prefix in [
                        "gpt-4", "gpt-3.5", "o1", "o3", "chatgpt"
                    ])
                    and "realtime" not in m["id"]  # Exclude realtime models
                    and "audio" not in m["id"]     # Exclude audio models
                ]
                # Sort with newest/best first
                chat_models.sort(reverse=True)

                # Fallback: if no models matched filter, return commonly available models
                if not chat_models:
                    logger.warning(
                        f"OpenAI returned {len(data.get('data', []))} models but none matched filter. "
                        f"Using fallback model list."
                    )
                    chat_models = [
                        "gpt-4o",
                        "gpt-4o-mini", 
                        "gpt-4-turbo",
                        "gpt-4",
                        "gpt-3.5-turbo"
                    ]

                return True, chat_models, None

        except httpx.TimeoutException:
            return False, [], "Connection timeout - check your internet connection"
        except httpx.ConnectError:
            return False, [], "Cannot connect to OpenAI API"
        except Exception as e:
            return False, [], f"Validation error: {str(e)}"

    @staticmethod
    async def validate_anthropic(api_key: str) -> Tuple[bool, List[str], Optional[str]]:
        """Validate Anthropic API key with minimal token usage.

        Args:
            api_key: Anthropic API key to validate.

        Returns:
            Tuple of (valid, models, error_message).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "Hi"}]
                    },
                    timeout=ProviderValidator.TIMEOUT
                )

                if response.status_code == 401:
                    return False, [], "Invalid API key"

                # 200 = success, 429 = rate limited but key is valid
                if response.status_code in [200, 429]:
                    # Anthropic doesn't have a models list API, return known models
                    models = [
                        "claude-opus-4-20250514",
                        "claude-sonnet-4-20250514",
                        "claude-3-5-sonnet-20241022",
                        "claude-3-5-haiku-20241022",
                        "claude-3-opus-20240229",
                        "claude-3-haiku-20240307"
                    ]
                    return True, models, None

                if response.status_code == 400:
                    return False, [], "Invalid request - API key may be malformed"

                return False, [], f"Unexpected response: {response.status_code}"

        except httpx.TimeoutException:
            return False, [], "Connection timeout - check your internet connection"
        except httpx.ConnectError:
            return False, [], "Cannot connect to Anthropic API"
        except Exception as e:
            return False, [], f"Validation error: {str(e)}"

    @staticmethod
    async def validate_ollama(host: str) -> Tuple[bool, List[str], Optional[str]]:
        """Validate Ollama connection and get available models.

        Args:
            host: Ollama host URL (e.g., http://localhost:11434).

        Returns:
            Tuple of (valid, models, error_message).
        """
        host = host.rstrip("/")

        try:
            async with httpx.AsyncClient() as client:
                # Check if Ollama is running by getting model list
                response = await client.get(
                    f"{host}/api/tags",
                    timeout=ProviderValidator.TIMEOUT
                )
                response.raise_for_status()
                data = response.json()

                models = [m["name"] for m in data.get("models", [])]

                if not models:
                    # Ollama is running but no models installed
                    return True, [], "Connected but no models installed. Run 'ollama pull llama3.1' to get started."

                return True, models, None

        except httpx.ConnectError:
            return False, [], f"Cannot connect to Ollama at {host}. Is Ollama running?"
        except httpx.TimeoutException:
            return False, [], "Connection timeout"
        except Exception as e:
            return False, [], f"Validation error: {str(e)}"

    @staticmethod
    async def validate_google(api_key: str) -> Tuple[bool, List[str], Optional[str]]:
        """Validate Google API key and return available Gemini models.

        Args:
            api_key: Google AI API key to validate.

        Returns:
            Tuple of (valid, models, error_message).
        """
        try:
            async with httpx.AsyncClient() as client:
                # Use the models list endpoint to validate the key
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                    timeout=ProviderValidator.TIMEOUT
                )

                if response.status_code == 400:
                    data = response.json()
                    error_msg = data.get("error", {}).get("message", "Invalid API key")
                    return False, [], error_msg

                if response.status_code == 403:
                    return False, [], "Invalid API key or API not enabled"

                if response.status_code == 429:
                    return False, [], "Rate limited - please try again later"

                response.raise_for_status()
                data = response.json()

                # Filter to generative models (Gemini)
                models = []
                for m in data.get("models", []):
                    name = m.get("name", "")
                    # Extract model ID from "models/gemini-xxx" format
                    if name.startswith("models/"):
                        model_id = name.replace("models/", "")
                        # Only include gemini models that support generateContent
                        supported_methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in supported_methods and "gemini" in model_id:
                            models.append(model_id)

                # Sort with newest/best first
                models.sort(reverse=True)

                if not models:
                    # Key is valid but no models available (unlikely)
                    return True, ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"], None

                return True, models, None

        except httpx.TimeoutException:
            return False, [], "Connection timeout - check your internet connection"
        except httpx.ConnectError:
            return False, [], "Cannot connect to Google AI API"
        except Exception as e:
            return False, [], f"Validation error: {str(e)}"

    @staticmethod
    async def validate_openai_compatible(
        host: str,
        api_key: Optional[str] = None
    ) -> Tuple[bool, List[str], Optional[str]]:
        """Validate OpenAI-compatible server and get available models.

        Works with OpenWebUI, llama.cpp, LM Studio, vLLM, LocalAI, etc.

        Args:
            host: Base URL (e.g., http://localhost:8080/v1 or https://openwebui.example.com/api/v1).
            api_key: Optional API key (some servers require it, some don't).

        Returns:
            Tuple of (valid, models, error_message).
        """
        host = host.rstrip("/")

        # Build headers
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with httpx.AsyncClient() as client:
                # Try to get models list (OpenAI-compatible endpoint)
                response = await client.get(
                    f"{host}/models",
                    headers=headers,
                    timeout=ProviderValidator.TIMEOUT
                )

                if response.status_code == 401:
                    return False, [], "Authentication required - please provide an API key"

                if response.status_code == 403:
                    return False, [], "Access forbidden - check your API key"

                if response.status_code == 404:
                    # Some servers use /v1/models, try without /v1 suffix
                    if not host.endswith("/v1"):
                        alt_host = f"{host}/v1"
                        response = await client.get(
                            f"{alt_host}/models",
                            headers=headers,
                            timeout=ProviderValidator.TIMEOUT
                        )
                        if response.status_code == 200:
                            # Update hint for user
                            pass
                        else:
                            return False, [], f"Models endpoint not found at {host}/models. Check if the URL is correct."
                    else:
                        return False, [], f"Models endpoint not found. Check if the URL is correct."

                response.raise_for_status()
                data = response.json()

                # Parse models - OpenAI format returns {"data": [...]}
                models = []
                if "data" in data:
                    models = [m.get("id", m.get("name", "")) for m in data["data"] if m.get("id") or m.get("name")]
                elif isinstance(data, list):
                    # Some servers return a plain list
                    models = [m.get("id", m.get("name", str(m))) for m in data]

                if not models:
                    return True, [], "Connected but no models found. You may need to enter the model name manually."

                return True, models, None

        except httpx.ConnectError:
            return False, [], f"Cannot connect to {host}. Is the server running?"
        except httpx.TimeoutException:
            return False, [], "Connection timeout - check if the server is accessible"
        except Exception as e:
            return False, [], f"Validation error: {str(e)}"

    @classmethod
    async def validate(
        cls,
        provider: AIProvider,
        api_key: Optional[str] = None,
        host: Optional[str] = None
    ) -> Tuple[bool, List[str], Optional[str]]:
        """Validate any provider.

        Args:
            provider: The AI provider to validate.
            api_key: API key (for OpenAI/Anthropic).
            host: Host URL (for Ollama).

        Returns:
            Tuple of (valid, models, error_message).
        """
        if provider == AIProvider.OPENAI:
            if not api_key:
                return False, [], "API key is required for OpenAI"
            return await cls.validate_openai(api_key)

        elif provider == AIProvider.ANTHROPIC:
            if not api_key:
                return False, [], "API key is required for Anthropic"
            return await cls.validate_anthropic(api_key)

        elif provider == AIProvider.OLLAMA:
            ollama_host = host or "http://localhost:11434"
            return await cls.validate_ollama(ollama_host)

        elif provider == AIProvider.GOOGLE:
            if not api_key:
                return False, [], "API key is required for Google"
            return await cls.validate_google(api_key)

        elif provider == AIProvider.OPENAI_COMPATIBLE:
            if not host:
                return False, [], "Base URL is required for OpenAI-compatible servers"
            return await cls.validate_openai_compatible(host, api_key)

        else:
            return False, [], f"Unknown provider: {provider}"


class HomeAssistantValidator:
    """Validates Home Assistant connection."""

    TIMEOUT = 10.0  # seconds

    @staticmethod
    async def validate(
        url: str,
        token: str,
        fetch_entities: bool = True
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate Home Assistant connection and optionally cache entities.

        Args:
            url: Home Assistant URL (e.g., http://192.168.1.100:8123).
            token: Long-lived access token.
            fetch_entities: If True, fetch and cache entity index after validation.

        Returns:
            Tuple of (valid, version, error_message).
        """
        url = url.rstrip("/")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/api/",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    timeout=HomeAssistantValidator.TIMEOUT
                )

                if response.status_code == 401:
                    return False, None, "Invalid access token"

                if response.status_code == 403:
                    return False, None, "Access forbidden - check token permissions"

                response.raise_for_status()
                data = response.json()

                version = data.get("version", "Unknown")

                # Fetch and cache entities in background if requested
                if fetch_entities:
                    import asyncio
                    asyncio.create_task(
                        HomeAssistantValidator._fetch_entities_background(url, token)
                    )

                return True, version, None

        except httpx.ConnectError:
            return False, None, f"Cannot connect to Home Assistant at {url}"
        except httpx.TimeoutException:
            return False, None, "Connection timeout - is Home Assistant running?"
        except Exception as e:
            return False, None, f"Validation error: {str(e)}"

    @staticmethod
    async def _fetch_entities_background(url: str, token: str) -> None:
        """Fetch entities in background - failures are logged but don't affect validation."""
        try:
            from app.setup.entity_cache import EntityCache
            cache = EntityCache()
            success, error = await cache.fetch_and_cache(url, token, background=True)
            if not success:
                # Log warning but don't fail - entity cache is optional
                import logging
                logging.warning(f"Entity cache fetch failed: {error}")
        except Exception as e:
            import logging
            logging.warning(f"Entity cache background fetch error: {e}")
