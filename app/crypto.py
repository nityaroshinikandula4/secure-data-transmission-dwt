from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 480_000


def derive_key(password: str, salt: bytes) -> bytes:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_message(message: str, password: str, salt: bytes) -> bytes:
    if not message:
        raise ValueError("Message cannot be empty.")
    return Fernet(derive_key(password, salt)).encrypt(message.encode("utf-8"))


def decrypt_message(token: bytes, password: str, salt: bytes) -> str:
    try:
        return Fernet(derive_key(password, salt)).decrypt(token).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError) as exc:
        raise ValueError("The password is incorrect or the embedded payload is damaged.") from exc


def permutation_seed(password: str, salt: bytes) -> int:
    digest = hashlib.sha256(b"WaveVault-permutation-v1\0" + salt + password.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")
