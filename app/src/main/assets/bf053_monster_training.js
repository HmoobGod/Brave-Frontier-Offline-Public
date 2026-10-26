/* BF_ORIGINAL_MONSTER_TRAINING_V053 */
(() => {
 'use strict';
 if(window.BF053TrainingMonsters)return;
 const source = Object.freeze(__BF053_MANIFEST__);
 const art = new Image();
 art.src = source.derivedAtlas.apkPath;
 const ids = source.entries.map(e=>e.id);
 const byKey = new Map(source.entries.map(e=>[e.trainingKey,e]));
 const questInfo = document.getElementById('questinfo');
 if(!questInfo)return;
 const panel=document.createElement('section');
 panel.id='bf053-training-panel';
 panel.setAttribute('aria-label','Archived BF1 monster animation training');
 panel.style.cssText='margin:8px 3px;padding:9px;border:1px solid #7a9d82;border-radius:8px;background:#17221e;color:#e1f2e3;font:12px/1.4 system-ui,sans-serif';
 const title=document.createElement('strong');
 title.textContent='ORIGINAL MONSTER ART · TRAINING (0009–0016)';
 const caption=document.createElement('p');
 caption.textContent='Eight recovered 2022 BF1 sprite sheets and CSV frame crops. Monster identities, timing, wave order, HP, ATK, DEF and AI are still DEMO; no rewards.';
 const label=document.createElement('label');
 label.style.cssText='display:flex;gap:7px;align-items:start;color:#f6dfb2';
 const box=document.createElement('input');
 box.type='checkbox';box.id='bf053-extra-monsters';box.checked=false;
 const labelText=document.createElement('span');
 labelText.textContent='Try additional archived monsters in Training Mode (off by default)';
 label.append(box,labelText);
 const note=document.createElement('small');
 note.textContent='Session only. Enabling in Training resets the current practice battle; never changes your save.';
 note.style.cssText='display:block;margin-top:6px;opacity:.8';
 panel.append(title,caption,label,note);
 questInfo.after(panel);
 function encounter(mode,wave,candidates){
   if(!box.checked || mode!=='training' || !Array.isArray(candidates) || !candidates.length)
     return null;
   return candidates.map((base,index)=>{
      const entry=source.entries[(wave*3+index)%source.entries.length];
      if(!entry || !byKey.has(entry.trainingKey))return base;
      return {...base,id:entry.trainingKey,name:'Monster '+entry.id+' · original sprite / DEMO combat',
        sourceArtId:entry.id,sourceArtOriginal:true};
   });
 }
 function drawSprite(e,now,ctx,x,y){
   const entry=byKey.get(e.id);
   if(!entry || !art.complete || !art.naturalWidth)return false;
   if(art.naturalWidth!==source.derivedAtlas.columns*source.derivedAtlas.cellW ||
      art.naturalHeight!==source.derivedAtlas.rows*source.derivedAtlas.cellH)return false;
   const cellW=source.derivedAtlas.cellW,cellH=source.derivedAtlas.cellH;
   const frame=Math.floor(Math.max(0,now-(e.animSeed||0))/140)%entry.frames;
   const scale=.45;
   ctx.save();
   ctx.globalAlpha=e.hp>0?1:.18;
   ctx.imageSmoothingEnabled=false;
   // Keep legacy prototype facing: monsters on left, facing player on right.
   ctx.translate(x,y);ctx.scale(-1,1);
   ctx.drawImage(art,frame*cellW,entry.row*cellH,cellW,cellH,
     -Math.round(cellW*scale/2),-Math.round((cellH-16)*scale),
     Math.round(cellW*scale),Math.round(cellH*scale));
   ctx.restore();
   return true;
 }
 box.addEventListener('change',()=>{
    const battle=window.BF_debug?.state();
    if(battle?.busy){
       box.checked=!box.checked;
       note.textContent='Cannot change training artwork during an action.';
       return;
    }
    note.textContent='Training setting is session-only; archived missions are unchanged.';
    if(document.getElementById('mode')?.value==='training')window.BF_debug?.reset();
 });
 window.BF053TrainingMonsters=Object.freeze({
   sourceIds:ids, encounter, drawSprite,
   get enabled(){return box.checked},
   get imageLoaded(){return art.complete&&art.naturalWidth>0},
   get atlasUrl(){return source.derivedAtlas.apkPath}
 });
})();
