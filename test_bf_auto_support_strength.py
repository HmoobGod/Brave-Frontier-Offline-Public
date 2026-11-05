"""Smart Auto's support decisions use the same verified BB strength as combat."""
from pathlib import Path
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
if '--source-only' in sys.argv:
    smart=(ROOT/'prepare_source_aware_auto_v041.py').read_text()
    coordinated=(ROOT/'prepare_coordinated_auto_v042.py').read_text()
    assert 'BFGlobalOriginalAtkBBLevelsV7100?.boostFor(unitId)' in smart
    assert 'BFGlobalOriginalAtkBBLevelsV7100?.boostFor(Number(p.unitId))' in coordinated
    assert 'python3 test_bf_auto_support_strength.py' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    print('PASS source: Smart Auto decisions and coordination use existing verified ATK BB levels')
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':393,'height':852})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('**/*',lambda route:route.abort())
    page.evaluate("""()=>{
      window.__strengthStorage=Object.create(null);window.__strengthWrites=0;
      const db=window.__strengthStorage;
      Object.defineProperty(window,'localStorage',{value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{window.__strengthWrites++;db[k]=String(v)},
        removeItem:k=>{window.__strengthWrites++;delete db[k]},
        clear:()=>{window.__strengthWrites++;Object.keys(db).forEach(k=>delete db[k])},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>false;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
    for name in ('bf6700_burst_recipient_rec.js','bf6800_original_heal_bb_levels.js',
                 'bf6900_elemental_combat.js','bf7100_original_atk_bb_levels.js',
                 'bf10500_qol_advanced_smart_auto.js'):
        page.add_script_tag(path=str(A/name))
    page.evaluate("""()=>{
      document.getElementById('bf041-smart-auto').checked=true;
      S.party[0].unitId=40021;
      for(const p of S.party){p.hp=p.maxHp;p.bb=0;p.atkBuff={pct:35,untilRound:S.round+2};p.action=null;}
      S.party[0].bb=100;
      S.enemies=[{...S.enemies[0],hp:100000,maxHp:100000,def:100}];
    }""")
    state='()=>JSON.stringify({player:P,storage:window.__strengthStorage,writes:window.__strengthWrites})'
    before=page.evaluate(state)
    assert page.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(10)')
    assert page.evaluate('BFGlobalOriginalAtkBBLevelsV7100.boostFor(40021)')==40
    decision=page.evaluate('BF041SmartAuto.kindFor(S.party[0])')
    assert decision=='burst',('Auto ignored usable verified Lv10 buff',decision)
    page.evaluate("async()=>{S.party[0].action={kind:BF041SmartAuto.kindFor(S.party[0]),target:0};await performUnit(S.party[0],epoch)}")
    assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>currentAtkBoost(p)===40)')
    assert page.evaluate('S.party[0].bb')==0
    assert page.evaluate(state)==before
    # Actual Lv10 #40022 and fixed #40023 both give +50%; prefer earlier slot.
    page.evaluate("""()=>{
      S.party[0].unitId=40022;S.party[1].unitId=40023;
      for(const p of S.party){p.atkBuff=null;p.action=null;}
      S.party[0].bb=S.party[1].bb=100;
    }""")
    kinds='()=>{const plan=BF042AutoCoordination.plan(liveParty());return [plan.get(S.party[0]),plan.get(S.party[1])]}'
    assert page.evaluate(kinds)==['burst','attack']
    page.evaluate("async()=>{S.party[0].action={kind:'burst',target:0};await performUnit(S.party[0],epoch)}")
    assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>currentAtkBoost(p)===50)')
    assert page.evaluate(state)==before
    # Lv1 and absent-preview fallback keep the original 40 versus 50 priority.
    page.evaluate('for(const p of S.party){p.atkBuff=null;p.action=null;}S.party[0].bb=100')
    assert page.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(1)')
    assert page.evaluate(kinds)==['attack','burst']
    page.evaluate('window.__heldLevels=BFGlobalOriginalAtkBBLevelsV7100;delete window.BFGlobalOriginalAtkBBLevelsV7100')
    assert page.evaluate(kinds)==['attack','burst']
    page.evaluate('window.BFGlobalOriginalAtkBBLevelsV7100=window.__heldLevels')
    assert page.evaluate(state)==before
    # Advanced Auto delegates ATK decisions to the same corrected baseline.
    assert page.evaluate('BFGlobalQoLAdvancedAutoV10500.set({on:true,heal:60,target:"percent",burst:"normal"})')
    # Preference setup deliberately writes only the isolated QoL fixture key.
    advanced_before=page.evaluate(state)
    setup=json.loads(advanced_before);initial=json.loads(before)
    assert setup['player']==initial['player']
    assert setup['writes']==initial['writes']+1
    pref='bf_global_offline_qol_advanced_auto_v105'
    assert {k:v for k,v in setup['storage'].items() if k!=pref}=={k:v for k,v in initial['storage'].items() if k!=pref}
    page.evaluate('S.party[0].unitId=40021;S.party[1].bb=0;for(const p of S.party)p.atkBuff={pct:35,untilRound:S.round+2}')
    assert page.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(10)')
    assert page.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
    assert page.evaluate('BFGlobalOriginalHealBBLevelsV6800.selectLevel(1)')
    assert page.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='attack'
    page.evaluate("document.getElementById('bf041-smart-auto').checked=false")
    assert page.evaluate('BF042AutoCoordination.plan(liveParty())') is None
    assert page.evaluate(state)==advanced_before
    assert not errors,errors
    print('PASS actual Lv10 support upgrades/ties, Lv1/absent fallback, Advanced Auto and progress isolation',flush=True)
    browser.close()
