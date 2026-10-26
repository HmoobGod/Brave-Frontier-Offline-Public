# Brave Frontier Global v64.00 — Battle-Legal Ailment Remedy Command

Base: exact green v63.00 commit 1a93792e4e91625dbbc73acfcb8517599986d479, GitHub Actions Build #278.

The original 2022 F_ITEM_MST_Ver1027 translated master identifies cure items #20200 (Poison), #20210 (Weakness/Sickness/Injury), #20220 (Curse), #20230 (Paralysis) and #50200 (all ailments). v57 provides validated, selective `ail.cure` logic; v64 exposes it as an optional battle command to cure an afflicted living ally using a separate eligible acting unit. Selective cure retains any unrelated codes; a universal remedy clears all. An acting unit consumes its existing DEMO Guard reservation. The panel only appears when ailments exist and archive battle mode is selected.

**Original-backed:** cure item IDs and status scopes. **Simulation only:** one charge per source item type per battle, item ownership/economy, Guard as cost, targeting UI/timing, status generation. No claimed native cures inventory or enemy ailment infliction probabilities. No save-state, storage, source archive, signing, package ID or Android permissions change. Prevent double spends by using v45 shared turn reservations and checking current stock. Reset temporary stock only when S battle object changes.

Verify Chromium test `test_bf_status_remedy_command_v6400.py`, all inherited regressions, v64 packaged APK check, debug signer continuity. This commit is candidate until Actions is successful and APK artifact uploaded.
