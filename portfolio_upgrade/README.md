# WaveVault Reference Implementation

WaveVault demonstrates the separation between real cryptographic protection and educational image-hiding techniques.

## Security model

1. A password is stretched with PBKDF2-HMAC-SHA256 using a random salt.
2. AES-256-GCM encrypts and authenticates the message.
3. The resulting binary payload can be framed and embedded in high-frequency coefficients from a reversible integer Haar transform.
4. A lossless image format is required so coefficient changes survive transport.
5. Optional image-block scrambling is treated only as visual obfuscation—not encryption.

## Run the isolated tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r portfolio_upgrade/requirements.txt
pytest -q portfolio_upgrade/tests
```

## Production boundary

This is a portfolio and teaching implementation. A deployed secure-messaging product would require a reviewed protocol, managed keys, authenticated identities, replay protection, secure password exchange, rate limits, audit logging, file scanning, monitoring, and independent security assessment.
