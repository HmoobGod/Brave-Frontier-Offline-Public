# v260 — Mobile Battle command controls: touch-size and wrapping

**UI-only priority:** Continue Brave Frontier Global offline interface improvements toward screen-by-screen acceptance. The **UI ~65% and full-game ~30% remain provisional**; this patch does not establish original 2022 screenshot parity or change combat.

**Stacked dependencies:** v260 follows v259 PR #193 exact head `2860551885bb2fd1bbf15f2fc8c31b090b241502`, then v258 PR #192, v257 PR #191 and v256 PR #190. v256 still requires **independent Claude exact-head review** of destructive/reset save-control appearance before any merge. Do not merge or automatically install v260 while those gates remain open.

## User-facing fix

The existing optional v21.00 **SQUAD COMMANDS · DEMO COMBAT** tray injects its own 37px enemy target and 44px batch-command button styles at runtime. The existing v20.00 story-battle button style uses 42px targets. On narrow phones these are smaller than the 48px mobile accessibility target used elsewhere. Long enemy names, HP readouts and command labels also need reliable wrapping.

A small scoped, append-only `bf_home_nav.css` patch:
- Makes optional tray enemy targets at least **48px** high and batch-action buttons at least **50px**, with readable wrapping and keyboard focus.
- Makes story-battle navigation buttons at least **48px** high; existing buttons, IDs, handlers and disabled states remain unchanged.
- Gives the real original-art Attack/Guard/BB action buttons a **50px** minimum touch height even where the older <=355px rule reduced them to 45px; preserves background source sprites, disabled cues and click handlers.
- Uses a one-column command grid at **320–359px**, two columns at **360px+**, keeping target selection as wrap-capable pill buttons.
- Scopes the selectors to the existing `body.bf-menu-mode` and known battle IDs to outrank the v20/v21 runtime-injected CSS without modifying those original scripts.

## Test and limits

`test_bf_battle_mobile_controls_v26000.py` uses a source-only fail-closed check and isolated Chromium fixtures at 320/359/360/393/412/540px. Crucially, fixture styles reproduce the later runtime CSS injection (37/42/44px originals) so the new CSS must actually win the cascade. It checks touch dimensions, no horizontal overflow, label wrapping, keyboard focus, disabled state, enemy `aria-pressed`, route hide/show and an ordinary button click. Registered in existing Android Back source preflight and signed APK workflow.

This is **not** a gameplay test, APK installation, owner-device screenshot acceptance, original Global visual parity or full v7 save acceptance. Real phone screenshots of Battle commands, target selection, damaged/disabled buttons, turn results, and historical Global layout comparison remain outstanding.

## Non-negotiable safety

No JavaScript or combat-command state-machine changes. No quests, enemies, Brave Burst gauge, auto mode, damage, rewards, gems, save handlers, save schema, user assets, signing, Java/Gradle/manifest or installed device modification. Preserve `org.bravefrontier.offline`, `bf_global_offline_demo_v7`, the owner's signed v251 APK and backed-up prior progress. Merge only after **sequential upstream merges**, retargeting to current main, all exact-head source preflights and full signed Android CI.
