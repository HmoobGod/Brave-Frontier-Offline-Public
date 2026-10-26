"""Verified original BF1 music assets and strictly opt-in offline audio playback.

Source MP3 bytes must match the archived Global sound pack SHA256 and be
bundled directly inside the APK. Uses a disposable browser/save and mocks
HTMLAudioElement.play() so CI doesn't require an audio output device.
"""
from pathlib import Path
import json,hashlib,shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
DATA=json.loads((ROOT/"source_data/bf_global_original_bgm.json").read_text("utf-8"))
assert DATA["schema"]=="bf-global-original-quest-audio-v1"
assert len(DATA["tracks"])==3
assert sorted(sum((t["missionIds"] for t in DATA["tracks"]),[]))==[1,2,10,11,12,20,21,22,23]
for row in DATA["tracks"]:
    original=ROOT/"source_assets/bf1/audio"/row["file"]
    bundled=ASSETS/"content/sound"/row["file"]
    assert original.read_bytes()==bundled.read_bytes(),row["file"]
    assert hashlib.sha256(bundled.read_bytes()).hexdigest()==row["sha256"]
    assert bundled.stat().st_size==row["bytes"]
    assert bundled.read_bytes().startswith(b"ID3")
print("PASS authentic Global MP3 bytes, archive hashes and full nine-mission music mapping")

with sync_playwright() as pw:
    browser=pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda err:errors.append(str(err)))
    def serve(route):
        relative=route.request.url.split("bf-assets.test/",1)[-1]
        file=ASSETS/relative
        mime="audio/mpeg" if file.suffix==".mp3" else "image/png" if file.suffix==".png" else "image/jpeg"
        if file.is_file() and file.resolve().is_relative_to(ASSETS.resolve()) and file.suffix in (".png",".jpg",".mp3"):
            route.fulfill(status=200,body=file.read_bytes(),content_type=mime)
        else:
            route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",serve)
    page.evaluate("""() => {
      const backing={};
      Object.defineProperty(window,"localStorage",{configurable:true,value:{
        getItem(k){return backing[k]??null},
        setItem(k,v){backing[k]=String(v)},
        removeItem(k){delete backing[k]},
        key(n){return Object.keys(backing)[n]??null},
        get length(){return Object.keys(backing).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
      window.__playCalls=0;window.__pauseCalls=0;
      HTMLMediaElement.prototype.play=function(){
        window.__playCalls++;
        return Promise.resolve();
      };
      HTMLMediaElement.prototype.pause=function(){window.__pauseCalls++;};
      HTMLMediaElement.prototype.load=function(){};
    }""")
    html=(ASSETS/"index.html").read_text("utf-8").replace(
        "<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    before=page.evaluate("""() => ({
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      zel:P.zel,questClears:JSON.stringify(P.questClears),
      save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    assert page.evaluate("window.__playCalls")==0
    assert page.evaluate("BFGlobalAudio.playingMode") is None
    assert page.evaluate("BFGlobalAudio.selectedTrack")=="bf010_map_grass.mp3"
    assert page.evaluate("BFGlobalAudio.track")==""
    assert page.locator("#bf-global-play-track").is_hidden()
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.locator("#bf-global-play-track").is_visible()
    assert page.evaluate("window.__playCalls")==0
    assert "prairie" in page.locator("#bf-global-track-label").inner_text().lower()
    page.locator("#bf-global-play-track").click()
    assert page.evaluate("window.__playCalls")==1
    assert page.evaluate("BFGlobalAudio.playingMode")=="quest"
    assert page.evaluate("BFGlobalAudio.track")=="content/sound/bf010_map_grass.mp3"
    assert page.locator("#bf-global-stop-track").is_enabled()

    page.evaluate("""() => {
      P.questClears[1]=1;P.questClears[2]=1;P.questClears[10]=1;
      P.questClears[11]=1;P.questClears[12]=1;
      renderQuestList();
    }""")
    page.locator('[data-bf-mission="20"]').click()
    page.wait_for_function("BFGlobalAudio.track.includes('bf011_map_firecave.mp3')")
    assert page.evaluate("BFGlobalAudio.selectedTrack")=="bf011_map_firecave.mp3"
    assert page.evaluate("BFGlobalAudio.playingMode")=="quest"
    assert page.evaluate("window.__playCalls")>=2
    print("PASS original prairie/cave soundtrack follows actual selected quest")

    page.locator("#bf-global-boss-preview").click()
    assert page.evaluate("BFGlobalAudio.playingMode")=="boss"
    assert page.evaluate("BFGlobalAudio.track")=="content/sound/bf006_btl_boss.mp3"
    assert page.locator("#bf-global-audio-status").is_visible()
    page.locator("#bf-global-stop-track").click()
    assert page.evaluate("BFGlobalAudio.playingMode") is None
    assert page.evaluate("BFGlobalAudio.track")==""
    assert page.locator("#bf-global-stop-track").is_disabled()
    # Changing mission while OFF must not reactivate audio.
    count=page.evaluate("window.__playCalls")
    page.locator('[data-bf-mission="10"]').click()
    assert page.evaluate("window.__playCalls")==count
    page.locator("#bf-global-play-track").click()
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert page.evaluate("BFGlobalAudio.playingMode") is None
    assert page.evaluate("BFGlobalAudio.track")==""
    print("PASS manual boss preview, stop and auto-pause when leaving Quest")

    # Changes to a selected quest are normal core save writes, but no
    # separate audio preferences are permitted in schema v7.
    after=page.evaluate("""() => ({
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),zel:P.zel,
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Array.from({length:localStorage.length},(_,i)=>localStorage.key(i))
    })""")
    assert after["squad"]==before["squad"]
    assert after["roster"]==before["roster"]
    assert after["zel"]==before["zel"]
    assert after["keys"]==['bf_global_offline_demo_v7']
    assert not errors,errors
    print("PASS no autoplay, no music-related save keys or game mutations, no JS errors")
    browser.close()
