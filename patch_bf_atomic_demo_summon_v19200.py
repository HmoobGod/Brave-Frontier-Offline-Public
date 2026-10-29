"""v192: make existing demo-token summon all-or-nothing in the canonical v7 save.

This does NOT add Gem spending or claim original 2022 summon rules. It keeps
the existing equal-likelihood demo recruit pool and one-token price exactly.
"""
from pathlib import Path

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets/index.html"
s=A.read_text("utf8")
tag="BF192_ATOMIC_DEMO_SUMMON"
if tag in s:
    assert s.count(tag)==1 and "P=before" in s and "if(!saveProgress())" in s
    print("PASS v192 existing atomic demo summon is unchanged")
    raise SystemExit(0)
old=""" E.summonbutton.disabled=S?.busy||P.summonTokens<1||remaining.length===0;"""
new=""" E.summonbutton.disabled=S?.busy||saveRecoveryPending||P.summonTokens<1||remaining.length===0;"""
assert s.count(old)==1
s=s.replace(old,new,1)
old="""E.summonbutton.onclick=()=>{
 if(S?.busy)return;
 const choices=RECRUIT_IDS.filter(id=>!P.roster.includes(id));
 if(P.summonTokens<1||!choices.length)return;
 // Offline demo only: equal likelihood among currently unowned units; NOT Brave Frontier's actual summon rates.
 const index=Math.floor(Math.random()*choices.length);const id=choices[index];
 P.summonTokens--;P.roster.push(id);P.summonHistory.push(id);
 E.summonresult.textContent=\`Recruited \${UNIT_BY_ID.get(id).name} (\${UNIT_BY_ID.get(id).element})! Unlocked for Squad Setup.\`;
 saveProgress();renderProgress();
};"""
new="""E.summonbutton.onclick=()=>{
 // BF192_ATOMIC_DEMO_SUMMON: existing demo token, NOT an original 2022 or Gem summon.
 if(S?.busy||saveRecoveryPending||P?.version!==7)return;
 const choices=RECRUIT_IDS.filter(id=>!P.roster.includes(id));
 if(P.summonTokens<1||!choices.length)return;
 // Original demo behavior: equally likely among unowned recruits; no new RNG rates.
 const index=Math.floor(Math.random()*choices.length);
 const id=choices[index];
 if(!UNIT_BY_ID.has(id))return;
 // A storage/quota failure must never spend a token or leave a phantom recruit.
 // saveProgress may normalize optional v7 wallets; roll back the entire state.
 const before=JSON.parse(JSON.stringify(P));
 P.summonTokens--;
 P.roster.push(id);
 P.summonHistory.push(id);
 if(P.summonHistory.length>100)P.summonHistory=P.summonHistory.slice(-100);
 if(!saveProgress()){
   P=before;
   E.summonresult.textContent='Summon not saved. No token was spent and no unit was added.';
   renderProgress();
   return;
 }
 E.summonresult.textContent=\`Recruited \${UNIT_BY_ID.get(id).name} (\${UNIT_BY_ID.get(id).element})! Unlocked for Squad Setup.\`;
 renderProgress();
};"""
assert s.count(old)==1,"Summon action changed; do not patch an unknown handler"
assert "bf_global_offline_demo_v7" in s and "BF_GLOBAL_GEMS_PERSONAL_V17000" in s
assert s.count("BF192_ATOMIC_DEMO_SUMMON")==0
s=s.replace(old,new,1)
assert s.count("BF192_ATOMIC_DEMO_SUMMON")==1
A.write_text(s,"utf8")
print("PASS v192: token summon save is atomic, roster and token rollback on write failure, canonical v7 unchanged")
