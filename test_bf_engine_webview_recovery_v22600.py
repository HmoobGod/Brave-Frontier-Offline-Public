"""v226 engine-only Android WebView recovery source checks; no on-device claims."""
from pathlib import Path
import re

R = Path(__file__).resolve().parent
java = (R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (R/"app/src/main/AndroidManifest.xml").read_text("utf-8")
navigation = (R/"app/src/main/assets/bf_home_nav.js").read_text("utf-8")

def require(fragment):
    assert fragment in java, fragment

require("private static final long UI_BACK_TIMEOUT_MS = 2500L;")
require("new android.os.Handler(android.os.Looper.getMainLooper())")
require("private int backDispatchToken = 0;")
require("private Runnable backTimeout;")
require("uiHandler.removeCallbacks(backTimeout);")
require("if (!backNavigationPending || token != backDispatchToken) return;")
require("if (!uiHandler.postDelayed(backTimeout, UI_BACK_TIMEOUT_MS))")
require("clearPendingBack();")
require('game.evaluateJavascript(UI_BACK_JS, handled ->')
require('if ("true".equals(handled)) return;')
require('if (!isFinishing() && !isDestroyed()) fallbackAndroidBack();')
require("onRenderProcessGone(")
require("android.webkit.RenderProcessGoneDetail detail")
require("if (view != game) return false;")
require("gameContainer.removeView(view);")
require('view.removeJavascriptInterface("BFAndroid");')
require("view.destroy();")
require("game = null;")
require('.setPositiveButton("Restart interface", (dialog, which) -> recreate())')
require(".setNegativeButton(\"Close\", (dialog, which) -> finish())")
require("unsaved actions may be lost")
require("Your saved data is not erased.")
assert len(re.findall(r'@Override protected void on(?:Pause|Destroy)\(\)',java))==2
assert java.count("clearPendingBack();")>=6
assert "window.BF_homeNav" in java and "window.BF_homeNav" in navigation
assert "bf_global_offline_demo_v7" not in java
assert "android.permission.INTERNET" not in manifest
assert 'android:usesCleartextTraffic="false"' in manifest
assert "localStorage" not in java
assert "Storage.setItem" not in java
print("PASS v226 source: bounded Android Back, stale callback guard, WebView renderer recovery, save schema untouched")
