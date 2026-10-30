"""v219: independent raw-byte pin for committed v127 source/readiness manifest.

All adversarial edits occur on temporary files. No original source artifact,
Android code, original evolution eligibility, live saves or APK is modified.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import audit_bf_7star_typed_evolution_preflight_v21500 as audit

# This expected hash is pinned independently from the audit's declaration and
# from the v127/v130 self-declared canonical-twelve source tuple SHA.
EXPECTED_FILE_SHA256 = "2fb14fda2d9a291df756d0e2332b68ded1929d8618e50159e899b68b5829146e"
original_manifest = audit.MANIFEST.read_bytes()
original_source = audit.SOURCE.read_bytes()
assert sha256(original_manifest).hexdigest() == EXPECTED_FILE_SHA256
assert audit.MANIFEST_FILE_SHA256 == EXPECTED_FILE_SHA256
assert len(audit.recipe_rows()) == 12
original = json.loads(original_manifest)

# The pre-existing canonical12 digest does not cover metadata or whitespace.
# Both of these valid JSON edits leave all twelve original recipe rows intact.
caution_changed = original_manifest.replace(
    b'"caution":"SOURCE PREPARATION ONLY.',
    b'"caution":"source PREPARATION ONLY.', 1
)
whitespace_changed = original_manifest.replace(b'"schema":', b'"schema" :', 1)
for label, modified in (
    ("noncanonical caution metadata", caution_changed),
    ("formatting-only whitespace", whitespace_changed),
):
    assert modified != original_manifest, label
    parsed = json.loads(modified)
    assert parsed["rows"] == original["rows"], label
    assert parsed["canonical12SourceSha256"] == original["canonical12SourceSha256"]
    with TemporaryDirectory() as tmp:
        candidate = Path(tmp) / "synthetic-v127-manifest.json"
        candidate.write_bytes(modified)
        with patch.object(audit, "MANIFEST", candidate):
            try:
                audit.recipe_rows()
            except ValueError as exc:
                assert str(exc) == "source manifest file checksum mismatch", (label, exc)
            else:
                raise AssertionError("modified on-disk original manifest accepted: " + label)

# In-memory synthetic fixtures remain supported by explicit arguments; the
# raw-file checksum is a DISK input gate, not a signed JSON/object signature.
synthetic_source = json.loads(original_source)
synthetic_manifest = deepcopy(original)
assert len(audit.recipe_rows(synthetic_source, synthetic_manifest)) == 12
assert len(audit.recipe_rows(source=synthetic_source)) == 12
assert audit.MANIFEST.read_bytes() == original_manifest
assert audit.SOURCE.read_bytes() == original_source
print("PASS v219: complete raw v127 manifest byte-pin, synthetic mutations and no writes")
