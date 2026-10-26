"""v45 original-item DEMO command cross-type actor turn exclusivity regression."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
js=(A/'bf4500_item_turn_reservations.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_ITEM_TURN_RESERVATIONS_V4500 */')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
ordered=['bf4100_live_quest_banner.js','bf4500_item_turn_reservations.js',
         'bf4200_demo_potion_command.js','bf4300_source_party_heal.js',
         'bf4400_source_atk_item.js']
assert all(java.index('readPackagedText("'+a+'")') <
           java.index('readPackagedText("'+b+'")') for a,b in zip(ordered,ordered[1:]))
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
 'bf4400_source_atk_item.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations.length')==0
 assert p.evaluate('BFGlobalSourcePartyHealV4300.source.itemTargetArea')==2
 assert p.evaluate('BFGlobalSourceAtkItemV4400.source.atkPercent')==30
 p.evaluate("""()=>{for(let i of [0,1,2])
    S.party[i].hp=Math.max(1,S.party[i].hp-900);}""")
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
   wave:S.wave,round:S.round})""")
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is True
 p.evaluate('S.party[0].action=null')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(0)') is False
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(0,3)') is False
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==1
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(1)') is True
 p.evaluate('S.party[1].action=null')
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(1)') is False
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,3)') is False
 assert p.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(2,3)') is True
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations.length')==3
 assert p.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining')==0
 assert p.evaluate('currentAtkBoost(S.party[3])')==30
 p.evaluate("""()=>{for(let i of [0,1,2])
    S.party[i].action={kind:'attack',target:0};
    BFGlobalItemTurnReservationsV4500.enforce();}""")
 assert p.evaluate('S.party.slice(0,3).every(x=>x.action.kind==="guard")') is True
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
   progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
   wave:S.wave,round:S.round})""")
 assert before==after,(before,after)
 p.evaluate("""()=>{
    S.round++;
    for(const unit of S.party) unit.action=null;
    S.party[0].hp=Math.max(1,S.party[0].hp-100);
 }""")
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.free(0)') is True
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is True
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().available') is False
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations.length')==0
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalDemoPotionV4200.snapshot().remaining')==3
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations.length')==0
 p.add_script_tag(path=str(A/'bf4500_item_turn_reservations.js'))
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations.length')==0
 assert not errors,errors
 b.close()
print('PASS v45: shared DEMO item action reservation, guarded rounds, save unchanged')
