"""v43.00 original 2022 party-heal scope, explicitly simulated values and save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf4300_source_party_heal.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_SOURCE_PARTY_HEAL_V4300 */')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf4200_demo_potion_command.js")')<java.index('readPackagedText("bf4300_source_party_heal.js")')
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
 'bf4300_source_party_heal.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.itemId')==20100
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.itemTargetArea')==2
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.itemMaxEquipped')==3
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.passiveSkillInfo')=='500,500,0,0'
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.archivedBaseHeal')==500
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 p.evaluate("""()=>{
   S.party[0].hp=Math.max(1,S.party[0].hp-400);
   S.party[1].hp=Math.max(1,S.party[1].hp-500);
   S.party[2].hp=0;
 }""")
 p.evaluate('BFGlobalSourcePartyHealV4300.refresh()')
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 h0=p.evaluate('S.party[0].hp');h1=p.evaluate('S.party[1].hp')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(3)') is True
 assert p.evaluate('S.party[0].hp')==h0+400
 assert p.evaluate('S.party[1].hp')==h1+500
 assert p.evaluate('S.party[2].hp')==0
 assert p.evaluate('S.party[3].action.kind')=='guard'
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==0
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(4)') is False
 p.evaluate("S.party[3].action={kind:'attack',target:0}")
 p.evaluate('BFGlobalSourcePartyHealV4300.enforceGuards()')
 assert p.evaluate('S.party[3].action.kind')=='guard'
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().available') is False
 assert p.locator('#bf4300-party').is_hidden()
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 assert not errors,errors
 b.close()
print('PASS v43.00: 2022 item #20100 party target; DEMO party healing, KO safe, Guard cost, save isolation')