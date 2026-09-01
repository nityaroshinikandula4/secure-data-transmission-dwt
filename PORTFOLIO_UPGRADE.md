# WaveVault — Recruiter-Facing Project Overview

WaveVault is a reversible secure-data transmission reference implementation that combines authenticated encryption with an integer Haar discrete wavelet transform and key-derived image scrambling. The project demonstrates how a security workflow, image-processing pipeline, API, tests, and usable interface can be connected end to end.

## Engineering highlights

- PBKDF2-based key derivation from a user passphrase and random salt
- AES-GCM authenticated encryption for confidentiality and tamper detection
- Reversible integer Haar wavelet transform for lossless coefficient reconstruction
- Framed payload embedding with capacity validation before modification
- Optional key-derived block scrambling and inverse reconstruction
- Round-trip verification covering encode, transmit, decode, authenticate, and recover
- FastAPI endpoints and a responsive studio interface in the complete project package
- Automated tests for cryptographic failure paths, capacity checks, and successful recovery

## Pipeline

```text
Plaintext or file bytes
        |
        v
PBKDF2 key derivation + AES-GCM
        |
        v
Framed encrypted payload
        |
        v
Integer Haar DWT coefficient embedding
        |
        v
Key-derived image block scrambling
        |
        v
Transmitted carrier image
        |
        v
Inverse scramble + extract + authenticate + decrypt
```

## Responsible framing

This is a portfolio reference build, not a standardized steganographic protocol or a claim of undetectability. Security comes from authenticated encryption; transform-domain embedding and scrambling are transport demonstrations. A production system would require independent cryptographic review, a versioned binary format, strict file limits, key-management infrastructure, metadata handling, compatibility tests, and threat-model documentation.

## Recommended repository topics

`python` · `fastapi` · `cryptography` · `aes-gcm` · `discrete-wavelet-transform` · `image-processing` · `secure-transmission`
