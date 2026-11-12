/* BF_CAPTURE_IMPORT_V366: source-only candidate adapter; never production spawn authorization. */
'use strict';
const crypto = require('node:crypto');

/**
 * Accept only an independently pinned, explicitly versioned adapter snapshot.
 * Fixture values are synthetic; this does NOT authenticate a 2022 capture.
 * Future runtime wiring MUST source mission/wave expectations from the pinned
 * original 2022 tuple ledger (SHA a1b36659...), never this envelope.
 */
function validateCaptureEnvelope(envelope, expectedDigest, expectedMissionId, expectedWaveCount) {
  const deny = reason => Object.freeze({accepted:false, reason});
  const positive = value => Number.isSafeInteger(value) && value > 0;
  // Strict contract: unknown fields are not silently excluded from the hash.
  // Read each declared field exactly once, then never consult the caller's
  // possibly stateful/proxied original object again.
  function pickExact(value, fields) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error('not-object');
    const keys = Reflect.ownKeys(value);
    if (keys.length !== fields.length || keys.some(key => !fields.includes(key)))
      throw Error('unexpected-field');
    const copy = {};
    for (const key of fields) copy[key] = value[key];
    return copy;
  }
  try {
    if (typeof expectedDigest !== 'string' || !/^[a-f0-9]{64}$/.test(expectedDigest) ||
        !positive(expectedMissionId) || !positive(expectedWaveCount))
      return deny('missing-external-trust-root');
    const header = pickExact(envelope, ['sourceYear','sourceType','missionId','waves']);
    if (header.sourceYear !== 2022 || header.sourceType !== 'MissionStart' ||
        header.missionId !== expectedMissionId ||
        !Array.isArray(header.waves) || header.waves.length !== expectedWaveCount)
      return deny('capture-mission-mismatch');
    const waves = [];
    for (let i = 0; i < expectedWaveCount; i++) {
      const wave = pickExact(header.waves[i], ['waveIndex','formationId','enemySlots']);
      if (wave.waveIndex !== i || !positive(wave.formationId) ||
          !Array.isArray(wave.enemySlots) || wave.enemySlots.length < 1 ||
          wave.enemySlots.length > 12)
        return deny('invalid-wave-structure');
      const seenSlots = new Set();
      const slots = [];
      for (let j = 0; j < wave.enemySlots.length; j++) {
        const slot = pickExact(wave.enemySlots[j], ['slot','unitId']);
        if (!Number.isSafeInteger(slot.slot) || slot.slot < 0 ||
            !positive(slot.unitId) || seenSlots.has(slot.slot))
          return deny('invalid-enemy-slot');
        seenSlots.add(slot.slot);
        slots.push(Object.freeze({slot:slot.slot,unitId:slot.unitId}));
      }
      waves.push(Object.freeze({
        waveIndex:wave.waveIndex, formationId:wave.formationId,
        enemySlots:Object.freeze(slots)
      }));
    }
    const canonicalCapture = Object.freeze({
      adapterVersion:1, sourceYear:header.sourceYear, sourceType:header.sourceType,
      missionId:header.missionId, waves:Object.freeze(waves)
    });
    const digest = crypto.createHash('sha256')
      .update(JSON.stringify(canonicalCapture),'utf8').digest('hex');
    if (digest !== expectedDigest) return deny('capture-digest-mismatch');
    return Object.freeze({
      accepted:true, missionId:expectedMissionId, waveCount:expectedWaveCount,
      captureDigest:digest, canonicalCapture,
      // Future consumers must read ONLY canonicalCapture, not their envelope.
      productionAuthorized:false
    });
  } catch (_) {
    // Malformed proxies/getters or unexpected data are denied without throws.
    return deny('unreadable-capture');
  }
}
module.exports = {validateCaptureEnvelope};
