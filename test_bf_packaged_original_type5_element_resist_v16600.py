"""v166 packaged Android APK: original type5 mitigation and v7 save invariants."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 html=z.read('assets/index.html').decode('utf8')
 js=z.read('assets/bf16600_original_type5_element_resist.js').decode('utf8')
 assert html.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
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
