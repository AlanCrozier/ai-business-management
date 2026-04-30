"""
Encryption service — Fernet symmetric encryption for service account JSON blobs.

The encryption key is read from the SA_ENCRYPTION_KEY environment variable.
If missing, a new key is auto-generated and saved to .env on first run.
"""
import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Load .env so the key is always available (even from CLI scripts)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

_fernet_instance: Fernet | None = None


def _get_or_create_key() -> bytes:
    """Return the Fernet key, auto-generating one if needed."""
    key = os.environ.get("SA_ENCRYPTION_KEY")
    if key:
        return key.encode()

    # Auto-generate and persist to .env
    new_key = Fernet.generate_key()
    env_path = Path(__file__).resolve().parent.parent / ".env"

    # Append to .env (create if missing)
    with open(env_path, "a") as f:
        f.write(f"\nSA_ENCRYPTION_KEY={new_key.decode()}\n")

    os.environ["SA_ENCRYPTION_KEY"] = new_key.decode()
    logger.warning(
        "Generated new SA_ENCRYPTION_KEY and saved to %s. "
        "Back this up — losing it means stored service accounts become unreadable.",
        env_path,
    )
    return new_key


def _get_fernet() -> Fernet:
    """Lazy-init singleton Fernet instance."""
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(_get_or_create_key())
    return _fernet_instance


def encrypt(plaintext: str) -> bytes:
    """Encrypt a plaintext string → ciphertext bytes."""
    return _get_fernet().encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes) -> str:
    """Decrypt ciphertext bytes → plaintext string."""
    return _get_fernet().decrypt(ciphertext).decode("utf-8")
