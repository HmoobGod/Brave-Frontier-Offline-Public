"""v173: claim source-corroborated original Global first-clear Gems safely.

This runs after v171 and v170. It changes the existing _bfGemV160 wallet
validator, not the v7 save key, version, or prior clear/migration evidence.
Only previously recorded v161 first clears are claimable; custom-mode paid
first clears and pre-v161 legacy clears are NOT eligible.
"""
import os
from pathlib import Path
R=Path(__file__).resolve().parent
path=Path(os.environ.get('BF173_HTML',str(R/'app/src/main/assets/index.html')))
s=path.read_text('utf8')
tag='BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300'
if tag in s:
    print('v173 original first-clear claim already patched')
    raise SystemExit(0)
assert s.count('BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER')==1
assert s.count('BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING')==1
assert s.count('BF_GLOBAL_GEMS_PERSONAL_V17000')==1
# Continue preserving the original v160 schema and exact source IDs.
old="""    source.schema!==1||source.balance!==0||
    !Array.isArray(source.paidFinales)||source.paidFinales.length!==0||
    !Array.isArray(source.legacyFinales))throw new Error('Invalid pending original Gem ledger');"""
new="""    source.schema!==1||
    !Number.isSafeInteger(source.balance)||source.balance<0||source.balance>22||
    !Array.isArray(source.paidFinales)||source.paidFinales.length!==source.balance||
    !Array.isArray(source.legacyFinales))throw new Error('Invalid pending original Gem ledger');"""
assert s.count(old)==1,'v173 original wallet schema changed unexpectedly'
s=s.replace(old,new,1)
a=""" const found=source.legacyFinales;
 if(found.length>22||found.some((id,i)=>"""
b=""" const found=source.legacyFinales,paid=source.paidFinales;
 if(paid.some((id,i)=>!Number.isSafeInteger(id)||!ids.includes(id)||
     !complete.includes(id)||(i>0&&id<=paid[i-1])))
   throw new Error('Invalid original Gem paid finale IDs');
 if(found.length>22||found.some((id,i)=>"""
assert s.count(a)==1
s=s.replace(a,b,1)
a=""" return {schema:1,balance:0,paidFinales:[],legacyFinales:complete};
}
"""
b=""" return {schema:1,balance:source.balance,paidFinales:[...paid],legacyFinales:complete};
}
"""
assert s.count(a)==1
s=s.replace(a,b,1)
# This is a saved original wallet, not the custom v170 wallet.
# The original validator still rejects all forged balance/count/ID mismatches.
helpers=r"""// BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300
// The 2022 original mission payload 8:0:1:0:0 and historical 2015
// clear_bonus gem:1 corroborate one Gem per FIRST clear for 22 live finales.
// Claim is MANUAL in this offline build, NOT a claim about native 2022 delivery.
// No retroactive v124/legacy payouts; source-only Amdahl cannot qualify.
function bf173ValidateOriginalClaims(state,pending,custom){
 if(!state||!custom||!Array.isArray(state.paidFinales)||
    !Array.isArray(pending)||!Array.isArray(custom.firstPaid))
   throw new Error('Invalid original Gem claim dependencies');
 const safe=bf161ValidateOriginalPending(pending,P?.questClears||{});
 // For parsed saves, the call above may use the previous P. Only the
 // already-parsed list membership matters here; the parser independently
 // validated the list against its own parsed quest-clear counts.
 if(state.paidFinales.some(id=>!pending.includes(id)||
    custom.firstPaid.includes(id)||!state.legacyFinales.includes(id)))
   throw new Error('Original Gem claim has no eligible first-clear evidence');
 return state;
}
function bf173OriginalAvailable(){
 if(typeof P==='undefined'||P?.version!==7||
    !Array.isArray(P._bfGemV161Pending)||
    !Array.isArray(P._bfGemV160?.paidFinales)||
    !Array.isArray(P._bfGemV170Custom?.firstPaid))return [];
 return BF160_ORIGINAL_GEM_FINAL_IDS.filter(id=>
    P._bfGemV161Pending.includes(id)&&
    !P._bfGemV160.paidFinales.includes(id)&&
    !P._bfGemV170Custom.firstPaid.includes(id));
}
function bf173ClaimOriginal(){
 if(typeof P==='undefined'||P?.version!==7||!saveEnabled||
    P._bfGemV170Custom?.mode!=='original')return false;
 const ids=bf173OriginalAvailable();
 if(!ids.length)return false;
 const prior=JSON.parse(JSON.stringify(P._bfGemV160));
 const paid=[...P._bfGemV160.paidFinales,...ids].sort((a,b)=>a-b);
 if(paid.length>22||paid.length!==new Set(paid).size)return false;
 P._bfGemV160={...P._bfGemV160,paidFinales:paid,balance:paid.length};
 if(saveProgress()){bf173Refresh();return ids.length;}
 P._bfGemV160=prior;
 bf173Refresh();
 return false;
}
const BF173Panel=(()=>{
 const host=document.getElementById('squadpicker')||
            document.getElementById('quest')||document.body;
 if(!host)return null;
 const panel=document.createElement('details');
 panel.id='bf17300-original-gems';
 panel.style.cssText='margin:8px 3px;padding:9px;border:1px solid #acc5ab;'+
 'border-radius:8px;background:#23363b;color:#f1f7ec;font:12px/1.5 system-ui';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL GLOBAL FIRST-CLEAR GEMS · VERIFIED FINALES';
 const status=document.createElement('p');
 const button=document.createElement('button');button.type='button';
 button.id='bf17300-claim';button.textContent='CLAIM VERIFIED ORIGINAL GEMS';
 button.style.cssText='min-height:42px;padding:8px';
 const note=document.createElement('p');
 note.textContent='One Gem per source-verified dungeon finale first clear (22 currently '+ 
 'playable). Claim manually in Original mode. Earlier v124 clears are not '+ 
 'back-paid; first clears already paid by Personal Offline custom mode '+ 
 'are excluded. This is offline claim delivery, not a verified native '+ 
 '2022 claiming flow. No native Gem spending/summons yet. Back up '+ 
 'your current v7 save before downgrading.';
 panel.append(heading,status,button,note);
 if(host===document.body)host.append(panel);else host.after(panel);
 button.addEventListener('click',()=>{bf173ClaimOriginal();bf173Refresh();});
 return {panel,status,button};
})();
function bf173Refresh(){
 if(!BF173Panel)return null;
 const available=bf173OriginalAvailable();
 const wallet=P?._bfGemV160;
 BF173Panel.status.textContent='Original earned: '+(wallet?.balance||0)+
  ' Gem(s) · eligible unclaimed: '+available.length+
  ' · existing original first-clear records: '+(P?._bfGemV161Pending?.length||0);
 BF173Panel.button.disabled=!available.length||!saveEnabled||
   P?._bfGemV170Custom?.mode!=='original';
 return {balance:wallet?.balance||0,eligible:[...available],
   paid:[...(wallet?.paidFinales||[])]};
}
window.BFGlobalOriginalGemClaimsV17300=Object.freeze({
 claim:bf173ClaimOriginal,snapshot:bf173Refresh,refresh:bf173Refresh
});
document.getElementById('mode')?.addEventListener('change',bf173Refresh);
document.getElementById('reset')?.addEventListener('click',()=>setTimeout(bf173Refresh,0));
setTimeout(bf173Refresh,0);
"""
# Avoid a cross-save context lookup in the helper. Parse/save already verify
# pending IDs against their own quest-clears using v161 first.
helpers=helpers.replace(""" const safe=bf161ValidateOriginalPending(pending,P?.questClears||{});
 // For parsed saves, the call above may use the previous P. Only the
 // already-parsed list membership matters here; the parser independently
 // validated the list against its own parsed quest-clear counts.
""","")
assert s.count('const defaultProgress=()=>(')==1
s=s.replace('const defaultProgress=()=>(',helpers+'const defaultProgress=()=>(',1)
# Validate claims after both the v161 evidence and the v170 wallet are parsed.
parse=""" out._bfGemV170Custom=bf170ValidateWallet(data._bfGemV170Custom,out.questClears);
"""
assert s.count(parse)==1
s=s.replace(parse,parse+
""" out._bfGemV160=bf173ValidateOriginalClaims(out._bfGemV160,out._bfGemV161Pending,out._bfGemV170Custom);
""",1)
save="""  P._bfGemV170Custom=bf170ValidateWallet(P._bfGemV170Custom,P.questClears);
"""
assert s.count(save)==1
s=s.replace(save,save+
"""  P._bfGemV160=bf173ValidateOriginalClaims(P._bfGemV160,P._bfGemV161Pending,P._bfGemV170Custom);
""",1)
# Refresh only after the successful canonical save, never after failed writes.
success="""localStorage.setItem(SAVE_KEY,JSON.stringify(P));saveEnabled=true;"""
assert s.count(success)==1
s=s.replace(success,success+
 """try{window.BFGlobalOriginalGemClaimsV17300?.refresh?.()}catch(_){}""",1)
assert s.count(tag)==1
assert s.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
path.write_text(s,'utf8')
print('PASS v173: manual original first-clear Gem claims, source-gated and canonical v7')
