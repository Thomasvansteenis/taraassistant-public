"""Pydantic models for device usage pattern tracking."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class PatternType(str, Enum):
    """Types of detected usage patterns."""

    TIME_BASED = "time_based"
    SEQUENTIAL = "sequential"


class EventSource(str, Enum):
    """Source of a device event."""

    ASSISTANT = "assistant"  # Triggered via this AI assistant
    EXTERNAL = "external"  # Triggered by user via HA frontend/app
    AUTOMATION = "automation"  # Triggered by HA automation
    UNKNOWN = "unknown"


class DeviceEvent(BaseModel):
    """A single device state change event."""

    id: Optional[int] = None
    entity_id: str
    domain: str
    old_state: Optional[str] = None
    new_state: str
    timestamp: datetime
    source: EventSource = EventSource.UNKNOWN
    context_user_id: Optional[str] = None
    context_parent_id: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class TimePatternData(BaseModel):
    """Data for a time-based pattern."""

    time_window_start: str  # HH:MM format
    time_window_end: str  # HH:MM format
    days_of_week: list[int]  # 0=Monday, 6=Sunday
    action: str  # turn_on, turn_off, etc.
    average_trigger_time: str  # HH:MM format
    variance_minutes: float


class SequentialPatternData(BaseModel):
    """Data for a sequential/trigger-based pattern."""

    sequence: list[dict[str, str]]  # [{entity_id, state}, ...]
    max_delay_seconds: int
    average_delay_seconds: float


class DetectedPattern(BaseModel):
    """A detected usage pattern."""

    id: Optional[int] = None
    pattern_type: PatternType
    entity_ids: list[str]
    pattern_data: dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    occurrence_count: int = 1
    first_seen: datetime
    last_seen: datetime
    is_active: bool = True
    suggestion_generated: bool = False


class PatternSuggestion(BaseModel):
    """An automation suggestion derived from a detected pattern."""

    pattern_id: int
    pattern_type: PatternType
    title: str
    description: str
    command: str  # Natural language command for the AI
    confidence: float
    occurrence_count: int
    entities_involved: list[str]
    automation_yaml: Optional[dict[str, Any]] = None


class UserPreference(BaseModel):
    """User feedback on a pattern or suggestion."""

    id: Optional[int] = None
    pattern_id: int
    preference_type: str  # dismissed, accepted, snoozed, created_automation
    automation_id: Optional[str] = None
    feedback_text: Optional[str] = None
    created_at: Optional[datetime] = None
