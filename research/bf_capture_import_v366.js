/* BF_CAPTURE_IMPORT_V366: source-only candidate adapter; never production spawn authorization. */
'use strict';
const crypto = require('node:crypto');

/**
 * Validate an EXTERNALLY authenticated original MissionStart capture envelope.
 * This is an adapter format for future recovered evidence, NOT an assertion
 * that any real 2022 capture exists. No fallback formation IDs or enemy data.
 * The expected SHA-256 must be independently pinned outside this envelope.
 */
function validateCaptureEnvelope(envelope, expectedDigest, expectedMissionId, expectedWaveCount) {
  const deny = reason => Object.freeze({accepted:false, reason});
  const positive = x => Number.isSafeInteger(x) && x > 0;
  if (!envelope || typeof envelope !== 'object' || Array.isArray(envelope) ||
      !/^[a-f0-9]{64}$/.test(expectedDigest || '') ||
      !positive(expectedMissionId) || !positive(expectedWaveCount))
    return deny('missing-external-trust-root');
  if (envelope.sourceYear !== 2022 || envelope.sourceType !== 'MissionStart' ||
      envelope.missionId !== expectedMissionId ||
      !Array.isArray(envelope.waves) ||
      envelope.waves.length !== expectedWaveCount)
    return deny('capture-mission-mismatch');
  const seen = new Set();
  for (let i = 0; i < envelope.waves.length; i++) {
    const wave = envelope.waves[i];
    if (!wave || typeof wave !== 'object' || Array.isArray(wave) ||
        wave.waveIndex !== i || !positive(wave.formationId) ||
        seen.has(wave.waveIndex) || !Array.isArray(wave.enemySlots) ||
        wave.enemySlots.length === 0 || wave.enemySlots.length > 12)
      return deny('invalid-wave-structure');
    seen.add(wave.waveIndex);
    const slots = new Set();
    for (const slot of wave.enemySlots) {
      if (!slot || typeof slot !== 'object' || Array.isArray(slot) ||
          !Number.isSafeInteger(slot.slot) || slot.slot < 0 ||
          !positive(slot.unitId) || slots.has(slot.slot))
        return deny('invalid-enemy-slot');
      slots.add(slot.slot);
    }
  }
  // Canonical serialization of this explicitly versioned adapter contract.
  // Source authenticity is still the responsibility of the external pin.
  const canonical = JSON.stringify({
    adapterVersion:1, sourceYear:2022, sourceType:'MissionStart',
    missionId:envelope.missionId,
    waves:envelope.waves.map(w=>({
      waveIndex:w.waveIndex,formationId:w.formationId,
      enemySlots:w.enemySlots.map(s=>({slot:s.slot,unitId:s.unitId}))
    }))
  });
  const digest = crypto.createHash('sha256').update(canonical,'utf8').digest('hex');
  if (digest !== expectedDigest) return deny('capture-digest-mismatch');
  return Object.freeze({accepted:true, missionId:expectedMissionId,
    waveCount:expectedWaveCount, captureDigest:digest,
    // No production authorization; a separate trusted integration is required.
    productionAuthorized:false});
}
module.exports = {validateCaptureEnvelope};
