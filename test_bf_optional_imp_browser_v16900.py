"""v169 end-to-end browser: original 2022 Imp caps, buttons, actual battle party lifecycle."""
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate('''()=>{
      const db={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
        removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }''')
    page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
    assert page.evaluate('P.version')==7
    # The v0.26 archive requires the routed Unit Box built by home_nav.
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    assert page.evaluate('!!window.BFUnitBox')
    page.add_script_tag(path=str(A/'bf_global_unit_archive.js'))
    assert page.evaluate('BFGlobalUnitArchive.count')==2291
    assert page.evaluate('BFGlobalUnitArchive.originalImpCaps(10011)')==[400,160,80,80]
    for name in ('bf11000_source_starter_leader_skills.js',
                 'bf11100_original_starter_leader_combat.js',
                 'bf11200_all_playable_leader_source.js',
                 'bf11500_original_unit_level_caps.js',
                 'bf11600_original_lord_stats_data.js',
                 'bf11600_original_lord_stats_reference.js',
                 'bf16800_original_level_one_lord_combat.js',
                 'bf16900_optional_imp_fusion.js'):
        page.add_script_tag(path=str(A/name))
    assert page.evaluate('!!window.BFGlobalOptionalImpsV16900')
    assert page.locator('#bf16900-imp-fusion').count()==1
    page.evaluate('''()=>{document.getElementById('mode').value='archive';
      P.squad=[10011];P.unitExp[10011]=0;reset();}''')
    before=page.evaluate('''()=>({
      p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })''')
    base=page.evaluate('S.party[0]')
    assert base['maxHp']==1030 and base['atk']==625,(base['maxHp'],base['atk'])
    assert page.evaluate('BFGlobalOptionalImpsV16900.snapshot().enabled') is False
    assert page.evaluate('BFGlobalOptionalImpsV16900.stock().arton')==0
    page.locator('#bf16900-imp-fusion').evaluate('(el)=>el.open=true')
    page.get_by_text('ENABLE OPTIONAL IMP FUSION',exact=False).first.evaluate('(el)=>el.click()')
    assert page.evaluate('BFGlobalOptionalImpsV16900.stock().arton')==5
    assert page.evaluate('BFGlobalOptionalImpsV16900.snapshot().mode')=='custom'
    assert page.evaluate('BFGlobalOptionalImpsV16900.maximum(10011).maximum')==[500,200,100,100]
    page.get_by_text('SMART BATCH FEED',exact=False).first.evaluate('(el)=>el.click()')
    assert page.evaluate('BFGlobalOptionalImpsV16900.stock().arton')==1
    assert page.evaluate('BFGlobalOptionalImpsV16900.bonus(10011)')==[500,200,100,100]
    assert page.evaluate('BFGlobalOptionalImpsV16900.feed(10011)') is False
    assert page.evaluate('BFGlobalOptionalImpsV16900.stock().arton')==1
    page.evaluate('reset()')
    new=page.evaluate('S.party[0]')
    assert new['maxHp']==new['hp']==1530,(new,base)
    assert new['atk']==875 and new['def']==510 and new['rec']==420,new
    assert page.evaluate('BFGlobalOptionalImpsV16900.snapshot().rows.length')==1
    page.evaluate('BFGlobalOptionalImpsV16900.apply(S.party[0],0)')
    assert page.evaluate('S.party[0].atk')==875
    # Original-cap mode clips excess, without erasing already fed Imps.
    page.locator('#bf16900-mode').select_option('original')
    page.evaluate('reset()')
    orig=page.evaluate('S.party[0]')
    assert orig['maxHp']==1430 and orig['atk']==825,(orig,new)
    assert page.evaluate('BFGlobalOptionalImpsV16900.bonus(10011)')==[500,200,100,100]
    page.locator('#bf16900-mode').select_option('custom')
    # Training never receives Imp stat modifications.
    page.evaluate('''()=>{document.getElementById('mode').value='training';reset();}''')
    assert page.evaluate('S.party[0].maxHp')==1030
    page.evaluate('''()=>{document.getElementById('mode').value='archive';reset();}''')
    assert page.evaluate('S.party[0].maxHp')==1530
    # Rewards come only from new DEMO quest clears after explicit activation.
    assert page.evaluate('BFGlobalOptionalImpsV16900.claim()')==0
    page.evaluate('''()=>{window.__imp169OldClear=Object.prototype.hasOwnProperty.call(P.questClears,'1')?P.questClears[1]:null;P.questClears[1]=(P.questClears[1]||0)+2;}''')
    assert page.evaluate('BFGlobalOptionalImpsV16900.claim()')==4
    assert page.evaluate('BFGlobalOptionalImpsV16900.claim()')==0
    # Updates to live quest-clear state above are test-owned; subtract them
    # before comparing the original game state and canonical v7 saved bytes.
    page.evaluate('''()=>{if(window.__imp169OldClear===null)delete P.questClears[1];else P.questClears[1]=window.__imp169OldClear;}''')
    after=page.evaluate('''()=>({
      p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })''')
    assert before==after,(before,after)
    assert page.evaluate('BFGlobalOptionalImpsV16900.exportState()') is not None
    assert not errors,errors
    browser.close()
print('PASS v169 full browser original archive, user enable/feed, battle bridge source+Imp+leader, original mode, training, earned Artons and v7 isolation')
