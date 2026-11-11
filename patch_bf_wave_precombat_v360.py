"""v360: abort corrupted 2022 source evidence before the first player action.

This extends v359's post-round live engine guard. It does not supply or
authenticate missing original enemy formations, alter save data, or touch
the original enemy/NPC AI. The legacy absent-source simulated DEMO remains.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent / "app/src/main/assets/index.html"
ORIGINAL_EXEC = "async function execute(){if(S.busy||S.over||liveParty().some(p=>!p.action))return;roundSpeed=Number(E.speed.value)||2;"
GUARDED_EXEC = """async function execute(){if(S.busy||S.over||liveParty().some(p=>!p.action))return;
 // v360: Never spend a player action, BB gauge or HP on a present corrupt
 // 2022 source. v359 separately rechecks after player attacks and before
 // simulated wave advancement or final-clear rewards.
 if(!sourceWaveCountReady()){
  S.auto=false;E.auto.checked=false;
  if(timer){clearTimeout(timer);timer=null;}
  roundSpeed=null;S.busy=false;
  for(const p of S.party)p.action=null;
  E.phase.textContent='Wave source mismatch · paused';
  msg('2022 source mission or wave evidence unavailable. Combat paused before actions; reset after restoring the verified source.');
  update();return;
 }
 roundSpeed=Number(E.speed.value)||2;"""

def apply():
    current = HTML.read_text(encoding="utf-8")
    # Both guards must be present in any completed or partially prepared
    # artifact. Never silently re-enable combat without v359's clear gate.
    if current.count("function sourceWaveCountReady()") != 1:
        raise SystemExit("v360: missing v359 source validator; refusing patch")
    if current.count("if(!sourceWaveCountReady()){") == 2 and current.count(GUARDED_EXEC) == 1:
        print("v360: native precombat source guard already present; unchanged")
        return
    if current.count("if(!sourceWaveCountReady()){") != 1 or current.count(ORIGINAL_EXEC) != 1:
        raise SystemExit("v360: unexpected live execute anchors; refusing patch")
    updated = current.replace(ORIGINAL_EXEC, GUARDED_EXEC, 1)
    if updated.count(GUARDED_EXEC) != 1 or updated.count("if(!sourceWaveCountReady()){") != 2:
        raise SystemExit("v360: output failed validation; original unchanged")
    HTML.write_text(updated, encoding="utf-8")
    print("v360: live source precombat fail-closed guard applied")

if __name__ == "__main__":
    apply()
