"""v44.00 2022 original +30% ATK / 3-turn item metadata with isolated DEMO use."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf4400_source_atk_item.js').read_text('utf8')
assert script.count('/* BF_GLOBAL_SOURCE_ATK_ITEM_V4400 */')==1
assert len(script.encode('utf8'))<65536
assert all(x not in script for x in ('localStorage','saveProgress(', 'BFAndroid'))
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf4300_source_party_heal.js")')<j.index('readPackagedText("bf4400_source_atk_item.js")')
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
 'bf4100_live_quest_banner.js','bf4200_demo_potion_command.js',
 'bf4300_source_party_heal.js','bf4400_source_atk_item.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 src=p.evaluate('BFGlobalSourceAtkItemV4400.source')
 assert (src['itemId'],src['atkPercent'],src['durationTurns'])==(20400,30,3)
 assert (src['itemTargetArea'],src['effectGroupId'])==(1,400)
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==1
 initial=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),wave:S.wave})""")
 # Existing active boosts must not be overwritten without known stacking rules.
 p.evaluate("S.party[1].atkBuff={pct:40,untilRound:S.round+1}")
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(0,1)') is False
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==1
 p.evaluate("S.party[1].atkBuff=null")
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(0,1)') is True
 assert p.evaluate('currentAtkBoost(S.party[1])')==30
 assert p.evaluate('S.party[1].atkBuff.untilRound===S.round+2') is True
 assert p.evaluate('S.party[0].action.kind')=='guard'
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==0
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(2,3)') is False
 p.evaluate("S.party[0].action={kind:'attack',target:0}")
 p.evaluate('BFGlobalSourceAtkItemV4400.enforceGuards()')
 assert p.evaluate('S.party[0].action.kind')=='guard'
 now=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),wave:S.wave})""")
 assert initial==now,(initial,now)
 p.evaluate("S.round++")
 assert p.evaluate('currentAtkBoost(S.party[1])')==30
 p.evaluate("S.round++")
 assert p.evaluate('currentAtkBoost(S.party[1])')==30
 p.evaluate("S.round++")
 assert p.evaluate('currentAtkBoost(S.party[1])')==0
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().available') is False
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==1
 assert not errors,errors
 b.close()
print('PASS v44.00 original #20400 +30% ATK / 3 turns in DEMO, no overwrite/save mutation')