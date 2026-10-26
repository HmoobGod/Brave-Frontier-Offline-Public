"""v75 2022 #20101 heals all living injured allies +1000 without inventory saves."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
data=json.loads((R/'source_data/bf_global_2022_saint_light_v7500.json').read_text('utf8'))
assert data['provenance']['fileSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
item=data['item']
assert (item['itemId'],item['itemTargetArea'],item['passiveSkillInfo'])==(20101,2,'1000,1000,0,0')
src=(A/'bf7500_original_saint_light.js').read_text('utf8')
assert len(src.encode('utf8'))<65536
assert all(s not in src for s in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf4300_source_party_heal.js")')<java.index('readPackagedText("bf7500_original_saint_light.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
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
 'bf4200_demo_potion_command.js','bf4300_source_party_heal.js'):
  p.add_script_tag(path=str(A/name))
 p.add_script_tag(path=str(A/'bf7500_original_saint_light.js'))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.source.itemId')==20101
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.snapshot().remaining')==1
 assert p.locator('#bf7500-use').is_disabled()
 p.evaluate("""()=>{S.party[0].hp=Math.max(1,S.party[0].maxHp-200);
 S.party[1].hp=Math.max(1,S.party[1].maxHp-1600);
 S.party[2].hp=0;S.party[4].hp=Math.max(1,S.party[4].maxHp-1300);}""")
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 h=p.evaluate('S.party.map(x=>x.hp)')
 maximum=p.evaluate('S.party.map(x=>x.maxHp)')
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.snapshot().recipientCount')>=3
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.useSaintLight(2)') is False
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.snapshot().remaining')==1
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.useSaintLight(3)') is True
 for i in [0,1,4]:
  assert p.evaluate(f'S.party[{i}].hp')==min(maximum[i],h[i]+1000)
 assert p.evaluate('S.party[2].hp')==0
 assert p.evaluate('S.party[3].action.kind')=='guard'
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.snapshot().remaining')==0
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.useSaintLight(5)') is False
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 p.evaluate('S.party[3].action=null')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(3)') is False
 # Older party heal still works after source Saint Light; wound one ally again.
 p.evaluate('S.party[1].hp=Math.max(1,S.party[1].hp-250)')
 assert p.evaluate('BFGlobalSourcePartyHealV4300.usePartyHeal(1)') is True
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==0
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.useSaintLight(5)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalSaintLightV7500.snapshot().remaining')==1
 assert p.evaluate('BFGlobalSourcePartyHealV4300.snapshot().remaining')==1
 p.evaluate('S.party[1].hp=Math.max(1,S.party[1].maxHp-1200)')
 p.evaluate('BFGlobalOriginalSaintLightV7500.refresh()')
 p.locator('#bf7500-saint-light summary').click()
 p.locator('#bf7500-actor').select_option('0')
 h=p.evaluate('S.party[1].hp')
 p.locator('#bf7500-use').click()
 assert p.evaluate('S.party[1].hp')-h==min(1000,p.evaluate('S.party[1].maxHp')-h)
 assert not errors,errors
 b.close()
print('PASS v75 original Saint Light 1000 all-ally base heal, KO excluded, separate Guard, v43 preservation, save')
