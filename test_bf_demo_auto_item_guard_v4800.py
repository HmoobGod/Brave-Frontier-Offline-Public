"""v48 ensure automatic battle cannot overwrite already paid DEMO item actions."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf4800_demo_auto_item_guard.js').read_text('utf8')
assert src.count('/* BF_GLOBAL_DEMO_AUTO_ITEM_GUARD_V4800 */')==1
assert len(src.encode('utf8'))<65536
assert all(x not in src for x in ('localStorage','saveProgress(', 'BFAndroid'))
ref=json.loads((R/'source_data/bf_global_2022_revive_item_evidence_v4700.json').read_text('utf8'))
assert ref['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
items={x['itemId']:x for x in ref['items']}
assert items[52400]['passiveSkillInfo']=='100'
assert (items[52400]['battleEffectGroupId'],items[52400]['itemTargetArea'])==(610,1)
assert items[22400]['passiveSkillInfo']=='1'
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf4700_source_full_revive.js")')<j.index('readPackagedText("bf4800_demo_auto_item_guard.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
 'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
 'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
 'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
 'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
 'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js',
 'bf3000_battle_results.js','bf3100_battle_focus.js','bf3200_combat_journal.js',
 'bf3300_story_playback.js','bf3400_source_scene_placement.js',
 'bf3500_dialogue_timeline.js','bf3600_event_composite.js',
 'bf3700_cinematic_reader.js','bf3800_source_battle_backdrop.js',
 'bf3900_story_battle_handoff.js','bf4000_next_chapter_intro.js',
 'bf4100_live_quest_banner.js','bf4500_item_turn_reservations.js',
 'bf4200_demo_potion_command.js','bf4300_source_party_heal.js',
 'bf4400_source_atk_item.js','bf4600_source_bb_gauge_item.js',
 'bf4700_source_full_revive.js','bf4800_demo_auto_item_guard.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('BFGlobalDemoAutoItemGuardV4800.snapshot().pending') is False
 # Unreserved Auto mode must remain functional; suppress its scheduled turn.
 p.evaluate('S.busy=true')
 p.locator('#auto').click()
 assert p.evaluate('S.auto') is True
 assert p.locator('#auto').is_checked()
 p.locator('#auto').click()
 assert p.evaluate('S.auto') is False
 p.evaluate('S.busy=false')
 p.evaluate('S.party[1].hp=0')
 before=p.evaluate("""()=>({
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
   wave:S.wave,round:S.round
 })""")
 assert p.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(0,1)') is True
 assert p.evaluate('S.party[1].hp===S.party[1].maxHp') is True
 assert p.evaluate('BFGlobalDemoAutoItemGuardV4800.snapshot().pending') is True
 # The user cannot turn Auto on and thereby overwrite consumed Guard commands.
 p.locator('#auto').click()
 assert p.locator('#auto').is_checked() is False
 assert p.evaluate('S.auto') is False
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('S.party[1].action.kind')=='guard'
 p.evaluate("""()=>{
   S.party[0].action={kind:'attack',target:0};
   S.party[1].action={kind:'attack',target:0};
   BFGlobalItemTurnReservationsV4500.enforce();
   BFGlobalSourceFullReviveV4700.enforceRevivedGuards();
 }""")
 assert p.evaluate('S.party[0].action.kind==="guard"&&S.party[1].action.kind==="guard"') is True
 after=p.evaluate("""()=>({
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
   wave:S.wave,round:S.round
 })""")
 assert before==after,(before,after)
 # The ledger must be released when the simulated round advances.
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalDemoAutoItemGuardV4800.snapshot().pending') is False
 p.evaluate('S.busy=true')
 p.locator('#auto').click()
 assert p.locator('#auto').is_checked()
 assert p.evaluate('S.auto') is True
 p.locator('#auto').click()
 p.evaluate('S.busy=false')
 assert p.evaluate('S.auto') is False
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalDemoAutoItemGuardV4800.snapshot().pending') is False
 p.add_script_tag(path=str(A/'bf4800_demo_auto_item_guard.js'))
 assert p.evaluate('BFGlobalDemoAutoItemGuardV4800.snapshot().reservations')==0
 assert not errors,errors
 b.close()
print('PASS v48: Auto cannot steal reserved DEMO item/KO Guard; normal Auto works, saves untouched')
