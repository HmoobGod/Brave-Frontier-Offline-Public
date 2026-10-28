"""v161: preserve source-authentic post-upgrade first-clear eligibility without Gems.

Run after v160 original Gem legacy ledger patch; only modifies bundled HTML.
P.version stays 7; all data stays in canonical bf_global_offline_demo_v7.
"""
from pathlib import Path
import os
R=Path(__file__).resolve().parent
file=Path(os.getenv('BF161_HTML',str(R/'app/src/main/assets/index.html')))
s=file.read_text('utf8')
tag='BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING'
if tag in s:
 print('v161 first-clear pending already patched');raise SystemExit(0)
assert s.count('BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER')==1
start='const defaultProgress=()=>('
assert s.count(start)==1
helpers='''// BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING
// Local evidence of a newly cleared ORIGINAL dungeon finale after v161 install.
// This marker is neither a Gem award nor an original server claim.
function bf161ValidateOriginalPending(source,clears){
 if(source===undefined)return [];
 if(!Array.isArray(source)||source.length>22)throw new Error('Invalid original Gem pending records');
 let prev=0;
 for(const id of source){
  if(!Number.isSafeInteger(id)||!BF160_ORIGINAL_GEM_FINAL_IDS.includes(id)||
     id<=prev||!Number.isSafeInteger(clears[id])||clears[id]<=0)
   throw new Error('Invalid original Gem first-clear evidence');
  prev=id;
 }
 return [...source];
}
function bf161RecordNewFirstClear(previousCount){
 if(previousCount!==0||!P||P.version!==7)return false;
 const id=QUEST?.missionId;
 if(!BF160_ORIGINAL_GEM_FINAL_IDS.includes(id)||
    P._bfGemV160.legacyFinales.includes(id)||
    P._bfGemV161Pending.includes(id))return false;
 P._bfGemV161Pending.push(id);P._bfGemV161Pending.sort((a,b)=>a-b);
 return true;
}
'''
s=s.replace(start,helpers+start,1)
a='_bfGemV160:{schema:1,balance:0,paidFinales:[],legacyFinales:[]}});'
b='_bfGemV160:{schema:1,balance:0,paidFinales:[],legacyFinales:[]},_bfGemV161Pending:[]});'
assert s.count(a)==1
s=s.replace(a,b,1)
parse=' out._bfGemV160=bf160MigratedGemState(data._bfGemV160,out.questClears);\n'
assert s.count(parse)==1
s=s.replace(parse,parse+' out._bfGemV161Pending=bf161ValidateOriginalPending(data._bfGemV161Pending,out.questClears);\n',1)
save='  P._bfGemV160=bf160MigratedGemState(P._bfGemV160,P.questClears);\n'
assert s.count(save)==1
s=s.replace(save,save+'  P._bfGemV161Pending=bf161ValidateOriginalPending(P._bfGemV161Pending,P.questClears);\n',1)
reward='function awardDemoRewards(){\n const previous=P.level;'
assert s.count(reward)==1
s=s.replace(reward,reward+'\n const previousQuestClearCount=P.questClears[QUEST.missionId]||0;',1)
trigger='P.questClears[QUEST.missionId]=(P.questClears[QUEST.missionId]||0)+1;P.summonTokens='
assert s.count(trigger)==1
s=s.replace(trigger,'P.questClears[QUEST.missionId]=(P.questClears[QUEST.missionId]||0)+1;bf161RecordNewFirstClear(previousQuestClearCount);P.summonTokens=',1)
assert s.count(tag)==1
assert s.count('bf161ValidateOriginalPending(')==3
assert s.count('bf161RecordNewFirstClear(')==2
assert s.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
file.write_text(s,'utf8')
print('PASS v161: pending original Gem first-clear evidence in v7 save; zero Gem grants')
