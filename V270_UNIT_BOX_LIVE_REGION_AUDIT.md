# v270 — Unit Box status and keyboard regression

Base: merged v269 main SHA 07b20053dc77a6565f54a090050386e44bed76d2.

This presentation-only patch addresses Claude's v269 finding N1. The Unit Box count remains a polite status region. The no-results message remains a status element. The surrounding results grid is no longer itself live, preventing nested announcements of the empty message and entire results list.

A new real-page browser test extends v269's coverage at 320, 359, 393 and 540 pixels. It checks the two independent status regions, Enter and Space activation of Clear Filters, search/Show/Element/Rarity reset, retained sorting, focus restoration, and unchanged synthetic game state. A disposable offline Chromium smoke run passed at all four widths. This is not a phone TalkBack or historical screenshot acceptance test.

Five-file source change: navigation JavaScript template, one browser regression, two CI registrations, and this document. No CSS, original art, game logic, save data, package identity, signer or installed app is changed.

Keep the PR draft until independent exact-head source/browser review and all PR source plus full signed Android checks and artifact identity gates pass. Preserve the working v265 owner install and game progress. Estimated UI completion 65%, full original game 30%, provisional.
