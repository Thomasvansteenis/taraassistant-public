"""Encrypted configuration storage."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.setup.encryption import EncryptionManager
from app.setup.models import StoredConfig


class ConfigStorage:
    """Encrypted configuration file storage."""

    CONFIG_DIR = Path("data")
    CONFIG_FILE = "config.enc"

    def __init__(self, passphrase: Optional[str] = None):
        """Initialize config storage.

        Args:
            passphrase: Optional passphrase for encryption.
                       If not provided, uses machine identifier.
        """
        self.encryption = EncryptionManager(passphrase)
        self.config_path = self.CONFIG_DIR / self.CONFIG_FILE

    def exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()

    def save(self, config: StoredConfig) -> None:
        """Save configuration encrypted to disk.

        Args:
            config: Configuration to save.
        """
        # Ensure directory exists
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Build data with metadata
        data = {
            "config": config.model_dump(),
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        # Encrypt and save
        encrypted = self.encryption.encrypt(json.dumps(data))
        self.config_path.write_bytes(encrypted)

        # Set restrictive permissions (owner read/write only)
        try:
            os.chmod(self.config_path, 0o600)
        except OSError:
            # Windows doesn't support chmod the same way
            pass

    def load(self) -> Optional[StoredConfig]:
        """Load and decrypt configuration.

        Returns:
            StoredConfig if exists and valid, None otherwise.
        """
        if not self.exists():
            return None

        try:
            encrypted = self.config_path.read_bytes()
            decrypted = self.encryption.decrypt(encrypted)
            data = json.loads(decrypted)
            return StoredConfig(**data["config"])
        except Exception:
            # Decryption failed or invalid data
            return None

    def delete(self) -> bool:
        """Delete configuration file.

        Returns:
            True if deleted, False if didn't exist.
        """
        if self.exists():
            self.config_path.unlink()
            return True
        return False

    def get_metadata(self) -> Optional[dict]:
        """Get configuration metadata without full config.

        Returns:
            Dict with created_at and version, or None.
        """
        if not self.exists():
            return None

        try:
            encrypted = self.config_path.read_bytes()
            decrypted = self.encryption.decrypt(encrypted)
            data = json.loads(decrypted)
            return {
                "created_at": data.get("created_at"),
                "version": data.get("version")
            }
        except Exception:
            return None
