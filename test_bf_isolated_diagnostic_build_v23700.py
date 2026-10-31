"""v237 diagnostic variant source and binary identity checks.

--packaged verifies both real Android APKs via Android SDK aapt; source-only
checks run without the SDK. This is NOT an owner-device or save test.
"""
from pathlib import Path
import os, re, shutil, subprocess, sys, zipfile
from xml.etree import ElementTree
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
gradle = (ROOT/"app/build.gradle").read_text("utf-8")
manifest = (ROOT/"app/src/main/AndroidManifest.xml").read_text("utf-8")
main_strings = ROOT/"app/src/main/res/values/strings.xml"
diag_strings = ROOT/"app/src/diagnostic/res/values/strings.xml"
wf = (ROOT/".github/workflows/build-debug-apk.yml").read_text("utf-8")
pre = (ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
debug_apk = ROOT/"app/build/outputs/apk/debug/app-debug.apk"
diag_apk = ROOT/"app/build/outputs/apk/diagnostic/app-diagnostic.apk"

assert gradle.count("applicationId 'org.bravefrontier.offline'") == 1
block = gradle.split("    buildTypes {", 1)[1].split("    compileOptions {", 1)[0]
assert re.search(r"(?m)^\s*debug\s*\{\s*signingConfig signingConfigs\.debug\s*\}", block)
m = re.search(r"(?ms)^\s*diagnostic\s*\{(.*?)^\s*\}", block)
assert m, "Missing explicit diagnostic-only build type"
variant = m.group(1)
assert re.search(r"\binitWith\s+debug\b", variant)
assert re.search(r"(?m)^\s*debuggable\s+true\s*$", variant)
assert not re.search(r"(?m)^\s*debuggable\s+false\b", variant)
assert re.search(r"\bapplicationIdSuffix\s+['\"]\.diagnostic['\"]", variant)
assert re.search(r"\bversionNameSuffix\s+['\"]-diagnostic['\"]", variant)
assert re.search(r"\bsigningConfig\s+signingConfigs\.debug\b", variant)
assert re.search(r"\bmatchingFallbacks\s*=\s*\[['\"]debug['\"]\]", variant)
assert block.count("applicationIdSuffix") == 1
assert "applicationIdSuffix" not in block.split("diagnostic {", 1)[0]
assert ElementTree.parse(main_strings).getroot().find("string[@name='app_name']").text == "Brave Frontier Offline Demo"
assert ElementTree.parse(diag_strings).getroot().find("string[@name='app_name']").text == "BF Offline Diagnostic"
assert "android.permission.INTERNET" not in manifest
# N2: independent package UID/storage; refuse shared UID, providers and fixed custom permissions.
ns = "{http://schemas.android.com/apk/res/android}"
manifest_root = ElementTree.fromstring(manifest)
assert ns+"sharedUserId" not in manifest_root.attrib
assert all(child.tag not in ("provider", "permission") for child in manifest_root.iter())
assert not (ROOT/"app/src/diagnostic/AndroidManifest.xml").exists(), "Unexpected diagnostic manifest overlay"
assert len(re.findall(r"^\s*python3 test_bf_isolated_diagnostic_build_v23700.py$", wf, re.M)) == 1
assert len(re.findall(r"^\s*(?:run:\s*)?python3 test_bf_isolated_diagnostic_build_v23700.py --packaged$", wf, re.M)) == 1
assert len(re.findall(r"^\s*(?:run:\s*)?python3 test_bf_isolated_diagnostic_build_v23700.py$", pre, re.M)) == 1
assert pre.count("test_bf_isolated_diagnostic_build_v23700.py") == 2
assert re.search(r"\bassembleDebug\b", wf) and re.search(r"\bassembleDiagnostic\b", wf)
assert wf.index("assembleDebug") < wf.index("name: Upload APK") < wf.index("assembleDiagnostic")
assert 'name: BraveFrontierOffline-isolated-diagnostic-apk' in wf
assert 'path: app/build/outputs/apk/diagnostic/app-diagnostic.apk' in wf
assert 'path: app/build/outputs/apk/debug/app-debug.apk' in wf
assert "BFOfflineTrace" not in gradle and "localStorage" not in gradle

# N3: publishing the isolated APK must be fail-closed. A diagnostic step
# silently skipped via 'if' or 'continue-on-error' is an acceptance failure.
def diagnostic_steps(source):
    names = [
        "Build separate-app diagnostic APK (must not overwrite Current build)",
        "Verify built APK IDs, original assets, and offline permissions",
        "Upload distinct diagnostic APK",
    ]
    blocks = []
    for name in names:
        start = "      - name: " + name + "\n"
        assert source.count(start) == 1, f"Missing/nonunique step: {name}"
        tail = source.split(start, 1)[1]
        section = tail.split("\n      - name: ", 1)[0]
        assert not re.search(r"(?m)^\s*(?:if:|continue-on-error:)", section), name
        assert "|| true" not in section, name
        blocks.append(section)
    assert re.search(r"(?m)^\s*run:\s*gradle --no-daemon assembleDiagnostic\b", blocks[0])
    assert re.search(r"(?m)^\s*run:\s*python3 test_bf_isolated_diagnostic_build_v23700.py --packaged\s*$", blocks[1])
    assert "uses: actions/upload-artifact@v4" in blocks[2]
    assert "if-no-files-found: error" in blocks[2]
    return True

assert diagnostic_steps(wf)
for name, mutation in (
    ("verify step bypass", wf.replace(
        "      - name: Verify built APK IDs, original assets, and offline permissions\n",
        "      - name: Verify built APK IDs, original assets, and offline permissions\n        continue-on-error: true\n")),
    ("build step skipped", wf.replace(
        "      - name: Build separate-app diagnostic APK (must not overwrite Current build)\n",
        "      - name: Build separate-app diagnostic APK (must not overwrite Current build)\n        if: false\n")),
    ("upload step bypass", wf.replace(
        "      - name: Upload distinct diagnostic APK\n",
        "      - name: Upload distinct diagnostic APK\n        continue-on-error: true\n")),
):
    assert mutation != wf, name + " was not applied"
    try:
        diagnostic_steps(mutation)
    except AssertionError:
        continue
    raise AssertionError("Unsafe diagnostic CI mutation accepted: " + name)

if "--packaged" in sys.argv[1:]:
    assert debug_apk.is_file() and diag_apk.is_file(), "Both APKs must exist"
    sdk = Path(os.environ.get("ANDROID_HOME", ""))
    candidates = [sdk/"build-tools/35.0.0/aapt"]
    which = shutil.which("aapt")
    if which:
        candidates.append(Path(which))
    aapt = next((x for x in candidates if x.is_file()), None)
    assert aapt, "Android SDK build-tools 35.0.0 aapt is required"
    def dump(apk, command):
        out = subprocess.run([str(aapt), "dump", command, str(apk)],
                             capture_output=True, text=True, check=True)
        return out.stdout
    regular, isolated = dump(debug_apk,"badging"), dump(diag_apk,"badging")
    def package(badging):
        match = re.search(r"(?m)^package: name='([^']+)'", badging)
        assert match, "Missing package ID"
        return match.group(1)
    assert package(regular) == "org.bravefrontier.offline"
    assert package(isolated) == "org.bravefrontier.offline.diagnostic"
    assert "application-label:'BF Offline Diagnostic'" in isolated
    assert "application-label:'Brave Frontier Offline Demo'" in regular
    assert re.search(r"(?m)^application-debuggable\s*$", isolated), "Diagnostic is not debuggable"
    # N2: verify absence of compiled manifest identity-sharing elements.
    for apk in (debug_apk, diag_apk):
        tree = subprocess.run([str(aapt), "dump", "xmltree", str(apk),
                               "AndroidManifest.xml"], capture_output=True, text=True,
                              check=True).stdout
        assert not re.search(r"(?m)^\s*E:\s*(?:provider|permission)\b", tree)
        assert not re.search(r"android:sharedUserId", tree)
    assert "android.permission.INTERNET" not in dump(debug_apk,"permissions")
    assert "android.permission.INTERNET" not in dump(diag_apk,"permissions")
    with zipfile.ZipFile(debug_apk) as first, zipfile.ZipFile(diag_apk) as second:
        left = {n for n in first.namelist() if n.startswith("assets/") and not n.endswith("/")}
        right = {n for n in second.namelist() if n.startswith("assets/") and not n.endswith("/")}
        assert left == right and "assets/index.html" in left
        assert all(sha256(first.read(name)).digest() == sha256(second.read(name)).digest()
                   for name in left), "Game assets changed in diagnostic variant"
    print("PASS v238 packaged: separate app IDs, debuggable trace, isolated manifests, identical game assets")
else:
    print("PASS v238 source: debuggable diagnostic app, manifest isolation, fail-closed CI steps")
