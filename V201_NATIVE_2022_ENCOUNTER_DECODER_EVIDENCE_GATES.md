# v201 research — native 2022 encounter decoder evidence gates

**Status:** research-only planning document. No original 2022 enemy waves are authenticated by this document. No gameplay, save, APK, CI, or signing changes.

## Reusable verified foundation

- v152 checks 142 original 2022 mission-reference strings against pinned original mission master excerpts.
- v199 establishes 29 **opaque reference strings** across Mistral (34 missions, 8 distinct), Morgan (36, 7), St Lamia (36, 7), and unplayable Amdahl (36, 7).
- In v199, 6 opaque strings occur four times, 20 occur five times, and 3 occur six times. No cross-area full-string collisions were observed.
- Those tokens must **not** be interpreted as wave counts, enemy IDs, probabilities, or formations. The 2022 decoder/join table remains unverified.

## Evidence required before implementing any native encounter

1. **Provenance:** Identify the original 2022 Global client or master table bytes, exact path/version, cryptographic digest, and redistribution constraints. A third-party 2014 or 2021 table is a candidate only, never proof of 2022 behavior.
2. **Decoder:** Document and independently reproduce the exact original parsing / join path from a raw mission reference to an encounter-group record. Include failure behavior for unknown/malformed inputs. No heuristic positional assumptions.
3. **Formation:** For each proposed playable quest, prove the ordered stage-to-enemy mapping, multiplicities, and boss/end-wave designation from the decoded 2022 data. Any unresolved field remains unsupported, not filled from historical versions.
4. **Mechanics:** Independently authenticate stats, skills, turn logic, randomization, rewards, drop behavior, and mimics before asserting original parity for them.
5. **Reproducibility:** Ship a byte-pinned, non-sensitive fixture with a deterministic *read-only* comparison and adversarial negative tests (missing key, duplicate key, ambiguous join, invalid references, cross-area mismatch, corrupted digests).
6. **Safety:** A later runtime patch must be opt-in or narrowly staged, preserve current DEMO flow and v7 save compatibility, and be reviewed by Claude. Require exact-head successful CI, guarded merge, new merged-main successful CI, then owner Android smoke testing.

## Implementation boundary

The next implementation step is **source discovery**, not guessing formations. If no original 2022 decoder or joined enemy-group evidence can be authenticated, keep the native formation gate BLOCKED and report precisely what is missing. Do not repurpose v199's 29 tokens as unique enemy formations. Avoid importing old-era encounter data into playable original-mode code.

This document references the already-merged `V199_ORIGINAL_2022_REFERENCE_COLLISION_AUDIT.md` and its reproducible audit. The work described here is pending; it does not claim new source extraction, emulator tests, or green CI.
