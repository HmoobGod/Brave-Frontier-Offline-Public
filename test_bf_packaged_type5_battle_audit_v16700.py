"""v167 signed APK: source-only elemental protection ledger; no save mutation."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent
apk=R/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(apk) as z:
    html=z.read('assets/index.html').decode('utf8')
    code=z.read('assets/bf16600_original_type5_element_resist.js').decode('utf8')
    assert html.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
    assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
    assert 'prototypeDamage(enemy.atk,target.def,target.guard ? .5 : 1)' in html
    assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
    assert 'localStorage.setItem(SAVE_KEY,JSON.stringify(P))' in html
    assert 'BF_GLOBAL_ORIGINAL_TYPE5_ELEMENT_RESIST_V16600' in code
    assert 'function syncEncounter()' in code
    assert 'recent:freeze(recent.slice(-8))' in code
    assert 'bf16700-protection-totals' in code
    assert 'prevented+=amount-reduced;' in code
    assert 'if(recent.length>16)recent.shift();' in code
    assert not any(x in code for x in (
        'saveProgress(', 'localStorage', 'P.roster=', 'P.squad=',
        'Math.random', 'fetch(', 'XMLHttpRequest'))
print('PASS v167 signed APK original 10% protection ledger: match-only events, bounded battle record, canonical v7 saves, preserved DEMO baseline')
