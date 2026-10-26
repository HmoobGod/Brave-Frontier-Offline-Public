/* BF_HISTORICAL_TOWER_FORMATIONS_V055 */
(() => {
  'use strict';
  if (window.BF055TowerBosses) return;
  // Historical community encounter REFERENCES, not decoded native wave tables.
  // Original encounter IDs, battle stats, AI, drops and sprite identities remain unverified.
  const recorded = window.BF052BossIntel?.entries;
  if (!Array.isArray(recorded) || recorded.length !== 5) return;
  const expected = Object.freeze({
    81:['King Glowy','King Gloomy'],
    82:['Behemoth','Skeleton','Skeleton'],
    83:['Wyvern'],
    84:['King Burny','King Squirty','King Mossy','King Sparky']
  });
  const formations = new Map();
  for (const [key,names] of Object.entries(expected)) {
    const record = recorded.find(row=>row.missionId === Number(key));
    if (!record || !Array.isArray(record.bosses)) return;
    const expanded = record.bosses.flatMap(b=>Array.from({length:b.count||1},()=>b));
    if (expanded.length !== names.length ||
        expanded.some((b,i)=>b.name!==names[i] ||
          (b.hp!=null && (!Number.isInteger(b.hp) || b.hp<=0)))) return;
    formations.set(Number(key),Object.freeze(expanded));
  }
  const anchor = document.getElementById('questinfo');
  if (!anchor) return;
  const panel = document.createElement('section');
  panel.id = 'bf055-formations';
  panel.setAttribute('aria-label','Optional historical Tower of Mistral boss formations');
  const label = document.createElement('label');
  const toggle = document.createElement('input');
  toggle.type = 'checkbox';
  toggle.id = 'bf055-enable-tower-formations';
  toggle.checked = false;
  const text = document.createElement('span');
  text.textContent = 'Optional historical boss names & groups (Tower Missions 81–84)';
  label.append(toggle,text);
  const note=document.createElement('small');
  note.id='bf055-formation-note';
  note.textContent = 'Off by default. Names and group sizes from historical sources; generic silhouettes, DEMO ATK/DEF, combat, AI and drops. Session only; changing resets battle.';
  panel.append(label,note);
  panel.style.cssText = 'margin:8px 3px;padding:10px;border:1px solid #958668;border-radius:8px;background:#211e1d;color:#f6efdb;font:12px/1.35 system-ui,sans-serif';
  label.style.cssText='display:flex;align-items:flex-start;gap:7px;font-weight:700';
  note.style.cssText='display:block;opacity:.9;margin-top:5px';
  anchor.after(panel);

  function refresh(){
    const id = typeof QUEST === 'undefined' ? -1 : QUEST.missionId;
    panel.hidden = !formations.has(id);
  }
  function encounter(missionId,wave,totalWaves,mode,fallback){
    if(!toggle.checked || mode !== 'archive' ||
       wave !== totalWaves-1 || !Array.isArray(fallback) || !fallback.length ||
       !formations.has(missionId)) return null;
    return formations.get(missionId).map((boss,i)=>{
      // Only source-proven 15k HP for Mission 81; other HP stays DEMO.
      const demo=fallback[i%fallback.length];
      const verifiedHp=boss.hp;
      return {
        id:demo.id, // never claim this unrelated archived art identifies the named boss
        name:boss.name+' · DEMO combat',
        maxHp:verifiedHp || demo.maxHp,
        atk:demo.atk,def:demo.def,
        historicalBossPreview:true,
        verifiedBossHp:Number.isInteger(verifiedHp),
        bossReferenceName:boss.name
      };
    });
  }
  function drawPlaceholder(e,ctx,x,y){
    if(!e.historicalBossPreview)return false;
    // Neutral placeholder instead of assigning the wrong original monster sprite.
    ctx.save();
    ctx.globalAlpha=e.hp>0?1:.25;
    ctx.fillStyle='#192332';ctx.strokeStyle='#c2d2df';ctx.lineWidth=2;
    ctx.beginPath();ctx.ellipse(x,y-25,24,33,0,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.fillStyle='#eef3ff';ctx.textAlign='center';
    ctx.font='bold 32px Georgia,serif';ctx.fillText('?',x,y-14);
    ctx.font='bold 9px system-ui';ctx.fillText('ART UNKNOWN',x,y+8);
    ctx.restore();
    return true;
  }
  toggle.addEventListener('change',()=>{
    if(window.BF_debug?.state()?.busy){
      toggle.checked=!toggle.checked;
      note.textContent='Cannot change boss preview while an action is running.';
      return;
    }
    note.textContent='Session-only research preview; changing resets battle. Enemy combat and rewards remain DEMO.';
    window.BF_debug?.reset();
    refresh();
  });
  new MutationObserver(refresh).observe(anchor,{childList:true,characterData:true,subtree:false});
  window.BF055TowerBosses=Object.freeze({
    encounter,drawPlaceholder,refresh,
    get enabled(){return toggle.checked},
    get missionIds(){return Array.from(formations.keys())}
  });
  refresh();
})();
