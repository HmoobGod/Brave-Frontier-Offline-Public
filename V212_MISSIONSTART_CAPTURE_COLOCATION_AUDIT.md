# v212 — Candidate MissionStart field co-location audit (local-only)

**Status:** research-only. No authenticated native 2022 battle waves, enemy rows, skills, AI or drops have been recovered by this change. No runtime/Android code, player save, quest, Gem, Imp, signing or application assets change.

## Motivation

v202 safely reports whether four public candidate field names occur *anywhere* in a decoded JSON document. That is too weak to distinguish an individual battle response from a file containing several unrelated packets. In particular, an archive may show all three candidate battle keys across different objects even when no individual object contains them together.

v212 adds a local read-only **same-JSON-object field-name co-location** audit, while retaining the v202 bounds and privacy restrictions.

## Usage

Run only on a locally **sanitized and decoded JSON** file, not on a raw HAR/PCAP or any encrypted/network payload:

    python audit_bf_server_battle_capture_colocation_v21200.py --input /private/sanitized-decoded-response.json

- Reuses v202's 8 MiB size ceiling, strict JSON duplicate-key rejection, UTF-8 requirement, 32-depth ceiling and 100,000-container bound.
- Reports the SHA-256 of the input, v202 candidate-key occurrence counts, the number of JSON objects with one/two/three/four literal candidate fields, the number containing all **three battle-key names together**, and the count containing all four including the candidate AI field.
- Does not print, export or store JSON values, row indices, object paths, headers, account information, mission identifiers, player saves or tokens. It does not produce a sanitized copy of the input.
- A common envelope, array or file containing keys in **separate child objects** does not count as same-object co-location.
- Field names may occur as scalar keys, empty lists, or arbitrary values: co-location is **not** schema validation, proof of equivalent packet provenance, or evidence that these are real decoded battle groups. No decoding or enemy ID joins are attempted.
- All native 2022 proof/readiness flags remain false, even when all four keys occur together. This is **never** a promotion to gameplay.

The synthetic regression covers nested non-co-located keys, all-four same-object keys, exactly-three objects, separate packet objects, text decoys, duplicate keys, invalid encoding, malformed JSON, oversized or overdeep inputs, node overload, deterministic output, CLI behavior, and no secret-value disclosure. Tests contain no authentic captures.

## Outstanding evidence

A dated, authenticated **original 2022 Global** battle response or equivalent source evidence is still necessary, with independently reproduced parsing and quest-to-group-to-ordered-wave joins, followed by enemy stat/skill/AI/drop verification. Candidate keys mentioned by community projects are research leads, not authenticated native formation claims. Do not place private packet captures or user-account tokens in this public repository.

CI in .github/workflows/battle-capture-intake.yml runs both v202 and v212 synthetic checks. The normal full Android workflow must also pass on the exact PR head. For research-only source/tools changes, device validation is not implied or claimed. Source/data promoted to live gameplay would need a separate Claude code review, exact-head CI, merged-main CI and owner device/save testing.
