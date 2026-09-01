# Portfolio Architecture Notes

## Encode flow

1. The client submits a carrier image, payload, passphrase, and optional scrambling settings.
2. The service validates file type, dimensions, payload size, and requested parameters.
3. PBKDF2 derives an encryption key from the passphrase and a random salt.
4. AES-GCM encrypts and authenticates the payload with a random nonce.
5. A compact versioned frame stores the salt, nonce, ciphertext length, and ciphertext.
6. The image is converted with a reversible integer Haar transform.
7. Capacity is checked before frame bits are embedded into selected coefficients.
8. Optional block scrambling uses a deterministic key-derived permutation.
9. The encoded carrier is returned with metadata required for the inverse flow.

## Decode flow

1. The service reverses the block permutation when enabled.
2. It extracts and validates the framed payload from transformed coefficients.
3. PBKDF2 recreates the key using the stored salt and supplied passphrase.
4. AES-GCM authenticates the frame before returning plaintext.
5. Authentication failure produces a clear error rather than partially recovered data.

## Important design choices

### Authenticated encryption is the security boundary

Wavelet embedding and visual scrambling do not replace cryptography. AES-GCM provides confidentiality and integrity; the image operations demonstrate a reversible carrier workflow.

### Integer transform for exact reconstruction

A lifting-style integer Haar transform avoids floating-point drift during a round trip.

### Capacity validation before mutation

The service calculates the available coefficient capacity and rejects oversized payloads before changing the image.

### Explicit framing and versioning

A frame header makes extraction deterministic and leaves room for future format migration.

## Production hardening backlog

- Replace passphrase-only workflows with managed keys or envelope encryption
- Define and publish a versioned binary-format specification
- Add streaming and strict decompression/file-bomb protections
- Add metadata-stripping policy and content-type verification
- Add interoperability fixtures across runtimes and image libraries
- Perform independent cryptographic and steganalysis review
- Add rate limits, authentication, audit logs, and secure temporary-file handling
