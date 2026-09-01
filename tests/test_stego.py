import pytest

from app.stego import decode, encode, sample_carrier


def test_encode_decode_round_trip() -> None:
    protected = encode(sample_carrier(320, 240), "claims reference 4821", "correct horse battery").image_bytes
    assert decode(protected, "correct horse battery") == "claims reference 4821"


def test_wrong_password_fails() -> None:
    protected = encode(sample_carrier(320, 240), "private message", "correct password").image_bytes
    with pytest.raises(ValueError, match="incorrect|damaged"):
        decode(protected, "wrong password")


def test_plain_image_has_no_payload() -> None:
    with pytest.raises(ValueError, match="No WaveVault payload|readable"):
        decode(sample_carrier(320, 240), "correct password")
