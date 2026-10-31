"""v228: navigation asset size budget remains bounded, without save/runtime mutation."""
from pathlib import Path
import re

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets"
java = (R / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
manifest = (R / "app/src/main/AndroidManifest.xml").read_text("utf8")
nav = (A / "bf_home_nav.js").read_bytes()
css = (A / "bf_home_nav.css").read_bytes()

assert 0 < len(nav) <= 128 * 1024, len(nav)
assert 0 < len(css) <= 128 * 1024
assert "window.BF_homeNav = {go,get current()" in nav.decode("utf8")
assert "bf-menu-mode" in css.decode("utf8")

assert re.search(r"UI_RESOURCE_LIMIT_BYTES\s*=\s*64\s*\*\s*1024", java)
assert re.search(r"NAV_RESOURCE_LIMIT_BYTES\s*=\s*128\s*\*\s*1024", java)
assert 'return "bf_home_nav.js".equals(file) || "bf_home_nav.css".equals(file)' in java
assert "? NAV_RESOURCE_LIMIT_BYTES : UI_RESOURCE_LIMIT_BYTES;" in java
assert "final int maxBytes = packagedUiResourceLimit(file);" in java
assert 'getAssets().open(file)' in java
assert 'if (out.size() + count > maxBytes) throw new IOException("Oversized UI resource");' in java
assert "new byte[4096]" in java
assert "StandardCharsets.UTF_8" in java
assert 'readPackagedText("bf_home_nav.js")' in java
assert 'readPackagedText("bf_home_nav.css")' in java

start = java.index("private static int packagedUiResourceLimit(String file)")
end = java.index("private void toGame(", start)
loader = java[start:end]
assert 'https://' not in loader and 'http://' not in loader
assert "localStorage" not in loader and "saveProgress" not in loader
assert "bf_global_offline_demo_v7" not in loader
assert "android.permission.INTERNET" not in manifest
assert 'android:usesCleartextTraffic="false"' in manifest
print(f"PASS v228: nav JS {len(nav)} bytes, CSS {len(css)} bytes; exact-only 128KiB allowance, 64KiB elsewhere; save untouched")
