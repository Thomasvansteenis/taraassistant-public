"""Token usage and LLM request logging."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from collections import deque
import json


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    session_id: str = "default"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LLMLogEntry:
    """A single LLM request/response log entry."""
    timestamp: str
    provider: str
    model: str
    request: Dict[str, Any]  # Messages and tools sent
    response: Dict[str, Any]  # Response content and tool calls
    input_tokens: int
    output_tokens: int
    duration_ms: int
    session_id: str = "default"
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HALogEntry:
    """A single Home Assistant API request/response log entry."""
    timestamp: str
    method: str
    endpoint: str
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    status_code: int
    duration_ms: int
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class UsageTracker:
    """Tracks token usage, LLM request logs, and HA API logs."""

    MAX_USAGE_HISTORY = 100
    MAX_LOG_HISTORY = 50
    MAX_HA_LOG_HISTORY = 100

    def __init__(self):
        self.usage_history: deque[TokenUsage] = deque(maxlen=self.MAX_USAGE_HISTORY)
        self.log_history: deque[LLMLogEntry] = deque(maxlen=self.MAX_LOG_HISTORY)
        self.ha_log_history: deque[HALogEntry] = deque(maxlen=self.MAX_HA_LOG_HISTORY)

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        session_id: str = "default"
    ) -> TokenUsage:
        """Record token usage for a request."""
        usage = TokenUsage(
            timestamp=datetime.utcnow().isoformat(),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            session_id=session_id
        )
        self.usage_history.append(usage)
        return usage

    def record_log(
        self,
        provider: str,
        model: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        session_id: str = "default",
        error: Optional[str] = None
    ) -> LLMLogEntry:
        """Record a full LLM request/response log."""
        log_entry = LLMLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            provider=provider,
            model=model,
            request=request,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            session_id=session_id,
            error=error
        )
        self.log_history.append(log_entry)
        return log_entry

    def get_usage_history(self, limit: int = 20) -> List[dict]:
        """Get recent token usage history."""
        items = list(self.usage_history)[-limit:]
        return [u.to_dict() for u in items]

    def get_log_history(self, limit: int = 20) -> List[dict]:
        """Get recent LLM request logs."""
        items = list(self.log_history)[-limit:]
        return [l.to_dict() for l in items]

    def record_ha_log(
        self,
        method: str,
        endpoint: str,
        request_data: Optional[Dict[str, Any]],
        response_data: Optional[Dict[str, Any]],
        status_code: int,
        duration_ms: int,
        error: Optional[str] = None
    ) -> HALogEntry:
        """Record a Home Assistant API request/response."""
        log_entry = HALogEntry(
            timestamp=datetime.utcnow().isoformat(),
            method=method,
            endpoint=endpoint,
            request_data=request_data,
            response_data=response_data,
            status_code=status_code,
            duration_ms=duration_ms,
            error=error
        )
        self.ha_log_history.append(log_entry)
        return log_entry

    def get_ha_log_history(self, limit: int = 20) -> List[dict]:
        """Get recent HA API logs."""
        items = list(self.ha_log_history)[-limit:]
        return [l.to_dict() for l in items]

    def get_usage_summary(self) -> dict:
        """Get summary statistics of token usage."""
        if not self.usage_history:
            return {
                "total_requests": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "avg_tokens_per_request": 0
            }

        total_input = sum(u.input_tokens for u in self.usage_history)
        total_output = sum(u.output_tokens for u in self.usage_history)
        total = total_input + total_output
        count = len(self.usage_history)

        return {
            "total_requests": count,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total,
            "avg_tokens_per_request": round(total / count, 1) if count > 0 else 0
        }

    def clear_logs(self) -> None:
        """Clear all log history."""
        self.log_history.clear()

    def clear_usage(self) -> None:
        """Clear all usage history."""
        self.usage_history.clear()

    def clear_ha_logs(self) -> None:
        """Clear HA API log history."""
        self.ha_log_history.clear()

    def clear_all(self) -> None:
        """Clear all history."""
        self.clear_logs()
        self.clear_usage()
        self.clear_ha_logs()


# Global tracker instance
_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get the global usage tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker
