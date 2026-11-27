#!/usr/bin/env python3
import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A,D,order=map(pathlib.Path,sys.argv[1:]);errors=[];n=0
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__writes=0;window.__fail=false;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{if(window.__fail)throw Error('quota');db[k]=String(v);window.__writes++},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve()}''')
 p.set_content((D/'index.html').read_text(),wait_until='load',timeout=45000)
 for f in order.read_text().splitlines():p.add_script_tag(content=((D/f) if (D/f).exists() else (A/f)).read_text())
 def ck(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 def ev(s):return p.evaluate(s)
 def select(id,qty=1):
  ev(f"(()=>{{let e=document.getElementById('bf-merit-offer');e.value='{id}';e.onchange();let q=document.getElementById('bf-merit-qty');q.value='{qty}';q.oninput()}})()")
 def click(id):
  if id.startswith('bf-merit-buy-'):select(id.removeprefix('bf-merit-buy-'));id='bf-merit-buy'
  return ev(f"document.getElementById('{id}').click()")
 ck(not errors,'native module order')
 ev("document.getElementById('mode').value='archive';reset();saveProgress()")
 ck(ev('copyCommitProgress(next=>{next.zel=1000000;next.trainingShards=1000;next.unitExp[10011]=327;next.evolutions[20011]=20015;next.unitExp[20011]=24255;next.unitExp[30011]=9999;return true})'),'disposable cap fixtures')
 ev('renderProgress();reset()')
 ck(ev('bfOwnedLevel(10011)===11&&bfOwnedNextExp(10011)===3&&bfOwnedLevel(20011)===99&&bfOwnedNextExp(20011)===495&&bfOwnedLevel(30011)===12&&bfOwnedNextExp(30011)===0'),'source caps and 99 to 100 bridge')
 ck(ev('!smartTrainingPlan(30011)&&!performTraining(30011,1)'),'legacy overflow remains intact, no wasted training')
 ck(ev('P.unitExp[30011]===9999'),'legacy EXP not erased')
 ck(ev('!performTraining(10011,5)'),'unnecessary bulk shard purchase blocked')
 ev('window.__writes=0;window.__z=P.zel;window.__sh=P.trainingShards;window.__raw=localStorage.getItem(SAVE_KEY);window.__fail=true')
 ck(ev('!performTraining(10011,1)&&P.unitExp[10011]===327&&P.zel===__z&&P.trainingShards===__sh&&localStorage.getItem(SAVE_KEY)===__raw'),'legacy training quota rollback')
 ev('window.__fail=false;saveProgress();renderProgress();window.__writes=0')
 ck(ev('performTraining(10011,1)&&P.unitExp[10011]===330&&P.zel===__z-150&&P.trainingShards===__sh-1&&__writes===1'),'one shard reaches exact cap atomically')
 ck(ev('bfOwnedLevel(10011)===12&&!smartTrainingPlan(10011)&&!performTraining(10011,1)'),'max cap blocks manual and smart')
 ck(ev('smartTrainingPlan(20011).count===50&&smartTrainingPlan(20011).gain===495'),'50 shards to level 100 bridge')
 ck(ev('smartTrainNext(20011,P)&&P.unitExp[20011]===24750&&bfOwnedLevel(20011)===100'),'actual level 100 training')
 ck(ev('S.party.find(a=>a.baseId===20011).level===100'),'battle level 100 matches training')
 ck(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'save roundtrip')
 ev('renderProgress();window.BF_homeNav.go("home")')
 ck(ev('document.querySelector(`[data-bf-home-unit-id="20011"] small`).textContent==="Lv.100"'),'Home level 100')
 ck(ev('document.querySelector(`[data-bf-home-unit-id="30011"] small`).textContent==="Lv.12"'),'Home legacy overcap display')
 ev('window.BF_homeNav.go("units");window.BFInnerScreens.setTab("box");window.BFUnitBox.showDetail(20011)')
 ck(ev('document.getElementById("bf-box-detail").textContent.includes("Lv.100")'),'Unit Box level 100')
 ev('window.BF_homeNav.go("home");window.__writes=0;window.__raw=localStorage.getItem(SAVE_KEY);document.getElementById("bf-r12-home-merit").click()')
 ck(ev('window.BF_homeNav.current==="units"&&window.BFInnerScreens.unitTab==="evolve"&&document.getElementById("bf-merit-experiment").open&&document.querySelector(".inventory-details").open'),'Home Merit shortcut routes to actual exchange')
 ck(ev('__writes===0&&localStorage.getItem(SAVE_KEY)===__raw'),'shortcut is read-only')
 ev('window.BF_homeNav.go("home");S.busy=true;document.getElementById("bf-r12-home-merit").click()')
 ck(ev('window.BF_homeNav.current==="home"'),'busy battle refuses shortcut')
 ev('S.busy=false')
 ck(not errors,'no page errors')
 print('TOTAL',n,flush=True);b.close()
