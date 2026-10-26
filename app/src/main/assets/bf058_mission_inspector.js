/* BF_ORIGINAL_MISSION_INSPECTOR_V058 */
(() => {
 'use strict';
 if(window.BFOriginalMissionInspector) return;
 const data=window.BFOriginalMissionEvidence;
 const reference=document.getElementById('questinfo');
 if(!data || data.count!==34 || !reference) return;
 const details=document.createElement('details');
 details.id='bf058-source-inspector';
 details.style.cssText='margin:9px 3px;padding:10px;border:1px solid #a18d67;border-radius:8px;background:#20202a;color:#e9e5db;font:12px/1.4 system-ui,sans-serif';
 const summary=document.createElement('summary');
 summary.textContent='Original 2022 quest-data evidence · read-only';
 summary.style.cssText='cursor:pointer;font-weight:700;color:#ecd2a3';
 const content=document.createElement('div');
 content.id='bf058-source-content';
 content.style.cssText='margin-top:7px;white-space:pre-wrap;overflow-wrap:anywhere;user-select:text';
 details.append(summary,content);
 reference.after(details);
 function current(){
    if(typeof QUEST==='undefined' || !QUEST)return null;
    return data.lookup(QUEST.missionId);
 }
 function show(){
    const row=current();
    details.hidden=!row;
    if(!row)return;
    const q=typeof QUEST!=='undefined'?QUEST:null;
    const battleCount=q?.battles;
    const parts=[
      'Mission '+row.missionId+' · '+(Number.isInteger(battleCount)?battleCount+' verified waves':'unknown wave count'),
      'Original source: '+data.facts.sourceFile,
      'Uninterpreted mission reference: '+row.rawEncounterRef,
      'Archived mimic field: '+row.rawMimicInfo+' (mechanics unknown)',
      'Archived additional reward: '+(row.rawRewards||'(blank)')+' (item identity unknown)',
      'Cutscene source field: '+row.rawCutscene+' (not restored)',
      'Mission NPC reference: '+row.rawMissionNpcId+' (no guest NPC claimed)',
      'Enemy identities, enemy AI, drop rates and damage formulas are NOT restored. Current battles are DEMO.'
    ];
    content.textContent=parts.join('\n');
 }
 // The core writes #questinfo when quest selection or waves change.
 new MutationObserver(show).observe(reference,{subtree:false,childList:true,characterData:true});
 window.BFOriginalMissionInspector=Object.freeze({
    refresh:show,
    get missionId(){return current()?.missionId??null},
    get open(){return details.open}
 });
 show();
})();
