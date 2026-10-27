/* v0.26 source-backed read-only Global unit index. No save/roster writes. */
(() => {
  'use strict';
  if(window.BFGlobalUnitArchive || !window.BFUnitBox) return;
  const payload=document.getElementById('bf-global-unit-catalog-data');
  const box=document.getElementById('bf-owned-box');
  if(!payload || !box) return;
  let archive;
  try{archive=JSON.parse(payload.textContent);}catch(_){return;}
  if(archive.schema!=='bf-global-unit-archive-2022-v1' || archive.units.length!==2291)return;
  const units=archive.units;
  const byId=new Map(units.map(u=>[u.id,u]));
  // v123: compact source-verified 2022 Imp *bonus cap metadata* only.
  // 2291 indexed bytes + 147 unique big-endian uint16x4 tuples. No enhancement
  // engine, saved unit stat write or numeric experience migration is involved.
  const originalImpCaps=(()=>{
    try{
      const ids=[...byId.keys()].sort((a,b)=>a-b);
      if(ids.length!==2291||ids[0]!==1||ids[1]!==10011||ids.at(-1)!==87602603)return null;
      const which=atob('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');
      const data=atob('AAAAAAAAAAAAZAEYACgAKACWACgAKABkAJYAKABQADwAlgA8ADwAPACWADwAPAEsAJYAUAAoADwAlgEsADwAPADIACgAKAAoAMgAUABQAFAAyABQAFABkADIAKAAUACgAMgAoACgAFAAyAGQAFAAUAD6AFAAUACMAPoAUAB4AGQA+gBkAGQAZAD6AGQAZAH0APoAeABQAGQA+gB4AHgAeAD6AfQAZABkASwAUABQAFABLABQAKAAeAEsAGQAZACgASwAeAB4AHgBLACgAFAAeAEsAMgAeADIASwAyADIAHgBXgDIAKAAjAFeANwAjACMAV4BBACMAQQBXgEEAQQAjAGQAGQAZABkAZAAeADIAKABkACMAIwAyAGQAKAAUABQAZAAoACgAKABkADIAHgAoAGQAMgAjAB4AZAC0ACgAKABwgCgALQAeAHCALQAjACgAcIAtAC0ASwBwgDIAMgBQAHCAPAAoADIAcIA8ADIALQBwgEEALQAtAH0AHgAeAB4AfQAjAEEAMgB9ACgAKABGAH0ALQAtADwAfQAyAB4AHgB9ADIAMgAyAH0AMgAyAEEAfQAyADcAKAB9ADIAQQAjAH0ANwAtADIAfQA8AC0AKAB9AEEAIwAyAH0AQQAyACMAfQBGACMARgB9AFAAIwAjAH0AZAAZABkAfQBkADIAZAB9AGQAZAAyAImANwA3AFUAlgAeAB4AHgCWADcANwBVAJYANwA3AFoAooBaAEsAVQCvADwAIwAjAK8AVQBLAEYArwBaAEYARgCvAJEARgCRAK8AkQCRAEYArwFUAEYARgC7gCMAIwAjALuAKAAoACgAu4AyAGQASwC7gDwAPABpALuAQQA8AGQAu4BGAFAASwC7gEsASwBLALuASwBLAFoAu4BLAEsAtAC7gEsAVQBBALuASwBkADIAu4BQAEsAUAC7gFUAPABLALuAVQBBAEsAu4BVAEYAQQC7gFUASwBLALuAV4AyAFeAu4BkADIASwC7gGQASwAyALuAfQAyADIA4QBaADIAMgDhAIIAWgBaAPoAMgAyADIA+gA8AGQAjAD6ADwAjABkAPoASwCWAGQA+gBQAFAAjAD6AFUAVQCbAPoAZABkAGQA+gBkAJYASwD6AIIAbgBkAPoAjAA8AGQA+gCWAEsAZAD6AJYAZABLAPoArwBGAF8A+gCvAEsASwD6ANIAZADSAPoA0gDSAGQBBoB4AG4AaQETAG4AbgBuARMAfQBLAH0BEwCCAGQAZAEsAHgAQQBBATiASwBLAEsBOIBkAMgAfQE4gHMAcwDNATiAfQCWAGQBOIB9AMgAZAE4gMgAZAB9ATiAyAB9AGQBOIDIAH0AfQE4gOEAZABkATiA+gBkAH0BRQETAIIBEwFFARMBEwCCAVGAVQCgADwBdwBLAEsASwF3AG4AvgCWAXcAlgCWAJYBdwC+AG4AlgF3AMgAfQB9AZAAjACMAAABqQCqAFoAWgG1gH0AyABkAfQAZABkAGQB9ADIAAAAZAH0AMgAyADIAfQA8ACgAMgCJgDcAHMAcwJYALQAtAAAAu4BLAEsASw');
      if(which.length!==2291||data.length!==1176)return null;
      const choices=[];
      for(let i=0;i<147;i++){
        const row=[];
        for(let k=0;k<4;k++){const at=i*8+k*2;row.push((data.charCodeAt(at)<<8)|data.charCodeAt(at+1));}
        choices.push(Object.freeze(row));
      }
      const out=new Map();
      for(let i=0;i<2291;i++){
        const code=which.charCodeAt(i);
        if(code>=147)return null;
        out.set(ids[i],choices[code]);
      }
      return out;
    }catch(_){return null;}
  })();
  // Hash-validated English strings, lore and precise evolution *references*.
  // Never evaluate archived skill formulas or mutate player records.
  let codex=null;
  try{
    const source=document.getElementById('bf-original-unit-lore-data');
    if(source){
      const parsed=JSON.parse(source.textContent);
      if(parsed.schema==='bf-global-original-lore-codex-v1' && parsed.units?.length===2291 &&
         parsed.stats?.rows===2291 && parsed.provenance?.mstZipSha256===
         '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'){
        codex=new Map(parsed.units.map(u=>[u.id,u]));
      }
    }
  }catch(_){codex=null;}

  const elements={1:'Fire',2:'Water',3:'Earth',4:'Thunder',5:'Light',6:'Dark'};
  const panel=document.createElement('section');
  panel.className='bf-global-original-unit-archive';
  panel.setAttribute('aria-label','2022 original Brave Frontier Global unit encyclopedia');
  panel.innerHTML=[
    '<details id="bf-unit-encyclopedia">',
      '<summary>ORIGINAL GLOBAL UNIT ARCHIVE <small>2,291 historic forms · recovered 2022 records</small></summary>',
      '<p class="bf-archive-warning">Browse original Global names, stats, evolution IDs and artwork. This is an <strong>archive viewer</strong>, not your owned Unit Box. Archived characters are not automatically unlocked, recruited or playable.</p>',
      '<div class="bf-archive-filters">',
        '<label>Search by name or unit ID<input id="bf-archive-search" type="search" autocomplete="off" placeholder="Vargas, Miku, 810547…" /></label>',
        '<label>Element<select id="bf-archive-element"><option value="all">All elements</option><option value="1">Fire</option><option value="2">Water</option><option value="3">Earth</option><option value="4">Thunder</option><option value="5">Light</option><option value="6">Dark</option></select></label>',
        '<label>Rarity<select id="bf-archive-rarity"><option value="all">All rarities</option></select></label>',
        '<label>Record type<select id="bf-archive-type"><option value="all">All original records</option><option value="0">Standard unit entries</option><option value="other">Other original kind codes</option></select></label>',
        '<label>Sort<select id="bf-archive-sort"><option value="id">Original ID</option><option value="name">English name</option><option value="rarity">Highest rarity</option></select></label>',
      '</div>',
      '<div id="bf-archive-count" role="status" aria-live="polite"></div>',
      '<div id="bf-archive-results" class="bf-archive-results"></div>',
      '<div class="bf-archive-pagination"><button id="bf-archive-prev" type="button">◀ PREV</button><span id="bf-archive-page" aria-live="polite"></span><button id="bf-archive-next" type="button">NEXT ▶</button></div>',
      '<div id="bf-archive-detail" class="bf-archive-detail" hidden></div>',
      '<small class="bf-archive-footnote">Source: original decoded Global master tables, original Global English sgtext, and lossless thumbnail PNGs. Base and Lord fields are archive stats, not current demo combat calculations. Some artwork is not bundled yet.</small>',
    '</details>'
  ].join('');
  box.append(panel);
  const get=id=>panel.querySelector('#'+id);
  const search=get('bf-archive-search'),element=get('bf-archive-element'),rarity=get('bf-archive-rarity'),kind=get('bf-archive-type'),sort=get('bf-archive-sort');
  const results=get('bf-archive-results'),counter=get('bf-archive-count'),prev=get('bf-archive-prev'),next=get('bf-archive-next'),pageLabel=get('bf-archive-page'),detail=get('bf-archive-detail');
  const pageSize=24;
  let page=0;
  const rarities=[...new Set(units.map(u=>u.rarity))].filter(Number.isInteger).sort((a,b)=>a-b);
  for(const n of rarities){const o=document.createElement('option');o.value=String(n);o.textContent=n+' stars';rarity.append(o);}
  const fmt=v=>v==null||v===0?'—':String(v);
  const item=(name,cls,value)=>{const e=document.createElement(name);if(cls)e.className=cls;e.textContent=String(value);return e;};
  function matches(){
    const q=search.value.trim().toLocaleLowerCase();
    const data=units.filter(u=>(element.value==='all'||u.element===Number(element.value)) &&
      (rarity.value==='all'||u.rarity===Number(rarity.value)) &&
      (kind.value==='all'||(kind.value==='0'?u.unitKind===0:u.unitKind!==0)) &&
      (!q||String(u.id).includes(q)||u.name.toLocaleLowerCase().includes(q)));
    if(sort.value==='name')data.sort((a,b)=>a.name.localeCompare(b.name)||a.id-b.id);
    if(sort.value==='rarity')data.sort((a,b)=>b.rarity-a.rarity||a.id-b.id);
    return data;
  }
  function showDetail(id){
    const u=byId.get(id);
    if(!u)return false;
    detail.replaceChildren();
    const close=document.createElement('button');close.type='button';close.className='bf-archive-close';close.textContent='CLOSE DETAILS';
    close.addEventListener('click',()=>{detail.hidden=true;detail.replaceChildren();});
    detail.append(close,item('h4','',u.name),item('p','','Original unit ID '+u.id+' · '+(elements[u.element]||'Element '+u.element)+' · '+u.rarity+'★'));
    detail.append(item('p','', 'Max level '+fmt(u.unitMaxLevel)+' · Cost '+fmt(u.unitCost)+' · '+(u.nameSource==='2022_Global_English'?'2022 Global English localization':u.nameSource==='master_literal'?'Literal master-table name':'Original English name not recovered')));
    // Original 2022 source Imp cap values are displayed as archival reference;
    // the offline demo does not apply these caps or mutate existing unit stats.
    const imp=originalImpCaps?.get(id);
    if(imp)detail.append(item('p','',
      'Original Imp bonus caps · HP +'+imp[0]+' · ATK +'+imp[1]+' · DEF +'+imp[2]+' · REC +'+imp[3]+
      ' · source reference only; demo enhancement is unchanged.'));

    // v125: source-authenticated 2022 normal attack frame evidence. Nothing here
    // affects damage, playable recruitment, attack speed, RNG, XP, or player saves.
    const originalNormal=window.BFGlobalOriginalNormalHitArchiveV12500?.lookup?.(id);
    if(originalNormal){
      const frameDetail=document.createElement('details');
      frameDetail.className='bf-codex-bb-levels';
      frameDetail.append(item('summary','','ORIGINAL NORMAL ATTACK FRAMES · '+originalNormal.events.length+' HITS'));
      frameDetail.append(item('p','bf-codex-note',
        'Original 2022 frame-tick and damage-weight references, NOT verified playback seconds or native damage calculation. This archive reference does not recruit or activate units.'));
      frameDetail.append(item('p','',originalNormal.events.map(e=>e[0]+' ticks · '+e[1]+'% weight').join(' | ')));
      detail.append(frameDetail);
    }

    const expPattern=window.BFGlobalOriginalExpPatternIdsV12100?.lookup?.(id);
    if(Number.isSafeInteger(expPattern)&&[10,15,20].includes(expPattern))
      detail.append(item('p','','Original EXP pattern ID '+expPattern+
        ' · numeric EXP thresholds not verified for 2022 Global; gameplay remains DEMO.'));
    const table=document.createElement('table');
    const head=document.createElement('tr');
    for(const label of ['Stat','Base','Lord'])head.append(item('th','',label));
    table.append(head);
    for(const [label,k] of [['HP','Hp'],['ATK','Atk'],['DEF','Def'],['REC','Rec']]){
      const tr=document.createElement('tr');
      tr.append(item('th','',label),item('td','',fmt(u['unitBase'+k])),item('td','',fmt(u['unitLord'+k])));
      table.append(tr);
    }
    detail.append(table,item('p','', 'Leader skill ID '+fmt(u.lsId)+' · BB '+fmt(u.bbId)+' · SBB '+fmt(u.sbbId)+' · UBB '+fmt(u.ubbId)+' · Extra skill '+fmt(u.esId)));
    const evolutions=u.evo.map(next=>byId.get(next)?.name+' ('+next+')'||String(next));
    detail.append(item('p','', 'Source-listed next evolution: '+(evolutions.join(' / ')||'None recorded')));
    // Source-verified original Global character lore and skill descriptions.
    // Source text is inserted with textContent, never as HTML.
    const original=codex?.get(id);
    if(original){
      const section=document.createElement('section');
      section.className='bf-archive-codex';
      section.setAttribute('aria-label','Archived Global story, skills and recipes');
      section.append(item('h4','','ORIGINAL GLOBAL RECORDS'));
      section.append(item('p','bf-codex-note',
        'Official 2022 Global text / master references. Skill descriptions are historical text, NOT implemented demo battle effects. Evolution costs below are original records, not payable demo costs.'));
      if(original.story){
        const story=document.createElement('details');story.className='bf-codex-story';
        story.append(item('summary','','UNIT HISTORY'),item('p','bf-codex-story-text',original.story));
        section.append(story);
      }
      const labels={leader:'LEADER SKILL',bb:'BRAVE BURST',sbb:'SUPER BRAVE BURST',ubb:'ULTIMATE BRAVE BURST',extra:'EXTRA SKILL'};
      const available=Object.keys(labels).filter(key=>original[key]);
      if(available.length){
        const skills=document.createElement('details');skills.className='bf-codex-skills';
        skills.append(item('summary','','ORIGINAL SKILLS · '+available.length));
        for(const key of available){
          const record=original[key];
          const entry=document.createElement('article');entry.className='bf-codex-ability';
          entry.append(item('strong','',labels[key]+' · '+(record.name||'NAME NOT RECOVERED')));
          entry.append(item('small','','Original skill ID '+record.id));
          if(record.description)entry.append(item('p','',record.description));
          else entry.append(item('p','bf-codex-missing','Original English description not recovered.'));
          // Twenty-four original offensive Brave Bursts have recovered
          // damage modifier percentages for skill Lv1-10. Only Lv1 is
          // currently applied on top of DEMO base damage.
          const bbPower=key==='bb'?window.BFOriginalBBPower?.forUnit(id):null;
          if(bbPower){
            const power=document.createElement('details');
            power.className='bf-codex-bb-levels';
            power.append(item('summary','','ORIGINAL BB POWER · LV1–10'));
            power.append(item('p','bf-codex-note',
              'Original skill damage-modifier percentages. Battle currently uses ONLY Lv1; original DEF/damage, other skill effects and actual BB leveling are not yet restored.'));
            const values=document.createElement('div');
            values.className='bf-codex-bb-power-grid';
            bbPower.levels.forEach((pct,i)=>values.append(
              item('span',i===0?'bf-codex-bb-current':'','Lv'+(i+1)+' · +'+pct+'%')
            ));
            power.append(values);
            if(bbPower.secondaryUnmodeled)power.append(
              item('small','bf-codex-note','This BB has a separate archived effect group not implemented in demo combat.')
            );
            entry.append(power);
          }
          skills.append(entry);
        }
        section.append(skills);
      }
      if(original.recipes?.length){
        const recipes=document.createElement('details');recipes.className='bf-codex-recipes';
        recipes.append(item('summary','','SOURCE EVOLUTION RECIPES · '+original.recipes.length));
        for(const recipe of original.recipes){
          const target=byId.get(recipe.target);
          const entry=document.createElement('article');entry.className='bf-codex-recipe';
          entry.append(item('strong','','→ '+(target?.name||'Unit')+' · #'+recipe.target));
          entry.append(item('p','','Archive price: '+recipe.zel.toLocaleString()+' Zel'+
            (recipe.karma?' · '+recipe.karma.toLocaleString()+' Karma':'')));
          const amounts=new Map();
          for(const mat of recipe.materials){
            const key=mat.type+':'+mat.id;
            const current=amounts.get(key)||{id:mat.id,type:mat.type,name:mat.name,count:0};
            current.count++;amounts.set(key,current);
          }
          const text=[...amounts.values()].map(mat=>(mat.name?mat.name+' · ':'')+
            'Material '+mat.id+' (type '+mat.type+') ×'+mat.count).join(' · ');
          entry.append(item('p','',text||'No source-listed materials'));
          if(target){
            const jump=document.createElement('button');jump.type='button';
            jump.className='bf-codex-evo-jump';jump.textContent='VIEW NEXT FORM ›';
            jump.addEventListener('click',()=>{showDetail(target.id);detail.scrollIntoView({block:'start',behavior:'smooth'});});
            entry.append(jump);
          }
          recipes.append(entry);
        }
        section.append(recipes);
      }
      if(section.children.length>2)detail.append(section);
    }
    detail.hidden=false;
    return true;
  }
  function render(){
    const matched=matches();
    const total=Math.max(1,Math.ceil(matched.length/pageSize));
    page=Math.min(page,total-1);
    const shown=matched.slice(page*pageSize,(page+1)*pageSize);
    results.replaceChildren();
    for(const u of shown){
      const button=document.createElement('button');button.type='button';button.className='bf-archive-unit';
      button.setAttribute('aria-label',u.name+', original Global unit '+u.id+', view archived statistics');
      if(u.thumbnail){
        const portrait=document.createElement('img');
        portrait.src='content/unit_archive/unit_ills_thum_'+u.id+'.png';
        portrait.alt='';portrait.loading='lazy';button.append(portrait);
      }else button.append(item('span','bf-archive-noart','ART PENDING'));
      const text=document.createElement('span');text.className='bf-archive-unit-text';
      text.append(item('strong','',u.name),item('small','','#'+u.id+' · '+(elements[u.element]||'Unknown')+' · '+u.rarity+'★'));
      button.append(text);button.addEventListener('click',()=>showDetail(u.id));results.append(button);
    }
    if(!shown.length)results.append(item('p','bf-archive-nohits','No matching original Global unit records.'));
    counter.textContent=matched.length.toLocaleString()+' matching archived forms · '+archive.stats.thumbnailCount+' original thumbnails bundled';
    pageLabel.textContent='Page '+(page+1)+' / '+total;
    prev.disabled=page===0;next.disabled=page>=total-1;
  }
  for(const select of [search,element,rarity,kind,sort])select.addEventListener(select===search?'input':'change',()=>{page=0;detail.hidden=true;render();});
  prev.addEventListener('click',()=>{if(page>0){page--;render();}});
  next.addEventListener('click',()=>{if(page+1<Math.ceil(matches().length/pageSize)){page++;render();}});
  render();
  window.BFGlobalUnitArchive=Object.freeze({
    get count(){return units.length;},
    originalImpCaps:id=>originalImpCaps?.get(Number(id))||null,
    get thumbnailCount(){return archive.stats.thumbnailCount;},
    get loreCount(){return codex ? [...codex.values()].filter(u=>!!u.story).length : 0;},
    get originalCodexAvailable(){return codex!==null;},
    originalRecord:id=>codex?.get(Number(id))||null,
    get activePage(){return page+1;},
    get matchingCount(){return matches().length;},
    find:id=>byId.get(Number(id))||null,
    showDetail,
    refresh:render
  });
})();
