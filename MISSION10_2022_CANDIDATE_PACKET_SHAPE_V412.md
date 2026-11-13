# Mission #10 — Local-only decoded candidate packet SHAPE audit (v412)

**Source diagnostics only. No original 2022 waves, AI, enemy identities or
drops were decoded, inferred, or added to gameplay.**

## What changed from earlier local capture tools

Existing v202 counts candidate names anywhere in a decoded JSON file.
Existing v212 counts candidate name co-location in the same object, including
scalar, empty and null values. Those tests can generate false leads.

v412 reuses v202/v212's strict UTF-8, duplicate-key rejection, 8 MiB cap,
32-depth cap, 100,000-container cap and input SHA-256. It additionally counts:
- Which of four public **candidate** keys have nonempty array/object values
  versus empty arrays/objects, null or scalar values.
- Objects containing all three candidate battle-field names **with nonempty
  data containers in that same object**.
- Objects containing all four candidate field names with nonempty containers.
- Candidate three-name objects containing any empty/null or scalar value.

The shape counts contain NO actual input values, identifiers, arrays, object
paths, token headers, mission IDs from input, enemy stats or reconstructed
groups. It emits only aggregate counts and SHA-256. Even if all four candidate
fields are nonempty, ALL original 2022 authenticity/semantic/join/readiness
flags remain false: this is a stronger lead for future reverse engineering,
**never a native formation proof**.

## Use locally, safely

    python3 audit_bf_server_battle_candidate_shapes_v41200.py --input /private/sanitized-decoded-response.json

Provide only locally sanitized and decoded JSON. Do not provide a raw HAR, PCAP,
account token, URL credential, personal save or private packet capture.
Nothing is sent to GitHub or printed beyond the safe summary. No live network
calls are made. Synthetic regressions intentionally include decoy token strings
and demonstrate the output cannot expose them.

## Next authentic 2022 gate

Original 2022 Mistral/Morgan quest metadata and wave counts exist in the
pinned source archive, but the 142 mission IDs and 29 reused opaque encounter
references do **not** establish a narrative mission ID to server encounter
group / ordered waves. A safely decoded, independently provenance-verified
original 2022 Global MissionStart response for Mission #10 is still needed
before discussing enemy identity, positions, stats, AI or item drops.

This branch neither edits the 2014 experimental practice arena nor imports
the donor's reconstructed 2014 mission data into native 2022 battles.
Main APK, v7 saves, no INTERNET, signing, app ID and player-only Auto/manual
fallback remain unchanged. Any future gameplay promotion needs a **separate**
Claude exact-head review, full signed Android CI, merge/owner device gate.
