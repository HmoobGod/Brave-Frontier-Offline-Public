'use strict';
const assert = require('node:assert/strict');
const {planPlayerWaveTransition:plan} = require('./bf_native_player_wave_gate_v357');
const state = Object.freeze({
  missionId:1,waveIndex:0,totalWaves:3,requestEpoch:12,consumedEpoch:11,
  actor:'player',owner:'player0',mode:'archive',terminal:false,cancelled:false,battleWon:true
});
const evidence = Object.freeze({
  verified:true,sourceYear:2022,missionId:1,waveIndex:1,totalWaves:3,
  formationId:123,sourceDigest:'a'.repeat(64)
});
// Synthetic evidence ONLY; formation 123 is deliberately NOT asserted to be historical.
const baseline = plan(state,evidence);
assert.equal(baseline.allowed,true);
assert.equal(baseline.nextWaveIndex,1);
assert(Object.isFrozen(baseline));
for(const [change,value] of [
  ['actor','enemy'],['actor','partner'],['owner','npc'],['mode','arena'],
  ['terminal',true],['cancelled',true],['battleWon',false],
  ['requestEpoch',11],['waveIndex',2],['totalWaves',0],['missionId',0]
]) assert.equal(plan({...state,[change]:value},evidence).allowed,false,change);
for(const [change,value] of [
  ['verified',false],['sourceYear',2021],['missionId',2],
  ['waveIndex',0],['totalWaves',4],['formationId',0],
  ['sourceDigest','unverified']
]) assert.equal(plan(state,{...evidence,[change]:value}).allowed,false,change);
assert.equal(plan(state,null).allowed,false);
assert.equal(plan(null,evidence).allowed,false);
assert.equal(plan({...state,requestEpoch:12,consumedEpoch:12},evidence).allowed,false);
assert.equal(plan({...state,waveIndex:1}, {...evidence,waveIndex:2}).allowed,true);
console.log('PASS: synthetic player-only next-wave preflight; no combat/save side effects');
