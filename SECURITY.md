# Security Policy

## Project scope

WaveVault is a portfolio reference implementation for authenticated encryption, reversible wavelet-domain payload embedding, and image scrambling. It is not an audited cryptographic product or an approved channel for sensitive data.

## Reporting a vulnerability

Please do not publish working exploit details, passphrases, private payloads, or malicious files in a public issue. Send a concise report to `nityaroshinikandula412@gmail.com` with:

- affected component and commit
- reproduction steps using synthetic data
- expected and observed behavior
- potential confidentiality, integrity, or availability impact
- proposed mitigation, when available

## Safe testing

- Use synthetic images and payloads only.
- Never reuse demonstration passphrases for real accounts or systems.
- Do not treat image scrambling as encryption.
- Reject unexpected file types and enforce conservative size limits.
- Keep cryptographic and image-processing dependencies current.

## Production expectations

A production implementation would require managed keys, TLS, authentication and authorization, strict resource limits, secure temporary storage, audit logging, dependency scanning, a documented binary format, independent cryptographic review, and an explicit threat model.
