"""v159: research-only browser Gem transaction persistence / v7 compatibility."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,re,shutil,json
R=Path(__file__).resolve().parent
JS=(R/'research/bf15900_gem_atomic_persistence_prototype.js').read_text('utf8')
V=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
H=json.loads((R/'source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json').read_text('utf8'))
assert V['originalRewardFinales']==H['corroboratedMissionCount']==29
assert V['currentPlayableFinales']==H['currentlyPlayable']==22
assert V['amdahlUnplayableFinales']==H['amdahlSourceOnly']==7
ids=[a[0] for a in V['rows'] if a[4]==1]
assert len(ids)==22 and len(set(ids))==22
m=re.search(r'const ELIGIBLE=(\[.*?\]);',JS,re.S)
assert m and re.fullmatch(r'[\[\]0-9,\s]+',m.group(1))
assert ast.literal_eval(m.group(1))==ids
assert 'BF_GLOBAL_GEM_ATOMIC_PERSISTENCE_LAB_V15900' in JS
assert JS.count('localStorage.')==0
assert 'bf_global_offline_demo_v7' not in JS
assert 'BFAndroid' not in JS
assert 'MAX_MODEL_GEMS=999999' in JS
assert 'livePayoutEnabled:false,v7SaveMutation:false' in JS
assert not (R/'app/src/main/assets/bf15900_gem_atomic_persistence_prototype.js').exists()
assert 'bf15900_gem_atomic_persistence_prototype.js' not in (R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 p=browser.new_page()
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto('about:blank')
 p.evaluate("""()=>{
    const data={'bf_global_offline_demo_v7':'untouched-v124-save'};
    let writes=[];
    window.store={
      getItem:k=>Object.prototype.hasOwnProperty.call(data,k)?data[k]:null,
      setItem:(k,v)=>{writes.push(k);data[k]=String(v);},
      removeItem:k=>{writes.push(k);delete data[k];}
    };
    window.__data=data;window.__writes=writes;
    window.P={version:7,roster:[10011],questClears:{12:1,1:40,365:0}};
 }""")
 p.add_script_tag(content=JS)
 A='BFGlobalGemAtomicPersistenceLabV15900'
 assert p.evaluate('Boolean(window.'+A+')') is True
 assert p.evaluate(A+'.eligible.length')==22
 assert p.evaluate(A+'.livePayoutEnabled') is False
 assert p.evaluate(A+'.v7SaveMutation') is False
 p.evaluate('window.initial='+A+'.fromLegacy(P)')
 assert p.evaluate('initial.legacyFinales')==[12]
 assert p.evaluate('initial.gems')==0
 p.evaluate('window.next='+A+'.apply(initial,365)')
 assert p.evaluate('next.credited') is True
 assert p.evaluate('next.state.gems')==1
 assert p.evaluate('initial.gems')==0
 assert p.evaluate('next.state.paidFinales')==[365]
 # Crash before commit: retries on the stored prior state pay exactly once.
 p.evaluate('window.retry='+A+'.apply(initial,365)')
 assert p.evaluate('JSON.stringify(next)===JSON.stringify(retry)') is True
 assert p.evaluate(A+'.read(store)') is None
 p.evaluate(A+'.commit(store,next.state)')
 assert p.evaluate(A+'.read(store).gems')==1
 assert p.evaluate('JSON.stringify('+A+'.read(store))===JSON.stringify(next.state)') is True
 # Replaying a committed clear cannot pay again.
 p.evaluate('window.replay='+A+'.apply('+A+'.read(store),365)')
 assert p.evaluate('replay.credited') is False
 assert p.evaluate('replay.state.gems')==1
 p.evaluate('window.amdahl='+A+'.apply('+A+'.read(store),404)')
 assert p.evaluate('amdahl.credited') is False
 assert p.evaluate('amdahl.state.gems')==1
 p.evaluate('window.oldQuest='+A+'.apply('+A+'.read(store),12)')
 assert p.evaluate('oldQuest.credited') is False
 p.evaluate("""()=>{window.failingStorage={
       getItem:k=>store.getItem(k),setItem:()=>{throw Error('quota exceeded');}
    };}""")
 assert p.evaluate("""()=>{try{
    BFGlobalGemAtomicPersistenceLabV15900.commit(failingStorage,replay.state);
    return false;}catch(e){return /quota exceeded/.test(String(e));}}""") is True
 assert p.evaluate(A+'.read(store).gems')==1
 for expr in (
   A+'.fromLegacy({version:8,questClears:{}})',
   A+'.fromLegacy({version:7,questClears:null})',
   A+'.fromLegacy({version:7})',
   A+'.fromLegacy({version:7,questClears:{"12":-1}})',
   A+'.fromLegacy({version:7,questClears:{"12":true}})',
   A+'.apply(initial,0)',
   A+'.apply({...initial,gems:-1},365)',
   A+'.apply({...initial,paidFinales:[12]},365)',
   A+'.apply({...initial,legacyFinales:[12,12]},365)',
   A+'.apply({...initial,paidFinales:[365],gems:1},365)',
 ):
  assert p.evaluate('''expr=>{try{(0,eval)(expr);return false;}catch(e){return true;}}''',expr),expr
 assert p.evaluate('P.version')==7
 assert p.evaluate('P.questClears[365]')==0
 assert p.evaluate("store.getItem('bf_global_offline_demo_v7')")=='untouched-v124-save'
 assert p.evaluate('__writes')==[p.evaluate(A+'.key')]
 assert not errors,errors
 browser.close()
print('PASS v159: source-anchored browser atomic one-key research prototype, crash/retry, no dup/Amdahl rewards, v7 untouched')
