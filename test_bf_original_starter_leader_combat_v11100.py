"""v111 original starter leader skills: source % applied once to archive DEMO party.

Pin exact SHA-256 of 4.47 MB original core HTML, ensuring playerUnit/reset
construction code has not drifted without a new audit. Preserve v7 saves.
"""
from pathlib import Path
import hashlib,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
core=(A/'index.html').read_bytes()
assert hashlib.sha256(core).hexdigest()=='82e81c853362342a753714b2569faa48e1d1fec7ac4c4676fdb419acd077a0f0'
js=(A/'bf11100_original_starter_leader_combat.js').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_STARTER_LEADER_COMBAT_V11100')==1
assert len(js.encode('utf8'))<65536
assert 'const original=window.playerUnit' in js
assert "mode.value!=='archive'" in js
assert 'nativeDamageAndRoundingNotFullyRecovered:true' in js
assert not any(x in js for x in ('localStorage','saveProgress(', 'P.squad=', 'P.evolutions=', 'S.party=',
    'window.reset=', 'Math.random', 'awardDemoRewards(', 'fetch(', 'XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11000_source_starter_leader_skills.js")')<java.index('readPackagedText("bf11100_original_starter_leader_combat.js")')
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
   HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 p.set_content(core.decode('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('typeof window.playerUnit')=='function'
 assert p.evaluate('typeof window.reset')=='function'
 old=p.evaluate("""()=>S.party.map(u=>({atk:u.atk,hp:u.maxHp,id:u.unitId}))""")
 assert len(old)==6 and old[0]['id']==10011
 before=p.evaluate("""()=>({P:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 assert p.evaluate('BFGlobalStarterLeaderSourceV11000.lookup(10011).atkPercent')==25
 p.add_script_tag(path=str(A/'bf11100_original_starter_leader_combat.js'))
 assert p.evaluate('!!window.BFGlobalStarterLeaderCombatV11100')
 assert p.locator('#bf11100-leader-combat').count()==1
 p.evaluate('reset()')
 first=p.evaluate('S.party.map(u=>({atk:u.atk,hp:u.maxHp,id:u.unitId}))')
 assert first[0]['atk']==old[0]['atk']*125//100,(old,first)
 assert first[0]['hp']==old[0]['hp']
 assert first[1:]==old[1:]
 snap=p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot()')
 assert snap['appliedPartyUnits']==1 and snap['rows'][0]['leaderId']==10011
 assert snap['saveFieldsAdded']==0 and snap['baseStatsAndDamageFormulaStillDemo']
 p.evaluate('reset()')
 assert p.evaluate('S.party.map(u=>({atk:u.atk,hp:u.maxHp,id:u.unitId}))')==first
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().appliedPartyUnits')==1
 p.evaluate('BFGlobalStarterLeaderCombatV11100.apply(S.party[0],0)')
 assert p.evaluate('S.party[0].atk')==first[0]['atk']
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.fromSource(10011,20011)') is None
 p.evaluate('P.evolutions[10011]=10015;reset()')
 final=p.evaluate('S.party[0]')
 expected=p.evaluate("""()=>{const src=effectiveUnit(10011),grow=demoLevel(P.unitExp[10011])-1;
    return {id:src.id,atk:src.stats.atk+grow*12,hp:src.stats.hp+grow*30}}""")
 assert final['unitId']==expected['id']==10015
 assert final['atk']==expected['atk']*150//100,(final,expected)
 assert final['maxHp']==final['hp']==expected['hp']*110//100,(final,expected)
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().rows[0].hpPercent')==10
 p.evaluate('document.getElementById("mode").value="training";reset()')
 training=p.evaluate('S.party[0]')
 assert training['atk']==expected['atk']
 assert training['maxHp']==training['hp']==expected['hp']
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().appliedPartyUnits')==0
 p.evaluate('delete P.evolutions[10011];P.squad=[20011,10011,30011,40011,50011,60011];document.getElementById("mode").value="archive";reset()')
 rotated=p.evaluate('S.party.map(u=>({atk:u.atk,hp:u.maxHp,id:u.unitId}))')
 assert rotated[0]['atk']==old[1]['atk']*125//100
 assert rotated[1]['atk']==old[0]['atk']
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().appliedPartyUnits')==1
 p.evaluate('P.squad=[10011,20011,30011,40011,50011,60011];reset()')
 assert p.evaluate('S.party.map(u=>({atk:u.atk,hp:u.maxHp,id:u.unitId}))')==first
 after=p.evaluate("""()=>({P:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 p.locator('#bf11100-leader-combat > summary').click()
 p.wait_for_function("document.querySelector('#bf11100-rows').children.length===1")
 assert 'ATK' in p.locator('#bf11100-rows').inner_text()
 p.add_script_tag(path=str(A/'bf11100_original_starter_leader_combat.js'))
 assert p.locator('#bf11100-leader-combat').count()==1
 assert not errors,errors
 b.close()
print('PASS v111 source-qualified starter leader % once per archive DEMO squad; training, saves, resets unchanged')
