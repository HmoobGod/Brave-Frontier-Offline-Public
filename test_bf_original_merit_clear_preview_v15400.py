"""v154: source-verified 2022 Merit achievements vs local v7 DEMO quest clears, no awards."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,base64,gzip,hashlib,json,re,shutil,os,zipfile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_merit_clear_preview_v154.json').read_text('utf8'))
v138=json.loads((R/'source_data/bf_global_2022_merit_achievement_v138.json').read_text('utf8'))
v142=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
JS=(A/'bf15400_original_merit_clear_preview.js').read_text('utf8')
archiveSha='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
masterSha='36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56'
assert M['schema']=='bf-global-original-2022-merit-quest-clear-eligibility-v154'
assert M['archiveSha256']==v138['sourceArchiveSha256']==archiveSha
assert M['sourceTableSha256']==v138['sourceFiles'][0]['sha256']==masterSha
assert M['sourceOriginalRowsSha256']=='9481225a123e6d5060321206082a90d1fe68889854c63793b182927676bc642b'
rows=M['rows']
assert len(rows)==11 and len({r[0] for r in rows})==11
assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==M['sourceOriginalRowsSha256']
assert M['readOnly'] is True and M['saveMutation'] is False and M['meritGrantEnabled'] is False
assert M['originalClaimStatusKnown'] is False
raw=gzip.decompress(base64.b64decode(v138['gzipBase64']))
source=json.loads(raw)
assert len(source)==657
milestone_ids={r[0] for r in rows}
from138=[r for r in source if r[1] in milestone_ids]
assert len(from138)==11
actual=sorted([[r[1],int(r[5]),r[6],r[2]] for r in from138],key=lambda x:x[1])
assert actual==rows
assert all(r[0]==1 and r[4]==8500 and r[7]=='9999-12-31 23:59:59' for r in from138)
story=M['storyClear']
boss=[r for r in source if r[1]==story['achievementSubjectId']]
assert len(boss)==1 and boss[0][0]==1 and boss[0][4]==8600
assert int(boss[0][5])==story['missionId']==365 and boss[0][6]==story['meritPointReward']==100
assert boss[0][2]==story['sourceName'] and boss[0][3]==story['sourceCompletionDescription']
assert boss[0][7]=='9999-12-31 23:59:59'
bonus=M['notPlayableBonus']
assert bonus=={'achievementSubjectId':36000,'missionId':90,'meritPointReward':1000}
live={r[0] for r in v142['records']}
assert len(live)==106 and 365 in live and 90 not in live
assert len([r for r in source if r[4]==8500])==14  # 3 SP-only rows excluded
assert len([r for r in source if r[4]==8600])==63
assert JS.count('BF_GLOBAL_2022_QUEST_CLEAR_MERIT_PREVIEW_V15400')==1
q=re.search(r'const sourceRows=(\[.*?\]);',JS,re.S)
assert q and re.fullmatch(r'[\[\],0-9\s]+',q.group(1))
assert ast.literal_eval(q.group(1))==[r[:3] for r in rows]
for forbidden in ('localStorage.', 'saveProgress(', 'P.questClears=', 'P.exp=', 
                 'P.zel=', 'P.karma=', 'awardDemoRewards(', 'Math.random(', 'fetch(',
                 'XMLHttpRequest(', 'setTimeout(', 'setInterval(', 'BFAndroid'):
 assert forbidden not in JS,forbidden
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf15300_legend_stone_merit_source.js")') < \
       java.index('readPackagedText("bf15400_original_merit_clear_preview.js")')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
archive=os.environ.get('BF_ORIGINAL_2022_MST_ZIP')
if archive:
 with zipfile.ZipFile(archive) as z:
  b=z.read(M['sourceTable'])
  assert hashlib.sha256(b).hexdigest()==masterSha
  orig=json.loads(b)
  got={}
  for r in orig:
   if r.get('achievementSubjectId','').isdigit() and int(r['achievementSubjectId']) in milestone_ids|{35000,36000}:
    got[int(r['achievementSubjectId'])]=r
  assert len(got)==13
  for aId,threshold,reward,name in rows:
   x=got[aId]
   assert x['achievementSubjectName']==name and int(x['ACHIEVEMENT_t5R47iwj'])==threshold
   assert int(x['meritPointReward'])==reward and x['achievmentType']=='8500'
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
     executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
     args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page()
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<!doctype html><html><body><details id="bf15300-legend-stone-source">'
                  '<summary>2022 source Legend Stone</summary></details></body></html>')
 page.evaluate("""()=>{
    let writes=0;const sav={'bf_global_offline_demo_v7':'original-v124-untouched'};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>sav[k]??null,setItem:(k,v)=>{writes++;sav[k]=String(v);},
      removeItem:k=>{writes++;delete sav[k];}
    }});
    window.__writes=()=>writes;
    window.P={version:7,roster:[10011],squad:[10011],
      questClears:{365:1,1:9,2:"90"},unitExp:{10011:5},materials:{}};
    window.S={mode:'quest',enemies:[{hp:50}]};
    window.QUESTS=[{missionId:365},...Array.from({length:105},(_,i)=>({missionId:i+1000}))];
    window.BFGlobalOriginalLegendStoneExchangeV15300={source:{
      archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
      originalPrice:4000,liveAcquisition:false
    }};
 }""")
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
     save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 page.add_script_tag(path=str(A/'bf15400_original_merit_clear_preview.js'))
 api='BFGlobalOriginalMeritQuestPreviewV15400'
 assert page.evaluate('Boolean(window.'+api+')')
 assert page.evaluate(api+'.source.sourceMilestoneCount')==11
 assert page.evaluate(api+'.source.originalStoryClearMissionId')==365
 assert page.evaluate(api+'.source.meritAwardEnabled') is False
 assert page.evaluate(api+'.source.saveMutation') is False
 assert page.evaluate(api+'.snapshot().localDemoQuestClearCount')==100
 assert page.evaluate(api+'.snapshot().creatorOfWorldClearRecorded') is True
 assert page.evaluate(api+'.snapshot().sourceMilestones.filter(r=>r.localDemoThresholdReached).length')==2
 assert page.evaluate(api+'.snapshot().sourceMilestones[1].originalMeritReward')==200
 assert page.evaluate(api+'.snapshot().sourceMilestones[0].originalAchievementClaimed') is None
 page.locator('#bf15400-original-merit-progress > summary').click()
 assert page.locator('#bf15400-milestones > li').count()==11
 assert 'achievement claimed: UNKNOWN' in page.locator('#bf15400-story').inner_text()
 assert 'does NOT establish' in page.locator('#bf15400-original-merit-progress').inner_text()
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
     save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 assert before==after,(before,after)
 page.add_script_tag(path=str(A/'bf15400_original_merit_clear_preview.js'))
 assert page.locator('#bf15400-original-merit-progress').count()==1
 page.evaluate('P.questClears[2]=-1')
 assert page.evaluate(api+'.snapshot()') is None
 page.evaluate(api+'.refresh()')
 assert 'not reliably readable' in page.locator('#bf15400-count').inner_text()
 page.evaluate('delete window.BFGlobalOriginalMeritQuestPreviewV15400;P.version=8')
 page.add_script_tag(path=str(A/'bf15400_original_merit_clear_preview.js'))
 assert page.evaluate('Boolean(window.'+api+')') is False
 assert not errors,errors
 browser.close()
print('PASS v154: 11 source milestone refs + mission365 preview, local clear counts only, corrupt fails closed, no Merit grant/v7 writes')
