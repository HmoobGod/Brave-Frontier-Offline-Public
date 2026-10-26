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

  function summary() {
    const level = typeof P !== 'undefined' && Number.isInteger(P.level) ? P.level : 1;
    const total = typeof P !== 'undefined' && Number.isFinite(P.exp) ? P.exp : 0;
    const threshold = Math.max(1,5*level);
    const earned = Math.max(0, Math.min(threshold,total-5*(level-1)*level/2));
    const capped = level >= 99;
    return {level, total, threshold, earned:capped?threshold:earned,
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
    if (lv && plevel) lv.textContent = plevel.textContent || String(value.level);
    if (zel && pzel) zel.textContent = pzel.textContent || '0';
    if (karma && pkarma) karma.textContent = pkarma.textContent || '0';
    fill.style.width = value.percent.toFixed(2)+'%';
    label.textContent = value.capped ? 'MAX' : value.earned+' / '+value.threshold;
    track.setAttribute('aria-valuemin','0');
    track.setAttribute('aria-valuemax',String(value.threshold));
    track.setAttribute('aria-valuenow',String(value.earned));
    track.setAttribute('aria-valuetext', value.capped
      ? 'Demo maximum level 99' : value.earned+' of '+value.threshold+' demo EXP');
  }
  const progress = document.getElementById('pexp');
  // Core renderProgress updates #pexp and #plevel whenever quest rewards,
  // import, reset or leveling changes. Observe only core text, not our HUD.
  const observer = new MutationObserver(refresh);
  for (const id of ['pexp','plevel','pzel','pkarma']) {
    const element = document.getElementById(id);
    if (element) observer.observe(element,{childList:true,characterData:true,subtree:true});
  }
  refresh();
  window.BF054HeaderStatus = Object.freeze({
    refresh,
    get state(){return summary()},
    get energyAvailable(){return false},
    get originalHeaderCropped(){return true}
  });
})();
