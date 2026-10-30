# v214 — Private decoded-capture CLI error privacy hardening

**Research-only follow-up to the independent v213 review of PR #146. No native 2022 encounter proof, gameplay, Android, save schema, account, currency, signing, or original master data changes.**

Both local Python CLI wrappers now:
- Turn input read/stat errors (including permission errors and races) into a fixed non-disclosing argparse exit-2 error instead of an uncaught OSError traceback.
- Reject decoder failures, deeply nested JSON, malformed JSON and invalid UTF-8 with the same fixed error, never appending exception text, offending bytes, byte offsets, paths, or source content. This removes the existing v202 invalid-UTF8 byte/offset diagnostic exposure.
- Keep identical v202/v212 `inspect_bytes` report contracts and safety limits. Their standalone functions may still raise for caller handling; only CLI behavior is standardized.

`test_bf_capture_cli_error_privacy_v21400.py` verifies:
- 40-deep valid array (safe depth bound), 4096-deep nested object (decoder recursion), malformed text containing private sentinel, invalid UTF-8, empty file;
- both CLI exit codes 2 with empty stdout and no traceback, input marker, invalid byte literal or decoder offset in stderr;
- both CLI valid-input paths and unchanged research-only readiness flags;
- injected `Path.read_bytes()` and `Path.stat()` permission failures without reliance on OS permissions or root status.

The no-secrets research workflow runs this regression alongside v202/v212/v213.

**Staging:** PR is intentionally based on v213's exact-reviewed head (not merged `main`). Merge v212 #145 and then v213 #146 with their own CI/review gates before retargeting v214 to the current main and completing fresh CI. Key-name co-location is not authenticated original 2022 wave evidence.
