"""v69 original Global element circle & isolated live DEMO damage application."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6900_elemental_combat.js').read_text('utf8')
html=(A/'index.html').read_text('utf8')
assert js.count('/* BF_GLOBAL_ELEMENTAL_COMBAT_V6900 */')==1
assert len(js.encode('utf8'))<65536
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
assert 'UNIT_BY_ID.get(p.unitId)?.element,foe.element' in html
assert 'enemy.element,UNIT_BY_ID.get(target.unitId)?.element' in html
assert html.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf6700_burst_recipient_rec.js")')<java.index('readPackagedText("bf6900_elemental_combat.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content(html,wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 m='BFGlobalElementalCombatV6900.multiplier'
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalElementalCombatV6900.source.advantage')==1.5
 for a,d in [('Fire','Earth'),('Earth','Thunder'),('Thunder','Water'),('Water','Fire'),('Light','Dark'),('Dark','Light')]:
  assert p.evaluate(f"{m}('{a}','{d}')")==1.5,(a,d)
 for a,d in [('Earth','Fire'),('Thunder','Earth'),('Water','Thunder'),('Fire','Water')]:
  assert p.evaluate(f"{m}('{a}','{d}')")==.5,(a,d)
 for a,d in [('Fire','Fire'),('Water','Earth'),('Light','Light'),('Light','Fire'),
             ('Fire',None),(None,'Dark')]:
  arg=lambda v: 'null' if v is None else "'"+v+"'"
  assert p.evaluate(f'{m}({arg(a)},{arg(d)})')==1,(a,d)
 assert p.evaluate("BFGlobalElementalCombatV6900.normalize(' WATER ')")=='Water'
 assert p.evaluate("BFGlobalElementalCombatV6900.normalize('Unknown')") is None
 before=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 # Existing core's original starter has source Fire element; DEMO enemies are
 # unknown by default and receive no inferred original element.
 assert p.evaluate("UNIT_BY_ID.get(10011).element")=='Fire'
 p.locator('#mode').select_option('training')
 assert p.evaluate(f"{m}('Fire','Earth')")==1
 p.locator('#mode').select_option('archive')
 assert p.evaluate(f"{m}('Fire','Earth')")==1.5
 def damage(enemy_element,has_module=True):
  p.locator('#reset').click()
  p.evaluate("""(el)=>{const foe=S.enemies[0];
    S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;});
    foe.hp=20000;foe.maxHp=20000;foe.def=0;foe.atk=0;
    if(el===null)delete foe.element;else foe.element=el;
    S.party[0].unitId=10011;S.party[0].atk=800;S.party[0].bb=0;
    S.party[0].action={kind:'attack',target:0};
    for(let i=1;i<S.party.length;i++)
      if(S.party[i].active&&S.party[i].hp>0)
        S.party[i].action={kind:'guard',target:0};
    S.target=0;
    document.getElementById('speed').value='4';
  }""",enemy_element)
  p.evaluate('BF_debug.execute()')
  return 20000-p.evaluate('S.enemies[0].hp')
 neutral=damage(None)
 strong=damage('Earth')
 weak=damage('Water')
 assert 450<=neutral<=550,('neutral normal hit',neutral)
 assert 680<=strong<=840,('advantaged normal hit',strong)
 assert 220<=weak<=300,('disadvantaged normal hit',weak)
 assert strong>neutral>weak,(strong,neutral,weak)
 # Missing optional extension must preserve exact neutral core calculation.
 p.evaluate('delete window.BFGlobalElementalCombatV6900')
 fallback=damage('Earth')
 assert 450<=fallback<=550,('module removal failed neutral fallback',fallback)
 p.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 after=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 p.evaluate('window.__bf68prior=window.BFGlobalElementalCombatV6900')
 p.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 assert p.evaluate('window.__bf68prior===window.BFGlobalElementalCombatV6900')
 assert not errors,errors
 b.close()
print('PASS v69 source-verified six-element matchup, opponent-sensitive DEMO damage, strict fallback, no save changes')
