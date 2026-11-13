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
  assert 'EXP '+str(row[5])+' · Zel '+str(row[6]) in label.text_content()
  assert 'DEMO credits EXP/Zel/Karma on clear' in label.text_content()
  assert 'stamina not enforced' in label.text_content()
 # v415 R2: interact with the ACTUAL live filter, not only source strings.
 selector=p.locator('#bf143-energy-range')
 clear=p.locator('#bf143-energy-clear')
 assert selector.count()==1 and clear.count()==1
 groups={
   'all':[r[0] for r in tuples],
   '0':[r[0] for r in tuples if r[4]==0],
   '1-3':[r[0] for r in tuples if 1<=r[4]<=3],
   '4-6':[r[0] for r in tuples if 4<=r[4]<=6],
   '7+':[r[0] for r in tuples if r[4]>=7],
 }
 for width in (320,370,390,540):
  p.set_viewport_size({'width':width,'height':844})
  measure=p.evaluate("""() => {
    const panel=document.querySelector('#bf143-energy-filter');
    const range=document.querySelector('#bf143-energy-range').getBoundingClientRect();
    const clear=document.querySelector('#bf143-energy-clear').getBoundingClientRect();
    const outer=panel.getBoundingClientRect();
    return {width:innerWidth,left:outer.left,right:outer.right,
      rangeHeight:range.height,clearHeight:clear.height,
      rangeLeft:range.left,rangeRight:range.right,
      clearLeft:clear.left,clearRight:clear.right};
  }""")
  assert measure['rangeHeight']>=44 and measure['clearHeight']>=44,(width,measure)
  assert measure['left']>=-1 and measure['right']<=width+1,(width,measure)
  assert all(-1<=measure[k]<=width+1 for k in
      ('rangeLeft','rangeRight','clearLeft','clearRight')),(width,measure)
  for key,expected in groups.items():
   selector.select_option(key)
   visible=p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
      .filter(b=>!b.hidden)
      .map(b=>Number((b.querySelector('strong')?.textContent||'').match(/Mission (\\d+)/)?.[1]))
      .filter(Number.isSafeInteger)""")
   assert sorted(visible)==sorted(expected),(width,key,visible,expected)
   assert p.locator('#bf143-energy-count').inner_text()==f'{len(expected)} of 106 source-matched quests shown'
   assert p.locator('#questlist button.questcard:visible').count()==len(expected),(width,key)
  selector.select_option('7+')
  # A core Quest-list rerender must preserve the user's read-only discovery filter.
  p.evaluate('renderQuestList()')
  p.wait_for_function("""() => document.querySelectorAll(
      '#questlist button.questcard .bf143-original-cost').length===106""")
  assert p.locator('#questlist button.questcard:visible').count()==len(groups['7+'])
  clear.click()
  assert selector.input_value()=='all'
  assert p.evaluate('document.activeElement.id')=='bf143-energy-range'
  assert p.locator('#questlist button.questcard:visible').count()==106
 p.set_viewport_size({'width':390,'height':844})
 # Existing demo mission selection, Auto and canonical save must not be mutated by filtering.
 assert before==p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   local:localStorage.getItem('bf_global_offline_demo_v7')})""")
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
print('PASS v143 original 2022 quest Energy/Karma/EXP/Zel references for 106 missions, repeat-render safe, v7 save untouched')
