"""v105: optional advanced Smart Auto only, original defaults unchanged."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf10500_qol_advanced_smart_auto.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500')==1
assert len(js.encode())<65536
assert not any(t in js for t in ('saveProgress(', 'awardDemoRewards(', 'P.squad=', 'S.party=', 'S.enemies='))
assert 'window.BF041SmartAuto=freeze({...smart,kindFor})' in js
assert 'window.BF042AutoCoordination=freeze({...coordinated,chooseTarget})' in js
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}}});
 }""")
 p.set_content("""<html><body><label id="bf041-smart-auto-label">
 <input id="bf041-smart-auto" type="checkbox" checked>Smart Support</label></body></html>""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011,20011,30011],squad:[10011,20011,30011],questClears:{}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.__party105=[
     {unitId:20011,id:0,active:true,hp:50,maxHp:100,bb:100},
     {unitId:10011,id:1,active:true,hp:100,maxHp:100,bb:100},
     {unitId:30011,id:2,active:true,hp:100,maxHp:100,bb:100}
   ];
   window.liveParty=()=>__party105;
   window.bfOriginalBB=id=>id===20011?{target:'support'}:
     id===30011?{target:'support'}:{target:'single'};
   window.originalSupport=id=>id===20011?{kind:'heal_all'}:
     id===30011?{kind:'atk_buff_all',pct:30}:null;
   window.BF041SmartAuto={
     enabled:()=>document.getElementById('bf041-smart-auto').checked,
     kindFor:p=>p.bb>=100?'burst':'attack'
   };
   window.BF042AutoCoordination={
     enabled:()=>BF041SmartAuto.enabled(),
     chooseTarget:foes=>foes.slice().sort((a,b)=>a.hp/a.maxHp-b.hp/b.maxHp)[0],
     plan:party=>new Map(party.map(u=>[u,BF041SmartAuto.kindFor(u)]))
   };
 }""")
 saved=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf10500_qol_advanced_smart_auto.js'))
 api='BFGlobalQoLAdvancedAutoV10500'
 assert p.evaluate(api+'.get().on') is False
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='burst'
 foes=[{'hp':70,'maxHp':1000,'slot':0},{'hp':20,'maxHp':100,'slot':1}]
 assert p.evaluate("""foes=>BF042AutoCoordination.chooseTarget(foes).slot""",foes)==0
 settings={'on':True,'heal':35,'target':'absolute','burst':'conserve'}
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate(api+'.active()') is True
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='attack'
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='attack'
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[2])')=='burst'
 assert p.evaluate("""foes=>BF042AutoCoordination.chooseTarget(foes).slot""",foes)==1
 settings['heal']=75
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='burst'
 p.locator('#bf041-smart-auto').uncheck()
 assert p.evaluate(api+'.active()') is False
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==saved
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_qol_advanced_auto_v105')).on") is None
 p.add_script_tag(path=str(A/'bf10500_qol_advanced_smart_auto.js'))
 assert p.locator('#bf10500-auto-settings').count()==1
 assert not errors,errors
 b.close()
print('PASS v105 Smart Auto defaults, healer threshold, target, BB conservation and v7 isolation')
