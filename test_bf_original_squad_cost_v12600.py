"""v126: Source-exact 2022 playable original unit cost display with v7 save isolation."""
import hashlib,json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_playable_unit_cost_v126.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-playable-unit-cost-v126'
assert source['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert [(r['path'],r['sha256']) for r in source['translatedFiles']]==[
 ('3-mst-translated/F_UNIT_MST_1_Ver1084.json','1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645'),
 ('3-mst-translated/F_UNIT_MST_2_Ver1084.json','0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b')]
rows=source['records']
assert len(rows)==72 and len({v[0] for v in rows})==72
assert all(isinstance(v,list) and len(v)==3 and all(type(x) is int for x in v) for v in rows)
assert all(v[1]>0 and 2<=v[2]<=6 for v in rows)
assert rows[0]==[10011,2,2] and rows[9]==[10025,25,6] and rows[-1]==[60042,6,3]
assert [v[1:] for v in rows[:12]]==[[2,2],[4,3],[8,4],[10,5],[20,6],[3,2],[5,3],[9,4],[14,5],[25,6],[4,2],[6,3]]
assert all(rows[12*i+j]==[10000*(i+1)+rows[j][0]%10000,rows[j][1],rows[j][2]] for i in range(6) for j in range(12))
digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
assert digest==source['canonicalSHA256']=='ad903ea6923fd71bfd14f50d6bfa566f2391e37a317a053c5236995118a12247'
code=(A/'bf12600_original_squad_cost.js').read_text('utf8')
assert len(code.encode())<65536
assert digest in code and source['sourceZipSha256'] in code
for forbidden in ('localStorage.setItem','saveProgress(', 'P.squad=', 'P.roster=', 'P.evolutions=', 'Math.random','fetch(','XMLHttpRequest'):
 assert forbidden not in code,forbidden
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11200_all_playable_leader_source.js")')<java.index('readPackagedText("bf12600_original_squad_cost.js")')
assert java.index('readPackagedText("bf11500_original_unit_level_caps.js")')<java.index('readPackagedText("bf12600_original_squad_cost.js")')
html=(A/'index.html').read_text('utf8')
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda err:errors.append(str(err)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content(html,wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 assert page.evaluate("typeof effectiveUnit")=='function'
 page.evaluate("""rows=>{
 const refs=new Map(rows.map(r=>[r[0],{unitId:r[0],rarity:r[2]}]));
 window.BFGlobalPlayableLeadersV11200={source:{forms:72},lookup:id=>refs.get(id)||null};
 }""", rows)
 page.add_script_tag(content=code)
 assert page.evaluate('typeof BFGlobalOriginalSquadCostV12600')=='object'
 observed=page.evaluate('(ids)=>ids.map(id=>BFGlobalOriginalSquadCostV12600.lookup(id))',[10011,10025,60042,123456789])
 assert observed[:3]==[{'unitId':10011,'cost':2,'rarity':2,'original2022':True,'displayOnly':True},{'unitId':10025,'cost':25,'rarity':6,'original2022':True,'displayOnly':True},{'unitId':60042,'cost':6,'rarity':3,'original2022':True,'displayOnly':True}]
 assert observed[3] is None
 assert page.locator('#bf12600-original-squad-cost').count()==1
 assert page.locator('#bf12600-original-squad-cost summary').count()==1
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:localStorage.getItem('bf_global_offline_demo_v7')})""")
 scenarios=page.evaluate("""()=>{
 const saved={roster:P.roster,squad:P.squad,evolutions:P.evolutions};
 try{
   P.roster=[10011,20011];P.squad=[10011,20011,null,null,null,null];P.evolutions={};
   const base=BFGlobalOriginalSquadCostV12600.snapshot();
   P.evolutions={10011:10015,20011:20015};
   const evolved=BFGlobalOriginalSquadCostV12600.refresh();
   P.evolutions={10011:123456789};
   const unknown=BFGlobalOriginalSquadCostV12600.refresh();
   return {base,evolved,unknown};
 }finally{P.roster=saved.roster;P.squad=saved.squad;P.evolutions=saved.evolutions;
   BFGlobalOriginalSquadCostV12600.refresh();}
 }""")
 assert scenarios['base']['originalSquadCost']==4 and scenarios['base']['count']==2 and scenarios['base']['complete']
 assert scenarios['evolved']['originalSquadCost']==40 and scenarios['evolved']['rows'][0]['unitId']==10015
 assert scenarios['evolved']['rows'][1]['unitId']==20015
 assert scenarios['unknown']['complete'] is False and scenarios['unknown']['count']==1
 assert scenarios['unknown']['originalSquadCost']==2 and len(scenarios['unknown']['unsupported'])==1
 assert scenarios['unknown']['capacityKnown'] is False and scenarios['unknown']['originalCapacityLimit'] is None
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert after==before,(before,after)
 assert not errors,errors
 browser.close()
print('PASS v126: 72 original 2022 playable unit cost/rarity values, live squad sums, incomplete-source rejection and v7 saves unchanged')
