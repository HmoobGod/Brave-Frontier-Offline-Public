package org.bravefrontier.offline;

import android.app.Activity;
import android.os.Bundle;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.WindowManager;
import android.view.WindowInsets;
import android.view.View;
import android.widget.FrameLayout;
import android.content.res.Configuration;
import android.graphics.Color;
import android.util.Base64;
import android.os.Build;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** Entire game ships inside the APK; SaveBridge uses Android's Storage Access Framework.
 *  User-selected documents only. No cloud sync, accounts, or INTERNET permission.
 */
public class MainActivity extends Activity {
    private WebView game;
    private FrameLayout gameContainer;
    private ValueCallback<Uri[]> pendingUpload;
    private String saveToWrite;
    private static final int PICK_BACKGROUND = 1001;
    private static final int PICK_SAVE_FILE = 1002;
    private static final int CREATE_SAVE_FILE = 1003;
    private static final int MAX_SAVE_BYTES = 1024 * 1024;

    // Small, bounded local UI resources; never read files outside this APK.
    private String readPackagedText(String file) throws IOException {
        try (InputStream in = getAssets().open(file); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[4096];
            int count;
            while ((count = in.read(buffer)) != -1) {
                if (out.size() + count > 64 * 1024) throw new IOException("Oversized UI resource");
                out.write(buffer, 0, count);
            }
            return new String(out.toByteArray(), StandardCharsets.UTF_8);
        }
    }
    private void toGame(String fn, String... arguments) {
        if (game == null) return;
        StringBuilder call = new StringBuilder("window.BFNativeTransfer && window.BFNativeTransfer.")
                .append(fn).append('(');
        for (int i = 0; i < arguments.length; i++) {
            if (i > 0) call.append(',');
            call.append(JSONObject.quote(arguments[i]));
        }
        call.append(");");
        game.evaluateJavascript(call.toString(), null);
    }
    public final class SaveBridge {
        @JavascriptInterface public void importSaveFile() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                try { startActivityForResult(intent, PICK_SAVE_FILE); }
                catch (ActivityNotFoundException ex) { toGame("error", "No Android file picker is available."); }
            });
        }
        @JavascriptInterface public void exportSaveFile(String json, String filename) {
            runOnUiThread(() -> {
                if (json == null || json.getBytes(StandardCharsets.UTF_8).length > MAX_SAVE_BYTES) {
                    toGame("error", "Save is too large (1 MB limit).");return;
                }
                saveToWrite = json;
                // Filename originates in packaged Javascript, but still sanitize defensively.
                String safe = filename == null ? "BraveFrontier-Offline.json" :
                        filename.replaceAll("[^A-Za-z0-9._-]", "_");
                if (!safe.endsWith(".json")) safe += ".json";
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("application/json");
                intent.putExtra(Intent.EXTRA_TITLE, safe);
                try { startActivityForResult(intent, CREATE_SAVE_FILE); }
                catch (ActivityNotFoundException ex) {
                    saveToWrite = null;toGame("error", "No Android save destination picker is available.");
                }
            });
        }
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        // Keep status/navigation bars visible; pad our *container* for enforced
        // edge-to-edge on targetSdk 35 / Android 15. Device testing still required.
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().setStatusBarColor(Color.rgb(14, 21, 33));
        getWindow().setNavigationBarColor(Color.rgb(14, 21, 33));
        gameContainer = new FrameLayout(this);
        gameContainer.setBackgroundColor(Color.rgb(14, 21, 33));
        gameContainer.setOnApplyWindowInsetsListener((v, insets) -> {
            // Android 15+ enforces edge-to-edge for targetSdk 35. On older
            // systems the decor already fits content within system bars.
            if (android.os.Build.VERSION.SDK_INT >= 35) {
                // The union selects the IME while the keyboard is showing,
                // otherwise the system bars and display cutouts.
                android.graphics.Insets safe = insets.getInsets(
                        WindowInsets.Type.systemBars() |
                        WindowInsets.Type.displayCutout() |
                        WindowInsets.Type.ime());
                v.setPadding(safe.left, safe.top, safe.right, safe.bottom);
            } else {
                v.setPadding(0, 0, 0, 0);
            }
            return insets;
        });
        game = new WebView(this);
        game.setBackgroundColor(Color.rgb(14, 21, 33));
        game.setOverScrollMode(WebView.OVER_SCROLL_NEVER);
        game.setWebViewClient(new WebViewClient() {
            // Load the independent navigation layer after the original page completes.
            // Inline injection avoids file:// cross-file script restrictions.
            @Override public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if (!"file:///android_asset/index.html".equals(url)) return;
                try {
                    String css = readPackagedText("bf_home_nav.css");
                    String js = readPackagedText("bf_home_nav.js");
                    view.evaluateJavascript(
                            "(function(){var style=document.createElement('style');" +
                            "style.textContent=" + JSONObject.quote(css) +
                            ";document.head.append(style);})();", null);
                    view.evaluateJavascript(js, null);
                    // v0.54: additive status overlay loaded AFTER the navigation header.
                    // Missing optional UI never blocks the original game or saves.
                    try {
                        String statusHud = readPackagedText("bf054_header_status.js");
                        view.evaluateJavascript(statusHud, null);
                    } catch (IOException headerError) {
                        android.util.Log.w("BraveFrontier", "Optional status overlay unavailable", headerError);
                    }
                    // v0.80: source-backed Morgan map is a separate small optional
                    // navigation extension, after the existing Mistral UI is ready.
                    try {
                        String morgan = readPackagedText("bf080_morgan_map.js");
                        view.evaluateJavascript(morgan, null);
                    } catch (IOException morganError) {
                        android.util.Log.w("BraveFrontier", "Optional Morgan map unavailable", morganError);
                    }
                    // v0.90: St. Lamia is a third independent original region.
                    try {
                        String stLamia = readPackagedText("bf090_st_lamia_map.js");
                        view.evaluateJavascript(stLamia, null);
                    } catch (IOException lamiaError) {
                        android.util.Log.w("BraveFrontier", "Optional St. Lamia map unavailable", lamiaError);
                    }
                    // v1.00-demo: read-only story progress across recovered regions.
                    try {
                        String campaign = readPackagedText("bf100_grand_gaia_campaign.js");
                        view.evaluateJavascript(campaign, null);
                    } catch (IOException campaignError) {
                        android.util.Log.w("BraveFrontier", "Optional campaign overview unavailable", campaignError);
                    }
                    // v1.01: optional unlock-gated Continue Story across 106 original quests.
                    try {
                        String continueStory = readPackagedText("bf101_story_continue.js");
                        view.evaluateJavascript(continueStory, null);
                    } catch (IOException continueError) {
                        android.util.Log.w("BraveFrontier", "Optional story continuation unavailable", continueError);
                    }
                    // v1.10: source-backed 106-mission journal; optional and save-read-only.
                    try {
                        String questJournal = readPackagedText("bf110_quest_journal.js");
                        view.evaluateJavascript(questJournal, null);
                    } catch (IOException journalError) {
                        android.util.Log.w("BraveFrontier", "Optional quest journal unavailable", journalError);
                    }
                    // v20.00: authentic 2022 quest metadata + live existing DEMO battle HUD.
                    // Optional and read-only; no native formula or save-schema changes.
                    try {
                        String storyHud = readPackagedText("bf2000_story_battle_hud.js");
                        view.evaluateJavascript(storyHud, null);
                    } catch (IOException storyHudError) {
                        android.util.Log.w("BraveFrontier", "Optional quest battle tracker unavailable", storyHudError);
                    }
                    // v21.00: additive, save-free battle command shortcuts.
                    try {
                        String commands = readPackagedText("bf2100_battle_command_tray.js");
                        view.evaluateJavascript(commands, null);
                    } catch (IOException commandsError) {
                        android.util.Log.w("BraveFrontier", "Optional battle commands unavailable", commandsError);
                    }
                    // v22.00: read-only 2022 Global event-script dialogue, quest-unlock gated.
                    try {
                        String events = readPackagedText("bf2200_original_event_reader.js");
                        view.evaluateJavascript(events, null);
                    } catch (IOException eventError) {
                        android.util.Log.w("BraveFrontier", "Optional original event dialogue unavailable", eventError);
                    }
                    // v23.00: original 2022 Morgan source-script dialogue.
                    try {
                        String morganDialogue = readPackagedText("bf2300_morgan_event_dialogue.js");
                        view.evaluateJavascript(morganDialogue, null);
                    } catch (IOException e) {
                        android.util.Log.w("BraveFrontier", "Optional Morgan story dialogue unavailable", e);
                    }
                    // v24.00: source-verified St. Lamia dialogue; exclude conflicting 350 script.
                    try {
                        String lamiaDialogue = readPackagedText("bf2400_st_lamia_event_dialogue.js");
                        view.evaluateJavascript(lamiaDialogue, null);
                    } catch (IOException e) {
                        android.util.Log.w("BraveFrontier", "St. Lamia dialogue unavailable", e);
                    }
                    // v25.00: contextual read-only source story prompts in playable missions.
                    try {
                        String cue = readPackagedText("bf2500_story_event_prompt.js");
                        view.evaluateJavascript(cue, null);
                    } catch (IOException e) {
                        android.util.Log.w("BraveFrontier", "Optional original story cue unavailable", e);
                    }
                    // v26.00: exact archived 2022 event character illustrations.
                    try {
                        String portraits = readPackagedText("bf2600_original_event_portraits.js");
                        view.evaluateJavascript(portraits, null);
                    } catch (IOException e) {
                        android.util.Log.w("BraveFrontier", "Original event portraits unavailable", e);
                    }
                    // v27.00: read-only 2022 event-script original dungeon backdrops.
                    try {
                        String eventStage = readPackagedText("bf2700_original_event_stage.js");
                        view.evaluateJavascript(eventStage, null);
                    } catch (IOException stageError) {
                        android.util.Log.w("BraveFrontier", "Optional original event backdrop unavailable", stageError);
                    }
                    // v28.00: speaker frames linked to archived original 2022 events.
                    try {
                        String speakers = readPackagedText("bf2800_dialogue_speaker_cues.js");
                        view.evaluateJavascript(speakers, null);
                    } catch (IOException speakerError) {
                        android.util.Log.w("BraveFrontier", "Optional original speaker metadata unavailable", speakerError);
                    }
                    // v29.00: exact original 2022 expression frames, no save or combat changes.
                    try {
                        String expressions = readPackagedText("bf2900_original_event_expressions.js");
                        view.evaluateJavascript(expressions, null);
                    } catch (IOException expressionError) {
                        android.util.Log.w("BraveFrontier", "Original expression reader unavailable", expressionError);
                    }
                    // v30.00: playable post-battle results and native replay/progression.
                    try {
                        String battleResults = readPackagedText("bf3000_battle_results.js");
                        view.evaluateJavascript(battleResults, null);
                    } catch (IOException resultError) {
                        android.util.Log.w("BraveFrontier", "Optional battle results unavailable", resultError);
                    }
                    // v31.00: optional enemy focus using existing demo battle commands.
                    try {
                        String focus = readPackagedText("bf3100_battle_focus.js");
                        view.evaluateJavascript(focus, null);
                    } catch (IOException focusError) {
                        android.util.Log.w("BraveFrontier", "Optional tactical focus unavailable", focusError);
                    }
                    // v32.00: retain in-memory demo battle logs, never modify saves.
                    try {
                        String journal = readPackagedText("bf3200_combat_journal.js");
                        view.evaluateJavascript(journal, null);
                    } catch (IOException journalError) {
                        android.util.Log.w("BraveFrontier", "Optional combat journal unavailable", journalError);
                    }
                    // v33.00: optional page timing controls for recovered story dialogues.
                    try {
                        String playback = readPackagedText("bf3300_story_playback.js");
                        view.evaluateJavascript(playback, null);
                    } catch (IOException playError) {
                        android.util.Log.w("BraveFrontier", "Optional story playback unavailable", playError);
                    }
                    // v34.00: optional archived event sprite X/Y staging reference.
                    try {
                        String placement = readPackagedText("bf3400_source_scene_placement.js");
                        view.evaluateJavascript(placement, null);
                    } catch (IOException placementError) {
                        android.util.Log.w("BraveFrontier", "Optional source scene placement unavailable", placementError);
                    }
                    // v35.00: optional unlocked original source story line navigation.
                    try {
                        String timeline = readPackagedText("bf3500_dialogue_timeline.js");
                        view.evaluateJavascript(timeline, null);
                    } catch (IOException timelineError) {
                        android.util.Log.w("BraveFrontier", "Optional dialogue line navigator unavailable", timelineError);
                    }
                    // v36.00: single original event JPG and exact expression PNG scene preview.
                    try {
                        String composite = readPackagedText("bf3600_event_composite.js");
                        view.evaluateJavascript(composite, null);
                    } catch (IOException compositeError) {
                        android.util.Log.w("BraveFrontier", "Optional composite source event unavailable", compositeError);
                    }
                    // v37.00: optional full-screen original archive story mode.
                    try {
                        String cinema = readPackagedText("bf3700_cinematic_reader.js");
                        view.evaluateJavascript(cinema, null);
                    } catch (IOException cinemaError) {
                        android.util.Log.w("BraveFrontier", "Optional cinematic story reader unavailable", cinemaError);
                    }
                    // v38.00: optional 2022 original dungeon JPG as live demo battle backdrop.
                    try {
                        String backdrop = readPackagedText("bf3800_source_battle_backdrop.js");
                        view.evaluateJavascript(backdrop, null);
                    } catch (IOException backdropError) {
                        android.util.Log.w("BraveFrontier", "Optional original dungeon battle image unavailable", backdropError);
                    }
                    // v39.00: optional original event intro to active demo battle navigation.
                    try {
                        String handoff = readPackagedText("bf3900_story_battle_handoff.js");
                        view.evaluateJavascript(handoff, null);
                    } catch (IOException handoffError) {
                        android.util.Log.w("BraveFrontier", "Optional story-to-battle handoff unavailable", handoffError);
                    }
                    // v40.00: demo victory to next unlocked original 2022 chapter introduction.
                    try {
                        String nextIntro = readPackagedText("bf4000_next_chapter_intro.js");
                        view.evaluateJavascript(nextIntro, null);
                    } catch (IOException nextIntroError) {
                        android.util.Log.w("BraveFrontier", "Optional next-chapter original intro unavailable", nextIntroError);
                    }
                    // v41.00: optional source-backed quest title over the DEMO battlefield.
                    try {
                        String banner = readPackagedText("bf4100_live_quest_banner.js");
                        view.evaluateJavascript(banner, null);
                    } catch (IOException bannerError) {
                        android.util.Log.w("BraveFrontier", "Optional live quest banner unavailable", bannerError);
                    }
                    // v45.00: one session-only item use per acting unit/round.
                    // Load before v42-v44 optional items. No save fields changed.
                    try {
                        String itemTurns = readPackagedText("bf4500_item_turn_reservations.js");
                        view.evaluateJavascript(itemTurns, null);
                    } catch (IOException itemTurnsError) {
                        android.util.Log.w("BraveFrontier", "Optional item reservation unavailable", itemTurnsError);
                    }
                    // v42.00: optional DEMO battle Potion, temporary and never saved.
                    try {
                        String potion = readPackagedText("bf4200_demo_potion_command.js");
                        view.evaluateJavascript(potion, null);
                    } catch (IOException potionError) {
                        android.util.Log.w("BraveFrontier", "Optional demo battle Potion unavailable", potionError);
                    }
                    // v43.00: archived 2022 party-healing item scope, optional DEMO effect.
                    try {
                        String partyHeal = readPackagedText("bf4300_source_party_heal.js");
                        view.evaluateJavascript(partyHeal, null);
                    } catch (IOException partyHealError) {
                        android.util.Log.w("BraveFrontier", "Optional party-heal source prototype unavailable", partyHealError);
                    }
                    // v44.00: source-backed +30% ATK for 3 DEMO rounds, session-only.
                    try {
                        String atkItem = readPackagedText("bf4400_source_atk_item.js");
                        view.evaluateJavascript(atkItem, null);
                    } catch (IOException atkItemError) {
                        android.util.Log.w("BraveFrontier", "Optional source ATK item unavailable", atkItemError);
                    }
                    // v46.00: source-verified 2022 BB gauge maximum, DEMO item action.
                    try {
                        String bbItem = readPackagedText("bf4600_source_bb_gauge_item.js");
                        view.evaluateJavascript(bbItem, null);
                    } catch (IOException bbItemError) {
                        android.util.Log.w("BraveFrontier", "Optional source BB item unavailable", bbItemError);
                    }
                    // v47.00: original full-HP revival effect with DEMO action costs.
                    try {
                        String fullRevive = readPackagedText("bf4700_source_full_revive.js");
                        view.evaluateJavascript(fullRevive, null);
                    } catch (IOException reviveError) {
                        android.util.Log.w("BraveFrontier", "Optional source full revive unavailable", reviveError);
                    }
                    // v48.00: prevent DEMO Auto Battle from double-spending a reserved item turn.
                    try {
                        String autoGuard = readPackagedText("bf4800_demo_auto_item_guard.js");
                        view.evaluateJavascript(autoGuard, null);
                    } catch (IOException autoGuardError) {
                        android.util.Log.w("BraveFrontier", "Optional item Auto safety unavailable", autoGuardError);
                    }
                    // v49.00: original single-target DEF item +30% for 3 DEMO rounds.
                    try {
                        String sourceDef = readPackagedText("bf4900_source_def_item.js");
                        view.evaluateJavascript(sourceDef, null);
                    } catch (IOException defItemError) {
                        android.util.Log.w("BraveFrontier", "Optional source DEF item unavailable", defItemError);
                    }
                    // v50.00: original 2022 all-ally ATK item, temporary DEMO inventory.
                    try {
                        String partyAtk = readPackagedText("bf5000_source_party_atk_item.js");
                        view.evaluateJavascript(partyAtk, null);
                    } catch (IOException partyAtkError) {
                        android.util.Log.w("BraveFrontier", "Optional party ATK item unavailable", partyAtkError);
                    }
                    // v51: archived one-ally double ATK item; DEMO charge/Guard only.
                    try {
                        String doubleAtk = readPackagedText("bf5100_source_double_atk_item.js");
                        view.evaluateJavascript(doubleAtk, null);
                    } catch (IOException doubleAtkError) {
                        android.util.Log.w("BraveFrontier", "Optional double ATK item unavailable", doubleAtkError);
                    }
                    // v52: 2022 source-backed single-ally double DEF; DEMO Guard cost.
                    try {
                        String doubleDef = readPackagedText("bf5200_source_double_def_item.js");
                        view.evaluateJavascript(doubleDef, null);
                    } catch (IOException doubleDefError) {
                        android.util.Log.w("BraveFrontier", "Optional double DEF item unavailable", doubleDefError);
                    }
                    // v53.00: 2022 original party DEF +50%; temporary DEMO stock.
                    try {
                        String partyDef = readPackagedText("bf5300_source_party_def_item.js");
                        view.evaluateJavascript(partyDef, null);
                    } catch (IOException partyDefError) {
                        android.util.Log.w("BraveFrontier", "Optional party DEF item unavailable", partyDefError);
                    }
                    // v54.00: source-backed Hope Light party HP recovery, DEMO healing calculation.
                    try {
                        String hopeLight = readPackagedText("bf5400_source_hope_light.js");
                        view.evaluateJavascript(hopeLight, null);
                    } catch (IOException hopeLightError) {
                        android.util.Log.w("BraveFrontier", "Optional Hope Light item unavailable", hopeLightError);
                    }
                    // v55.00: archived Strong Life single-ally recovery, DEMO HP math.
                    try {
                        String strongLife = readPackagedText("bf5500_source_strong_life.js");
                        view.evaluateJavascript(strongLife, null);
                    } catch (IOException strongLifeError) {
                        android.util.Log.w("BraveFrontier", "Optional Strong Life unavailable", strongLifeError);
                    }
                    // v56.00: original 2022 Life Potion one-ally heal; DEMO HP math.
                    try {
                        String lifePotion = readPackagedText("bf5600_source_life_potion.js");
                        view.evaluateJavascript(lifePotion, null);
                    } catch (IOException lifePotionError) {
                        android.util.Log.w("BraveFrontier", "Optional Life Potion unavailable", lifePotionError);
                    }
                    // v57.00: original ailment identity/cure-state foundation only.
                    try {
                        String originalAilments = readPackagedText("bf5700_original_ailment_state.js");
                        view.evaluateJavascript(originalAilments, null);
                    } catch (IOException ailmentError) {
                        android.util.Log.w("BraveFrontier", "Optional original ailment state unavailable", ailmentError);
                    }
                    // v58.00: Global-era poison HP-per-turn reference, demo rounding.
                    try {
                        String poisonTurn = readPackagedText("bf5800_poison_turn.js");
                        view.evaluateJavascript(poisonTurn, null);
                    } catch (IOException poisonError) {
                        android.util.Log.w("BraveFrontier", "Optional poison turn handling unavailable", poisonError);
                    }
                    // v59.00: original-source Curse code, community-described BB lock.
                    try {
                        String curseBB = readPackagedText("bf5900_curse_bb_lock.js");
                        view.evaluateJavascript(curseBB, null);
                    } catch (IOException curseError) {
                        android.util.Log.w("BraveFrontier", "Optional Curse BB lock unavailable", curseError);
                    }
                    // v60.00: source-status Paralysis denial of DEMO unit actions.
                    try {
                        String paralysis = readPackagedText("bf6000_paralysis_action_lock.js");
                        view.evaluateJavascript(paralysis, null);
                    } catch (IOException paralysisError) {
                        android.util.Log.w("BraveFrontier", "Optional Paralysis action lock unavailable", paralysisError);
                    }
                    // v80.00: v61 Weakness now subtracts -50% from source DEF buffs rather than halving a buffed stat.
                    // v61.00: community-documented Weakness DEF reduction during DEMO enemy damage.
                    try {
                        String weakness = readPackagedText("bf6100_weakness_defense.js");
                        view.evaluateJavascript(weakness, null);
                    } catch (IOException weaknessError) {
                        android.util.Log.w("BraveFrontier", "Optional Weakness DEF integration unavailable", weaknessError);
                    }
                    // v62.00: community-documented Injury ATK penalty in DEMO actions.
                    try {
                        String injury = readPackagedText("bf6200_injury_attack.js");
                        view.evaluateJavascript(injury, null);
                    } catch (IOException injuryError) {
                        android.util.Log.w("BraveFrontier", "Optional Injury ATK integration unavailable", injuryError);
                    }
                    // v64.00: original-source ailment remedies, explicit DEMO battle command.
                    try {
                        String remedies = readPackagedText("bf6400_status_remedy_command.js");
                        view.evaluateJavascript(remedies, null);
                    } catch (IOException remedyError) {
                        android.util.Log.w("BraveFrontier", "Optional ailment remedy command unavailable", remedyError);
                    }
                    // v65.00: Global Sickness status reduces REC during DEMO player actions.
                    try {
                        String sickness = readPackagedText("bf6500_sickness_recovery.js");
                        view.evaluateJavascript(sickness, null);
                    } catch (IOException sicknessError) {
                        android.util.Log.w("BraveFrontier", "Optional Sickness REC effect unavailable", sicknessError);
                    }
                    // v79.00: original Injury -50% ATK is additive with positive buffs
                    // in the existing v62 action hook; no new JavaScript load order.
                    // v66.00 Curse item-restore gate is integrated in the v46 source module.
                    // v67.00: additive original burst-healing REC contribution.
                    try {
                        String recipientREC = readPackagedText("bf6700_burst_recipient_rec.js");
                        view.evaluateJavascript(recipientREC, null);
                    } catch (IOException burstRecError) {
                        android.util.Log.w("BraveFrontier", "Optional burst recipient REC rule unavailable", burstRecError);
                    }
                    // v68.00: source-verifiable healing BB level 1–10 preview only.
                    try {
                        String healLevels = readPackagedText("bf6800_original_heal_bb_levels.js");
                        view.evaluateJavascript(healLevels, null);
                    } catch (IOException healLevelError) {
                        android.util.Log.w("BraveFrontier", "Optional healing BB level preview unavailable", healLevelError);
                    }
                    // v69.00: original elemental matchups, only when both combatants have known elements.
                    try {
                        String element = readPackagedText("bf6900_elemental_combat.js");
                        view.evaluateJavascript(element, null);
                    } catch (IOException elementError) {
                        android.util.Log.w("BraveFrontier", "Optional original elemental combat unavailable", elementError);
                    }
                    // v71.00: source-exact ten-level ATK support BB preview, save-safe.
                    try {
                        String atkLevels = readPackagedText("bf7100_original_atk_bb_levels.js");
                        view.evaluateJavascript(atkLevels, null);
                    } catch (IOException atkLevelsError) {
                        android.util.Log.w("BraveFrontier", "Optional original ATK BB level preview unavailable", atkLevelsError);
                    }
                    // v74.00: source-backed single ally 1000/2000 HP recovery potions.
                    try {
                        String potions = readPackagedText("bf7400_original_strong_potions.js");
                        view.evaluateJavascript(potions, null);
                    } catch (IOException recoveryPotionError) {
                        android.util.Log.w("BraveFrontier", "Optional archived recovery potions unavailable", recoveryPotionError);
                    }
                    // v75.00: exact original 2022 Saint Light 1000 HP all allies.
                    try {
                        String saint = readPackagedText("bf7500_original_saint_light.js");
                        view.evaluateJavascript(saint, null);
                    } catch (IOException saintError) {
                        android.util.Log.w("BraveFrontier", "Optional Saint Light unavailable", saintError);
                    }
                    // v76.00: original all-ailment status negation with 3-turn source.
                    try {
                        String nullifier = readPackagedText("bf7600_original_status_nullifier.js");
                        view.evaluateJavascript(nullifier, null);
                    } catch (IOException nullifierError) {
                        android.util.Log.w("BraveFrontier", "Optional original Nullifier unavailable", nullifierError);
                    }
                    // v77.00: original Global Regeneration Light three-turn group recovery.
                    try {
                        String regen = readPackagedText("bf7700_original_party_regen.js");
                        view.evaluateJavascript(regen, null);
                    } catch (IOException regenError) {
                        android.util.Log.w("BraveFrontier", "Optional party gradual recovery unavailable", regenError);
                    }
                    // v78.00: read-only all-ally battle status display for sourced ailments.
                    try {
                        String battleStatus = readPackagedText("bf7800_live_battle_status.js");
                        view.evaluateJavascript(battleStatus, null);
                    } catch (IOException statusError) {
                        android.util.Log.w("BraveFrontier", "Optional live battle status unavailable", statusError);
                    }
                    // v1.20: 2014 historical source preview. Never alters demo combat.
                    try {
                        String historic = readPackagedText("bf120_historical_encounters.js");
                        view.evaluateJavascript(historic, null);
                    } catch (IOException historyError) {
                        android.util.Log.w("BraveFrontier", "Optional historical reference unavailable", historyError);
                    }
                } catch (IOException ex) {
                    android.util.Log.e("BraveFrontier", "Home navigation unavailable; game still playable", ex);
                }
                // Separate small layer: Android's navigation reader caps each file
                // at 64 KiB. The 2,291-entry catalog is embedded as inert JSON in
                // index.html by the verified build-time preparation script.
                try {
                    String catalogStyle = readPackagedText("bf_global_unit_archive.css");
                    String catalogScript = readPackagedText("bf_global_unit_archive.js");
                    view.evaluateJavascript(
                            "(function(){var style=document.createElement('style');" +
                            "style.textContent=" + JSONObject.quote(catalogStyle) +
                            ";document.head.append(style);})();", null);
                    view.evaluateJavascript(catalogScript, null);
                    // v1.50: optional cross-era ID research and local QA; load
                    // only after the archived 2,291-unit catalog renderer.
                    try {
                        String crosscheck = readPackagedText("bf150_source_crosscheck.js");
                        view.evaluateJavascript(crosscheck, null);
                        // v2.00 optional 2014 practice sandbox; no native save/combat writes.
                        try {
                            String historicalLab = readPackagedText("bf200_historical_wave_lab.js");
                            view.evaluateJavascript(historicalLab, null);
                            // v87 historical 2014 mission AI/reward descriptors are read-only.
                            // Do not use these as native 2022 gameplay logic.
                            try {
                                String basicsAI = readPackagedText("bf8700_original_basics_ai_reference.js");
                                view.evaluateJavascript(basicsAI, null);
                            } catch (IOException basicsAIError) {
                                android.util.Log.w("BraveFrontier", "Optional historical 2014 AI reference unavailable", basicsAIError);
                            }
                            // v2.50: isolated squad training clones source-backed
                            // owned units; never alters real battle or local saves.
                            try {
                                String squadTraining = readPackagedText("bf250_squad_training.js");
                                view.evaluateJavascript(squadTraining, null);
                                // v3.00 optional coordinated tactical simulation.
                                // All practice data is RAM-only and cannot write saves.
                                try {
                                    // v5.00 original Global source data (optional, read-only).
                                    try {
                                        String originalBB = readPackagedText("bf500_source_bb_evidence.js");
                                        view.evaluateJavascript(originalBB, null);
                                    } catch (IOException sourceError) {
                                        android.util.Log.w("BraveFrontier", "Optional original BB evidence unavailable", sourceError);
                                    }
                                    // v7.00 additional original F_UNIT normal hit evidence.
                                    try {
                                        String originalHits = readPackagedText("bf700_original_normal_hits.js");
                                        view.evaluateJavascript(originalHits, null);
                                        // v81.00: pure original BC/HC drop-roll core after source hit data.
                                        String crystals = readPackagedText("bf8100_original_crystal_drop_core.js");
                                        view.evaluateJavascript(crystals, null);
                                        // v82.00 original F_UNIT normal attack BC dropCheckCount joins.
                                        String sourceChecks = readPackagedText("bf8200_original_normal_crystal_checks.js");
                                        view.evaluateJavascript(sourceChecks, null);
                                        // v83: source-joined BB/SBB per-skill drop checks, read-only.
                                        try {
                                            String burstChecks = readPackagedText("bf8300_original_burst_crystal_checks.js");
                                            view.evaluateJavascript(burstChecks, null);
                                            // v84 source-normal profiles across 2,258 original unit forms.
                                            try {
                                                String allNormals = readPackagedText("bf8400_original_normal_crystal_checks.js");
                                                view.evaluateJavascript(allNormals, null);
                                                // v88: sample source-backed normal crystal production only
                                                // after a real demo attack; do not invent pickups/BB or healing.
                                                try {
                                                    String normalEvents = readPackagedText("bf8800_live_normal_crystal_events.js");
                                                    view.evaluateJavascript(normalEvents, null);
                                                } catch (IOException normalEventsError) {
                                                    android.util.Log.w("BraveFrontier", "Optional source-normal battle events unavailable", normalEventsError);
                                                }
                                                // v85: source-backed all-unit BB per-skill BC evidence.
                                                try {
                                                    String allBurst = readPackagedText("bf8500_original_all_bb_checks.js");
                                                    view.evaluateJavascript(allBurst, null);
                                                    // v89 strictly source-supported single-group offensive BB
                                                    // reference crystals; actual pickups remain unresolved.
                                                    try {
                                                        String simpleBurstEvents = readPackagedText("bf8900_live_simple_bb_crystals.js");
                                                        view.evaluateJavascript(simpleBurstEvents, null);
                                                        // v90: source-validated read-only crystal ledger.
                                                        try {
                                                            String ledger = readPackagedText("bf9000_live_crystal_provenance.js");
                                                            view.evaluateJavascript(ledger, null);
                                                            // v91: exact 2022 original unit innate ailment immunity.
                                                            try {
                                                                String innateResist = readPackagedText("bf9100_innate_status_resistance.js");
                                                                view.evaluateJavascript(innateResist, null);
                                                                // v92: recovered BB Lv1–10 offensive power in real demo turns.
                                                                try {
                                                                    String offensiveLevels = readPackagedText("bf9200_source_offensive_bb_levels.js");
                                                                    view.evaluateJavascript(offensiveLevels, null);
                                                                    // v93 original single-hit critical base gameplay.
                                                                    try {
                                                                        String singleCrit = readPackagedText("bf9300_single_hit_critical_combat.js");
                                                                        view.evaluateJavascript(singleCrit, null);
                                                                        // v95: source-verified multi-hit normal critical strikes.
                                                                        try {
                                                                            String multiCrit = readPackagedText("bf9500_multihit_critical_combat.js");
                                                                            view.evaluateJavascript(multiCrit, null);
                                                                        } catch (IOException multiCritError) {
                                                                            android.util.Log.w("BraveFrontier", "Optional original multi-hit critical combat unavailable", multiCritError);
                                                                        }
                                                                    } catch (IOException singleCritError) {
                                                                        android.util.Log.w("BraveFrontier", "Optional original critical combat unavailable", singleCritError);
                                                                    }
                                                                } catch (IOException offensiveLevelsError) {
                                                                    android.util.Log.w("BraveFrontier", "Optional original offensive BB levels unavailable", offensiveLevelsError);
                                                                }
                                                            } catch (IOException innateResistError) {
                                                                android.util.Log.w("BraveFrontier", "Optional original innate status resistance unavailable", innateResistError);
                                                            }
                                                        } catch (IOException ledgerError) {
                                                            android.util.Log.w("BraveFrontier", "Optional source crystal ledger unavailable", ledgerError);
                                                        }
                                                    } catch (IOException simpleBurstError) {
                                                        android.util.Log.w("BraveFrontier", "Optional source BB crystal events unavailable", simpleBurstError);
                                                    }
                                                    // v86 source SBB/UBB per-skill check evidence.
                                                    try {
                                                        String allBurstTiers = readPackagedText("bf8600_original_all_sbb_ubb_checks.js");
                                                        view.evaluateJavascript(allBurstTiers, null);
                                                    } catch (IOException allBurstTiersError) {
                                                        android.util.Log.w("BraveFrontier", "Optional original SBB/UBB evidence unavailable", allBurstTiersError);
                                                    }
                                                } catch (IOException allBurstError) {
                                                    android.util.Log.w("BraveFrontier", "Optional original all BB evidence unavailable", allBurstError);
                                                }
                                            } catch (IOException allNormalError) {
                                                android.util.Log.w("BraveFrontier", "Optional original full normal profile evidence unavailable", allNormalError);
                                            }
                                        } catch (IOException burstCheckError) {
                                            android.util.Log.w("BraveFrontier", "Optional source burst drop-check evidence unavailable", burstCheckError);
                                        }
                                    } catch (IOException hitError) {
                                        android.util.Log.w("BraveFrontier", "Optional original normal hit evidence unavailable", hitError);
                                    }
                                    String rounds = readPackagedText("bf300_tactical_rounds.js");
                                    view.evaluateJavascript(rounds, null);
                                    // v4.00 original Global source dossier is read-only.
                                    // Load after archived unit catalog and tactical UI.
                                    try {
                                        String dossier = readPackagedText("bf400_original_battle_dossier.js");
                                        view.evaluateJavascript(dossier, null);
                                        // v8.00 practice-only draft from archived Global forms.
                                        try {
                                            String archiveDraft = readPackagedText("bf800_archive_draft.js");
                                            view.evaluateJavascript(archiveDraft, null);
                                            // v9.00 research hub stays closed until requested.
                                            try {
                                                String hub = readPackagedText("bf900_optional_labs_hub.js");
                                                view.evaluateJavascript(hub, null);
                                                // v10.00 read-only 2022 Global unit evolution links.
                                                try {
                                                    String evolution = readPackagedText("bf1000_original_evolution_paths.js");
                                                    view.evaluateJavascript(evolution, null);
                                                    // v14.00 read-only archive evolution material planner.
                                                    try {
                                                        String materialPlan = readPackagedText("bf1400_evolution_material_planner.js");
                                                        view.evaluateJavascript(materialPlan, null);
                                                        // v15.00 only documented original 2022 recipe path stages.
                                                        try {
                                                            String evolutionChain = readPackagedText("bf1500_evolution_chain.js");
                                                            view.evaluateJavascript(evolutionChain, null);
                                                            // v16.00 source recipe path -> reversible temporary draft evolution.
                                                            try {
                                                                String draftEvolved = readPackagedText("bf1600_draft_evolution.js");
                                                                view.evaluateJavascript(draftEvolved, null);
                                                                // v17.00 reversible multi-form original recipe batch planner.
                                                                try {
                                                                    String batchEvolved = readPackagedText("bf1700_batch_draft_evolution.js");
                                                                    view.evaluateJavascript(batchEvolved, null);
                                                                    // v18.00 exact source multi-stage evolution squad preview and undo.
                                                                    try {
                                                                        String multiStage = readPackagedText("bf1800_multistage_draft.js");
                                                                        view.evaluateJavascript(multiStage, null);
                                                                        // v19.00 matched source squad A/B synthetic combat.
                                                                        try {
                                                                            String evolutionAB = readPackagedText("bf1900_evolution_ab.js");
                                                                            view.evaluateJavascript(evolutionAB, null);
                                                                        } catch (IOException evolutionABError) {
                                                                            android.util.Log.w("BraveFrontier", "Optional evolution combat comparison unavailable", evolutionABError);
                                                                        }
                                                                    } catch (IOException multiStageError) {
                                                                        android.util.Log.w("BraveFrontier", "Optional sourced multi-stage draft unavailable", multiStageError);
                                                                    }
                                                                } catch (IOException batchError) {
                                                                    android.util.Log.w("BraveFrontier", "Optional batch source evolution unavailable", batchError);
                                                                }
                                                            } catch (IOException draftEvoError) {
                                                                android.util.Log.w("BraveFrontier", "Optional temporary source evolution unavailable", draftEvoError);
                                                            }
                                                        } catch (IOException chainError) {
                                                            android.util.Log.w("BraveFrontier", "Optional source evolution chain unavailable", chainError);
                                                        }
                                                    } catch (IOException materialError) {
                                                        android.util.Log.w("BraveFrontier", "Optional evolution material plan unavailable", materialError);
                                                    }
                                                } catch (IOException evoError) {
                                                    android.util.Log.w("BraveFrontier", "Optional original evolution source unavailable", evoError);
                                                }
                                            } catch (IOException hubError) {
                                                android.util.Log.w("BraveFrontier", "Optional research hub unavailable", hubError);
                                            }
                                        } catch (IOException draftError) {
                                            android.util.Log.w("BraveFrontier", "Optional archive draft unavailable", draftError);
                                        }
                                    } catch (IOException dossierError) {
                                        android.util.Log.w("BraveFrontier", "Optional original battle dossier unavailable", dossierError);
                                    }
                                } catch (IOException roundError) {
                                    android.util.Log.w("BraveFrontier", "Optional tactical rounds unavailable", roundError);
                                }
                            } catch (IOException squadError) {
                                android.util.Log.w("BraveFrontier", "Optional squad training unavailable", squadError);
                            }
                        } catch (IOException labError) {
                            android.util.Log.w("BraveFrontier", "Optional historical practice unavailable", labError);
                        }
                    } catch (IOException xrefError) {
                        android.util.Log.w("BraveFrontier", "Optional source crosscheck unavailable", xrefError);
                    }
                } catch (IOException ex) {
                    android.util.Log.e("BraveFrontier", "Unit archive preview unavailable; gameplay unaffected", ex);
                }
                // v97 QoL: additive local backups; no active-save or combat hooks.
                // Independently try this even if optional archive research is missing.
                try {
                    String qolBackups = readPackagedText("bf9700_qol_rotating_backups.js");
                    view.evaluateJavascript(qolBackups, null);
                } catch (IOException backupError) {
                    android.util.Log.w("BraveFrontier", "Optional local backup panel unavailable", backupError);
                }
                // v98 QoL: bounded replay of cleared quests via existing Auto + result API.
                try {
                    String qolRepeat = readPackagedText("bf9800_qol_cleared_quest_repeat.js");
                    view.evaluateJavascript(qolRepeat, null);
                } catch (IOException repeatError) {
                    android.util.Log.w("BraveFrontier", "Optional quest repeat unavailable", repeatError);
                }
                // v99 QoL: optional battle speeds and skip-presentation toggle.
                try {
                    String qolSpeed = readPackagedText("bf9900_qol_battle_speed.js");
                    view.evaluateJavascript(qolSpeed, null);
                } catch (IOException speedError) {
                    android.util.Log.w("BraveFrontier", "Optional battle speed UI unavailable", speedError);
                }
                // v100 QoL: manual owned-unit squad loadouts, no new save schema.
                try {
                    String qolSquads = readPackagedText("bf10000_qol_squad_presets.js");
                    view.evaluateJavascript(qolSquads, null);
                } catch (IOException squadPresetError) {
                    android.util.Log.w("BraveFrontier", "Optional squad presets unavailable", squadPresetError);
                }
                // v101 QoL: unlock-gated, already-viewed source dialogue skips.
                try {
                    String viewed = readPackagedText("bf10100_qol_viewed_dialogue.js");
                    view.evaluateJavascript(viewed, null);
                } catch (IOException viewedError) {
                    android.util.Log.w("BraveFrontier", "Optional viewed dialogue control unavailable", viewedError);
                }
                // v102 QoL: advisory owned-unit favorites and lock markers.
                try {
                    String markers = readPackagedText("bf10200_qol_unit_flags.js");
                    view.evaluateJavascript(markers, null);
                } catch (IOException markerError) {
                    android.util.Log.w("BraveFrontier", "Optional unit markers unavailable", markerError);
                }
                // v103 QoL: read-only per-unit live HP/BB and critical detail panel.
                try {
                    String battleDetails = readPackagedText("bf10300_qol_battle_details.js");
                    view.evaluateJavascript(battleDetails, null);
                } catch (IOException detailsError) {
                    android.util.Log.w("BraveFrontier", "Optional battle details unavailable", detailsError);
                }
            }
            // External navigation isn't needed for the bundled offline game.
            @Override public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return !url.startsWith("file:///android_asset/");
            }
        });
        game.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView web, ValueCallback<Uri[]> callback,
                    FileChooserParams params) {
                if (pendingUpload != null) pendingUpload.onReceiveValue(null);
                pendingUpload = callback;
                try { startActivityForResult(params.createIntent(), PICK_BACKGROUND); return true; }
                catch (ActivityNotFoundException ex) { pendingUpload = null; return false; }
            }
        });
        WebSettings settings = game.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);  // local packaged android_asset page
        settings.setAllowContentAccess(true);  // user-selected images and JSON documents
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        game.addJavascriptInterface(new SaveBridge(), "BFAndroid");
        game.loadUrl("file:///android_asset/index.html");
        gameContainer.addView(game, new FrameLayout.LayoutParams(-1, -1));
        setContentView(gameContainer);
        if (state != null) saveToWrite = state.getString("pending_save_to_write");
    }
    @Override protected void onSaveInstanceState(Bundle out) {
        if (saveToWrite != null) out.putString("pending_save_to_write", saveToWrite);
        super.onSaveInstanceState(out);
    }
    @Override public void onConfigurationChanged(Configuration cfg) {
        super.onConfigurationChanged(cfg);
        if (gameContainer != null) gameContainer.requestApplyInsets();
    }
    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == PICK_BACKGROUND) {
            if (pendingUpload != null) {
                pendingUpload.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
                pendingUpload = null;
            }
            return;
        }
        if (requestCode == PICK_SAVE_FILE) {
            if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                try (InputStream in = getContentResolver().openInputStream(data.getData());
                     ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                    if (in == null) throw new IOException("The selected file is not readable.");
                    byte[] buf = new byte[8192];int count;
                    while ((count = in.read(buf)) != -1) {
                        if (out.size() + count > MAX_SAVE_BYTES) throw new IOException("File exceeds 1 MB.");
                        out.write(buf, 0, count);
                    }
                    String base64 = Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP);
                    toGame("receiveSaveBase64", base64);
                } catch (Exception ex) { toGame("error", "Could not read save file: " + ex.getMessage()); }
            } else toGame("error", "Save import cancelled.");
            return;
        }
        if (requestCode == CREATE_SAVE_FILE) {
            String payload = saveToWrite;saveToWrite = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null && payload != null) {
                try (OutputStream out = getContentResolver().openOutputStream(data.getData(), "wt")) {
                    if (out == null) throw new IOException("Destination is not writable.");
                    out.write(payload.getBytes(StandardCharsets.UTF_8));out.flush();
                    toGame("exportResult", "true", "You can import the .json in a browser or another APK.");
                } catch (Exception ex) { toGame("exportResult", "false", ex.getMessage()); }
            } else toGame("exportResult", "false", "File picker cancelled.");
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
    @Override public void onBackPressed() {
        if (game != null && game.canGoBack()) game.goBack();
        else super.onBackPressed();
    }
    @Override protected void onPause() {
        if (game != null) game.onPause();
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        if (game != null) game.onResume();
    }
    @Override protected void onDestroy() {
        if (game != null) {game.removeJavascriptInterface("BFAndroid");game.destroy();game = null;}
        super.onDestroy();
    }
}
