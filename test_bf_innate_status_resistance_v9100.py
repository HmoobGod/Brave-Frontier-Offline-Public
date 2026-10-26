"""v91 original 2022 innate status resistances affect actual DEMO ailment infliction."""
from pathlib import Path
import re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf9100_innate_status_resistance.js').read_text('utf8')
base=(A/'bf5700_original_ailment_state.js').read_text('utf8')
assert len(js.encode())<65536 and js.count('BF_GLOBAL_INNATE_STATUS_RESISTANCE_V9100')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
assert 'BFGlobalInnateStatusResistV9100?.immune(slot,code)' in base
assert sum(line.strip() == 'if(window.BFGlobalInnateStatusResistV9100?.immune(slot,code))return false;' for line in base.splitlines()) == 1
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf5700_original_ailment_state.js")') < java.index('readPackagedText("bf9100_innate_status_resistance.js")')
assert java.index('readPackagedText("bf9000_live_crystal_provenance.js")')<java.index('readPackagedText("bf9100_innate_status_resistance.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf5700_original_ailment_state.js'))
 assert p.evaluate('P.version')==7
 # Missing optional module retains fully backwards compatible v57 behavior.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,6)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20230).removed')==[6]
 saved=p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7'),
 stats:S.party.map(u=>[u.hp,u.bb,u.atk,u.def])})""")
 p.add_script_tag(path=str(A/'bf9100_innate_status_resistance.js'))
 a='BFGlobalInnateStatusResistV9100'
 assert p.evaluate(a+'.source.originalRows')==2291
 assert p.evaluate(a+'.source.allImmuneRows')==28
 assert p.evaluate(a+'.source.paralysisOnlyRows')==2
 assert p.evaluate(a+'.source.malformedExcludedRows')==2
 assert p.evaluate(a+'.lookup(810212).percentages')==[0,0,0,0,0,100]
 assert p.evaluate(a+'.lookup(730302).percentages')==[100]*6
 assert p.evaluate(a+'.lookup(820518)') is None
 assert p.evaluate(a+'.lookup(830328)') is None
 assert p.evaluate(a+'.lookup(10011)') is None
 assert p.evaluate(a+'.isImmune(810212,6)') is True
 assert p.evaluate(a+'.isImmune(810212,5)') is False
 assert p.evaluate(a+'.isImmune(730302,1)') is True
 assert p.evaluate(a+'.isImmune(730302,6)') is True
 assert p.evaluate(a+'.isImmune(10011,6)') is False
 assert p.evaluate(a+'.isImmune(810212,7)') is False
 # Exact 2022 source immunity is enforced at existing v57 inflict.
 # Keep fixture-only unsupported unit IDs scoped to ONE browser task:
 # the production game's animation timer must never render a substituted ID.
 results=p.evaluate("""()=>{const unit=S.party[0],original=unit.unitId;
  const innate=BFGlobalInnateStatusResistV9100;
  const ail=BFGlobalOriginalAilmentStateV5700;
  try{
   unit.unitId=810212;
   const immunity=innate.immune(0,6),paralysis=ail.inflict(0,6),empty=ail.codesFor(0);
   const poison=ail.inflict(0,1),cure=ail.cure(0,20200)?.removed;
   unit.unitId=820212;
   const secondParalysis=ail.inflict(0,6);
   unit.unitId=730302;
   const allStatus=[1,2,3,4,5,6].map(code=>ail.inflict(0,code));
   const allCodes=ail.codesFor(0);
   unit.unitId=10011;
   const ordinaryParalysis=ail.inflict(0,6);
   const normalCure=ail.cure(0,20230)?.removed;
   return {immunity,paralysis,empty,poison,cure,secondParalysis,
     allStatus,allCodes,ordinaryParalysis,normalCure};
  }finally{unit.unitId=original}
 }""")
 assert results=={
  'immunity':True,'paralysis':False,'empty':[],
  'poison':True,'cure':[1],'secondParalysis':False,
  'allStatus':[False]*6,'allCodes':[],
  'ordinaryParalysis':True,'normalCure':[6]},results
 # Training mode cannot apply new ailments, and no source immunity is asserted.
 p.locator('#mode').select_option('training')
 assert p.evaluate(a+'.immune(0,6)') is False
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,6)') is False
 p.locator('#mode').select_option('archive')
 p.evaluate('S.party[0].unitId=10011')
 assert p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7'),
 stats:S.party.map(u=>[u.hp,u.bb,u.atk,u.def])})""")==saved
 p.add_script_tag(path=str(A/'bf9100_innate_status_resistance.js'))
 assert p.evaluate(a+'.source.allImmuneRows')==28
 assert not errors,errors
 b.close()
print('PASS v91 native-source innate ailment immunity, real inflict guard, malformed exclusions and v7 save isolation')
