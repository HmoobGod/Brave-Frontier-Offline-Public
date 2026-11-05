# v267 — Unit portrait fallback readability

Base: merged v266 main SHA 047914b991a1a30f3d399d6583748f2e61fded3a.

This patch addresses two nonblocking findings from Claude's approved v266 PR #201: the missing-art label splits mid-word in a 67px evolution tile at 320/359px, and 8–9px text is difficult to read. The visible fallback becomes NO ART at 11px with no letter spacing and normal word breaks. The complete accessible label still identifies the specific unit whose portrait is unavailable. Original portrait sources and rendering remain unchanged when images are valid.

Changed scope: presentation string in bf_home_nav.js, additive scoped CSS, one updated assertion in the v266 regression, a dedicated v267 real-page browser regression, CI registrations, and this document. No game logic, save, original image, Android Java/manifest/Gradle/signing or installed APK changes.

Local verification: the original packaged v266 APK game page was tested with candidate v267 JS/CSS in isolated offline Chromium. v267 source-only checks and four mobile viewport cases at 320, 359, 393, 540 passed. Each checks missing-art legibility, intact word wrapping, preserved unit-specific aria-label and unchanged synthetic player/save state. The older v266 12-case regression remains registered for full CI.

Keep PR draft pending exact-head signed Android CI, artifact/identity checks and independent Claude review. Do not install an unaccepted APK on the owner's working v265 device. UI estimate 65%, full historical game estimate 30%, provisional.
