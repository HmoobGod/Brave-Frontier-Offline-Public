"""v198: strictly opt-in PERSONAL OFFLINE Gem summons; preserve original mode.

Patch only the CI-prepared HTML after v170/v171/v173/v192. Keep canonical v7
storage and all original 2022 Gem claim records independent. This is not a
native 2022 price or summon probability model.
"""
from pathlib import Path

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets/index.html"
s = A.read_text("utf8")
tag = "BF198_PERSONAL_GEM_SUMMON_V19800"
if tag in s:
    assert s.count(tag) == 1
    print("PASS v198 previously prepared")
    raise SystemExit(0)
assert s.count("BF_GLOBAL_GEMS_PERSONAL_V17000") == 1
assert s.count("BF192_ATOMIC_DEMO_SUMMON") == 1
assert s.count("BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300") == 1
assert s.count("bf_global_offline_demo_v7") >= 1

helpers = r"""
// BF198_PERSONAL_GEM_SUMMON_V19800
// Owner-selected PERSONAL OFFLINE economics: 100 Gem per UNIQUE demo recruit.
// This is not original Global's banner price, probabilities, or Gem ledger.
const BF198_PERSONAL_SUMMON_COST = 100;
function bf198ValidateWallet(source, clears, roster) {
 if(!source || source.schema!==2)return bf170ValidateWallet(source,clears);
 const keys=Object.keys(source).sort().join(',');
 if(keys!=='balance,dailyClaims,firstPaid,lastDailyDate,legacyClears,mode,receipts,replaysPaid,schema,spent,welcomeClaimed'||
    !Number.isSafeInteger(source.spent)||source.spent<0||
    !Number.isSafeInteger(source.balance)||source.balance<0||
    !Array.isArray(source.receipts)||source.receipts.length>RECRUIT_IDS.length||
    !Array.isArray(roster))
   throw new Error('Invalid personal Gem purchase ledger');
 const ids=new Set();
 for(const receipt of source.receipts){
   if(!receipt||typeof receipt!=='object'||Array.isArray(receipt)||
      Object.keys(receipt).sort().join(',')!=='cost,unitId'||
      receipt.cost!==BF198_PERSONAL_SUMMON_COST||
      !Number.isSafeInteger(receipt.unitId)||
      !RECRUIT_IDS.includes(receipt.unitId)||
      !roster.includes(receipt.unitId)||ids.has(receipt.unitId))
     throw new Error('Invalid personal Gem summon receipt');
   ids.add(receipt.unitId);
 }
 if(source.spent!==BF198_PERSONAL_SUMMON_COST*source.receipts.length||
    source.balance+source.spent>BF170_MAX_GEMS)
   throw new Error('Personal Gem spending mismatch');
 // Validate all original v170 earns/first-clear quarantine with its existing
 // strict schema-1 validator, using total earned BEFORE spending.
 const legacy={...source,schema:1,balance:source.balance+source.spent};
 delete legacy.spent;
 delete legacy.receipts;
 const valid=bf170ValidateWallet(legacy,clears);
 return {...valid,schema:2,balance:source.balance,spent:source.spent,
   receipts:source.receipts.map(r=>({unitId:r.unitId,cost:r.cost}))};
}
function bf198PersonalSummon(){
 if(S?.busy||saveRecoveryPending||P?.version!==7)return false;
 const w=P._bfGemV170Custom;
 if(!w||w.mode!=='custom')return false;
 // Validate before RNG, roster mutation or spending. Invalid wallet fails closed.
 try{bf198ValidateWallet(w,P.questClears,P.roster)}catch(_){return false}
 const choices=RECRUIT_IDS.filter(id=>!P.roster.includes(id));
 if(!choices.length||w.balance<BF198_PERSONAL_SUMMON_COST)return false;
 const random=Math.random();
 if(!Number.isFinite(random)||random<0||random>=1)return false;
 const id=choices[Math.floor(random*choices.length)];
 if(!UNIT_BY_ID.has(id))return false;
 const before=JSON.parse(JSON.stringify(P));
 const receipts=w.schema===2?w.receipts.map(r=>({...r})):[];
 receipts.push({unitId:id,cost:BF198_PERSONAL_SUMMON_COST});
 P._bfGemV170Custom={...w,schema:2,
   balance:w.balance-BF198_PERSONAL_SUMMON_COST,
   spent:(w.schema===2?w.spent:0)+BF198_PERSONAL_SUMMON_COST,
   receipts};
 P.roster.push(id);
 P.summonHistory.push(id);
 if(P.summonHistory.length>100)P.summonHistory=P.summonHistory.slice(-100);
 if(!saveProgress()){
   P=before;
   E.summonresult.textContent='Personal summon not saved. No Gems spent and no unit added.';
   renderProgress();
   return false;
 }
 E.summonresult.textContent='PERSONAL OFFLINE summon: recruited '+
   UNIT_BY_ID.get(id).name+' for 100 personal Gems (not original 2022 rates).';
 renderProgress();
 return true;
}
"""
anchor="function bf170ApplyQuestReward(previousCount,missionId){"
assert s.count(anchor)==1
s=s.replace(anchor,helpers+anchor,1)
old="out._bfGemV170Custom=bf170ValidateWallet(data._bfGemV170Custom,out.questClears);"
assert s.count(old)==1
s=s.replace(old,"out._bfGemV170Custom=bf198ValidateWallet(data._bfGemV170Custom,out.questClears,out.roster);",1)
old="P._bfGemV170Custom=bf170ValidateWallet(P._bfGemV170Custom,P.questClears);"
assert s.count(old)==1
s=s.replace(old,"P._bfGemV170Custom=bf198ValidateWallet(P._bfGemV170Custom,P.questClears,P.roster);",1)
# Existing v170 API claims/mode switches must update the personal summon button.
old=" if(saveProgress())return true;\n P._bfGemV170Custom=before;"
assert s.count(old)==1
s=s.replace(old," if(saveProgress()){renderSummonPanel();return true;}\n P._bfGemV170Custom=before;",1)
old=" E.summonbutton.textContent=remaining.length?'Summon · 1 token':'Collection complete';\n}"
assert s.count(old)==1
new=""" E.summonbutton.textContent=remaining.length?'Summon · 1 token':'Collection complete';
 // Optional custom Gem summon: never modifies original Gem claims or token cost.
 let gemButton=document.getElementById('bf19800-personal-summon');
 if(!gemButton){
   gemButton=document.createElement('button');gemButton.type='button';
   gemButton.id='bf19800-personal-summon';
   gemButton.style.cssText='display:block;min-height:44px;width:100%;margin:9px 0;'+
     'padding:10px;border-radius:8px;font-weight:700';
   gemButton.addEventListener('click',bf198PersonalSummon);
   E.summonbutton.insertAdjacentElement('afterend',gemButton);
 }
 const personal=P._bfGemV170Custom;
 gemButton.textContent='PERSONAL OFFLINE Summon · 100 Gems'+
   (personal?.mode==='custom'?' ('+personal.balance.toLocaleString()+' available)':'');
 gemButton.title='Custom offline economy only. Draws uniformly from unowned DEMO recruits.';
 gemButton.disabled=!!S?.busy||saveRecoveryPending||P.version!==7||
   personal?.mode!=='custom'||personal.balance<BF198_PERSONAL_SUMMON_COST||
   remaining.length===0;
}"""
s=s.replace(old,new,1)
assert s.count(tag)==1
assert s.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))")==1
A.write_text(s,"utf8")
print("PASS v198 prepared personal-only 100-Gem summon with strict v7 schema2 receipts and atomic rollback")
