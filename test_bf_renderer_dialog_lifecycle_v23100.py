"""v231 static regression: renderer recovery dialog ownership; never claims device coverage."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent
java = (root/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
manifest = (root/"app/src/main/AndroidManifest.xml").read_text("utf8")
workflow = (root/".github/workflows/build-debug-apk.yml").read_text("utf8")
preflight = (root/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")

assert "private android.app.AlertDialog rendererFailureDialog;" in java
dispose = java.split("private void dismissRendererFailureDialog() {",1)[1].split("\n    }",1)[0]
assert "if (rendererFailureDialog == null) return;" in dispose
assert "rendererFailureDialog.dismiss();" in dispose
assert "rendererFailureDialog = null;" in dispose

renderer = java.split("@Override public boolean onRenderProcessGone(",1)[1].split("// Load the independent navigation layer",1)[0]
assert "if (view != game) return false;" in renderer
assert "clearPendingBack();" in renderer
assert "dismissOfflinePageError();" in renderer
assert "view.destroy();" in renderer
assert "game = null;" in renderer
assert "dismissRendererFailureDialog();" in renderer
assert "rendererFailureDialog = new android.app.AlertDialog.Builder(MainActivity.this)" in renderer
assert ".setPositiveButton(\"Restart interface\", (dialog, which) -> recreate())" in renderer
assert ".setNegativeButton(\"Close\", (dialog, which) -> finish())" in renderer
assert ".setCancelable(false)\n                            .create();" in renderer
assert "rendererFailureDialog.show();" in renderer
assert ".setCancelable(false)\n                            .show();" not in renderer

destroy = java.split("@Override protected void onDestroy() {",1)[1].split("\n    }",1)[0]
assert destroy.index("dismissRendererFailureDialog();") < destroy.index("super.onDestroy();")
assert destroy.index("dismissOfflinePageError();") < destroy.index("super.onDestroy();")
assert destroy.index("clearPendingBack();") < destroy.index("super.onDestroy();")

assert re.findall(r"^\s*python3 test_bf_renderer_dialog_lifecycle_v23100.py$",workflow,re.M).__len__() == 1
assert "test_bf_renderer_dialog_lifecycle_v23100.py" in preflight
assert "android.permission.INTERNET" not in manifest
assert "localStorage" not in java and "bf_global_offline_demo_v7" not in java
print("PASS v231: renderer dialog lifecycle owner cleared on destroy; offline/save guards intact")
