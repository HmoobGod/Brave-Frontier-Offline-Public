"""Disposable Chromium test with actual prepared game and native module order."""
import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]);errors=[];n=0
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__writes=0;window.__fail=false;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{if(window.__fail)throw Error('quota');db[k]=String(v);window.__writes++},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve()}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 for f in pathlib.Path(__file__).with_name('native-order.txt').read_text().splitlines():p.add_script_tag(content=(A/f).read_text())
 def ev(s):return p.evaluate(s)
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 check(not errors,'native order loaded')
 ev("P.trainingShards=100;P.zel=100000;P.unitExp[10011]=225;saveProgress();renderProgress();BF_homeNav.go('units');BFInnerScreens.setTab('training')")
 plan=ev('smartTrainingPlan(10011)');check(plan['level']==10 and plan['count']==5 and plan['cost']==750,'minimum whole-shard selection')
 check(ev('P.trainingShards===100&&P.unitExp[10011]===225'),'preview pure')
 old=ev('JSON.parse(JSON.stringify(P))');writes=ev('__writes');btn=p.locator('.bf-smart-train-next[data-owned-id="10011"]');check(btn.is_visible() and btn.is_enabled(),'normal training UI visible')
 btn.click(timeout=5000);new=ev('JSON.parse(JSON.stringify(P))');check(new['trainingShards']==95 and new['trainingSpent']==old['trainingSpent']+5 and new['zel']==old['zel']-750,'exact existing shard/Zel debit')
 check(new['unitExp']['10011']==275 and ev('demoLevel(P.unitExp[10011])')==11,'next level reached')
 check(ev('__writes')==writes+1,'one atomic canonical write')
 check(new['roster']==old['roster'] and new['materials']==old['materials'] and new['squad']==old['squad'],'no units or other materials consumed')
 check(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'legacy v7 exact roundtrip')
 check(ev('''()=>{const snapshot={exp:P.unitExp[10011],water:P.unitExp[20011],evo:P.evolutions[20011]};try{P.evolutions[20011]=20015;let tested=0;for(const [id,cap] of [[10011,12],[20011,100]]){const end=5*(cap-1)*cap/2;let level=1;for(let x=0;x<end;x++){P.unitExp[id]=x;while(x>=5*level*(level+1)/2)level++;const next=5*level*(level+1)/2,need=next-x,count=Math.ceil(need/10),plan=smartTrainingPlan(id);if(!plan||plan.level!==level||plan.count!==count||plan.cost!==150*count||plan.gain!==Math.min(10*count,end-x)||x+plan.gain<next||x+10*(count-1)>=next)return false;tested++;}P.unitExp[id]=end;if(smartTrainingPlan(id)!==null)return false;}return tested===25080;}finally{P.unitExp[10011]=snapshot.exp;P.unitExp[20011]=snapshot.water;if(snapshot.evo===undefined)delete P.evolutions[20011];else P.evolutions[20011]=snapshot.evo;}}'''),'25080 EXP positions minimal shard math, starter Lv12 and evolved Lv100 caps')
 ev('P.trainingShards=0;saveProgress();renderTrainingPanel()');check(btn.is_disabled() and ev('smartTrainNext(10011,P)') is False,'insufficient shards')
 ev('P.trainingShards=100;P.zel=0;saveProgress();renderTrainingPanel()');check(btn.is_disabled(),'insufficient Zel')
 ev('P.zel=100000;P.trainingSpent=100000;saveProgress();renderTrainingPanel()');check(btn.is_disabled(),'existing spending cap')
 ev('P.trainingSpent=0;P.unitExp[10011]=330;saveProgress();renderTrainingPanel()');check(btn.is_disabled(),'max level protected')
 ev('P.unitExp[10011]=225;saveProgress();renderTrainingPanel();window.confirm=()=>false');before=ev('JSON.stringify(P)');writes=ev('__writes');btn.click(timeout=5000);check(ev('JSON.stringify(P)')==before and ev('__writes')==writes,'cancel no write')
 ev('window.confirm=()=>true;S.busy=true');check(ev('smartTrainNext(10011,P)') is False,'active battle blocked');ev('S.busy=false;S.auto=true;S.over=false');check(ev('smartTrainNext(10011,P)') is False,'active Auto blocked');ev('S.auto=false;saveRecoveryPending=true');check(ev('smartTrainNext(10011,P)') is False,'recovery blocked');ev('saveRecoveryPending=false');check(ev('smartTrainNext(999999,P)') is False,'unowned rejected')
 ev('window.__fail=true');before=ev('JSON.stringify(P)');raw=ev('localStorage.getItem(SAVE_KEY)');check(ev('smartTrainNext(10011,P)') is False and ev('JSON.stringify(P)')==before and ev('localStorage.getItem(SAVE_KEY)')==raw,'quota failure atomic rollback');ev('window.__fail=false;saveProgress()')
 ev("P.summonTokens=2;saveProgress();renderProgress();BF_homeNav.go('summon');Math.random=()=>0")
 p.locator('#bf-copy-summon-optin').check(timeout=5000);p.locator('#bf-copy-token-summon').click(timeout=5000);p.locator('#bf-copy-token-summon').click(timeout=5000)
 check(ev('P.roster.includes(1000000001)'),'normal duplicate acquisition')
 ev("BF_homeNav.go('units');BFInnerScreens.setTab('training');P.unitExp[1000000001]=225;saveProgress();renderTrainingPanel()")
 old=ev('JSON.parse(JSON.stringify(P))');writes=ev('__writes');p.locator('.bf-smart-train-next[data-owned-id="1000000001"]').click(timeout=5000);new=ev('JSON.parse(JSON.stringify(P))');check(new['unitExp']['1000000001']==275 and new['unitExp']['10011']==old['unitExp']['10011'],'duplicate independent training');check(new['roster']==old['roster'] and ev('__writes')==writes+1,'copy transaction one write and ownership preserved')
 check(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'copy save exact roundtrip')
 check(not errors,'no uncaught errors');print('TOTAL',n,flush=True);b.close()
