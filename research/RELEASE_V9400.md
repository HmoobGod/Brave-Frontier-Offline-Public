# Brave Frontier Global v94.00 — Visible Critical-Hit Feedback During Gameplay

**Verified parent:** v93.00 Build #345, commit `4629f4b7c62b586415bbb91ddf50d991beb92eeb`, signed APK artifact `12598658229`.

The source-qualified single-hit critical attack was already implemented by v93. That gameplay improvement was visible in its expandable diagnostics panel but **not in the actual combat log at the time of the hit**. The log is also collapsed by default, so the separate on-screen battle header must show confirmed criticals.

v94 adds a readable **CRITICAL HIT!** battle-log entry only when the v93 actual single-hit critical is observed and recorded. The entry includes the acting unit ID and observed demo HP loss. Noncritical attacks, multi-hit attacks, Brave Bursts, training and all unsupported source records do not display it. This is user-visible feedback for a real, already-triggered combat effect—there is **no new RNG roll, altered damage, attack AI, skill status, counter, or battle turn**. It does not claim to recreate the original game's precise font, particle effect, animation, or sound.

The visible header badge persists for subsequent ally actions **in the same battle round**, but clears as soon as a later round or wave starts. Its underlying critical event remains in the combat history. A standalone V8 mock-DOM runtime smoke test of the exact candidate JavaScript covered critical damage/notice, same-round noncritical preservation, and next-round clearing; full Chromium and signed-APK gates remain pending because GitHub Actions has not assigned a runner to recent private-repository jobs.

Browser regression now asserts one notice for an actual eligible critical, none for an ordinary hit and none for a disallowed multi-hit actor. Existing v93 tests of 10%/150% rule, combat HP changes, no extra save writes, reset and duplicate injection remain. APK regression additionally checks feedback is packaged.

Keep `P.version=7` and `bf_global_offline_demo_v7`, existing saved content, `org.bravefrontier.offline`, the development debug keystore, and offline manifest with no INTERNET permission. Promote only when the **exact v94 SHA passes GitHub Actions and produces a signed APK**; physical Android testing remains unclaimed.

Further authentic gameplay work requires recovered 2022 native mission-to-wave enemy mapping and battle AI, or independently established BC/HC pickup and original damage timing. No guessed mechanics should replace working systems.
