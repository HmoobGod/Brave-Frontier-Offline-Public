"""v162: fail-closed downgrade/migration contract before original Gems go live.

Pure source guard: no player save or production wallet is modified.
"""
from pathlib import Path
import json
import re

R = Path(__file__).resolve().parent
pending = (R / "patch_bf_original_gem_pending_v16100.py").read_text(encoding="utf8")
ledger = (R / "patch_bf_original_gem_ledger_v16000.py").read_text(encoding="utf8")
workflow = (R / ".github/workflows/build-debug-apk.yml").read_text(encoding="utf8")
rows = json.loads((R / "source_data/bf_global_2022_dungeon_finale_eligibility_v156.json").read_text(encoding="utf8"))
eligible = sorted(row[0] for row in rows["rows"] if row[4] == 1)
ineligible = sorted(row[0] for row in rows["rows"] if row[4] != 1)
assert len(eligible) == len(set(eligible)) == 22
assert len(ineligible) == len(set(ineligible)) == 7
assert not (set(eligible) & set(ineligible))
assert rows["originalRewardFinales"] == 29

# New-first-clear evidence is local audit metadata, not a spendable entitlement.
assert "_bfGemV161Pending:[]" in pending
assert "previousCount!==0" in pending
assert "P._bfGemV160.legacyFinales.includes(id)" in pending
assert "P._bfGemV161Pending.includes(id)" in pending
assert "BF160_ORIGINAL_GEM_FINAL_IDS.includes(id)" in pending
assert "source.length>22" in pending
assert "id<=prev" in pending
assert "clears[id]<=0" in pending
assert "P._bfGemV161Pending.sort((a,b)=>a-b)" in pending

# Preserve same canonical storage transaction and save version for upgrade.
assert "SAME atomic v7 JSON save write" in ledger
assert "P.version=7" in pending
assert "out._bfGemV161Pending=bf161ValidateOriginalPending" in pending
assert "P._bfGemV161Pending=bf161ValidateOriginalPending" in pending
assert "localStorage.setItem(SAVE_KEY,JSON.stringify(P))" in ledger
assert "balance:0,paidFinales:[]" in ledger
assert not re.search(r"\\.balance\\s*(?:\\+\\+|\\+=|=\\s*[1-9])", pending)
assert "test_bf_original_gem_pending_v16100.py" in workflow

# A downgraded APK can discard unknown namespaced fields on its next save.
# Therefore no actual Gem payout may be enabled without a separate backup,
# upgrade and downgrade validation gate.
assert "P._bfGemV160.balance+=" not in pending
print("PASS v162: 22/7 source eligibility, canonical v7 pending ledger, zero payout and downgrade safety gate")
