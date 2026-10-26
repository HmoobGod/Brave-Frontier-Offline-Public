"""v42.00 optional live battle demo Potion consumes Guard action and never touches save."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf4200_demo_potion_command.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_DEMO_POTION_COMMAND_V4200 */')==1
assert len(src.encode('utf8'))<65536
assert all(word not in src for word in ('localStorage','saveProgress(', 'BFAndroid','P.questClears='))
assert java.index('readPackagedText("bf4100_live_quest_banner.js")')<java.index('readPackagedText("bf4200_demo_potion_command.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
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
 'bf4100_live_quest_banner.js','bf4200_demo_potion_command.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate("P.version")==7
 assert page.evaluate("BFGlobalDemoPotionV4200.snapshot().remaining")==3
 assert page.locator('#bf4200-items').is_visible()
 assert page.locator('#bf4200-use').is_disabled()
 page.evaluate("""()=>{S.party[0].hp=Math.max(1,S.party[0].hp-750);
                       S.party[1].hp=Math.max(1,S.party[1].hp-900);
                       S.party[2].hp=Math.max(1,S.party[2].hp-900);}""")
 before=page.evaluate("""()=>({progress:JSON.stringify(P),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   clears:JSON.stringify(P.questClears),wave:S.wave,round:S.round})""")
 before_hp=page.evaluate("S.party[0].hp")
 page.evaluate('BFGlobalDemoPotionV4200.refresh()')
 assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is True
 assert page.evaluate('S.party[0].hp')==before_hp+min(500,750)
 assert page.evaluate('S.party[0].action.kind')=='guard'
 assert page.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==2
 assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is False
 # Guard remains locked if the player changes to Attack after healing.
 page.evaluate("S.party[0].action={kind:'attack',target:0}")
 page.evaluate("BFGlobalDemoPotionV4200.enforceGuards()")
 assert page.evaluate('S.party[0].action.kind')=='guard'
 assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(1)') is True
 assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(2)') is True
 assert page.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==0
 assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(3)') is False
 after=page.evaluate("""()=>({progress:JSON.stringify(P),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   clears:JSON.stringify(P.questClears),wave:S.wave,round:S.round})""")
 assert before==after,(before,after)
 page.locator('#mode').select_option('training')
 assert page.evaluate('BFGlobalDemoPotionV4200.snapshot().available') is False
 assert page.locator('#bf4200-items').is_hidden()
 page.locator('#mode').select_option('archive')
 assert page.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 assert page.evaluate('BFGlobalDemoPotionV4200.snapshot().eligible')==[]
 assert not errors,errors
 browser.close()
print('PASS v42.00: demo Potion +500 HP, Guard action, 3-stock cap, reset and save isolation')