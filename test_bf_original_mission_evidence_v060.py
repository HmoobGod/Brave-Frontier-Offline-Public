"""v0.60 browser regression: source-exact quest fields, read-only inspector, save integrity."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf-8'))
assert len(source['rows'])==34
assert source['source']['fileSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
html_path=ASSETS/'index.html'
html=html_path.read_text('utf-8')
for marker in ('BF_ORIGINAL_MISSION_EVIDENCE_V057','BF_ORIGINAL_MISSION_INSPECTOR_V058',
               'BF_ORIGINAL_MISSION_INSPECTOR_STAGED_V060',
               'BF_TOWER_BOSS_FORMATION_HOOK_V055','BF_MONSTER_TRAINING_HOOK_V053'):
    assert html.count('/* '+marker+' */')==1,marker
before=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(ROOT/'prepare_original_mission_evidence_v060.py')],check=True,cwd=ROOT)
assert hashlib.sha256(html_path.read_bytes()).digest()==before,'preparation must be idempotent'

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
       executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
       args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        asset=ASSETS/rel
        if asset.is_file() and asset.resolve().is_relative_to(ASSETS.resolve()) and asset.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=asset.read_bytes(),
               content_type='image/jpeg' if asset.suffix=='.jpg' else 'image/png')
        else:route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',local)
    page.evaluate("""() => {
      const db={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
                     wait_until='load',timeout=90000)
    assert page.evaluate('P.version')==7
    assert page.evaluate('BFOriginalMissionEvidence.count')==34
    assert page.evaluate('BFOriginalMissionEvidence.missionIds')==[r['missionId'] for r in source['rows']]
    assert page.evaluate('BFOriginalMissionEvidence.lookup(999)') is None
    assert page.evaluate('BFOriginalMissionEvidence.parseOpaqueReferences("not:a:pair")') is None
    parsed=page.evaluate('BFOriginalMissionEvidence.parseOpaqueReferences("1:10800,0:10801")')
    assert parsed==[{'opaqueLabel':'1','opaqueRef':'10800'},{'opaqueLabel':'0','opaqueRef':'10801'}]
    assert page.evaluate('Object.isFrozen(BFOriginalMissionEvidence.lookup(85))') is True
    for expected in source['rows']:
        actual=page.evaluate('(id)=>BFOriginalMissionEvidence.lookup(id)',expected['missionId'])
        assert actual==expected,(expected,actual)
    assert page.locator('#bf058-source-inspector').count()==1
    assert page.locator('#bf058-source-inspector').evaluate('(el)=>el.open') is False
    assert page.evaluate('BFOriginalMissionInspector.missionId')==1
    assert '3:10100,1:10101,0:10102' in page.locator('#bf058-source-content').text_content()
    assert 'NOT restored' in page.locator('#bf058-source-content').text_content()

    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate('()=>{for(const id of [73,81,82,83,84])P.questClears[id]=1;renderQuestList()}')
    saved=page.evaluate("""() => ({
      progress:JSON.stringify(P),
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster)
    })""")
    page.locator('[data-bf-mission="85"]').click()
    page.wait_for_function('()=>BFOriginalMissionInspector.missionId===85')
    content=page.locator('#bf058-source-content').text_content()
    assert '1:10800,0:10801' in content
    assert '8:0:1:0:0' in content
    assert 'item identity unknown' in content
    assert 'Current battles are DEMO' in content
    page.locator('#bf058-source-inspector summary').click()
    assert page.evaluate('BFOriginalMissionInspector.open') is True
    assert page.evaluate('S.totalWaves')==8
    page.locator('[data-bf-mission="81"]').click()
    page.wait_for_function('()=>BFOriginalMissionInspector.missionId===81')
    assert 'Archived additional reward: (blank)' in page.locator('#bf058-source-content').text_content()
    assert page.evaluate('S.totalWaves')==7
    assert page.evaluate('BFOriginalMissionEvidence.lookup(81).rawCutscene')=='0,0'
    assert page.evaluate('BFOriginalMissionEvidence.lookup(10).rawCutscene')=='0,map1-dungeon0-1end.txt'
    assert page.evaluate('BF052BossIntel.enabled') is False
    assert page.evaluate('BF053TrainingMonsters.enabled') is False
    assert page.evaluate('BF055TowerBosses.enabled') is False
    state=page.evaluate("""() => ({
      progress:JSON.stringify(P),
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster)
    })""")
    # Selecting a different quest legitimately writes P.lastMission and localStorage;
    # compare only stable user data across navigation, then verify that the
    # source panel itself does not write any save or progress data.
    assert state['squad']==saved['squad'] and state['roster']==saved['roster']
    assert page.evaluate('P.version')==7
    before_panel=page.evaluate("""() => ({
       progress:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.locator('#bf058-source-inspector summary').click()
    page.locator('#bf058-source-inspector summary').click()
    after_panel=page.evaluate("""() => ({
       progress:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    assert after_panel==before_panel,(before_panel,after_panel)
    assert not errors,errors
    browser.close()
print('PASS v0.60: 34 exact original mission source records, honest UI, no guessed waves/drops, v7 stable')
