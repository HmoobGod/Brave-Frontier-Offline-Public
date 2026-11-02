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
    "test_bf_morgan_original_v080.py",
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
ADDITIONAL_PACKAGED = tuple("test_bf_packaged_" + part + ".py" for part in (
    "global_codex", "grand_gaia_campaign_v100", "monsters_nest_v050",
    "morgan_source_v080", "morgan_v080", "original_bb_power",
    "quest_english_data_v048", "remains_mirza_v049", "st_lamia_v090",
    "tower_of_mistral_v051",
))
EXPECTED = set(LEGACY + PACKAGED + ADDITIONAL_PACKAGED)
assert len(EXPECTED) == 38

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


def integer_value(expr, constants):
    """Resolve simple literal or named integer limits without executing source."""
    if isinstance(expr, ast.Constant) and type(expr.value) is int:
        return expr.value
    if isinstance(expr, ast.Name):
        return constants.get(expr.id)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Mult, ast.Add, ast.Sub, ast.Pow)):
        a, b = integer_value(expr.left, constants), integer_value(expr.right, constants)
        if a is None or b is None:
            return None
        if isinstance(expr.op, ast.Mult):
            return a * b
        if isinstance(expr.op, ast.Add):
            return a + b
        if isinstance(expr.op, ast.Sub):
            return a - b
        return a ** b if 0 <= b < 20 else None
    return None


def target_names(target):
    return {node.id for node in ast.walk(target) if isinstance(node, ast.Name)}


def nav_reference(expr, aliases):
    """Recognize only actual nav paths and in-scope derived values."""
    return any(
        (isinstance(node, ast.Name) and node.id in aliases)
        or (isinstance(node, ast.Constant) and isinstance(node.value, str)
            and (node.value == "bf_home_nav.js" or node.value == "bf_home_nav.css"
                 or node.value.endswith("/bf_home_nav.js")
                 or node.value.endswith("/bf_home_nav.css")))
        for node in ast.walk(expr)
    )


def nav_measure(expr, aliases):
    """Identify length, filesystem stat, ZIP member size and their aliases."""
    if isinstance(expr, ast.Name):
        return aliases.get(expr.id) == "size"
    if isinstance(expr, ast.Call):
        func = expr.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else "")
        if name in ("len", "getsize") and len(expr.args) == 1:
            return nav_reference(expr.args[0], aliases)
    if isinstance(expr, ast.Attribute) and expr.attr in ("st_size", "file_size"):
        return nav_reference(expr.value, aliases)
    return False


def inspect_test(expr, aliases, constants, found, line, guard=False):
    """Inspect comparisons in asserts, ifs, loops and unittest methods."""
    checks = []
    for node in ast.walk(expr):
        if isinstance(node, ast.Compare):
            values = [node.left] + node.comparators
            for left, op, right in zip(values, node.ops, values[1:]):
                is_left = nav_measure(left, aliases)
                is_right = nav_measure(right, aliases)
                if is_left == is_right:
                    continue
                # A lower-bound health check (0 < len(nav)) is not a size cap.
                # In an if/while guard, >= may be a fail-closed oversized check.
                upper = (is_left and isinstance(op, (ast.Lt, ast.LtE))
                         or is_right and isinstance(op, (ast.Gt, ast.GtE)))
                rejecting_guard = (guard and
                                   (is_left and isinstance(op, (ast.Gt, ast.GtE))
                                    or is_right and isinstance(op, (ast.Lt, ast.LtE))))
                if not (upper or rejecting_guard):
                    continue
                bound = integer_value(right if is_left else left, constants)
                if bound is not None:
                    checks.append((line, bound,
                                   isinstance(op, (ast.LtE, ast.GtE)),
                                   "comparison"))
        elif isinstance(node, ast.Call):
            method = node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if method in ("assertLess", "assertLessEqual",
                          "assertGreater", "assertGreaterEqual") and len(node.args) >= 2:
                a, b = node.args[:2]
                if nav_measure(a, aliases) != nav_measure(b, aliases):
                    bound = integer_value(b if nav_measure(a, aliases) else a, constants)
                    if bound is not None:
                        checks.append((line, bound,
                                       method in ("assertLessEqual", "assertGreaterEqual"),
                                       method))
    if checks:
        assert not any(isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or)
                       for node in ast.walk(expr)), ("nav assertion OR bypass", line)
        found.extend(checks)


def analyze_statements(statements, aliases=None, constants=None):
    """Sequential, scope-aware dataflow; reassignment clears old nav aliases."""
    aliases = dict(aliases or {})
    constants = dict(constants or {})
    found = []
    for stmt in statements:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            local_alias = aliases.copy()
            local_const = constants.copy()
            for arg in stmt.args.posonlyargs + stmt.args.args + stmt.args.kwonlyargs:
                local_alias.pop(arg.arg, None)
                local_const.pop(arg.arg, None)
            if stmt.args.vararg:
                local_alias.pop(stmt.args.vararg.arg, None)
            if stmt.args.kwarg:
                local_alias.pop(stmt.args.kwarg.arg, None)
            found.extend(analyze_statements(stmt.body, local_alias, local_const))
            continue
        if isinstance(stmt, ast.ClassDef):
            found.extend(analyze_statements(stmt.body, aliases, constants))
            continue
        if isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            val = stmt.value
            if val is None:
                continue
            inspect_test(val, aliases, constants, found, stmt.lineno)
            is_size = nav_measure(val, aliases)
            is_nav = is_size or nav_reference(val, aliases)
            number = integer_value(val, constants)
            for target in targets:
                for name in target_names(target):
                    aliases.pop(name, None)
                    constants.pop(name, None)
                    if is_nav:
                        aliases[name] = "size" if is_size else "resource"
                    if number is not None:
                        constants[name] = number
            continue
        if isinstance(stmt, (ast.If, ast.While)):
            inspect_test(stmt.test, aliases, constants, found, stmt.lineno, guard=True)
            found.extend(analyze_statements(stmt.body, aliases, constants))
            found.extend(analyze_statements(stmt.orelse, aliases, constants))
            continue
        if isinstance(stmt, (ast.For, ast.AsyncFor)):
            inspect_test(stmt.iter, aliases, constants, found, stmt.lineno)
            found.extend(analyze_statements(stmt.body, aliases, constants))
            found.extend(analyze_statements(stmt.orelse, aliases, constants))
            continue
        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            for item in stmt.items:
                inspect_test(item.context_expr, aliases, constants, found, stmt.lineno)
            found.extend(analyze_statements(stmt.body, aliases, constants))
            continue
        if isinstance(stmt, ast.Try):
            found.extend(analyze_statements(stmt.body, aliases, constants))
            for handler in stmt.handlers:
                found.extend(analyze_statements(handler.body, aliases, constants))
            found.extend(analyze_statements(stmt.orelse, aliases, constants))
            found.extend(analyze_statements(stmt.finalbody, aliases, constants))
            continue
        if isinstance(stmt, ast.Assert):
            inspect_test(stmt.test, aliases, constants, found, stmt.lineno)
        elif isinstance(stmt, (ast.Expr, ast.Raise, ast.Return)):
            expr = (stmt.value if isinstance(stmt, (ast.Expr, ast.Return))
                    else stmt.exc)
            if expr is not None:
                inspect_test(expr, aliases, constants, found, stmt.lineno)
    return found


def nav_limits(tree):
    return analyze_statements(tree.body)


def check_limits(label, limits):
    for lineno, value, inclusive, mechanism in limits:
        assert 65536 < value <= CAP, (
            label, lineno, mechanism, "stale or unsafe navigation byte cap", value)


def self_test_detector():
    """Mutation probes run every time in both source-only and full CI."""
    invalid_cases = (
        "assert (A/'bf_home_nav.js').stat().st_size < 65536",
        "import os\nassert os.path.getsize(A/'bf_home_nav.js') <= 65536",
        "info = apk.getinfo('assets/bf_home_nav.js')\nassert info.file_size < 65536",
        "LIMIT = 65536\nnav = (A/'bf_home_nav.js').read_bytes()\nassert len(nav) <= LIMIT",
        "nav = (A/'bf_home_nav.js').read_bytes()\nif len(nav) >= 65536:\n    raise RuntimeError()",
        "nav = (A/'bf_home_nav.js').read_bytes()\nself.assertLess(len(nav), 65536)",
        "nav = (A/'bf_home_nav.js').read_bytes()\nn = len(nav)\nassert n <= 65536",
        "p = A/'bf_home_nav.js'\ndata = p.read_bytes()\nn = len(data)\nassert n < 65536",
        "assert len((A/'bf_home_nav.css').read_bytes()) < 65536",
        "nav = (A/'bf_home_nav.js').read_bytes()\nassert len(nav)<=128*1024 or True",
    )
    for src in invalid_cases:
        tree = ast.parse(src)
        try:
            limits = nav_limits(tree)
            assert limits, ("detector missed source", src)
            check_limits("mutation", limits)
        except AssertionError:
            continue
        raise AssertionError(("mutation unexpectedly accepted", src))

    valid_cases = (
        "nav=(A/'bf_home_nav.js').read_bytes()\nassert len(nav)<=128*1024",
        "nav=(A/'bf_home_nav.js').read_bytes()\nnav=(A/'other.js').read_bytes()\nassert len(nav)<=65536",
        "def one():\n    nav=(A/'bf_home_nav.js').read_bytes()\ndef two():\n    nav=(A/'other.js').read_bytes()\n    assert len(nav)<=65536",
        "nav=(A/'bf_home_nav.js').read_bytes()\narchive=(A/'bf_global_unit_archive.js').read_bytes()\nassert len(nav)<=128*1024 and len(archive)<=65536",
    )
    for src in valid_cases:
        check_limits("valid", nav_limits(ast.parse(src)))


self_test_detector()
seen = {}
violations = []
for path in sorted(ROOT.glob("test_*.py")):
    tree = ast.parse(path.read_text("utf8"), filename=path.name)
    limits = nav_limits(tree)
    for lineno, value, inclusive, mechanism in limits:
        if not 65536 < value <= CAP:
            violations.append((path.name, lineno, value, inclusive, mechanism))
    if limits:
        seen[path.name] = limits

assert not violations, ("stale or unsafe nav size assertions across all tests", violations)

for filename in EXPECTED:
    assert filename in seen and len(seen[filename]) == 1, (
        filename, "missing or ambiguous nav JS 128KiB assertion", seen.get(filename))
    assert seen[filename][0][1:3] == (CAP, True), (
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
      f"{len(EXPECTED)} nav assertions <=128KiB; exact-name Java loader; save untouched")
