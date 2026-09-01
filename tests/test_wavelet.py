import numpy as np

from app.wavelet import forward_block, forward_channel, inverse_block, inverse_channel


def test_block_transform_is_exact() -> None:
    pixels = (17, 92, 141, 233)
    assert inverse_block(forward_block(*pixels)) == pixels


def test_channel_round_trip_is_exact() -> None:
    channel = np.arange(64, dtype=np.uint8).reshape(8, 8) * 3
    blocks, height, width = forward_channel(channel)
    restored = inverse_channel(blocks, height, width)
    assert np.array_equal(channel, restored)
