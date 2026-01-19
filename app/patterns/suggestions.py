"""Generate automation suggestions from detected patterns."""

import logging
from typing import Any, Optional

from app.patterns.database import get_pattern_db
from app.patterns.models import DetectedPattern, PatternSuggestion, PatternType

logger = logging.getLogger(__name__)


class SuggestionGenerator:
    """Generates automation suggestions from detected patterns."""

    # Day name mapping for readable output
    DAY_NAMES = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    DAY_ABBREVS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def __init__(self, entity_cache=None):
        self.db = get_pattern_db()
        self._entity_cache = entity_cache

    def generate_suggestions(
        self,
        min_confidence: float = 0.4,
        max_suggestions: int = 5,
    ) -> list[PatternSuggestion]:
        """Generate automation suggestions from high-confidence patterns."""
        patterns = self.db.get_active_patterns(min_confidence)

        # Filter out dismissed patterns
        dismissed_ids = self.db.get_dismissed_pattern_ids()
        patterns = [p for p in patterns if p.id not in dismissed_ids]

        suggestions = []
        for pattern in patterns:
            suggestion = self._pattern_to_suggestion(pattern)
            if suggestion:
                suggestions.append(suggestion)

        # Sort by confidence and occurrence count
        suggestions.sort(
            key=lambda s: (s.confidence, s.occurrence_count), reverse=True
        )

        return suggestions[:max_suggestions]

    def _pattern_to_suggestion(
        self, pattern: DetectedPattern
    ) -> Optional[PatternSuggestion]:
        """Convert a detected pattern to an automation suggestion."""
        if pattern.pattern_type == PatternType.TIME_BASED:
            return self._time_pattern_to_suggestion(pattern)
        elif pattern.pattern_type == PatternType.SEQUENTIAL:
            return self._sequential_pattern_to_suggestion(pattern)
        return None

    def _get_friendly_name(self, entity_id: str) -> str:
        """Get friendly name for an entity."""
        # Try to use entity cache if available
        if self._entity_cache:
            try:
                index = self._entity_cache.load()
                if index:
                    for entity in index.entities:
                        if entity.entity_id == entity_id:
                            return entity.friendly_name
            except Exception:
                pass

        # Fallback: extract from entity_id
        name = entity_id.split(".")[-1] if "." in entity_id else entity_id
        return name.replace("_", " ").title()

    def _format_days(self, days: list[int]) -> str:
        """Format day numbers to readable string."""
        if not days:
            return "every day"

        days_set = set(days)

        if days_set == {0, 1, 2, 3, 4}:
            return "weekdays"
        elif days_set == {5, 6}:
            return "weekends"
        elif days_set == set(range(7)):
            return "every day"
        else:
            return ", ".join(self.DAY_NAMES[d] for d in sorted(days))

    def _format_action(self, action: str) -> str:
        """Format action string for display."""
        if action == "on":
            return "on"
        elif action == "off":
            return "off"
        elif action in ("locked", "unlocked", "open", "closed"):
            return action
        else:
            return action

    def _time_pattern_to_suggestion(
        self, pattern: DetectedPattern
    ) -> Optional[PatternSuggestion]:
        """Convert time-based pattern to suggestion."""
        if pattern.id is None:
            return None

        data = pattern.pattern_data
        entity_id = pattern.entity_ids[0]
        friendly_name = self._get_friendly_name(entity_id)

        action = data.get("action", "on")
        avg_time = data.get("average_trigger_time", "00:00")
        days = data.get("days_of_week", [])
        days_str = self._format_days(days)

        # Build suggestion text
        title = f"Automate {friendly_name}"
        description = (
            f"You turn {friendly_name} {self._format_action(action)} "
            f"around {avg_time} on {days_str}. "
            f"Detected {pattern.occurrence_count} times."
        )
        command = (
            f"Create an automation to turn {friendly_name} {action} "
            f"at {avg_time} on {days_str}"
        )

        # Build Home Assistant automation YAML
        automation_yaml = self._build_time_automation(
            entity_id, action, avg_time, days
        )

        return PatternSuggestion(
            pattern_id=pattern.id,
            pattern_type=pattern.pattern_type,
            title=title,
            description=description,
            command=command,
            confidence=pattern.confidence,
            occurrence_count=pattern.occurrence_count,
            entities_involved=pattern.entity_ids,
            automation_yaml=automation_yaml,
        )

    def _sequential_pattern_to_suggestion(
        self, pattern: DetectedPattern
    ) -> Optional[PatternSuggestion]:
        """Convert sequential pattern to suggestion."""
        if pattern.id is None:
            return None

        data = pattern.pattern_data
        sequence = data.get("sequence", [])

        if len(sequence) < 2:
            return None

        trigger_entity = sequence[0]["entity_id"]
        trigger_state = sequence[0]["state"]
        action_entity = sequence[1]["entity_id"]
        action_state = sequence[1]["state"]

        trigger_name = self._get_friendly_name(trigger_entity)
        action_name = self._get_friendly_name(action_entity)

        avg_delay = data.get("average_delay_seconds", 0)
        if avg_delay < 60:
            delay_str = f"{int(avg_delay)} seconds"
        else:
            delay_str = f"{int(avg_delay / 60)} minutes"

        # Build suggestion text
        title = f"Link {trigger_name} to {action_name}"
        description = (
            f"When {trigger_name} becomes {trigger_state}, "
            f"you typically set {action_name} to {action_state} within {delay_str}. "
            f"Detected {pattern.occurrence_count} times."
        )
        command = (
            f"Create an automation that turns {action_name} {action_state} "
            f"when {trigger_name} becomes {trigger_state}"
        )

        # Build Home Assistant automation YAML
        automation_yaml = self._build_trigger_automation(
            trigger_entity, trigger_state, action_entity, action_state
        )

        return PatternSuggestion(
            pattern_id=pattern.id,
            pattern_type=pattern.pattern_type,
            title=title,
            description=description,
            command=command,
            confidence=pattern.confidence,
            occurrence_count=pattern.occurrence_count,
            entities_involved=pattern.entity_ids,
            automation_yaml=automation_yaml,
        )

    def _build_time_automation(
        self,
        entity_id: str,
        action: str,
        time: str,
        days: list[int],
    ) -> dict[str, Any]:
        """Build Home Assistant automation YAML for time-based trigger."""
        domain = entity_id.split(".")[0]

        # Determine service based on action
        if action in ("on", "off"):
            service = f"turn_{action}"
        else:
            service = action

        # Build condition for specific days if not every day
        conditions = []
        if days and set(days) != set(range(7)):
            day_list = [self.DAY_ABBREVS[d] for d in days]
            conditions.append({"condition": "time", "weekday": day_list})

        entity_name = entity_id.split(".")[-1]
        alias = f"Auto {entity_name} {action} at {time.replace(':', '')}"

        automation = {
            "alias": alias,
            "trigger": [{"platform": "time", "at": time}],
            "action": [
                {
                    "service": f"{domain}.{service}",
                    "target": {"entity_id": entity_id},
                }
            ],
        }

        if conditions:
            automation["condition"] = conditions

        return automation

    def _build_trigger_automation(
        self,
        trigger_entity: str,
        trigger_state: str,
        action_entity: str,
        action_state: str,
    ) -> dict[str, Any]:
        """Build Home Assistant automation YAML for state trigger."""
        domain = action_entity.split(".")[0]

        # Determine service based on action state
        if action_state in ("on", "off"):
            service = f"turn_{action_state}"
        elif action_state == "locked":
            service = "lock"
        elif action_state == "unlocked":
            service = "unlock"
        elif action_state == "open":
            service = "open_cover"
        elif action_state == "closed":
            service = "close_cover"
        else:
            service = action_state

        trigger_name = trigger_entity.split(".")[-1]
        action_name = action_entity.split(".")[-1]
        alias = f"Auto {trigger_name} triggers {action_name}"

        return {
            "alias": alias,
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": trigger_entity,
                    "to": trigger_state,
                }
            ],
            "action": [
                {
                    "service": f"{domain}.{service}",
                    "target": {"entity_id": action_entity},
                }
            ],
        }


def get_suggestion_generator(entity_cache=None) -> SuggestionGenerator:
    """Get a SuggestionGenerator instance."""
    return SuggestionGenerator(entity_cache=entity_cache)
