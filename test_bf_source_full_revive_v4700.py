"""v47 original single-ally full revive and shared DEMO item turn safety."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf4700_source_full_revive.js').read_text('utf8')
assert src.count('/* BF_GLOBAL_SOURCE_FULL_REVIVE_ITEM_V4700 */')==1
assert len(src.encode('utf8'))<65536
assert all(x not in src for x in ('localStorage','saveProgress(', 'BFAndroid'))
ref=json.loads((R/'source_data/bf_global_2022_revive_item_evidence_v4700.json').read_text('utf8'))
assert ref['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
items={x['itemId']:x for x in ref['items']}
assert items[52400]['passiveSkillInfo']=='100'
assert (items[52400]['battleEffectGroupId'],items[52400]['itemTargetArea'])==(610,1)
assert items[22400]['passiveSkillInfo']=='1'
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf4600_source_bb_gauge_item.js")')<j.index('readPackagedText("bf4700_source_full_revive.js")')
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
 'bf4700_source_full_revive.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 s=p.evaluate('BFGlobalSourceFullReviveV4700.source')
 assert (s['itemId'],s['itemTargetArea'],s['battleEffectGroupId'])==(52400,1,610)
 assert (s['passiveSkillInfo'],s['itemMaxEquipped'])==('100',2)
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().remaining')==1
 # Full HP targets are NOT legal; KO actor cannot use an item.
 assert p.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(0,1)') is False
 p.evaluate('S.party[1].hp=0')
 assert p.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(1,1)') is False
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().available') is True
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 assert p.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(0,1)') is True
 assert p.evaluate('S.party[1].hp===S.party[1].maxHp') is True
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('S.party[1].action.kind')=='guard'
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().remaining')==0
 assert p.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(2,3)') is False
 p.evaluate('S.party[0].action=null')
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(0,2)') is False
 p.evaluate('S.party[1].action=null')
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(1,2)') is False
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.free(1)') is False
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.snapshot().remaining')==1
 p.evaluate("""()=>{
    S.party[0].action={kind:'attack',target:0};
    S.party[1].action={kind:'attack',target:0};
    BFGlobalItemTurnReservationsV4500.enforce();
    BFGlobalSourceFullReviveV4700.enforceRevivedGuards();
 }""")
 assert p.evaluate('S.party[0].action.kind==="guard"&&S.party[1].action.kind==="guard"') is True
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 assert before==after,(before,after)
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().revivedThisRound.length')==0
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().remaining')==0
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().available') is False
 assert p.locator('#bf4700-revive').is_hidden()
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalSourceFullReviveV4700.snapshot().remaining')==1
 p.add_script_tag(path=str(A/'bf4700_source_full_revive.js'))
 assert p.locator('#bf4700-revive').count()==1
 assert not errors,errors
 b.close()
print('PASS v47 original #52400 single KO full revive; DEMO turn/recipient Guard, stock, saved state')
