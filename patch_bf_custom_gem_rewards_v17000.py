"""v170: opt-in personal offline Gem economy in the SAME canonical v7 save.

Runs only after v160/v161 original first-clear evidence patch. Original
2022 Gem reward reference stays unchanged and no sidecar account is created.
"""
from pathlib import Path
import os
R=Path(__file__).resolve().parent
html=Path(os.getenv('BF170_HTML',str(R/'app/src/main/assets/index.html')))
s=html.read_text('utf8')
tag='BF_GLOBAL_GEMS_PERSONAL_V17000'
if tag in s:
 print('v170 personal Gem patch already applied');raise SystemExit(0)
assert s.count('BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER')==1
assert s.count('BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING')==1
intro='const defaultProgress=()=>('
assert s.count(intro)==1
helpers=r"""// BF_GLOBAL_GEMS_PERSONAL_V17000
// Personal offline QoL only: original archived source rewards remain separate.
const BF170_QUEST_IDS=Object.freeze([1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,50,51,52,53,60,61,62,63,70,71,72,73,80,81,82,83,84,85,
 200,201,202,203,204,210,211,212,213,214,220,221,222,223,224,230,231,232,233,234,240,241,242,243,244,250,251,252,253,254,260,261,262,263,264,265,
 300,301,302,303,304,310,311,312,313,314,320,321,322,323,324,330,331,332,333,334,340,341,342,343,344,350,351,352,353,354,360,361,362,363,364,365]);
const BF170_FIRST_WELCOME=1000, BF170_DAILY=100,
 BF170_REGULAR_FIRST=25, BF170_FINALE_FIRST=100,
 BF170_REPLAY=1, BF170_MAX_GEMS=9999999;
const BF170_QUEST_SET=new Set(BF170_QUEST_IDS);
function bf170OldClears(clears) {
 return BF170_QUEST_IDS.filter(id=>(clears[id]||0)>0);
}
function bf170NewWallet(clears) {
 return {schema:1,mode:'original',balance:0,welcomeClaimed:false,
  lastDailyDate:null,dailyClaims:0,firstPaid:[],
  legacyClears:bf170OldClears(clears),replaysPaid:0};
}
function bf170ValidLocalDate(value){
 if(typeof value!=='string'||!/^20[2-9]\d-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/.test(value))return false;
 const [year,month,day]=value.split('-').map(Number),date=new Date(year,month-1,day);
 return date.getFullYear()===year&&date.getMonth()+1===month&&date.getDate()===day;
}
function bf170ValidateWallet(source,clears) {
 if(source===undefined)return bf170NewWallet(clears);
 if(!source||typeof source!=='object'||Array.isArray(source)||
   Object.keys(source).sort().join(',')!==
   'balance,dailyClaims,firstPaid,lastDailyDate,legacyClears,mode,replaysPaid,schema,welcomeClaimed'||
   source.schema!==1||!['original','custom'].includes(source.mode)||
   typeof source.welcomeClaimed!=='boolean'||
   !Number.isSafeInteger(source.balance)||source.balance<0||source.balance>BF170_MAX_GEMS||
   !Number.isSafeInteger(source.dailyClaims)||source.dailyClaims<0||source.dailyClaims>36500||
   !Number.isSafeInteger(source.replaysPaid)||source.replaysPaid<0||source.replaysPaid>1000000||
   !Array.isArray(source.firstPaid)||!Array.isArray(source.legacyClears))
  throw new Error('Invalid custom offline Gem wallet');
 if(source.dailyClaims===0&&source.lastDailyDate!==null||
    source.dailyClaims>0&&!(bf170ValidLocalDate(source.lastDailyDate)))
  throw new Error('Invalid personal Gem daily date');
 const completed=bf170OldClears(clears),check=(list)=>{
  if(list.length>106)return false;
  return list.every((id,i)=>Number.isSafeInteger(id)&&BF170_QUEST_SET.has(id)&&
   completed.includes(id)&&(i===0||id>list[i-1]));
 };
 if(!check(source.firstPaid)||!check(source.legacyClears)||
    source.firstPaid.some(id=>source.legacyClears.includes(id)))
  throw new Error('Invalid personal Gem first-clear claims');
 const total=(source.welcomeClaimed?BF170_FIRST_WELCOME:0)+
   source.dailyClaims*BF170_DAILY+
   source.replaysPaid*BF170_REPLAY+
   source.firstPaid.reduce((n,id)=>n+
     (BF160_ORIGINAL_GEM_FINAL_IDS.includes(id)?BF170_FINALE_FIRST:BF170_REGULAR_FIRST),0);
 if(total!==source.balance||total>BF170_MAX_GEMS)
  throw new Error('Custom Gem wallet balance mismatch');
 // Any quests already completed without a custom first-clear claim are legacy.
 const legacy=completed.filter(id=>!source.firstPaid.includes(id));
 return {schema:1,mode:source.mode,balance:source.balance,
   welcomeClaimed:source.welcomeClaimed,lastDailyDate:source.lastDailyDate,
   dailyClaims:source.dailyClaims,firstPaid:[...source.firstPaid],
   legacyClears:legacy,replaysPaid:source.replaysPaid};
}
function bf170ApplyQuestReward(previousCount,missionId){
 if(!P||P.version!==7||P._bfGemV170Custom?.mode!=='custom'||
    !BF170_QUEST_SET.has(missionId)||!Number.isSafeInteger(previousCount)||
    previousCount<0||!Number.isSafeInteger(P.questClears[missionId])||
    P.questClears[missionId]!==previousCount+1)return false;
 const wallet=P._bfGemV170Custom;
 const amount=previousCount>0?BF170_REPLAY:
   BF160_ORIGINAL_GEM_FINAL_IDS.includes(missionId)?BF170_FINALE_FIRST:BF170_REGULAR_FIRST;
 if(previousCount===0&&(wallet.firstPaid.includes(missionId)||
   wallet.legacyClears.includes(missionId))||
   wallet.balance>BF170_MAX_GEMS-amount||
   previousCount>0&&wallet.replaysPaid>=1000000)return false;
 if(previousCount>0)wallet.replaysPaid++;
 else {wallet.firstPaid.push(missionId);wallet.firstPaid.sort((a,b)=>a-b);}
 wallet.balance+=amount;
 return amount;
}
function bf170LocalDate(){
 const d=new Date();
 if(!Number.isFinite(d.getTime())||d.getFullYear()<2020||d.getFullYear()>2099)return null;
 const p=x=>String(x).padStart(2,'0');
 return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());
}
function bf170CommitUpdate(fn){
 if(!P||P.version!==7||!P._bfGemV170Custom)return false;
 const before=JSON.parse(JSON.stringify(P._bfGemV170Custom));
 if(!fn(P._bfGemV170Custom)){return false;}
 if(saveProgress())return true;
 P._bfGemV170Custom=before;
 return false;
}
const BF170PersonalGemsAPI=Object.freeze({
 snapshot:()=>Object.freeze(P?{...P._bfGemV170Custom,
  firstPaid:Object.freeze([...P._bfGemV170Custom.firstPaid]),
  legacyClears:Object.freeze([...P._bfGemV170Custom.legacyClears])}:{}),
 setMode:(mode)=>['original','custom'].includes(mode)&&
   bf170CommitUpdate(w=>{if(w.mode===mode)return false;w.mode=mode;return true;}),
 claimWelcome:()=>bf170CommitUpdate(w=>{
   if(w.mode!=='custom'||w.welcomeClaimed||w.balance>BF170_MAX_GEMS-BF170_FIRST_WELCOME)return false;
   w.welcomeClaimed=true;w.balance+=BF170_FIRST_WELCOME;return true;
 }),
 claimDaily:()=>bf170CommitUpdate(w=>{
   const today=bf170LocalDate();
   if(w.mode!=='custom'||!today||w.dailyClaims>=36500||
       w.balance>BF170_MAX_GEMS-BF170_DAILY||
       w.lastDailyDate!==null&&today<=w.lastDailyDate)return false;
   w.lastDailyDate=today;w.dailyClaims++;w.balance+=BF170_DAILY;return true;
 }),
 rates:Object.freeze({welcome:1000,daily:100,regularFirst:25,finaleFirst:100,replay:1}),
 localDate:bf170LocalDate
});
window.BFGlobalCustomGemsV17000=BF170PersonalGemsAPI;
"""
# In this production patch, assemble exact IDs from the source-verified live
# 2022 quest list instead of trusting manual typing in the static JS helper.
import json,re
manifest=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
gate=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
assert manifest['total']==106 and gate['currentPlayableFinales']==22
ids=[row[0] for row in manifest['records']]
assert len(ids)==106 and len(set(ids))==106
assert set(row[0] for row in gate['rows'] if row[4]==1).issubset(ids)
qpattern=r'const BF170_QUEST_IDS=Object\.freeze\(\[.*?\]\);'
assert len(re.findall(qpattern,helpers,flags=re.S))==1
helpers=re.sub(qpattern,'const BF170_QUEST_IDS=Object.freeze('+json.dumps(sorted(ids),separators=(',',':'))+');',helpers,count=1,flags=re.S)
s=s.replace(intro,helpers+intro,1)
# Extend the same saved v7 data object and strict existing parser.
a='_bfGemV161Pending:[]});'
b='_bfGemV161Pending:[],_bfGemV170Custom:bf170NewWallet({})});'
assert s.count(a)==1
s=s.replace(a,b,1)
a=' out._bfGemV161Pending=bf161ValidateOriginalPending(data._bfGemV161Pending,out.questClears);\n'
assert s.count(a)==1
s=s.replace(a,a+' out._bfGemV170Custom=bf170ValidateWallet(data._bfGemV170Custom,out.questClears);\n',1)
a='  P._bfGemV161Pending=bf161ValidateOriginalPending(P._bfGemV161Pending,P.questClears);\n'
assert s.count(a)==1
s=s.replace(a,a+'  P._bfGemV170Custom=bf170ValidateWallet(P._bfGemV170Custom,P.questClears);\n',1)
# Existing first-clear marker is preserved; custom per-run reward is added
# to the same canonical quest/squad save without new keys or storage writes.
a='bf161RecordNewFirstClear(previousQuestClearCount);P.summonTokens='
assert s.count(a)==1
s=s.replace(a,'bf161RecordNewFirstClear(previousQuestClearCount);bf170ApplyQuestReward(previousQuestClearCount,QUEST.missionId);P.summonTokens=',1)
assert s.count('BF_GLOBAL_GEMS_PERSONAL_V17000')==1
# A custom-balance panel must refresh only AFTER a successful canonical
# save. In particular, a failed/quota save must not display phantom Gems.
commit='localStorage.setItem(SAVE_KEY,JSON.stringify(P));saveEnabled=true;return true;}'
assert s.count(commit)==1,'v170 unexpected canonical save success path'
s=s.replace(commit,'localStorage.setItem(SAVE_KEY,JSON.stringify(P));saveEnabled=true;'+
 'window.BFGlobalPersonalGemUIV17000?.refresh?.();return true;}',1)
assert s.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
html.write_text(s,'utf8')
print('PASS patch v170: personal Gem wallet, 106 source quests, original 22 finales, one-Gem replay and login claims in canonical v7 save')
