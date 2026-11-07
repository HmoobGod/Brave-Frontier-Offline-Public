"""New explicit music choices survive older aborted play promises.

Runs in isolated Chromium, not Android hardware; no media methods are mocked.
"""
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
A = ROOT / 'app/src/main/assets'
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width':393, 'height':852})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    bad_audio = False
    def serve(route):
        prefix = 'http://bf-music.test/'
        if not route.request.url.startswith(prefix):
            route.abort(); return
        p = A / route.request.url[len(prefix):]
        if p.is_file() and p.resolve().is_relative_to(A.resolve()):
            mime = 'audio/mpeg' if p.suffix == '.mp3' else 'image/png'
            route.fulfill(status=200, body=(b'not an MP3' if bad_audio and p.suffix == '.mp3' else p.read_bytes()), content_type=mime)
        else:
            route.fulfill(status=404, body=b'')
    page.route('**/*', serve)
    page.evaluate(INSTALL_STORAGE)
    html = (A / 'index.html').read_text().replace(
        '<head>', '<head><base href="http://bf-music.test/">', 1)
    page.set_content(html)
    page.add_style_tag(path=str(A / 'bf_home_nav.css'))
    page.add_script_tag(path=str(A / 'bf_home_nav.js'))
    page.evaluate('''() => {
        const RealAudio=window.Audio;
        window.Audio=function(...args){
            const audio=new RealAudio(...args);window.__routeLegacyAudio=audio;return audio;
        };
        window.__routePlayEvents=0;window.__routeHiddenEvents=0;window.__routeNativePause=0;
        document.addEventListener('visibilitychange',()=>__routeHiddenEvents++);
        window.addEventListener('bf-native-background',()=>__routeNativePause++);
        document.getElementById('mode').value='archive';BF_debug.reset();
    }''')
    page.add_script_tag(path=str(A / 'bf14500_original_global_music.js'))
    page.evaluate('''() => {
        document.querySelector('.bf-global-audio audio').addEventListener('playing',()=>__routePlayEvents++);
        __routeLegacyAudio.addEventListener('playing',()=>__routePlayEvents++);
    }''')
    page.evaluate("BF_homeNav.go('quest')")
    # Establish real user activation; every later call still uses real media.
    page.locator('#bf-global-play-track').click()
    page.wait_for_function('BFGlobalAudio.playing&&document.querySelector(".bf-global-audio audio").currentTime>0.02')
    page.locator('#bf-global-stop-track').click()
    before = page.evaluate(SNAPSHOT)
    sequences = [(['map','boss'],'boss'), (['boss','map'],'map'),
                 (['map','map'],'map'), (['boss','boss'],'boss'),
                 (['map','stop','map'],'map'), (['map','leave-return','map'],'map')]
    def reset():
        page.evaluate("() => {BFGlobalAudio.stop();document.querySelectorAll('#bf145-original-music button')[2].click();BF_homeNav.go('quest')}")
    def choose(player, steps):
        page.evaluate('''({player,steps}) => {
            for(const step of steps){
                if(step==='leave-return'){BF_homeNav.go('units');BF_homeNav.go('quest');continue;}
                if(player==='quest')document.getElementById(step==='map'?'bf-global-play-track':
                    step==='boss'?'bf-global-boss-preview':'bf-global-stop-track').click();
                else document.querySelectorAll('#bf145-original-music button')[
                    step==='map'?0:step==='boss'?1:2].click();
            }
        }''', {'player':player,'steps':steps})
    for player in ('quest','legacy'):
        page.evaluate("player=>{window.__requestAudio=player==='quest'?document.querySelector('.bf-global-audio audio'):__routeLegacyAudio}",player)
        for steps, latest in sequences:
            reset();choose(player,steps)
            page.wait_for_timeout(100)
            expected = ('quest' if latest=='map' else 'boss') if player=='quest' else latest
            actual = page.evaluate("player=>player==='quest'?BFGlobalAudio.playingMode:BFOriginalGlobalMusicV14500.state.active",player)
            assert actual == expected, (player,steps,'Old play rejection cancelled latest explicit choice',actual)
            page.wait_for_function('!__requestAudio.paused&&__requestAudio.currentTime>0.02')
            assert_unchanged(page,before,(player,steps))
            print('PASS real decoded replacement',player,steps,flush=True)
        reset();choose(player,['map','stop']);page.wait_for_timeout(150)
        assert page.evaluate('__requestAudio.paused&&!__requestAudio.getAttribute("src")')
        assert_unchanged(page,before,'stop still wins')
        # Actual decoder failure for the CURRENT request must remain handled.
        bad_audio = True
        choose(player,['boss'])
        page.wait_for_function("player=>player==='quest'?BFGlobalAudio.playingMode===null:BFOriginalGlobalMusicV14500.state.stopped",arg=player)
        assert page.evaluate('__requestAudio.paused')
        bad_audio = False
        reset();choose(player,['map'])
        page.wait_for_function('!__requestAudio.paused&&__requestAudio.currentTime>0.02')
        if player == 'quest':
            # No current MediaError exists while the real MP3 is decoding.
            # A late event queued by a detached source must not cancel it.
            assert page.evaluate('__requestAudio.error===null')
            page.evaluate("__requestAudio.dispatchEvent(new Event('error'))")
            assert page.evaluate("BFGlobalAudio.playingMode==='quest'&&!__requestAudio.paused")
            # Nor may a stale error overwrite the user's explicit Stop state.
            page.locator('#bf-global-stop-track').click()
            status_before = page.locator('.bf-global-audio-status').inner_text()
            assert status_before == 'Music stopped.'
            page.evaluate("__requestAudio.dispatchEvent(new Event('error'))")
            assert page.locator('.bf-global-audio-status').inner_text() == status_before
            page.locator('#bf-global-play-track').click()
            page.wait_for_function('!__requestAudio.paused&&__requestAudio.currentTime>0.02')
        assert_unchanged(page,before,'current decoder failure and explicit recovery')
    reset()
    assert page.evaluate('!document.hidden&&__routeHiddenEvents===0&&__routeNativePause===0')
    assert not errors,errors
    browser.close()
print('PASS both real MP3 players: latest explicit request wins, stop/errors preserved, no P/storage changes')
