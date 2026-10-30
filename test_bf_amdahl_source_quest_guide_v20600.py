"""v206: source-exact Amdahl 36-story-quest guide and private-save isolation.

No new battles, quest unlocks, native wave claims, energy use, or save changes.
"""
from pathlib import Path
import json,re,shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
APP=ROOT/'app/src/main/assets'
SOURCE=json.loads((ROOT/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
E=json.loads((ROOT/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
JS=(APP/'bf20600_amdahl_source_quest_guide.js').read_text('utf8')
JAVA=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert SOURCE['schema']=='bf-global-2022-amdahl-quest-readiness-v147'
assert SOURCE['provenance']['missionTableSha256']==E['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert SOURCE['provenance']['questCanonSha256']=='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3'
assert SOURCE['area']['playableNow'] is False and SOURCE['area']['originalEnemyWavesDecoded'] is False
assert len(SOURCE['quests'])==36 and len(SOURCE['dungeons'])==7
assert JS.count('BF_AMDAHL_ORIGINAL_2022_STORY_GUIDE_V20600')==1
assert len(JS.encode('utf8'))<65536
for token in ('localStorage.', 'saveProgress(', 'awardDemoRewards(', 'Math.random(',
              'P.questClears=', 'P.roster=', 'QUESTS.push(', 'startQuest(',
              'fetch(', 'XMLHttpRequest(', 'BFAndroid'):
 assert token not in JS,token
match=re.search(r'const rows=(\[.*?\]);\n const ids=',JS,re.S)
assert match
sourceRows=[[q[k] for k in ('id','dungeonId','prerequisiteMissionId','waveCount',
                             'energy','exp','zel','karma','name','description')]
            for q in SOURCE['quests']]
assert json.loads(match.group(1))==sourceRows
assert JAVA.count('readPackagedText("bf20600_amdahl_source_quest_guide.js")')==1
assert JAVA.index('readPackagedText("bf14900_original_amdahl_art.js")')<JAVA.index('readPackagedText("bf15100_amdahl_encounter_evidence.js")')<JAVA.index('readPackagedText("bf20600_amdahl_source_quest_guide.js")')
assert E['total']==106

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
 page.set_content('<!doctype html><html><body><details id="bf14900-amdahl-art">'
  '<summary>Original Amdahl art</summary><div id="bf14900-selected"></div>'
  +''.join('<button type="button" data-bf14900-dungeon="'+str(q['id'])+'"></button>'
     for q in SOURCE['dungeons'])+'</details></body></html>')
 page.evaluate("""data=>{
  let writes=0;const store={'bf_global_offline_demo_v7':'owner-v7-save-untouched'};
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>store[k]??null,setItem:(k,v)=>{writes++;store[k]=String(v)},
   removeItem:k=>{writes++;delete store[k]},
   key:i=>Object.keys(store)[i]??null,get length(){return Object.keys(store).length}}});
  window.__saveWrites=()=>writes;
  window.P={version:7,squad:[10011],roster:[10011],questClears:{365:1},zel:1350,karma:300};
  window.S={busy:false,party:[{unitId:10011}],enemies:[]};
  window.QUESTS=data.playable.map(r=>({missionId:r[0]}));
  const ds=data.dungeons.map(d=>({id:d.id,name:d.name,firstMissionId:d.id}));
  window.BFAmdahlOriginalArtV14900={
   entries:ds,source:{originalGameplayEnabled:false,decodedEnemyWaves:false},
   lookup:id=>ds.find(d=>d.id===id)||null,
   preview:id=>(window.__lastArtPreview=id,true)
  };
  const list=data.rows.map(r=>({
   missionId:r[0],dungeonId:r[1],requires:r[2],originalSourceWaveCount:r[3],
   name:r[8],playable:false
  }));
  window.BFGlobalEncounterReferencesV15100={
   summary:{amdahlSourceOnlyMissions:36,playableMissions:106,meaningDecoded:false},
   lookup:id=>list.find(r=>r.missionId===id)||null
  };
  window.__initial=JSON.stringify({player:P,battle:S,quests:QUESTS});
 }""",{'playable':E['records'],'rows':sourceRows,'dungeons':SOURCE['dungeons']})
 before=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
    quests:JSON.stringify(QUESTS),save:localStorage.getItem('bf_global_offline_demo_v7'),
    writes:__saveWrites()})""")
 page.add_script_tag(path=str(APP/'bf20600_amdahl_source_quest_guide.js'))
 assert page.locator('#bf20600-amdahl-guide').count()==1
 assert page.locator('#bf20600-dungeon option').count()==7
 assert page.locator('#bf20600-quest-list li').count()==5
 assert 'The Scars of War' in page.locator('#bf20600-quest-list').inner_text()
 assert 'NOT PLAYABLE' in page.locator('#bf20600-quest-list').inner_text()
 assert '1800 EXP' in page.locator('#bf20600-quest-list').inner_text()
 assert page.evaluate('BFAmdahlSourceQuestGuideV20600.lookup(400)')[8]=='The Scars of War'
 assert page.evaluate('BFAmdahlSourceQuestGuideV20600.lookup(99999)') is None
 assert page.evaluate('BFAmdahlSourceQuestGuideV20600.source.playable') is False
 assert page.evaluate('BFAmdahlSourceQuestGuideV20600.source.saveMutation') is False
 page.locator('#bf20600-dungeon').select_option('460')
 assert page.locator('#bf20600-quest-list li').count()==6
 assert 'Malevolent Ceremony' in page.locator('#bf20600-quest-list').inner_text()
 assert page.evaluate('__lastArtPreview')==460
 page.locator('#bf14900-amdahl-art [data-bf14900-dungeon="420"]').click()
 assert page.locator('#bf20600-dungeon').input_value()=='420'
 assert page.locator('#bf20600-quest-list li').count()==5
 page.add_script_tag(path=str(APP/'bf20600_amdahl_source_quest_guide.js'))
 assert page.locator('#bf20600-amdahl-guide').count()==1
 after=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
    quests:JSON.stringify(QUESTS),save:localStorage.getItem('bf_global_offline_demo_v7'),
    writes:__saveWrites()})""")
 assert before==after,(before,after)
 page.evaluate('delete window.BFAmdahlSourceQuestGuideV20600;P.version=8')
 page.add_script_tag(path=str(APP/'bf20600_amdahl_source_quest_guide.js'))
 assert page.evaluate('Boolean(BFAmdahlSourceQuestGuideV20600)') is False
 assert page.locator('#bf20600-amdahl-guide').count()==1
 assert not errors,errors
 browser.close()
print('PASS v206: exact 36 2022 Amdahl original story guide, 7 dungeons, no quest/save changes')
