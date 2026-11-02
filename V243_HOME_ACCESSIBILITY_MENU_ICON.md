# v243 — Original Home UI legibility & narrow-screen Menu icon

**UI-first visible patch; draft pending exact-head Android CI and Claude review.** Follow-up to merged v242 Home hierarchy. These are **three specific visual/accessibility corrections** Claude identified in the v242 review:

- **320/360dp phones:** the original Global Menu image (`home_new_btn_menu1.png`) incorrectly inherited the `footer_btn2.png` atlas background-size on small screens. Reapply `background-size:contain` at the end of the 360dp media rule; the original PNG and its alt/navigation label remain unchanged.
- **Home locked destinations:** Vortex Gate, Arena, Raid and Randall remain disabled original-art previews, but each is now exposed to assistive tech as a labeled `role=group` rather than four anonymous `NOT YET AVAILABLE` divs. The two section captions become semantic level-3 headings; Quest/Summon stay the only two enabled destinations.
- **Readability:** raise locked status labels from 8px to 10px and muted art opacity from .62 to .76 while keeping them clearly distinguishable from the featured playable cards.

No page route, Java, manifest, game state, player v7 save, rewards, battle system, existing art bytes, installer/package ID or signing changes. Existing five route buttons and Save/export/import controls unchanged. New source + Playwright checks evaluate MENU background-size/image, locked status computed font size and image `object-fit:contain`, role labels, and Quest/Menu routing at 320/360/393/412/540px. Existing v242 Home source/browser, v227 accessibility, v228 asset budget, full Android and separate diagnostic package tests remain required.

Original 2022 gameplay parity and real on-device screenshot fidelity not claimed. v250 remains intended owner APK checkpoint; Current v124 and real save are not modified.
