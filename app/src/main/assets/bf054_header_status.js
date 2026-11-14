/* BF_HEADER_STATUS_FIDELITY_V054 */
(() => {
  'use strict';
  if (window.BF054HeaderStatus) return;
  const header = document.querySelector('.bf-shell-head');
  if (!header || !document.getElementById('plevel') || !document.getElementById('pexp')) return;

  // Archived header_ui3.png is a UI atlas: its bottom 32px contains unrelated
  // orange, green and black sprite strips, NOT progress meters. Crop at y=174.
  // Keep the original 644px-wide graphic unmodified in the APK.
  const style = document.createElement('style');
  style.id = 'bf054-header-style';
  style.textContent = [
    '.bf-shell-head{aspect-ratio:644/174!important;background-size:100% auto!important;',
    'background-position:center top!important;background-repeat:no-repeat!important;overflow:hidden!important}',
    '.bf-shell-head .bf-global-level{top:29%!important;left:22%!important}',
    '.bf-shell-head .bf-global-zel{top:42%!important}',
    '.bf-shell-head .bf-global-karma{top:60%!important}',
    '#bf054-exp{position:absolute;left:8.3%;top:43.7%;width:20.6%;height:10.8%;',
    'border-radius:7px;overflow:hidden;background:#091e2b;border:1px solid #5e8ab0;',
    'box-shadow:inset 0 1px 3px #000a}',
    '#bf054-exp-fill{position:absolute;left:0;top:0;bottom:0;width:0%;',
    'background:linear-gradient(180deg,#baf4ff,#269bd2 65%,#12639e);',
    'transition:width .15s linear}',
    '#bf054-exp-text{position:absolute;inset:0;display:flex;align-items:center;',
    'justify-content:center;color:#fff;font:700 clamp(8px,2vw,11px) Arial,sans-serif;',
    'white-space:nowrap;text-shadow:0 1px 2px #000,0 0 3px #000}',
    '#bf054-energy{position:absolute;left:8.3%;top:61%;width:20.6%;height:10%;',
    'display:flex;align-items:center;justify-content:center;color:#e1e6eb;',
    'font:700 clamp(8px,2vw,11px) Arial,sans-serif;text-shadow:0 1px 2px #000}',
    '#bf054-home-details{margin:8px 0;padding:7px 10px;border:1px solid #a88d62;',
    'border-radius:7px;background:linear-gradient(145deg,#27374c,#19253b);',
    'color:#f3e2c2;font:12px/1.5 Arial,sans-serif}',
    '#bf054-home-details summary{min-height:44px;display:flex;align-items:center;',
    'cursor:pointer;font-weight:800;letter-spacing:.03em;list-style-position:inside}',
    '#bf054-home-details summary:focus-visible{outline:3px solid #9fdbff;outline-offset:2px}',
    '#bf054-home-details p{margin:5px 0 2px;overflow-wrap:anywhere}',
    '@media(max-width:360px){#bf054-exp-text,#bf054-energy{font-size:8px}}'
  ].join('');
  document.head.append(style);

  const track = document.createElement('div');
  track.id = 'bf054-exp';
  track.setAttribute('role', 'progressbar');
  track.setAttribute('aria-label', 'Offline demo summoner experience toward next level');
  const fill = document.createElement('span');
  fill.id = 'bf054-exp-fill';
  const label = document.createElement('span');
  label.id = 'bf054-exp-text';
  track.append(fill,label);
  const energy = document.createElement('span');
  energy.id = 'bf054-energy';
  energy.textContent = '— / —';
  energy.title = 'Energy is not simulated in this offline build; no balance is stored or deducted.';
  energy.setAttribute('aria-label', 'Energy unavailable: offline demo does not simulate energy');
  header.append(track,energy);

  // Optional native Home details disclosure: read existing local player state
  // without changing the original BF1 header sprite or canonical v7 save.
  const home = document.getElementById('bf-home');
  const homeTitle = home?.querySelector('.bf-scene-title');
  const homeDetails = homeTitle ? document.createElement('details') : null;
  let homeValues = null;
  if (homeDetails) {
    homeDetails.id = 'bf054-home-details';
    const label = document.createElement('summary');
    label.textContent = 'SUMMONER STATUS · DETAILS';
    homeValues = document.createElement('p');
    homeValues.id = 'bf054-home-values';
    homeValues.setAttribute('aria-live', 'polite');
    homeDetails.append(label,homeValues);
    homeTitle.after(homeDetails);
  }
  // v401: On narrow phones, the playable original-art Quest and Summon
  // location tiles should come before the growing read-only squad/status
  // detail stack. Reorder EXISTING nodes (not clones/CSS order), so the
  // visual, keyboard, and screen-reader orders stay aligned. Wider phones
  // retain the accepted original reconstructed Home order.
  const sceneSquad = home?.querySelector('.bf-scene-squad');
  const sceneExplore = home?.querySelector('.bf-scene-explore');
  const sceneTools = home?.querySelector('.bf-scene-tools');
  const compactHome = typeof window.matchMedia === 'function' ?
    window.matchMedia('(max-width:370px)') : null;
  // #420 places its optional 2022 mission preview immediately after the
  // Adventure region. Keep the two nodes adjacent when screen width changes.
  // No extra Home art is cloned, no route is clicked, no player state is saved.
  function adjacentPreview() {
    const panel=home?.querySelector('#bf420-home-readiness');
    return panel?.parentElement===home ? panel : null;
  }
  function syncNarrowHome() {
    if (!home || !sceneSquad || !sceneExplore || !sceneTools || !compactHome)
      return false;
    const preview=adjacentPreview();
    if (compactHome.matches) {
      // Put the two real playable Quest/Summon tiles ahead of the expanding
      // squad/story stack; the optional preview always follows Adventure.
      home.insertBefore(sceneExplore,sceneSquad);
      if (preview) home.insertBefore(preview,sceneSquad);
    } else {
      // Restore DOM/keyboard order on larger phones, including the optional
      // preview. Move the actual existing nodes, never duplicate controls.
      home.insertBefore(sceneExplore,sceneTools);
      if (preview) home.insertBefore(preview,sceneTools);
    }
    return compactHome.matches;
  }
  if (compactHome) {
    if (typeof compactHome.addEventListener === 'function')
      compactHome.addEventListener('change',syncNarrowHome);
    else if (typeof compactHome.addListener === 'function')
      compactHome.addListener(syncNarrowHome);
    syncNarrowHome();
  }
  const safeCount = x => Number.isSafeInteger(x) && x >= 0 ?
    x.toLocaleString('en-US') : '—';

  function summary() {
    // Never invent level-one EXP for a malformed canonical v7 player.
    // This observer is read-only: invalid values are unavailable, not fixed.
    // v456: the core EXP meter is cumulative across levels. A level 2+
    // player cannot have less EXP than was required to reach that level.
    // Never turn impossible local progress into a plausible 0/next bar.
    const levelFloor = typeof P !== 'undefined' &&
      Number.isSafeInteger(P?.level) && P.level>=1 && P.level<=99 ?
        5*(P.level-1)*P.level/2 : null;
    const valid = typeof P !== 'undefined' && P?.version===7 &&
      levelFloor!==null &&
      Number.isSafeInteger(P.exp) && P.exp>=levelFloor;
    if(!valid)return {valid:false,level:null,total:null,
      threshold:1,earned:0,percent:0,capped:false};
    const level=P.level,total=P.exp;
    const threshold = Math.max(1,5*level);
    const earned = Math.max(0, Math.min(threshold,total-5*(level-1)*level/2));
    const capped = level >= 99;
    return {valid:true,level, total, threshold, earned:capped?threshold:earned,
      percent:capped?100:Math.min(100,Math.max(0,earned/threshold*100)), capped};
  }
  function refresh() {
    const value = summary();
    const lv = document.getElementById('bf-nav-level');
    const zel = document.getElementById('bf-nav-zel');
    const karma = document.getElementById('bf-nav-karma');
    const plevel = document.getElementById('plevel');
    const pzel = document.getElementById('pzel');
    const pkarma = document.getElementById('pkarma');
    // v460 HOME: source #plevel/#pzel/#pkarma text can lag a bad import
    // or a stale render. Never echo it as trusted v7 account state.
    const player = typeof P !== 'undefined' && P?.version===7 ? P : null;
    if (lv) lv.textContent = value.valid ? String(value.level) : '—';
    if (zel) zel.textContent = player ? safeCount(player.zel) : '—';
    if (karma) karma.textContent = player ? safeCount(player.karma) : '—';
    fill.style.width = value.percent.toFixed(2)+'%';
    label.textContent = !value.valid?'— / —':value.capped?'MAX':
      value.earned+' / '+value.threshold;
    track.setAttribute('aria-valuemin','0');
    track.setAttribute('aria-valuemax',String(value.threshold));
    track.setAttribute('aria-valuenow',String(value.earned));
    track.setAttribute('aria-valuetext', !value.valid?
      'Demo summoner experience unavailable: invalid local state':
      value.capped?'Demo maximum level 99':
        value.earned+' of '+value.threshold+' demo EXP');
    if (homeValues) {
      const p = typeof P !== 'undefined' && P?.version===7 ? P : {};
      const text = (value.valid?'Demo Lv.'+safeCount(p.level)+' · EXP '+
        (value.capped?'MAX':safeCount(value.earned)+'/'+safeCount(value.threshold)):
        'Demo Lv./EXP unavailable (invalid local state)')+
        ' · Zel '+safeCount(p.zel)+' · Karma '+safeCount(p.karma)+
        ' · Energy unavailable (offline, not deducted).';
      if (homeValues.textContent !== text) homeValues.textContent = text;
    }
  }
  const progress = document.getElementById('pexp');
  // Core renderProgress updates #pexp and #plevel whenever quest rewards,
  // import, reset or leveling changes. Observe only core text, not our HUD.
  const observer = new MutationObserver(refresh);
  for (const id of ['pexp','plevel','pzel','pkarma']) {
    const element = document.getElementById(id);
    if (element) observer.observe(element,{childList:true,characterData:true,subtree:true});
  }
  // go() can copy stale core text into the nav header after a route change.
  // Revalidate the actual player on that same synchronous route event.
  window.addEventListener('bf-route-change', refresh);
  refresh();
  window.BF054HeaderStatus = Object.freeze({
    refresh,
    get state(){return summary()},
    get energyAvailable(){return false},
    get originalHeaderCropped(){return true}
  });
})();
