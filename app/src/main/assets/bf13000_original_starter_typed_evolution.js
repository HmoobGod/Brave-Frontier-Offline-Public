/* BF_GLOBAL_ORIGINAL_STARTER_TYPED_EVOLUTION_V13000 */
(() => {
 'use strict';
 // Original 2022 F_UNIT_EVO: unit material type 1 != item material type 2.
 // Never treat source item 110100 as P.materials or spend any inventory.
 if(window.BFGlobalOriginalStarterTypedEvolutionV13000 ||
    typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster)||
    !Array.isArray(P.squad)||typeof effectiveUnit!=='function')return;
 const raw=[[10016,10015,7,38,120,1500000,0,[[1,1,10354],[2,1,50354],[3,1,10133],[4,1,10132],[5,2,110100]]],[10017,10016,8,45,150,3000000,1000000,[[1,1,10354],[2,1,10354],[3,1,50354],[4,1,10133],[5,1,10132],[6,1,10131],[7,1,10130],[8,2,110100]]],[20016,20015,7,38,120,1500000,0,[[1,1,20344],[2,1,50354],[3,1,20133],[4,1,20132],[5,2,110100]]],[20017,20016,8,45,150,3000000,1000000,[[1,1,20344],[2,1,20344],[3,1,50354],[4,1,20133],[5,1,20132],[6,1,20131],[7,1,20130],[8,2,110100]]],[30016,30015,7,38,120,1500000,0,[[1,1,30334],[2,1,50354],[3,1,30133],[4,1,30132],[5,2,110100]]],[30017,30016,8,45,150,3000000,1000000,[[1,1,30334],[2,1,30334],[3,1,50354],[4,1,30133],[5,1,30132],[6,1,30131],[7,1,30130],[8,2,110100]]],[40016,40015,7,38,120,1500000,0,[[1,1,40334],[2,1,50354],[3,1,40133],[4,1,40132],[5,2,110100]]],[40017,40016,8,45,150,3000000,1000000,[[1,1,40334],[2,1,40334],[3,1,50354],[4,1,40133],[5,1,40132],[6,1,40131],[7,1,40130],[8,2,110100]]],[50016,50015,7,38,120,1500000,0,[[1,1,50394],[2,1,50354],[3,1,50123],[4,1,50122],[5,2,110100]]],[50017,50016,8,45,150,3000000,1000000,[[1,1,50394],[2,1,50394],[3,1,50354],[4,1,50123],[5,1,50122],[6,1,50121],[7,1,50120],[8,2,110100]]],[60016,60015,7,38,120,1500000,0,[[1,1,60344],[2,1,50354],[3,1,60123],[4,1,60122],[5,2,110100]]],[60017,60016,8,45,150,3000000,1000000,[[1,1,60344],[2,1,60344],[3,1,50354],[4,1,60123],[5,1,60122],[6,1,60121],[7,1,60120],[8,2,110100]]]];
 const freeze=Object.freeze;
 const rows=new Map();
 for(const v of raw){
   const [unitId,fromId,rarity,cost,maxLevel,zel,karma,mats]=v;
   if(!Number.isSafeInteger(unitId)||rows.has(unitId)||
      ![7,8].includes(rarity)||unitId%100!==rarity+9||
      fromId!==unitId-1||cost!==(rarity===7?38:45)||
      maxLevel!==(rarity===7?120:150)||
      zel!==(rarity===7?1500000:3000000)||
      karma!==(rarity===7?0:1000000)||
      mats.length!==(rarity===7?5:8)||
      mats.some(([slot,type,id],i)=>slot!==i+1||![1,2].includes(type)||
        !Number.isSafeInteger(id)||id<=0)||
      mats.filter(x=>x[1]===2).length!==1||
      mats.at(-1)[1]!==2||mats.at(-1)[2]!==110100)return;
   rows.set(unitId,freeze({unitId,fromId,rarity,unitCost:cost,
     maxLevel,zel,karma,materials:freeze(mats.map(
       ([slot,type,id])=>freeze({slot,type,id,kind:type===1?'original unit':'original item'})))}));
 }
 if(rows.size!==12||![10016,20016,30016,40016,50016,60016].every(x=>rows.has(x)&&rows.has(x+1)))return;
 const source=freeze({year:2022,archiveSha256:
   '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   typedRowsSha256:'a5b91a61b5101f378fcc2692ca97b601c2034cf150c0716e9b561aebc7a0bed6',totalForms:12,
   sourceItemId:110100,itemMeaning:'source type 2; original non-unit evolution item',
   verifiedEnglishItemName:true,sourceItemName:'Legend Stone',
   sourceTextPackSha256:'4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285',
   sourceItemAcquisitionKnown:false,
   playableExpansion:false,inventoryMutated:false,saveFieldsAdded:0});
 function lookup(id){return Number.isSafeInteger(id)?rows.get(id)||null:null;}
 function snapshot(){
   const possible=[];
   for(const base of P.roster){
     if(!Number.isSafeInteger(base))continue;
     const current=effectiveUnit(base);
     const next=lookup((current?.id||0)+1);
     if(next&&next.fromId===current?.id)
       possible.push(freeze({ownedBaseId:base,fromId:current.id,
         sourceNextId:next.unitId,notYetPlayable:true}));
   }
   return freeze({possible:freeze(possible),source,playableFormCountChanged:false});
 }
 const host=document.getElementById('bf12600-original-squad-cost')||
   document.getElementById('squadpicker');
 if(!host)return;
 const panel=document.createElement('details');panel.id='bf13000-source-evolutions';
 panel.style.cssText='margin:8px 4px;padding:10px;border:1px solid #acaa83;'+
   'border-radius:7px;background:#303729;color:#f3f1df;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='ORIGINAL 2022 7★ / 8★ STARTER EVOLUTION RECIPES · SOURCE ONLY';
 title.style.cssText='font-weight:800;cursor:pointer;min-height:38px';
 const select=document.createElement('select');select.id='bf13000-select';
 select.setAttribute('aria-label','Archived starter evolution recipe');
 select.style.cssText='margin:8px 0;width:100%;min-height:42px;background:#30443e;color:#f9f5e9';
 for(const r of rows.values()){
   const opt=document.createElement('option');opt.value=String(r.unitId);
   opt.textContent=r.rarity+'★ #'+r.unitId+' (from #'+r.fromId+')';select.append(opt);
 }
 const list=document.createElement('ol');list.id='bf13000-materials';
 const costs=document.createElement('p');costs.id='bf13000-price';
 const note=document.createElement('small');note.textContent=
   'Original 2022 typed recipe metadata only. Type 1 = material UNIT; '+
   'type 2 = separate original evolution ITEM #110100 (Legend Stone, 2022 Global English). '+
   'Item acquisition, current inventory and summoner resource handling are '+
   'not restored. No 7★/8★ units are playable here, and no resources or saved '+
   'evolutions are changed.';
 panel.append(title,select,costs,list,note);host.after(panel);
 function refresh(){
   const row=lookup(Number(select.value));list.replaceChildren();
   if(!row)return null;
   costs.textContent=row.fromId+' → '+row.unitId+' · '+row.rarity+'★ · '+
     'original cost '+row.unitCost+' · max Lv '+row.maxLevel+' · '+
     row.zel.toLocaleString('en-US')+' Zel · '+row.karma.toLocaleString('en-US')+' Karma';
   for(const m of row.materials){
     const item=document.createElement('li');item.textContent='Slot '+m.slot+': '+
       (m.type===1?'original material UNIT':'original evolution ITEM')+' #'+m.id+
       (m.type===2?' · original English: Legend Stone':'');
     list.append(item);
   }
   return row;
 }
 select.addEventListener('change',refresh);refresh();
 window.BFGlobalOriginalStarterTypedEvolutionV13000=
   freeze({source,lookup,snapshot,refresh});
})();
