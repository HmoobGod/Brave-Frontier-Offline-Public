# v253 — Quest mission-card mobile UI follow-up

**Stacked dependency:** v252 PR #186 exact head `ab5c48b76ff87f055acf8047ff11d6159b8ce0e7` (not yet merged when v253 was authored). v253 must not merge until v252 is reviewed, fully CI-green, and merged; then retarget/revalidate v253 on current main.

**Owner directive:** UI only, target 100% **audited offline UI**, not original 2022 gameplay parity.

## Scope

Improve the existing Quest mission-list buttons using their **already referenced original mission_frame_off.png** art. Increase minimum touch/card height and padding, provide readable wrapped mission names and descriptions rather than clipped long English source names, and strengthen disabled versus enabled presentation, keyboard focus visibility, and pressed feedback. On screens narrower than 360px, increase target height while moderating text sizing. The existing `#questlist button.questcard[hidden]` filtering rule remains unchanged.

This change modifies **only CSS and test/CI/docs**. It does not invent quest data, unlock missions, create reward logic, edit enemy formations, alter the quest click handler, add new JavaScript, change `P`, network permissions, APK signing identity or save code. It does not assert that original game screens already match 2022 screenshots.

## Tests

`test_bf_quest_mission_cards_v25300.py --source-only` asserts original art reference, styles for disabled/focus/pressed, minimum dimensions, source size budget, no save/quests/network writes and source/preflight registrations. Browser mode renders real v252 navigation bootstrap with representative Quest mission buttons at 320, 360, 393, 412 and 540px. It checks active and disabled visibility, hidden quest filtering, original-art CSS linkage, text wrapping, >=68px target height, reduced opacity for locked rows, visible focus, route switching and no overflow/JS error. This is a CSS/fixture smoke test; original game save migration, source-text authenticity and physical-device fidelity remain independent.

**Gate:** exact-head green source preflights, full signed Android Build, and source-level Claude review if the stacked base or UI behavior creates new risk. No owner APK installation automatically follows merge.

## UI progress

UI/engine ~65% remains a provisional planning estimate; v253 does not automatically increase it. Continue Quest/Battle, Units/Box, Summon, Saves/Settings and inactive original Global location polish until each UI screen meets screenshot/device/accessibility acceptance.
