"""v166 packaged Android APK: original type5 mitigation and v7 save invariants."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 html=z.read('assets/index.html').decode('utf8')
 js=z.read('assets/bf16600_original_type5_element_resist.js').decode('utf8')
 assert html.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
 if __import__('hashlib').sha256(html.encode('utf8')).hexdigest()=='bbb6c33bbf0a1813c0b1f5a0222829291741bba820bf7e75385dda9b01efca1c':
  assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==1
  assert html.count('function bfR16Outgoing(p,foe,total)')==1
  assert html.count('return api?.scaleDamage(total,element,foe.element)??total;')==1
  assert 'bfR16Outgoing(p,foe,prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst)+(burst?bfR16BurstBonus(p):0)))' in html
  assert 'bfR20Incoming(target,Math.round(((incoming)=>window.BFGlobalOriginalElementResistV16600?.scaleIncoming(incoming,enemy.element,target)??incoming)(((total)=>window.BFGlobalElementalCombatV6900?.scaleDamage(total,enemy.element,UNIT_BY_ID.get(target.unitId)?.element)??total)(prototypeDamage(bfR21EnemyAtk(enemy),bfR15Defense(target),bfR16GuardMultiplier(target))))))' in html
 else:
  assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
  assert 'prototypeDamage(enemy.atk,target.def,target.guard ? .5 : 1)' in html
 assert 'BF_GLOBAL_ORIGINAL_TYPE5_ELEMENT_RESIST_V16600' in js
 assert 'reductionPercent:10' in js
 assert 'unknownEnemyElementsUnaffected:true' in js
 assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
 assert 'localStorage.setItem(SAVE_KEY,JSON.stringify(P))' in html
 assert 'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in html
 assert 'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING' in html
print('PASS v166 signed APK: original type5 10% known-element leader protection, original damage formula preserved, canonical v7 save unchanged')

with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/bf_leader_defense_bypass.js')==(R/'app/src/main/assets/bf_leader_defense_bypass.js').read_bytes()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf11400_original_global_leader_english.js")') < java.index('readPackagedText("bf_leader_defense_bypass.js")')
