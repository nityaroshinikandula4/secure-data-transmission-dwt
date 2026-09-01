## Summary

Describe the secure-transmission or image-processing behavior this change addresses.

## What changed

- 

## Validation

- [ ] Encode/decode round-trip tests pass
- [ ] Wrong-passphrase and tamper-detection paths remain covered
- [ ] Payload-capacity validation is tested
- [ ] Image reconstruction is deterministic for supported inputs
- [ ] No real secrets, private payloads, or sensitive images are included
- [ ] Documentation distinguishes encryption from embedding and scrambling

## Security review

Explain any change to key derivation, nonce or salt handling, frame parsing, authenticated data, coefficient selection, temporary files, or resource limits.

## Screenshots or examples

Include a studio screenshot or a synthetic round-trip example when the interface or output format changes.
