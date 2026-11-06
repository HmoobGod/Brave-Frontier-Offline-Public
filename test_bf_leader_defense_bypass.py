"""Source-qualified Mifune DEF component on actual single-hit normal turns."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
catalog=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text())
raw=next(x for x in catalog['rows'] if x['unitId']==60025)
assert (raw['leaderSkillId'],raw['skillTypeRaw'],raw['passiveSkillInfoRaw'])==(1314,'31@29','50,0,0,0,0,0@15')
english=json.loads((R/'source_data/bf_global_2022_playable_leader_english_v114.json').read_text())
assert next(x for x in english['records'] if x['leaderSkillId']==1314)['originalEnglishName']=="Ruin God's Epidemic"
js=(A/'bf_leader_defense_bypass.js').read_text();assert len(js.encode())<12000
assert not any(x in js for x in ('saveProgress(', 'localStorage', 'BFAndroid', 'fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf11400_original_global_leader_english.js")') < java.index('readPackagedText("bf_leader_defense_bypass.js")')
tree=ast.parse((R/'test_bf_paralysis_action_lock_v6000.py').read_text())
base=next(ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.Tuple) and n.elts and isinstance(n.elts[0],ast.Constant) and n.elts[0].value=='bf_home_nav.js')
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
    p=b.new_page();errors=[];p.on('pageerror',lambda error:errors.append(str(error)))
    p.route('**/*',lambda route:route.abort());p.evaluate(INSTALL_STORAGE)
    p.evaluate('''()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();
      HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}''')
    p.set_content((A/'index.html').read_text());p.add_style_tag(path=str(A/'bf_home_nav.css'))
    for name in base:p.add_script_tag(path=str(A/name))
    for name in ('bf6100_weakness_defense.js','bf6200_injury_attack.js',
                 'bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js','bf9300_single_hit_critical_combat.js',
                 'bf9500_multihit_critical_combat.js','bf11000_source_starter_leader_skills.js',
                 'bf11200_all_playable_leader_source.js','bf11400_original_global_leader_english.js'):
        p.add_script_tag(path=str(A/name))
    p.evaluate('()=>{window.__defPriorPerform=performUnit;window.__defPriorDamage=prototypeDamage}')
    p.add_script_tag(path=str(A/'bf_leader_defense_bypass.js'))
    p.evaluate('()=>{window.__defWrapped=performUnit}')
    p.add_script_tag(path=str(A/'bf_leader_defense_bypass.js'))
    assert p.evaluate('__defWrapped===performUnit')
    api='BFGlobalLeaderDefenseBypass'
    for value,expected in ((0,True),(0.149999,True),(0.15,False),(0.95,False)):
        assert p.evaluate('r=>BFGlobalLeaderDefenseBypass.roll(()=>r)',value) is expected
    assert p.evaluate(api+'.roll(()=>NaN)') is None
    p.locator('.bf-navbar [data-bf-goto="quest"]').click()
    p.evaluate('window.__defStart=JSON.stringify(S)')
    cases=[
      ('ordinary',1000,.95,60025,'attack',40011,False,False),
      ('proc',1000,.149999,60025,'attack',40011,False,False),
      ('zero-def',0,.149999,60025,'attack',40011,False,False),
      ('boundary',1000,.15,60025,'attack',40011,False,False),
      ('wrong-leader',1000,.149999,60024,'attack',40011,False,False),
      ('proc-critical',1000,0,60025,'attack',40011,False,False),
      ('zero-critical',0,0,60025,'attack',40011,False,False),
      ('injured-proc',1000,.149999,60025,'attack',40011,True,False),
      ('injured-zero',0,.149999,60025,'attack',40011,True,False),
      ('multi',1000,.149999,60025,'attack',10011,False,False),
      ('multi-control',1000,.149999,60024,'attack',10011,False,False),
      ('bb',1000,.149999,60025,'burst',40011,False,False),
      ('bb-control',1000,.149999,60024,'burst',40011,False,False),
      ('guard',1000,.149999,60025,'guard',40011,False,False),
      ('guard-control',1000,.149999,60024,'guard',40011,False,False),
      ('auto',1000,.149999,60025,'attack',40011,False,True),
      ('auto-zero',0,.149999,60025,'attack',40011,False,True),
    ]
    results={}
    for label,defense,random,form,kind,unit,injury,auto in cases:
        p.evaluate('''({defense,form,unit,kind})=>{
          S=JSON.parse(__defStart);if(!P.roster.includes(60021))P.roster.push(60021);
          P.squad[0]=60021;P.evolutions[60021]=form;
          for(const u of S.party){u.active=u.id<2;u.action=null;u.hp=20000;u.maxHp=20000;u.bb=0;u.atkBuff=null;u.def=500}
          Object.assign(S.party[0],{baseId:60021,unitId:form,atk:1});
          Object.assign(S.party[1],{unitId:unit,atk:1000,bb:kind==='burst'?100:0});
          S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,atk:1,def:defense}];
          S.selected=0;S.target=0;seed=771;document.getElementById('speed').value='4';update();
        }''',{'defense':defense,'form':form,'unit':unit,'kind':kind})
        if injury:assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,4)')
        if not auto:
            p.locator('#guard').click();p.locator('#'+{'attack':'attack','burst':'burst','guard':'guard'}[kind]).click()
        before=p.evaluate(SNAPSHOT)
        p.evaluate('''async({random,auto})=>{
          const old=Math.random,original=execute;Math.random=()=>random;
          try{if(!auto)await BF_debug.execute();
            else await new Promise((resolve,reject)=>{
              execute=async function(...args){
                try{const result=await original.apply(this,args);resolve(result);return result}
                catch(error){reject(error);throw error}
                finally{S.auto=false;if(timer){clearTimeout(timer);timer=null}execute=original}
              };S.auto=true;scheduleAuto();
            });
          }finally{Math.random=old;execute=original}
        }''',{'random':random,'auto':auto})
        one=p.evaluate('BFGlobalSingleHitCriticalV9300.snapshot().recent.filter(e=>e.slot===1)')
        own_damage=one[0]['observedHpLoss'] if one else 100000-p.evaluate('S.enemies[0].hp')
        results[label]={'damage':own_damage,'hp':p.evaluate('S.party.map(u=>u.hp)')}
        assert p.evaluate('S.enemies[0].def')==defense
        assert p.evaluate('S.party[1].atk')==1000
        if kind=='attack' and unit==40011:assert len(one)==1
        if kind in ('burst','guard'):assert not one
        assert_unchanged(p,before,label)
        print('PASS DEF component',label,own_damage,'enemy DEF and P/storage intact',flush=True)
    assert results['proc']['damage']==results['zero-def']['damage']>results['ordinary']['damage']
    assert results['boundary']['damage']==results['wrong-leader']['damage']==results['ordinary']['damage']
    assert results['proc-critical']['damage']==results['zero-critical']['damage']>results['proc']['damage']
    assert results['injured-proc']['damage']==results['injured-zero']['damage']<results['proc']['damage']
    assert results['multi']['damage']==results['multi-control']['damage']
    assert results['bb']['damage']==results['bb-control']['damage']
    assert results['guard']==results['guard-control'] and results['guard']['damage']==0
    assert results['auto']['damage']==results['auto-zero']['damage']
    # A later unrelated damage call must not inherit the action's bypass context.
    assert p.evaluate('''()=>{seed=771;const a=prototypeDamage(1000,1000);seed=771;
      return a===__defPriorDamage(1000,1000)}''')
    before=p.evaluate(SNAPSHOT)
    p.evaluate('window.__defRoster=P.roster;P.roster=P.roster.filter(id=>id!==60021)')
    assert p.evaluate(api+'.leader()') is None
    p.evaluate('P.roster=__defRoster')
    p.evaluate("S.mode='training'")
    assert p.evaluate(api+'.leader()') is None
    p.evaluate("S.mode='archive';S.party[0].unitId=60024")
    assert p.evaluate(api+'.leader()') is None
    p.evaluate('S.party[0].unitId=60025')
    assert_unchanged(p,before,'ownership/mode/form controls')
    assert not errors,errors;b.close()
print('PASS 17 actual manual/Auto turns, sourced15% boundary, exclusions and no context/save leak')
