import pytest

from portfolio_upgrade.codec import decrypt_message, encrypt_message, set_coefficient_parity


def test_encryption_round_trip() -> None:
    payload = encrypt_message("Protected claims reference 4821", "correct-horse")
    assert decrypt_message(payload, "correct-horse") == "Protected claims reference 4821"


def test_wrong_password_fails_authentication() -> None:
    payload = encrypt_message("Sensitive message", "correct-horse")
    with pytest.raises(ValueError, match="incorrect|modified"):
        decrypt_message(payload, "wrong-password")


def test_coefficient_parity() -> None:
    for value in (-8, -3, 0, 5, 12):
        for bit in (0, 1):
            assert abs(set_coefficient_parity(value, bit)) % 2 == bit
