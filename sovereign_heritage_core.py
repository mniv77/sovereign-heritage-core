# sovereign_heritage_core.py
# Embeddable Security & Legacy Engine - Sanitized ASCII Version
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class SovereignHeritageCore:
    """
    AES-256-GCM encryption engine for Zero-Knowledge data protection.
    Strictly standard ASCII - No non-printable characters.
    """
    def __init__(self, master_password, salt=b'sovereign_heritage_salt_v1'):
        self.salt = salt
        # Derive a secure 32-byte key from the volatile master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        self.key = kdf.derive(master_password.encode())
        self.aesgcm = AESGCM(self.key)

    def seal_title(self, title_text):
        """Encrypts the identifying title fragment."""
        return self._encrypt_string(title_text)

    def seal_record(self, record_text):
        """Encrypts the sensitive content of the vault entry."""
        return self._encrypt_string(record_text)

    def seal_file(self, file_bytes):
        """Encrypts raw binary data for the deepest tier of the hierarchy."""
        if not file_bytes:
            return None
        nonce = os.urandom(12)
        return nonce + self.aesgcm.encrypt(nonce, file_bytes, None)

    def open_text(self, encrypted_b64):
        """Universal Opener for Title and Record layers."""
        if not encrypted_b64:
            return ""
        try:
            raw = base64.b64decode(encrypted_b64)
            nonce, ciphertext = raw[:12], raw[12:]
            return self.aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        except Exception:
            return "[DECRYPTION_ERROR]"

    def open_file(self, encrypted_bytes):
        """Universal Opener for the File layer."""
        if not encrypted_bytes:
            return None
        try:
            nonce, ciphertext = encrypted_bytes[:12], encrypted_bytes[12:]
            return self.aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            return None

    def _encrypt_string(self, plain_text):
        """Internal helper for string-based encryption."""
        if not plain_text:
            return None
        nonce = os.urandom(12)
        ct = self.aesgcm.encrypt(nonce, plain_text.encode(), None)
        return base64.b64encode(nonce + ct).decode('utf-8')