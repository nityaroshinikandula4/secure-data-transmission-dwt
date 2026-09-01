# WaveVault Portfolio Upgrade

This review branch reframes the original secure-transmission project as a clear, auditable reference implementation.

## Evidence demonstrated

- PBKDF2-HMAC-SHA256 key derivation
- AES-GCM authenticated encryption
- Reversible integer Haar wavelet concepts
- Optional key-derived image-block scrambling
- Round-trip and wrong-password tests
- Explicit security limitations

## Review order

1. Read `portfolio_upgrade/README.md`.
2. Inspect `portfolio_upgrade/codec.py` for the authenticated-encryption boundary.
3. Run `pytest -q portfolio_upgrade/tests`.

This remains an educational reference build, not an audited secure-messaging protocol.
