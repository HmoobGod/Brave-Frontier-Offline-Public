/* BF_PLAYABLE_ORIGINAL_HITS_V062 */
(() => {
  'use strict';
  if (window.BFPlayableAttackFramesV062) return;
  const source = __BF_PLAYABLE_ATTACK_FRAMES__;
  const old = window.BF_ARCHIVE_NORMAL_HITS;
  if (!old || source?.schema !== 'bf-global-playable-original-normal-hit-frames-v061' ||
      source.rows?.length !== 72 || !Array.isArray(source.rows)) return;
  const entries = new Map(), valid = new Map(), skipped = new Map();
  for (const record of source.rows) {
    if (!Number.isSafeInteger(record.unitId) || entries.has(record.unitId) ||
        typeof record.damageFrames !== 'string' ||
        !/^\d+:\d+:\d+:\d+(?:,\d+:\d+:\d+:\d+)*$/.test(record.damageFrames)) return;
    const events = record.damageFrames.split(',').map(x=>x.split(':').map(Number));
    const weight = events.reduce((a,x)=>a+x[1],0);
    const safe = events.every(e=>e.length===4 && e.every(Number.isSafeInteger) &&
      e[0]>=0 && e[1]>=0 && e[1]<=100 && e[2]>=0 && e[3]>=0);
    if (!safe) return;
    const frozen = Object.freeze({
      raw:record.damageFrames,weightsTotal:weight,
      events:Object.freeze(events.map(e=>Object.freeze(e)))
    });
    entries.set(record.unitId,frozen);
    if (weight===100) valid.set(record.unitId,frozen);
    else skipped.set(record.unitId,frozen);
  }
  if (entries.size!==72 || valid.size!==71 || skipped.size!==1 ||
      skipped.get(10023)?.weightsTotal!==130) return;
  const ids=[10011,20011,30011,40011,50011,60011];
  for (const id of ids) {
    const previous=old[String(id)],next=valid.get(id);
    if (!previous || !next || previous.raw!==next.raw ||
        previous.weightsTotal!==next.weightsTotal) return;
  }
  for (const [id,reference] of valid) if (!old[String(id)])
    old[String(id)]=reference;
  window.BFPlayableAttackFramesV062 = Object.freeze({
    count:entries.size,eligible:valid.size,excluded:1,
    lookup(id){return entries.get(Number(id)) || null;},
    eligibleForPlayback(id){return valid.has(Number(id));},
    excludedReason(id){return skipped.has(Number(id)) ?
      'Archived attack weights sum to '+skipped.get(Number(id)).weightsTotal+
      ' rather than 100; no invented normalization' : null;},
    sourceSha256:source.provenance.masterParts.map(x=>x.sha256).join(' / '),
    timingAssumption:'UNVERIFIED 60 ticks/s prototype timing; damage still DEMO'
  });
})();
