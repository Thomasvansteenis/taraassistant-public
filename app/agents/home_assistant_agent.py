"""Home Assistant AI Agent - Full featured version matching n8n workflow."""
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
import string

from app.providers.llm import get_llm_provider, Message, LLMResponse, BaseLLMProvider
from app.tools.home_assistant import HomeAssistantTools
from app.intent_classifier import IntentClassifier, RouteType, ClassifiedIntent
from app.guardrails import SafetyGuardrails, GuardrailResult
from app.fast_path import FastPathExecutor
from app.memory import get_memory, ConversationMemory


SYSTEM_PROMPT_TEMPLATE = """You are a Home Assistant AI controller. You help users control their smart home using natural language.

## AVAILABLE DEVICES

{device_list}

IMPORTANT: Always use the exact entity_id from this list. Do NOT guess entity IDs.

## AVAILABLE SCRIPTS (from scripts.yaml)

{script_list}

## WHEN TO CHECK STATE FIRST

**CHECK STATE BEFORE** these commands:
- Turning devices on/off → Check if device is available
- Launching apps NOW → Check source_list for correct app name
- Checking what's currently playing

**DON'T NEED TO CHECK STATE** for:
- Creating automations → Just use known package names
- Listing automations → Read from list_automations tool
- Deleting/disabling automations → Just call the service
- Answering questions about capabilities

## KNOWN APP PACKAGE NAMES (for automations)

| App | Package Name |
|-----|-------------|
| Netflix | com.netflix.ninja |
| YouTube | com.google.android.youtube.tv |
| Apple TV | com.apple.atve.androidtv.appletv |
| Disney+ | com.disney.disneyplus |
| Hulu | com.hulu.plus |
| Prime Video | com.amazon.avod.thirdpartyclient |
| Spotify | com.spotify.tv.android |
| HBO Max | com.hbo.hbonow |
| Plex | com.plexapp.android |

## CREATING AUTOMATIONS

Use create_automation tool with:
- automation_id: unique lowercase ID (e.g., "open_netflix_10pm")
- alias: human-readable name
- trigger_type: "time" or "state"
- trigger_value: time like "22:00:00" or entity_id
- action_domain, action_service, action_entity_id, action_data

## MANAGING AUTOMATIONS

- List: Use list_automations tool
- Disable: Use call_service with domain="automation", service="turn_off"
- Enable: Use call_service with domain="automation", service="turn_on"

## LAUNCHING APPS DIRECTLY

When user wants to open an app RIGHT NOW:
1. Get entity state first to check source_list
2. Find the app in source_list
3. Use call_service with:
   - domain: "media_player"
   - service: "play_media"
   - service_data: {{"media_content_type": "app", "media_content_id": "<package>"}}

## CRITICAL RULES

- Always verify commands worked by checking state after
- Be honest if something fails
- Keep responses concise but informative
- Use ✅ for success, ❌ for failure

## RESPONSE STYLE

- Be concise and helpful
- If something fails, explain why and suggest fixes
- Don't be overly verbose
"""


@dataclass
class AgentState:
    """Tracks the state of an agent conversation."""
    messages: list[Message] = field(default_factory=list)
    max_iterations: int = 10
    iteration: int = 0


class HomeAssistantAgent:
    """Full-featured AI Agent for controlling Home Assistant."""

    def __init__(self):
        self._validate_system_prompt_template()
        self.llm = get_llm_provider()
        self.tools = HomeAssistantTools()
        self.tool_definitions = self.tools.get_tool_definitions()
        self.classifier = IntentClassifier()
        self.guardrails = SafetyGuardrails()
        self.fast_executor = FastPathExecutor()

    def _validate_system_prompt_template(self) -> None:
        """Fail fast if the system prompt has unexpected format placeholders."""
        formatter = string.Formatter()
        allowed_fields = {"device_list", "script_list"}
        for _, field_name, _, _ in formatter.parse(SYSTEM_PROMPT_TEMPLATE):
            if field_name and field_name not in allowed_fields:
                raise ValueError(
                    f"Unexpected format field in SYSTEM_PROMPT_TEMPLATE: {field_name}"
                )

    def _get_script_list(self) -> str:
        """Load scripts from scripts.yaml for LLM context."""
        path = Path("scripts.yaml")
        if not path.exists():
            return "No scripts.yaml found."

        scripts = []
        current_id = None
        current_alias = None
        for raw_line in path.read_text().splitlines():
            line = raw_line.rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" ") and line.endswith(":"):
                if current_id:
                    scripts.append((current_id, current_alias))
                current_id = line.split(":", 1)[0].strip()
                current_alias = None
                continue
            if current_id and line.lstrip().startswith("alias:"):
                current_alias = line.split("alias:", 1)[1].strip()

        if current_id:
            scripts.append((current_id, current_alias))

        if not scripts:
            return "No scripts found in scripts.yaml."

        lines = []
        for script_id, alias in scripts:
            name = alias or script_id
            lines.append(f"- {name}: `script.{script_id}`")
        return "\n".join(lines)

    def _get_device_list(self) -> str:
        """Get device list from cached entity index."""
        try:
            from app.setup.entity_cache import get_entity_cache
            cache = get_entity_cache()
            return cache.get_formatted_device_list()
        except Exception as e:
            return f"Could not load device cache: {e}. Use list_entities tool to discover devices."

    def _get_system_prompt(self) -> str:
        """Build system prompt with cached device list."""
        device_list = self._get_device_list()
        script_list = self._get_script_list()
        return SYSTEM_PROMPT_TEMPLATE.format(
            device_list=device_list,
            script_list=script_list
        )

    async def run(
        self,
        user_message: str,
        session_id: str = "default"
    ) -> str:
        """Run the agent with a user message."""

        # Get conversation memory
        memory = get_memory(session_id)
        
        # Step 1: Classify intent
        intent = self.classifier.classify(user_message)
        
        # Step 2: Run LLM-based safety check
        guardrail_result = await self.guardrails.check(user_message)
        if not guardrail_result.passed:
            rejection = self.guardrails.format_rejection(guardrail_result)
            memory.add_user_message(user_message)
            memory.add_assistant_message(rejection)
            return rejection
        
        # Step 3: Route to fast path or AI
        if intent.route == RouteType.FAST:
            result = await self._handle_fast_path(intent, memory)
        else:
            result = await self._handle_ai_path(user_message, memory)
        
        return result
    
    async def _handle_fast_path(
        self, 
        intent: ClassifiedIntent, 
        memory: ConversationMemory
    ) -> str:
        """Handle simple commands via fast path."""
        memory.add_user_message(intent.original_input)
        
        result = await self.fast_executor.execute(intent)
        
        memory.add_assistant_message(result.message)
        return result.message
    
    async def _handle_ai_path(
        self,
        user_message: str,
        memory: ConversationMemory
    ) -> str:
        """Handle complex commands via AI agent."""

        # Initialize state
        state = AgentState()

        # Add system prompt with cached device list
        system_prompt = self._get_system_prompt()
        state.messages.append(Message(role="system", content=system_prompt))
        
        # Add conversation history
        history = memory.get_messages()
        if history:
            # Only add recent history to avoid context overflow
            recent_history = history[-10:]  # Last 10 messages
            state.messages.extend(recent_history)
        
        # Add current user message
        state.messages.append(Message(role="user", content=user_message))
        memory.add_user_message(user_message)
        
        # Agent loop
        while state.iteration < state.max_iterations:
            state.iteration += 1
            
            # Get LLM response
            try:
                response = await self.llm.chat(
                    messages=state.messages,
                    tools=self.tool_definitions
                )
            except Exception as e:
                error_msg = f"❌ Error communicating with AI: {str(e)}"
                memory.add_assistant_message(error_msg)
                return error_msg
            
            # If no tool calls, we're done
            if not response.tool_calls:
                final_response = response.content or "Done!"
                memory.add_assistant_message(final_response)
                return final_response
            
            # Add assistant message with tool calls
            state.messages.append(Message(
                role="assistant",
                content=response.content,
                tool_calls=[
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": str(tc.arguments)
                        }
                    }
                    for tc in response.tool_calls
                ]
            ))
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                try:
                    result = await self.tools.execute_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                except Exception as e:
                    result = f"Error executing {tool_call.name}: {str(e)}"
                
                # Add tool result to messages
                state.messages.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=tool_call.id
                ))
            
            # Small delay between iterations
            await asyncio.sleep(0.5)
        
        timeout_msg = "I reached the maximum number of steps. Please try a simpler request."
        memory.add_assistant_message(timeout_msg)
        return timeout_msg


# Convenience function
async def chat(message: str, session_id: str = "default") -> str:
    """Quick function to chat with the agent."""
    agent = HomeAssistantAgent()
    return await agent.run(message, session_id)
