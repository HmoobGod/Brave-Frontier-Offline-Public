"""Intense Edge critical component on actual normal attacks; synthetic saves only."""
from pathlib import Path
import ast
import json
import shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

R = Path(__file__).resolve().parent
A = R / 'app/src/main/assets'
catalog = json.loads((R / 'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text())
raw = next(r for r in catalog['rows'] if r['unitId'] == 10025)
assert (raw['leaderSkillId'], raw['skillTypeRaw'], raw['passiveSkillInfoRaw']) == (
    1313, '31@34', '50,0,0,0,0,0@0.5')
english = json.loads((R / 'source_data/bf_global_2022_playable_leader_english_v114.json').read_text())
text = next(r for r in english['records'] if r['leaderSkillId'] == 1313)
assert text['originalEnglishName'] == 'Intense Edge'
assert text['originalEnglishDescription'] == 'Huge boost to damage produced during Spark & slight boost to critical hit damage'
js = (A / 'bf_leader_critical_bonus.js').read_text()
assert len(js.encode()) < 12000
assert all(x not in js for x in ('localStorage', 'saveProgress(', 'BFAndroid', 'Math.random', 'fetch('))
java = (R / 'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf11400_original_global_leader_english.js")') < java.index('readPackagedText("bf_leader_critical_bonus.js")')

tree = ast.parse((R / 'test_bf_paralysis_action_lock_v6000.py').read_text())
base = next(ast.literal_eval(n) for n in ast.walk(tree)
            if isinstance(n, ast.Tuple) and n.elts
            and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == 'bf_home_nav.js')
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
                                shutil.which('google-chrome'), args=['--no-sandbox'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/*', lambda route: route.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();
      HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}''')
    page.set_content((A / 'index.html').read_text())
    page.add_style_tag(path=str(A / 'bf_home_nav.css'))
    for name in base:
        page.add_script_tag(path=str(A / name))
    for name in ('bf700_original_normal_hits.js', 'bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js', 'bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js', 'bf9300_single_hit_critical_combat.js',
                 'bf9500_multihit_critical_combat.js', 'bf10700_source_landed_crystal_eligibility.js',
                 'bf11000_source_starter_leader_skills.js',
                 'bf11200_all_playable_leader_source.js', 'bf11400_original_global_leader_english.js',
                 'bf_leader_critical_bonus.js','bf_sbb_fallback_dispatch.js'):
        page.add_script_tag(path=str(A / name))
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('window.__edgeBattle=JSON.stringify(S)')
    for unit in (40011, 10011):
        for form, random, action in ((10025, 0, 'attack'), (10024, 0, 'attack'),
                                     (10025, 0.95, 'attack'), (10025, 0, 'sbb_demo')):
            page.evaluate('''({unit,form})=>{
              S=JSON.parse(__edgeBattle);
              if(!P.roster.includes(10021))P.roster.push(10021);
              P.squad[0]=10021;P.evolutions[10021]=form;
              for(const u of S.party){u.active=u.id<2;u.action=null;u.hp=1000;u.maxHp=1000;u.bb=0}
              Object.assign(S.party[0],{baseId:10021,unitId:form});
              Object.assign(S.party[1],{unitId:unit,atk:1000});
              S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:0,atk:1}];
              S.target=0;S.selected=0;seed=771;document.getElementById('speed').value='4';update();
            }''', {'unit': unit, 'form': form})
            page.locator('#guard').click()
            page.locator('#attack').click()
            # A now-disabled queued SBB must enter the same normal critical chain.
            page.evaluate("kind=>{document.getElementById('bf044-enable').checked=false;S.party[1].action.kind=kind}", action)
            before = page.evaluate(SNAPSHOT)
            page.evaluate('''async random=>{const old=Math.random;Math.random=()=>random;
              try{await BF_debug.execute()}finally{Math.random=old}}''', random)
            events = page.evaluate('''BFGlobalSingleHitCriticalV9300.snapshot().recent
              .concat(BFGlobalMultiHitCriticalV9500.snapshot().recent).filter(e=>e.slot===1)''')
            assert len(events) == 1, events
            event = events[0]
            critical = random == 0
            multiplier = (2 if form == 10025 else 1.5) if critical else 1
            if unit == 40011:
                assert event['critical'] is critical
                assert event['resultDamage'] == int(event['baseDamage'] * multiplier), event
            else:
                assert event['rolls'] == 3 and event['criticals'] == (3 if critical else 0), event
                assert all(h['critical'] is critical and h['resultDamage'] == int(h['baseDamage'] * multiplier)
                           for h in event['hits']), event
            loss = 100000 - page.evaluate('S.enemies[0].hp')
            assert event['observedHpLoss'] == loss and loss > 0, event
            assert_unchanged(page, before, (unit, form, random))
            print('PASS actual Intense Edge normal/fallback turn', unit, form, random, action,
                  'multiplier', multiplier, 'P/storage intact', flush=True)

    # Restore the qualified fixture for isolated negative-eligibility controls.
    page.evaluate('''()=>{P.evolutions[10021]=10025;S.party[0].unitId=10025;
      S.party[1].action={kind:'attack',target:0};S.party[1].hp=1000}''')
    api = 'BFGlobalLeaderCriticalBonus'
    before = page.evaluate(SNAPSHOT)
    assert page.evaluate(api + '.scale(100,150,S.party[1],true)') == 200
    assert page.evaluate(api + '.scale(100,100,S.party[1],false)') == 100
    for change, undo in (
        ("S.mode='training'", "S.mode='archive'"),
        ('S.over=true', 'S.over=false'),
        ('S.party[1].hp=0', 'S.party[1].hp=1000'),
        ('S.party[1].active=false', 'S.party[1].active=true'),
        ("S.party[1].action.kind='burst'", "S.party[1].action.kind='attack'"),
        ('S.party[0].unitId=10024', 'S.party[0].unitId=10025'),
        ('P.evolutions[10021]=10024', 'P.evolutions[10021]=10025'),
    ):
        page.evaluate(change)
        assert page.evaluate(api + '.scale(100,150,S.party[1],true)') == 150, change
        page.evaluate(undo)
    assert page.evaluate(api + '.scale(100,150,{...S.party[1]},true)') == 150
    assert page.evaluate(api + '.scale(100,149,S.party[1],true)') == 149
    assert page.evaluate(api + '.scale(NaN,150,S.party[1],true)') == 150
    page.evaluate('window.__edgeRoster=P.roster;P.roster=P.roster.filter(id=>id!==10021)')
    assert page.evaluate(api + '.scale(100,150,S.party[1],true)') == 150
    page.evaluate('P.roster=__edgeRoster')
    # Existing leader policy persists through KO; do not invent leader removal.
    page.evaluate('S.party[0].hp=0')
    assert page.evaluate(api + '.scale(100,150,S.party[1],true)') == 200
    assert page.evaluate(api + '.source.sparkImplemented') is False
    assert_unchanged(page, before, 'eligibility controls')

    # One landed strike defeats this target; keep a second enemy alive so this
    # actual turn cannot clear a quest or award synthetic progress either.
    page.evaluate('''()=>{
      S=JSON.parse(__edgeBattle);
      for(const u of S.party){u.active=u.id<2;u.hp=1000;u.maxHp=1000;u.bb=0;u.action=null}
      Object.assign(S.party[0],{baseId:10021,unitId:10025,hp:0});
      Object.assign(S.party[1],{unitId:10011,atk:1000});
      const e={...S.enemies[0],atk:1,def:0};
      S.enemies=[{...e,slot:0,hp:1,maxHp:1},{...e,slot:1,hp:100000,maxHp:100000}];
      S.selected=1;S.target=0;seed=771;update();
    }''')
    page.locator('#attack').click()
    before = page.evaluate(SNAPSHOT)
    page.evaluate('''async()=>{const old=Math.random;window.__edgeRolls=0;
      Math.random=()=>{__edgeRolls++;return 0};
      try{await BF_debug.execute()}finally{Math.random=old}}''')
    event = page.evaluate('BFGlobalMultiHitCriticalV9500.snapshot().recent[0]')
    assert event['rolls'] == event['criticals'] == page.evaluate('__edgeRolls') == 1, event
    assert event['hits'][0]['resultDamage'] == event['hits'][0]['baseDamage'] * 2
    assert all(not h['landed'] and not h['critical'] for h in event['hits'][1:]), event
    assert event['observedHpLoss'] == 1 and page.evaluate('S.enemies[1].hp') == 100000
    audit = page.evaluate("BFGlobalLandedCrystalEligibilityV10700.audit(BFGlobalMultiHitCriticalV9500.snapshot().recent[0],'normal-multi')")
    assert audit['landedHits'] == audit['criticalHits'] == 1 and audit['skippedPostKO'] == 2, audit
    assert audit['referenceOnly'] and not audit['collected'], audit
    assert_unchanged(page, before, 'Intense Edge with KO leader and target')
    print('PASS Intense Edge multi-hit KO: one real critical roll, no phantom hits, P/storage intact')
    assert not errors, errors
    browser.close()
print('PASS Intense Edge source guards, normal-only critical scaling, negative controls; no Spark/save changes')
