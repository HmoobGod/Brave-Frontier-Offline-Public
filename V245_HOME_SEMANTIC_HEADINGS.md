# v245 — Original Global Home semantic heading hierarchy

**Purpose:** small UI/accessibility follow-up after merged v244 nav resource-budget safety work. Preserve the reconstructed original Global Home art, route behavior and demo gameplay.

## UI change
The main **GRAND GAIA** Home title now exposes a level-1 heading. Existing section titles **CURRENT SQUAD**, **ADVENTURE**, and **HOME SHORTCUTS** expose level-2 headings. Existing **AVAILABLE OFFLINE** and **RECOVERED GLOBAL LOCATIONS** retain their level-3 headings (as verified by v243), providing a logical 1 → 2 → 3 navigation order for assistive technology.

Vortex Gate, Arena, Raid Battle, Capital Randall and Exchange Hall are still read-only artwork previews. Their existing accessible names stay unchanged; `aria-disabled="true"` communicates the unavailable state explicitly. Exchange Hall also has a semantic group role. They remain **non-clickable, non-focusable, without handlers or fake routes**.

No original image files, CSS layout, sprite positioning, route names or gameplay controls changed. No Java/manifest/gradle, local storage, v7 save, summon economy, reward, signing, network access, or Current APK changes.

## Automated verification
New `test_bf_home_semantic_hierarchy_v24500.py` checks source semantics and runs Chromium against the actual nav bootstrap at 320/360/393/412/540 pixel widths. It validates heading order, disabled states, lack of interactive children on locked art, unchanged Quest/Summon navigation, JavaScript errors, offline manifest and resource cap. It runs source-only in the dedicated Android Back/UI preflight and full browser verification in the Android APK workflow. Existing v242, v243, v244, v227/v228 and independent save/build gates remain mandatory.

This patch is **UI-only/low risk**; use source and full CI as default acceptance. Escalate to Claude only if a material regression, ambiguous semantics, code-risk finding, or the planned v250 owner APK release milestone warrants independent review. No original 2022 device screenshot fidelity or physical phone acceptance is claimed.

**Base:** merged v244 main `310a8f84a88c8fd4251ee2f529533df8b2341530`. User's Current app and saves must not be overwritten.
