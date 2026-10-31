"""v220: independent read-only source/art byte gate, no Chromium or Android build."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import json
import zipfile

import prepare_bf_original_2022_dungeon_backdrops_v22000 as audit

cat, old, new = audit.verified_catalog()
assert len(old) == 29 and len(new) == 77
assert len(cat["dungeonToBackground"]) == 23
assert len(cat["imageSources"]) == 22
assert len(set(x[0] for x in old+new)) == 106
assert cat["changesCombat"] is False and cat["changesSaves"] is False
assert cat["visualFeatureOptIn"] is True
original = audit.COVERAGE.read_bytes()
original_zip = audit.ART.read_bytes()
assert hashlib.sha256(original_zip).hexdigest() == audit.ZIP_SHA
with zipfile.ZipFile(audit.ART) as z:
    assert z.testzip() is None
    expected = {"SOURCE_MANIFEST_V220.json"}
    expected |= {"content/dungeon/" + a["file"] for a in cat["imageSources"]
                 if not a["alreadyPackagedByV191"]}
    assert set(z.namelist()) == expected
    assert json.loads(z.read("SOURCE_MANIFEST_V220.json")) == cat
    for asset in cat["imageSources"]:
        if asset["alreadyPackagedByV191"]:
            b = (audit.ROOT/"source_assets/bf1/dungeon"/asset["file"]).read_bytes()
        else:
            b = z.read("content/dungeon/" + asset["file"])
        assert len(b) == asset["sizeBytes"], asset["file"]
        assert hashlib.sha256(b).hexdigest() == asset["sha256"], asset["file"]
        assert b[:2] == b"\\xff\\xd8" and b[-2:] == b"\\xff\\xd9", asset["file"]

# Tamper metadata-only catalog contents in temporary files, not production.
for mutation in ("duplicate", "wrong-background", "invented-runtime", "wrong-source"):
    altered = deepcopy(cat)
    if mutation == "duplicate":
        altered["dungeonToBackground"][1][0] = altered["dungeonToBackground"][0][0]
    elif mutation == "wrong-background":
        altered["dungeonToBackground"][0][1] = "dungeon_battle_20700.jpg"
    elif mutation == "invented-runtime":
        altered["changesCombat"] = True
    else:
        altered["sourceArchiveSha256"] = "0" * 64
    with TemporaryDirectory() as td:
        path = Path(td)/"adversarial-source.json"
        path.write_text(json.dumps(altered), encoding="utf8")
        with patch.object(audit, "COVERAGE", path):
            try:
                audit.verified_catalog()
            except (ValueError, AssertionError):
                pass
            else:
                raise AssertionError("tampered v220 source accepted: " + mutation)
assert audit.COVERAGE.read_bytes() == original
assert audit.ART.read_bytes() == original_zip
print("PASS v220: 106 exact source joins, 22 authentic original JPGs, 15 new, 4 adversarial probes, no writes")
