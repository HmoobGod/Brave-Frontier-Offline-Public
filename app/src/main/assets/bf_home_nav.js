/* Offline home navigation pilot: additive view over the unchanged v0.13.1 demo.
 * Archive sprites and exact original layout are NOT yet wired in.
 * No save fields or combat logic are introduced here.
 */
(() => {
  'use strict';
  const wrap = document.querySelector('main.wrap');
  if (!wrap || document.getElementById('bf-home')) return;
  const original = Array.from(wrap.children);
  const shell = document.createElement('div');
  shell.className = 'bf-shell-head';
  shell.innerHTML = '<div class="bf-global-level" aria-label="Summoner level">Lv <b id="bf-nav-level">1</b></div>' +
    '<div class="bf-global-zel" aria-label="Zel">Zel <b id="bf-nav-zel">0</b></div>' +
    '<div class="bf-global-karma" aria-label="Karma">Karma <b id="bf-nav-karma">0</b></div>';
  wrap.prepend(shell);
  const home = document.createElement('section');
  home.id = 'bf-home';
  home.className = 'bf-home';
  home.setAttribute('aria-label', 'Home');
  home.innerHTML =
    '<div class="bf-home-caption"><strong>GRAND GAIA</strong><small>ORIGINAL GLOBAL ART · OFFLINE DEMO</small></div>' +
    '<div class="bf-home-portals">' +
      '<button type="button" class="bf-home-portal" data-bf-goto="quest" aria-label="Quest: open demo quests"><img src="content/home/home_win_quest.png" alt="Quest" /><span>QUEST <small>Play current demo battles</small></span></button>' +
      '<div class="bf-home-portal bf-home-locked" aria-label="Vortex Gate: not implemented"><img src="content/home/home_win_gate.png" alt="Vortex Gate" /><span>VORTEX GATE <small>Not yet implemented</small></span></div>' +
    '</div>' +
    '<div class="bf-section-heading">ADVENTURE <small>Available offline</small></div>' +
    '<div class="bf-home-quick">' +
      '<button type="button" data-bf-goto="units">UNITS <span>Squad · training · evolution</span></button>' +
      '<button type="button" data-bf-goto="summon">SUMMON <span>Demo recruitment</span></button>' +
      '<button type="button" data-bf-goto="menu">MENU <span>Save · export · import</span></button>' +
    '</div>' +
    '<div class="bf-section-heading">GLOBAL LOCATIONS <small>Artwork recovered · not playable</small></div>' +
    '<div class="bf-home-upcoming">' +
      '<div class="bf-upcoming-location"><img src="content/home/home_win_arena.png" alt="Arena"/><span>Coming later</span></div>' +
      '<div class="bf-upcoming-location"><img src="content/home/home_win_raid_open.png" alt="Raid Battle"/><span>Coming later</span></div>' +
    '</div>' +
    '<p class="bf-home-notice">Header, navigation art and location art come from the archived BF1 assets. Layout and game systems remain a reconstruction. Quest and summon content are demos; inactive modes are not available yet.</p>';
  shell.insertAdjacentElement('afterend', home);
  const heading = document.createElement('div');
  heading.id = 'bf-route-title';
  heading.className = 'bf-route-title';
  heading.hidden = true;
  home.insertAdjacentElement('afterend', heading);
  const nav = document.createElement('nav');
  nav.className = 'bf-navbar';
  nav.setAttribute('aria-label', 'Main navigation');
  nav.innerHTML = [
    ['home','Home'],['units','Units'],['quest','Quest'],['summon','Summon'],['menu','Menu']
  ].map(([route,label]) => '<button type="button" data-bf-goto="' + route + '" aria-label="' + label + '"><span class="bf-nav-art bf-nav-art-' + route + '" aria-hidden="true"></span>' + label + '</button>').join('');
  document.body.append(nav);
  const routes = new Map();
  for (const element of original) {
    let route = null;
    if (element.classList.contains('progresspanel') || element.classList.contains('hit-panel') ||
        element.classList.contains('notice') || element.classList.contains('foot')) route = 'menu';
    else if (element.classList.contains('summonpanel')) route = 'summon';
    else if (element.classList.contains('squadsetup') || element.classList.contains('evo-panel') ||
             element.classList.contains('training-panel')) route = 'units';
    else if (element.classList.contains('questpanel') || element.classList.contains('squad-panel') ||
             element.classList.contains('resultpanel') || element.classList.contains('log-panel') ||
             element.querySelector('#battle')) route = 'quest';
    if (route) routes.set(element, route);
  }
  const names = {home:'HOME',units:'UNITS · SQUAD',quest:'QUEST · BATTLE',
                 summon:'SUMMON GATE · DEMO',menu:'MENU · SAVES'};
  let current = 'home';
  function syncProgress() {
    for (const [source, dest] of [['plevel','bf-nav-level'],['pzel','bf-nav-zel'],['pkarma','bf-nav-karma']]) {
      const from = document.getElementById(source), to = document.getElementById(dest);
      if (from && to) to.textContent = from.textContent || '0';
    }
  }
  function go(route) {
    if (!Object.prototype.hasOwnProperty.call(names,route)) return false;
    current = route;
    home.classList.toggle('bf-hidden',route !== 'home');
    home.setAttribute('aria-hidden',String(route !== 'home'));
    for (const [element,page] of routes) {
      const hide = page !== route;
      element.classList.toggle('bf-hidden',hide);
      element.setAttribute('aria-hidden',String(hide));
    }
    heading.hidden = route === 'home';
    heading.textContent = names[route];
    for (const button of nav.querySelectorAll('button')) {
      if (button.dataset.bfGoto === route) button.setAttribute('aria-current','page');
      else button.removeAttribute('aria-current');
    }
    syncProgress();
    window.scrollTo(0,0);
    return true;
  }
  function navigate(event) {
    const button = event.target.closest('[data-bf-goto]');
    if (button) go(button.dataset.bfGoto);
  }
  home.addEventListener('click',navigate);
  nav.addEventListener('click',navigate);
  document.body.classList.add('bf-menu-mode');
  window.BF_homeNav = {go,get current(){return current;},get routedPanels(){return routes.size;}};
  go('home');
})();


/* Build #9: original Global home location hub, read-only squad preview.
   Scene and inactive modes are reconstruction work, not original engine logic. */
(() => {
  'use strict';
  const home = document.getElementById('bf-home');
  if (!home || home.dataset.globalScene || !window.BF_homeNav) return;
  home.dataset.globalScene = '1';
  home.innerHTML = [
    '<div class="bf-scene-title"><div><strong>GRAND GAIA</strong><small>BRAVE FRONTIER GLOBAL · OFFLINE</small></div><span>RECONSTRUCTION</span></div>',
    '<section class="bf-scene-squad" aria-label="Your squad">',
      '<div class="bf-scene-heading"><strong>CURRENT SQUAD</strong><button type="button" data-bf-goto="units">EDIT SQUAD ›</button></div>',
      '<div id="bf-scene-party" class="bf-scene-party" aria-live="polite"></div>',
    '</section>',
    '<section class="bf-scene-explore" aria-label="Global locations">',
      '<div class="bf-scene-heading"><strong>ADVENTURE</strong><small>Recovered Global artwork</small></div>',
      '<div class="bf-scene-places">',
        '<button type="button" class="bf-scene-place bf-scene-active" data-bf-goto="quest" aria-label="Quest: play demo battles"><img src="content/home/home_win_quest.png" alt="" /><span class="bf-scene-status">PLAY QUEST</span></button>',
        '<div class="bf-scene-place bf-scene-locked" aria-label="Vortex Gate not implemented"><img src="content/home/home_win_gate.png" alt="" /><span class="bf-scene-status">NOT YET AVAILABLE</span></div>',
        '<div class="bf-scene-place bf-scene-locked" aria-label="Arena not implemented"><img src="content/home/home_win_arena.png" alt="" /><span class="bf-scene-status">NOT YET AVAILABLE</span></div>',
        '<div class="bf-scene-place bf-scene-locked" aria-label="Raid Battle not implemented"><img src="content/home/home_win_raid_open.png" alt="" /><span class="bf-scene-status">NOT YET AVAILABLE</span></div>',
        '<button type="button" class="bf-scene-place bf-scene-active" data-bf-goto="summon" aria-label="Summoning Hall: demo recruitment"><img src="content/home/home_win_akras_smn_hall.png" alt="" /><span class="bf-scene-status">DEMO SUMMON</span></button>',
        '<div class="bf-scene-place bf-scene-locked" aria-label="Capital Randall not implemented"><img src="content/home/home_win_randall.png" alt="" /><span class="bf-scene-status">NOT YET AVAILABLE</span></div>',
      '</div>',
    '</section>',
    '<section class="bf-scene-tools" aria-label="Home shortcuts">',
      '<div class="bf-scene-heading"><strong>HOME SHORTCUTS</strong><small>Available offline</small></div>',
      '<div class="bf-scene-toolrow">',
        '<button type="button" data-bf-goto="quest"><img src="content/home/home_new_btn_mission1.png" alt="" /><span>QUESTS</span></button>',
        '<button type="button" data-bf-goto="units"><img src="content/home/home_new_btn_shortcut1.png" alt="" /><span>UNITS</span></button>',
        '<button type="button" data-bf-goto="menu"><img src="content/home/home_new_btn_menu1.png" alt="" /><span>SAVES</span></button>',
        '<button type="button" class="bf-scene-tool-box" data-bf-goto="units" data-bf-open-box="1" aria-label="Open owned Unit Box"><img src="content/home/home_new_btn_box1.png" alt="" /><span>UNIT BOX</span></button>',
        '<div class="bf-scene-tool-locked" aria-label="Exchange Hall not implemented"><img src="content/home/home_new_btn_exchange1.png" alt="" /><span>EXCHANGE · LATER</span></div>',
      '</div>',
    '</section>',
    '<p class="bf-scene-note">Original Global graphics; recreated arrangement. Current Quest and Summon modes are demos. Unavailable locations are artwork previews, not simulated online features.</p>'
  ].join('');

  const party = document.getElementById('bf-scene-party');
  function refreshParty() {
    const members = typeof P !== 'undefined' && P && Array.isArray(P.squad) ? P.squad.slice(0, 6) : [];
    const nodes = [];
    for (let index = 0; index < 6; index++) {
      const baseId = members[index];
      const unit = baseId != null && typeof effectiveUnit === 'function' ? effectiveUnit(baseId) : null;
      const card = document.createElement('div');
      card.className = 'bf-scene-member' + (unit ? '' : ' bf-scene-empty');
      if (unit) {
        const img = document.createElement('img');
        img.src = unit.portrait || '';
        img.alt = '';
        const name = document.createElement('strong');
        name.textContent = unit.name || 'Unit';
        const level = document.createElement('small');
        const exp = P.unitExp && P.unitExp[baseId] || 0;
        level.textContent = 'Lv.' + (typeof demoLevel === 'function' ? demoLevel(exp) : '1');
        card.setAttribute('aria-label', name.textContent + ', ' + level.textContent);
        card.append(img, name, level);
      } else {
        card.textContent = '—';
        card.setAttribute('aria-label', 'Empty squad slot');
      }
      nodes.push(card);
    }
    party.replaceChildren(...nodes);
  }
  refreshParty();
  const picker = document.getElementById('squadpicker');
  if (picker) new MutationObserver(refreshParty).observe(picker, {childList:true});
  const nav = document.querySelector('.bf-navbar');
  if (nav) nav.addEventListener('click', refreshParty);
  window.BFGlobalHome = {refreshParty};
})();


/* Build #11 - recovered BF1 Global artwork for the existing Units, Quest and
 * Summon panels. Pure presentation: never rewrites game content or save schema.
 * Only the squad editor, evolution demo and training demo are operational. */
(() => {
  'use strict';
  if (!window.BF_homeNav || window.BFInnerScreens) return;
  const squad = document.querySelector('section.squadsetup');
  const evo = document.querySelector('section.evo-panel');
  const training = document.querySelector('section.training-panel');
  const quest = document.querySelector('section.questpanel');
  const summon = document.querySelector('section.summonpanel');
  if (!squad || !evo || !training || !quest || !summon) return;

  const hub = document.createElement('div');
  hub.className = 'bf-units-hub';
  hub.innerHTML = [
    '<div class="bf-inner-banner"><div class="bf-inner-title">UNITS</div>',
      '<p>Manage your current squad, inspect recovered evolution forms and use the demo training system.</p></div>',
    '<div class="bf-unit-actions" role="group" aria-label="Unit functions">',
      '<button type="button" data-bf-unit-tab="box" aria-pressed="false">',
        '<img src="content/unit_top/unit_top_box_btn1.png" alt="Unit Box" />',
        '<span>UNIT BOX</span></button>',
      '<button type="button" data-bf-unit-tab="squad" aria-pressed="true">',
        '<img src="content/unit_top/unit_top_edit_btn1.png" alt="Manage Squad" />',
        '<span>ACTIVE SQUAD</span></button>',
      '<button type="button" data-bf-unit-tab="evolve" aria-pressed="false">',
        '<img src="content/unit_top/unit_top_evo_btn1.png" alt="Evolve Unit" />',
        '<span>EVOLUTION · DEMO COST</span></button>',
      '<button type="button" data-bf-unit-tab="training" aria-pressed="false">',
        '<span class="bf-training-art" aria-hidden="true">EXP</span>',
        '<span>TRAINING · DEMO</span></button>',
    '</div>',
    '<div class="bf-unit-selected" aria-live="polite">',
      '<span id="bf-unit-tab-label">ACTIVE SQUAD</span>',
      '<span id="bf-unit-tab-detail">Use the existing squad editor below.</span></div>'
  ].join('');
  squad.prepend(hub);
  // Unit Box is nested inside a routed Units panel, preserving the existing router.
  const unitBox = document.createElement('section');
  unitBox.className = 'bf-owned-box';
  unitBox.id = 'bf-owned-box';
  unitBox.setAttribute('aria-label', 'Owned Unit Box');
  unitBox.hidden = true;
  hub.after(unitBox);

  let selected = 'squad';
  const names = {
    box: ['UNIT BOX', 'Browse and inspect your actual owned units, no changes to the save.'],
    squad: ['ACTIVE SQUAD', 'Select 1–6 owned characters. Your current save is preserved.'],
    evolve: ['EVOLUTION LAB', 'Archived forms and recipes; material drops and payable costs are demo.'],
    training: ['DEMO TRAINING', 'Uses demo Training Shards and EXP, not original Fusion.']
  };
  function setTab(next) {
    if (!Object.prototype.hasOwnProperty.call(names, next)) return false;
    selected = next;
    squad.dataset.bfUnitTab = next;
    unitBox.hidden = next !== 'box';
    unitBox.setAttribute('aria-hidden', String(next !== 'box'));
    if (next === 'box') window.BFUnitBox?.refresh();
    evo.classList.toggle('bf-units-subhidden', next !== 'evolve');
    training.classList.toggle('bf-units-subhidden', next !== 'training');
    if (window.BF_homeNav.current === 'units') {
      evo.setAttribute('aria-hidden', String(next !== 'evolve'));
      training.setAttribute('aria-hidden', String(next !== 'training'));
    }
    for (const button of hub.querySelectorAll('button[data-bf-unit-tab]')) {
      button.setAttribute('aria-pressed', String(button.dataset.bfUnitTab === next));
    }
    document.getElementById('bf-unit-tab-label').textContent = names[next][0];
    document.getElementById('bf-unit-tab-detail').textContent = names[next][1];
    return true;
  }
  hub.addEventListener('click', event => {
    const button = event.target.closest('button[data-bf-unit-tab]');
    if (button && setTab(button.dataset.bfUnitTab)) {
      hub.scrollIntoView({block:'start', behavior:'instant'});
    }
  });
  setTab('squad');
  // Build #9's Home and nav continue to own top-level routing. Reapply the
  // subtab a click later because that router sets all Units panels visible.
  document.querySelector('.bf-navbar')?.addEventListener('click', () => {
    if (window.BF_homeNav.current === 'units') setTab(selected);
  });
  document.querySelector('#bf-home')?.addEventListener('click', event => {
    if (event.target.closest('[data-bf-goto="units"]')) setTab('squad');
  });

  const questTop = document.createElement('div');
  questTop.className = 'bf-quest-archive-head';
  questTop.innerHTML = [
    '<div class="bf-quest-scroll"><span>GRAND GAIA</span></div>',
    '<div class="bf-quest-head-grid">',
      '<div class="bf-quest-head-copy"><strong>QUEST SELECTION</strong>',
        '<span>Original Global mission UI · early archived quest records</span>',
        '<small>Enemy waves and damage remain simulated in this demo.</small></div>',
      '<button type="button" class="bf-quest-manage" aria-label="Manage squad before quest">',
        '<img src="content/mission_select/party_frame_quest_btn1.png" alt="Manage Squad" /></button>',
    '</div>'
  ].join('');
  quest.prepend(questTop);
  questTop.querySelector('.bf-quest-manage').addEventListener('click', () => {
    setTab('squad');
    window.BF_homeNav.go('units');
  });

  const summonTop = document.createElement('div');
  summonTop.className = 'bf-summon-archive-head';
  summonTop.innerHTML = [
    '<img src="content/home/home_win_akras_smn_hall.png" alt="Akras Summoning Hall" />',
    '<div><strong>SUMMONING HALL</strong>',
      '<span>Offline recruitment prototype</span>',
      '<small>Archived Global art. No original rates or gacha system are claimed.</small></div>'
  ].join('');
  summon.prepend(summonTop);
  window.BFInnerScreens = {setTab, get unitTab(){return selected;}};
})();


/* Build #12: read-only owned Unit Box and source-derived quest details.
 * Do not modify roster, session, combat or saved progress from these views. */
(() => {
  'use strict';
  const box = document.getElementById('bf-owned-box');
  const questPanel = document.querySelector('section.questpanel');
  if (!box || !questPanel || window.BFUnitBox) return;

  box.innerHTML = [
    '<div class="bf-box-head"><strong>UNIT BOX</strong><span id="bf-box-count"></span></div>',
    '<p class="bf-box-hint">Your owned archived characters. Demo collection only; no selling, locking, duplicates or original capacity mechanics.</p>',
    '<div class="bf-box-filters">',
      '<label>Find unit<input id="bf-box-search" type="search" autocomplete="off" placeholder="Name or ID" /></label>',
      '<label>Show<select id="bf-box-filter"><option value="all">All owned</option><option value="squad">In squad</option><option value="reserve">Reserve</option></select></label>',
      '<label>Element<select id="bf-box-element"><option value="all">All elements</option></select></label>',
      '<label>Rarity<select id="bf-box-rarity"><option value="all">All rarities</option></select></label>',
      '<label>Sort<select id="bf-box-sort"><option value="name">Name</option><option value="rarity">Rarity</option><option value="level">Level</option><option value="element">Element</option><option value="squad">Squad first</option></select></label>',
    '</div>',
    '<div id="bf-box-results" class="bf-box-results" aria-live="polite"></div>',
    '<section id="bf-box-detail" class="bf-box-detail" aria-label="Unit details">',
      '<p>Select a unit above to inspect its archived base statistics.</p>',
    '</section>'
  ].join('');
  const results = box.querySelector('#bf-box-results');
  const count = box.querySelector('#bf-box-count');
  const detail = box.querySelector('#bf-box-detail');
  const search = box.querySelector('#bf-box-search');
  const filter = box.querySelector('#bf-box-filter');
  const sort = box.querySelector('#bf-box-sort');
  const elementFilter = box.querySelector('#bf-box-element');
  const rarityFilter = box.querySelector('#bf-box-rarity');
  let activeId = null;
  function ownedUnits() {
    if (typeof P === 'undefined' || !P || !Array.isArray(P.roster)) return {owned:[],filtered:[]};
    const owned = P.roster.map(id => ({id, unit: typeof effectiveUnit === 'function' ? effectiveUnit(id) : null})).filter(row => row.unit);
    const term = search.value.trim().toLocaleLowerCase();
    const filtered = owned.filter(({id,unit}) =>
      (!term || unit.name.toLocaleLowerCase().includes(term) || String(id).includes(term) || String(unit.id).includes(term) || unit.element.toLocaleLowerCase().includes(term)) &&
      (filter.value === 'all' || (filter.value === 'squad') === P.squad.includes(id)) &&
      (elementFilter.value === 'all' || unit.element === elementFilter.value) &&
      (rarityFilter.value === 'all' || String(unit.rarity) === rarityFilter.value));
    filtered.sort((a,b) => {
      if (sort.value === 'level') return demoLevel(P.unitExp[b.id] || 0) - demoLevel(P.unitExp[a.id] || 0) || a.id-b.id;
      if (sort.value === 'rarity') return (b.unit.rarity||0) - (a.unit.rarity||0) || a.id-b.id;
      if (sort.value === 'element') return a.unit.element.localeCompare(b.unit.element) || a.unit.name.localeCompare(b.unit.name) || a.id-b.id;
      if (sort.value === 'squad') return Number(P.squad.includes(b.id))-Number(P.squad.includes(a.id)) || a.unit.name.localeCompare(b.unit.name) || a.id-b.id;
      return a.unit.name.localeCompare(b.unit.name) || a.id-b.id;
    });
    return {owned, filtered};
  }
  function showDetail(id) {
    detail.replaceChildren();
    const unit = effectiveUnit(id);
    if (!unit || !P.roster.includes(id)) {
      const note=document.createElement('p');
      note.textContent='Select an owned unit to view its archived base statistics.';
      detail.append(note); activeId=null; return;
    }
    activeId=id;
    const img=document.createElement('img');img.src=unit.portrait;img.alt='';
    const content=document.createElement('div');
    const heading=document.createElement('h3');heading.textContent=unit.name+' · ★'+unit.rarity;
    const sub=document.createElement('p');
    sub.textContent=unit.element+' · Lv.'+demoLevel(P.unitExp[id]||0)+' · '+(P.squad.includes(id)?'In squad':'Reserve');
    const stats=document.createElement('p');
    const values=unit.stats||{};
    stats.textContent='Archived base stats · HP '+(values.hp??'?')+' · ATK '+(values.atk??'?')+' · DEF '+(values.def??'?')+' · REC '+(values.rec??'?');
    const form=document.createElement('small');
    form.textContent='Base roster ID '+id+' · Current form '+unit.id+' · Displayed stats are archive base values, not leveled combat stats.';
    const action=document.createElement('button');
    action.type='button';action.className='bf-box-manage';
    action.textContent='EDIT SQUAD ›';
    action.addEventListener('click',()=>window.BFInnerScreens.setTab('squad'));
    content.append(heading,sub,stats,form,action);
    // Read-only lookup of the original Global profile; never writes player data.
    const originalProfile=document.createElement('button');
    originalProfile.type='button';
    originalProfile.className='bf-box-original-profile';
    originalProfile.textContent='VIEW ORIGINAL GLOBAL PROFILE ›';
    originalProfile.addEventListener('click',()=>{
      if(!window.BFGlobalUnitArchive)return;
      const encyclopedia=document.getElementById('bf-unit-encyclopedia');
      if(encyclopedia)encyclopedia.open=true;
      if(window.BFGlobalUnitArchive.showDetail(unit.id)){
        document.getElementById('bf-archive-detail')?.scrollIntoView({block:'start',behavior:'smooth'});
      }
    });
    content.append(originalProfile);
    detail.append(img,content);
    // The recovered evolution relationship is shown as a preview only.
    // Its source stats are not computed by the demo battle formula and this
    // panel never consumes Zel, catalysts, levels or changes saved forms.
    const recipe=EVO_RECIPES.find(row=>row.baseId===id);
    const evolved=recipe&&UNIT_BY_ID.get(recipe.evolvedId);
    if(evolved){
      const preview=document.createElement('section');
      preview.className='bf-evo-preview';
      preview.setAttribute('aria-label','Recovered evolution preview');
      const figure=document.createElement('img');
      figure.src=evolved.portrait;figure.alt='';
      const body=document.createElement('div');
      const title=document.createElement('strong');
      const completed=!!P.evolutions[id];
      title.textContent=completed?'CURRENT EVOLVED FORM':'NEXT ARCHIVED FORM';
      const desc=document.createElement('p');
      desc.textContent=evolved.name+' · ★'+evolved.rarity+' · Unit ID '+evolved.id;
      const base=document.createElement('small');
      base.textContent='Archive base stats: HP '+evolved.stats.hp+' · ATK '+evolved.stats.atk+
        ' · DEF '+evolved.stats.def+' · REC '+evolved.stats.rec;
      const needs=document.createElement('small');
      needs.textContent=completed?'Evolved on this save': 'Archive catalyst IDs: '+
        Object.entries(recipe.materials).map(([key,n])=>key+' ×'+n).join(', ')+
        ' · Archived Zel '+recipe.archivedZel+' (demo payable cost differs)';
      const open=document.createElement('button');
      open.type='button';open.className='bf-evo-open';
      open.textContent='OPEN EVOLUTION LAB ›';
      open.addEventListener('click',()=>window.BFInnerScreens.setTab('evolve'));
      body.append(title,desc,base,needs,open);
      preview.append(figure,body);
      detail.append(preview);
    }
    for (const card of results.querySelectorAll('button[data-bf-unit-id]')) card.setAttribute('aria-pressed', String(Number(card.dataset.bfUnitId) === id));
  }
  function refresh() {
    const {owned, filtered}=ownedUnits();
    const uniqElements=[...new Set(owned.map(({unit})=>unit.element))].sort();
    const uniqRarities=[...new Set(owned.map(({unit})=>unit.rarity))].sort((a,b)=>a-b);
    const syncOptions=(control,values,label)=>{
      const old=control.value;
      control.replaceChildren(new Option(label,'all'));
      for(const value of values) control.add(new Option(control===rarityFilter?'★'+value:String(value),String(value)));
      control.value=values.some(value=>String(value)===old)?old:'all';
    };
    syncOptions(elementFilter,uniqElements,'All elements');
    syncOptions(rarityFilter,uniqRarities,'All rarities');
    count.textContent=filtered.length+' shown / '+owned.length+' owned · '+P.squad.length+' active';
    results.replaceChildren();
    if (!filtered.length) {
      const empty=document.createElement('p');empty.className='bf-box-empty';
      empty.textContent='No owned units match this filter.';results.append(empty);
    }
    for(const {id,unit} of filtered){
      const card=document.createElement('button');card.type='button';card.className='bf-box-card';
      card.dataset.bfUnitId=String(id);
      card.setAttribute('aria-label',unit.name+', level '+demoLevel(P.unitExp[id]||0));
      const img=document.createElement('img');img.src=unit.portrait;img.alt='';
      const name=document.createElement('strong');name.textContent=unit.name;
      const info=document.createElement('span');info.textContent='★'+unit.rarity+' · Lv.'+demoLevel(P.unitExp[id]||0);
      const state=document.createElement('small');state.textContent=P.squad.includes(id)?'ACTIVE':'RESERVE';
      card.append(img,name,info,state);
      card.setAttribute('aria-pressed',String(id===activeId));
      results.append(card);
    }
    if (activeId != null && filtered.some(row => row.id === activeId)) showDetail(activeId);
    else if(filtered.length) showDetail(filtered[0].id);
    else showDetail(null);
  }
  results.addEventListener('click',event => {
    const card=event.target.closest('button[data-bf-unit-id]');
    if(card) showDetail(Number(card.dataset.bfUnitId));
  });
  search.addEventListener('input',refresh);
  filter.addEventListener('change',refresh);
  sort.addEventListener('change',refresh);
  elementFilter.addEventListener('change',refresh);
  rarityFilter.addEventListener('change',refresh);
  const picker=document.getElementById('squadpicker');
  if(picker) new MutationObserver(() => {
    if(window.BF_homeNav.current==='units' && window.BFInnerScreens?.unitTab==='box') refresh();
  }).observe(picker,{childList:true});

  const questDetail=document.createElement('section');
  questDetail.id='bf-quest-details';questDetail.className='bf-quest-details';
  questDetail.setAttribute('aria-label','Selected quest details');
  questPanel.querySelector('.bf-quest-archive-head')?.after(questDetail);
  questDetail.innerHTML=[
    '<header><strong>SELECTED QUEST</strong><span id="bf-mission-availability"></span></header>',
    '<p class="bf-mission-name" id="bf-mission-name"></p>',
    '<p class="bf-mission-source" id="bf-mission-key"></p>',
    '<div class="bf-mission-stats" id="bf-mission-stats"></div>',
    '<p class="bf-mission-source" id="bf-mission-footnote">Archived mission metadata; encounter scripts and reward mechanics remain demo.</p>',
    '<button type="button" id="bf-quest-battle-jump">VIEW BATTLE CONTROLS ↓</button>'
  ].join('');
  function updateQuestDetails(){
    if(typeof QUEST==='undefined' || !QUEST) return;
    const q=QUEST;
    const locked=typeof questUnlocked==='function' && !questUnlocked(q);
    questDetail.querySelector('#bf-mission-name').textContent='Mission '+q.missionId+' · Dungeon '+q.dungeonId;
    questDetail.querySelector('#bf-mission-availability').textContent=locked?'LOCKED':'AVAILABLE';
    questDetail.querySelector('#bf-mission-key').textContent='Archive text keys: '+q.missionNameKey+' / '+q.dungeonNameKey;
    const tiles=[
      ['BATTLES',q.battles],['ENERGY',q.energy],['EXP',q.exp],
      ['ZEL',q.zel],['KARMA',q.karma],['CLEARS',P.questClears?.[q.missionId]||0]
    ];
    const target=questDetail.querySelector('#bf-mission-stats');target.replaceChildren();
    for(const [label,value] of tiles){
      const cell=document.createElement('span');
      const labelNode=document.createElement('small');labelNode.textContent=label;
      const valueNode=document.createElement('strong');valueNode.textContent=String(value);
      cell.append(labelNode,valueNode);target.append(cell);
    }
  }
  const list=document.getElementById('questlist');
  if(list) new MutationObserver(updateQuestDetails).observe(list,{childList:true});
  const battleLink=questDetail.querySelector('#bf-quest-battle-jump');
  battleLink.setAttribute('aria-label','View existing battle controls for selected mission');
  battleLink.innerHTML='<img src="content/mission_select/start_battle_btn1.png" alt="" /><span>VIEW DEMO BATTLE CONTROLS ↓</span>';
  battleLink.addEventListener('click',()=>{
    const canvas=document.getElementById('battle');
    if(canvas) canvas.scrollIntoView({block:'start',behavior:'smooth'});
  });
  document.querySelector('.bf-navbar')?.addEventListener('click',() => {
    if(window.BF_homeNav.current==='quest') updateQuestDetails();
  });
  updateQuestDetails();
  window.BFUnitBox={refresh,showDetail,updateQuestDetails};
})();


/* Source-backed quest grouping and Unit Box. */
(() => {
  'use strict';
  if (window.BFQuestAreas || !window.BF_homeNav || typeof QUESTS==='undefined') return;
  const list=document.getElementById('questlist');
  const details=document.getElementById('bf-quest-details');
  if(!list || !details) return;
  const browse=document.createElement('section');
  browse.className='bf-quest-areas';
  browse.setAttribute('aria-label','Browse archived dungeons');
  browse.innerHTML=[
    '<div class="bf-quest-area-title"><strong>GRAND GAIA QUEST PATH</strong><small>Source dungeon IDs · offline demo</small></div>',
    '<div class="bf-quest-area-tabs" role="group" aria-label="Filter by dungeon"></div>',
    '<p class="bf-quest-area-hint">Archive text for these dungeons has not been verified in English. IDs and quest requirements come from the Global master tables.</p>'
  ].join('');
  details.before(browse);
  // The master-table chain determines the path, not invented English titles.
  // Locked missions are visible but cannot be selected from the navigator.
  const pathbar=document.createElement('div');
  pathbar.className='bf-mission-path';
  pathbar.setAttribute('aria-label','Archived mission progression');
  pathbar.innerHTML=[
    '<div class="bf-mission-path-head"><strong>MISSION PATH</strong><span>Source order · unlocked progression</span></div>',
    '<div class="bf-mission-step-row" role="group" aria-label="Select available quest mission"></div>',
    '<div class="bf-mission-step-actions">',
      '<button type="button" id="bf-quest-prev" aria-label="Previous unlocked mission"><img src="content/mission_select/arrow_left.png" alt="" /><span>PREVIOUS</span></button>',
      '<span id="bf-quest-route-status" aria-live="polite"></span>',
      '<button type="button" id="bf-quest-next" aria-label="Next unlocked mission"><span>NEXT</span><img src="content/mission_select/arrow_right.png" alt="" /></button>',
    '</div>',
  ].join('');
  browse.append(pathbar);
  const stepRow=pathbar.querySelector('.bf-mission-step-row');
  const previous=pathbar.querySelector('#bf-quest-prev');
  const next=pathbar.querySelector('#bf-quest-next');
  const routeStatus=pathbar.querySelector('#bf-quest-route-status');
  const steps=new Map();
  for(const q of QUESTS){
    const button=document.createElement('button');
    button.type='button';button.dataset.bfMission=String(q.missionId);
    button.setAttribute('aria-label','Mission '+q.missionId);
    button.innerHTML='<strong>MISSION '+q.missionId+'</strong><small></small>';
    button.addEventListener('click',()=>choose(q));
    stepRow.append(button);steps.set(q.missionId,button);
  }
  function choose(q){
    if(!q||!questUnlocked(q)||S?.busy)return false;
    const i=QUESTS.findIndex(row=>row.missionId===q.missionId);
    if(i<0)return false;
    // Route through the *original existing quest click handler* so reset,
    // saveProgress, selected mission background and safety checks stay intact.
    active='all';
    update();
    const target=list.querySelectorAll('button.questcard')[i];
    if(!target || target.disabled)return false;
    target.click();
    update();
    return QUEST.missionId===q.missionId;
  }
  previous.addEventListener('click',()=>{
    const idx=QUESTS.findIndex(q=>q.missionId===QUEST.missionId);
    const q=QUESTS.slice(0,idx).reverse().find(questUnlocked);
    if(q)choose(q);
  });
  next.addEventListener('click',()=>{
    const idx=QUESTS.findIndex(q=>q.missionId===QUEST.missionId);
    const q=QUESTS.slice(idx+1).find(questUnlocked);
    if(q)choose(q);
  });
  const tabs=browse.querySelector('.bf-quest-area-tabs');
  const dungeonIDs=[...new Set(QUESTS.map(q=>q.dungeonId))].sort((a,b)=>a-b);
  let active='all';
  const navButton=(value,label)=>{
    const button=document.createElement('button');button.type='button';
    button.dataset.bfDungeon=String(value);button.textContent=label;
    button.setAttribute('aria-pressed',String(String(value)===active));
    button.addEventListener('click',()=>{
      active=String(value);
      update();
    });
    tabs.append(button);
  };
  navButton('all','ALL QUESTS');
  for(const id of dungeonIDs) navButton(id,'DUNGEON '+id);
  function update(){
    for(const button of tabs.querySelectorAll('button')) button.setAttribute('aria-pressed',String(button.dataset.bfDungeon===active));
    const cards=[...list.querySelectorAll('button.questcard')];
    for(let i=0;i<cards.length;i++){
      const q=QUESTS[i];if(q)cards[i].hidden=active!=='all' && String(q.dungeonId)!==active;
    }
    // Filter only the display; never trigger core quest selection or progression.
    const shown=QUESTS.filter(q=>active==='all'||String(q.dungeonId)===active);
    browse.querySelector('.bf-quest-area-hint').textContent=
      shown.length+' archived missions · '+shown.filter(q=>(P.questClears?.[q.missionId]||0)>0).length+
      ' cleared · '+shown.filter(q=>questUnlocked(q)).length+
      ' currently unlocked. Dungeon names have unresolved Global text keys.';
    for(const q of QUESTS){
      const button=steps.get(q.missionId);
      if(!button)continue;
      const locked=!questUnlocked(q);
      button.disabled=locked || !!S?.busy;
      button.setAttribute('aria-pressed',String(QUEST.missionId===q.missionId));
      button.classList.toggle('bf-step-clear',(P.questClears?.[q.missionId]||0)>0);
      button.querySelector('small').textContent=locked?'LOCKED':(P.questClears?.[q.missionId]||0)>0?'CLEARED':'AVAILABLE';
      button.title='Archive mission '+q.missionId+' · dungeon '+q.dungeonId+
        (locked?' · requires Mission '+q.requires:' · '+q.battles+' battles');
    }
    const index=QUESTS.findIndex(q=>q.missionId===QUEST.missionId);
    const earlier=QUESTS.slice(0,index).reverse().find(questUnlocked);
    const later=QUESTS.slice(index+1).find(questUnlocked);
    previous.disabled=!earlier||!!S?.busy;
    next.disabled=!later||!!S?.busy;
    routeStatus.textContent='MISSION '+QUEST.missionId+' / '+QUESTS.length+
      ' · '+(P.questClears?.[QUEST.missionId]?'CLEARED':'IN PROGRESS');
  
  }
  new MutationObserver(update).observe(list,{childList:true});
  update();
  // Home's original Box shortcut now uses the existing Units route and box tab.
  // Bind after the existing Home routing and squad-reset handlers.
  const home=document.getElementById('bf-home');
  home?.addEventListener('click',event=>{
    if(event.target.closest('[data-bf-open-box]')) window.BFInnerScreens?.setTab('box');
  });
  window.BFQuestAreas={update,choose,get selectedDungeon(){return active;}};
})();


/* Original Global English quest text; sourced from 2022 sgtext. */
(() => {
  'use strict';
  if (window.BFGlobalQuestText || !window.BFQuestAreas || !window.BFUnitBox) return;
  /* BF_GLOBAL_QUEST_TEXT_DATA_V048: descriptions staged from exact source manifests. */
  const legacyEnglish = window.BF_QUEST_ENGLISH_DESCRIPTIONS;
  const mirzaEnglish = window.BF_QUEST_ENGLISH_DESCRIPTIONS_V049;
  if (!legacyEnglish || Object.keys(legacyEnglish).length !== 21 ||
      !mirzaEnglish || Object.keys(mirzaEnglish).length !== 4) return;
  const nestEnglish = window.BF_QUEST_ENGLISH_DESCRIPTIONS_V050;
  if (!nestEnglish || Object.keys(nestEnglish).length !== 4) return;
  const towerEnglish = window.BF_QUEST_ENGLISH_DESCRIPTIONS_V051;
  if (!towerEnglish || Object.keys(towerEnglish).length !== 5) return;
  const morgan = window.BF_MORGAN_QUEST_DATA_V080;
  if (morgan?.schema!=='bf-global-morgan-2022-original-quests-v080' ||
      morgan.quests?.length!==36 || morgan.dungeons?.length!==7) return;
  const stlamia = window.BF_STLAMIA_QUEST_DATA_V090;
  if(stlamia?.schema!=='bf-global-st-lamia-2022-original-quests-v090' ||
     stlamia.quests?.length!==36 || stlamia.dungeons?.length!==7) return;
  const english = {...legacyEnglish,...mirzaEnglish,...nestEnglish,...towerEnglish,
      ...Object.fromEntries(morgan.quests.map(q=>[q.missionId,q.description])),
      ...Object.fromEntries(stlamia.quests.map(q=>[q.missionId,q.description]))};
  const missions = [
    [1, 'Basics of Battle'],
    [2, 'Element & Skill'],
    [10, 'Start of Adventure'],
    [11, 'Monsters of the Prairie'],
    [12, 'Guardians of the Prairie'],
    [20, 'Cave of Dancing Flames'],
    [21, 'Wielder of the Fire'],
    [22, "The Thief's Hideout"],
    [23, 'The Blazing Beast'],
    [30, "Breath Freezing Snowfields"],
    [31, "Manipulator of the Water"],
    [32, "The Pirate on Ice"],
    [33, "The Dragon Hunting Ice Knight"],
    [40, "Shadowy Forests"],
    [41, "Puppeteer of the Trees"],
    [42, "Bandit of the Forest"],
    [43, "Hunter from the Forest"],
    [50, "Thunder Blasting Wetlands"],
    [51, "Commander of the Thunder"],
    [52, "Pirate of the Wetlands"],
    [53, "The Thundering Strategist"],
    [60, "Sacred Ruins"],
    [61, "Wielder of the Light"],
    [62, "The White Horse of Light"],
    [63, "Moonlit Battle"],
    [70, "The Heinous Chamber"],
    [71, "Manipulator of the Dark"],
    [72, "The Cursed Snake"],
    [73, "The Monster Slaying Blade"],
    [81, "The Skyhigh Tower"],
    [82, "Monsters of the Corridor"],
    [83, "The Stairs of Trial"],
    [84, "The Pillars of Force"],
    [85, "The Forged Gigantor"]
  ].concat(morgan.quests.map(q=>[q.missionId,q.name]), stlamia.quests.map(q=>[q.missionId,q.name])).map(([id,name]) => [id,name,english[id]]);
  if (missions.some(([, ,desc]) => typeof desc !== 'string' || !desc)) return;
  const dungeons = [
    [1, "Beginner's Prairie"],
    [10, "Adventurer's Prairie"],
    [20, 'Cave of Flames'],
    [30, 'Egor Snowfield'],
    [40, 'Forest of Beasts'],
    [50, 'Magutagal Wetlands'],
    [60, 'Remains of Mirza'],
    [70, "Monster's Nest"],
    [80, 'Tower of Mistral']
  ].concat(morgan.dungeons.map(d=>[d.id,d.name]), stlamia.dungeons.map(d=>[d.id,d.name]));
  const missionById = new Map(missions.map(([id, name, description]) =>
    [id, {id, key:'MST_DUNGEONS_MISSION_'+id+'_NAME', name,
      descriptionKey:'MST_DUNGEONS_MISSION_'+id+'_DESCRIPTION', description}]));
  const dungeonById = new Map(dungeons.map(([id, name]) =>
    [id, {id, key:'MST_DUNGEONS_DUNGEON_'+id+'_NAME', name}]));

  function sourceFor(quest) {
    if (!quest) return null;
    const mission = missionById.get(quest.missionId);
    const dungeon = dungeonById.get(quest.dungeonId);
    // Reject mismatched joins: a coincidental ID is not proof of a source match.
    if (!mission || !dungeon || mission.key !== quest.missionNameKey ||
        dungeon.key !== quest.dungeonNameKey) return null;
    return {mission, dungeon};
  }

  const list = document.getElementById('questlist');
  const path = document.querySelector('.bf-mission-step-row');
  const areaTabs = document.querySelector('.bf-quest-area-tabs');
  const detail = document.getElementById('bf-quest-details');
  const detailName = document.getElementById('bf-mission-name');
  const regionTitle = document.querySelector('.bf-quest-scroll span');
  if (!list || !path || !areaTabs || !detail || !detailName) return;

  const description = document.createElement('section');
  description.className = 'bf-global-mission-description';
  description.setAttribute('aria-label', 'Original Brave Frontier Global mission description');
  const caption = document.createElement('strong');
  caption.textContent = 'GLOBAL QUEST DESCRIPTION';
  const paragraph = document.createElement('p');
  const sourceLine = document.createElement('small');
  sourceLine.textContent = '2022 Global English sgtext · original source wording';
  description.append(caption, paragraph, sourceLine);
  detailName.after(description);

  function syncGlobalNames() {
    // renderQuestList() recreates these quest buttons on each ordinary save
    // refresh; apply text to the new buttons, never override their onclick.
    const questButtons = list.querySelectorAll('button.questcard');
    questButtons.forEach((button, index) => {
      const quest = QUESTS[index];
      const source = sourceFor(quest);
      if (!source) return;
      const heading = button.querySelector('strong');
      const sub = button.querySelector('small');
      const locked = !questUnlocked(quest);
      const nextTitle = (locked ? '🔒 ' : '') + source.mission.name;
      if (heading && heading.textContent !== nextTitle) heading.textContent = nextTitle;
      const detailText = 'Mission ' + quest.missionId + ' · ' +
        quest.battles + ' battles · ' +
        (locked ? 'Clear Mission '+quest.requires+' to unlock' :
          quest.exp+' EXP · '+quest.zel+' Zel');
      if (sub && sub.textContent !== detailText) sub.textContent = detailText;
      button.setAttribute('aria-label', source.mission.name + ', Mission ' +
        quest.missionId + (locked ? ', locked' : ', selectable'));
    });
    for (const button of path.querySelectorAll('button[data-bf-mission]')) {
      const id = Number(button.dataset.bfMission);
      const quest = QUESTS.find(q => q.missionId === id);
      const source = sourceFor(quest);
      if (!source) continue;
      const nameNode = button.querySelector('strong');
      if (nameNode && nameNode.textContent !== source.mission.name)
        nameNode.textContent = source.mission.name;
      button.setAttribute('aria-label',
        source.mission.name + ', Mission ' + id +
        (button.disabled ? ', locked' : ', selectable'));
      // Do not disturb status or the selected-state class set by BFQuestAreas.
    }
    for (const button of areaTabs.querySelectorAll('button[data-bf-dungeon]')) {
      const id = Number(button.dataset.bfDungeon);
      const source = dungeonById.get(id);
      if (!source) continue;
      const text = source.name;
      if (button.textContent !== text) button.textContent = text;
      button.title = 'Global dungeon ' + id + ': ' + text;
    }
  }

  function syncSelectedDescription() {
    const quest = (typeof QUEST !== 'undefined') ? QUEST : null;
    const source = sourceFor(quest);
    const title = source ? source.mission.name + ' · Mission ' + quest.missionId
                         : quest ? 'Mission ' + quest.missionId : '';
    if (detailName.textContent !== title) detailName.textContent = title;
    if (!source) {
      description.hidden = true;
      return;
    }
    description.hidden = false;
    if (paragraph.textContent !== source.mission.description)
      paragraph.textContent = source.mission.description;
    if (regionTitle && regionTitle.textContent !== source.dungeon.name)
      regionTitle.textContent = source.dungeon.name;
    const archiveKey = detail.querySelector('#bf-mission-key');
    if (archiveKey && archiveKey.textContent !==
        'Dungeon: '+source.dungeon.name+' · Archive keys: '+
        source.mission.key+' / '+source.dungeon.key)
      archiveKey.textContent = 'Dungeon: '+source.dungeon.name+' · Archive keys: '+
        source.mission.key+' / '+source.dungeon.key;
  }

  // Core quest selection renders both list & summary anew. Our observers only
  // watch direct children, so editing text nodes cannot cause a feedback loop.
  new MutationObserver(() => { syncGlobalNames(); syncSelectedDescription(); })
    .observe(list, {childList:true});
  // Core detail writer is independent of the quest list, so handle both orders.
  new MutationObserver(syncSelectedDescription).observe(detailName,{childList:true});
  syncGlobalNames();
  syncSelectedDescription();

  window.BFGlobalQuestText = {
    sourceFor,
    refresh() {syncGlobalNames();syncSelectedDescription();},
    missions: missions.map(([id,name,description]) =>
      ({id,key:'MST_DUNGEONS_MISSION_'+id+'_NAME',name,
        descriptionKey:'MST_DUNGEONS_MISSION_'+id+'_DESCRIPTION',description})),
    dungeons: dungeons.map(([id,name]) =>
      ({id,key:'MST_DUNGEONS_DUNGEON_'+id+'_NAME',name}))
  };
})();


/* Original optional Global BGM; verified in source manifest. */
(() => {
  'use strict';
  if (!window.BF_homeNav || !window.BFGlobalQuestText || window.BFGlobalAudio) return;
  const quest=document.querySelector('section.questpanel');
  const host=quest?.querySelector('.bf-quest-archive-head');
  const list=document.getElementById('questlist');
  if(!quest || !host || !list) return;
  const mapping=new Map([
    [1,'bf010_map_grass.mp3'],[2,'bf010_map_grass.mp3'],
    [10,'bf010_map_grass.mp3'],[11,'bf010_map_grass.mp3'],[12,'bf010_map_grass.mp3'],
    [20,'bf011_map_firecave.mp3'],[21,'bf011_map_firecave.mp3'],
    [22,'bf011_map_firecave.mp3'],[23,'bf011_map_firecave.mp3']
  ]);
  const tracks=new Set(['bf010_map_grass.mp3','bf011_map_firecave.mp3','bf006_btl_boss.mp3']);
  const panel=document.createElement('section');
  panel.className='bf-global-audio';
  panel.setAttribute('aria-label','Original Brave Frontier Global music controls');
  panel.innerHTML=[
    '<div class="bf-global-audio-top">',
      '<div><strong>ORIGINAL GLOBAL MUSIC</strong><small>2022 archive · on-device audio</small></div>',
      '<span class="bf-global-audio-tag">OFF BY DEFAULT</span>',
    '</div>',
    '<p id="bf-global-track-label">Music for the selected mission</p>',
    '<div class="bf-global-audio-controls">',
      '<button type="button" id="bf-global-play-track">PLAY QUEST BGM</button>',
      '<button type="button" id="bf-global-boss-preview">PREVIEW BOSS BGM</button>',
      '<button type="button" id="bf-global-stop-track" disabled>STOP</button>',
    '</div>',
    '<p class="bf-global-audio-status" id="bf-global-audio-status" role="status" aria-live="polite">Audio disabled. No automatic playback.</p>',
    '<small class="bf-global-audio-note">Boss music is a source-verified track preview, not a verified boss encounter. No data or audio is streamed.</small>'
  ].join('');
  host.after(panel);
  const play=panel.querySelector('#bf-global-play-track');
  const boss=panel.querySelector('#bf-global-boss-preview');
  const stop=panel.querySelector('#bf-global-stop-track');
  const trackText=panel.querySelector('#bf-global-track-label');
  const status=panel.querySelector('#bf-global-audio-status');
  const audio=document.createElement('audio');
  audio.preload='none';
  audio.loop=true;
  audio.volume=.42;
  audio.setAttribute('aria-hidden','true');
  panel.append(audio);
  let mode=null; // either quest/boss or null; never saved
  const base='content/sound/';
  const pathFor=file=>{
    if(!tracks.has(file))throw new Error('Unverified Global sound file');
    return base+file;
  };
  const missionTrack=()=>mapping.get(QUEST?.missionId) || null;
  const titleFor=file=>file==='bf011_map_firecave.mp3'?
    'Cave of Flames — original bf011_map_firecave.mp3' :
    file==='bf010_map_grass.mp3'?
    'Grand Gaia prairie — original bf010_map_grass.mp3':
    'Archived boss theme — bf006_btl_boss.mp3';
  const labelCurrent=()=>{
    const file=missionTrack();
    trackText.textContent=file?
      'Mission '+QUEST.missionId+': '+titleFor(file):
      'No verified original music for this mission';
    play.disabled=!file;
  };
  const setStatus=msg=>{status.textContent=msg;};
  function halt(msg){
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
    mode=null;
    stop.disabled=true;
    if(msg)setStatus(msg);
  }
  function start(file,nextMode){
    if(!file){halt('No verified original track for selected mission.');return;}
    if(window.BF_homeNav.current!=='quest'){
      halt('Open Quest to preview original music.');return;
    }
    const track=pathFor(file);
    if(audio.getAttribute('src')!==track){
      audio.src=track;
      audio.load();
    }
    mode=nextMode;
    stop.disabled=false;
    setStatus('Starting '+titleFor(file)+'…');
    try{
      const promise=audio.play();
      if(promise?.catch)promise.catch(()=>{
        halt('Playback blocked or unsupported; tap PLAY again if your device allows audio.');
      });
    }catch(error){halt('Audio unavailable on this device.');}
  }
  play.addEventListener('click',()=>start(missionTrack(),'quest'));
  boss.addEventListener('click',()=>start('bf006_btl_boss.mp3','boss'));
  stop.addEventListener('click',()=>halt('Music stopped.'));
  audio.addEventListener('playing',()=>{
    if(mode)setStatus('Playing '+titleFor(mode==='boss'?'bf006_btl_boss.mp3':missionTrack()));
  });
  audio.addEventListener('error',()=>halt('Bundled audio could not be decoded.'));
  function sync(){
    labelCurrent();
    if(window.BF_homeNav.current!=='quest' && mode){
      halt('Paused when leaving Quest.');return;
    }
    if(mode==='quest'){
      const file=missionTrack();
      if(!file){halt('No verified soundtrack for this mission.');return;}
      if(audio.getAttribute('src')!==pathFor(file)){
        // A quest-selection gesture is allowed to request playback.
        start(file,'quest');
      }
    }
  }
  new MutationObserver(sync).observe(list,{childList:true});
  document.querySelector('.bf-navbar')?.addEventListener('click',sync);
  document.querySelector('#bf-home')?.addEventListener('click',sync);
  window.addEventListener('pagehide',()=>halt());
  sync();
  window.BFGlobalAudio={
    get playingMode(){return mode;},
    get track(){return audio.getAttribute('src')||'';},
    get playing(){return !audio.paused;},
    get selectedTrack(){return missionTrack();},
    playQuest(){start(missionTrack(),'quest');},
    previewBoss(){start('bf006_btl_boss.mp3','boss');},
    stop(){halt('Music stopped.');},
    sync,
    mapping: Object.freeze(Object.fromEntries(mapping))
  };
})();


/* Original Mistral map; no unlock bypass. */
(() => {
  'use strict';
  if (window.BFMistralMap || !window.BFQuestAreas || !window.BFGlobalQuestText) return;
  const quest = document.querySelector('section.questpanel');
  const homeHeader = quest?.querySelector('.bf-quest-archive-head');
  const list = document.getElementById('questlist');
  if (!quest || !homeHeader || !list || !Array.isArray(QUESTS)) return;
  const data = Object.freeze([
    Object.freeze({id:1, name:"Beginner's Prairie",nameKey:'MST_DUNGEONS_DUNGEON_1_NAME',x:400,y:780,required:0}),
    Object.freeze({id:10,name:"Adventurer's Prairie",nameKey:'MST_DUNGEONS_DUNGEON_10_NAME',x:378,y:829,required:0}),
    Object.freeze({id:20,name:'Cave of Flames',nameKey:'MST_DUNGEONS_DUNGEON_20_NAME',x:36,y:698,required:12}),
    Object.freeze({id:30,name:'Egor Snowfield',nameKey:'MST_DUNGEONS_DUNGEON_30_NAME',x:344,y:656,required:23}),
    Object.freeze({id:40,name:'Forest of Beasts',nameKey:'MST_DUNGEONS_DUNGEON_40_NAME',x:64,y:502,required:33}),
    Object.freeze({id:50,name:'Magutagal Wetlands',nameKey:'MST_DUNGEONS_DUNGEON_50_NAME',x:252,y:420,required:43}),
    Object.freeze({id:60,name:'Remains of Mirza',nameKey:'MST_DUNGEONS_DUNGEON_60_NAME',x:425,y:343,required:53}),
    Object.freeze({id:70,name:"Monster's Nest",nameKey:'MST_DUNGEONS_DUNGEON_70_NAME',x:49,y:264,required:63}),
    Object.freeze({id:80,name:'Tower of Mistral',nameKey:'MST_DUNGEONS_DUNGEON_80_NAME',x:330,y:193,required:73})
  ]);
  const panel=document.createElement('section');
  panel.className='bf-mistral-map';
  panel.setAttribute('aria-label','Original Brave Frontier Global Mistral area map');
  panel.innerHTML=[
    '<header class="bf-mistral-map-heading">',
      '<img src="content/area/area_plate_0001.png" alt="Original Brave Frontier Global Mistral plate" />',
      '<div><strong>MISTRAL · GRAND GAIA</strong><small>Original area artwork and archived dungeon locations</small></div>',
    '</header>',
    '<div class="bf-mistral-map-frame">',
      '<img class="bf-mistral-map-art" src="content/area/area_0001.jpg" alt="Original 2022 Global Mistral world map with prairie, forests, cave and mountain." />',
      '<div class="bf-mistral-map-pins" role="group" aria-label="Choose a Mistral dungeon"></div>',
    '</div>',
    '<p class="bf-mistral-map-label" id="bf-mistral-map-label" aria-live="polite">Select a dungeon location to browse its archived missions.</p>',
    '<div class="bf-mistral-map-list" role="group" aria-label="Mistral dungeon list"></div>',
    '<small class="bf-mistral-map-note">Original map and recorded location coordinates. Enemy waves and battle formulas are still the offline demo.</small>'
  ].join('');
  homeHeader.after(panel);
  const pins=panel.querySelector('.bf-mistral-map-pins');
  const itemList=panel.querySelector('.bf-mistral-map-list');
  const notice=panel.querySelector('#bf-mistral-map-label');
  const controls=new Map();
  function missionsFor(id){return QUESTS.filter(q=>q.dungeonId===id);}
  function access(id){return missionsFor(id).some(q=>questUnlocked(q));}
  function reveal(id){
    const info=data.find(x=>x.id===id);
    if(!info)return false;
    const options=missionsFor(id).filter(q=>questUnlocked(q));
    if(!options.length){
      notice.textContent=info.name+' is locked. Complete the preceding missions to unlock it.';
      return false;
    }
    // Prefer first unfinished mission, falling back to the last unlocked quest.
    const target=options.find(q=>(P.questClears?.[q.missionId]||0)===0) || options[options.length-1];
    if(!target)return false;
    if(QUEST.missionId!==target.missionId && !window.BFQuestAreas.choose(target)){
      notice.textContent='Quest selection is unavailable during combat.';
      return false;
    }
    const tab=quest.querySelector('.bf-quest-area-tabs [data-bf-dungeon="'+id+'"]');
    tab?.click();
    const selected=window.BFGlobalQuestText.sourceFor(QUEST);
    notice.textContent=info.name+' · '+(selected?.mission.name||'Mission '+QUEST.missionId)+
      ' · '+options.length+' available mission'+(options.length===1?'':'s');
    refresh();
    return true;
  }
  for(const entry of data){
    const pin=document.createElement('button');
    pin.type='button';pin.className='bf-mistral-pin';pin.dataset.bfMapDungeon=String(entry.id);
    pin.textContent=String(entry.id);
    pin.title=entry.name;
    pin.style.left=(entry.x/640*100)+'%';
    pin.style.top=(entry.y/960*100)+'%';
    pin.setAttribute('aria-label','View '+entry.name+' on the Mistral area map');
    pin.addEventListener('click',()=>reveal(entry.id));
    pins.append(pin);

    const row=document.createElement('button');
    row.type='button';row.className='bf-mistral-list-item';
    row.dataset.bfMapList=String(entry.id);
    row.innerHTML='<span class="bf-mistral-list-num"></span><span class="bf-mistral-list-copy"><strong></strong><small></small></span>';
    row.querySelector('.bf-mistral-list-num').textContent=String(entry.id);
    row.querySelector('strong').textContent=entry.name;
    row.setAttribute('aria-label','Browse '+entry.name);
    row.addEventListener('click',()=>reveal(entry.id));
    itemList.append(row);
    controls.set(entry.id,{pin,row});
  }
  function refresh(){
    for(const info of data){
      const unlocked=access(info.id);
      const missions=missionsFor(info.id);
      const cleared=missions.filter(q=>(P.questClears?.[q.missionId]||0)>0).length;
      const selected=QUEST?.dungeonId===info.id;
      const {pin,row}=controls.get(info.id);
      pin.classList.toggle('bf-mistral-locked',!unlocked);
      row.classList.toggle('bf-mistral-locked',!unlocked);
      pin.setAttribute('aria-pressed',String(selected));
      row.setAttribute('aria-pressed',String(selected));
      const state=unlocked?'AVAILABLE':'LOCKED';
      const desc=state+' · '+cleared+'/'+missions.length+' cleared';
      row.querySelector('small').textContent=desc;
      pin.setAttribute('aria-label',info.name+', '+desc);
      row.setAttribute('aria-label',info.name+', '+desc);
    }
  }
  new MutationObserver(refresh).observe(list,{childList:true});
  document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
  refresh();
  window.BFMistralMap={
    entries:data,refresh,reveal,
    get selectedDungeon(){return QUEST?.dungeonId;},
    isUnlocked(id){return access(id);}
  };
})();


/* Original Global battle action images; demo controls preserved. */
(() => {
  'use strict';
  if (window.BFOriginalBattleUI || !window.BF_homeNav) return;
  const row=document.querySelector('.squad-panel .actionrow');
  const tools=document.querySelector('.squad-panel .tools');
  const nativeAuto=document.getElementById('auto');
  const attack=document.getElementById('attack');
  const burst=document.getElementById('burst');
  const guard=document.getElementById('guard');
  const execute=document.getElementById('execute');
  if (!row || !tools || !nativeAuto || !attack || !burst || !guard || !execute) return;
  for(const [button,name] of [
    [attack,'Attack'],[burst,'Brave Burst'],[guard,'Guard']]){
    button.classList.add('bf-original-action');
    button.setAttribute('aria-label',name);
    button.title=name+' (original Global action artwork)';
  }
  const originalAuto=document.createElement('button');
  originalAuto.type='button';
  originalAuto.className='bf-original-auto-action';
  originalAuto.id='bf-original-auto-action';
  originalAuto.setAttribute('aria-controls','auto');
  originalAuto.setAttribute('aria-pressed','false');
  originalAuto.textContent='Auto Battle';
  tools.prepend(originalAuto);
  const toggle=()=>{
    originalAuto.setAttribute('aria-pressed',String(nativeAuto.checked));
    originalAuto.setAttribute('aria-label','Auto Battle '+(nativeAuto.checked?'ON':'OFF'));
    originalAuto.title='Original Global Auto Battle artwork · '+(nativeAuto.checked?'ON':'OFF');
  };
  originalAuto.addEventListener('click',()=>{
    if(nativeAuto.disabled)return;
    nativeAuto.click(); // Retains original native checkbox onchange / demo AI.
    toggle();
  });
  nativeAuto.addEventListener('change',toggle);
  // Core uses direct checked assignment when battle resets or ends, so watch
  // its normal visible status label without introducing a timer or mutation.
  const phase=document.getElementById('phase');
  if(phase)new MutationObserver(toggle).observe(phase,{childList:true,characterData:true,subtree:true});
  document.getElementById('reset')?.addEventListener('click',toggle);
  document.querySelector('.bf-navbar')?.addEventListener('click',toggle);
  toggle();
  window.BFOriginalBattleUI={
    get autoEnabled(){return nativeAuto.checked;},
    get autoPressed(){return originalAuto.getAttribute('aria-pressed')==='true';},
    refresh:toggle
  };
})();


/* Read-only Global collaboration archive reference. */
(() => {
  'use strict';
  if (window.BFGlobalCollaborationArchive || !window.BFUnitBox) return;
  const box = document.getElementById('bf-owned-box');
  if (!box) return;
  const units = Object.freeze([{"id":810547,"name":"Natsu Dragneel","series":"Fairy Tail","animation":"CGG/CGS"},{"id":840548,"name":"Erza Scarlet","series":"Fairy Tail","animation":"CGG/CGS"},{"id":860637,"name":"Acnologia","series":"Fairy Tail","animation":"CGG/CGS"},{"id":810588,"name":"Katsuki Bakugo","series":"My Hero Academia","animation":"CGG/CGS"},{"id":850588,"name":"All Might","series":"My Hero Academia","animation":"CGG/CGS"},{"id":810178,"name":"Mai Shiranui","series":"The King of Fighters","animation":"CGG/CGS"},{"id":860868,"name":"Legato Bluesummers","series":"Trigun","animation":"CGG/CGS"},{"id":850198,"name":"Mankai Sakura Miku","series":"Hatsune Miku","animation":"SAM"}].map(unit => Object.freeze(unit)));
  const section = document.createElement('section');
  section.className = 'bf-global-collab-archive';
  section.setAttribute('aria-label','Original Global collaboration archive preview');
  section.innerHTML = [
    '<details id="bf-collab-browser">',
      '<summary>GLOBAL COLLABORATION ARCHIVE <small>8 documented examples · preview</small></summary>',
      '<p>Original Global database unit IDs cross-referenced with archived asset paths. These characters are <strong>not yet recruitable</strong>, and their artwork and combat data are not included in this preview. This is not the complete collaboration roster.</p>',
      '<label for="bf-collab-search">Search character, series or original ID</label>',
      '<input id="bf-collab-search" type="search" autocomplete="off" placeholder="Search archived units" />',
      '<label for="bf-collab-series">Series</label>',
      '<select id="bf-collab-series"><option value="all">All series</option></select>',
      '<div id="bf-collab-count" role="status" aria-live="polite"></div>',
      '<div id="bf-collab-results" class="bf-collab-results"></div>',
      '<p class="bf-collab-provenance">Source: decoded 2022 Global master tables and archived asset-path manifest. Paths are references, not bundled animations. Gameplay remains the demo.</p>',
    '</details>'
  ].join('');
  box.append(section);
  const search=section.querySelector('#bf-collab-search');
  const filter=section.querySelector('#bf-collab-series');
  const results=section.querySelector('#bf-collab-results');
  const count=section.querySelector('#bf-collab-count');
  for (const name of [...new Set(units.map(u=>u.series))].sort()) {
    const option=document.createElement('option');
    option.value=name;
    option.textContent=name;
    filter.append(option);
  }
  function render() {
    const query=search.value.trim().toLocaleLowerCase();
    const visible=units.filter(unit =>
      (filter.value==='all' || unit.series===filter.value) &&
      [unit.id,unit.name,unit.series].some(value=>String(value).toLocaleLowerCase().includes(query))
    );
    results.replaceChildren();
    for(const unit of visible) {
      const card=document.createElement('article');
      card.className='bf-collab-card';
      const title=document.createElement('strong');
      title.textContent=unit.name;
      const origin=document.createElement('span');
      origin.textContent=unit.series+' · Original unit ID '+unit.id;
      const type=document.createElement('small');
      type.textContent='Animation reference: '+unit.animation+' · Archive preview only';
      card.append(title,origin,type);
      results.append(card);
    }
    if(!visible.length) {
      const empty=document.createElement('p');
      empty.className='bf-collab-empty';
      empty.textContent='No matching archived characters.';
      results.append(empty);
    }
    count.textContent=visible.length+' of '+units.length+' documented references';
  }
  search.addEventListener('input',render);
  filter.addEventListener('change',render);
  render();
  window.BFGlobalCollaborationArchive=Object.freeze({
    entries:units,
    get count(){return units.length;},
    search(query,series='all'){
      return units.filter(unit=>(series==='all'||unit.series===series) &&
        [unit.id,unit.name,unit.series].some(value=>String(value).toLowerCase().includes(String(query).toLowerCase())));
    },
    refresh:render
  });
})();
