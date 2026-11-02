"""v244: audit every test's Home-nav byte ceiling against Android's loader.

This source-only gate scans *all* test_*.py files (not just the historical 27),
tracks nav JS/CSS variables, and guards the exact nav-only loader allowance.
Actual packaged/gameplay tests remain in the full Android workflow.
"""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
WORKFLOW = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
CAP = 128 * 1024

LEGACY = (
    "test_bf_quest_english_data_v048.py",
    "test_bf_remains_mirza_v049.py",
    "test_bf_monsters_nest_v050.py",
    "test_bf_tower_of_mistral_v051.py",
    "test_bf_original_bb_power.py",
)
PACKAGED = tuple("test_bf_packaged_" + part + ".py" for part in (
    "five_star_starters", "header_status_v054", "historical_encounters_v120",
    "historical_wave_lab_v200", "monster_training_v053", "more_second_stage",
    "original_battle_dossier_v400", "original_mission_evidence_v060",
    "other_five_star", "other_six_star", "playable_attack_frames_v065",
    "playable_hit_inspector_v070", "playable_identity", "quest_journal_v110",
    "six_evolutions", "six_star_starters", "source_crosscheck_v150",
    "squad_training_v250", "story_continue_v101", "tactical_rounds_v300",
    "tactical_undo_v350", "tower_formations_v055",
))
EXPECTED = set(LEGACY + PACKAGED)
assert len(EXPECTED) == 27

# Verify the actual exact-name Android selector, not just a substring that could
# become a broader OR condition, while preserving the separate general UI limit.
assert re.search(r"\bUI_RESOURCE_LIMIT_BYTES\s*=\s*64\s*\*\s*1024\s*;", JAVA)
assert re.search(r"\bNAV_RESOURCE_LIMIT_BYTES\s*=\s*128\s*\*\s*1024\s*;", JAVA)
assert re.search(
    r"private static int packagedUiResourceLimit\(String file\)\s*\{\s*"
    r'return\s+"bf_home_nav\.js"\.equals\(file\)\s*\|\|\s*'
    r'"bf_home_nav\.css"\.equals\(file\)\s*'
    r"\?\s*NAV_RESOURCE_LIMIT_BYTES\s*:\s*UI_RESOURCE_LIMIT_BYTES\s*;\s*\}",
    JAVA,
)
assert 'final int maxBytes = packagedUiResourceLimit(file);' in JAVA
assert 'if (out.size() + count > maxBytes) throw new IOException("Oversized UI resource");' in JAVA

def integer_value(expr):
    if isinstance(expr, ast.Constant) and type(expr.value) is int:
        return expr.value
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mult):
        a, b = integer_value(expr.left), integer_value(expr.right)
        return a * b if a is not None and b is not None else None
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Pow):
        a, b = integer_value(expr.left), integer_value(expr.right)
        return a ** b if a is not None and b is not None and b < 20 else None
    return None

def names_targeted(target):
    return {node.id for node in ast.walk(target) if isinstance(node, ast.Name)}

def nav_aliases(tree):
    """Track assigned aliases for assets or nav-derived sizes, including in functions."""
    assignments = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if node.value is not None:
                assignments.append((set().union(*(names_targeted(t) for t in targets)), node.value))
    aliases = set()
    for _ in range(len(assignments) + 1):
        before = len(aliases)
        for targets, value in assignments:
            source = ast.unparse(value)
            direct = any(name in source for name in ("bf_home_nav.js", "bf_home_nav.css"))
            refers = any(isinstance(n, ast.Name) and n.id in aliases for n in ast.walk(value))
            if direct or refers:
                aliases.update(targets)
        if len(aliases) == before:
            break
    return aliases

def references_nav_length(expr, aliases):
    if isinstance(expr, ast.Name):
        return expr.id in aliases
    if not isinstance(expr, ast.Call) or not isinstance(expr.func, ast.Name) or expr.func.id != "len":
        return False
    if len(expr.args) != 1:
        return False
    arg = expr.args[0]
    return ("bf_home_nav.js" in ast.unparse(arg)
            or "bf_home_nav.css" in ast.unparse(arg)
            or any(isinstance(n, ast.Name) and n.id in aliases for n in ast.walk(arg)))

def nav_limits(tree):
    aliases = nav_aliases(tree)
    found = []
    for statement in ast.walk(tree):
        if not isinstance(statement, ast.Assert):
            continue
        for compare in (n for n in ast.walk(statement.test) if isinstance(n, ast.Compare)):
            terms = [compare.left] + compare.comparators
            for left, op, right in zip(terms, compare.ops, terms[1:]):
                if references_nav_length(left, aliases) and isinstance(op, (ast.Lt, ast.LtE)):
                    limit, inclusive = integer_value(right), isinstance(op, ast.LtE)
                elif references_nav_length(right, aliases) and isinstance(op, (ast.Gt, ast.GtE)):
                    limit, inclusive = integer_value(left), isinstance(op, ast.GtE)
                else:
                    continue
                if limit is not None:
                    assert not any(isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or)
                                   for n in ast.walk(statement.test)), (
                        "nav size assertion has OR bypass", statement.lineno)
                    found.append((statement.lineno, limit, inclusive))
    return found

seen = {}
violations = []
for path in sorted(ROOT.glob("test_*.py")):
    tree = ast.parse(path.read_text("utf8"), filename=path.name)
    limits = nav_limits(tree)
    for lineno, limit, inclusive in limits:
        if not 65536 < limit <= CAP:
            violations.append((path.name, lineno, limit, inclusive))
    if limits:
        seen[path.name] = limits

assert not violations, ("stale or unsafe nav asset size assertions across all tests", violations)

for filename in EXPECTED:
    assert filename in seen and len(seen[filename]) == 1, (
        filename, "missing or ambiguous nav JS 128KiB assertion", seen.get(filename))
    assert seen[filename][0][1:] == (CAP, True), (
        filename, "known historical nav check must be exactly <=128KiB", seen[filename])
    assert re.search(r"\bpython3?\s+" + re.escape(filename) + r"\b", WORKFLOW), (
        filename, "not run by full Android build")

assert WORKFLOW.count("python3 test_bf_nav_resource_budget_alignment_v24400.py") == 1
assert PREFLIGHT.count("test_bf_nav_resource_budget_alignment_v24400.py") == 2
assert "test_bf_engine_ui_asset_budget_v22800.py" in WORKFLOW
for filename in ("bf_home_nav.js", "bf_home_nav.css"):
    count = (ASSETS / filename).stat().st_size
    assert 0 < count <= CAP, (filename, count)
print(f"PASS v244: audited {len(list(ROOT.glob('test_*.py')))} tests; "
      f"{len(EXPECTED)} legacy nav assertions <=128KiB; exact-name Java loader; save untouched")
