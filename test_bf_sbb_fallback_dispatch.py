"""Invalid queued experimental SBB uses the full normal pipeline exactly once."""
from pathlib import Path
import ast
import shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf9500_multihit_critical_combat.js")') < java.index('readPackagedText("bf_sbb_fallback_dispatch.js")')
tree=ast.parse((R/'test_bf_paralysis_action_lock_v6000.py').read_text())
base=next(ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.Tuple)
          and n.elts and isinstance(n.elts[0],ast.Constant) and n.elts[0].value=='bf_home_nav.js')
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
    page=browser.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('**/*',lambda route:route.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();
      HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}''')
    page.set_content((A/'index.html').read_text())
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    for name in base:page.add_script_tag(path=str(A/name))
    for name in ('bf6100_weakness_defense.js','bf6200_injury_attack.js',
                 'bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js',
                 'bf9300_single_hit_critical_combat.js','bf9500_multihit_critical_combat.js',
                 'bf_sbb_fallback_dispatch.js'):
        page.add_script_tag(path=str(A/name))
    assert page.evaluate('!!BFGlobalInjuryAttackV6200 && !!BFGlobalSBBFallbackDispatch')
    page.evaluate('()=>{window.__fallbackPerform=performUnit}')
    page.add_script_tag(path=str(A/'bf_sbb_fallback_dispatch.js'))
    assert page.evaluate('__fallbackPerform===performUnit')
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('window.__fallbackStart=JSON.stringify(S)')
    def setup(injured,buff):
        page.evaluate('''buff=>{S=JSON.parse(__fallbackStart);
          for(const u of S.party){u.active=u.id===0;u.action=null;u.hp=1000;u.maxHp=1000;u.bb=100}
          Object.assign(S.party[0],{unitId:10015,atk:1000,
            atkBuff:buff?{pct:buff,untilRound:S.round+2}:null});
          S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:100,atk:1}];
          S.selected=0;S.target=0;seed=771;document.getElementById('speed').value='4';
          document.getElementById('bf044-enable').checked=true;update();BF044SBBDemo.refresh();
        }''',buff)
        if injured:assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)')
    def queue_sbb():
        page.locator('#bf044-queue').evaluate("el=>{for(let p=el;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}")
        page.locator('#bf044-queue').click()
        assert page.evaluate('S.party[0].action.kind')=='sbb_demo'
    def execute():
        page.evaluate('''async()=>{const old=Math.random;Math.random=()=>0.95;
          try{await BF_debug.execute()}finally{Math.random=old}}''')
    for injured in (False,True):
        for buff in (0,50,100):
            reference=None;low_gauge_reference=None
            for mode in ('normal','normal-low-gauge','disabled','low-gauge','missing-source'):
                setup(injured,buff)
                if mode in ('normal','normal-low-gauge'):
                    if mode=='normal-low-gauge':page.evaluate('S.party[0].bb=20')
                    page.locator('#attack').click()
                else:
                    queue_sbb()
                    if mode=='disabled':page.evaluate("document.getElementById('bf044-enable').checked=false")
                    elif mode=='low-gauge':page.evaluate('S.party[0].bb=20')
                    else:page.evaluate('S.party[0].unitId=10011')
                before=page.evaluate(SNAPSHOT);execute()
                damage=100000-page.evaluate('S.enemies[0].hp')
                if mode=='normal':reference=damage
                assert damage==reference and damage>0,(injured,buff,mode,damage,reference)
                assert page.evaluate('S.party[0].atk')==1000
                gauge=page.evaluate('S.party[0].bb')
                if mode=='normal-low-gauge':low_gauge_reference=gauge
                assert gauge==(low_gauge_reference if mode in ('normal-low-gauge','low-gauge') else 100),(mode,gauge)
                events=page.evaluate('BFGlobalMultiHitCriticalV9500.snapshot().recent')
                assert len(events)==1 and events[0]['observedHpLoss']==damage,events
                assert len(page.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().recent'))==1
                assert_unchanged(page,before,(injured,buff,mode))
                print('PASS SBB fallback',injured,buff,mode,'damage',damage,'one normal path, P/storage intact',flush=True)
    setup(True,100);queue_sbb();before=page.evaluate(SNAPSHOT);execute()
    assert page.evaluate('S.party[0].bb')==0 and page.evaluate('S.enemies[0].hp')<100000
    assert page.evaluate('BFGlobalMultiHitCriticalV9500.snapshot().recent')==[]
    assert page.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().recent')==[]
    assert page.evaluate('S.party[0].atk')==1000
    assert_unchanged(page,before,'valid enabled SBB control')
    assert not errors,errors
    browser.close()
print('PASS enabled SBB unchanged, optional wrapper idempotent; no native SBB/save changes')
