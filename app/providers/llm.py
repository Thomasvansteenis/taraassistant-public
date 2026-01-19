"""LLM Provider abstraction - supports OpenAI, Anthropic, and Ollama."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import time

from app.config import get_settings
from app.usage import get_usage_tracker


@dataclass
class Message:
    """A chat message."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


@dataclass
class ToolCall:
    """A tool call request from the LLM."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Response from an LLM."""
    content: str | None
    tool_calls: list[ToolCall] | None
    finish_reason: str
    input_tokens: int = 0
    output_tokens: int = 0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    provider_name: str = "unknown"
    model: str = "unknown"

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        """Send a chat completion request."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""

    provider_name = "openai"

    def __init__(self):
        from openai import AsyncOpenAI
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        start_time = time.time()
        tracker = get_usage_tracker()

        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            openai_messages.append(m)

        kwargs = {
            "model": self.model,
            "messages": openai_messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Build request log
        request_log = {
            "messages": openai_messages,
            "tools": tools,
            "model": self.model
        }

        try:
            response = await self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls = None
            if choice.message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                    )
                    for tc in choice.message.tool_calls
                ]

            # Extract token usage
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            duration_ms = int((time.time() - start_time) * 1000)

            # Build response log
            response_log = {
                "content": choice.message.content,
                "tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls] if tool_calls else None,
                "finish_reason": choice.finish_reason
            }

            # Record usage and log
            tracker.record_usage(
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id
            )
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response=response_log,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                session_id=session_id
            )

            return LLMResponse(
                content=choice.message.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response={},
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                session_id=session_id,
                error=str(e)
            )
            raise


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI-compatible API provider for self-hosted servers.

    Works with OpenWebUI, llama.cpp, LM Studio, vLLM, LocalAI, text-generation-webui, etc.
    """

    provider_name = "openai_compatible"

    def __init__(self):
        from openai import AsyncOpenAI
        settings = get_settings()
        # Use custom base URL, API key is optional (use "none" if not provided)
        api_key = settings.openai_compatible_api_key or "none"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=settings.openai_compatible_host
        )
        self.model = settings.openai_compatible_model

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        start_time = time.time()
        tracker = get_usage_tracker()

        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            openai_messages.append(m)

        kwargs = {
            "model": self.model,
            "messages": openai_messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Build request log
        request_log = {
            "messages": openai_messages,
            "tools": tools,
            "model": self.model
        }

        try:
            response = await self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls = None
            if choice.message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                    )
                    for tc in choice.message.tool_calls
                ]

            # Extract token usage (may not be available on all servers)
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            duration_ms = int((time.time() - start_time) * 1000)

            # Build response log
            response_log = {
                "content": choice.message.content,
                "tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls] if tool_calls else None,
                "finish_reason": choice.finish_reason
            }

            # Record usage and log
            tracker.record_usage(
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id
            )
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response=response_log,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                session_id=session_id
            )

            return LLMResponse(
                content=choice.message.content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response={},
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                session_id=session_id,
                error=str(e)
            )
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    provider_name = "anthropic"

    def __init__(self):
        from anthropic import AsyncAnthropic
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def _convert_tools_to_anthropic(self, tools: list[dict]) -> list[dict]:
        """Convert OpenAI tool format to Anthropic format."""
        anthropic_tools = []
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"]
                })
        return anthropic_tools

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        start_time = time.time()
        tracker = get_usage_tracker()

        # Extract system message
        system = None
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            elif msg.role == "tool":
                # Anthropic uses tool_result
                chat_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content
                    }]
                })
            else:
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        settings = get_settings()
        kwargs = {
            "model": self.model,
            "max_tokens": settings.max_tokens_per_response,
            "messages": chat_messages,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic(tools)

        # Build request log
        request_log = {
            "messages": chat_messages,
            "system": system,
            "tools": kwargs.get("tools"),
            "model": self.model,
            "max_tokens": settings.max_tokens_per_response
        }

        try:
            response = await self.client.messages.create(**kwargs)

            content = None
            tool_calls = None

            for block in response.content:
                if block.type == "text":
                    content = block.text
                elif block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append(ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    ))

            # Extract token usage
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0

            duration_ms = int((time.time() - start_time) * 1000)

            # Build response log
            response_log = {
                "content": content,
                "tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls] if tool_calls else None,
                "stop_reason": response.stop_reason
            }

            # Record usage and log
            tracker.record_usage(
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id
            )
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response=response_log,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                session_id=session_id
            )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=response.stop_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response={},
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                session_id=session_id,
                error=str(e)
            )
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""

    provider_name = "ollama"

    def __init__(self):
        import httpx
        settings = get_settings()
        self.host = settings.ollama_host
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        start_time = time.time()
        tracker = get_usage_tracker()

        # Convert messages
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Ollama tool support is limited, so we embed tool descriptions in the prompt
        if tools:
            tool_desc = self._format_tools_for_prompt(tools)
            # Prepend to system message or add one
            if ollama_messages and ollama_messages[0]["role"] == "system":
                ollama_messages[0]["content"] += f"\n\n{tool_desc}"
            else:
                ollama_messages.insert(0, {"role": "system", "content": tool_desc})

        request_body = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False
        }

        # Build request log
        request_log = {
            "messages": ollama_messages,
            "tools": tools,
            "model": self.model
        }

        try:
            response = await self.client.post(
                f"{self.host}/api/chat",
                json=request_body
            )
            response.raise_for_status()
            data = response.json()

            content = data["message"]["content"]
            tool_calls = self._parse_tool_calls_from_response(content) if tools else None

            # Ollama provides token counts in some versions
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)

            duration_ms = int((time.time() - start_time) * 1000)

            # Build response log
            response_log = {
                "content": content,
                "tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls] if tool_calls else None,
            }

            # Record usage and log
            tracker.record_usage(
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id
            )
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response=response_log,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                session_id=session_id
            )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason="stop",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response={},
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                session_id=session_id,
                error=str(e)
            )
            raise

    def _format_tools_for_prompt(self, tools: list[dict]) -> str:
        """Format tools as text for Ollama prompt."""
        lines = ["You have access to these tools. To use a tool, respond with JSON in this format:",
                 '{"tool": "tool_name", "arguments": {...}}',
                 "",
                 "Available tools:"]
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                lines.append(f"\n- {func['name']}: {func['description']}")
                lines.append(f"  Parameters: {json.dumps(func['parameters']['properties'])}")
        return "\n".join(lines)

    def _parse_tool_calls_from_response(self, content: str) -> list[ToolCall] | None:
        """Try to parse tool calls from Ollama response."""
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                if "tool" in data:
                    return [ToolCall(
                        id="ollama-1",
                        name=data["tool"],
                        arguments=data.get("arguments", {})
                    )]
        except:
            pass
        return None


class GoogleProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    provider_name = "google"

    def __init__(self):
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "Google provider requires google-genai. Install with `pip install google-genai`."
            ) from exc
        settings = get_settings()
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.google_model

    def _convert_tools_to_google(self, tools: list[dict]) -> list[dict]:
        """Convert OpenAI tool format to Google format."""
        google_tools = []
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                google_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"]
                })
        return google_tools

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        session_id: str = "default",
    ) -> LLMResponse:
        start_time = time.time()
        tracker = get_usage_tracker()

        # Extract system instruction and convert messages
        system_instruction = None
        google_messages = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "tool":
                # Google uses function_response
                google_messages.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": msg.tool_call_id or "function",
                            "response": {"result": msg.content}
                        }
                    }]
                })
            elif msg.role == "assistant" and msg.tool_calls:
                # Assistant message with tool calls
                parts = []
                if msg.content:
                    parts.append({"text": msg.content})
                for tc in msg.tool_calls:
                    parts.append({
                        "function_call": {
                            "name": tc.get("function", {}).get("name", ""),
                            "args": json.loads(tc.get("function", {}).get("arguments", "{}"))
                        }
                    })
                google_messages.append({"role": "model", "parts": parts})
            else:
                role = "model" if msg.role == "assistant" else "user"
                google_messages.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

        # Build request log
        request_log = {
            "messages": google_messages,
            "system_instruction": system_instruction,
            "tools": tools,
            "model": self.model
        }

        try:
            # Build config
            from google.genai import types

            config_kwargs = {}
            if system_instruction:
                config_kwargs["system_instruction"] = system_instruction

            if tools:
                google_tools = self._convert_tools_to_google(tools)
                config_kwargs["tools"] = [{"function_declarations": google_tools}]

            config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

            # Make the API call
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=google_messages,
                config=config
            )

            # Extract content and tool calls
            content = None
            tool_calls = None

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        content = part.text
                    elif hasattr(part, 'function_call') and part.function_call:
                        if tool_calls is None:
                            tool_calls = []
                        fc = part.function_call
                        tool_calls.append(ToolCall(
                            id=f"google-{len(tool_calls)}",
                            name=fc.name,
                            arguments=dict(fc.args) if fc.args else {}
                        ))

            # Extract token usage
            input_tokens = 0
            output_tokens = 0
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            duration_ms = int((time.time() - start_time) * 1000)

            # Determine finish reason
            finish_reason = "stop"
            if tool_calls:
                finish_reason = "tool_calls"

            # Build response log
            response_log = {
                "content": content,
                "tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in tool_calls] if tool_calls else None,
                "finish_reason": finish_reason
            }

            # Record usage and log
            tracker.record_usage(
                provider=self.provider_name,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id
            )
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response=response_log,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                session_id=session_id
            )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            tracker.record_log(
                provider=self.provider_name,
                model=self.model,
                request=request_log,
                response={},
                input_tokens=0,
                output_tokens=0,
                duration_ms=duration_ms,
                session_id=session_id,
                error=str(e)
            )
            raise


def get_llm_provider() -> BaseLLMProvider:
    """Get the configured LLM provider."""
    settings = get_settings()

    if settings.ai_provider == "openai":
        return OpenAIProvider()
    elif settings.ai_provider == "anthropic":
        return AnthropicProvider()
    elif settings.ai_provider == "ollama":
        return OllamaProvider()
    elif settings.ai_provider == "google":
        return GoogleProvider()
    elif settings.ai_provider == "openai_compatible":
        return OpenAICompatibleProvider()
    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
