"""v239: create and verify a deliberately missing-index *isolated* diagnostic APK.

The normal and diagnostic APKs remain byte-for-byte untouched. The ONLY
altered app is org.bravefrontier.offline.diagnostic, never Current.
Run --source-only during source preflight, --build and --verify in signed CI.
This prepares a test artifact, NOT a physical Android callback test.
"""
from __future__ import annotations
import hashlib
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
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout

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
    with zipfile.ZipFile(DIAGNOSTIC) as before, zipfile.ZipFile(OUTPUT) as after:
        old_assets = {n for n in before.namelist() if n.startswith("assets/") and not n.endswith("/")}
        new_assets = {n for n in after.namelist() if n.startswith("assets/") and not n.endswith("/")}
        assert MISSING in old_assets and MISSING not in new_assets
        assert new_assets == old_assets - {MISSING}
        assert all(hashlib.sha256(before.read(n)).digest() ==
                   hashlib.sha256(after.read(n)).digest() for n in new_assets)
        # Android component and permissions are inherited; no manifest patch.
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
        run([apksigner, "sign", "--ks", str(KEYSTORE), "--ks-pass", "pass:android",
             "--ks-key-alias", "androiddebugkey", "--key-pass", "pass:android",
             "--out", str(OUTPUT), str(aligned)])
    verify_structure(aapt, apksigner, original_hash, diagnostic_hash)
    print("PASS v239 built: signed isolated missing-index APK; Current + diagnostic inputs untouched")

def verify() -> None:
    aapt, apksigner = tool("aapt"), tool("apksigner")
    original_hash, diagnostic_hash = sha(NORMAL), sha(DIAGNOSTIC)
    verify_structure(aapt, apksigner, original_hash, diagnostic_hash)
    print("PASS v239 packaged: same diagnostic ID/signing, index missing only, no original files changed")

if __name__ == "__main__":
    args = sys.argv[1:]
    assert args in (["--source-only"], ["--build"], ["--verify"]), args
    source_gate()
    if args == ["--build"]:
        build()
    elif args == ["--verify"]:
        verify()
    else:
        print("PASS v239 source: isolated fault-only APK wiring and immutable input checks")
