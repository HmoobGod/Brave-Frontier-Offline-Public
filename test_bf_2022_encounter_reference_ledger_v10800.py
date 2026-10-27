"""v108: original 2022 opaque encounter mission evidence joins and live read-only audit."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
mistral=json.loads((R/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf8'))
morgan=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text('utf8'))
js=(A/'bf10800_2022_encounter_reference_ledger.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert mistral['schema']=='bf-global-2022-mistral-raw-mission-evidence-v056'
assert morgan['schema']=='bf-global-morgan-2022-original-quests-v080'
assert mistral['source']['fileSha256']==morgan['provenance']['missionMasterSha256']
assert len(mistral['rows'])==34 and len(morgan['quests'])==36
assert js.count('BF_GLOBAL_2022_ENCOUNTER_REFERENCE_LEDGER_V10800')==1
assert len(js.encode())<65536
assert 'nativeWaveIdentitiesKnown:false' in js
assert 'nativeEnemyIdsKnown:false' in js
assert 'meaningDecoded:false' in js
assert not any(x in js for x in ('saveProgress(', 'localStorage',
       'P.squad=', 'P.roster=', 'S.party=', 'S.enemies=', 'awardDemoRewards(',
       'Math.random', 'fetch(', 'XMLHttpRequest', 'performUnit='))
assert java.index('readPackagedText("bf10700_source_landed_crystal_eligibility.js")')<java.index('readPackagedText("bf10800_2022_encounter_reference_ledger.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda x:errors.append(str(x)))
 p.set_content('<html><body><div id="bf110-journal"></div></body></html>')
 source={'mistral':mistral,'morgan':morgan}
 p.evaluate("""src=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:2}};
   window.S={mode:'archive',party:[],enemies:[]};
   window.__saved108=JSON.stringify(P);
   const ids=src.mistral.rows.map(r=>r.missionId);
   const rows=new Map(src.mistral.rows.map(r=>[r.missionId,r]));
   window.BFOriginalMissionEvidence={
    count:34,missionIds:ids,
    facts:{sourceSha256:src.mistral.source.fileSha256},
    lookup:id=>rows.get(id)||null,
    parseOpaqueReferences:raw=>raw.split(',').map(t=>{
      const parts=t.split(':');return {opaqueLabel:parts[0],opaqueRef:parts[1]};
    })
   };
   window.BF_MORGAN_QUEST_DATA_V080=src.morgan;
 }""",source)
 p.add_script_tag(path=str(A/'bf10800_2022_encounter_reference_ledger.js'))
 api='BFGlobalEncounterReferencesV10800'
 assert p.evaluate('Boolean(window.'+api+')') is True
 assert p.evaluate(api+'.summary.archivedMissions')==70
 assert p.evaluate(api+'.summary.mistralMissions')==34
 assert p.evaluate(api+'.summary.morganMissions')==36
 assert p.evaluate(api+'.summary.distinctOpaqueRefs')==31
 assert p.evaluate(api+'.summary.meaningDecoded') is False
 assert p.evaluate(api+'.summary.gameplayMutation') is False
 assert p.evaluate(api+'.lookup(100)') is None
 assert p.evaluate(api+'.lookup("1")') is None
 assert p.evaluate(api+'.lookup(1).raw')=='3:10100,1:10101,0:10102'
 assert p.evaluate(api+'.lookup(200).raw')=='3:20100,0:20101'
 assert p.evaluate(api+'.lookup(265).raw')=='1:20700,0:20701'
 assert p.evaluate(api+'.lookup(200).nativeEnemyIdsKnown') is False
 assert p.evaluate(api+'.lookup(200).nativeWaveIdentitiesKnown') is False
 assert p.evaluate(api+'.parseOpaque("3:10100,1:10101").length')==2
 assert p.evaluate(api+'.parseOpaque("3:0")') is None
 assert p.evaluate(api+'.parseOpaque("3:abc")') is None
 assert p.evaluate(api+'.parseOpaque("1:12345678901234567890123456789")') is None
 assert p.evaluate(api+'.parseOpaque("__proto__:1")') is None
 assert p.evaluate(api+'.references("10100")')==[1,2,10,11,12]
 assert p.evaluate(api+'.references("invalid")')==[]
 assert p.locator('#bf10800-mission option').count()==70
 p.locator('#bf10800-encounter-ledger > summary').click()
 p.locator('#bf10800-mission').select_option('265')
 assert '1:20700,0:20701' in p.locator('#bf10800-raw').inner_text()
 assert p.evaluate('JSON.stringify(P)')==p.evaluate('window.__saved108')
 assert p.evaluate('S.mode')=='archive'
 p.add_script_tag(path=str(A/'bf10800_2022_encounter_reference_ledger.js'))
 assert p.locator('#bf10800-encounter-ledger').count()==1
 assert not errors,errors
 b.close()
print('PASS v108 all 70 original 2022 mission raw refs, 31 tokens, malformed reject, provenance, save isolation')
