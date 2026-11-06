"""Session Quest-preview audio settings; no autoplay, persistent saves or gameplay."""
from pathlib import Path
import sys,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
J=(A/'bf_home_nav.js').read_text();C=(A/'bf_home_nav.css').read_text()
MARK='/* Session-only Quest preview audio settings;'
MODULE=J.split(MARK,1)[1].split('\n})();',1)[0]+'\n})();'
assert not any(s in MODULE for s in ('localStorage','saveProgress','P.','S.','.play(','fetch(','BFAndroid'))
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
assert 'test_bf_session_settings.py --source-only' in (R/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
assert 'python3 test_bf_session_settings.py' in (R/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:print('PASS session-settings source: bounded UI, no persistence/game/playback APIs');raise SystemExit(0)
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
 for width,height in ((320,740),(393,852),(540,900),(740,360)):
  p=b.new_page(viewport={'width':width,'height':height});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE)
  p.evaluate('()=>{window.__plays=0;HTMLMediaElement.prototype.play=function(){window.__plays++;return Promise.resolve()};}')
  p.set_content((A/'index.html').read_text());p.add_style_tag(content=C);p.add_script_tag(content=J)
  before=p.evaluate(SNAPSHOT);battle=p.evaluate('JSON.stringify(S)')
  p.locator('.bf-navbar [data-bf-goto="menu"]').click();panel=p.locator('#bf-menu-settings');panel.locator('summary').click()
  volume=p.locator('#bf-session-volume');mute=p.locator('#bf-session-mute');assert volume.input_value()=='42' and not mute.is_checked()
  for v in (0,17,100):
   volume.fill(str(v));volume.dispatch_event('input');assert p.evaluate('document.querySelector(".bf-global-audio audio").volume')==v/100
   assert p.locator('#bf-session-volume-value').inner_text()==str(v)+'%'
  volume.focus();p.keyboard.press('ArrowLeft');assert volume.input_value()=='99'
  mute.check();assert p.evaluate('document.querySelector(".bf-global-audio audio").muted') is True
  mute.uncheck();assert p.evaluate('document.querySelector(".bf-global-audio audio").muted') is False
  p.evaluate('document.querySelector(".bf-global-audio audio").volume=.23');p.wait_for_function('document.querySelector("#bf-session-volume-value").textContent==="23%"')
  assert p.evaluate('__plays')==0 and p.evaluate('BFGlobalAudio.track')=='' and p.evaluate('BFGlobalAudio.playingMode') is None, p.evaluate('({plays:__plays,track:BFGlobalAudio.track,mode:BFGlobalAudio.playingMode})')
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert volume.bounding_box()['height']>=44
  assert_unchanged(p,before,width);assert p.evaluate('JSON.stringify(S)')==battle
  p.locator('.bf-navbar [data-bf-goto="home"]').click();assert not panel.is_visible();assert not errors,errors
  p.close();print('PASS',width,'volume/mute/keyboard/external sync, no autoplay/P/S/storage writes')
 # New document starts at original session defaults; unavailable player is disabled.
 p=b.new_page();p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE);p.set_content((A/'index.html').read_text());p.add_script_tag(content=J.split(MARK,1)[0]);assert p.evaluate('document.querySelector(".bf-global-audio audio").volume')==.42
 p.evaluate('document.querySelector(".bf-global-audio audio").remove()');p.add_script_tag(content=MARK+MODULE)
 assert p.locator('#bf-session-volume').is_disabled() and p.locator('#bf-session-mute').is_disabled()
 p.add_script_tag(content=MARK+MODULE);assert p.locator('#bf-menu-settings').count()==1
 p.close();b.close()
print('PASS fresh session defaults, missing player and duplicate injection')
