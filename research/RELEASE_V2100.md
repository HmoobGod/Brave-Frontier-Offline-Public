# v21.00 — Battle Command Tray

Branch from v20.00 verified Build #206 1f07d7d2263c2f18b284547b2c2e379caecee065.

Add an optional, mobile-friendly, directly playable **squad command tray** adjacent to the actual native demo battle command area. Includes tap target selection with live foe HP, queue-all normal attacks, queue-all guards, and full-gauge Brave Bursts with attack fallback. Actions are queued by clicking the same existing six slot and combat buttons as manual play; final Execute still uses the native Execute control. The tray checks phase guards (busy, ended, auto-battle), does not change outcome or damage, and never calls save/write APIs.

This is a quality-of-life interface for the existing *DEMO* encounter engine, NOT a restoration of native original BF1 combat AI, enemy spawns, or formulas. It affects neither 2014 historical sandbox nor saved v7 progress, native Android identity/signing, networking, or earlier features.

Browser smoke covers six-unit attack/guard/BB queue, switching target, illegality safeguards and executing a real turn; packaged APK and all inherited release tests must pass. Device acceptance still pending.
