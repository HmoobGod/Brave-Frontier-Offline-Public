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
assert.equal(verify(capture,digest,1,2).accepted,true);
console.log('PASS synthetic capture provenance: no original formations certified');
