"""v109 strict 2022 master St. Lamia raw encounter refs extend original 70 to 106."""
from pathlib import Path
from zipfile import ZipFile
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
raw=json.loads((R/'source_data/bf_global_st_lamia_raw_encounter_refs_v109.json').read_text('utf8'))
with ZipFile(R/'source_assets/bf1/stlamia/StLamia_2022_Source_Dataset_v090.zip') as z:
 original=json.loads(z.read('source_data/bf_global_st_lamia_original_v090.json'))
mistral=json.loads((R/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf8'))
morgan=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text('utf8'))
assert raw['schema']=='bf-global-st-lamia-2022-raw-encounter-refs-v109'
sha='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert raw['provenance']['masterSha256']==sha
assert original['provenance']['missionMasterSha256']==sha
assert mistral['source']['fileSha256']==sha
assert morgan['provenance']['missionMasterSha256']==sha
assert len(raw['rows'])==36 and len(original['quests'])==36
assert [r['missionId'] for r in raw['rows']]==[q['missionId'] for q in original['quests']]
assert [r['missionId'] for r in raw['rows']]==list(range(300,305))+list(range(310,315))+list(range(320,325))+list(range(330,335))+list(range(340,345))+list(range(350,355))+list(range(360,366))
patterns=[(300,5,'3:30100,0:30101'),(310,5,'3:30200,1:30201'),
          (320,5,'3:30300,2:30301'),(330,5,'1:30400,0:30401'),
          (340,5,'3:30500,0:30501'),(350,5,'3:30600,0:30601'),
          (360,6,'3:30700')]
assert [x['rawEncounterRef'] for x in raw['rows']]==[pattern for start,num,pattern in patterns for _ in range(num)]
assert len(set(t.split(':')[1] for row in raw['rows'] for t in row['rawEncounterRef'].split(',')))==13
js=(A/'bf10900_stlamia_encounter_refs.js').read_text('utf8')
assert js.count('BF_GLOBAL_2022_STLAMIA_ENCOUNTER_REFERENCE_EXTENSION_V10900')==1
assert len(js.encode())<65536
assert all(x not in js for x in ('saveProgress(', 'localStorage', 'Math.random', 'awardDemoRewards(', 'S.enemies=', 'S.party=', 'P.roster=', 'fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10800_2022_encounter_reference_ledger.js")')<java.index('readPackagedText("bf10900_stlamia_encounter_refs.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><details id="bf10800-encounter-ledger"><summary>2022 GLOBAL ENCOUNTER REFS · 70 MISSION RECORDS</summary><p></p><select id="bf10800-mission"></select><p id="bf10800-raw"></p></details></body></html>')
 p.evaluate("""src=>{
    window.P={version:7,roster:[10011],squad:[10011],questClears:{1:1}};
    window.S={mode:'archive',enemies:[]};
    window.__start109=JSON.stringify(P);
    const prior=[...src.mistral.rows,...src.morgan.quests].map(x=>({
      missionId:x.missionId,raw:x.rawEncounterRef,
      refs:x.rawEncounterRef.split(',').map(v=>({opaqueLabel:v.split(':')[0],opaqueRef:v.split(':')[1]}))
    }));
    const map=new Map(prior.map(x=>[x.missionId,x]));
    const sel=document.querySelector('#bf10800-mission');
    for(const row of prior){const o=document.createElement('option');
       o.value=String(row.missionId);o.textContent='Mission '+row.missionId;sel.append(o);}
    window.BFGlobalEncounterReferencesV10800={
      summary:{archivedMissions:70,sha256:src.mistral.source.fileSha256},
      lookup:id=>map.get(id)||null,
      references:token=>prior.filter(x=>x.refs.some(v=>v.opaqueRef===token))
         .map(x=>x.missionId),
      parseOpaque:raw=>raw.split(',').map(x=>({
         opaqueLabel:x.split(':')[0],opaqueRef:x.split(':')[1]}))
    };
    window.BF_STLAMIA_QUEST_DATA_V090=src.st;
 }""",{'mistral':mistral,'morgan':morgan,'st':original})
 p.add_script_tag(path=str(A/'bf10900_stlamia_encounter_refs.js'))
 api='BFGlobalEncounterReferencesV10900'
 assert p.evaluate('Boolean(window.'+api+')') is True
 assert p.evaluate(api+'.summary.archivedMissions')==106
 assert p.evaluate(api+'.summary.stLamiaMissions')==36
 assert p.evaluate(api+'.summary.stLamiaDistinctOpaqueRefs')==13
 assert p.evaluate(api+'.summary.meaningDecoded') is False
 assert p.evaluate(api+'.summary.gameplayMutation') is False
 assert p.locator('#bf10800-mission option').count()==106
 assert '106 MISSION RECORDS' in p.locator('#bf10800-encounter-ledger summary').inner_text()
 assert p.evaluate(api+'.lookup(1).raw')=='3:10100,1:10101,0:10102'
 assert p.evaluate(api+'.lookup(265).raw')=='1:20700,0:20701'
 assert p.evaluate(api+'.lookup(300).raw')=='3:30100,0:30101'
 assert p.evaluate(api+'.lookup(365).raw')=='3:30700'
 assert p.evaluate(api+'.lookup(365).nativeEnemyIdsKnown') is False
 assert p.evaluate(api+'.lookup(365).nativeWaveIdentitiesKnown') is False
 assert p.evaluate(api+'.references("30100")')==[300,301,302,303,304]
 assert p.evaluate(api+'.references("10100")')==[1,2,10,11,12]
 assert p.evaluate(api+'.lookup(399)') is None
 p.locator('#bf10800-mission').select_option('365')
 assert '3:30700' in p.locator('#bf10800-raw').inner_text()
 assert p.evaluate('JSON.stringify(P)')==p.evaluate('window.__start109')
 p.add_script_tag(path=str(A/'bf10900_stlamia_encounter_refs.js'))
 assert p.locator('#bf10800-mission option').count()==106
 assert not errors,errors
 b.close()
print('PASS v109 original source St. Lamia 36 refs, 106-total integration, exact mission archive provenance and no save writes')
