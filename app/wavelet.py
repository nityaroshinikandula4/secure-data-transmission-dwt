from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def ceil_half(value: int) -> int:
    return (value + 1) // 2


@dataclass
class CoeffBlock:
    ll: int
    lh: int
    hl: int
    hh: int


def forward_block(a: int, b: int, c: int, d: int) -> CoeffBlock:
    top_sum = (a + b) // 2
    top_diff = a - b
    bottom_sum = (c + d) // 2
    bottom_diff = c - d
    return CoeffBlock(
        ll=(top_sum + bottom_sum) // 2,
        lh=top_sum - bottom_sum,
        hl=(top_diff + bottom_diff) // 2,
        hh=top_diff - bottom_diff,
    )


def inverse_block(block: CoeffBlock) -> tuple[int, int, int, int]:
    top_sum = block.ll + ceil_half(block.lh)
    bottom_sum = block.ll - (block.lh // 2)
    top_diff = block.hl + ceil_half(block.hh)
    bottom_diff = block.hl - (block.hh // 2)
    a = top_sum + ceil_half(top_diff)
    b = top_sum - (top_diff // 2)
    c = bottom_sum + ceil_half(bottom_diff)
    d = bottom_sum - (bottom_diff // 2)
    return a, b, c, d


def forward_channel(channel: np.ndarray) -> tuple[list[CoeffBlock], int, int]:
    if channel.ndim != 2:
        raise ValueError("Expected a single image channel.")
    height, width = channel.shape
    if height % 2 or width % 2:
        raise ValueError("Channel dimensions must be even.")
    blocks: list[CoeffBlock] = []
    for row in range(0, height, 2):
        for col in range(0, width, 2):
            blocks.append(forward_block(
                int(channel[row, col]), int(channel[row, col + 1]),
                int(channel[row + 1, col]), int(channel[row + 1, col + 1]),
            ))
    return blocks, height, width


def inverse_channel(blocks: list[CoeffBlock], height: int, width: int) -> np.ndarray:
    expected = (height // 2) * (width // 2)
    if len(blocks) != expected:
        raise ValueError(f"Expected {expected} blocks, received {len(blocks)}.")
    output = np.zeros((height, width), dtype=np.uint8)
    index = 0
    for row in range(0, height, 2):
        for col in range(0, width, 2):
            pixels = inverse_block(blocks[index])
            if any(pixel < 0 or pixel > 255 for pixel in pixels):
                raise ValueError("Wavelet coefficient adjustment would exceed the 8-bit image range.")
            output[row, col], output[row, col + 1], output[row + 1, col], output[row + 1, col + 1] = pixels
            index += 1
    return output


def target_hh(block: CoeffBlock, bit: int) -> int:
    if bit not in (0, 1):
        raise ValueError("Bit must be 0 or 1.")
    group = block.hh // 4
    return (4 * group) + (1 if bit == 0 else 2)


def is_carrier_block(block: CoeffBlock) -> bool:
    # Both bit states use residues inside the same group of four, so the group
    # remains stable after embedding and extraction can select identical blocks.
    for bit in (0, 1):
        candidate = CoeffBlock(block.ll, block.lh, block.hl, target_hh(block, bit))
        if any(pixel < 0 or pixel > 255 for pixel in inverse_block(candidate)):
            return False
    return True


def carrier_indices(blocks: list[CoeffBlock]) -> list[int]:
    return [index for index, block in enumerate(blocks) if is_carrier_block(block)]


def embed_bit(block: CoeffBlock, bit: int) -> None:
    if not is_carrier_block(block):
        raise ValueError("Selected block cannot safely represent both bit states.")
    block.hh = target_hh(block, bit)


def extract_bit(block: CoeffBlock) -> int:
    residue = block.hh % 4
    if residue == 1:
        return 0
    if residue == 2:
        return 1
    raise ValueError("Carrier block does not contain a WaveVault bit marker.")
