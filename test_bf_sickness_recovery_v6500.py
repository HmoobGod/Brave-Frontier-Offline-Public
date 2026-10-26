"""v65 Sickness -50% REC in DEMO action scope, selective expiry, cure and reinfliction."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf6500_sickness_recovery.js').read_text('utf8')
assert 'BF_GLOBAL_SICKNESS_RECOVERY_V6500' in script
assert len(script.encode('utf8'))<65536
assert all(x not in script for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6400_status_remedy_command.js")')<java.index('readPackagedText("bf6500_sickness_recovery.js")')
tree=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
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
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 st=p.evaluate('BFGlobalSicknessRecoveryV6500.snapshot()')
 assert st['performHooked'] and st['enemyHooked']
 assert st['source']['statusCode']==3 and st['source']['penaltyPercent']==50
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.labels[3]')=='Sickness'
 assert st['sickSlots']==[]
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P),
 hp:S.party.map(p=>p.hp),rec:S.party.map(p=>p.rec)})""")
 recs=before['rec']
 assert all(isinstance(n,(int,float)) and n>=0 for n in recs)
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,3)') is True
 token=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,3)')
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.sick(0)') is True
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.effectiveRecovery(0)')==(recs[0]+1)//2
 result=p.evaluate("""async()=>BFGlobalSicknessRecoveryV6500.withSicknessRecovery(
 async()=>({sick:S.party[0].rec,unaffected:S.party[1].rec}))""")
 assert result=={'sick':(recs[0]+1)//2,'unaffected':recs[1]}
 assert p.evaluate('S.party.map(p=>p.rec)')==recs
 assert p.evaluate("""async()=>{
 try{await BFGlobalSicknessRecoveryV6500.withSicknessRecovery(async()=>{
 throw Error('sickness-test')})}catch(e){return e.message==='sickness-test'}
 return false}""") is True
 assert p.evaluate('S.party.map(p=>p.rec)')==recs
 # Sickness and Injury affect separate stats without changing permanent REC.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,2)') is True
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.expireAfterTurn()')==[0]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2,4]
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.effectiveRecovery(0)')==recs[0]
 # Reinfliction has a new generation and full lifespan.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,3)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,3)')!=token
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20210).removed')==[2,3,4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[]
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.effectiveRecovery(0)')==recs[0]
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),P:JSON.stringify(P),
 hp:S.party.map(p=>p.hp),rec:S.party.map(p=>p.rec)})""")
 assert before==after,(before,after)
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,3)') is True
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.snapshot().sickSlots')==[]
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.effectiveRecovery(1)')==recs[1]
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalSicknessRecoveryV6500.snapshot().sickSlots')==[]
 p.evaluate('()=>{window.__bf65prior=window.performUnit;return true}')
 p.add_script_tag(path=str(A/'bf6500_sickness_recovery.js'))
 assert p.evaluate('window.__bf65prior===window.performUnit') is True
 assert not errors,errors
 b.close()
print('PASS v65 Sickness -50% REC status scope, independent duration, cure/reinfliction, no save mutation')
