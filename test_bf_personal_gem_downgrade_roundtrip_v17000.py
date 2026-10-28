"""v170: real browser old->new parser downgrade, wallet loss and backup recovery.

Representative old APK parser from unchanged repository HTML, NOT owner's
physical v124 APK. Never modify user data.
"""
from pathlib import Path
import json, shutil, subprocess
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
KEY='bf_global_offline_demo_v7'
modern=(R/'app/src/main/assets/index.html').read_text('utf8')
legacy=subprocess.run(
  ['git','show','HEAD:app/src/main/assets/index.html'],cwd=R,
  check=True,capture_output=True,text=True
).stdout
assert 'BF_GLOBAL_GEMS_PERSONAL_V17000' in modern
assert 'BF_GLOBAL_GEMS_PERSONAL_V17000' not in legacy
assert KEY in modern and KEY in legacy

with sync_playwright() as pw:
 browser=pw.chromium.launch(
   headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 errors=[]
 def load(html):
  p=browser.new_page(viewport={'width':390,'height':844})
  p.on('pageerror',lambda e:errors.append(str(e)))
  p.evaluate("""()=>{const db={};window.__v170downgradeDb=db;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""")
  p.set_content(html,wait_until='load',timeout=90000)
  assert p.evaluate('P.version')==7
  return p
 new=load(modern)
 assert new.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
 assert new.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is True
 assert new.evaluate('BFGlobalCustomGemsV17000.claimDaily()') is True
 new.evaluate('QUEST=QUESTS.find(q=>q.missionId===10);awardDemoRewards()')
 assert new.evaluate('P._bfGemV170Custom.balance')==1125
 backup=new.evaluate(f"localStorage.getItem('{KEY}')")
 assert json.loads(backup)['_bfGemV170Custom']['balance']==1125
 assert len(json.loads(backup)['_bfGemV170Custom']['firstPaid'])==1
 old=load(legacy)
 old.evaluate("raw=>{P=parseProgress(JSON.parse(raw));}",backup)
 assert old.evaluate('P.questClears[10]')==1
 assert old.evaluate("Object.prototype.hasOwnProperty.call(P,'_bfGemV170Custom')") is False
 assert old.evaluate('saveProgress()') is True
 downgraded=old.evaluate(f"localStorage.getItem('{KEY}')")
 assert '_bfGemV170Custom' not in json.loads(downgraded)
 new.evaluate("raw=>{P=parseProgress(JSON.parse(raw));}",downgraded)
 assert new.evaluate('P._bfGemV170Custom.balance')==0
 assert new.evaluate('P._bfGemV170Custom.mode')=='original'
 assert new.evaluate('P._bfGemV170Custom.legacyClears')==[10]
 assert new.evaluate('P._bfGemV170Custom.welcomeClaimed') is False
 assert new.evaluate('P._bfGemV170Custom.dailyClaims')==0
 # A player MUST restore a pre-downgrade backup to retain Gem wallet data.
 new.evaluate("raw=>{P=parseProgress(JSON.parse(raw));}",backup)
 assert new.evaluate('P._bfGemV170Custom.balance')==1125
 assert new.evaluate('P._bfGemV170Custom.mode')=='custom'
 assert new.evaluate('P._bfGemV170Custom.welcomeClaimed') is True
 assert new.evaluate('P._bfGemV170Custom.dailyClaims')==1
 assert new.evaluate('P._bfGemV170Custom.firstPaid')==[10]
 assert new.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is False
 assert new.evaluate('BFGlobalCustomGemsV17000.claimDaily()') is False
 assert new.evaluate('saveProgress()') is True
 assert json.loads(new.evaluate(f"localStorage.getItem('{KEY}')"))['_bfGemV170Custom']['balance']==1125
 assert not errors,errors
 browser.close()
print('PASS v170: original v7 parser drops wallet on downgrade (warn/backup), pristine pre-downgrade export restores 1125 balance and claim history without duplicate')
