'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const {_android} = require(process.env.BF_PLAYWRIGHT_PACKAGE);
const serial = 'emulator-5556';
const pkg = 'org.bravefrontier.offline.diagnostic';
const component = process.env.BF_TEST_COMPONENT;
assert.match(component || '', /^org\.bravefrontier\.offline\.diagnostic\/[A-Za-z0-9_.]+$/);
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const adb = (...args) => execFileSync(process.env.BF_TEST_ADB,
  ['-s', serial, ...args], {encoding:'utf8',timeout:60000}).trim();
assert.equal(adb('shell','getprop','ro.kernel.qemu'),'1');

(async () => {
  // No automatic Playwright helper APK installation on detected devices.
  const devices = await _android.devices({omitDriverInstall:true});
  assert.equal(devices.length,1,'Only the dedicated emulator may be connected');
  const device = devices[0];
  assert.equal(device.serial(),serial,'Unexpected Android target');
  try {
    const web = await device.webView({pkg});
    const page = await web.page();
    page.setDefaultTimeout(120000);
    await page.waitForFunction(() => !document.hidden && typeof P !== 'undefined' && P.version === 7 &&
      window.BF_homeNav && window.BF041SmartAuto?.pauseForBackground &&
      window.BFGlobalQoLBattleSpeedV9900 && window.BFGlobalSBBFallbackDispatch && window.BFGlobalAudio,
      null, {polling:100});
    const snapshot = () => page.evaluate(() => JSON.stringify({
      player:JSON.stringify(P),canonical:localStorage.getItem('bf_global_offline_demo_v7')
    }));
    const before = hash(await snapshot());
    await page.evaluate(()=>BF_homeNav.go('quest'));
    const startQuestMusic=async()=>{
      await page.locator('#bf-global-play-track').click();
      await page.waitForFunction(()=>BFGlobalAudio.playingMode==='quest' &&
        BFGlobalAudio.playing && document.querySelector('.bf-global-audio audio').currentTime>0,
        null,{polling:100});
    };
    await startQuestMusic();
    await page.locator('#bf-global-stop-track').click();
    // Both real UI handlers run before the first play promise can settle.
    await page.evaluate(()=>{
      document.getElementById('bf-global-play-track').click();
      document.getElementById('bf-global-boss-preview').click();
    });
    await page.waitForFunction(()=>BFGlobalAudio.playingMode==='boss' &&
      BFGlobalAudio.playing && document.querySelector('.bf-global-audio audio').currentTime>0,
      null,{polling:100});
    await page.locator('#bf-global-stop-track').click();
    await startQuestMusic();
    const round = await page.evaluate(() => {
      BF_homeNav.go('quest');
      for(const unit of S.party){
        unit.active=unit.id===0;unit.action=null;unit.bb=0;
        unit.hp=unit.maxHp=100000;unit.atk=100;
      }
      S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
        maxHp:100000000,def:100,atk:1}];
      window.__nativeHidden=[];window.__nativePause=[];
      window.addEventListener('bf-native-background',()=>{
        __nativePause.push({auto:S.auto,checked:E.auto.checked,hidden:document.hidden});
      });
      document.addEventListener('visibilitychange',()=>{
        if(document.hidden)__nativeHidden.push({auto:S.auto,checked:E.auto.checked});
      });
      E.speed.value='1';E.auto.checked=true;
      E.auto.dispatchEvent(new Event('change'));
      return S.round;
    });
    // Actual Android HOME / Activity pause and return, not a synthetic DOM event.
    adb('shell','input','keyevent','KEYCODE_HOME');
    await new Promise(resolve=>setTimeout(resolve,2000));
    adb('shell','am','start','-W','-n',component);
    await page.waitForFunction(() => !document.hidden && !S.busy, null, {polling:100});
    const state = await page.evaluate(() => ({events:__nativeHidden,nativeEvents:__nativePause,
      auto:S.auto,checked:E.auto.checked,timer:timer,round:S.round,over:S.over,
      musicMode:BFGlobalAudio.playingMode,musicTrack:BFGlobalAudio.track,
      musicPlaying:BFGlobalAudio.playing,
      sdkBrowser:/Chrome\/([\d.]+)/.exec(navigator.userAgent)?.[1] || 'unknown'}));
    console.log(JSON.stringify({scope:'Android background observations',
      nativeCallbacks:state.nativeEvents.length,domHiddenEvents:state.events.length,
      auto:state.auto,checked:state.checked,roundDelta:state.round-round,
      browserVersion:state.sdkBrowser}));
    assert.ok(state.nativeEvents.length>0,'Native Activity pause callback was not observed');
    assert.ok(state.nativeEvents.every(event=>event.auto===false && event.checked===false),
      'Auto controls stayed enabled after native background notification');
    assert.equal(state.auto,false);assert.equal(state.checked,false);
    assert.equal(state.timer,null);assert.equal(state.over,false);
    assert.equal(state.musicMode,null);assert.equal(state.musicTrack,'');
    assert.equal(state.musicPlaying,false,'Quest music stayed active after native pause');
    assert.ok(state.round>=round && state.round<=round+1,'Unexpected extra Auto rounds');
    await new Promise(resolve=>setTimeout(resolve,1500));
    assert.equal(await page.evaluate(()=>S.round),state.round,'Auto resumed without input');
    assert.equal(await page.evaluate(()=>BFGlobalAudio.playingMode),null,'Music resumed without input');
    assert.equal(await page.evaluate(()=>BFGlobalAudio.track),'');
    await startQuestMusic();
    await page.locator('#bf-global-stop-track').click();
    assert.equal(await page.evaluate(()=>BFGlobalAudio.playingMode),null);
    assert.equal(await page.evaluate(()=>BFGlobalAudio.track),'');
    assert.equal(await page.evaluate(()=>BFGlobalAudio.playing),false);
    // Exercise the real Android key dispatch and Java-to-WebView route bridge.
    const backRoutes=['quest','units','summon','menu'];
    for(const route of backRoutes){
      assert.equal(await page.evaluate(route=>BF_homeNav.go(route),route),true);
      if(route==='quest')await startQuestMusic();
      adb('shell','input','keyevent','KEYCODE_BACK');
      await page.waitForFunction(()=>BF_homeNav.current==='home',null,{polling:100});
      if(route==='quest'){
        assert.equal(await page.evaluate(()=>BFGlobalAudio.playingMode),null,
          'Quest music intent survived native Back navigation');
        assert.equal(await page.evaluate(()=>BFGlobalAudio.track),'');
        assert.equal(await page.evaluate(()=>BFGlobalAudio.playing),false);
        await page.evaluate(()=>BF_homeNav.go('quest'));
        await new Promise(resolve=>setTimeout(resolve,500));
        assert.equal(await page.evaluate(()=>BFGlobalAudio.playingMode),null);
        assert.equal(await page.evaluate(()=>BFGlobalAudio.track),'');
        assert.equal(await page.evaluate(()=>BFGlobalAudio.playing),false,
          'Quest music restarted after returning without Play');
      }
    }
    assert.equal(hash(await snapshot()),before,'Player/canonical save changed');
    console.log(JSON.stringify({result:'PASS',scope:'isolated Android35 emulator',
      package:pkg,browserVersion:state.sdkBrowser,nativeBackgroundCallbackObserved:true,
      domHiddenEventObserved:state.events.length>0,
      foregroundAutoRemainsOff:true,nativeBackRoutesReturnedHome:backRoutes,
      questMusicDecodedBeforePause:true,questMusicStopsWithoutAutoResume:true,
      questMusicExplicitResumeAndStop:true,
      questMusicStopsOnNativeBack:true,questMusicNoRestartAfterQuestReturn:true,
      nativeQuestMusicReplacementKeepsLatest:true,
      playerAndCanonicalSaveUnchanged:true,
      ownerPhoneOrSaveTested:false}));
  } finally {
    await device.close();
  }
})().catch(error=>{console.error(error.stack || error.message);process.exitCode=1;});
