"""Read-only native training quotes use disposable v7 state and never train."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>false;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'));p.add_script_tag(path=str(A/'bf_home_nav.js'))
 p.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training');document.querySelector('#bf-training-quote').open=true")
 stable=p.evaluate("JSON.stringify({P,S,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  p.locator('#bf-training-quote-count').select_option('5')
  assert '+ 750 Zel' in p.locator('#bf-training-quote-text').text_content()
  assert p.locator('#bf-training-quote-count').bounding_box()['height']>=44
 assert p.evaluate("JSON.stringify({P,S,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 result=p.evaluate("""()=>{const api=BFTrainingQuoteB100,id=P.roster[0],old={shards:P.trainingShards,zel:P.zel,spent:P.trainingSpent,exp:P.unitExp[id]},before=JSON.stringify({P,S}),out=[];
 try{P.trainingShards=8;P.zel=2000;P.trainingSpent=0;P.unitExp[id]=0;
 for(const count of [1,5]){const start=JSON.stringify({P,S});out.push({q:api.quote(id,count),unchanged:JSON.stringify({P,S})===start});}
 const bad=[null,2,'1',-1].map(v=>api.quote(id,v));P.unitExp[id]='0';const malformed=api.quote(id,1);
 return {out,bad,malformed};}finally{P.trainingShards=old.shards;P.zel=old.zel;P.trainingSpent=old.spent;P.unitExp[id]=old.exp;api.refresh();}}""")
 for row,count in zip(result['out'],(1,5)):
  assert row['unchanged'] and row['q']['cost']==150*count and row['q']['expAfter']==10*count and row['q']['shardsAfter']==8-count and row['q']['zelAfter']==2000-150*count,row
 assert result['bad']==[None]*4 and result['malformed'] is None,result
 assert p.evaluate("JSON.stringify({P,S,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 assert not errors,errors
 b.close()
print('PASS native training cost/EXP quote, two exact budgets, malformed refusal, three widths and full state invariance')
