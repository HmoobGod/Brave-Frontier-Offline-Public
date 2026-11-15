/* v398: Quest route section jump bar. Reconstructed offline convenience,
 * NOT a recovered 2022 engine feature. Scroll-only: it never reads or writes
 * the canonical save, never starts, selects or auto-plays a mission, and never
 * touches battle state. Targets missing or hidden are simply not offered. */
(() => {
  'use strict';
  if (window.BFQuestSectionJumpV39800) return;
  const nav = window.BF_homeNav;
  const panel = document.querySelector('section.questpanel');
  if (!nav || typeof nav.go !== 'function' || !panel) return;

  // Label, then candidate selectors in priority order (first visible wins).
  const SECTIONS = Object.freeze([
    ['story', 'STORY', ['#bf101-story-continue']],
    ['map', 'MAP', ['.bf080-region-tabs', '.bf-mistral-map']],
    ['areas', 'AREAS', ['.bf-quest-areas']],
    ['mission', 'MISSION', ['#bf-quest-details']],
    ['live', 'LIVE RUN', ['#bf2000-run']],
    ['list', 'MISSIONS', ['#questlist']],
    ['battle', 'BATTLE', ['#battle', '.arena']],
    ['squad', 'SQUAD', ['section.squad-panel']]
  ]);

  const bar = document.createElement('nav');
  bar.id = 'bf39800-quest-jump';
  bar.setAttribute('aria-label', 'Quest sections');
  bar.style.cssText =
    'position:sticky;z-index:9;box-sizing:border-box;max-width:100%;min-width:0;' +
    'margin:0 0 8px;padding:5px;display:flex;gap:5px;overflow-x:auto;' +
    'overscroll-behavior-x:contain;scrollbar-width:thin;' +
    'border:1px solid #9b8050;border-radius:6px;' +
    'background:linear-gradient(#2b4258,#122637);box-shadow:0 3px 10px #0008';
  const buttons = new Map();
  for (const [key, label] of SECTIONS) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.bfJump = key;
    button.textContent = label;
    button.style.cssText =
      'flex:0 0 auto;min-height:44px;min-width:44px;box-sizing:border-box;' +
      'padding:4px 10px;cursor:pointer;white-space:nowrap;' +
      'font:800 12px/1 Georgia,serif;letter-spacing:.04em;color:#ffedc8;' +
      'border:2px ridge #bd995d;border-radius:5px;' +
      'background:linear-gradient(#5d5136,#263646)';
    buttons.set(key, button);
    bar.append(button);
  }
  // .questpanel clips overflow, so a sticky child could never stick: mount
  // the bar as its sibling and mirror the router's visibility for Quest.
  panel.before(bar);
  const COMBAT = new Set(['battle', 'squad']);

  function visible(el) {
    if (!el || !el.isConnected || el.closest('.bf-hidden,[hidden]')) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function target(key) {
    const entry = SECTIONS.find(s => s[0] === key);
    if (!entry) return null;
    for (const selector of entry[2]) {
      const el = document.querySelector(selector);
      if (visible(el)) return el;
    }
    return null;
  }
  function stickyTop() {
    const head = document.querySelector('.bf-shell-head');
    if (!head || getComputedStyle(head).position !== 'sticky') return 0;
    return Math.max(0, Math.round(head.getBoundingClientRect().height));
  }
  function refresh() {
    const onQuest = nav.current === 'quest' && !panel.classList.contains('bf-hidden');
    bar.hidden = !onQuest;
    bar.style.display = onQuest ? 'flex' : 'none';
    bar.setAttribute('aria-hidden', String(!onQuest));
    if (!onQuest) return;
    bar.style.top = stickyTop() + 'px';
    for (const [key, button] of buttons) button.hidden = !target(key);
    markCurrent();
  }
  function markCurrent() {
    // Fixed reading line (header + bar), independent of the bar's own
    // sticky/relative state so un-sticking can never flip the result back.
    const line = stickyTop() + bar.offsetHeight + 12;
    let current = null;
    for (const [key] of SECTIONS) {
      const el = target(key);
      if (el && el.getBoundingClientRect().top <= line) current = key;
    }
    // At the page bottom a short final section can never reach the line;
    // then the last section whose top is on screen is the one being read.
    const doc = document.documentElement;
    if (window.scrollY + window.innerHeight >= doc.scrollHeight - 2) {
      for (const [key] of SECTIONS) {
        const el = target(key);
        if (el && el.getBoundingClientRect().top < window.innerHeight) current = key;
      }
    }
    for (const [key, button] of buttons) {
      if (key === current) button.setAttribute('aria-current', 'location');
      else button.removeAttribute('aria-current');
      button.style.outline = key === current ? '2px solid #f3d99d' : '';
    }
    // Never float over live combat: stop sticking once the arena is reached.
    bar.style.position = COMBAT.has(current) ? 'relative' : 'sticky';
    const active = current && buttons.get(current);
    if (active && !active.hidden) {
      const b = bar.getBoundingClientRect(), a = active.getBoundingClientRect();
      if (a.left < b.left) bar.scrollLeft -= b.left - a.left + 5;
      else if (a.right > b.right) bar.scrollLeft += a.right - b.right + 5;
    }
  }
  function jump(key) {
    if (nav.current !== 'quest' || bar.hidden) return false;
    const el = target(key);
    if (!el) { refresh(); return false; }
    const offset = stickyTop() + (COMBAT.has(key) ? 0 : bar.getBoundingClientRect().height) + 8;
    const top = el.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo(0, Math.max(0, Math.round(top)));
    markCurrent();
    return true;
  }
  bar.addEventListener('click', event => {
    const button = event.target.closest('[data-bf-jump]');
    if (button) jump(button.dataset.bfJump);
  });
  let pending = false;
  window.addEventListener('scroll', () => {
    if (pending || nav.current !== 'quest') return;
    pending = true;
    requestAnimationFrame(() => { pending = false; markCurrent(); });
  }, {passive: true});
  window.addEventListener('resize', refresh, {passive: true});
  window.addEventListener('bf-route-change', refresh);
  refresh();
  window.BFQuestSectionJumpV39800 = Object.freeze({
    jump,
    refresh,
    get sections() { return SECTIONS.map(s => s[0]); },
    get offered() { return [...buttons].filter(([, b]) => !b.hidden).map(([k]) => k); }
  });
})();
