"""v0.39 — opt-in, read-only Evolution Roadmap using existing source-verified recipes.

Never rewrites evolution tables, quest rewards, save key/schema or battle mechanics.
Build-time injection is repeatable and fails closed if the verified v0.38 source
is absent. UI code treats archived recipe IDs as data, never executable markup.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
HTML = ROOT / "app/src/main/assets/index.html"
s = HTML.read_text("utf-8")
assert s.count("/* BF_GLOBAL_OTHER_SIX_STAR_V038 */") == 1, "Expected verified v0.38 base"
assert "bf_global_offline_demo_v7" in s
MARK = "/* BF_EVOLUTION_ROADMAP_V039 */"
JS = r"""
/* BF_EVOLUTION_ROADMAP_V039 */
(() => {
  'use strict';
  // v0.39 is informational QoL, NOT an original Global gameplay rule.
  // Do not edit P, call saveProgress, or add fields to save schema v7.
  let selectedBase = null;
  let queued = false;
  const id = 'bf-evolution-roadmap-v039';
  const fmt = n => Number(n || 0).toLocaleString('en-US');
  function ready() {
    return typeof P !== 'undefined' &&
           typeof EVO_RECIPES !== 'undefined' &&
           typeof UNIT_BY_ID !== 'undefined' &&
           typeof effectiveUnit === 'function' &&
           Array.isArray(P.roster) && Array.isArray(EVO_RECIPES);
  }
  function getPlan(base) {
    if (!ready() || !P.roster.some(n => Number(n) === base)) return null;
    const current = effectiveUnit(base);
    if (!current) return null;
    const next = EVO_RECIPES.find(r =>
      Number(r.baseId) === base && Number(r.fromId) === Number(current.id));
    if (!next) return {base, current, complete:true};
    const target = UNIT_BY_ID.get(Number(next.evolvedId));
    if (!target) return {base, current, unavailable:true};
    const inventory = P.materials || {};
    const materials = Object.entries(next.materials || {})
      .map(([itemId, count]) => {
        const required = Number(count);
        const owned = Math.max(0, Number(inventory[itemId]) || 0);
        return {itemId, required, owned, missing:Math.max(0, required - owned)};
      }).sort((a,b) => Number(a.itemId) - Number(b.itemId));
    return {base, current, next, target, materials,
      demoZel:Number(next.demoZel || 0), archivedZel:Number(next.archivedZel || 0)};
  }
  // Exposed only for deterministic browser regression inspection.
  window.BF_EvolutionRoadmapV039 = Object.freeze({plan:getPlan});
  function el(tag, cls, value) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (value !== undefined) node.textContent = value;
    return node;
  }
  function update() {
    const root = document.getElementById(id);
    if (!root || !root.open || !ready()) return;
    const pick = root.querySelector('select');
    const body = root.querySelector('.bf039-body');
    const owned = [...new Set(P.roster.map(Number))]
      .filter(x => Number.isSafeInteger(x) && UNIT_BY_ID.has(x));
    if (!owned.length) {
      pick.replaceChildren();
      body.replaceChildren(el('p', '', 'No owned units yet.'));
      return;
    }
    if (!owned.includes(selectedBase)) selectedBase = owned[0];
    const choices = owned.map(base => {
      const form = effectiveUnit(base) || UNIT_BY_ID.get(base);
      const o = el('option', '', form.name + ' · #' + base);
      o.value = String(base);
      return o;
    });
    pick.replaceChildren(...choices);
    pick.value = String(selectedBase);
    const plan = getPlan(selectedBase);
    body.replaceChildren();
    if (!plan) {body.append(el('p', '', 'Evolution details unavailable.'));return;}
    if (plan.complete) {
      body.append(el('p', '', plan.current.name +
        ' — no further evolution currently implemented for this unit.'));
      return;
    }
    if (plan.unavailable) {
      body.append(el('p', '', 'Verified next form not available in this build.'));
      return;
    }
    body.append(el('p', 'bf039-heading', plan.current.name + ' → ' +
      plan.target.name + ' (' + fmt(plan.next.sourceRarity) + '★ → ' +
      fmt(plan.next.targetRarity) + '★)'));
    const zelHave = Math.max(0, Number(P.zel) || 0);
    body.append(el('p', '', 'DEMO Zel: ' + fmt(zelHave) + ' / ' +
      fmt(plan.demoZel) + (zelHave < plan.demoZel
        ? ' — missing ' + fmt(plan.demoZel - zelHave) : ' — enough Zel')));
    body.append(el('p', '', 'Original Global source recipe: ' +
      fmt(plan.archivedZel) + ' Zel (reference only; not charged).'));
    const ul = el('ul', 'bf039-materials');
    for (const item of plan.materials) {
      ul.append(el('li', item.missing ? 'bf039-missing' : 'bf039-have',
        'Material #' + item.itemId + ': ' + fmt(item.owned) + ' / ' +
        fmt(item.required) + (item.missing ? ' — missing ' + fmt(item.missing) : ' ✓')));
    }
    body.append(ul);
    body.append(el('p', 'bf039-note',
      'DEMO training Lv.2 is also required. This guide is read-only; evolve in the regular Evolution Lab.'));
    body.append(el('p', 'bf039-note',
      'Some catalysts are awarded at per-quest DEMO clear milestones (6, 12, 18, 24, 30, 36). These are not original enemy drop rates.'));
  }
  function mount() {
    if (!ready()) return;
    const first = document.querySelector('.evocard');
    if (!first || !first.parentElement) return;
    const parent = first.parentElement;
    let root = document.getElementById(id);
    if (root && root.parentElement === parent) return;
    if (root) root.remove();
    root = el('details');
    root.id = id;
    root.append(el('summary', '', 'EVOLUTION ROADMAP · DEMO GUIDE'));
    const wrapper = el('div', 'bf039-content');
    const label = el('label', '', 'Owned unit ');
    const pick = el('select');
    pick.setAttribute('aria-label', 'Choose owned unit for next evolution');
    label.append(pick);
    wrapper.append(label, el('div', 'bf039-body'));
    root.append(wrapper);
    root.addEventListener('toggle', update);
    pick.addEventListener('change', () => {
      selectedBase = Number(pick.value);
      update();
    });
    parent.insertBefore(root, first);
  }
  function scheduleMount() {
    if (queued) return;
    queued = true;
    queueMicrotask(() => {queued = false; mount();});
  }
  function initialize() {
    mount();
    const observer = new MutationObserver(mutations => {
      if (mutations.every(m => m.target.nodeType === 1 &&
          m.target.closest && m.target.closest('#' + id))) return;
      scheduleMount();
    });
    observer.observe(document.body, {childList:true,subtree:true});
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded',initialize,{once:true});
  } else initialize();
})();
"""
CSS = r"""
<style id="bf039-evo-roadmap-style">
#bf-evolution-roadmap-v039 { margin:10px 4px 14px; padding:10px 12px;
 border:1px solid rgba(255,201,95,.65); border-radius:9px; color:#f7eddf;
 background:linear-gradient(160deg,#3c2b18,#201d1b); font-size:13px }
#bf-evolution-roadmap-v039 summary { cursor:pointer; font-weight:750;
 color:#ffd27f; letter-spacing:.4px; padding:4px 0 }
#bf-evolution-roadmap-v039 .bf039-content { padding:10px 0 4px }
#bf-evolution-roadmap-v039 select { max-width:100%; min-width:150px;
 padding:6px; font:inherit; color:#fff; background:#272727; border:1px solid #a78046;
 border-radius:5px }
#bf-evolution-roadmap-v039 p { margin:8px 0; line-height:1.4 }
#bf-evolution-roadmap-v039 .bf039-heading { font-weight:700; color:#ffe2a7 }
#bf-evolution-roadmap-v039 .bf039-materials { padding-left:20px; margin:8px 0 }
#bf-evolution-roadmap-v039 .bf039-materials li { margin:4px 0 }
#bf-evolution-roadmap-v039 .bf039-missing { color:#ffb5a9 }
#bf-evolution-roadmap-v039 .bf039-have { color:#b2e3b3 }
#bf-evolution-roadmap-v039 .bf039-note { opacity:.85; font-size:12px }
</style>
"""
snippet = CSS + "\n<script>\n" + JS + "\n</script>\n"
if s.count(MARK) == 1:
    assert s.count('id="bf039-evo-roadmap-style"') == 1
    print("v0.39 Evolution Roadmap already staged")
elif s.count(MARK) == 0:
    assert s.count("</body>") == 1, "Unexpected HTML body boundary"
    HTML.write_text(s.replace("</body>",snippet+"</body>",1),"utf-8")
    print("Staged optional v0.39 Evolution Roadmap; schema v7 untouched")
else:
    raise SystemExit("Duplicate v0.39 patch marker")
