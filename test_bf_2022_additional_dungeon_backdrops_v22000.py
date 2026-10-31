"""v220: full 106 original 2022 story backgrounds, opt-in and save inert."""
from pathlib import Path
import hashlib, json, shutil
from playwright.sync_api import sync_playwright
import prepare_bf_original_2022_dungeon_backdrops_v22000 as v220

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
cat, old, new = v220.verified_catalog()
assert len(old)==29 and len(new)==77
assert cat['distinctOriginalJpgCount']==22 and len(cat['imageSources'])==22
assert cat['previouslyPackagedOriginalJpgCount']==7
assert cat['additionalSourceJpgCount']==15
assert {mid for mid,_ in old}.isdisjoint({mid for mid,_ in new})
assert len({mid for mid,_ in old+new})==106
for rec in cat['imageSources']:
 path=A/'content/dungeon'/rec['file']
 assert path.is_file(), rec['file']
 data=path.read_bytes()
 assert len(data)==rec['sizeBytes'] and hashlib.sha256(data).hexdigest()==rec['sha256'], rec['file']
js=(A/'bf22000_original_2022_additional_dungeon_backdrops.js').read_text('utf8')
v38=(A/'bf3800_source_battle_backdrop.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'BF_GLOBAL_2022_ADDITIONAL_MISSION_BACKDROPS_V22000' in js
assert 'BFGlobalOriginalDungeonBackdropsV19100?.lookup?.(q.missionId)' in v38
assert 'BFGlobalOriginalDungeonBackdropsV22000?.lookup?.(q.missionId)' in v38
assert java.index('readPackagedText("bf19100_original_2022_dungeon_backdrops.js")') < java.index('readPackagedText("bf22000_original_2022_additional_dungeon_backdrops.js")')
for content in (js,v38):
 assert 'saveProgress(' not in content and 'localStorage' not in content
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};window.__v220Writes=[];
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v);__v220Writes.push(k)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
 'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
 'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
 'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
 'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
 'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js',
 'bf3000_battle_results.js','bf3100_battle_focus.js',
 'bf3200_combat_journal.js','bf3300_story_playback.js',
 'bf3400_source_scene_placement.js','bf3500_dialogue_timeline.js',
 'bf3600_event_composite.js','bf3700_cinematic_reader.js',
 'bf3800_source_battle_backdrop.js'):
  page.add_script_tag(path=str(A/name))
 all_missions=dict(old+new)
 refdict={str(mid):{'missionId':mid,'playable':True,'sourceIsOriginal2022':True,
  'originalDungeonBattleBackground':image,'enemyWavesDecoded':False,
  'enemyAIDecoded':False,'enemyIdsDecoded':False} for mid,image in all_missions.items()}
 page.evaluate("""data=>{window.BFGlobalEncounterCrossrefsV17400=Object.freeze({
    source:Object.freeze({year:2022,
     crossTableRowsSha256:'2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284',
     nativeWavesDecoded:false,nativeEnemyIdsDecoded:false}),
    lookup(id){return data[String(id)]||null}
  });}""",refdict)
 page.add_script_tag(path=str(A/'bf19100_original_2022_dungeon_backdrops.js'))
 page.add_script_tag(path=str(A/'bf22000_original_2022_additional_dungeon_backdrops.js'))
 assert page.evaluate('BFGlobalOriginalDungeonBackdropsV19100.source.missionCount')==29
 assert page.evaluate('BFGlobalOriginalDungeonBackdropsV22000.source.missionCount')==77
 assert not page.locator('#bf3800-toggle').is_checked()
 page.evaluate("""()=>{document.getElementById('mode').value='archive';window.questUnlocked=()=>true;}""")
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),writes:JSON.stringify(__v220Writes),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 for mid,image in old+new:
  rec=page.evaluate("""id=>{QUEST=QUESTS.find(q=>q.missionId===id);
   return BFGlobalBattleBackdropV3800.refresh();}""",mid)
  assert rec['available'] is True and rec['background']==image and rec['applied'] is False,(mid,rec)
 for id,image in new:
  assert page.evaluate(f'BFGlobalOriginalDungeonBackdropsV19100.lookup({id})') is None
  assert page.evaluate(f'BFGlobalOriginalDungeonBackdropsV22000.lookup({id}).image')==image
 for id,image in old:
  assert page.evaluate(f'BFGlobalOriginalDungeonBackdropsV19100.lookup({id}).image')==image
  assert page.evaluate(f'BFGlobalOriginalDungeonBackdropsV22000.lookup({id})') is None
 assert page.evaluate('BFGlobalOriginalDungeonBackdropsV22000.lookup(400)') is None
 page.evaluate('QUEST=QUESTS.find(q=>q.missionId===200)')
 assert page.evaluate('BFGlobalBattleBackdropV3800.setEnabled(true)') is True
 state=page.evaluate('BFGlobalBattleBackdropV3800.refresh()')
 assert state['background']=='dungeon_battle_20100.jpg' and state['applied'] is True
 assert page.evaluate('BFGlobalBattleBackdropV3800.setEnabled(false)') is True
 page.evaluate("document.getElementById('mode').value='training'")
 assert page.evaluate('BFGlobalBattleBackdropV3800.refresh().available') is False
 page.evaluate("document.getElementById('mode').value='archive'")
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),writes:JSON.stringify(__v220Writes),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print('PASS v220: original 2022 battle JPGs for all 106 live quests, 29 legacy/77 new, opt-in default off, no P/S/save mutation')
