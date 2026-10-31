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
assert re.search(r"\bapplicationIdSuffix\s+['\"]\.diagnostic['\"]", variant)
assert re.search(r"\bversionNameSuffix\s+['\"]-diagnostic['\"]", variant)
assert re.search(r"\bsigningConfig\s+signingConfigs\.debug\b", variant)
assert re.search(r"\bmatchingFallbacks\s*=\s*\[['\"]debug['\"]\]", variant)
assert block.count("applicationIdSuffix") == 1
assert "applicationIdSuffix" not in block.split("diagnostic {", 1)[0]
assert ElementTree.parse(main_strings).getroot().find("string[@name='app_name']").text == "Brave Frontier Offline Demo"
assert ElementTree.parse(diag_strings).getroot().find("string[@name='app_name']").text == "BF Offline Diagnostic"
assert "android.permission.INTERNET" not in manifest
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
    assert "android.permission.INTERNET" not in dump(debug_apk,"permissions")
    assert "android.permission.INTERNET" not in dump(diag_apk,"permissions")
    with zipfile.ZipFile(debug_apk) as first, zipfile.ZipFile(diag_apk) as second:
        left = {n for n in first.namelist() if n.startswith("assets/") and not n.endswith("/")}
        right = {n for n in second.namelist() if n.startswith("assets/") and not n.endswith("/")}
        assert left == right and "assets/index.html" in left
        assert all(sha256(first.read(name)).digest() == sha256(second.read(name)).digest()
                   for name in left), "Game assets changed in diagnostic variant"
    print("PASS v237 packaged: separate app IDs and labels, same offline assets, no INTERNET")
else:
    print("PASS v237 source: isolated diagnostic-only variant and independent APK CI gates")
