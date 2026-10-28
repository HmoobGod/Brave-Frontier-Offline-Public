/* v167: prove original source qualification, live hit ledger and v7 isolation. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const src='app/src/main/assets/bf16600_original_type5_element_resist.js';
const code=fs.readFileSync(src,'utf8');
assert.equal(code.split('BF_GLOBAL_ORIGINAL_TYPE5_ELEMENT_RESIST_V16600').length-1,1);
assert.ok(code.length<12000);
for(const forbidden of ['localStorage','saveProgress(','P.squad=','P.roster=','Math.random','fetch(','XMLHttpRequest']){
 assert.equal(code.includes(forbidden),false,'unexpected mutation or network: '+forbidden);
}
const catalog=JSON.parse(fs.readFileSync('source_data/bf_global_2022_playable_leader_catalog_v112.json','utf8'));
const english=JSON.parse(fs.readFileSync('source_data/bf_global_2022_playable_leader_english_v114.json','utf8'));
const rows=catalog.rows.filter(r=>r.skillTypeRaw==='5');
const labels=new Map(english.records.map(x=>[x.leaderSkillId,x.originalEnglishDescription]));
assert.equal(rows.length,12);
const elements=['Fire','Water','Earth','Thunder','Light','Dark'];
const profiles=new Map();
for(const r of rows){
 const i=r.element-1;
 assert.ok(i>=0&&i<6);
 assert.equal(r.passiveSkillInfoRaw,String(r.element)+',10');
 assert.equal(labels.get(r.leaderSkillId),'10% reduction in damage from '+elements[i]+' Types');
 profiles.set(r.unitId,{unitId:r.unitId,lsId:r.leaderSkillId,
  skillTypeRaw:r.skillTypeRaw,passiveSkillInfoRaw:r.passiveSkillInfoRaw});
}
const p={version:7,roster:[...profiles.keys()],squad:[10041]};
const actor={id:0,unitId:10041,active:true,hp:1000,maxHp:1000};
const bad={id:1,active:true,hp:1000};
const state={mode:'archive',over:false,party:[actor],wave:0,round:1};
const nodes=new Map();
function element(tag){
 return {tag,hidden:false,textContent:'',style:{},children:[],id:'',
  append(...args){this.children.push(...args);for(const x of args)if(x.id)nodes.set(x.id,x);},
  after(n){if(n.id)nodes.set(n.id,n);},
  addEventListener(){}};
}
const host=element('div');nodes.set('squadpicker',host);
const mode=element('select');nodes.set('mode',mode);
const reset=element('button');nodes.set('reset',reset);
const document={
 getElementById(id){return nodes.get(id)||null;},
 querySelector(){return null;},
 createElement:element
};
const window={
 BFGlobalPlayableLeadersV11200:{lookup:id=>profiles.get(id)||null},
 BFGlobalOriginalLeaderEnglishV11400:{lookup:id=>({originalEnglishDescription:labels.get(id)})},
 BFGlobalElementalCombatV6900:{normalize:s=>
   typeof s==='string'?elements.find(e=>e.toLowerCase()===s.trim().toLowerCase())||null:null}
};
const context=vm.createContext({window,P:p,S:state,document,
 effectiveUnit:id=>({id}),console});
const before=JSON.stringify(p);
vm.runInContext(code,context,{filename:src,timeout:5000});
const api=window.BFGlobalOriginalElementResistV16600;
assert.ok(api&&api.scaleIncoming);
assert.ok(nodes.has('bf16600-resist'));
assert.ok(nodes.has('bf16700-protection-totals'));
assert.equal(api.snapshot().applied,0);
for(const r of rows){
 p.squad[0]=r.unitId;
 actor.unitId=r.unitId;
 const e=elements[r.element-1];
 assert.equal(api.leader().resistedElement,e);
 assert.equal(api.scaleIncoming(100,e,actor),90);
 assert.equal(api.scaleIncoming(100,'unidentified',actor),100);
 const other=elements[r.element%6];
 assert.equal(api.scaleIncoming(100,other,actor),100);
 assert.equal(api.scaleIncoming(100,e,bad),100);
 assert.equal(api.scaleIncoming(100,e,{active:true,hp:20}),100);
}
assert.equal(api.snapshot().applied,12);
assert.equal(api.snapshot().prevented,120);
assert.equal(api.snapshot().recent.length,8);
assert.ok(nodes.get('bf16700-protection-totals').textContent.includes('120 actual DEMO damage prevented'));
p.squad[0]=10041;actor.unitId=10041;
assert.equal(api.scaleIncoming(1,'Fire',actor),1);
assert.equal(api.snapshot().prevented,120);
assert.equal(api.scaleIncoming(11,'Fire',actor),10);
assert.equal(api.snapshot().prevented,121);
assert.equal(api.scaleIncoming(0,'Fire',actor),0);
actor.hp=0;assert.equal(api.scaleIncoming(100,'Fire',actor),100);actor.hp=1000;
state.over=true;assert.equal(api.scaleIncoming(100,'Fire',actor),100);state.over=false;
state.mode='training';assert.equal(api.scaleIncoming(100,'Fire',actor),100);state.mode='archive';
p.squad[0]=10011;assert.equal(api.scaleIncoming(100,'Fire',actor),100);
p.squad[0]=10041;
assert.equal(JSON.stringify(p),before.replace('10041','10041')); // squad selection returned to original
const second={mode:'archive',over:false,party:[actor],wave:2,round:7};
context.S=second;
assert.equal(api.snapshot().applied,0);
assert.equal(api.snapshot().prevented,0);
assert.equal(api.snapshot().recent.length,0);
assert.equal(api.scaleIncoming(100,'Fire',actor),90);
const latest=api.snapshot();
assert.equal(latest.applied,1);
assert.equal(latest.prevented,10);
assert.equal(latest.recent[0].round,7);
assert.equal(latest.recent[0].wave,3);
assert.equal(latest.recent[0].result,90);
assert.equal(latest.recent[0].original,100);
assert.equal(latest.recent[0].sourceQualified,true);
assert.equal(JSON.stringify(p),before);
vm.runInContext(code,context,{filename:src,timeout:5000});
assert.equal(window.BFGlobalOriginalElementResistV16600,api,'must remain idempotent');
console.log('PASS v167 original type5 12-form source audit, exact damage delta, bounded battle ledger, reset, fail-closed exclusions, unchanged v7 state');
