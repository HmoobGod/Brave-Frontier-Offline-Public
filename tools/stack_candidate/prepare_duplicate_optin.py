#!/usr/bin/env python3
"""Exact A17 prepared HTML transform; no save schema or acquisition changes."""
from pathlib import Path
from hashlib import sha256
import sys
BASE='bb45645fc06e370f02f10e819401422ac7079eba97f6618904cbb066bff74bd5'
def transform(raw):
 if sha256(raw).hexdigest()!=BASE:raise ValueError('Expected exact A17 prepared index')
 s=raw.decode('utf8')
 def one(a,b):
  nonlocal s
  if s.count(a)!=1:raise ValueError('Ambiguous anchor: '+a[:100])
  s=s.replace(a,b,1)
 one('let copySaveEpoch=0;', '''let copySaveEpoch=0;
// BF_COPY_PLAYER_OPTIN_R1: session-only consent. No save field or sidecar.
let copyPlayerSummonEnabled=false;
function copyPlayerSummonIdle(){
 try{return !S?.busy&&!(S?.auto&&!S.over)&&window.BFGlobalQoLQuestRepeatV9800?.statusSnapshot?.()?.active!==true;}catch(_){return false;}
}
function copyPlayerSummonAvailable(){
 return copyPlayerSummonEnabled&&saveEnabled&&!saveRecoveryPending&&P?.version===7&&copyPlayerSummonIdle()&&Number.isSafeInteger(P.summonTokens)&&P.summonTokens>0&&P.summonHistory.length<100;
}
function copySummonControlEnabled(){return copyPlayerSummonEnabled||window.BF_STACK_DISPOSABLE_UI===true;}
''')
 # Keep existing disposable fixture route; normal control does not need it.
 one(' if(window.BF_STACK_DISPOSABLE_UI===true){\n  let duplicateButton=', ''' // Explicit player-facing opt-in; normal token and Gem summons are unchanged.
 let copyOptIn=document.getElementById('bf-copy-summon-optin');
 if(!copyOptIn){
  const label=document.createElement('label');label.id='bf-copy-summon-optin-label';label.style.cssText='display:block;min-height:44px;padding:8px 0';
  copyOptIn=document.createElement('input');copyOptIn.type='checkbox';copyOptIn.id='bf-copy-summon-optin';
  label.append(copyOptIn,document.createTextNode(' Allow duplicate token summons (this session)'));
  const hint=document.createElement('small');hint.style.display='block';hint.textContent='Optional offline demo: 1 token per random recruit, including owned forms. Existing copies stay owned when disabled. Limit: 100 summon history entries.';label.append(hint);
  E.summonbutton.insertAdjacentElement('afterend',label);
  copyOptIn.addEventListener('change',()=>{
   copyPlayerSummonEnabled=copyOptIn.checked===true&&saveEnabled&&!saveRecoveryPending&&copyPlayerSummonIdle();
   renderSummonPanel();
  });
 }
 copyOptIn.checked=copyPlayerSummonEnabled;
 copyOptIn.disabled=!saveEnabled||saveRecoveryPending||!copyPlayerSummonIdle();
 if(copySummonControlEnabled()){
  let duplicateButton=''')
 one("if(window.BF_STACK_DISPOSABLE_UI!==true||!confirm('Experimental custom demo summon: spend 1 token for a random recruit, duplicates possible?'))return;", "if(!(copyPlayerSummonAvailable()||window.BF_STACK_DISPOSABLE_UI===true)||!confirm('Optional custom demo summon: spend 1 token for a random recruit, duplicates possible?'))return;\n   if(!(copyPlayerSummonAvailable()||window.BF_STACK_DISPOSABLE_UI===true))return;")
 one("  duplicateButton.textContent='EXPERIMENTAL · Summon with duplicates (1 demo token)';duplicateButton.disabled=!!S?.busy||saveRecoveryPending||S?.auto&&!S.over||P.summonTokens<1||P.summonHistory.length>=100;\n }", "  duplicateButton.textContent='CUSTOM · Summon with duplicates (1 demo token)';duplicateButton.disabled=window.BF_STACK_DISPOSABLE_UI===true?!!S?.busy||saveRecoveryPending||S?.auto&&!S.over||P.summonTokens<1||P.summonHistory.length>=100:!copyPlayerSummonAvailable();\n }else document.getElementById('bf-copy-token-summon')?.remove();")
 one('copySaveEpoch++;return true;', 'copySaveEpoch++;copyPlayerSummonEnabled=false;return true;')
 one('P=incoming;saveRecoveryPending=false;', 'P=incoming;copyPlayerSummonEnabled=false;saveRecoveryPending=false;')
 one('P=defaultProgress();saveProgress();reset();renderProgress();msg(\'Created a new demo save.\');', "P=defaultProgress();copyPlayerSummonEnabled=false;saveProgress();reset();renderProgress();msg('Created a new demo save.');")
 return s.encode('utf8')
if __name__=='__main__':
 a,b=map(Path,sys.argv[1:]);out=transform(a.read_bytes());b.write_bytes(out);print(sha256(out).hexdigest())
