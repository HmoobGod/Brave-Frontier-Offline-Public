# Complete progress and storage audit for source screenshots

Local candidate based only on merged main `c59c73dff94a9dcc7536b90525202d946a26c822`.
No numbered release milestone is assigned. The earlier local prototype named
“v273 capture audit” predates synchronization with the authoritative tracker;
actual merged v273 is Training cost guidance, PR #208. The prototype is preserved
separately and must not replace that work.

## Problem and change

The v263 navigation runner compared squad, Zel, Gems and one save string; the
v272 nested runner compared additional selected player fields. They could miss
quest/dialogue/inventory changes, other save keys and writes later undone.
Both now share `bf_capture_progress_audit.py`: a fresh synthetic in-memory
storage implementation, a snapshot of the entire JSON player object and all
storage entries, and a monotonic count of setItem/removeItem/clear calls.
After default initialization and after each screenshot, all three must match.
Even removing an absent key, clearing empty storage, or writing the same value
fails the read-only navigation gate. Receipts add full-player/storage equality
flags and zero storageWriteCalls since baseline without exposing save contents.

The guard is test infrastructure; it is not added to Android assets. v263 now
installs synthetic storage before boot using a browser init script; v272 keeps
its existing opaque-origin, memory-only initialization. No existing storage or
owner profile is mounted. Progress snapshots cannot detect a transient in-memory
player change that is completely restored between samples; storage method calls
are counted even when their effects are restored. This does not prove native
WebView localStorage durability or canonical save parser correctness.

## Verification

`python3 test_bf_capture_progress_audit.py --source-only` runs the actual JavaScript
expressions in Node, checks both runners use the guard and verifies CI wiring.
`--browser` also executes the actual Python comparison against isolated Chromium.
Ten negative cases cover quest clears, dialogue, inventory, Training spent,
other-key and primary-key writes, write/remove restoration, absent remove,
empty clear, and same-value writes. Read-only positive controls must pass.

The source check runs in Android Back/UI preflight; the browser check runs before
screenshot capture in signed Android CI. Run the existing screenshot commands
against the full CI-prepared source copy for 10 navigation and 12 nested receipts.
Local results and exact candidate identity are recorded in the master tracker.
New signed CI is pending; browser/source checks are not Android device acceptance.

## Integration boundary

This branch contains no unmerged v274–v278 code and changes no gameplay, save
schema, original assets, HTML, Android code, signing or installed APK. The owner authorizes isolated feature-branch publication and draft PR preparation.
Automatic merging is disabled. Existing APKs
and authentic owner progress remain untouched.

Keep separate from the tracker's v278.1-R2 screenshot-distinctness and R4.1 Home
accessibility proposals. This audit does not repair or certify Save Controls
screenshot uniqueness/visibility. Future integration must reconcile edits to the
same screenshot runner and rerun source/browser/signed CI on the final base.
Codex-led review follows the current master policy; historical mandatory-Claude
notes are not a new review requirement. Merges remain owner-controlled; APK installation, public releases and real-save
operations require explicit authorization.

## Verified local checkpoint — November 4, 2026

- Full current-main preparation: 63 CI preparation commands passed in an isolated
  source copy; no old APK or prepared onboarding files were overwritten.
- Six applicable source preflights: 54 commands passed (44 Back/UI, 6 integrated
  UI, and one each touch, navigation budget, dungeon source, item gallery).
- Node and Chromium: all ten negative cases detected, read-only positives passed.
- Both actual prepared-source runners: 22/22 image hashes and byte counts verified,
  complete player/storage unchanged, zero storage calls since initialization,
  no missing/external assets. Exactly 20 distinct hashes confirms the already
  tracked duplicate Save Controls evidence; this is not 22 distinct-view acceptance.
- The pre-existing unsigned onboarding APK still matches its recorded SHA-256.
- At this checkpoint source work was local-only; no signed candidate build or real device test.

The initial six-workflow shell runner recognized only `python3` and stopped on
one workflow's `python` spelling after 52 successful commands. The two remaining
source checks were then run directly and passed; this was runner discovery,
not a failing product test. Evidence logs and manifests live outside the branch
under `/workspace/work/`.
