"""Legacy optional Global music: play() sync/async failures must fail closed.

Real MP3 decoding before/after synthetic platform failures; zero owner save
or Android-device access. The injected errors are not evidence of device faults.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import mimetypes, shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
JS=(A/'bf14500_original_global_music.js').read_text('utf8')
assert JS.count("try{result=sound.play();}catch(_){failure();return false;}")==1
assert "result.catch(failure)" in JS
assert all(term not in JS for term in ('localStorage.setItem','saveProgress(', 'BFAndroid'))
HTML=(A/'index.html').read_text('utf8').replace(
    '<head>','<head><base href="http://bf-legacy-sync.test/">',1)
CSS=(A/'bf_home_nav.css').read_text('utf8')
NAV=(A/'bf_home_nav.js').read_text('utf8')
chrome=shutil.which('chromium') or shutil.which('google-chrome')
assert chrome,'Chromium required for source-browser music regression'
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
         args=['--no-sandbox','--disable-dev-shm-usage',
               '--autoplay-policy=no-user-gesture-required'])
    for width in (320,393):
        ctx=browser.new_context(viewport={'width':width,'height':852},
           service_workers='block',reduced_motion='reduce')
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('dialog',lambda d:d.dismiss())
        external=[]
        def serve(route):
            u=urlsplit(route.request.url)
            if u.scheme!='http' or u.hostname!='bf-legacy-sync.test':
                external.append(u.hostname or u.scheme)
                route.abort()
                return
            name=unquote(u.path).lstrip('/')
            if '..' in Path(name).parts or name.startswith('.') or '\\' in name:
                route.abort()
                return
            file=(A/name)
            if file.is_file() and file.resolve().is_relative_to(A.resolve()):
                route.fulfill(status=200,body=file.read_bytes(),
                    content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
            else:
                route.abort()
        page.route('**/*',serve)
        page.evaluate("""() => {const m=Object.create(null);window.__musicStorage=m;
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }}); }""")
        page.set_content(HTML,wait_until='load',timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=NAV)
        page.evaluate("""() => {
          const NativeAudio=window.Audio;
          window.Audio=function(...args){
            const audio=new NativeAudio(...args);
            window.__legacyTestAudio=audio;return audio;
          };
          BF_homeNav.go('quest');
          document.getElementById('mode').value='archive';
        }""")
        page.add_script_tag(content=JS)
        assert page.locator('#bf145-original-music button').count()==3
        state="JSON.stringify({P,storage:window.__musicStorage})"
        original=page.evaluate(state)
        buttons=page.locator('#bf145-original-music button')
        # Decode actual bundled MP3 first, without replacing any media method.
        buttons.nth(0).click()
        page.wait_for_function('!__legacyTestAudio.paused&&__legacyTestAudio.currentTime>0.02')
        buttons.nth(2).click()
        assert page.evaluate('BFOriginalGlobalMusicV14500.state.stopped')
        page.evaluate("""() => {
          __legacyTestAudio.play=()=>{
            throw new DOMException('Injected synchronous playback failure','NotAllowedError');
          };
        }""")
        buttons.nth(0).click()
        page.wait_for_function('BFOriginalGlobalMusicV14500.state.stopped')
        assert page.evaluate('BFOriginalGlobalMusicV14500.state.active') is None
        assert buttons.nth(2).is_disabled()
        assert page.locator('#bf145-original-music-status').inner_text()==(
            'Playback blocked or unavailable. Tap Play again.')
        page.evaluate("""() => {
          __legacyTestAudio.play=()=>Promise.reject(
            new DOMException('Injected rejected play promise','NotAllowedError'));
        }""")
        buttons.nth(0).click()
        page.wait_for_function('BFOriginalGlobalMusicV14500.state.stopped')
        assert buttons.nth(2).is_disabled()
        assert page.locator('#bf145-original-music-status').inner_text()==(
            'Playback blocked or unavailable. Tap Play again.')
        # Old rejected promise must never cancel the subsequent real request.
        page.evaluate("""() => {
          __legacyTestAudio.play=()=>new Promise((resolve,reject)=>{
             window.__rejectLegacyOld=reject;
          });
        }""")
        buttons.nth(0).click()
        page.evaluate('delete __legacyTestAudio.play')
        buttons.nth(1).click()
        page.wait_for_function('!__legacyTestAudio.paused&&__legacyTestAudio.currentTime>0.02')
        page.evaluate("""() => __rejectLegacyOld(
          new DOMException('Stale promise','AbortError'))""")
        page.wait_for_timeout(80)
        assert page.evaluate("BFOriginalGlobalMusicV14500.state.active==='boss'")
        assert page.evaluate('!__legacyTestAudio.paused')
        buttons.nth(2).click()
        assert page.evaluate('BFOriginalGlobalMusicV14500.state.stopped')
        # Real audio can still start after the synthetic failure sequence.
        buttons.nth(0).click()
        page.wait_for_function('!__legacyTestAudio.paused&&__legacyTestAudio.currentTime>0.02')
        buttons.nth(2).click()
        assert page.evaluate(state)==original,(width,'synthetic player/storage mutation')
        assert not errors,(width,errors)
        assert not external,(width,external)
        ctx.close()
        print('PASS legacy optional real music playback/failure/recovery',width)
    browser.close()
print('PASS legacy music sync and Promise failures, stale rejection, full save isolation')
