/* v169 isolated optional Imp feeding test. No browser or Android runtime required. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const script=fs.readFileSync('app/src/main/assets/bf16900_optional_imp_fusion.js','utf8');
const bridge=fs.readFileSync('app/src/main/assets/bf11100_original_starter_leader_combat.js','utf8');
const java=fs.readFileSync('app/src/main/java/org/bravefrontier/offline/MainActivity.java','utf8');
assert.match(script,/BF_GLOBAL_OPTIONAL_IMP_FUSION_V16900/);
assert.match(bridge,/BFGlobalOptionalImpsV16900\?\.apply\?\.\(unit,i\)/);
assert(java.indexOf('readPackagedText("bf_global_unit_archive.js")') <
       java.indexOf('readPackagedText("bf16900_optional_imp_fusion.js")'));
assert(java.indexOf('readPackagedText("bf16800_original_level_one_lord_combat.js")') <
       java.indexOf('readPackagedText("bf16900_optional_imp_fusion.js")'));
const coreSave='bf_global_offline_demo_v7';
for(const denied of ['localStorage.removeItem(', 'localStorage.clear(', 'P.roster=', 'P.unitExp=',
                     'P.questClears=', 'saveProgress(', 'awardDemoRewards(', 'Math.random', 'fetch('])
  assert(!script.includes(denied),denied);
const db=new Map([[coreSave,'{"version":7,"roster":[10011]}']]);
let failWrite=false;
const localStorage={getItem:k=>db.get(k)??null,setItem:(k,v)=>{
  if(failWrite)throw Error('disk full');db.set(k,String(v));
}};
const elements=new Map();
const mode={value:'archive',addEventListener(){}};
function el(tag='div'){
  const e={tag,id:'',value:'',textContent:'',hidden:false,disabled:false,style:{},open:false,
    children:[],options:[],append(...items){for(const item of items){this.children.push(item);
      if(tag==='select'&&item.tag==='option'){this.options.push(item);
        if(this.options.length===1)this.value=item.value;}
      if(item.id)elements.set(item.id,item)}},
    after(item){if(item.id)elements.set(item.id,item)},
    replaceChildren(...items){this.children=[];this.options=[];this.value='';
      this.append(...items)},addEventListener(type,fn){this['on'+type]=fn},
    setAttribute(){}};
  return e;
}
elements.set('mode',mode);elements.set('squadpicker',el());
const document={getElementById:k=>elements.get(k)||null,createElement:el};
const P={version:7,roster:[10011,10025,60015,10041],squad:[10011],
  questClears:{10:2},unitExp:{10011:0}};
const S={mode:'archive',party:[]};
const source={10011:[400,160,80,80],10025:[1000,240,560,400],
  60015:[700,580,580,280],10041:[400,160,80,80],
  20011:[750,350,200,350],99999:[0,0,0,0]};
const window={BFGlobalUnitArchive:{count:2291,originalImpCaps:id=>source[id]||null}};
const ctx={window,P,S,document,localStorage,effectiveUnit:baseId=>({id:baseId,stats:{
  hp:1030,atk:500,def:410,rec:320}})};
vm.runInNewContext(script,ctx,{filename:'bf16900_optional_imp_fusion.js'});
const imp=window.BFGlobalOptionalImpsV16900;
assert(imp,'module not constructed');
assert.equal(imp.snapshot().enabled,false);
assert.equal(imp.plan(10011),null);
assert.deepEqual(Array.from(imp.maximum(10011,'custom').maximum),[500,200,100,100]);
assert.deepEqual(Array.from(imp.maximum(10025,'custom').maximum),[1250,300,700,500]);
assert.deepEqual(Array.from(imp.maximum(10011,'original').maximum),[400,160,80,80]);
assert.deepEqual(Array.from(imp.gains.arton),[150,60,60,60]);
assert.equal(imp.activate(),true);
assert.equal(imp.activate(),false);
assert.equal(imp.snapshot().mode,'custom');
assert.equal(imp.stock().arton,5);
assert.deepEqual(Array.from(imp.bonus(10011)),[0,0,0,0]);
assert.equal(db.get(coreSave),'{"version":7,"roster":[10011]}');
assert.equal(imp.claim(),0,'no retroactive claim for existing cleared quests');
P.questClears[10]=5;
assert.equal(imp.claim(),6,'two Artons per newly recorded DEMO clear');
assert.equal(imp.claim(),0,'claim must be idempotent');
assert.equal(imp.stock().arton,11);
assert.equal(imp.plan(10011,'smart').total,4);
assert.equal(imp.plan(10011,'smart').materials.arton,4);
const spent=imp.feed(10011);
assert(spent&&spent.total===4);
assert.deepEqual(Array.from(imp.bonus(10011)),[500,200,100,100]);
assert.equal(imp.stock().arton,7);
assert.equal(imp.feed(10011),false,'maxed unit cannot waste Imp materials');
assert.equal(imp.plan(10011,'arton').total,0);
const newBattleUnit=()=>({active:true,baseId:10011,unitId:10011,level:1,
  maxHp:1030,hp:1030,atk:500,def:410,rec:320});
const unit=newBattleUnit();
imp.apply(unit,0);
assert.equal(unit.maxHp,1530);assert.equal(unit.atk,700);
assert.equal(unit.def,510);assert.equal(unit.rec,420);
imp.apply(unit,0);assert.equal(unit.maxHp,1530,'double application forbidden');
const snap=imp.snapshot();assert.equal(snap.noCanonicalSaveMutation,true);
S.party=[unit];assert.equal(imp.snapshot().rows.length,1);
mode.value='training';const training=newBattleUnit();
imp.apply(training,0);assert.equal(training.hp,1030);
mode.value='archive';assert.equal(imp.modeChange('original'),true);
const originalUnit=newBattleUnit();imp.apply(originalUnit,0);
assert.equal(originalUnit.maxHp,1430);assert.equal(originalUnit.atk,660);
assert.deepEqual(Array.from(imp.bonus(10011)),[500,200,100,100],
  'switching back to custom must preserve excess paid-for Imp progress');
assert.equal(imp.modeChange('custom'),true);
assert.equal(imp.view(10011).remaining.reduce((a,b)=>a+b,0),0);
const saved=imp.exportState();assert.equal(typeof saved,'string');
const existing=imp.stock().arton;
assert.equal(imp.importState('{"version":1}'),false);
assert.equal(imp.stock().arton,existing);
assert.equal(imp.importState(saved),true);
failWrite=true;
assert.equal(imp.feed(10025),false,'write failure must roll back full transaction');
assert.equal(imp.stock().arton,existing);
failWrite=false;
const second=imp.feed(10025);
assert(second&&second.total>0);
assert.equal(imp.view(10025).applied[0]>0,true);
assert.equal(db.get(coreSave),'{"version":7,"roster":[10011]}');
const wrongUnit={...newBattleUnit(),unitId:20011};imp.apply(wrongUnit,0);
assert.equal(wrongUnit.hp,1030,'mismatched form cannot receive Imp bonuses');
// Corrupted optional sidecar must fail closed, while explicit restore must work.
const backup=db.get(imp.key);db.set(imp.key,'{malformed');
const window2={BFGlobalUnitArchive:window.BFGlobalUnitArchive};
const ctx2={...ctx,window:window2};
vm.runInNewContext(script,ctx2);
assert.equal(window2.BFGlobalOptionalImpsV16900.snapshot().enabled,false);
assert.equal(window2.BFGlobalOptionalImpsV16900.feed(10011),false);
assert.equal(window2.BFGlobalOptionalImpsV16900.importState(backup),true);
assert.equal(window2.BFGlobalOptionalImpsV16900.snapshot().enabled,true);
console.log('PASS v169: 125% source caps, 5 Imp types, 4-item full Vargas Smart batch, Arton quest supply, original mode, source-only owned form, battle application, save rollback, corrupted backup restore');
