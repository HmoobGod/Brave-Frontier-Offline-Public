"""v0.65: all playable normal attack source frames, 100% gate and save v7."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf-8'))
assert len(source['rows'])==72
assert len({v['unitId'] for v in source['rows']})==72
assert source['provenance']['excludedUnitIds']==[10023]
html_file=ASSETS/'index.html'
html=html_file.read_text('utf-8')
assert html.count('/* BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065 */')==1
assert html.count('/* BF_PLAYABLE_ORIGINAL_HITS_V062 */')==1
digest=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(ROOT/'prepare_playable_attack_frames_v065.py')],check=True,cwd=ROOT)
assert hashlib.sha256(html_file.read_bytes()).digest()==digest

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
       executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
       args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.evaluate("""() => {
      const saved={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>saved[k]??null,setItem:(k,v)=>{saved[k]=String(v)},
        removeItem:k=>{delete saved[k]},key:i=>Object.keys(saved)[i]??null,
        get length(){return Object.keys(saved).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html,wait_until='load',timeout=90000)
    assert page.evaluate('P.version')==7
    assert page.evaluate('BFPlayableAttackFramesV062.count')==72
    assert page.evaluate('BFPlayableAttackFramesV062.eligible')==71
    assert page.evaluate('BFPlayableAttackFramesV062.excluded')==1
    assert '130 rather than 100' in page.evaluate('BFPlayableAttackFramesV062.excludedReason(10023)')
    assert page.evaluate('archivedNormalAttackEvents(10023)') is None
    assert page.evaluate('archivedNormalAttackEvents(999999)') is None
    baseline=page.evaluate("""() => ({
        player:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    master=page.evaluate("""() => {
        const base=document.getElementById('bf-global-unit-catalog-data');
        const catalog=JSON.parse(base.textContent);
        return catalog.units.map(x=>x.id);
    }""")
    assert len(master)==2291
    for record in source['rows']:
        id=record['unitId']
        assert id in master,id
        lookup=page.evaluate('(id)=>BFPlayableAttackFramesV062.lookup(id)',id)
        assert lookup['raw']==record['damageFrames']
        splits=[[int(s) for s in e.split(':')] for e in record['damageFrames'].split(',')]
        assert lookup['events']==splits,id
        total=sum(row[1] for row in splits)
        assert lookup['weightsTotal']==total
        assert page.evaluate('(id)=>BFPlayableAttackFramesV062.eligibleForPlayback(id)',id)==(total==100)
        playback=page.evaluate('(id)=>archivedNormalAttackEvents(id)',id)
        assert playback==(splits if total==100 else None),(id,total)
    for id in (10013,20024,30025,40042,50015,60025):
        events=page.evaluate('(id)=>archivedNormalAttackEvents(id)',id)
        total=sum(e[1] for e in events)
        assert total==100
        damage=page.evaluate('(events)=>splitDemoDamage(137,events)',events)
        assert len(damage)==len(events) and sum(damage)==137,(id,damage)
    # Base six original frames are unchanged by the added source extension.
    expected=[10011,20011,30011,40011,50011,60011]
    for id in expected:
        info=page.evaluate('(id)=>BF_ARCHIVE_NORMAL_HITS[String(id)]',id)
        assert info['raw']==next(x['damageFrames'] for x in source['rows'] if x['unitId']==id)
    assert page.evaluate('JSON.stringify(P)')==baseline['player']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==baseline['save']
    assert not errors,errors
    browser.close()
print('PASS v0.65 71/72 archived normal hit timings playable, 10023 excluded 130%, DEMO damage only, save v7')
