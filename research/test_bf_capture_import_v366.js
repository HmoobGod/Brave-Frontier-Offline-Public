'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {validateCaptureEnvelope:verify} = require('./bf_capture_import_v366');
const capture = {
  sourceYear:2022,sourceType:'MissionStart',missionId:1,
  waves:[
    {waveIndex:0,formationId:101,enemySlots:[{slot:0,unitId:201},{slot:1,unitId:202}]},
    {waveIndex:1,formationId:102,enemySlots:[{slot:0,unitId:203}]}
  ]
};
// Synthetic fixture ONLY. These IDs are invented test values, never original data.
const canonical = JSON.stringify({adapterVersion:1,sourceYear:2022,
  sourceType:'MissionStart',missionId:1,waves:capture.waves});
const digest = crypto.createHash('sha256').update(canonical).digest('hex');
const valid = verify(capture,digest,1,2);
assert.equal(valid.accepted,true);
assert.equal(valid.productionAuthorized,false);
assert(Object.isFrozen(valid));
assert.equal(valid.canonicalCapture.missionId,1);
assert.equal(valid.canonicalCapture.waves[0].formationId,101);
assert(Object.isFrozen(valid.canonicalCapture));
assert(Object.isFrozen(valid.canonicalCapture.waves));
assert(Object.isFrozen(valid.canonicalCapture.waves[0]));
assert(Object.isFrozen(valid.canonicalCapture.waves[0].enemySlots));
assert(Object.isFrozen(valid.canonicalCapture.waves[0].enemySlots[0]));
const reject = (v,hash=digest,id=1,count=2) =>
  assert.equal(verify(v,hash,id,count).accepted,false);
reject(capture,'0'.repeat(64));
reject(capture,'not-an-external-pin');
reject(capture,digest,2);
reject(capture,digest,1,3);
reject({...capture,sourceYear:2021});
reject({...capture,sourceType:'community'});
reject({...capture,waves:[capture.waves[1],capture.waves[0]]});
reject({...capture,waves:[capture.waves[0],capture.waves[0]]});
reject({...capture,waves:[{...capture.waves[0],formationId:0},capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[]},capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[
  {slot:0,unitId:201},{slot:0,unitId:202}]},capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[
  {slot:0,unitId:999},{slot:1,unitId:202}]},capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[
  {slot:0,unitId:'201'}]},capture.waves[1]]});
reject(null);
reject({...capture,secret:'unpinned-extra-field'});
reject({...capture,waves:[{...capture.waves[0],enemyHp:1e9},capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[
  {...capture.waves[0].enemySlots[0],secret:'never-import'},
  capture.waves[0].enemySlots[1]]},capture.waves[1]]});
// The external pin binds the returned immutable snapshot, NOT the envelope:
// a stateful getter cannot change an already accepted formation later.
let formationReads=0;
const statefulWave={...capture.waves[0],
  get formationId(){return ++formationReads===1?101:999}};
const stateful={...capture,waves:[statefulWave,capture.waves[1]]};
const acceptedSnapshot=verify(stateful,digest,1,2);
assert.equal(acceptedSnapshot.accepted,true);
assert.equal(acceptedSnapshot.canonicalCapture.waves[0].formationId,101);
assert.equal(stateful.waves[0].formationId,999);
assert.equal(acceptedSnapshot.canonicalCapture.waves[0].formationId,101);
// Untrusted JSON adapters/objects must deny throwing providers instead of
// propagating exceptions into a future battle-starting caller.
reject({...capture,get sourceYear(){throw new Error('unreadable-year')}});
reject({...capture,get waves(){throw new Error('unreadable-waves')}});
reject({...capture,waves:[new Proxy(capture.waves[0],{
  get(target,prop){if(prop==='formationId')throw new Error('unreadable-formation');return target[prop]}
}),capture.waves[1]]});
reject({...capture,waves:[{...capture.waves[0],enemySlots:[{
  get slot(){throw new Error('unreadable-slot')},unitId:201
}]},capture.waves[1]]});
assert.equal(verify(capture,digest,1,2).accepted,true);
console.log('PASS synthetic capture provenance: no original formations certified');
