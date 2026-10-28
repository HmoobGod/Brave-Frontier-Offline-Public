"""v145: original 2022 music cue identity + opt-in existing MP3 WebView playback.

Music is never played without an explicit user action and has no v7 save fields.
"""
from pathlib import Path
import hashlib, json, re, shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_original_quest_music_v145.json').read_text())
assert M['schema']=='bf-global-original-2022-music-cues-v145'
assert M['year']==2022 and M['originalQuestCues']==106
assert M['uniqueOriginalMp3']==18 and M['bundledMp3']==3
assert M['masterArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert M['sourceSoundPackSha256']=='9be425acdd37d036c2c14b1fa4457aa07632e528e4633d0f9e35b78c4df0be5d'
assert M['originalBattleCueStartUnknown'] and M['originalMapVsBossCueTriggerUnknown']
assert M['notAnOriginalPlayer'] and M['saveMutation'] is False
assert len(M['unpackagedOriginalMp3'])==15
cues=M['cues']
assert len(cues)==106 and len({x[0] for x in cues})==106
assert hashlib.sha256(json.dumps(cues,separators=(',',':')).encode()).hexdigest()==M['canonicalCueSha256']
assert len({track for row in cues for track in row[1:]})==18
assert sum(row[1] in M['packagedAudio'] for row in cues)==14
assert sum(row[2] in M['packagedAudio'] for row in cues)==104
for track,details in M['packagedAudio'].items():
 data=(A/'content/sound'/track).read_bytes()
 assert len(data)==details['bytes'] and hashlib.sha256(data).hexdigest()==details['sha256']
js=(A/'bf14500_original_global_music.js').read_text()
assert len(js.encode())<65536
assert js.count('BF_ORIGINAL_2022_GLOBAL_OPTIN_MUSIC_V14500')==1
assert M['canonicalCueSha256'] in js
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
assert 'sound.preload=\'none\'' in js and 'sound.loop=true' in js
assert 'autoplay:false,saveMutation:false' in js
assert 'sound.play()' in js
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf14300_original_quest_energy.js")')<java.index('readPackagedText("bf14500_original_global_music.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
  window.__playCalls=0;window.__pauseCalls=0;
  window.Audio=class {
   constructor(){this.src='';this.loop=false;this.preload='';this.volume=1}
   pause(){window.__pauseCalls++}
   removeAttribute(k){if(k==='src')this.src=''}
   getAttribute(k){return k==='src'&&this.src?this.src:null}
   load(){}
   play(){window.__playCalls++;return Promise.resolve()}
  };
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('window.__playCalls')==0
 page.add_script_tag(path=str(A/'bf14500_original_global_music.js'))
 assert page.locator('#bf145-original-music').count()==1
 assert page.evaluate('BFOriginalGlobalMusicV14500.source.missions')==106
 assert page.evaluate('BFOriginalGlobalMusicV14500.source.originalFiles')==18
 assert page.evaluate('BFOriginalGlobalMusicV14500.source.saveMutation') is False
 assert page.evaluate('BFOriginalGlobalMusicV14500.state.stopped') is True
 assert page.evaluate('window.__playCalls')==0
 assert page.locator('#bf145-original-music button').count()==3
 assert page.evaluate('BFOriginalGlobalMusicV14500.lookup(1).map')=='bf010_map_grass.mp3'
 assert page.evaluate('BFOriginalGlobalMusicV14500.lookup(20).map')=='bf011_map_firecave.mp3'
 assert page.evaluate('BFOriginalGlobalMusicV14500.lookup(365).boss')=='bf028_map_space.mp3'
 # Original mission 1 - both packaged map and boss music.
 assert not page.locator('#bf145-original-music button').nth(0).is_disabled()
 assert not page.locator('#bf145-original-music button').nth(1).is_disabled()
 page.locator('#bf145-original-music button').nth(0).click()
 assert page.evaluate('window.__playCalls')==1
 assert page.evaluate('BFOriginalGlobalMusicV14500.state.src')=='content/sound/bf010_map_grass.mp3'
 page.locator('#bf145-original-music button').nth(1).click()
 assert page.evaluate('window.__playCalls')==2
 assert page.evaluate('BFOriginalGlobalMusicV14500.state.src')=='content/sound/bf006_btl_boss.mp3'
 page.locator('#bf145-original-music button').nth(2).click()
 assert page.evaluate('BFOriginalGlobalMusicV14500.state.stopped') is True
 # Change selected mission in browser-only test (no mutation of P save).
 page.evaluate('QUEST=QUEST_BY_ID.get(20);BFOriginalGlobalMusicV14500.refresh()')
 assert page.evaluate('BFOriginalGlobalMusicV14500.lookup(20).map')=='bf011_map_firecave.mp3'
 page.locator('#bf145-original-music button').nth(0).click()
 assert page.evaluate('BFOriginalGlobalMusicV14500.state.src')=='content/sound/bf011_map_firecave.mp3'
 page.locator('#bf145-original-music button').nth(2).click()
 page.evaluate('QUEST=QUEST_BY_ID.get(365);BFOriginalGlobalMusicV14500.refresh()')
 assert page.locator('#bf145-original-music button').nth(1).is_disabled()
 assert page.locator('#bf145-original-music button').nth(0).is_disabled()
 # Reassign mission without saving then disable mode: must fail closed.
 page.evaluate('QUEST=QUEST_BY_ID.get(1);E.mode.value="training";BFOriginalGlobalMusicV14500.refresh()')
 assert page.locator('#bf145-original-music button').nth(0).is_disabled()
 assert page.locator('#bf145-original-music button').nth(1).is_disabled()
 page.add_script_tag(path=str(A/'bf14500_original_global_music.js'))
 assert page.locator('#bf145-original-music').count()==1
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'music-only UI must not touch P, S or v7 saved data'
 assert not errors,errors
 browser.close()
print('PASS v145: original 106 mission music cues, original bundled MP3 source SHA, opt-in guarded playback and v7 save isolation')
