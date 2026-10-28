/* BF_GLOBAL_ORIGINAL_2022_LEGEND_STONE_MERIT_EXCHANGE_V15300 */
(() => {
 'use strict';
 // Source-authentic 2022 listing. The mission Exchange Hall uses Merit
 // Points (separately corroborated by community documentation). No runtime
 // currency, source item inventory, evolving, purchases or save mutation.
 const evo=window.BFGlobalOriginalStarterTypedEvolutionV13000;
 if(window.BFGlobalOriginalLegendStoneExchangeV15300||
    typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster)||
    !evo||evo.source?.sourceItemId!==110100||
    evo.source?.playableExpansion!==false||
    evo.source?.sourceItemAcquisitionKnown!==false)return;
 const host=document.getElementById('bf13000-source-evolutions');
 if(!host)return;
 // [offerId, original cost, monthly max, raw item payload, starts, ends].
 // Actual owner 2022 F_ACHIEVEMENT_TRADE_MST_2_Ver432 rows.
 const records=[[80000056,4000,99,'4:110100:1:0','2022-01-01 08:00:00','2022-02-01 07:59:59'],[80000057,4000,99,'4:110100:1:0','2022-02-01 08:00:00','2022-03-01 07:59:59'],[80000058,4000,99,'4:110100:1:0','2022-03-01 08:00:00','2022-04-01 07:59:59'],[80000059,4000,99,'4:110100:1:0','2022-04-01 08:00:00','2022-05-01 07:59:59']];
 if(records.length!==4||records.some((r,i)=>r.length!==6||
    r[0]!==80000056+i||r[1]!==4000||r[2]!==99||
    r[3]!=='4:110100:1:0'||typeof r[4]!=='string'||typeof r[5]!=='string'))return;
 const freeze=Object.freeze;
 const rows=freeze(records.map(([id,cost,limit,item,starts,ends])=>freeze({
    offerId:id,originalMeritCost:cost,historicalLimit:limit,
    originalRawReward:item,itemId:110100,itemName:'Legend Stone',
    validFromIn2022:starts,validUntilIn2022:ends,
    currentlyAvailable:false,livePurchasable:false
 })));
 const source=freeze({
    archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
    exchangeMasterSha256:'00fc854cdcf3f507ac0544a6e6774af5afad22cf89e0c1b535d11258ab3b54e9',
    sourceMaster:'F_ACHIEVEMENT_TRADE_MST_2_Ver432.json',
    originalSourceItemId:110100,
    meritCurrencyFromIndependentHistoricalDocumentation:true,
    originalSourceCurrencyColumnNotExplicit:true,
    year:2022,historicalRows:4,originalPrice:4000,
    sourceOnly:true,playableEvolutionsUnlocked:false,
    liveMeritEarnings:false,liveAcquisition:false,saveMutation:false
 });
 const panel=document.createElement('details');
 panel.id='bf15300-legend-stone-source';
 panel.style.cssText='margin:10px 4px;padding:10px;border:1px solid #86a7a0;'+
    'border-radius:7px;background:#233b39;color:#eff7ec;font:12px/1.55 system-ui';
 const title=document.createElement('summary');
 title.style.cssText='font-weight:750;cursor:pointer;min-height:37px';
 title.textContent='2022 ORIGINAL LEGEND STONE · MERIT EXCHANGE (SOURCE REFERENCE)';
 const paragraph=document.createElement('p');paragraph.id='bf15300-price';
 paragraph.textContent='Legend Stone (original item #110100) · '+source.originalPrice.toLocaleString('en-US')+
   ' Merit Points per stone · original per-period offer limit 99.';
 const history=document.createElement('p');
 history.textContent='Original source lists four consecutive monthly offer windows (January–April 2022), '+
   'ending May 1, 2022. These are historical source records, NOT a restriction on offline play.';
 const notice=document.createElement('small');
 notice.textContent='Merit Points as Exchange Hall currency are corroborated by historical Global game '+
   'documentation, not an explicit currency field in this archived table. '+
   'No Merit Points balance, earning rules, spending, item inventory or 7★/8★ '+
   'evolution purchase is enabled. Existing DEMO progression and saved data are untouched.';
 panel.append(title,paragraph,history,notice);
 host.after(panel);
 window.BFGlobalOriginalLegendStoneExchangeV15300=freeze({
   source,offers:rows,
   lookup:id=>Number.isSafeInteger(id)?rows.find(r=>r.offerId===id)||null:null
 });
})();
