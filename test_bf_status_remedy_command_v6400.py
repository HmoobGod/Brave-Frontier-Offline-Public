"""v64 source-remedy battle command: selective cure, Guard action, no save writes."""
from pathlib import Path
import ast, json, shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
module=(A/'bf6400_status_remedy_command.js').read_text('utf8')
assert 'BF_GLOBAL_STATUS_REMEDY_COMMAND_V6400' in module
assert len(module.encode('utf8'))<65536
assert all(s not in module for s in ('localStorage','saveProgress(', 'BFAndroid'))
evidence=json.loads((R/'source_data/bf_global_2022_status_cure_evidence_v5700.json').read_text('utf8'))
assert {r['itemId']:r['codes'] for r in evidence['cures']}=={
 20200:[1],20210:[2,3,4],20220:[5],20230:[6],50200:[1,2,3,4,5,6]}
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6200_injury_attack.js")')<j.index('readPackagedText("bf6400_status_remedy_command.js")')
source=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
script_names=next(ast.literal_eval(f.iter) for f in ast.walk(source)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in script_names:p.add_script_tag(path=str(A/name))
 p.add_script_tag(path=str(A/'bf6400_status_remedy_command.js'))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().available') is False
 assert p.locator('#bf6400-remedies').is_hidden()
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),p:JSON.stringify(P),
 hp:S.party.map(p=>p.hp),bb:S.party.map(p=>p.bb),stats:S.party.map(p=>[p.atk,p.def])})""")
 for code in (1,5):assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.inflict(0,{code})') is True
 for code in (2,3,4):assert p.evaluate(f'BFGlobalOriginalAilmentStateV5700.inflict(1,{code})') is True
 p.evaluate('BFGlobalStatusRemedyCommandV6400.refresh()')
 assert p.locator('#bf6400-remedies').is_visible()
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().available') is True
 # v438: corrupt DEMO identities/health must fail before reserving any
 # player-owned Guard turn, spending transient stock, or writing the v7 save.
 guards=p.evaluate("""()=>{
   const api=BFGlobalStatusRemedyCommandV6400;
   const party=S.party, target=party[0], actor=party[2];
   const oldSave=localStorage.getItem('bf_global_offline_demo_v7');
   const oldP=JSON.stringify(P);
   const before=JSON.stringify(api.snapshot().stock);
   const beforeLocks=JSON.stringify(BFGlobalItemTurnReservationsV4500.snapshot().reservations);
   const oldActorId=actor.id, oldTargetHp=target.hp, oldTargetMaxHp=target.maxHp;
   const fail=()=>api.useRemedy(2,0,20200)===false;
   let mismatched,shuffled,nanHp,zeroMax,overheal;
   try{
     actor.id=1;mismatched=fail();actor.id=oldActorId;
     S.party=[party[0],party[2],party[1],...party.slice(3)];
     shuffled=fail();S.party=party;
     target.hp=NaN;nanHp=fail();target.hp=oldTargetHp;
     target.maxHp=0;zeroMax=fail();target.maxHp=oldTargetMaxHp;
     target.hp=oldTargetMaxHp+1;overheal=fail();
   }finally{
     S.party=party;actor.id=oldActorId;
     target.hp=oldTargetHp;target.maxHp=oldTargetMaxHp;
   }
   return {mismatched,shuffled,nanHp,zeroMax,overheal,
     stockSame:JSON.stringify(api.snapshot().stock)===before,
     locksSame:JSON.stringify(BFGlobalItemTurnReservationsV4500.snapshot().reservations)===beforeLocks,
     playerSame:JSON.stringify(P)===oldP,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===oldSave};
 }""")
 assert guards==dict(mismatched=True,shuffled=True,nanHp=True,zeroMax=True,
                     overheal=True,stockSame=True,locksSame=True,
                     playerSame=True,saveSame=True),guards
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  for selector in ('#bf6400-remedies summary','#bf6400-item',
                   '#bf6400-actor','#bf6400-target','#bf6400-use'):
   assert p.locator(selector).evaluate('(e)=>e.getBoundingClientRect().height')>=44,(width,selector)
  assert p.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),width
 p.set_viewport_size({'width':390,'height':844})
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(0,0,99999)') is False
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(0,0,20210)') is False
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(2,0,20200)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[5]
 assert p.evaluate('S.party[2].action.kind')=='guard'
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(2,0,20220)') is False
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(3,0,20220)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[]
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(4,1,20210)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(1)')==[]
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().stock.filter(x=>x.remaining===0).length')==3
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is True
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(5,0,20200)') is False
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(5,0,50200)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[]
 assert p.evaluate('S.party[5].action.kind')=='guard'
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),p:JSON.stringify(P),
 hp:S.party.map(p=>p.hp),bb:S.party.map(p=>p.bb),stats:S.party.map(p=>[p.atk,p.def])})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().available') is False
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.useRemedy(1,0,50200)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().stock.every(x=>x.remaining===1)') is True
 assert p.evaluate('BFGlobalStatusRemedyCommandV6400.snapshot().available') is False
 old=p.evaluate('window.BFGlobalStatusRemedyCommandV6400')
 p.add_script_tag(path=str(A/'bf6400_status_remedy_command.js'))
 assert p.locator('#bf6400-remedies').count()==1
 assert not errors,errors
 b.close()
print('PASS v64 original remedy item codes, interactive DEMO Guard cost, isolated stock, no save changes')
