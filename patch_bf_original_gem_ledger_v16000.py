"""v160: append authentic 2022 first-clear Gem history to existing v7 save.

This patch NEVER awards currency, never writes a Gem sidecar, and preserves
all existing player progress. Inject after other bundled HTML patches.
"""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent
html=Path(os.environ.get('BF160_HTML',str(ROOT/'app/src/main/assets/index.html')))
s=html.read_text('utf8')
TAG='BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER'
if TAG in s:
    print('v160 original Gem ledger already patched')
    raise SystemExit(0)
old_default='questClears:{},lastMission:1});'
new_default='questClears:{},lastMission:1,_bfGemV160:{schema:1,balance:0,paidFinales:[],legacyFinales:[]}});'
assert s.count(old_default)==1,'v160 unexpected original default save schema'
old_return=' return out;\n}\nlet P=defaultProgress(),saveEnabled=true;'
assert s.count(old_return)==1,'v160 unexpected parseProgress return boundary'
source='''// BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER
// Original owner-2022 dungeon finales, independently corroborated as
// one-Gem FIRST-clear rewards by pinned historical Global mission data.
// v160 ONLY migrates metadata; does not credit, spend or display Gems.
const BF160_ORIGINAL_GEM_FINAL_IDS=Object.freeze([12,23,33,43,53,63,73,85,
 204,214,224,234,244,254,265,304,314,324,334,344,354,365]);
function bf160MigratedGemState(source,clears){
 const ids=BF160_ORIGINAL_GEM_FINAL_IDS;
 const complete=ids.filter(id=>(clears[id]||0)>0);
 if(source===undefined)return {schema:1,balance:0,paidFinales:[],legacyFinales:complete};
 if(!source||typeof source!=='object'||Array.isArray(source)||
    Object.keys(source).sort().join(',')!=='balance,legacyFinales,paidFinales,schema'||
    source.schema!==1||source.balance!==0||
    !Array.isArray(source.paidFinales)||source.paidFinales.length!==0||
    !Array.isArray(source.legacyFinales))throw new Error('Invalid pending original Gem ledger');
 const found=source.legacyFinales;
 if(found.length>22||found.some((id,i)=>
      !Number.isSafeInteger(id)||!ids.includes(id)||
      (i>0&&id<=found[i-1])||!complete.includes(id)))
   throw new Error('Invalid original Gem legacy finale records');
 // No original Gem awards are inferred from a pre-v160 save, nor from
 // additional quests cleared while v160 is installed; preserve evidence.
 return {schema:1,balance:0,paidFinales:[],legacyFinales:complete};
}
'''
s=s.replace(old_default,new_default,1)
assert s.count('const defaultProgress=()=>(')==1
s=s.replace('const defaultProgress=()=>(',source+'const defaultProgress=()=>(',1)
s=s.replace(old_return,' out._bfGemV160=bf160MigratedGemState(data._bfGemV160,out.questClears);\n'+old_return,1)
save_old=' try{localStorage.setItem(SAVE_KEY,JSON.stringify(P));saveEnabled=true;return true;}'
assert s.count(save_old)==1,'v160 unexpected canonical saveProgress path'
s=s.replace(save_old,''' try{\n  // The cleared-quest evidence uses the SAME atomic v7 JSON save write.\n  // This does NOT grant Gems or create a second storage key.\n  P._bfGemV160=bf160MigratedGemState(P._bfGemV160,P.questClears);\n  localStorage.setItem(SAVE_KEY,JSON.stringify(P));saveEnabled=true;return true;}''',1)
assert s.count(TAG)==1 and s.count('bf160MigratedGemState(')==3
html.write_text(s,'utf8')
print('PASS patch v160: original Gem finale ledger, zero awards, canonical v7 save')
