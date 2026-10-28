"""v155: source 2022 story first-clear reward references, NO live Gem grant."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,base64,gzip,hashlib,json,os,re,shutil,zipfile
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_first_clear_gem_source_v155.json').read_text('utf8'))
V=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
v152=(R/'source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64').read_text('ascii').strip()
all142=json.loads(gzip.decompress(base64.b64decode(v152)))
js=(A/'bf15500_first_clear_gem_source.js').read_text('utf8')
sourceSha='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
missionSha='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert M['schema']=='bf-global-2022-original-story-first-clear-gem-source-v155'
assert M['originalZipSha256']==V['sourceArchiveSha256']==sourceSha
assert M['sourceTables'][0]['sha256']==V['missionMasterSha256']==missionSha
assert M['sourceRowsSha256']=='de8bde1cbee451e3c1b07c8b3e47afd38bc0465787b2b4aa6f5c8a620c4c83a7'
rows=M['rows']
assert len(rows)==29 and len({r[0] for r in rows})==29
assert rows==sorted(rows) and all(r[1]=='8:0:1:0:0' and r[2] in (0,1) for r in rows)
assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()==M['sourceRowsSha256']
assert sum(r[2] for r in rows)==22 and sum(1-r[2] for r in rows)==7
assert [r[0] for r in rows[22:]]==[404,414,424,434,444,454,465]
assert M['currentlyLiveRewardMissions']==22 and M['amdahlSourceOnlyRewardMissions']==7
assert M['liveGemGrantEnabled'] is False and M['gemWalletMigrated'] is False
assert M['existingV7ProgressUnaffected'] is True and M['sourceOnly'] is True
live={q[0] for q in V['records']}
all142ids={q[0] for q in all142['rows']}
assert len(live)==106 and len(all142ids)==142
assert all(q[0] in all142ids and (q[0] in live)==bool(q[2]) for q in rows)
assert M['sourceGrandRewardType8Rows']==62 and M['sourceGrandType8Item0Amount1Rows']==45
assert M['achievementEnumCrosschecks']==[
 [7000,'8:0:1:0:0','1000 Merit Points Accumulated'],
 [7020,'8:0:2:0:0','10000 Merit Points Accumulated'],
 [7040,'8:0:3:0:0','50000 Merit Points Accumulated'],
 [7060,'8:0:5:0:0','200000 Merit Points Accumulated']]
assert js.count('BF_GLOBAL_2022_DUNGEON_FIRST_CLEAR_REWARD_SOURCE_V15500')==1
match=re.search(r'const ids=(\[.*?\]);',js,re.S)
assert match and re.fullmatch(r'[\[\],0-9\s]+',match.group(1))
assert ast.literal_eval(match.group(1))==[row[0] for row in rows]
for forbidden in ('saveProgress(', 'localStorage.', 'P.questClears=', 'P.gems=',
                  'P.zel=', 'P.exp=', 'P.clears=', 'awardDemoRewards(',
                  'Math.random(', 'fetch(', 'XMLHttpRequest(', 'BFAndroid'):
 assert forbidden not in js,forbidden
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf15400_original_merit_clear_preview.js")') < \
       java.index('readPackagedText("bf15500_first_clear_gem_source.js")')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
archive=os.environ.get('BF_ORIGINAL_2022_MST_ZIP')
if archive:
 archive=Path(archive);assert hashlib.sha256(archive.read_bytes()).hexdigest()==sourceSha
 with zipfile.ZipFile(archive) as z:
  def load(index,sha):
   b=z.read(M['sourceTables'][index]['path'])
   assert hashlib.sha256(b).hexdigest()==sha
   return json.loads(b)
  original=load(0,missionSha)
  grand=load(1,'f6e6a0c450c99045af81bcbdfffaab3e73845dd4e2240f04fd8d7fcfcc7705bf')
  ach=load(2,'36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56')
  byid={int(q['missionId']):q for q in original if q.get('missionId','').isdigit()}
  raw=[q for q in byid.values() if int(q['missionId']) in all142ids and q.get('missionRewards')]
  assert sorted([[int(q['missionId']),q['missionRewards'],1 if int(q['missionId']) in live else 0] for q in raw])==rows
  assert sum(x['rewardType']=='8' for x in grand)==62
  assert sum(x['rewardType']=='8' and x['rewardItemId']=='0' and x['rewardAmount']=='1' for x in grand)==45
  a={int(q['achievementSubjectId']):q for q in ach if q.get('achievementSubjectId','').isdigit()}
  assert all(a[id]['rewardInfo']==reward and a[id]['achievementSubjectName'].replace('<br>',' ')==name for id,reward,name in M['achievementEnumCrosschecks'])
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
     executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
     args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<!doctype html><html><body><details id="bf10800-encounter-ledger">'
                  '<summary>142 original references</summary></details></body></html>')
 page.evaluate("""sourceIds=>{
   let writes=0;const sav={'bf_global_offline_demo_v7':'v124-player-save'};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>sav[k]??null,setItem:(k,v)=>{writes++;sav[k]=String(v);},
    removeItem:k=>{writes++;delete sav[k];}
   }});
   window.__writes=()=>writes;window.P={version:7,questClears:{12:1,365:2},roster:[10011],materials:{}};
   window.S={mode:'quest',enemies:[]};
   window.QUESTS=[...sourceIds.slice(0,22).map(missionId=>({missionId})),
       ...Array.from({length:84},(_,i)=>({missionId:1000+i}))];
   window.BFGlobalEncounterReferencesV15100={
     summary:{archivedMissions:142,playableMissions:106,meaningDecoded:false}
   };
 }""",[x[0] for x in rows])
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 page.add_script_tag(path=str(A/'bf15500_first_clear_gem_source.js'))
 api='BFGlobalOriginalFirstClearRewardsV15500'
 assert page.evaluate('Boolean(window.'+api+')') is True
 assert page.evaluate(api+'.source.originalSourceRewardCount')==29
 assert page.evaluate(api+'.source.liveStoryQuestRewardCount')==22
 assert page.evaluate(api+'.source.amdahlSourceOnlyRewardCount')==7
 assert page.evaluate(api+'.source.liveGemGrantEnabled') is False
 assert page.evaluate(api+'.source.saveMutation') is False
 assert page.evaluate(api+'.lookup(12).sourceReward')=='8:0:1:0:0'
 assert page.evaluate(api+'.lookup(404).liveInDemo') is False
 assert page.evaluate(api+'.lookup(9999)') is None
 assert page.locator('#bf15500-mission option').count()==29
 page.locator('#bf15500-first-clear-sources > summary').click()
 assert 'local DEMO clear recorded: YES' in page.locator('#bf15500-source-detail').inner_text()
 page.locator('#bf15500-mission').select_option('404')
 assert 'NON-PLAYABLE Amdahl' in page.locator('#bf15500-source-detail').inner_text()
 assert 'Gems granted here: ZERO' in page.locator('#bf15500-source-detail').inner_text()
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 assert after==before
 page.add_script_tag(path=str(A/'bf15500_first_clear_gem_source.js'))
 assert page.locator('#bf15500-first-clear-sources').count()==1
 page.evaluate('delete window.BFGlobalOriginalFirstClearRewardsV15500;P.version=8')
 page.add_script_tag(path=str(A/'bf15500_first_clear_gem_source.js'))
 assert page.evaluate('Boolean(window.'+api+')') is False
 assert not errors,errors
 browser.close()
print('PASS v155: 29 original source 2022 fixed first-clear rewards (22 live, 7 locked), Gem enum corroborated, no Gem grants/v7 save changes')
