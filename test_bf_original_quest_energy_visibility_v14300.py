"""v143: source-exact 2022 quest Energy/Karma in live offline list; no stamina/save mutation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,shutil
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
assert M['total']==106 and M['year']==2022
js=(A/'bf14300_original_quest_energy.js').read_text('utf8')
assert 0<len(js.encode('utf8'))<65536
assert js.count('BF_ORIGINAL_2022_QUEST_ENERGY_VISIBILITY_V14300')==1
assert M['canonicalTupleSha256'] in js
i=js.index('const records=')+len('const records=')
tuples,_=json.JSONDecoder().raw_decode(js[i:])
assert tuples==M['records']
assert len({row[0] for row in tuples})==106
assert 'staminaEnforced:false' in js and 'saveMutation:false' in js
assert 'saveProgress(' not in js and 'localStorage' not in js and 'BFAndroid' not in js
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf14300_original_quest_energy.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=> {
   const d={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>d[k]??null,setItem:(k,v)=>d[k]=String(v),removeItem:k=>delete d[k],
     key:i=>Object.keys(d)[i]??null,get length(){return Object.keys(d).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.locator('button.questcard').count()==106
 before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   local:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.add_script_tag(path=str(A/'bf14300_original_quest_energy.js'))
 assert p.evaluate('BFOriginalGlobalQuestEnergyV14300.source.recordCount')==106
 assert p.evaluate('BFOriginalGlobalQuestEnergyV14300.source.staminaEnforced') is False
 assert p.locator('button.questcard .bf143-original-cost').count()==106
 for row in M['records']:
  label=p.locator('button.questcard .bf143-original-cost').nth(
      next(i for i,q in enumerate(tuples) if q[0]==row[0]))
  assert 'Energy '+str(row[4])+' · Karma '+str(row[7]) in label.text_content()
 p.evaluate('renderQuestList()')
 p.wait_for_function("""()=>document.querySelectorAll('button.questcard .bf143-original-cost').length===106""")
 p.evaluate('renderQuestList()')
 p.wait_for_function("""()=>document.querySelectorAll('button.questcard .bf143-original-cost').length===106""")
 assert p.evaluate("BFOriginalGlobalQuestEnergyV14300.refresh()")==106
 assert p.evaluate("BFOriginalGlobalQuestEnergyV14300.lookup(99999)===null") is True
 assert p.evaluate('BFOriginalGlobalQuestEnergyV14300.lookup(1)[4]')==0
 assert p.locator('button.questcard .bf143-original-cost').count()==106
 after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   local:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after
 assert not errors,errors
 b.close()
print('PASS v143 original 2022 quest energy/karma visible for 106 live missions, repeat-render safe, v7 save untouched')
