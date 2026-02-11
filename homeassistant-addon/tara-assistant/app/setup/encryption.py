"""Encryption utilities for secure credential storage."""
import base64
import hashlib
import platform
import uuid
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class EncryptionManager:
    """Manages encryption key derivation and data encryption using Fernet."""

    SALT = b"home_ai_assistant_v1_salt"
    ITERATIONS = 480000  # OWASP 2023 recommendation

    @classmethod
    def get_machine_identifier(cls) -> str:
        """Generate a machine-specific identifier from MAC address and hostname."""
        mac = hex(uuid.getnode())
        hostname = platform.node()
        return f"{mac}-{hostname}-tara-assistant"

    @classmethod
    def derive_key(cls, passphrase: Optional[str] = None) -> bytes:
        """Derive encryption key from passphrase or machine identifier.

        Args:
            passphrase: Optional user-provided passphrase. If not provided,
                       uses machine-specific identifier.

        Returns:
            URL-safe base64-encoded 32-byte key for Fernet.
        """
        source = passphrase if passphrase else cls.get_machine_identifier()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=cls.SALT,
            iterations=cls.ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(source.encode()))
        return key

    def __init__(self, passphrase: Optional[str] = None):
        """Initialize encryption manager.

        Args:
            passphrase: Optional passphrase for key derivation.
                       If not provided, uses machine identifier.
        """
        self.key = self.derive_key(passphrase)
        self.fernet = Fernet(self.key)

    def encrypt(self, data: str) -> bytes:
        """Encrypt string data.

        Args:
            data: Plain text string to encrypt.

        Returns:
            Encrypted bytes.
        """
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data to string.

        Args:
            encrypted_data: Encrypted bytes to decrypt.

        Returns:
            Decrypted string.

        Raises:
            InvalidToken: If decryption fails (wrong key or corrupted data).
        """
        return self.fernet.decrypt(encrypted_data).decode()

    def is_valid_encrypted_data(self, encrypted_data: bytes) -> bool:
        """Check if data can be decrypted with current key.

        Args:
            encrypted_data: Encrypted bytes to validate.

        Returns:
            True if data can be decrypted, False otherwise.
        """
        try:
            self.fernet.decrypt(encrypted_data)
            return True
        except InvalidToken:
            return False
