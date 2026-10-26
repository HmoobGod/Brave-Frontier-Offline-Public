"""v103: read-only detailed battle observer stays separate from gameplay."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf10300_qol_battle_details.js').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_BATTLE_DETAILS_V10300')==1
assert len(src.encode())<65536
assert not any(t in src for t in ('localStorage','saveProgress(', 'awardDemoRewards(', 'S.party=','S.enemies=','P.squad='))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><div id="bf2000-run">Original battle</div></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:2}};
   window.S={mode:'archive',wave:0,totalWaves:3,round:1,busy:false,
   over:false,phase:'Action',
   party:[{name:'Vargas',unitId:10011,active:true,hp:600,maxHp:1000,bb:70,guard:false}],
   enemies:[{name:'Enemy',unitId:20011,hp:220,maxHp:440}]};
   window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:2})};
   window.BFGlobalMultiHitCriticalV9500={snapshot:()=>({criticalHits:3})};
 }""")
 before=p.evaluate("JSON.stringify({P,S})")
 p.add_script_tag(path=str(A/'bf10300_qol_battle_details.js'))
 api='BFGlobalQoLBattleDetailsV10300'
 s=p.evaluate(api+'.snapshot()')
 assert s['wave']==1 and s['totalWaves']==3 and s['round']==1
 assert s['sourceScopedCriticalHits']==5
 assert s['allies'][0]['hpPercent']==60 and s['allies'][0]['bb']==70
 assert s['foes'][0]['hpPercent']==50
 p.locator('#bf10300-details > summary').click()
 assert 'Vargas' in p.locator('#bf10300-allies').inner_text()
 assert 'Enemy' in p.locator('#bf10300-enemies').inner_text()
 p.evaluate("S.party[0].hp=0")
 p.evaluate(api+'.refresh()')
 assert 'KO' in p.locator('#bf10300-allies').inner_text()
 assert before != p.evaluate("JSON.stringify({P,S})")
 assert p.evaluate("P.version")==7
 p.add_script_tag(path=str(A/'bf10300_qol_battle_details.js'))
 assert p.locator('#bf10300-details').count()==1
 assert not errors,errors
 b.close()
print('PASS v103 read-only battle HP/BB/source critical HUD, no save or combat writes')
