"""Intent classifier for routing commands to fast path or AI agent."""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RouteType(Enum):
    FAST = "fast"
    AI = "ai"


class ActionType(Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    TOGGLE = "toggle"


@dataclass
class ClassifiedIntent:
    """Result of intent classification."""
    route: RouteType
    reason: str
    original_input: str
    cleaned_input: str

    # For fast path
    action: Optional[ActionType] = None
    target: Optional[str] = None
    entity_id: Optional[str] = None
    domain: Optional[str] = None
    expected_state: Optional[list[str]] = None


class IntentClassifier:
    """Simple intent classifier - questions go to AI, simple commands go to fast path."""

    # Polite prefixes to strip
    POLITE_PREFIXES = re.compile(
        r'^(can you |could you |please |would you |will you |hey |hi |)',
        re.IGNORECASE
    )

    # Question detection - starts with question word OR ends with ?
    QUESTION_STARTERS = re.compile(
        r'^(is |are |was |were |do |does |did |what |when |where |why |how |which |who |can |could |will |would |should |has |have |had |check |list |show |tell )',
        re.IGNORECASE
    )

    # Multi-step indicators
    MULTI_STEP_PATTERNS = [
        re.compile(r' and then ', re.IGNORECASE),
        re.compile(r' then ', re.IGNORECASE),
        re.compile(r' after ', re.IGNORECASE),
        re.compile(r' before ', re.IGNORECASE),
        re.compile(r' wait ', re.IGNORECASE),
        re.compile(r' and (turn|switch|set|open|launch|start|select|play)', re.IGNORECASE),
    ]

    # App launch patterns - need AI for verification
    APP_LAUNCH = re.compile(r'^(open|launch|start|play)\s+', re.IGNORECASE)

    # Domains that should be excluded from simple on/off commands
    EXCLUDED_DOMAINS = {"automation", "script", "scene", "sensor", "binary_sensor", "person", "zone", "sun", "weather"}

    # Common device aliases - maps user terms to search terms
    DEVICE_ALIASES = {
        "tv": ["tv", "television", "streaming", "roku", "firestick", "chromecast", "android tv", "onn"],
        "television": ["tv", "television", "streaming", "roku", "firestick", "chromecast", "android tv", "onn"],
    }

    # Fast path patterns - ONLY simple on/off
    FAST_PATTERNS = [
        # "turn on X" / "turn off X" (action at start)
        (re.compile(r'^(turn on|switch on|enable|power on)\s+(?:the\s+)?(.+)$', re.IGNORECASE), ActionType.TURN_ON, 2),
        (re.compile(r'^(turn off|switch off|disable|power off)\s+(?:the\s+)?(.+)$', re.IGNORECASE), ActionType.TURN_OFF, 2),
        (re.compile(r'^toggle\s+(?:the\s+)?(.+)$', re.IGNORECASE), ActionType.TOGGLE, 1),
        # "turn X on" / "turn X off" (action at end)
        (re.compile(r'^turn\s+(?:the\s+)?(.+?)\s+on$', re.IGNORECASE), ActionType.TURN_ON, 1),
        (re.compile(r'^turn\s+(?:the\s+)?(.+?)\s+off$', re.IGNORECASE), ActionType.TURN_OFF, 1),
        # "X on" / "X off" (no turn prefix)
        (re.compile(r'^(.+?)\s+(on)$', re.IGNORECASE), ActionType.TURN_ON, 1),
        (re.compile(r'^(.+?)\s+(off)$', re.IGNORECASE), ActionType.TURN_OFF, 1),
    ]

    def classify(self, message: str) -> ClassifiedIntent:
        """Classify the intent of a user message."""
        original = message
        cleaned = message.lower().strip()

        # Step 1: Clean polite phrases
        cleaned = self.POLITE_PREFIXES.sub('', cleaned)
        cleaned = re.sub(r'( please)$', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        # Step 2: QUESTIONS → Always AI (check this FIRST!)
        is_question = (
            cleaned.endswith('?') or
            bool(self.QUESTION_STARTERS.match(cleaned))
        )

        if is_question:
            return ClassifiedIntent(
                route=RouteType.AI,
                reason="question",
                original_input=original,
                cleaned_input=cleaned
            )

        # Step 3: Multi-step commands → AI
        for pattern in self.MULTI_STEP_PATTERNS:
            if pattern.search(cleaned):
                return ClassifiedIntent(
                    route=RouteType.AI,
                    reason="multi_step",
                    original_input=original,
                    cleaned_input=cleaned
                )

        # Step 4: App launches → AI (needs source_list verification)
        if self.APP_LAUNCH.match(cleaned):
            return ClassifiedIntent(
                route=RouteType.AI,
                reason="app_launch",
                original_input=original,
                cleaned_input=cleaned
            )

        # Step 5: Simple on/off commands → Fast path
        for pattern, action, target_group in self.FAST_PATTERNS:
            match = pattern.match(cleaned)
            if match:
                target = match.group(target_group).strip()

                # Skip if target has action words (probably complex)
                if re.search(r'\b(and|then|after|select|open|launch)\b', target, re.IGNORECASE):
                    continue

                # Get entity info from cache
                entity_id, domain, expected_state = self._resolve_entity(target, action)

                return ClassifiedIntent(
                    route=RouteType.FAST,
                    reason="simple_command",
                    original_input=original,
                    cleaned_input=cleaned,
                    action=action,
                    target=target,
                    entity_id=entity_id,
                    domain=domain,
                    expected_state=expected_state
                )

        # Step 6: Default → AI
        return ClassifiedIntent(
            route=RouteType.AI,
            reason="unrecognized",
            original_input=original,
            cleaned_input=cleaned
        )

    def _resolve_entity(self, target: str, action: ActionType) -> tuple[str, str, list[str]]:
        """Resolve target name to entity_id using cached entities."""
        target_lower = target.lower()

        # Try to find entity from cache
        try:
            from app.setup.entity_cache import get_entity_cache
            cache = get_entity_cache()

            # Get search terms - include aliases if available
            search_terms = [target_lower]
            for alias_key, alias_terms in self.DEVICE_ALIASES.items():
                if alias_key in target_lower:
                    search_terms.extend(alias_terms)

            # Search for matching entity using all search terms
            all_matches = []
            for term in search_terms:
                matches = cache.search_entities(term)
                all_matches.extend(matches)

            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for m in all_matches:
                if m.entity_id not in seen:
                    seen.add(m.entity_id)
                    unique_matches.append(m)

            if unique_matches:
                # Filter out non-controllable domains (automations, sensors, etc.)
                controllable = [e for e in unique_matches if e.domain not in self.EXCLUDED_DOMAINS]
                
                if controllable:
                    # Prefer media_player for "tv", light for "light", etc.
                    for entity in controllable:
                        if "tv" in target_lower and entity.domain == "media_player":
                            return self._get_entity_result(entity, action)
                        if "light" in target_lower and entity.domain == "light":
                            return self._get_entity_result(entity, action)
                        if "switch" in target_lower and entity.domain == "switch":
                            return self._get_entity_result(entity, action)
                        if "fan" in target_lower and entity.domain == "fan":
                            return self._get_entity_result(entity, action)

                    # Return first controllable match if no domain preference
                    return self._get_entity_result(controllable[0], action)

        except Exception:
            pass

        # Fallback: guess based on keywords with proper entity_id format
        if "tv" in target_lower or "television" in target_lower:
            domain = "media_player"
            # Use a reasonable default entity_id pattern for media_player
            entity_id = f"media_player.{target_lower.replace(' ', '_')}"
            expected = ["on", "playing", "idle", "paused"] if action == ActionType.TURN_ON else ["off", "standby", "unavailable"]
        elif "light" in target_lower:
            domain = "light"
            entity_id = f"light.{target_lower.replace(' ', '_')}"
            expected = ["on"] if action == ActionType.TURN_ON else ["off"]
        elif "switch" in target_lower:
            domain = "switch"
            entity_id = f"switch.{target_lower.replace(' ', '_')}"
            expected = ["on"] if action == ActionType.TURN_ON else ["off"]
        elif "fan" in target_lower:
            domain = "fan"
            entity_id = f"fan.{target_lower.replace(' ', '_')}"
            expected = ["on"] if action == ActionType.TURN_ON else ["off"]
        else:
            domain = "light"  # Default
            entity_id = f"light.{target_lower.replace(' ', '_')}"
            expected = ["on"] if action == ActionType.TURN_ON else ["off"]

        return entity_id, domain, expected

    def _get_entity_result(self, entity, action: ActionType) -> tuple[str, str, list[str]]:
        """Get entity result tuple from EntityInfo."""
        if entity.domain == "media_player":
            expected = ["on", "playing", "idle", "paused"] if action == ActionType.TURN_ON else ["off", "standby", "unavailable"]
        else:
            expected = ["on"] if action == ActionType.TURN_ON else ["off"]

        return entity.entity_id, entity.domain, expected
