"""v171: canonical Imp state is lost by an old parser; original export restores it.

Actual repository HTML parsers under Chromium. Does NOT claim old APK runtime or
upgrade equivalence with the owner's real installed signed v124.
"""
from pathlib import Path
import json,shutil,subprocess
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
KEY='bf_global_offline_demo_v7'
modern=(R/'app/src/main/assets/index.html').read_text('utf8')
legacy=subprocess.run(['git','show','HEAD:app/src/main/assets/index.html'],
    cwd=R,capture_output=True,text=True,check=True).stdout
assert 'BF_GLOBAL_IMP_CANONICAL_V17100' in modern
assert 'BF_GLOBAL_IMP_CANONICAL_V17100' not in legacy
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 errors=[]
 def page_for(html):
  p=b.new_page(viewport={'width':390,'height':844})
  p.on('pageerror',lambda e:errors.append(str(e)))
  p.evaluate("""()=>{const db={};
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
 modern_p=page_for(modern)
 modern_p.evaluate("""()=>{P.questClears[10]=3;
   P._bfImpsV171={version:1,started:true,mode:'custom',
    amounts:{'10011':[100,40,0,0]},
    inventory:{molin:1,pakpak:2,ganju:3,fwahl:4,arton:7},
    cursors:{'10':3}};
   if(!saveProgress())throw Error('could not save modern state');
 }""")
 backup=modern_p.evaluate(f"localStorage.getItem('{KEY}')")
 saved=json.loads(backup)
 assert saved['_bfImpsV171']['amounts']['10011']==[100,40,0,0]
 assert saved['_bfImpsV171']['inventory']['arton']==7
 old=page_for(legacy)
 old.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}",backup)
 assert old.evaluate('P.questClears[10]')==3
 assert old.evaluate("Object.prototype.hasOwnProperty.call(P,'_bfImpsV171')") is False
 assert old.evaluate('saveProgress()') is True
 downgraded=old.evaluate(f"localStorage.getItem('{KEY}')")
 assert '_bfImpsV171' not in json.loads(downgraded)
 modern_p.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}",downgraded)
 assert modern_p.evaluate('P._bfImpsV171') is None
 assert modern_p.evaluate('P.questClears[10]')==3
 # Imported old JSON cannot reattach a legacy sidecar automatically.
 # The user's originally exported compatible v171 JSON restores full Imps.
 modern_p.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}",backup)
 assert modern_p.evaluate('P._bfImpsV171.amounts["10011"]')==[100,40,0,0]
 assert modern_p.evaluate('P._bfImpsV171.inventory.arton')==7
 assert modern_p.evaluate('P._bfImpsV171.cursors["10"]')==3
 assert modern_p.evaluate('saveProgress()') is True
 assert json.loads(modern_p.evaluate(f"localStorage.getItem('{KEY}')"))['_bfImpsV171']==saved['_bfImpsV171']
 assert not errors,errors
 b.close()
print('PASS v171: old APK parser drops optional canonical Imps, external v171 export restores exact fields; no retroactive auto-attachment')
