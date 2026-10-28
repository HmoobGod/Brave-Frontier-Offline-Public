/* BF_GLOBAL_GEM_ATOMIC_PERSISTENCE_LAB_V15900
 * RESEARCH HARNESS ONLY. NOT LOADED BY ANDROID APK OR PRODUCTION WEBVIEW.
 * Demonstrates atomic ONE-key write in browser storage for a prospective
 * first-clear Gem transaction. Legacy v7 remains unmodified.
 */
(function(root) {
 'use strict';
 const KEY='bf_global_offline_RESEARCH_ONLY_gem_lab_v159';
 // Exactly 22 live original finale IDs in source v156; seven Amdahl omitted.
 const ELIGIBLE=[12,23,33,43,53,63,73,85,204,214,224,234,244,254,265,
                 304,314,324,334,344,354,365];
 const ELIGIBLE_SET=new Set(ELIGIBLE);
 const MAX_MODEL_GEMS=999999; // SAFETY TEST BOUND, NOT AUTHENTIC 2022 CAP
 const own=(obj,k)=>Object.prototype.hasOwnProperty.call(obj,k);
 function isObject(obj) {return obj!==null&&typeof obj==='object'&&!Array.isArray(obj);}
 function assert(ok,label){if(!ok)throw new Error('v159 lab: '+label);}
 function safeCount(n){return Number.isSafeInteger(n)&&n>=0;}
 function validKeys(obj){
  assert(isObject(obj),'invalid clear dictionary');
  const out={};
  for(const [key,value] of Object.entries(obj)){
   assert(/^[1-9]\d*$/.test(key)&&Number.isSafeInteger(Number(key))&&
          Number(key)<=100000000,'unsafe mission key');
   assert(safeCount(value),'unsafe clear count');
   out[key]=value;
  }
  return out;
 }
 function validIds(arr,label){
  assert(Array.isArray(arr)&&arr.length<=22,label+' array');
  let last=0;
  for(const id of arr){
   assert(Number.isSafeInteger(id)&&ELIGIBLE_SET.has(id)&&id>last,label+' sorted ids');
   last=id;
  }
  return arr;
 }
 function validate(s){
  assert(isObject(s)&&Object.keys(s).sort().join(',')==='gems,legacyFinales,modelVersion,paidFinales,questClears','strict schema');
  assert(s.modelVersion===1&&safeCount(s.gems)&&s.gems<=MAX_MODEL_GEMS,'invalid wallet');
  validKeys(s.questClears);
  validIds(s.legacyFinales,'legacy');validIds(s.paidFinales,'paid');
  const legacy=new Set(s.legacyFinales);
  for(const id of s.paidFinales){
   assert(!legacy.has(id),'duplicate legacy/paid');
   assert(s.questClears[String(id)]>=1,'paid without clear');
  }
  assert(s.paidFinales.length===s.gems,'prototype one Gem per paid finale');
  for(const id of s.legacyFinales){assert(s.questClears[String(id)]>=1,'legacy without clear');}
  return s;
 }
 function clone(s){return JSON.parse(JSON.stringify(s));}
 function fromLegacy(old){
  assert(isObject(old)&&old.version===7,'only old v7 progress');
  const c=validKeys(old.questClears);
  return validate({modelVersion:1,gems:0,questClears:c,
     legacyFinales:ELIGIBLE.filter(id=>(c[String(id)]||0)>0),paidFinales:[]});
 }
 function apply(state,missionId){
  const s=clone(validate(state));
  assert(Number.isSafeInteger(missionId)&&missionId>0&&missionId<=100000000,'mission id');
  const key=String(missionId),prior=s.questClears[key]||0;
  assert(prior<Number.MAX_SAFE_INTEGER,'clear overflow');
  s.questClears[key]=prior+1;
  let credited=false;
  if(ELIGIBLE_SET.has(missionId)&&prior===0&&
     !s.legacyFinales.includes(missionId)&&!s.paidFinales.includes(missionId)&&
     s.gems<MAX_MODEL_GEMS){
   s.gems+=1;s.paidFinales.push(missionId);
   s.paidFinales.sort((a,b)=>a-b);
   credited=true;
  }
  return {state:validate(s),credited};
 }
 function read(storage){
  const raw=storage.getItem(KEY);
  if(raw===null)return null;
  assert(typeof raw==='string'&&raw.length<250000,'oversized saved prototype');
  return validate(JSON.parse(raw));
 }
 function commit(storage,state){
  const s=validate(state);
  // Browsers atomically replace one localStorage key or throw; never write
  // the existing game key. This alone does NOT make two-key game + lab
  // commits atomic; production integration needs the single canonical save.
  storage.setItem(KEY,JSON.stringify(s));
  return read(storage);
 }
 const api=Object.freeze({
  source:'research-only; not an authentic 2022 wallet or migration policy',
  key:KEY,eligible:Object.freeze(ELIGIBLE.slice()),
  version:1,livePayoutEnabled:false,v7SaveMutation:false,
  legacyPolicyProven:false,nativeGemCapProven:false,
  fromLegacy,apply,read,commit
 });
 root.BFGlobalGemAtomicPersistenceLabV15900=api;
})(typeof window!=='undefined'?window:globalThis);
