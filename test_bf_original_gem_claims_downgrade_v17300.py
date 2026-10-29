"""v173: browser-prove claimed original Gems are unsafe to downgrade.

Cross-version boundary is tested with three separately loaded pages:
- current, fully prepared v173 runtime
- prior v172 validator reconstructed by EXACT reversal of the v173
  build-time injection on that same prepared page (not a downloaded v172 APK)
- checked-in pre-v160 HTML parser representative of owner v124 legacy schema

The source-exact v172 rule was balance===0 and paidFinales empty. A nonzero
v173 claim triggers recovery, not a silent claim balance loss on v172.
The pre-v160 parser silently drops claims on its next canonical v7 save.
No actual Android runtime, user save or original v172 APK is used.
"""
import json,re,shutil,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
KEY='bf_global_offline_demo_v7'
modern=(R/'app/src/main/assets/index.html').read_text('utf8')
legacy=subprocess.run(['git','show','HEAD:app/src/main/assets/index.html'],
 cwd=R,check=True,capture_output=True,text=True).stdout
assert 'BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300' in modern
assert 'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in modern
assert 'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' not in legacy
v160=(R/'patch_bf_original_gem_ledger_v16000.py').read_text('utf8')
assert 'source.schema!==1||source.balance!==0||' in v160
assert '!Array.isArray(source.paidFinales)||source.paidFinales.length!==0||' in v160
# Exact prior code reconstructed using the unchanged v160 rule and removing
# only the v173 build-time additions; all other game code remains identical.
v172=modern
def undo(new,old):
 global v172
 assert v172.count(new)==1,(new[:80],v172.count(new))
 v172=v172.replace(new,old,1)
undo("""    source.schema!==1||
    !Number.isSafeInteger(source.balance)||source.balance<0||source.balance>22||
    !Array.isArray(source.paidFinales)||source.paidFinales.length!==source.balance||
    !Array.isArray(source.legacyFinales))throw new Error('Invalid pending original Gem ledger');""",
"""    source.schema!==1||source.balance!==0||
    !Array.isArray(source.paidFinales)||source.paidFinales.length!==0||
    !Array.isArray(source.legacyFinales))throw new Error('Invalid pending original Gem ledger');""")
undo(""" const found=source.legacyFinales,paid=source.paidFinales;
 if(paid.some((id,i)=>!Number.isSafeInteger(id)||!ids.includes(id)||
     !complete.includes(id)||(i>0&&id<=paid[i-1])))
   throw new Error('Invalid original Gem paid finale IDs');
 if(found.length>22||found.some((id,i)=>""",
""" const found=source.legacyFinales;
 if(found.length>22||found.some((id,i)=>""")
undo(" return {schema:1,balance:source.balance,paidFinales:[...paid],legacyFinales:complete};",
 " return {schema:1,balance:0,paidFinales:[],legacyFinales:complete};")
# v173's helpers are inserted as a single block immediately before default.
start=v172.index('// BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300')
end=v172.index('const defaultProgress=()=>(',start)
assert v172.count('// BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300')==1
v172=v172[:start]+v172[end:]
for inserted in (
 ' out._bfGemV160=bf173ValidateOriginalClaims(out._bfGemV160,out._bfGemV161Pending,out._bfGemV170Custom);\n',
 '  P._bfGemV160=bf173ValidateOriginalClaims(P._bfGemV160,P._bfGemV161Pending,P._bfGemV170Custom);\n',
 'try{window.BFGlobalOriginalGemClaimsV17300?.refresh?.()}catch(_){}',
):
 undo(inserted,'')
assert 'BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300' not in v172
assert 'source.balance!==0' in v172
assert 'source.paidFinales.length!==0' in v172
assert KEY in modern and KEY in v172 and KEY in legacy

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 errors=[]
 def load(html,initial=None):
  p=browser.new_page(viewport={'width':390,'height':844})
  p.on('pageerror',lambda e:errors.append(str(e)))
  p.evaluate("""({key,raw})=>{
   const db={};if(raw!==null)db[key]=raw;
   window.__downgrade173DB=db;window.__downgrade173Writes=[];
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,
    setItem:(k,v)=>{window.__downgrade173Writes.push(k);db[k]=String(v)},
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""",{'key':KEY,'raw':initial})
  p.set_content(html,wait_until='load',timeout=90000)
  assert p.evaluate('P.version')==7
  return p
 new=load(modern)
 new.evaluate('QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()')
 assert new.evaluate('BFGlobalOriginalGemClaimsV17300.claim()')==1
 assert new.evaluate('P._bfGemV160.balance')==1
 assert new.evaluate('P._bfGemV160.paidFinales')==[12]
 backed=new.evaluate(f"localStorage.getItem('{KEY}')")
 assert json.loads(backed)['_bfGemV160']['balance']==1
 # v160-v172 on-load parser must refuse the positive wallet and quarantine.
 previous=load(v172,backed)
 assert previous.evaluate('P.clears')==0
 assert previous.evaluate('saveRecoveryPending') is True
 assert previous.evaluate(f"localStorage.getItem('{KEY}')")==backed
 assert previous.evaluate('__downgrade173Writes')==[]
 assert previous.evaluate("""raw=>{
  try{parseProgress(JSON.parse(raw));return false}catch(_){return true}
 }""",backed) is True
 # An unpatched legacy (v124-like) save parser accepts the quest progress,
 # but it loses the original Gem metadata if used to write a new save.
 old=load(legacy)
 old.evaluate('raw=>{P=parseProgress(JSON.parse(raw))}',backed)
 assert old.evaluate('P.questClears[12]')==1
 assert old.evaluate("Object.prototype.hasOwnProperty.call(P,'_bfGemV160')") is False
 assert old.evaluate('saveProgress()') is True
 downgraded=old.evaluate(f"localStorage.getItem('{KEY}')")
 assert '_bfGemV160' not in json.loads(downgraded)
 new.evaluate('raw=>{P=parseProgress(JSON.parse(raw))}',downgraded)
 assert new.evaluate('P.questClears[12]')==1
 assert new.evaluate('P._bfGemV160.balance')==0
 assert new.evaluate('P._bfGemV160.paidFinales')==[]
 assert new.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 # Restoring the pre-downgrade export fully restores the paid source ID,
 # and the same first-clear can NEVER mint a second Gem.
 new.evaluate('raw=>{P=parseProgress(JSON.parse(raw))}',backed)
 assert new.evaluate('P._bfGemV160.balance')==1
 assert new.evaluate('P._bfGemV160.paidFinales')==[12]
 assert new.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 assert new.evaluate('saveProgress()') is True
 assert json.loads(new.evaluate(f"localStorage.getItem('{KEY}')"))['_bfGemV160']['balance']==1
 assert not errors,errors
 browser.close()
print('PASS v173 downgrade: reconstructed v172 validator quarantines positive original balance; pre-v160 drops metadata; original exported v7 restores exact paid claim without duplicates')
