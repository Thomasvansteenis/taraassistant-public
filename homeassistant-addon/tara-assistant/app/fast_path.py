"""Fast path executor for simple commands with retry logic."""
import asyncio
from dataclasses import dataclass
from typing import Optional

from app.intent_classifier import ClassifiedIntent, ActionType
from app.tools.home_assistant import HomeAssistantClient, HAState


@dataclass
class ExecutionResult:
    """Result of a fast path execution."""
    success: bool
    message: str
    state_before: Optional[HAState] = None
    state_after: Optional[HAState] = None
    retry_count: int = 0


class FastPathExecutor:
    """Executes simple commands with verification and retry logic."""
    
    def __init__(self, max_retries: int = 2, retry_delay: float = 2.0):
        self.client = HomeAssistantClient()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def execute(self, intent: ClassifiedIntent) -> ExecutionResult:
        """Execute a classified intent with verification and retry."""
        
        # Get state before
        state_before = await self.client.get_state(intent.entity_id)
        
        if not state_before:
            return ExecutionResult(
                success=False,
                message=f"❌ Entity {intent.entity_id} not found. Is the device configured in Home Assistant?"
            )
        
        # NOTE: We intentionally do NOT check if already in desired state before executing.
        # Many devices (especially media players/TVs) report incorrect states like "off" or
        # "standby" when they're actually on. This matches the N8N workflow behavior which
        # always sends the command first, then verifies the result.

        # Execute with retry loop
        for attempt in range(self.max_retries + 1):
            try:
                # Call the service
                service = self._get_service_name(intent.action)
                await self.client.call_service(
                    domain=intent.domain,
                    service=service,
                    entity_id=intent.entity_id
                )
                
                # Wait for device to respond
                await asyncio.sleep(self.retry_delay)
                
                # Verify state
                state_after = await self.client.get_state(intent.entity_id)
                
                if state_after and intent.expected_state:
                    if state_after.state in intent.expected_state:
                        # Avoid false positives when the state was already reported as expected.
                        if self._looks_unverified(state_before, state_after, intent.expected_state):
                            if attempt < self.max_retries:
                                continue
                            return ExecutionResult(
                                success=False,
                                message=self._format_unverified_message(intent, state_after.state),
                                state_before=state_before,
                                state_after=state_after,
                                retry_count=attempt
                            )

                        # Success!
                        action_word = self._get_action_word(intent.action)
                        return ExecutionResult(
                            success=True,
                            message=f"✅ {action_word} {intent.target}",
                            state_before=state_before,
                            state_after=state_after,
                            retry_count=attempt
                        )
                
                # If not successful and not last attempt, retry
                if attempt < self.max_retries:
                    continue
                    
            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return ExecutionResult(
                        success=False,
                        message=f"❌ Error controlling {intent.target}: {str(e)}",
                        state_before=state_before,
                        retry_count=attempt
                    )
        
        # Max retries reached
        state_after = await self.client.get_state(intent.entity_id)
        current_state = state_after.state if state_after else "unknown"
        
        return ExecutionResult(
            success=False,
            message=self._format_failure_message(intent, current_state),
            state_before=state_before,
            state_after=state_after,
            retry_count=self.max_retries
        )
    
    def _get_service_name(self, action: ActionType) -> str:
        """Convert action type to HA service name."""
        return {
            ActionType.TURN_ON: "turn_on",
            ActionType.TURN_OFF: "turn_off",
            ActionType.TOGGLE: "toggle",
        }.get(action, "turn_on")
    
    def _get_action_word(self, action: ActionType) -> str:
        """Get human-readable action word."""
        return {
            ActionType.TURN_ON: "Turned on",
            ActionType.TURN_OFF: "Turned off",
            ActionType.TOGGLE: "Toggled",
        }.get(action, "Controlled")
    
    def _format_failure_message(self, intent: ClassifiedIntent, current_state: str) -> str:
        """Format a helpful failure message."""
        action_phrase = {
            ActionType.TURN_ON: "turn on",
            ActionType.TURN_OFF: "turn off",
            ActionType.TOGGLE: "toggle",
        }.get(intent.action, "control")
        
        expected = ", ".join(intent.expected_state) if intent.expected_state else "changed"
        
        return f"""❌ Couldn't {action_phrase} {intent.target}

**Current state:** {current_state}
**Expected:** {expected}

Tried {self.max_retries + 1} times. The device might be:
• Offline or unplugged
• Not responding to commands
• Having network issues

Try checking if the device is powered on and connected."""

    def _looks_unverified(
        self,
        state_before: Optional[HAState],
        state_after: Optional[HAState],
        expected_state: list[str]
    ) -> bool:
        """Detect cases where HA reports the expected state but no change occurred."""
        if not state_before or not state_after:
            return False

        was_expected = state_before.state in expected_state
        if not was_expected:
            return False

        if state_before.last_changed and state_after.last_changed:
            return state_before.last_changed == state_after.last_changed

        return state_before.state == state_after.state

    def _format_unverified_message(self, intent: ClassifiedIntent, current_state: str) -> str:
        """Format a message for unverified commands."""
        action_phrase = {
            ActionType.TURN_ON: "turn on",
            ActionType.TURN_OFF: "turn off",
            ActionType.TOGGLE: "toggle",
        }.get(intent.action, "control")

        return (
            f"⚠️ Sent the command to {action_phrase} {intent.target}, but Home Assistant "
            f"still reports the state as '{current_state}'. The device might not be reporting "
            "its state accurately. Please check the device directly."
        )
