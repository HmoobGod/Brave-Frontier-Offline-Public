"""v174 browser regression: exact original 2022 encounter crossrefs, no gameplay."""
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
s=(A/'bf17400_original_2022_encounter_crossrefs.js').read_text('utf8')
packed=base64.b64decode((R/'source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64').read_text('ascii').strip(),validate=True)
assert hashlib.sha256(packed).hexdigest()=='cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a'
data=json.loads(gzip.decompress(packed))
assert data['canonicalRowsSha256']=='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'
live=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
amd=json.loads((R/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
waves={r[0]:r[3] for r in live['records']}
waves.update({q['id']:q['waveCount'] for q in amd['quests']})
expected=[r+[waves[r[0]]] for r in data['rows']]
m=re.search(r'const rows=(\[.*?\]);',s,re.S)
assert m and json.loads(m.group(1))==expected
assert len(s.encode())<65536
assert s.count('BF_GLOBAL_ORIGINAL_2022_ENCOUNTER_CROSSREFS_V17400')==1
assert not any(t in s for t in ('localStorage','saveProgress(', 'P.questClears=', 'P.roster=', 'S.enemies=', 'awardDemoRewards(', 'Math.random(', 'fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf15100_amdahl_encounter_evidence.js")')<java.index(
 'readPackagedText("bf17400_original_2022_encounter_crossrefs.js")')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<html><body><details id="bf10800-encounter-ledger"><summary>Refs</summary><select id="bf10800-mission"></select><p id="bf10800-raw"></p></details></body></html>')
 page.evaluate("""data=>{
  const saved={'bf_global_offline_demo_v7':'original-save-stays-byte-exact'};
  let writes=0;window.__writes=()=>writes;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>saved[k]??null,setItem:(k,v)=>{writes++;saved[k]=String(v);},
   removeItem:k=>{writes++;delete saved[k]}
  }});
  window.P={version:7,roster:[10011],squad:[10011],questClears:{12:1}};
  window.S={mode:'archive',party:[{baseId:10011}],enemies:[{hp:500}]};
  window.QUESTS=data.rows.slice(0,106).map(r=>({missionId:r[0]}));
  const byId=new Map(data.rows.map(r=>[r[0],{
   missionId:r[0],raw:r[1],
   ...(r[0]>=400?{originalSourceWaveCount:r[5],playable:false}:{})
  }]));
  window.BFGlobalEncounterReferencesV15100={
   summary:{archivedMissions:142,playableMissions:106,
    amdahlSourceOnlyMissions:36,sha256:data.master,meaningDecoded:false},
   lookup:id=>byId.get(id)||null
  };
  window.__Pbefore=JSON.stringify(P);window.__Sbefore=JSON.stringify(S);
  for(const row of data.rows){
   const opt=document.createElement('option');opt.value=String(row[0]);
   opt.textContent='Source mission '+row[0];
   document.getElementById('bf10800-mission').append(opt);
  }
 }""",{'rows':expected,'master':live['missionMasterSha256']})
 baseline=page.evaluate("""()=>({
  P:JSON.stringify(P),S:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7'),
  writes:__writes(),missions:QUESTS.length,options:document.getElementById('bf10800-mission').options.length
 })""")
 page.add_script_tag(path=str(A/'bf17400_original_2022_encounter_crossrefs.js'))
 api='BFGlobalEncounterCrossrefsV17400'
 assert page.evaluate('Boolean(window.'+api+')') is True
 assert page.evaluate(api+'.source.total')==142
 assert page.evaluate(api+'.source.playable')==106
 assert page.evaluate(api+'.source.amdahlReadOnly')==36
 assert page.evaluate(api+'.source.firstRefBackgroundMatches')==133
 assert page.evaluate(api+'.source.firstRefBackgroundExceptions')==9
 assert page.evaluate(api+'.source.nativeEnemyIdsDecoded') is False
 assert page.evaluate(api+'.source.nativeAIDecoded') is False
 assert page.evaluate(api+'.source.saveFieldsAdded')==0
 assert page.locator('#bf17400-encounter-crossrefs').count()==1
 for row in expected:
  id,opaque,bg,g,r,waves=row
  result=page.evaluate(api+'.lookup('+str(id)+')')
  assert result['missionId']==id and result['opaqueEncounterField']==opaque
  assert result['originalDungeonBattleBackground']==bg
  assert result['crossTableGrandSpotMatches']==g and result['crossTableRaidPointMatches']==r
  assert result['originalSourceWaveCount']==waves
  assert result['playable']==(id<400)
  assert result['enemyIdsDecoded'] is False
  assert result['enemyWavesDecoded'] is False
 assert page.evaluate(api+'.lookup(999999)') is None
 assert page.evaluate(api+'.lookup("12")') is None
 assert page.evaluate(api+'.lookup(12).firstOpaqueRefMatchesBackground') is True
 for id in [70,71,72,73,230,231,232,233,234]:
  assert page.evaluate(api+'.lookup('+str(id)+').firstOpaqueRefMatchesBackground') is False
 for id in [12,70,230,400,465]:
  page.locator('#bf10800-mission').select_option(str(id))
  rendered=page.locator('#bf17400-encounter-crossrefs').inner_text()
  assert f'2022 mission {id}' in rendered
  assert 'original battle background:' in rendered
  if id>=400:assert 'SOURCE ONLY' in rendered
  else:assert 'live quest' in rendered
  if id in (70,230): assert 'differ' in rendered
 page.add_script_tag(path=str(A/'bf17400_original_2022_encounter_crossrefs.js'))
 assert page.locator('#bf17400-encounter-crossrefs').count()==1
 now=page.evaluate("""()=>({
  P:JSON.stringify(P),S:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7'),
  writes:__writes(),missions:QUESTS.length,options:document.getElementById('bf10800-mission').options.length
 })""")
 assert now==baseline,(now,baseline)
 # All-or-nothing initialization gate: wrong save version is refused.
 page.evaluate('P.version=8;delete window.BFGlobalEncounterCrossrefsV17400')
 page.add_script_tag(path=str(A/'bf17400_original_2022_encounter_crossrefs.js'))
 assert page.evaluate('Boolean(window.'+api+')') is False
 assert page.locator('#bf17400-encounter-crossrefs').count()==1
 assert not errors,errors
 browser.close()
print('PASS v174: 142 exact 2022 source crossrefs, 133 consistent backdrops, 9 mismatches, no save/gameplay mutation')
