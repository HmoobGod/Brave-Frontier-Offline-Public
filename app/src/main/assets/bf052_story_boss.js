/* BF_MISTRAL_BOSS_INTEL_V052 */
(() => {
  'use strict';
  if (window.BF052BossIntel) return;
  // Source identities are historical community records, NOT decoded 2022 spawn tables.
  const archive = Object.freeze(__BOSS_SOURCE_JSON__);
  const byMission = new Map(archive.entries.map(row => [row.missionId, row]));
  const reference = document.getElementById('questinfo');
  if (!reference) return;

  const panel = document.createElement('section');
  panel.id = 'bf052-boss-intel';
  panel.setAttribute('aria-label', 'Historical Global boss references');
  const heading = document.createElement('strong');
  heading.textContent = 'BOSS RESEARCH · HISTORICAL GLOBAL RECORD';
  const summary = document.createElement('p');
  const details = document.createElement('p');
  const scope = document.createElement('small');
  scope.textContent = 'Original boss identities are research references. Unverified enemy waves, AI, ATK/DEF, damage, capture and drops remain DEMO.';
  const control = document.createElement('label');
  control.className = 'bf052-toggle';
  const toggle = document.createElement('input');
  toggle.type = 'checkbox';
  toggle.id = 'bf052-enable-original-juggernaut';
  toggle.checked = false; // session-only opt-in; never change the persisted v7 save.
  const title = document.createElement('span');
  title.textContent = 'Experimental: original 50,000-HP Juggernaut in Mission 85 final wave (demo AI/ATK/DEF)';
  control.append(toggle, title);
  const notice = document.createElement('small');
  notice.textContent = 'Off by default. Changing this option restarts the current battle; it does not save the setting.';
  const link = document.createElement('a');
  link.href = archive.provenance.sourceUrl;
  link.textContent = 'Historical Global wiki boss reference';
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  panel.append(heading, summary, details, scope, control, notice, link);
  reference.after(panel);
  const css = document.createElement('style');
  css.textContent = '#bf052-boss-intel{margin:8px 3px;padding:10px;border:1px solid #9c7445;border-radius:8px;background:#1c1b25;color:#f2eadf;font:12px/1.4 system-ui,sans-serif}' +
    '#bf052-boss-intel p{margin:5px 0}' +
    '#bf052-boss-intel strong{color:#f7ce93;letter-spacing:.35px}' +
    '#bf052-boss-intel small{display:block;opacity:.85;margin:5px 0}' +
    '#bf052-boss-intel .bf052-toggle{display:flex;align-items:flex-start;gap:7px;margin:10px 0;color:#ffe0ae}' +
    '#bf052-boss-intel input{margin-top:2px;flex-shrink:0}' +
    '#bf052-boss-intel a{color:#95c8ff}';
  document.head.append(css);

  function current() {
    return typeof QUEST === 'undefined' ? null : byMission.get(QUEST.missionId);
  }
  function refresh() {
    const row = current();
    panel.hidden = !row;
    if (!row) return;
    const label = row.bosses.map(b => b.name + (b.count ? ' ×' + b.count : '') +
      (b.hp ? ' · ' + b.hp.toLocaleString('en-US') + ' HP (historical)' : '')).join(' | ');
    summary.textContent = 'Mission ' + row.missionId + ': ' + label;
    details.textContent = row.notes.join(' · ');
    control.hidden = row.missionId !== 85;
    notice.hidden = row.missionId !== 85;
  }

  const boss = byMission.get(85)?.bosses?.[0];
  function encounter(missionId, waveIndex, totalWaves, mode, fallback) {
    if (!toggle.checked || missionId !== 85 || mode !== 'archive' ||
        waveIndex !== totalWaves - 1 || !boss || boss.name !== 'Juggernaut' ||
        boss.hp !== 50000 || boss.monsterGraphicId !== '0001' ||
        boss.bundledSpriteKey !== 'gel' ||
        window.BF_MONSTER_DATA?.monster?.gel?.id !== '0001' ||
        !Array.isArray(fallback) || fallback.length < 1) return null;
    const base = fallback[0];
    // Only name, sprite, element and HP are evidenced; attacking/defense stay DEMO.
    return [{id:'gel', name:'Juggernaut · demo combat',
      element:'Thunder', maxHp:boss.hp, atk:base.atk, def:base.def,
      sourceBackedBoss:true}];
  }

  toggle.addEventListener('change', () => {
    const state = window.BF_debug?.state();
    if (state?.busy) {
      toggle.checked = !toggle.checked;
      notice.textContent = 'Cannot change boss encounter while an action is executing.';
      return;
    }
    notice.textContent = 'Setting is session-only. The battle has restarted (existing v7 save unchanged).';
    window.BF_debug?.reset();
    refresh();
  });
  // Core gameplay updates questinfo using textContent after quest changes.
  new MutationObserver(refresh).observe(reference, {childList:true,subtree:false});
  window.BF052BossIntel = Object.freeze({
    entries:archive.entries,
    encounter,
    get enabled() { return toggle.checked; },
    refresh
  });
  refresh();
})();
