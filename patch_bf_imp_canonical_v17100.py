"""v171: move opt-in Imp progress to the SAME canonical v7 save transaction.

Run AFTER v160/v161 and v170 build-time HTML patches. Existing v169 separate
sidecars are NEVER silently attached to an imported save: owner explicitly
migrates using the Imp panel, while the original sidecar is retained.
"""
from pathlib import Path
import os
R=Path(__file__).resolve().parent
file=Path(os.getenv('BF171_HTML',str(R/'app/src/main/assets/index.html')))
s=file.read_text('utf8')
TAG='BF_GLOBAL_IMP_CANONICAL_V17100'
if TAG in s:
 print('v171 Imp save adapter already patched');raise SystemExit(0)
assert s.count('BF_GLOBAL_GEMS_PERSONAL_V17000')==1
assert s.count('BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING')==1
anchor='const defaultProgress=()=>('
assert s.count(anchor)==1
helper=r"""// BF_GLOBAL_IMP_CANONICAL_V17100
// An optional v171 Imp field persists atomically with quests, Gems and units.
function bf171ValidateCanonicalImps(raw){
 if(raw===undefined||raw===null)return null;
 if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.version!==1||
    raw.started!==true||!['custom','original'].includes(raw.mode)||
    !raw.amounts||typeof raw.amounts!=='object'||Array.isArray(raw.amounts)||
    !raw.inventory||typeof raw.inventory!=='object'||Array.isArray(raw.inventory)||
    !raw.cursors||typeof raw.cursors!=='object'||Array.isArray(raw.cursors))
   throw new Error('Invalid saved Imp enhancement state');
 if(Object.keys(raw.amounts).length>5000||
    Object.keys(raw.cursors).length>3000)return bf171RejectImps();
 const amounts={},inventory={},cursors={};
 for(const [k,v] of Object.entries(raw.amounts)){
   if(!/^[1-9]\d{0,9}$/.test(k)||!Array.isArray(v)||v.length!==4||
      v.some(n=>!Number.isSafeInteger(n)||n<0||n>65535))
     return bf171RejectImps();
   amounts[k]=v.slice();
 }
 for(const key of ['molin','pakpak','ganju','fwahl','arton']){
   const n=raw.inventory[key];
   if(!Number.isSafeInteger(n)||n<0||n>10000)return bf171RejectImps();
   inventory[key]=n;
 }
 for(const [k,n] of Object.entries(raw.cursors)){
   if(!/^[1-9]\d{0,7}$/.test(k)||!Number.isSafeInteger(n)||
      n<0||n>10000000)return bf171RejectImps();
   cursors[k]=n;
 }
 return {version:1,started:true,mode:raw.mode,amounts,inventory,cursors};
}
function bf171RejectImps(){throw new Error('Invalid saved Imp enhancement data');}
"""
s=s.replace(anchor,helper+anchor,1)
default='_bfGemV170Custom:bf170NewWallet({})'
assert s.count(default)==1
s=s.replace(default,default+',_bfImpsV171:null',1)
old=' out._bfGemV170Custom=bf170ValidateWallet(data._bfGemV170Custom,out.questClears);\n'
assert s.count(old)==1
s=s.replace(old,old+' out._bfImpsV171=bf171ValidateCanonicalImps(data._bfImpsV171);\n',1)
old='  P._bfGemV170Custom=bf170ValidateWallet(P._bfGemV170Custom,P.questClears);\n'
assert s.count(old)==1
s=s.replace(old,old+'  P._bfImpsV171=bf171ValidateCanonicalImps(P._bfImpsV171);\n',1)
assert s.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))")==1
file.write_text(s,'utf8')
print('PASS v171: Imp and Gem state now share one canonical v7 transaction; legacy sidecar requires explicit migration')
