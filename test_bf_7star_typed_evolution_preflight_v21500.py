"""v215: original 2022 typed starter material preflight, synthetic non-saving tests."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import audit_bf_7star_typed_evolution_preflight_v21500 as v

rows = v.recipe_rows()
assert len(rows) == 12
assert len([r for r in rows if r[2] == 7]) == 6
assert len([r for r in rows if r[2] == 8]) == 6
inputs = [v.SOURCE, v.MANIFEST, v.ROOT / 'app/src/main/assets/index.html']
before_hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs]


def synthetic(r):
    target, previous, _, _, _, zel, karma, materials = r
    units = Counter(m[2] for m in materials if m[1] == 1)
    items = Counter(m[2] for m in materials if m[1] == 2)
    return {
        'target': target, 'owned_forms': {previous},
        'unit_materials': dict(units), 'original_items': dict(items),
        'zel': zel, 'karma': karma
    }


for row in rows:
    data = synthetic(row)
    original = deepcopy(data)
    result = v.preflight(**data)
    assert result['syntheticResourceCoverage'] is True, row[0]
    assert result['sourceTargetId'] == row[0]
    assert result['sourcePreviousFormId'] == row[1]
    assert result['sourceOriginalItemCounts'] == {110100: 1}
    assert result['sourceMaterialUnitCounts'] == dict(Counter(
        m[2] for m in row[7] if m[1] == 1
    ))
    assert result['missingSyntheticItemCounts'] == {}
    assert result['missingSyntheticUnitCounts'] == {}
    assert data == original, 'preflight mutated caller input'
    assert result == v.preflight(**data), 'nondeterministic preflight'
    for gate in (
        'original2022ExpAndLevelRulesVerified',
        'original2022VisualAnimationRulesVerified',
        'original2022EvolutionInventorySemanticsVerified',
        'original2022EvolutionAuthorized', 'changesPlayability',
        'readsOrWritesPlayerSaves',
    ):
        assert result[gate] is False, (row[0], gate)

    # Item ID 110100 in unit materials can never substitute for the original item.
    no_stone = deepcopy(data)
    no_stone['original_items'] = {}
    no_stone['unit_materials'][110100] = 999
    failed = v.preflight(**no_stone)
    assert failed['syntheticResourceCoverage'] is False
    assert failed['missingSyntheticItemCounts'] == {110100: 1}
    assert failed['original2022EvolutionAuthorized'] is False

    # Missing ownership, duplicated target, lacking money/units must fail.
    missing_owner = deepcopy(data)
    missing_owner['owned_forms'].clear()
    assert not v.preflight(**missing_owner)['syntheticResourceCoverage']
    already_owned = deepcopy(data)
    already_owned['owned_forms'].add(row[0])
    assert not v.preflight(**already_owned)['syntheticResourceCoverage']
    money = deepcopy(data)
    money['zel'] = row[5] - 1
    assert not v.preflight(**money)['syntheticResourceCoverage']
    if row[6]:
        low_karma = deepcopy(data)
        low_karma['karma'] = row[6] - 1
        assert not v.preflight(**low_karma)['syntheticResourceCoverage']
    first_material = row[7][0][2]
    short_unit = deepcopy(data)
    short_unit['unit_materials'][first_material] -= 1
    assert not v.preflight(**short_unit)['syntheticResourceCoverage']
    assert v.preflight(**short_unit)['missingSyntheticUnitCounts'][first_material] == 1

# Exact duplicate-material multiplicity: the 8-star fire line needs 2 of 10354.
eight = synthetic(next(r for r in rows if r[0] == 10017))
assert eight['unit_materials'][10354] == 2
eight['unit_materials'][10354] = 1
assert v.preflight(**eight)['missingSyntheticUnitCounts'] == {10354: 1}

# Bad input is rejected instead of silently coerced.
def rejects(callable_):
    try:
        callable_()
    except (ValueError, TypeError, KeyError):
        return
    raise AssertionError('unverified preflight data accepted')


valid = synthetic(rows[0])
rejects(lambda: v.preflight(True, {10015}, {}, {110100: 1}, 1500000, 0))
rejects(lambda: v.preflight(10016, {True}, {}, {110100: 1}, 1500000, 0))
rejects(lambda: v.preflight(**dict(valid, zel=True)))
rejects(lambda: v.preflight(**dict(valid, karma=-1)))
rejects(lambda: v.preflight(**dict(valid, original_items={110100: 0.5})))
rejects(lambda: v.preflight(**dict(valid, unit_materials={10354: -1})))
rejects(lambda: v.preflight(**dict(valid, target=999999)))

source = json.loads(v.SOURCE.read_text(encoding='utf8'))
manifest = json.loads(v.MANIFEST.read_text(encoding='utf8'))


def corrupt_source(edit):
    copy = deepcopy(source)
    edit(copy)
    rejects(lambda: v.recipe_rows(copy, manifest))


def corrupt_manifest(edit):
    copy = deepcopy(manifest)
    edit(copy)
    rejects(lambda: v.recipe_rows(source, copy))


corrupt_source(lambda x: x.update(typedRowsSha256='0' * 64))
corrupt_source(lambda x: x['rows'][0][7][-1].__setitem__(1, 1))
corrupt_source(lambda x: x['rows'][0][7][-1].__setitem__(2, 110101))
corrupt_source(lambda x: x['rows'][0].__setitem__(5, 0))
corrupt_source(lambda x: x.update(saveMutation=True))
corrupt_source(lambda x: x['rows'].pop())
corrupt_manifest(lambda x: x.update(canonical12SourceSha256='0' * 64))
corrupt_manifest(lambda x: x['rows'][0].update(unitId=10017))
corrupt_manifest(lambda x: x['rows'][0]['originalEvo']['materialSlots'][-1].update(type=1))

assert before_hashes == [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs]
script = (v.ROOT / 'audit_bf_7star_typed_evolution_preflight_v21500.py').read_text('utf8')
for forbidden in ('localStorage', 'saveProgress(', 'P.materials[', 'P.evolutions[',
                  'MainActivity.java', 'patch_bf_', 'request.get(', 'fetch('):
    assert forbidden not in script, forbidden
print('PASS v215: 12 source-exact typed recipes, synthetic 7/8-star resource coverage, corruption and v7 no-write guards')
