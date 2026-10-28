"""v153 2022 original Global 4k Merit Legend Stone offer reference, not a purchase."""
from pathlib import Path
import hashlib,json,os,re,shutil,zipfile
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
v137=json.loads((R/'source_data/bf_global_2022_legend_stone_exchange_v137.json').read_text('utf8'))
v130=json.loads((R/'source_data/bf_global_2022_starter_typed_evolution_v130.json').read_text('utf8'))
src=(A/'bf15300_legend_stone_merit_source.js').read_text('utf8')
archiveSha='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
masterSha='00fc854cdcf3f507ac0544a6e6774af5afad22cf89e0c1b535d11258ab3b54e9'
assert v137['sourceArchiveSha256']==archiveSha and v137['sourceFileSha256']['exchangeHall']==masterSha
assert v137['exchangeHall']['sourceCostCurrencyVerified'] is False
assert v137['liveAcquisitionEnabled'] is False and v137['playerInventoryMigrated'] is False
assert len(v130['rows'])==12 and all(
 any(material[1]==2 and material[2]==110100 for material in row[7])
 for row in v130['rows'])
assert src.count('BF_GLOBAL_ORIGINAL_2022_LEGEND_STONE_MERIT_EXCHANGE_V15300')==1
assert 0<len(src.encode())<65536
m=re.search(r'const records=(\[.*?\]);',src,re.S)
assert m
# JS literals are single-quoted; use a safe literal-only conversion after
# restricting exact formatting. No script evaluation in Python.
raw=m.group(1)
assert re.fullmatch(r"[\[\],0-9:'\s-]+",raw),raw[:200]
import ast
records=ast.literal_eval(raw)
assert records==v137['exchangeHall']['last2022Rows']
assert [r[0] for r in records]==[80000056,80000057,80000058,80000059]
assert all(r[1:4]==[4000,99,'4:110100:1:0'] for r in records)
assert all(r[4][:7] in ['2022-01','2022-02','2022-03','2022-04'] for r in records)
assert records[-1][5]=='2022-05-01 07:59:59'
assert all(r in v137['exchangeHall']['historicalNamedRows'] for r in records)
assert all(t not in src for t in ('localStorage.', 'saveProgress(', 'P.materials=', 'P.unitExp=',
    'P.roster=', 'S.enemies=', 'awardDemoRewards(', 'Math.random(', 'fetch(', 'XMLHttpRequest(',
    'BFAndroid', 'setTimeout(', 'setInterval('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf13000_original_starter_typed_evolution.js")') < \
       java.index('readPackagedText("bf15300_legend_stone_merit_source.js")')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
archive=os.getenv('BF_ORIGINAL_2022_MST_ZIP')
if archive:
 payload=Path(archive).read_bytes()
 assert hashlib.sha256(payload).hexdigest()==archiveSha
 with zipfile.ZipFile(archive) as z:
  b=z.read('3-mst-translated/F_ACHIEVEMENT_TRADE_MST_2_Ver432.json')
  assert hashlib.sha256(b).hexdigest()==masterSha
  whole=json.loads(b)
  reconstructed=[]
  for r in whole:
   if r.get('exchangeHallId') in {str(x[0]) for x in records}:
    reconstructed.append([int(r['exchangeHallId']),int(r['exchangeHallCost']),
       int(r['exchangeHallLimit']),r['exchangeHallItem'],
       r['availabilityTimeStart'],r['availabilityTimeEnd']])
  assert sorted(reconstructed)==records
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=browser.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<!doctype html><html><body><details id="bf13000-source-evolutions">'
               '<summary>2022 original recipes</summary></details></body></html>')
 p.evaluate("""()=>{
   let writes=0;const save={'bf_global_offline_demo_v7':'keep-v124-save'};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>save[k]??null,setItem:(k,v)=>{writes++;save[k]=String(v);},
     removeItem:k=>{writes++;delete save[k];}
   }});
   window.__writes=()=>writes;
   window.P={version:7,roster:[10011,20011],squad:[10011],unitExp:{10011:300},materials:{}};
   window.S={mode:'idle',party:[],enemies:[]};
   window.BFGlobalOriginalStarterTypedEvolutionV13000={
      source:{sourceItemId:110100,playableExpansion:false,sourceItemAcquisitionKnown:false}
   };
 }""")
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 p.add_script_tag(path=str(A/'bf15300_legend_stone_merit_source.js'))
 api='BFGlobalOriginalLegendStoneExchangeV15300'
 assert p.evaluate('Boolean(window.'+api+')') is True
 assert p.evaluate(api+'.source.originalPrice')==4000
 assert p.evaluate(api+'.source.liveAcquisition') is False
 assert p.evaluate(api+'.source.saveMutation') is False
 assert p.evaluate(api+'.offers.length')==4
 assert p.evaluate(api+'.lookup(80000059).historicalLimit')==99
 assert p.evaluate(api+'.lookup(80000059).livePurchasable') is False
 assert p.evaluate(api+'.lookup(9999)') is None
 p.locator('#bf15300-legend-stone-source > summary').click()
 assert '4,000 Merit Points' in p.locator('#bf15300-price').inner_text()
 assert 'NOT a restriction' in p.locator('#bf15300-legend-stone-source').inner_text()
 assert p.locator('#bf15300-legend-stone-source').count()==1
 assert p.evaluate('Object.isFrozen('+api+'.source)') is True
 assert p.evaluate('Object.isFrozen('+api+'.offers)') is True
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})""")
 assert before==after,(before,after)
 p.add_script_tag(path=str(A/'bf15300_legend_stone_merit_source.js'))
 assert p.locator('#bf15300-legend-stone-source').count()==1
 # If the evidence gate fails, neither UI nor API may be installed.
 p.evaluate('delete window.BFGlobalOriginalLegendStoneExchangeV15300;P.version=8')
 p.add_script_tag(path=str(A/'bf15300_legend_stone_merit_source.js'))
 assert p.evaluate('Boolean(window.'+api+')') is False
 assert not errors,errors
 browser.close()
print('PASS v153: exact 2022 Legend Stone 4k source price, 4 monthly records, no purchase or save mutation')
