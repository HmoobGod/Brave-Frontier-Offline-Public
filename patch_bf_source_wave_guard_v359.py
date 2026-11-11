"""v359: apply source-qualified live-wave boundary guards to built Android HTML.

The 4.5 MB original bundled index is intentionally not rewritten through
the GitHub API. The same idempotent small patch is applied for CI and Gradle
builds, preserving existing save/reward/AI engine functions otherwise.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent / "app/src/main/assets/index.html"
ORIGINAL_WAVES = "function modeWaves(){return E.mode.value==='archive'?QUEST.battles:2;}\n"
GUARDED_WAVES = """function modeWaves(){return E.mode.value==='archive'?QUEST.battles:2;}
// This authenticates archived mission WAVE COUNTS only. Original 2022 enemy
// formations and native battle AI are NOT reconstructed by this guard.
// v143 is loaded after index on Android. Absent legacy source keeps the
// prior simulated DEMO; a present corrupt source may not advance it.
function sourceWaveCountReady(){
 if(S.mode!=='archive')return true;
 const api=window.BFOriginalGlobalQuestEnergyV14300;
 if(api===undefined)return true;
 try{
  const metadata=api.source;
  if(metadata?.year!==2022||metadata.recordCount!==106||
     metadata.sourceSha256!=='a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66'||
     metadata.staminaEnforced!==false||metadata.saveMutation!==false||
     typeof api.lookup!=='function')return false;
  const row=api.lookup(QUEST?.missionId);
  const expected=[QUEST?.missionId,QUEST?.dungeonId,QUEST?.requires,QUEST?.battles,
    QUEST?.energy,QUEST?.exp,QUEST?.zel,QUEST?.karma];
  if(!Array.isArray(row)||row.length!==8||row.some((v,i)=>
      !Number.isSafeInteger(v)||v<0||v!==expected[i]))return false;
  return row[3]>0&&Number.isSafeInteger(S.totalWaves)&&
    S.totalWaves===row[3]&&Number.isSafeInteger(S.wave)&&
    S.wave>=0&&S.wave<S.totalWaves;
 }catch(_){return false;}
}
"""
ORIGINAL_STEP = "if(!livingEnemies().length){if(S.wave>=S.totalWaves-1){finish(true);return}S.wave++;S.enemies=makeWave(S.wave);"
GUARDED_STEP = """if(!livingEnemies().length){
 // Genuine 2022 source count gate in the live DEMO engine. Never infer enemy
 // identities, loot, native actions or source formations from these counts.
 if(!sourceWaveCountReady()){
  S.auto=false;E.auto.checked=false;S.busy=false;roundSpeed=null;
  for(const p of S.party)p.action=null;
  E.phase.textContent='Wave source mismatch · paused';
  msg('2022 source wave count or mission identity changed. No next wave or clear reward granted. Reset the mission after restoring verified source.');
  update();return;
 }
 if(S.wave>=S.totalWaves-1){finish(true);return}S.wave++;S.enemies=makeWave(S.wave);"""

def apply():
    current = HTML.read_text(encoding="utf-8")
    if current.count(GUARDED_WAVES) == 1 and current.count(GUARDED_STEP) == 1:
        print("v359 guarded native wave source already present; unchanged")
        return
    if current.count(ORIGINAL_WAVES) != 1 or current.count(ORIGINAL_STEP) != 1:
        raise SystemExit("v359: unexpected core HTML anchors; refusing to modify")
    if "function sourceWaveCountReady()" in current:
        raise SystemExit("v359: partial/duplicate guard; refusing to modify")
    updated = current.replace(ORIGINAL_WAVES, GUARDED_WAVES, 1)
    updated = updated.replace(ORIGINAL_STEP, GUARDED_STEP, 1)
    if updated.count("function sourceWaveCountReady()") != 1 or updated.count(GUARDED_STEP) != 1:
        raise SystemExit("v359: patch verification failed; original left unchanged")
    HTML.write_text(updated, encoding="utf-8")
    print("v359: live DEMO wave and final-clear source count guard applied")

if __name__ == "__main__":
    apply()
