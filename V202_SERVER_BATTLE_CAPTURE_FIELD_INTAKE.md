# v202 — Bounded local-only candidate battle-response field inventory

**Read-only research. This does not authenticate or reconstruct original 2022
enemy waves.** No runtime, APK, Java, JavaScript, Gradle, signing, wallet, Imp,
P.version=7 or `bf_global_offline_demo_v7` changes.

## Why this is necessary

BF Revive's 2026 recovery/bounty index reports that Gumi's original enemy
waves, enemy stats and boss skills were supplied by the server and not retained
in APK/OBB files. It identifies archived decoded `MissionStart` responses
as candidate evidence, including `U0v5IeJo` (monster rows),
`75t0sx9z` (monster groups), `pj41dy9g` (battle groups) and
`89ausgc4` (AI records). Public reference:
https://bfrevive.net/bounty/

These labels are **third-party research hints**, not an independently
authenticated decoder, byte-pinned 2022 capture or proven stage-to-enemy join.
The v175/v176 source scanners remain useful for client/master metadata; an
APK/master table by itself cannot establish every original battle response.
Archived 2014 or authored 2026 waves are not automatically original 2022 data.

## Use — decoded local JSON only

```bash
python audit_bf_server_battle_capture_fields_v20200.py --input /private/local/sanitized-decoded-response.json
```

- Input: a locally available **decoded JSON** object or array. Raw network
  captures (HAR/PCAP, encrypted payloads, compressed binary or SREE blobs)
  are **not decoded** by this script.
- Traverses nested arrays/objects without reading network headers,
  cookies, accounts or tokens as values. Exact *field-name presence only*.
- Enforces an 8 MiB input limit, 32-level nesting, 100,000 container nodes,
  unique JSON keys and valid UTF-8. Rejects malformed/oversized inputs.
- Prints a JSON report with the SHA-256 of the input, field-name counts and
  Boolean candidate flags only. **No source packet values, credentials,
  enemy IDs, personal metadata, monster stats, dates or response bodies** are
  printed, written, uploaded or committed.
- Presence of all three candidate battle fields is **not** enough to prove
  fields belong to the same quest or response; not enough to decode wave
  order, enemy identities, AI, drops, boss stats or 2022 source authenticity.
  The inspector keeps every original-2022 verified flag false.
- Synthetic regression
  `test_bf_server_battle_capture_fields_v20200.py` covers valid nested
  candidate keys, privacy and deterministic hashes, decoys, partial evidence,
  and seven malformed/unsafe inputs. It contains **no authentic captures**.
  `.github/workflows/battle-capture-intake.yml` runs that test in CI with
  no signing secret, APK or download dependency.

## Important privacy and provenance boundary

Do **not** upload unredacted HAR/PCAP files, access tokens, passwords or
original account saves to GitHub or public research repos. Redact sensitive
information before sharing artifacts. Keep original historical captures local.
Even a real 2014 decrypted response is evidence for 2014 until an
independent source establishes what was identical in 2022.

## Next evidence gate

Acquire a redacted, authenticated 2022 `MissionStart` reply (or a complete
unedited original battle video for a named mission), independently establish
the response decoder and stage join, compare enemy identities and wave order,
then ask Claude to review **any proposed playable gameplay change**.
Require exact-head Android CI, merge, merged-main CI and owner device/save test.
This PR **does not** close the v201 native 2022 encounter gate.
