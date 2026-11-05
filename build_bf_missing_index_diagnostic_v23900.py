"""v239: create and verify a deliberately missing-index *isolated* diagnostic APK.

The normal and diagnostic APKs remain byte-for-byte untouched. The ONLY
altered app is org.bravefrontier.offline.diagnostic, never Current.
Run --source-only during source preflight, --build and --verify in signed CI.
This prepares a test artifact, NOT a physical Android callback test.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
NORMAL = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
DIAGNOSTIC = ROOT / "app/build/outputs/apk/diagnostic/app-diagnostic.apk"
OUTPUT = ROOT / "app/build/outputs/apk/diagnostic-fault/app-diagnostic-missing-index.apk"
# Persist cross-step hashes so --verify cannot compare each input to itself.
HASH_RECORD = OUTPUT.parent / "v240-fault-apk-input-digests.json"
KEYSTORE = ROOT / ".github/debug/bf-development-debug.keystore"
WORKFLOW = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
EXPECTED_ID = "org.bravefrontier.offline.diagnostic"
FORBIDDEN_ID = "org.bravefrontier.offline"
MISSING = "assets/index.html"
SIGNATURE_ENTRY = re.compile(r"^META-INF/[^/]+\.(?:SF|RSA|DSA|EC)$", re.I)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tool(name: str) -> str:
    sdk = Path(os.environ.get("ANDROID_HOME", ""))
    candidate = sdk / "build-tools/35.0.0" / name
    assert candidate.is_file(), "Required Android SDK build-tools/35.0.0/" + name
    return str(candidate)

def run(args: list[str]) -> str:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(
            "Android SDK command failed (exit %s): %s\n%s" %
            (proc.returncode, args[0:2], proc.stderr[-3000:]))
    return proc.stdout

def badge(aapt: str, apk: Path) -> str:
    return run([aapt, "dump", "badging", str(apk)])

def package(badging: str) -> str:
    found = re.search(r"(?m)^package: name='([^']+)'", badging)
    assert found, "Missing AAPT package identity"
    return found.group(1)

def signature(apksigner: str, apk: Path) -> str:
    report = run([apksigner, "verify", "--verbose", "--print-certs", str(apk)])
    fingerprint = re.search(r"Signer #1 certificate SHA-256 digest:\s*([a-fA-F0-9]+)", report)
    assert fingerprint, "Missing verified signing certificate"
    return fingerprint.group(1).lower()

def source_gate() -> None:
    script = Path(__file__).read_text("utf-8")
    assert FORBIDDEN_ID != EXPECTED_ID
    assert "diagnostic-fault/app-diagnostic-missing-index.apk" in script
    assert "org.bravefrontier.offline.diagnostic" in script
    assert "app/build/outputs/apk/debug/app-debug.apk" in script
    assert "app/build/outputs/apk/diagnostic/app-diagnostic.apk" in script
    assert 'MISSING = "assets/index.html"' in script
    assert 'assert package(badge(aapt, NORMAL)) == FORBIDDEN_ID' in script
    assert 'assert package(badge(aapt, DIAGNOSTIC)) == EXPECTED_ID' in script
    assert 'assert package(badge(aapt, OUTPUT)) == EXPECTED_ID' in script
    assert "assert sha(NORMAL) == original_hash" in script
    assert "assert sha(DIAGNOSTIC) == diagnostic_hash" in script
    assert WORKFLOW.count("build_bf_missing_index_diagnostic_v23900.py --build") == 1
    assert WORKFLOW.count("build_bf_missing_index_diagnostic_v23900.py --verify") == 1
    assert PREFLIGHT.count("build_bf_missing_index_diagnostic_v23900.py") == 2
    assert "continue-on-error: true" not in WORKFLOW
    assert "if-no-files-found: error" in WORKFLOW.split(
        "      - name: Upload missing-index failure test APK", 1)[1]
    assert "zipalign" in script and "resources.arsc" in script
    assert "HASH_RECORD.write_text" in script and "HASH_RECORD.read_text" in script
    for step in (
        "Create isolated packaged-page failure APK (diagnostic ID only)",
        "Verify signed fault APK, untouched diagnostic APK and isolated identity",
        "Upload missing-index failure test APK (never install over Current)",
    ):
        marker = "      - name: " + step + "\n"
        assert WORKFLOW.count(marker) == 1
        tail = WORKFLOW.split(marker, 1)[1].split("\n      - name: ", 1)[0]
        assert not re.search(r"(?m)^\s*(?:if:|continue-on-error:)", tail)
        assert "|| true" not in tail
    assert WORKFLOW.index("name: Upload distinct diagnostic APK") < WORKFLOW.index(
        "name: Create isolated packaged-page failure APK")
    assert WORKFLOW.index("name: Create isolated packaged-page failure APK") < WORKFLOW.index(
        "name: Verify signed fault APK") < WORKFLOW.index(
        "name: Upload missing-index failure test APK")

def verify_structure(aapt: str, apksigner: str, original_hash: str, diagnostic_hash: str) -> None:
    assert NORMAL.is_file() and DIAGNOSTIC.is_file() and OUTPUT.is_file()
    assert sha(NORMAL) == original_hash
    assert sha(DIAGNOSTIC) == diagnostic_hash
    assert package(badge(aapt, NORMAL)) == FORBIDDEN_ID
    assert package(badge(aapt, DIAGNOSTIC)) == EXPECTED_ID
    assert package(badge(aapt, OUTPUT)) == EXPECTED_ID
    assert signature(apksigner, OUTPUT) == signature(apksigner, DIAGNOSTIC)
    assert "application-debuggable" in badge(aapt, OUTPUT)
    assert "android.permission.INTERNET" not in run([aapt, "dump", "permissions", str(OUTPUT)])
    # Installability gate: compressed or misaligned resources.arsc can be
    # rejected by modern Android even when aapt/signer accept the package.
    assert run([tool("zipalign"), "-c", "-p", "4", str(OUTPUT)]) is not None
    with zipfile.ZipFile(DIAGNOSTIC) as before, zipfile.ZipFile(OUTPUT) as after:
        old_files = [x.filename for x in before.infolist() if not x.is_dir()]
        new_files = [x.filename for x in after.infolist() if not x.is_dir()]
        assert len(old_files) == len(set(old_files)), "Duplicate original ZIP entries"
        assert len(new_files) == len(set(new_files)), "Duplicate output ZIP entries"
        old_contents = {n for n in old_files if not SIGNATURE_ENTRY.match(n)}
        new_contents = {n for n in new_files if not SIGNATURE_ENTRY.match(n)}
        assert MISSING in old_contents and MISSING not in new_contents
        expected_contents = old_contents - {MISSING}
        assert new_contents == expected_contents, (
            "Non-signature ZIP entry mismatch; added=%r removed=%r" %
            (sorted(new_contents - expected_contents),
             sorted(expected_contents - new_contents)))
        assert "resources.arsc" in old_contents
        assert before.getinfo("resources.arsc").compress_type == zipfile.ZIP_STORED
        assert after.getinfo("resources.arsc").compress_type == zipfile.ZIP_STORED
        assert all(hashlib.sha256(before.read(n)).digest() ==
                   hashlib.sha256(after.read(n)).digest() for n in new_contents), (
                   "Non-signature contents changed")
        # The full manifest and dex/native resources also remain untouched.
        assert before.read("AndroidManifest.xml") == after.read("AndroidManifest.xml")

def build() -> None:
    aapt, zipalign, apksigner = tool("aapt"), tool("zipalign"), tool("apksigner")
    assert NORMAL.is_file() and DIAGNOSTIC.is_file() and KEYSTORE.is_file()
    original_hash, diagnostic_hash = sha(NORMAL), sha(DIAGNOSTIC)
    assert package(badge(aapt, NORMAL)) == FORBIDDEN_ID
    assert package(badge(aapt, DIAGNOSTIC)) == EXPECTED_ID
    assert "application-debuggable" in badge(aapt, DIAGNOSTIC)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    assert OUTPUT != NORMAL and OUTPUT != DIAGNOSTIC
    with tempfile.TemporaryDirectory(prefix="bf239-") as temp:
        t = Path(temp)
        raw, aligned = t/"missing-unsigned.apk", t/"missing-aligned.apk"
        with zipfile.ZipFile(DIAGNOSTIC) as src, zipfile.ZipFile(raw, "w") as dst:
            for info in src.infolist():
                if info.filename == MISSING or SIGNATURE_ENTRY.match(info.filename):
                    continue
                dst.writestr(info, src.read(info.filename))
        run([zipalign, "-f", "-p", "4", str(raw), str(aligned)])
        # Disable v1 signatures explicitly: apksigner may otherwise insert
        # META-INF/MANIFEST.MF, which is not an original game file.
        run([apksigner, "sign", "--v1-signing-enabled", "false",
             "--ks", str(KEYSTORE), "--ks-pass", "pass:android",
             "--ks-key-alias", "androiddebugkey", "--key-pass", "pass:android",
             "--out", str(OUTPUT), str(aligned)])
    verify_structure(aapt, apksigner, original_hash, diagnostic_hash)
    record = {"normal_sha256": original_hash,
              "diagnostic_sha256": diagnostic_hash,
              "fault_sha256": sha(OUTPUT)}
    HASH_RECORD.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS v240 built: signed aligned missing-index APK; input SHA-256 baseline persisted")

def verify() -> None:
    aapt, apksigner = tool("aapt"), tool("apksigner")
    assert HASH_RECORD.is_file(), "Build-step hash baseline missing"
    record = json.loads(HASH_RECORD.read_text("utf-8"))
    assert set(record) == {"normal_sha256", "diagnostic_sha256", "fault_sha256"}
    original_hash = record["normal_sha256"]
    diagnostic_hash = record["diagnostic_sha256"]
    assert re.fullmatch(r"[a-f0-9]{64}", original_hash)
    assert re.fullmatch(r"[a-f0-9]{64}", diagnostic_hash)
    assert re.fullmatch(r"[a-f0-9]{64}", record["fault_sha256"])
    assert sha(OUTPUT) == record["fault_sha256"], "Fault APK mutated after build"
    verify_structure(aapt, apksigner, original_hash, diagnostic_hash)
    print("PASS v240 packaged: aligned+signed isolated fault APK, all ZIP files preserved except index/signatures, cross-step hashes unchanged")

if __name__ == "__main__":
    args = sys.argv[1:]
    assert args in (["--source-only"], ["--build"], ["--verify"]), args
    source_gate()
    if args == ["--build"]:
        build()
    elif args == ["--verify"]:
        verify()
    else:
        print("PASS v240 source: isolated fault-only APK with complete file and cross-step hash checks")
