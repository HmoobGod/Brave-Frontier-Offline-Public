# v213 — Fail-closed local battle-capture CLI safety regression

**Review follow-up to Claude's v212 PR #145 review. Research-only; no game mechanics, Android app, source encounter data, player saves, Gems, source provenance, or signing modifications.**

The v202 and v212 Python auditors previously rejected malformed/oversized decoded JSON but could emit a Python traceback on deeply nested, syntactically valid arrays: CPython's JSON decoder can raise \`RecursionError\` before our post-parse 32-depth bounded traversal runs.

## Changes
- Both local CLI main functions now classify \`RecursionError\` as invalid input, via the existing \`argparse.ArgumentParser.error\` exit-2 path. Existing size/depth/container/duplicate-key and strict-UTF8 policies are unchanged; the standalone \`inspect_bytes\` functions may still raise to their caller.
- New \`test_bf_capture_cli_fail_closed_v21300.py\` checks **both** CLIs with deeply nested JSON, missing files, duplicate keys, malformed JSON with a private-value sentinel, invalid UTF-8, scalar root and oversized input. Exit must be 2 with no traceback, no stdout and no sentinel on stderr. Input bytes remain untouched.
- Added adversarial 3-key example: two candidate battle fields plus the candidate AI field inside one object **must not** count as a complete co-located three-battle-field record.
- v212's output note now accurately states that JSON values are parsed but **never reported**, rather than saying they are never read.
- Add the targeted regression to the existing secret-free \`battle-capture-intake.yml\` research workflow and its path filters.

## Limitations
Only four public candidate keys are counted. Co-location is a syntactic grouping, not evidence of true packet boundaries, field semantics, enemy identities, wave order, boss fights, AI, reward/drop logic, or an authenticated original 2022 battle response. All original 2022 readiness flags remain permanently false in this patch. Do not share unredacted raw captures, saves, or credentials.

**Staging:** The PR is based on v212's exact-reviewed head, not released main. Retarget to main **only after** v212 is merged and current main is verified. Require independent review, exact-head successful targeted and Android CI, head-guarded merge, and post-merge CI. An APK/user save smoke check remains a separate gate for any future gameplay change.
