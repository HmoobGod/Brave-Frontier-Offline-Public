"""v216: independent adversarial probes for the v215 synthetic source checker.

No player saves, APK, app resources or actual unit evolution are accessed.
"""
from copy import deepcopy
from unittest.mock import patch
import hashlib
import json
import audit_bf_7star_typed_evolution_preflight_v21500 as audit

source = json.loads(audit.SOURCE.read_text(encoding='utf-8'))
manifest = json.loads(audit.MANIFEST.read_text(encoding='utf-8'))
original_source = audit.SOURCE.read_bytes()
original_manifest = audit.MANIFEST.read_bytes()
assert len(audit.recipe_rows()) == 12


def must_value_error(s, m):
    try:
        audit.recipe_rows(s, m)
    except ValueError:
        return
    raise AssertionError('source corruption unexpectedly accepted')


# A coordinated edit in BOTH checked manifests defeats the ordinary equality
# join. Only recomputing the canonical v130 row SHA against a pinned value
# distinguishes this from the exact source materials previously authenticated.
both_source = deepcopy(source)
both_manifest = deepcopy(manifest)
old_id = both_source['rows'][0][7][0][2]
assert old_id == both_manifest['rows'][0]['originalEvo']['materialSlots'][0]['id']
both_source['rows'][0][7][0][2] = old_id + 1
both_manifest['rows'][0]['originalEvo']['materialSlots'][0]['id'] = old_id + 1
assert both_source['typedRowsSha256'] == audit.ROWS_SHA  # attack keeps stale declared SHA
assert both_manifest['canonical12SourceSha256'] == audit.MANIFEST_SHA
must_value_error(both_source, both_manifest)

# Isolate the six-element 8-star set-completeness condition from the hash
# and cross-manifest joins: copy one legitimate 8-star form over another,
# update both test-only manifests AND substitute a matching test-only rows
# checksum. Without a complete six-element check, this would pass.
duplicate_source = deepcopy(source)
duplicate_manifest = deepcopy(manifest)
last_8star = -1
assert duplicate_source['rows'][last_8star][0] == 60017
assert duplicate_source['rows'][-3][0] == 50017
duplicate_source['rows'][last_8star] = deepcopy(duplicate_source['rows'][-3])
duplicate_manifest['rows'][last_8star] = deepcopy(duplicate_manifest['rows'][-3])
updated_sha = hashlib.sha256(json.dumps(
    duplicate_source['rows'], separators=(',', ':'), ensure_ascii=True
).encode()).hexdigest()
duplicate_source['typedRowsSha256'] = updated_sha
assert updated_sha != audit.ROWS_SHA
with patch.object(audit, 'ROWS_SHA', updated_sha):
    must_value_error(duplicate_source, duplicate_manifest)

# Consistently reject malformed source manifests, not only fail closed with
# unrelated AttributeError or TypeError tracebacks. Test non-dict rows,
# None for originalEvo, absent/bad typed material record and bad v130 row.
for bad_value in (None, [], 4, 'malformed'):
    corrupted = deepcopy(manifest)
    corrupted['rows'][0] = bad_value
    must_value_error(source, corrupted)
for bad_value in (None, [], 'malformed'):
    corrupted = deepcopy(manifest)
    corrupted['rows'][0]['originalEvo'] = bad_value
    must_value_error(source, corrupted)
for bad_value in (None, {}, 'malformed', [None]):
    corrupted = deepcopy(manifest)
    corrupted['rows'][0]['originalEvo']['materialSlots'] = bad_value
    must_value_error(source, corrupted)
for bad_value in (None, {}, 'malformed'):
    corrupted = deepcopy(source)
    corrupted['rows'][0] = bad_value
    must_value_error(corrupted, manifest)

# All positive cases still pass, including all source-verified 7/8-star forms.
expected = [10016, 10017, 20016, 20017, 30016, 30017,
            40016, 40017, 50016, 50017, 60016, 60017]
assert [r[0] for r in audit.recipe_rows()] == expected
assert original_source == audit.SOURCE.read_bytes()
assert original_manifest == audit.MANIFEST.read_bytes()
assert all(audit.preflight(r[0], {r[1]},
            {x[2]: sum(1 for y in r[7] if y[1] == 1 and y[2] == x[2])
             for x in r[7] if x[1] == 1},
            {110100: 1}, r[5], r[6])['original2022EvolutionAuthorized'] is False
           for r in audit.recipe_rows())
print('PASS v216: coordinated tampering SHA guard, six-element 8-star identity, malformed-source ValueError and no save mutation')
