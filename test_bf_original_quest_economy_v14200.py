"""v142: 106 LIVE original 2022 Global story quest rewards/gating, no guessed drops."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,json,os,re,shutil
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
V=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
assert V['schema']=='bf-global-original-2022-live-quest-economy-v142'
assert V['year']==2022 and V['readOnly'] is True and V['total']==106
assert V['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert V['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
columns=['missionId','missionDungeonId','requiredMissionId','missionBattleCount','missionEnergyUse','exp','zel','karma']
assert V['columns']==columns
source=V['records']
assert len(source)==len({row[0] for row in source})==106
assert source==sorted(source) and all(len(r)==8 and all(isinstance(v,int) and v>=0 for v in r) for r in source)
canonical=json.dumps(source,separators=(',',':')).encode()
assert hashlib.sha256(canonical).hexdigest()=='a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66'
assert V['canonicalTupleSha256']==hashlib.sha256(canonical).hexdigest()
html_path=Path(os.environ.get('BF142_HTML',str(A/'index.html')))
html=html_path.read_text('utf8')
decoder=json.JSONDecoder();name='window.BF_QUEST_CATALOG='
pos=html.find(name)
assert pos>=0
quests,_=decoder.raw_decode(html[pos+len(name):])
for match in re.finditer(r'window\.BF_QUEST_CATALOG\.push\(',html):
 start=match.end();end=html.find(');',start)
 assert end>start and end-start<100000
 blocks,_=decoder.raw_decode('['+html[start:end]+']')
 quests.extend(blocks)
assert len(quests)==len({q['missionId'] for q in quests})==106
lookup={q['missionId']:q for q in quests}
assert set(lookup)=={x[0] for x in source}
for row in source:
 q=lookup[row[0]]
 actual=[q['missionId'],q['dungeonId'],q['requires'],q['battles'],q['energy'],q['exp'],q['zel'],q['karma']]
 assert actual==row,(row[0],actual,row)
assert 'function awardDemoRewards()' in html
assert 'P.exp+=QUEST.exp;P.zel+=QUEST.zel;P.karma+=QUEST.karma;' in html
assert 'P.questClears[QUEST.missionId]' in html
assert 'bf_global_offline_demo_v7' in html
# Full packaged WebView evaluates exactly the same quest economy with no save mutation.
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const data={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k],
    key:i=>Object.keys(data)[i]??null,get length(){return Object.keys(data).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content(html,wait_until='load',timeout=90000)
 state=page.evaluate('''()=>({version:P.version,save:localStorage.getItem('bf_global_offline_demo_v7'),
   quests:QUESTS.map(q=>[q.missionId,q.dungeonId,q.requires,q.battles,q.energy,q.exp,q.zel,q.karma])})''')
 assert state['version']==7
 assert state['quests']==[ [q['missionId'],q['dungeonId'],q['requires'],q['battles'],q['energy'],q['exp'],q['zel'],q['karma']] for q in quests]
 assert state['save']==page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 assert not errors,errors
 browser.close()
print('PASS v142: 106 LIVE quests match exact original 2022 source mission rewards, energy, waves, unlocks; save remains v7')
