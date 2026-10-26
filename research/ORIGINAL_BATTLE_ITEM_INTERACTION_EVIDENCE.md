# Brave Frontier Global — Historical Battle-Item Interaction Evidence

Status: research notes for future **original-faithful** battle item implementation. Do not treat DEMO action/stock systems as native behavior.

## Recoverable original source facts

The 2022 translated table `3-mst-translated/F_ITEM_MST_Ver1027.json` in `mst-decoded.zip` (table SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`) contains item identity, effect group, target area, encoded effect parameters, and item-specific maximum equipped amounts. The v50 packaged source index includes 99 item-effect rows from that table (including legacy placeholders). It is evidence, not an executable inventory system.

Source examples: #21000 fills one ally's BB gauge, #52400 revives one KO ally to full HP, #20600 gives one ally +30% DEF for 3 turns, and #50400 gives living allies +50% ATK for 3 turns.

## Independent period documentation

- Agent86, 15 March 2014, *Brave Frontier Guide: Combat*, https://www.withoutthesarcasm.com/posts/brave-frontier-guide-combat/ : players choose up to a limited item loadout before quests. Targeted items **can only be used on units that have not yet moved**. The article describes attack/Guard and Brave Burst as separate unit commands. This does **not** establish an item's action-cost or native consumption-order algorithm.
- Agent86, *Brave Frontier Guide: Basics*, https://www.withoutthesarcasm.com/posts/brave-frontier-guide-basics/ : the original Item hut allows choosing **five item types** and (at that historical stage) **up to ten of each item**. Later 2022 item-specific caps differ; do not hard-code 2014 amounts for all item IDs.
- Brave Frontier Global Wiki, *Arena*, https://bravefrontierglobal.fandom.com/wiki/Arena : items are not usable in Arena; this is not relevant to regular quest-battle item availability.

The archived 2022 Global asset manifest lists `_dlcbundle/layout_battle_item_confirm.csv` and `_dlcbundle/layout_battle_item_unit_select.csv` as historical UI asset paths. The actual layout behavior and event scripting have **not** been decoded by those file names alone.

## Fidelity questions / next steps

1. Recover the authentic quest preparation and Item hut loadout, inventory amounts, and source recipe/drop or shop acquisition data. Treat equipped item quota separately from stored inventory.
2. Verify exactly whether battle-item use consumes the actor's command, whether multiple items may be used by the same ally during a round, whether using an item changes target eligibility, and whether it must happen before an action. Only the *target has not yet moved* restriction is independently supported above.
3. Implement source-native item effects, timing, and stacking; preserve all recoverable original name, scope and numeric parameters. Distinguish unknown math, such as the precise HP recovery formula for effect 520.
4. Preserve v7 saves through additive, validated migrations if later inventory state must be persisted, and preserve Android signing / no-network behavior.
5. Until those facts are resolved, all v42–v50 item `Guard` costs, one-charge stocks, and stacking details remain clearly labeled **DEMO**, separate from original reconstructed mechanics.

Do not promote a prototype as authenticated original behavior solely because the item's name and modifier are source-backed.
