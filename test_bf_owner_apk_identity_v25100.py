"""v251: publish privacy-safe, real signed-APK identity evidence.

This verifies the BUILT standard APK, not the owner's installed app/save.
The certificate digest is public metadata; never read or upload keystore bytes.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
WORKFLOW = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
GRADLE = (ROOT / "app/build.gradle").read_text("utf8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
REPORT = ROOT / "source_audit_reports/BraveFrontier-v251-owner-apk-identity.json"
PACKAGE = "org.bravefrontier.offline"
ARTIFACT = "BraveFrontierOffline-v251-owner-apk-identity"

def package_info(text):
    match = re.search(
        r"(?m)^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']+)'",
        text,
    )
    assert match, "APK badging has no unambiguous package/version fields"
    return match.group(1), int(match.group(2)), match.group(3)

def certificate_digest(text):
    digests = re.findall(
        r"(?im)^Signer #[0-9]+ certificate SHA-256 digest:\s*([a-f0-9]{64})\s*$",
        text,
    )
    assert len(digests) == 1, "Exactly one signer SHA-256 certificate digest is required"
    return digests[0].lower()

def provenance(event_name, github_sha, pr_head_sha):
    """Differentiate the checked-out workflow commit from the logical PR head.

    On pull_request, Actions normally checks out a synthetic merge SHA; the
    distinct PR head is recorded for independent exact-head review.
    """
    assert event_name in ("push", "pull_request", "workflow_dispatch"), "Unknown GitHub event"
    assert isinstance(github_sha, str) and re.fullmatch(r"[0-9a-f]{40}", github_sha), (
        "Missing/invalid GitHub build SHA"
    )
    assert isinstance(pr_head_sha, str), "Missing PR-head environment value"
    if event_name == "pull_request":
        assert re.fullmatch(r"[0-9a-f]{40}", pr_head_sha), (
            "PR event requires an exact 40-hex pull request head SHA"
        )
        logical_head = pr_head_sha
    else:
        assert not pr_head_sha, "Non-PR event must not claim a PR head"
        logical_head = github_sha
    return {
        "github_sha": github_sha,
        "github_event_name": event_name,
        "pull_request_head_sha": pr_head_sha if event_name == "pull_request" else None,
        "source_head_sha": logical_head,
    }

def sdk_tool(name):
    home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    assert home, "Android SDK path unavailable"
    tool = Path(home) / "build-tools/35.0.0" / name
    assert tool.is_file(), "Android build-tools 35.0.0 missing: " + name
    return str(tool)

def inspect_artifact():
    assert APK.is_file() and APK.stat().st_size > 1024, "Standard debug APK missing"
    aapt = sdk_tool("aapt")
    signer = sdk_tool("apksigner")
    package, code, version = package_info(subprocess.check_output(
        [aapt, "dump", "badging", str(APK)], text=True,
    ))
    assert package == PACKAGE, "Wrong APK applicationId (possibly diagnostic)"
    run_number = int(os.environ["GITHUB_RUN_NUMBER"])
    assert run_number > 0
    assert code == 100000 + run_number, "Unexpected APK versionCode"
    assert version == "174.00.0-demo", "Legacy packaged tests pin display versionName"
    permissions = subprocess.check_output([aapt, "dump", "permissions", str(APK)], text=True)
    assert "android.permission.INTERNET" not in permissions, "Network permission prohibited"
    verification = subprocess.check_output(
        [signer, "verify", "--verbose", "--print-certs", str(APK)], text=True,
    )
    cert = certificate_digest(verification)
    with APK.open("rb") as apk_file:
        digest = hashlib.file_digest(apk_file, "sha256").hexdigest()
    source = provenance(
        os.environ["BF_EVENT_NAME"],
        os.environ["GITHUB_SHA"],
        os.environ["BF_PR_HEAD_SHA"],
    )
    assert source["github_event_name"] == os.environ["GITHUB_EVENT_NAME"], "Event mismatch"
    checkout_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert re.fullmatch(r"[0-9a-f]{40}", checkout_sha), "Invalid checked-out commit"
    assert checkout_sha == source["github_sha"], "GitHub event SHA disagrees with checked-out build"
    result = {
        "schema": "bf-offline-v251-owner-apk-identity-v2",
        **source,
        "checked_out_commit_sha": checkout_sha,
        "build_run_number": run_number,
        "apk_filename": APK.name,
        "apk_sha256": digest,
        "apk_size_bytes": APK.stat().st_size,
        "package_id": package,
        "version_code": code,
        "version_name": version,
        "signing_certificate_sha256": cert,
        "internet_permission": False,
        "owner_installed_certificate_match": "NOT_CHECKED",
        "owner_installed_version_code": "NOT_CHECKED",
        "owner_real_v124_save_backup": "NOT_CHECKED",
        "owner_real_device_upgrade": "NOT_CHECKED",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", "utf8")
    assert json.loads(REPORT.read_text("utf8")) == result
    print("PASS v251 signed owner APK identity: package/versionCode, certificate and SHA-256 recorded")
    print("Owner device signature, installed versionCode and real save: NOT CHECKED")

# Source-only guards ensure the report is derived from the exact signed APK,
# uploaded separately and never substituted for the user-installable artifact.
assert "applicationId 'org.bravefrontier.offline'" in GRADLE
assert "project.findProperty('ciVersionCode')" in GRADLE
assert "versionName '174.00.0-demo'" in GRADLE
assert "android.permission.INTERNET" not in MANIFEST
assert "BF_DEBUG_KEYSTORE_B64" in WORKFLOW
assert "test_bf_owner_apk_identity_v25100.py --packaged" in WORKFLOW
assert re.search(
    r"(?m)^\s*BF_PR_HEAD_SHA:\s*\$\{\{\s*github\.event\.pull_request\.head\.sha\s*\}\}\s*$",
    WORKFLOW,
), "Workflow must pass the exact PR head SHA"
assert re.search(
    r"(?m)^\s*BF_EVENT_NAME:\s*\$\{\{\s*github\.event_name\s*\}\}\s*$",
    WORKFLOW,
), "Workflow must pass the GitHub event name"

assert "test_bf_owner_apk_identity_v25100.py --source-only" in PREFLIGHT
assert "BraveFrontierOffline-demo-debug-apk" in WORKFLOW
assert ARTIFACT in WORKFLOW
assert "source_audit_reports/BraveFrontier-v251-owner-apk-identity.json" in WORKFLOW
assert WORKFLOW.index("python3 test_bf_owner_apk_identity_v25100.py --packaged") < WORKFLOW.index("name: Upload APK")
assert "if-no-files-found: error" in WORKFLOW
# Parsers reject missing, ambiguous or off-target package/certificate data.
assert package_info("package: name='org.bravefrontier.offline' versionCode='101488' versionName='174.00.0-demo'\n") == (
    PACKAGE, 101488, "174.00.0-demo"
)
for invalid in ("", "package: name='x'\n"):
    try:
        package_info(invalid)
    except AssertionError:
        pass
    else:
        raise AssertionError("Malformed package badging accepted")
good_cert = "Signer #1 certificate SHA-256 digest: " + ("ab" * 32) + "\n"
assert certificate_digest(good_cert) == ("ab" * 32)
for invalid in ("", good_cert + good_cert, "Signer #1 certificate SHA-256 digest: DEAD\n"):
    try:
        certificate_digest(invalid)
    except AssertionError:
        pass
    else:
        raise AssertionError("Malformed/multiple signing certificates accepted")
# Attestation provenance must distinguish PR merge builds from PR head commits.
assert provenance("pull_request", "a" * 40, "b" * 40) == {
    "github_sha": "a" * 40,
    "github_event_name": "pull_request",
    "pull_request_head_sha": "b" * 40,
    "source_head_sha": "b" * 40,
}
for event_name in ("push", "workflow_dispatch"):
    assert provenance(event_name, "c" * 40, "") == {
        "github_sha": "c" * 40,
        "github_event_name": event_name,
        "pull_request_head_sha": None,
        "source_head_sha": "c" * 40,
    }
for invalid in (
    ("pull_request", "a" * 40, ""),
    ("pull_request", "a" * 40, "x" * 40),
    ("pull_request", "a" * 40, "B" * 40),
    ("pull_request", "a" * 39, "b" * 40),
    ("pull_request", "A" * 40, "b" * 40),
    ("push", "a" * 40, "b" * 40),
    ("workflow_dispatch", "", ""),
    ("unsupported_event", "a" * 40, ""),
):
    try:
        provenance(*invalid)
    except AssertionError:
        pass
    else:
        raise AssertionError("Unsafe or misleading source provenance was accepted")

print("PASS v251 source: attestation must target standard signed APK, not diagnostic, with fail-closed identity parsing")

if "--packaged" in sys.argv[1:]:
    inspect_artifact()
elif "--source-only" not in sys.argv[1:]:
    raise SystemExit("Specify --source-only or --packaged; no implicit APK handling")
