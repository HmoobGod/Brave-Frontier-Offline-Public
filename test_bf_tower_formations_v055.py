"""v0.55 historical Tower boss composition: original names; demo stats; safe opt-in."""
from pathlib import Path
import json,hashlib,subprocess,shutil,sys
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_mistral_boss_intel_v052.json').read_text('utf-8'))
assert source['provenance']['classification']=='historical-community-record, not 2022 MST combat formula'
html_path=A/'index.html'
html=html_path.read_text('utf-8')
for marker in ('BF_TOWER_BOSS_FORMATION_HOOK_V055','BF_TOWER_BOSS_PLACEHOLDER_V055',
               'BF_HISTORICAL_TOWER_FORMATIONS_V055'):
    assert html.count('/* '+marker+' */')==1,marker
original_hash=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(R/'prepare_tower_formations_v055.py')],check=True,cwd=R)
assert hashlib.sha256(html_path.read_bytes()).digest()==original_hash,'staging must be idempotent'
assert 'bf_global_offline_demo_v7' in html

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
       executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
       args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
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
    assert page.evaluate('BF055TowerBosses.missionIds')==[81,82,83,84]
    assert page.evaluate('BF055TowerBosses.enabled') is False
    assert page.evaluate('xyEnemy.length')==4
    assert page.evaluate('BF052BossIntel.enabled') is False
    assert page.locator('#bf055-enable-tower-formations').count()==1

    # All original simulated encounters remain in force with the option OFF.
    for mission,count in [(81,2),(82,3),(83,1),(84,4)]:
        row=page.evaluate("""id => {
          const candidates=[{id:'gel',name:'base',maxHp:900,atk:123,def:88}];
          const q=QUESTS.find(q=>q.missionId===id);
          return BF055TowerBosses.encounter(id,q.battles-1,q.battles,'archive',candidates);
        }""",mission)
        assert row is None,(mission,row)

    # Select unlocked Mission 81, then toggle; no persistent save writes.
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate('()=>{P.questClears[73]=1;renderQuestList()}')
    page.locator('[data-bf-mission="81"]').click()
    assert page.evaluate('QUEST.missionId')==81
    assert not page.locator('#bf055-formations').is_hidden()
    start=page.evaluate("""() => ({
      progress:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.locator('#bf055-enable-tower-formations').check()
    assert page.evaluate('BF055TowerBosses.enabled') is True
    assert page.evaluate('BF052BossIntel.enabled') is False
    assert page.evaluate('S.wave')==0
    assert page.evaluate('JSON.stringify(P)')==start['progress']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==start['save']

    expectations={81:['King Glowy','King Gloomy'],
      82:['Behemoth','Skeleton','Skeleton'],
      83:['Wyvern'],
      84:['King Burny','King Squirty','King Mossy','King Sparky']}
    for mission,names in expectations.items():
        q=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',mission)
        out=page.evaluate("""({id,total})=>{
          const base=[{id:'gel',maxHp:800,atk:111,def:77},
                      {id:'wisp',maxHp:900,atk:222,def:88},
                      {id:'golem',maxHp:1000,atk:333,def:99}];
          return BF055TowerBosses.encounter(id,total-1,total,'archive',base);
        }""",{'id':mission,'total':q['battles']})
        assert [e['bossReferenceName'] for e in out]==names,mission
        assert len(out)==len(names),mission
        assert all(e['historicalBossPreview'] is True for e in out)
        assert all('DEMO combat' in e['name'] and e['atk'] in [111,222,333] for e in out)
        assert all(e['def'] in [77,88,99] for e in out)
        if mission==81:
            assert [e['maxHp'] for e in out]==[15000,15000]
            assert all(e['verifiedBossHp'] is True for e in out)
        else:
            assert all(e['verifiedBossHp'] is False for e in out)
        for badwave in [0,q['battles']-2]:
            assert page.evaluate("""({id,total,wave})=>
                BF055TowerBosses.encounter(id,wave,total,'archive',[{id:'gel',maxHp:900,atk:40,def:20}])""",
                {'id':mission,'total':q['battles'],'wave':badwave}) is None
        assert page.evaluate("""({id,total})=>
                BF055TowerBosses.encounter(id,total-1,total,'training',[{id:'gel',maxHp:900,atk:40,def:20}])""",
                {'id':mission,'total':q['battles']}) is None

    assert page.evaluate("""() =>
        BF055TowerBosses.encounter(85,7,8,'archive',[{id:'gel',maxHp:700,atk:45,def:25}])
    """) is None, 'v0.52 Juggernaut remains separate'

    # Four enemy slots must render as neutral silhouettes, not incorrect game art.
    page.evaluate("""() => {
      QUEST=QUESTS.find(q=>q.missionId===84);
      S.wave=6;S.totalWaves=7;S.enemies=makeWave(6);S.target=0;update();
    }""")
    assert page.evaluate('S.enemies.length')==4
    assert page.locator('#targets button').count()==4
    page.locator('#targets button').last.click()
    assert page.evaluate('S.target')==3
    drew=page.evaluate("""() => {
      const canvas=document.createElement('canvas');canvas.width=480;canvas.height=344;
      const context=canvas.getContext('2d');
      return S.enemies.map((enemy,i)=>
        BF055TowerBosses.drawPlaceholder(enemy,context,70+i*35,150));
    }""")
    assert drew==[True,True,True,True]
    assert page.evaluate('JSON.stringify(P)')==start['progress']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==start['save']
    page.locator('#bf055-enable-tower-formations').uncheck()
    assert page.evaluate('BF055TowerBosses.enabled') is False
    assert page.evaluate("S.enemies.every(e=>!e.historicalBossPreview)") is True
    assert page.evaluate('JSON.stringify(P)')==start['progress']
    assert not errors,errors
    browser.close()
print('PASS v0.55 historical Tower groups 81-84, four-slot targeting, no false art, DEMO stats, v7')
