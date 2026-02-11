"""SQLite database management for device usage pattern tracking."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, Optional

from app.patterns.models import (
    DetectedPattern,
    DeviceEvent,
    EventSource,
    PatternType,
)


class PatternDatabase:
    """SQLite database for device usage patterns."""

    DB_FILE = "usage_patterns.db"

    def __init__(self):
        from app.config import is_addon_mode
        self.DB_DIR = Path("/data/app_data") if is_addon_mode() else Path("data")
        self.db_path = self.DB_DIR / self.DB_FILE
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = sqlite3.connect(
            str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Initialize database schema if needed."""
        with self._get_connection() as conn:
            conn.executescript(self._get_schema_sql())
            conn.commit()

    def _get_schema_sql(self) -> str:
        """Return the full database schema SQL."""
        return """
        -- Device state change events
        CREATE TABLE IF NOT EXISTS device_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT NOT NULL,
            domain TEXT NOT NULL,
            old_state TEXT,
            new_state TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            context_user_id TEXT,
            context_parent_id TEXT,
            attributes_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_events_entity_timestamp
            ON device_events(entity_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp
            ON device_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_domain
            ON device_events(domain, timestamp);

        -- Detected usage patterns
        CREATE TABLE IF NOT EXISTS detected_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            entity_ids TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            confidence REAL NOT NULL,
            occurrence_count INTEGER DEFAULT 1,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            suggestion_generated INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_patterns_active
            ON detected_patterns(is_active, confidence DESC);
        CREATE INDEX IF NOT EXISTS idx_patterns_type
            ON detected_patterns(pattern_type);

        -- User preferences/feedback on patterns
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id INTEGER,
            preference_type TEXT NOT NULL,
            automation_id TEXT,
            feedback_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pattern_id) REFERENCES detected_patterns(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_prefs_pattern
            ON user_preferences(pattern_id);

        -- Sync metadata for HA History API
        CREATE TABLE IF NOT EXISTS sync_metadata (
            id INTEGER PRIMARY KEY DEFAULT 1,
            last_sync_timestamp TEXT,
            last_sync_entity_count INTEGER,
            sync_duration_ms INTEGER,
            error_message TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO sync_metadata (id) VALUES (1);
        """

    # ==================== Event Operations ====================

    def insert_event(self, event: DeviceEvent) -> int:
        """Insert a device event and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO device_events
                   (entity_id, domain, old_state, new_state, timestamp, source,
                    context_user_id, context_parent_id, attributes_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.entity_id,
                    event.domain,
                    event.old_state,
                    event.new_state,
                    event.timestamp.isoformat(),
                    event.source.value,
                    event.context_user_id,
                    event.context_parent_id,
                    json.dumps(event.attributes),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def insert_events_batch(self, events: list[DeviceEvent]) -> int:
        """Insert multiple events efficiently. Returns count inserted."""
        if not events:
            return 0

        with self._get_connection() as conn:
            conn.executemany(
                """INSERT INTO device_events
                   (entity_id, domain, old_state, new_state, timestamp, source,
                    context_user_id, context_parent_id, attributes_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        e.entity_id,
                        e.domain,
                        e.old_state,
                        e.new_state,
                        e.timestamp.isoformat(),
                        e.source.value,
                        e.context_user_id,
                        e.context_parent_id,
                        json.dumps(e.attributes),
                    )
                    for e in events
                ],
            )
            conn.commit()
            return len(events)

    def get_events_in_range(
        self,
        start: datetime,
        end: datetime,
        entity_id: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> list[DeviceEvent]:
        """Get events within a time range."""
        query = "SELECT * FROM device_events WHERE timestamp BETWEEN ? AND ?"
        params: list = [start.isoformat(), end.isoformat()]

        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)
        if domain:
            query += " AND domain = ?"
            params.append(domain)

        query += " ORDER BY timestamp ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_event(row) for row in rows]

    def get_event_count(self) -> int:
        """Get total number of events."""
        with self._get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM device_events").fetchone()
            return result[0] if result else 0

    def _row_to_event(self, row: sqlite3.Row) -> DeviceEvent:
        """Convert a database row to DeviceEvent."""
        return DeviceEvent(
            id=row["id"],
            entity_id=row["entity_id"],
            domain=row["domain"],
            old_state=row["old_state"],
            new_state=row["new_state"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            source=EventSource(row["source"]),
            context_user_id=row["context_user_id"],
            context_parent_id=row["context_parent_id"],
            attributes=json.loads(row["attributes_json"])
            if row["attributes_json"]
            else {},
        )

    # ==================== Pattern Operations ====================

    def insert_pattern(self, pattern: DetectedPattern) -> int:
        """Insert a detected pattern and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO detected_patterns
                   (pattern_type, entity_ids, pattern_data, confidence,
                    occurrence_count, first_seen, last_seen)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    pattern.pattern_type.value,
                    json.dumps(pattern.entity_ids),
                    json.dumps(pattern.pattern_data),
                    pattern.confidence,
                    pattern.occurrence_count,
                    pattern.first_seen.isoformat(),
                    pattern.last_seen.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_pattern(self, pattern: DetectedPattern) -> None:
        """Update an existing pattern."""
        if pattern.id is None:
            return

        with self._get_connection() as conn:
            conn.execute(
                """UPDATE detected_patterns SET
                   confidence = ?, occurrence_count = ?, last_seen = ?,
                   pattern_data = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    pattern.confidence,
                    pattern.occurrence_count,
                    pattern.last_seen.isoformat(),
                    json.dumps(pattern.pattern_data),
                    datetime.utcnow().isoformat(),
                    pattern.id,
                ),
            )
            conn.commit()

    def get_active_patterns(
        self, min_confidence: float = 0.3
    ) -> list[DetectedPattern]:
        """Get all active patterns above confidence threshold."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM detected_patterns
                   WHERE is_active = 1 AND confidence >= ?
                   ORDER BY confidence DESC, occurrence_count DESC""",
                (min_confidence,),
            ).fetchall()
            return [self._row_to_pattern(row) for row in rows]

    def get_pattern_by_id(self, pattern_id: int) -> Optional[DetectedPattern]:
        """Get a specific pattern by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM detected_patterns WHERE id = ?", (pattern_id,)
            ).fetchone()
            return self._row_to_pattern(row) if row else None

    def deactivate_pattern(self, pattern_id: int) -> None:
        """Mark a pattern as inactive (soft delete)."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE detected_patterns SET is_active = 0, updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), pattern_id),
            )
            conn.commit()

    def _row_to_pattern(self, row: sqlite3.Row) -> DetectedPattern:
        """Convert a database row to DetectedPattern."""
        return DetectedPattern(
            id=row["id"],
            pattern_type=PatternType(row["pattern_type"]),
            entity_ids=json.loads(row["entity_ids"]),
            pattern_data=json.loads(row["pattern_data"]),
            confidence=row["confidence"],
            occurrence_count=row["occurrence_count"],
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            is_active=bool(row["is_active"]),
            suggestion_generated=bool(row["suggestion_generated"]),
        )

    # ==================== User Preference Operations ====================

    def insert_user_preference(
        self,
        pattern_id: int,
        preference_type: str,
        automation_id: Optional[str] = None,
        feedback_text: Optional[str] = None,
    ) -> int:
        """Record user preference for a pattern."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO user_preferences
                   (pattern_id, preference_type, automation_id, feedback_text)
                   VALUES (?, ?, ?, ?)""",
                (pattern_id, preference_type, automation_id, feedback_text),
            )
            conn.commit()
            return cursor.lastrowid

    def get_dismissed_pattern_ids(self) -> set[int]:
        """Get IDs of patterns the user has dismissed."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT pattern_id FROM user_preferences WHERE preference_type = 'dismissed'"
            ).fetchall()
            return {row["pattern_id"] for row in rows}

    # ==================== Sync Metadata Operations ====================

    def get_last_sync_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of last successful sync."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT last_sync_timestamp FROM sync_metadata WHERE id = 1"
            ).fetchone()
            if row and row["last_sync_timestamp"]:
                return datetime.fromisoformat(row["last_sync_timestamp"])
            return None

    def update_sync_metadata(
        self,
        timestamp: datetime,
        entity_count: int,
        duration_ms: int,
        error: Optional[str] = None,
    ) -> None:
        """Update sync metadata after a sync operation."""
        with self._get_connection() as conn:
            conn.execute(
                """UPDATE sync_metadata SET
                   last_sync_timestamp = ?, last_sync_entity_count = ?,
                   sync_duration_ms = ?, error_message = ?, updated_at = ?
                   WHERE id = 1""",
                (
                    timestamp.isoformat(),
                    entity_count,
                    duration_ms,
                    error,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    # ==================== Cleanup Operations ====================

    def cleanup_old_events(self, days: int = 30) -> int:
        """Remove events older than specified days. Returns count deleted."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM device_events WHERE timestamp < ?",
                (cutoff.isoformat(),),
            )
            conn.commit()
            return cursor.rowcount

    # ==================== Statistics ====================

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self._get_connection() as conn:
            event_count = conn.execute(
                "SELECT COUNT(*) FROM device_events"
            ).fetchone()[0]

            source_counts = conn.execute(
                "SELECT source, COUNT(*) as count FROM device_events GROUP BY source"
            ).fetchall()

            pattern_counts = conn.execute(
                """SELECT pattern_type, COUNT(*) as count
                   FROM detected_patterns WHERE is_active = 1
                   GROUP BY pattern_type"""
            ).fetchall()

            date_range = conn.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM device_events"
            ).fetchone()

            return {
                "total_events": event_count,
                "events_by_source": {
                    row["source"]: row["count"] for row in source_counts
                },
                "patterns_by_type": {
                    row["pattern_type"]: row["count"] for row in pattern_counts
                },
                "date_range": {
                    "earliest": date_range[0],
                    "latest": date_range[1],
                }
                if date_range[0]
                else None,
            }


# Singleton instance
_pattern_db: Optional[PatternDatabase] = None


def get_pattern_db() -> PatternDatabase:
    """Get the global pattern database instance."""
    global _pattern_db
    if _pattern_db is None:
        _pattern_db = PatternDatabase()
    return _pattern_db
