"""Real bundled MP3 decoding must stop on route exit and the native Back JS.

Runs in isolated Chromium, not Android hardware; no media methods are mocked.
"""
from pathlib import Path
import json
import re
import shutil

from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
A = ROOT / 'app/src/main/assets'
java = (ROOT / 'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
back = json.loads(re.search(r'UI_BACK_JS\s*=\s*("[^\n]+");', java)[1])
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width':393, 'height':852})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    def serve(route):
        prefix = 'http://bf-music.test/'
        if not route.request.url.startswith(prefix):
            route.abort(); return
        p = A / route.request.url[len(prefix):]
        if p.is_file() and p.resolve().is_relative_to(A.resolve()):
            mime = 'audio/mpeg' if p.suffix == '.mp3' else 'image/png'
            route.fulfill(status=200, body=p.read_bytes(), content_type=mime)
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
    before = page.evaluate(SNAPSHOT)
    assert page.evaluate('__routePlayEvents') == 0
    for player in ('quest', 'legacy'):
        for kind in ('map', 'boss'):
            for route in ('native-back', 'units', 'summon', 'menu', 'nav-home'):
                page.evaluate("BF_homeNav.go('quest')")
                page.evaluate('''player=>{window.__routeAudio=player==='quest'?
                    document.querySelector('.bf-global-audio audio'):__routeLegacyAudio}''', player)
                button = ('#bf-global-play-track' if kind == 'map' else '#bf-global-boss-preview') if player == 'quest' else None
                if button:
                    page.locator(button).click()
                else:
                    page.locator('#bf145-original-music button').nth(0 if kind == 'map' else 1).click()
                page.wait_for_function('!__routeAudio.paused&&__routeAudio.currentTime>0.02')
                plays = page.evaluate('__routePlayEvents')
                if route == 'native-back':
                    assert page.evaluate(back) is True
                elif route == 'nav-home':
                    page.locator('.bf-navbar [data-bf-goto="home"]').click()
                else:
                    page.evaluate('route=>BF_homeNav.go(route)', route)
                assert page.evaluate('__routeAudio.paused&&!__routeAudio.getAttribute("src")'), (
                    player, kind, route, 'Quest audio kept playing after navigation')
                assert page.evaluate('BFGlobalAudio.playingMode===null&&BFOriginalGlobalMusicV14500.state.stopped')
                page.evaluate("BF_homeNav.go('quest')")
                page.wait_for_timeout(150)
                assert page.evaluate('__routePlayEvents') == plays
                assert page.evaluate('__routeAudio.paused&&!__routeAudio.getAttribute("src")')
                assert_unchanged(page, before, (player, kind, route))
                print('PASS real MP3 route stop', player, kind, route, flush=True)
    assert page.evaluate('!document.hidden&&__routeHiddenEvents===0&&__routeNativePause===0')
    assert not errors, errors
    browser.close()
print('PASS both players: native Back expression, navigation, explicit replay, no autoplay and full P/storage')
