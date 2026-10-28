"""v151: original 2022 Amdahl source-only encounter tokens extend the verified 106 to 142.

Checks exact owner-source provenance, seven unchanged opaque patterns, fail-closed
UI extension, and the absence of gameplay or save mutation. No native wave AI claim.
"""
from pathlib import Path
import json,re,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
Q=json.loads((R/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
E=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
st=json.loads((R/'source_data/bf_global_st_lamia_raw_encounter_refs_v109.json').read_text('utf8'))
js=(A/'bf15100_amdahl_encounter_evidence.js').read_text('utf8')
master='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert Q['provenance']['missionTableSha256']==E['missionMasterSha256']==st['provenance']['masterSha256']==master
assert Q['provenance']['mstZipSha256']==E['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert Q['provenance']['questCanonSha256']=='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3'
assert Q['area']['originalEnemyWavesDecoded'] is False and Q['area']['playableNow'] is False
assert Q['area']['missionCount']==36 and Q['area']['dungeonCount']==7
assert E['total']==106 and len(E['records'])==106
assert js.count('BF_GLOBAL_2022_AMDAHL_ENCOUNTER_EVIDENCE_V15100')==1
assert len(js.encode('utf8'))<65536
assert not any(bad in js for bad in (
    'saveProgress(', 'localStorage.', 'awardDemoRewards(', 'Math.random(',
    'S.enemies=', 'S.party=', 'P.roster=', 'P.questClears=', 'fetch(',
    'XMLHttpRequest(', 'BFAndroid', 'startQuest('))
match=re.search(r'const sourceRows=(\[.*?\]);',js,re.S)
assert match,'missing pinned v151 rows'
actual=json.loads(match.group(1))
expected=[[q['id'],q['dungeonId'],q['prerequisiteMissionId'],q['waveCount'],q['rawEncounterRef'],q['name']] for q in Q['quests']]
assert actual==expected
patterns={d['id']:{q['rawEncounterRef'] for q in Q['quests'] if q['dungeonId']==d['id']} for d in Q['dungeons']}
assert len(patterns)==7 and all(len(values)==1 for values in patterns.values())
assert len({pair.split(':')[1] for q in Q['quests'] for pair in q['rawEncounterRef'].split(',')})==14
assert all(q['rawEncounterRef'].count(',')+1<=3 for q in Q['quests'])
assert {q['id'] for q in Q['quests']}.isdisjoint({r[0] for r in E['records']})
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10900_stlamia_encounter_refs.js")')<java.index('readPackagedText("bf15100_amdahl_encounter_evidence.js")')
assert java.index('readPackagedText("bf14900_original_amdahl_art.js")')<java.index('readPackagedText("bf15100_amdahl_encounter_evidence.js")')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content('<!doctype html><html><body><details id="bf10800-encounter-ledger">'
        '<summary>2022 GLOBAL ENCOUNTER REFS · 106 MISSION RECORDS</summary><p>source only</p>'
        '<select id="bf10800-mission"></select><p id="bf10800-raw"></p></details></body></html>')
    page.evaluate("""data=>{
      const saved={'bf_global_offline_demo_v7':'existing-save-must-not-change'};
      let writes=0;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>saved[k]??null,setItem:(k,v)=>{writes++;saved[k]=String(v);},
        removeItem:k=>{writes++;delete saved[k];}
      }});
      window.__writes=()=>writes;
      window.P={version:7,roster:[10011],squad:[10011],questClears:{365:1}};
      window.S={mode:'archive',party:[{unitId:10011}],enemies:[]};
      window.QUESTS=data.live.map(r=>({missionId:r[0]}));
      window.__beforeP=JSON.stringify(P);window.__beforeS=JSON.stringify(S);
      const refs=new Map(data.live.map(r=>[r[0],{
        missionId:r[0],raw:'3:10100',
        refs:[{opaqueLabel:'3',opaqueRef:'10100'}]
      }]));
      window.BFGlobalEncounterReferencesV10900={
        summary:{archivedMissions:106,sha256:data.master,meaningDecoded:false},
        lookup:id=>refs.get(id)||null,
        references:token=>token==='10100'?[1,2]:[]
      };
      const dungeons=data.dungeons.map(d=>({
        id:d.id,firstMissionId:d.id,name:d.name
      }));
      window.BFAmdahlOriginalArtV14900={
        entries:dungeons,lookup:id=>dungeons.find(d=>d.id===id)||null,
        source:{sourceYear:2022,originalGameplayEnabled:false,decodedEnemyWaves:false}
      };
      const select=document.getElementById('bf10800-mission');
      for(const row of data.live){const option=document.createElement('option');
        option.value=String(row[0]);option.textContent='Mission '+row[0];select.append(option);}
    }""",{'live':E['records'],'dungeons':Q['dungeons'],'master':master})
    before=page.evaluate("""()=>({
       p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
    })""")
    page.add_script_tag(path=str(A/'bf15100_amdahl_encounter_evidence.js'))
    api='BFGlobalEncounterReferencesV15100'
    assert page.evaluate('Boolean(window.'+api+')') is True
    assert page.evaluate(api+'.summary.archivedMissions')==142
    assert page.evaluate(api+'.summary.playableMissions')==106
    assert page.evaluate(api+'.summary.amdahlSourceOnlyMissions')==36
    assert page.evaluate(api+'.summary.meaningDecoded') is False
    assert page.evaluate(api+'.summary.gameplayMutation') is False
    assert page.evaluate(api+'.summary.saveMutation') is False
    assert page.locator('#bf10800-mission option').count()==142
    assert page.evaluate(api+'.lookup(400).requires')==365
    assert page.evaluate(api+'.lookup(465).requires')==464
    assert page.evaluate(api+'.lookup(465).originalSourceWaveCount')==12
    assert page.evaluate(api+'.lookup(460).playable') is False
    assert page.evaluate(api+'.lookup(460).nativeEnemyIdsKnown') is False
    assert page.evaluate(api+'.lookup(365).missionId')==365
    assert page.evaluate(api+'.lookup(999)') is None
    assert page.evaluate(api+'.references("50100")')==[400,401,402,403,404]
    assert page.evaluate(api+'.references("10100")')==[1,2]
    assert page.evaluate(api+'.references("__proto__")')==[]
    assert '142 SOURCE MISSIONS' in page.locator('#bf10800-encounter-ledger summary').inner_text()
    page.locator('#bf10800-encounter-ledger > summary').click()
    page.locator('#bf10800-mission').select_option('465')
    rendered=page.locator('#bf10800-raw').inner_text()
    assert 'Amdahl' in rendered and 'NO decoded enemy formations' in rendered
    after=page.evaluate("""()=>({
       p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()
    })""")
    assert after==before,(before,after)
    page.add_script_tag(path=str(A/'bf15100_amdahl_encounter_evidence.js'))
    assert page.locator('#bf10800-mission option').count()==142
    page.evaluate('P.version=8')
    page.evaluate('delete window.BFGlobalEncounterReferencesV15100')
    page.add_script_tag(path=str(A/'bf15100_amdahl_encounter_evidence.js'))
    assert page.evaluate('Boolean(window.'+api+')') is False
    assert page.locator('#bf10800-mission option').count()==142
    assert not errors,errors
    browser.close()
print('PASS v151: 36 authentic Amdahl opaque refs / 7 patterns extend 106→142 source records; 106 playable and v7 saves unchanged')
