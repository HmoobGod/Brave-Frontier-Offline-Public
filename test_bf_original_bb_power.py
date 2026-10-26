'''v0.30 original 2022 Global offensive BB Lv1 modifier regression.'''
from pathlib import Path
import json, shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'source_data/bf_global_original_bb_power_v030.json').read_text())
TARG=json.loads((ROOT/'source_data/bf_global_original_bb_targeting.json').read_text())['targets']
assert len(DATA['skills'])==24
assert all(len(v['levels'])==10 for v in DATA['skills'].values())
assert sum(TARG[u]['target']=='all_enemies' for u in DATA['skills'])==19
assert sum(TARG[u]['target']=='single_enemy' for u in DATA['skills'])==5
assert [DATA['skills'][i]['levels'][0]['damageModifierPct'] for i in ['10011','10021','30022','50022']]==[30,150,50,70]
html=(ROOT/'app/src/main/assets/index.html').read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_POWER_V030 */')==1
assert 'prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst))' in html
print('PASS 24 offensive BBs and source Lv1-10 records',flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or shutil.which('chromium'),
                               args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=60000)
    result=page.evaluate('''()=>{
       const ids=[10011,10021,30022,50022];
       return {count:BFOriginalBBPower.count,values:ids.map(id=>BFOriginalBBPower.multiplierFor(id)),
         first:BFOriginalBBPower.levelsFor(10011),support:BFOriginalBBPower.forUnit(40021),
         normal:bbDamageMultiplier({unitId:10011},false),save:SAVE_KEY};
    }''')
    assert result['values']==[1.3,2.5,1.5,1.7] and result['count']==24,result
    assert result['first']==[30,35,40,45,50,55,60,65,70,75],result
    assert result['support'] is None and result['normal']==1 and result['save']=='bf_global_offline_demo_v7',result
    print('PASS original BB Lv1 multipliers and unmodified normal attack',flush=True)
    for unit_id in [10011,10021,30022,50022]:
        out=page.evaluate('''async ({id})=>{
          BF_debug.reset();wait=()=>Promise.resolve();
          S.enemies=[{slot:0,id:'gel',name:'Dummy',hp:999999,maxHp:999999,atk:100,def:20}];
          const unit=S.party[0];unit.unitId=id;unit.bb=100;unit.action={kind:'burst',target:0};
          const prior=JSON.stringify(P),baseAtk=unit.atk;
          seed=771;
          const predicted=prototypeDamage(effectivePlayerAtk(unit),20,bbDamageMultiplier(unit,true));
          seed=771;await performUnit(unit,epoch);
          return {predicted,actual:999999-S.enemies[0].hp,bb:unit.bb,baseAtk,
            afterAtk:unit.atk,save:prior===JSON.stringify(P),log:E.log.textContent};
        }''',{'id':unit_id})
        assert out['actual']==out['predicted'] and out['actual']>0,(unit_id,out)
        assert out['bb']==0 and out['afterAtk']==out['baseAtk'] and out['save'],(unit_id,out)
        assert 'original BB Lv1 +' in out['log'],(unit_id,out)
    print('PASS actual offensive BB damage matches archived Lv1 modifiers for 1500/1800/2000',flush=True)
    out=page.evaluate('''async ()=>{
        BF_debug.reset();wait=()=>Promise.resolve();
        const p=S.party[0];p.unitId=10011;p.bb=0;p.action={kind:'attack',target:0};
        S.enemies=[{slot:0,id:'gel',name:'Enemy',hp:999999,maxHp:999999,def:20,atk:100}];
        seed=771;const predicted=prototypeDamage(effectivePlayerAtk(p),20,1);
        seed=771;await performUnit(p,epoch);
        return {predicted,actual:999999-S.enemies[0].hp,bb:p.bb,
          support:BFOriginalSupportEffects.forUnit(40021).pct,targets:BFOriginalBBTargets.count};
    }''')
    assert out['actual']==out['predicted'] and out['bb']==34,out
    assert out['support']==30 and out['targets']==30 and not errors,(out,errors)
    print('PASS normal attacks, BB gauge, 30 target scopes and v0.29 support unaffected',flush=True)
    nav=(ROOT/'app/src/main/assets/bf_home_nav.js').read_text('utf-8')
    archive=(ROOT/'app/src/main/assets/bf_global_unit_archive.js').read_text('utf-8')
    assert len(nav.encode())<=65536 and len(archive.encode())<=65536
    page.evaluate(nav)
    page.evaluate(archive)
    assert page.evaluate('BFGlobalUnitArchive.count')==2291
    assert page.evaluate('BFGlobalUnitArchive.showDetail(10011)')
    panel=page.locator('.bf-codex-bb-levels')
    assert panel.count()==1
    panel.evaluate('(node)=>node.open=true')
    labels=panel.locator('.bf-codex-bb-power-grid span').all_text_contents()
    assert labels[0]=='Lv1 · +30%' and labels[-1]=='Lv10 · +75%',labels
    assert page.evaluate('BFGlobalUnitArchive.showDetail(40021)')
    assert page.locator('.bf-codex-bb-levels').count()==0
    assert not errors,errors
    print('PASS archived skill details list all original levels with no fabricated support modifiers',flush=True)
    browser.close()
