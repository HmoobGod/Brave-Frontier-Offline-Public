"""Browser integration test using real prepared game, catalog, copy ownership and v7 parser.
Disposable in-memory Storage shim; no device or owner save; all network blocked.
Usage: python test_imp_squad_browser.py <prepared assets dir>
"""
from pathlib import Path
import sys, shutil, json
from playwright.sync_api import sync_playwright
root=Path(sys.argv[1]).resolve()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'],headless=True)
 page=b.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda r:r.abort())
 page.evaluate('''()=>{const db=new Map();window.__writes=0;window.__failWrite=false;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db.has(k)?db.get(k):null,setItem:(k,v)=>{if(window.__failWrite)throw Error('simulated quota');db.set(k,String(v));window.__writes++},removeItem:k=>db.delete(k),key:i=>[...db.keys()][i]??null,get length(){return db.size}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve()}''')
 page.set_content((root/'index.html').read_text('utf8'),wait_until='domcontentloaded',timeout=90000)
 for n in ('bf_home_nav.js','bf_global_unit_archive.js','bf11000_source_starter_leader_skills.js','bf11100_original_starter_leader_combat.js','bf11200_all_playable_leader_source.js','bf11500_original_unit_level_caps.js','bf11600_original_lord_stats_data.js','bf11600_original_lord_stats_reference.js','bf16800_original_level_one_lord_combat.js','bf16900_optional_imp_fusion.js'):
  page.add_script_tag(content=(root/n).read_text('utf8'))
 out=page.evaluate('''()=>{
 const api=window.BFGlobalOptionalImpsV16900,copyId=1000000001;let checks=0;
 const ok=(v,m)=>{if(!v)throw Error(m);checks++};const eq=(a,b,m)=>ok(JSON.stringify(a)===JSON.stringify(b),m+': '+JSON.stringify(a)+' != '+JSON.stringify(b));
 const n=defaultProgress();n.roster.push(copyId);n.unitExp[copyId]=0;n.squad=[10011,copyId];n._bfUnitInstancesV1={nextId:copyId+1,baseById:{[copyId]:10011}};n._bfImpsV171={version:1,started:true,mode:'custom',amounts:{},inventory:{molin:0,pakpak:0,ganju:0,fwahl:0,arton:1},cursors:{}};
 P=parseProgress(n);saveRecoveryPending=false;ok(saveProgress(),'fixture persist');api.refresh();document.getElementById('mode').value='archive';reset();
 const stats=()=>S.party.slice(0,2).map(u=>[u.baseId,u.unitId,u.maxHp,u.atk,u.def,u.rec,u.hp]);
 const old=stats();eq(old.map(u=>u.slice(0,2)),[[10011,10011],[copyId,10011]],'actual separate battle slots');
 const before=window.__writes;ok(api.feedSquad(),'leader feed');eq(window.__writes,before+1,'one save');eq(api.bonus(10011),[150,60,60,60],'leader gain');eq(api.bonus(copyId),[0,0,0,0],'copy unaffected');eq(stats(),old,'live battle not mutated');
 reset();const next=stats();eq(next[1],old[1],'copy stats unchanged in next battle');ok(next[0][2]>old[0][2]&&next[0][3]>old[0][3]&&next[0][4]>old[0][4]&&next[0][5]>old[0][5],'leader gains reach actual battle');eq(next[0][6],next[0][2],'full HP');const rows=api.snapshot().rows;eq(rows.map(r=>r.baseId),[10011,copyId],'real audit ids');eq(rows[0].applied,[150,60,60,60],'leader audit');eq(rows[1].applied,[0,0,0,0],'copy audit');
 api.apply(S.party[0],0);eq(stats(),next,'no double application');
 document.getElementById('mode').value='training';reset();eq(api.snapshot().rows.length,0,'training excluded');
 document.getElementById('mode').value='archive';reset();eq(stats(),next,'archive rebuild stable');
 const save=localStorage.getItem(SAVE_KEY);P=parseProgress(JSON.parse(save));reset();eq(stats(),next,'save parse battle rebuild');eq(api.bonus(copyId),[0,0,0,0],'copy persists separately');
 return {checks,old,next,rows};
 }''')
 assert not errors,errors
 print('PASS actual next-battle stat application',json.dumps(out,sort_keys=True));b.close()
