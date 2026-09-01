from __future__ import annotations

import io
import os
import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps

from .crypto import decrypt_message, encrypt_message, permutation_seed
from .wavelet import carrier_indices, embed_bit, extract_bit, forward_channel, inverse_channel

MAGIC = b"WVT1"
SALT_BYTES = 16
LENGTH_BYTES = 4
HEADER_BYTES = len(MAGIC) + SALT_BYTES + LENGTH_BYTES
HEADER_BITS = HEADER_BYTES * 8
MAX_MESSAGE_BYTES = 16_384


@dataclass(frozen=True)
class EncodeResult:
    image_bytes: bytes
    width: int
    height: int
    capacity_bytes: int
    payload_bytes: int


def bytes_to_bits(payload: bytes) -> list[int]:
    return [(byte >> shift) & 1 for byte in payload for shift in range(7, -1, -1)]


def bits_to_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("Bit count must be divisible by eight.")
    output = bytearray()
    for offset in range(0, len(bits), 8):
        value = 0
        for bit in bits[offset:offset + 8]:
            value = (value << 1) | bit
        output.append(value)
    return bytes(output)


def _open_even_rgb(image_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except Exception as exc:  # Pillow raises several format-specific exceptions.
        raise ValueError("Upload a valid PNG or JPEG image.") from exc
    image = ImageOps.exif_transpose(image).convert("RGB")
    if image.width < 64 or image.height < 64:
        raise ValueError("Carrier image must be at least 64 × 64 pixels.")
    if image.width * image.height > 16_000_000:
        raise ValueError("Carrier image is too large for this demo (maximum 16 megapixels).")
    pad_right = image.width % 2
    pad_bottom = image.height % 2
    if pad_right or pad_bottom:
        image = ImageOps.expand(image, border=(0, 0, pad_right, pad_bottom), fill=None)
        # Copy edge pixels into the padded row/column to avoid a black seam.
        pixels = np.array(image)
        if pad_right:
            pixels[:, -1] = pixels[:, -2]
        if pad_bottom:
            pixels[-1, :] = pixels[-2, :]
        image = Image.fromarray(pixels.astype(np.uint8), mode="RGB")
    return image


def _save_png(rgb: np.ndarray) -> bytes:
    output = io.BytesIO()
    Image.fromarray(rgb.astype(np.uint8), mode="RGB").save(output, format="PNG", optimize=True)
    return output.getvalue()


def encode(image_bytes: bytes, message: str, password: str) -> EncodeResult:
    encoded_message = message.encode("utf-8")
    if len(encoded_message) > MAX_MESSAGE_BYTES:
        raise ValueError(f"Message exceeds the {MAX_MESSAGE_BYTES}-byte demo limit.")

    image = _open_even_rgb(image_bytes)
    rgb = np.array(image, dtype=np.uint8)
    blocks, height, width = forward_channel(rgb[:, :, 2])
    candidates = carrier_indices(blocks)
    if len(candidates) <= HEADER_BITS:
        raise ValueError("Carrier image does not contain enough stable wavelet blocks.")

    salt = os.urandom(SALT_BYTES)
    token = encrypt_message(message, password, salt)
    header = MAGIC + salt + len(token).to_bytes(LENGTH_BYTES, "big")
    header_bits = bytes_to_bits(header)
    token_bits = bytes_to_bits(token)
    available_payload_bits = len(candidates) - HEADER_BITS
    if len(token_bits) > available_payload_bits:
        capacity_bytes = max(0, available_payload_bits // 8)
        raise ValueError(f"Encrypted payload is too large for this carrier. Approximate encrypted capacity: {capacity_bytes} bytes.")

    for block_index, bit in zip(candidates[:HEADER_BITS], header_bits, strict=True):
        embed_bit(blocks[block_index], bit)

    payload_positions = candidates[HEADER_BITS:]
    random.Random(permutation_seed(password, salt)).shuffle(payload_positions)
    for block_index, bit in zip(payload_positions[:len(token_bits)], token_bits, strict=True):
        embed_bit(blocks[block_index], bit)

    rgb[:, :, 2] = inverse_channel(blocks, height, width)
    png = _save_png(rgb)
    return EncodeResult(
        image_bytes=png,
        width=width,
        height=height,
        capacity_bytes=available_payload_bits // 8,
        payload_bytes=len(token),
    )


def decode(image_bytes: bytes, password: str) -> str:
    image = _open_even_rgb(image_bytes)
    rgb = np.array(image, dtype=np.uint8)
    blocks, _, _ = forward_channel(rgb[:, :, 2])
    candidates = carrier_indices(blocks)
    if len(candidates) <= HEADER_BITS:
        raise ValueError("Image does not contain a readable WaveVault header.")

    try:
        header_bits = [extract_bit(blocks[index]) for index in candidates[:HEADER_BITS]]
    except ValueError as exc:
        raise ValueError("Image does not contain a readable WaveVault header.") from exc
    header = bits_to_bytes(header_bits)
    if header[:len(MAGIC)] != MAGIC:
        raise ValueError("No WaveVault payload was found in this image.")

    salt_start = len(MAGIC)
    salt = header[salt_start:salt_start + SALT_BYTES]
    length_start = salt_start + SALT_BYTES
    token_length = int.from_bytes(header[length_start:length_start + LENGTH_BYTES], "big")
    if token_length <= 0 or token_length > 1_000_000:
        raise ValueError("Embedded payload length is invalid.")

    required_bits = token_length * 8
    payload_positions = candidates[HEADER_BITS:]
    if required_bits > len(payload_positions):
        raise ValueError("Embedded payload is incomplete.")
    random.Random(permutation_seed(password, salt)).shuffle(payload_positions)
    try:
        token_bits = [extract_bit(blocks[index]) for index in payload_positions[:required_bits]]
    except ValueError as exc:
        raise ValueError("Embedded payload is damaged.") from exc
    return decrypt_message(bits_to_bytes(token_bits), password, salt)


def sample_carrier(width: int = 960, height: int = 640) -> bytes:
    x = np.linspace(0, 1, width, dtype=np.float64)
    y = np.linspace(0, 1, height, dtype=np.float64)[:, None]
    red = 65 + (80 * x)[None, :] + (25 * y)
    green = 110 + (95 * x)[None, :] - (30 * y)
    blue = 155 + (45 * x)[None, :] - (55 * y)
    rgb = np.stack([red, green, blue], axis=2)
    # Add broad shapes without saturated colors so every early block remains reversible.
    yy, xx = np.mgrid[0:height, 0:width]
    mountain = yy > (height * .78 - np.abs(xx - width * .36) * .62)
    ridge = yy > (height * .82 - np.abs(xx - width * .68) * .48)
    rgb[mountain] = np.array([31, 72, 84])
    rgb[ridge] = np.array([24, 58, 71])
    sun = (xx - width * .77) ** 2 + (yy - height * .22) ** 2 < (height * .075) ** 2
    rgb[sun] = np.array([245, 220, 125])
    return _save_png(np.clip(rgb, 0, 255).astype(np.uint8))
