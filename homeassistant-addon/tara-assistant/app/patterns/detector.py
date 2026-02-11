"""Pattern detection algorithms for device usage analysis."""

import logging
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from app.patterns.database import get_pattern_db
from app.patterns.models import DetectedPattern, DeviceEvent, PatternType

logger = logging.getLogger(__name__)


class PatternDetector:
    """Detects usage patterns from device events."""

    # Minimum occurrences to consider a pattern valid
    MIN_TIME_OCCURRENCES = 3
    MIN_SEQUENCE_OCCURRENCES = 2

    # Time window for grouping similar events (minutes)
    TIME_WINDOW_MINUTES = 30

    # Maximum delay between sequential events (seconds)
    MAX_SEQUENCE_DELAY = 300  # 5 minutes

    # Minimum delay to avoid same-trigger events (seconds)
    MIN_SEQUENCE_DELAY = 2

    def __init__(self):
        self.db = get_pattern_db()

    def detect_all_patterns(
        self, lookback_days: int = 14
    ) -> list[DetectedPattern]:
        """Run all pattern detection algorithms."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=lookback_days)

        events = self.db.get_events_in_range(start_time, end_time)

        if not events:
            logger.info("No events found for pattern detection")
            return []

        logger.info(f"Analyzing {len(events)} events for patterns")

        patterns = []

        # Detect time-based patterns
        time_patterns = self._detect_time_patterns(events)
        patterns.extend(time_patterns)
        logger.info(f"Found {len(time_patterns)} time-based patterns")

        # Detect sequential patterns
        seq_patterns = self._detect_sequential_patterns(events)
        patterns.extend(seq_patterns)
        logger.info(f"Found {len(seq_patterns)} sequential patterns")

        # Store or update patterns in database
        self._persist_patterns(patterns)

        return patterns

    def _detect_time_patterns(
        self, events: list[DeviceEvent]
    ) -> list[DetectedPattern]:
        """Detect recurring time-based patterns."""
        patterns = []

        # Group events by entity_id and action (new_state)
        entity_action_events: dict[tuple[str, str], list[DeviceEvent]] = (
            defaultdict(list)
        )

        for event in events:
            # Only look at meaningful state changes
            if event.new_state in ("unavailable", "unknown"):
                continue
            key = (event.entity_id, event.new_state)
            entity_action_events[key].append(event)

        for (entity_id, action), entity_events in entity_action_events.items():
            if len(entity_events) < self.MIN_TIME_OCCURRENCES:
                continue

            # Analyze time pattern for this entity/action combo
            pattern = self._analyze_time_pattern(entity_id, action, entity_events)
            if pattern:
                patterns.append(pattern)

        return patterns

    def _analyze_time_pattern(
        self,
        entity_id: str,
        action: str,
        events: list[DeviceEvent],
    ) -> Optional[DetectedPattern]:
        """Analyze events for time-based patterns."""
        # Extract time components: day_of_week -> list of minutes since midnight
        times_by_day: dict[int, list[int]] = defaultdict(list)

        for event in events:
            day_of_week = event.timestamp.weekday()
            minutes = event.timestamp.hour * 60 + event.timestamp.minute
            times_by_day[day_of_week].append(minutes)

        # Find days with consistent patterns (at least 2 occurrences on that day)
        consistent_days = []
        all_minutes = []

        for day, minutes_list in times_by_day.items():
            if len(minutes_list) >= 2:
                try:
                    avg = statistics.mean(minutes_list)
                    stdev = (
                        statistics.stdev(minutes_list)
                        if len(minutes_list) > 1
                        else 0
                    )

                    # If times are consistent within our window
                    if stdev <= self.TIME_WINDOW_MINUTES:
                        consistent_days.append(day)
                        all_minutes.extend(minutes_list)
                except statistics.StatisticsError:
                    continue

        # Need enough occurrences across consistent days
        if (
            not consistent_days
            or len(all_minutes) < self.MIN_TIME_OCCURRENCES
        ):
            return None

        # Calculate pattern statistics
        try:
            avg_minutes = statistics.mean(all_minutes)
            variance = (
                statistics.stdev(all_minutes) if len(all_minutes) > 1 else 0
            )
        except statistics.StatisticsError:
            return None

        avg_hour = int(avg_minutes // 60)
        avg_min = int(avg_minutes % 60)

        # Create time window around average
        window_start_min = max(0, avg_minutes - self.TIME_WINDOW_MINUTES)
        window_end_min = min(1439, avg_minutes + self.TIME_WINDOW_MINUTES)

        window_start = (
            f"{int(window_start_min // 60):02d}:{int(window_start_min % 60):02d}"
        )
        window_end = (
            f"{int(window_end_min // 60):02d}:{int(window_end_min % 60):02d}"
        )

        # Calculate confidence based on occurrences and consistency
        # More occurrences = higher base confidence
        # Lower variance = higher consistency multiplier
        base_confidence = min(1.0, len(all_minutes) / 10)
        consistency_factor = max(0.3, 1 - (variance / 60))
        confidence = base_confidence * consistency_factor
        confidence = max(0.1, min(1.0, confidence))

        pattern_data = {
            "time_window_start": window_start,
            "time_window_end": window_end,
            "days_of_week": sorted(consistent_days),
            "action": action,
            "average_trigger_time": f"{avg_hour:02d}:{avg_min:02d}",
            "variance_minutes": round(variance, 1),
        }

        return DetectedPattern(
            pattern_type=PatternType.TIME_BASED,
            entity_ids=[entity_id],
            pattern_data=pattern_data,
            confidence=round(confidence, 2),
            occurrence_count=len(all_minutes),
            first_seen=min(e.timestamp for e in events),
            last_seen=max(e.timestamp for e in events),
        )

    def _detect_sequential_patterns(
        self, events: list[DeviceEvent]
    ) -> list[DetectedPattern]:
        """Detect sequential patterns (A happens, then B follows)."""
        patterns = []

        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Track sequences: (entity_a, state_a, entity_b, state_b) -> list of delays
        sequences: dict[tuple[str, str, str, str], list[float]] = defaultdict(
            list
        )

        # Look for pairs of events within time window
        for i, event_a in enumerate(sorted_events):
            # Skip unavailable states
            if event_a.new_state in ("unavailable", "unknown"):
                continue

            for event_b in sorted_events[i + 1 :]:
                # Skip same entity
                if event_a.entity_id == event_b.entity_id:
                    continue

                # Skip unavailable states
                if event_b.new_state in ("unavailable", "unknown"):
                    continue

                delay = (
                    event_b.timestamp - event_a.timestamp
                ).total_seconds()

                # Stop if too far apart
                if delay > self.MAX_SEQUENCE_DELAY:
                    break

                # Skip if delay is too short (likely same trigger)
                if delay < self.MIN_SEQUENCE_DELAY:
                    continue

                key = (
                    event_a.entity_id,
                    event_a.new_state,
                    event_b.entity_id,
                    event_b.new_state,
                )
                sequences[key].append(delay)

        # Filter to significant sequences
        for key, delays in sequences.items():
            if len(delays) < self.MIN_SEQUENCE_OCCURRENCES:
                continue

            entity_a, state_a, entity_b, state_b = key

            try:
                avg_delay = statistics.mean(delays)
                max_delay = max(delays)

                # Calculate consistency of delays
                if len(delays) > 1:
                    delay_stdev = statistics.stdev(delays)
                    consistency = max(0.3, 1 - (delay_stdev / avg_delay))
                else:
                    consistency = 0.5

                # Calculate confidence
                base_confidence = min(1.0, len(delays) / 5)
                confidence = base_confidence * consistency
                confidence = max(0.1, min(1.0, confidence))

            except (statistics.StatisticsError, ZeroDivisionError):
                continue

            pattern_data = {
                "sequence": [
                    {"entity_id": entity_a, "state": state_a},
                    {"entity_id": entity_b, "state": state_b},
                ],
                "max_delay_seconds": int(max_delay),
                "average_delay_seconds": round(avg_delay, 1),
            }

            # Estimate first/last seen based on event timestamps
            first_seen = datetime.utcnow() - timedelta(days=14)
            last_seen = datetime.utcnow()

            patterns.append(
                DetectedPattern(
                    pattern_type=PatternType.SEQUENTIAL,
                    entity_ids=[entity_a, entity_b],
                    pattern_data=pattern_data,
                    confidence=round(confidence, 2),
                    occurrence_count=len(delays),
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
            )

        return patterns

    def _persist_patterns(self, patterns: list[DetectedPattern]) -> None:
        """Store or update patterns in database."""
        # Get existing patterns for comparison
        existing = self.db.get_active_patterns(min_confidence=0)

        # Create lookup by (entity_ids tuple, pattern_type)
        existing_lookup: dict[
            tuple[tuple[str, ...], PatternType], DetectedPattern
        ] = {}
        for p in existing:
            key = (tuple(sorted(p.entity_ids)), p.pattern_type)
            existing_lookup[key] = p

        for pattern in patterns:
            key = (tuple(sorted(pattern.entity_ids)), pattern.pattern_type)

            if key in existing_lookup:
                # Update existing pattern
                existing_pattern = existing_lookup[key]
                pattern.id = existing_pattern.id
                pattern.occurrence_count = max(
                    pattern.occurrence_count,
                    existing_pattern.occurrence_count,
                )
                pattern.first_seen = min(
                    pattern.first_seen, existing_pattern.first_seen
                )
                self.db.update_pattern(pattern)
                logger.debug(f"Updated pattern {pattern.id}")
            else:
                # Insert new pattern
                pattern_id = self.db.insert_pattern(pattern)
                pattern.id = pattern_id
                logger.debug(f"Inserted new pattern {pattern_id}")


def get_pattern_detector() -> PatternDetector:
    """Get a PatternDetector instance."""
    return PatternDetector()
