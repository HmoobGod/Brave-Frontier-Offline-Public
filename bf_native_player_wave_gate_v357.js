/* BF_NATIVE_PLAYER_WAVE_GATE_V357: source-only, no runtime hook or spawn authorization. */
'use strict';
/**
 * Pure transition preflight for a future player-owned native multi-wave adapter.
 * Evidence must be authenticated externally against original formation records.
 * This module does not implement battles, choose enemies, grant rewards, or save.
 */
function planPlayerWaveTransition(state, evidence) {
  const deny = reason => Object.freeze({allowed:false,reason});
  if (!state || !evidence || typeof state !== 'object' || typeof evidence !== 'object')
    return deny('missing-evidence');
  // Only a contiguous unconsumed request can authorize a next-wave plan.\n  // Caller must authenticate formation evidence independently.\n  const integer = n => Number.isSafeInteger(n) && n >= 0;
  if (!integer(state.missionId) || state.missionId === 0 ||
      !integer(state.waveIndex) || !integer(state.totalWaves) || state.totalWaves < 1 ||
      !integer(state.requestEpoch) || state.requestEpoch === 0 ||
      !integer(state.consumedEpoch) || state.consumedEpoch !== state.requestEpoch - 1)
    return deny('invalid-state');
  if (state.actor !== 'player' || state.owner !== 'player0' ||
      state.mode !== 'archive' || state.terminal === true ||
      state.cancelled === true || state.battleWon !== true)
    return deny('not-player-wave-victory');
  if (state.waveIndex >= state.totalWaves - 1)
    return deny('terminal-wave');
  if (state.requestEpoch === state.consumedEpoch)
    return deny('already-consumed');
  if (evidence.verified !== true || evidence.sourceYear !== 2022 ||
      evidence.missionId !== state.missionId ||
      evidence.waveIndex !== state.waveIndex + 1 ||
      evidence.totalWaves !== state.totalWaves ||
      !integer(evidence.formationId) || evidence.formationId === 0 ||
      typeof evidence.sourceDigest !== 'string' ||
      !/^[a-f0-9]{64}$/.test(evidence.sourceDigest))
    return deny('unverified-next-formation');
  return Object.freeze({
    allowed:true, reason:'verified-player-next-wave',
    missionId:state.missionId, nextWaveIndex:state.waveIndex + 1,
    formationId:evidence.formationId, requestEpoch:state.requestEpoch,
    sourceDigest:evidence.sourceDigest
  });
}
if (typeof module !== 'undefined') module.exports = {planPlayerWaveTransition};
