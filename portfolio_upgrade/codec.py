from __future__ import annotations

import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"WV1"
KDF_ITERATIONS = 210_000


def derive_key(password: str, salt: bytes) -> bytes:
    if len(password) < 8:
        raise ValueError("Use a password with at least eight characters.")
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        KDF_ITERATIONS,
        dklen=32,
    )


def encrypt_message(message: str, password: str) -> bytes:
    if not message.strip():
        raise ValueError("Enter a message to protect.")
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, message.encode("utf-8"), MAGIC)
    return MAGIC + salt + nonce + ciphertext


def decrypt_message(payload: bytes, password: str) -> str:
    if len(payload) < 47 or not payload.startswith(MAGIC):
        raise ValueError("No valid WaveVault payload was found.")
    salt = payload[3:19]
    nonce = payload[19:31]
    ciphertext = payload[31:]
    key = derive_key(password, salt)
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, MAGIC).decode("utf-8")
    except Exception as exc:
        raise ValueError("The password is incorrect or the payload was modified.") from exc


def set_coefficient_parity(value: int, bit: int) -> int:
    """Return a nearby integer whose absolute parity matches bit.

    The full portfolio package applies this primitive to high-frequency
    coefficients from a reversible integer Haar transform and verifies the
    payload before returning a lossless PNG carrier.
    """
    if bit not in (0, 1):
        raise ValueError("Bit must be zero or one.")
    if abs(value) % 2 == bit:
        return value
    return value + 1 if value >= 0 else value - 1
