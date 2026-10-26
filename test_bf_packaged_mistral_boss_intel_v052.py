"""v0.52: verify source-backed boss overlay and no save schema changes inside APK."""
from pathlib import Path
import json
from zipfile import ZipFile
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_mistral_boss_intel_v052.json').read_text('utf8'))
assert m['entries'][-1]['bosses'][0]['hp']==50000
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    html=z.read('assets/index.html').decode('utf8')
    js=z.read('assets/bf052_story_boss.js').decode('utf8')
    assert html.count('/* BF_MISTRAL_BOSS_HOOK_V052 */')==1
    assert html.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==1
    assert js.count('__BOSS_SOURCE_JSON__')==1
    assert '50000' in html and 'Juggernaut' in html and 'bf_global_offline_demo_v7' in html
    assert 'toggle.checked = false' in html
    assert 'window.BF052BossIntel?.encounter' in html
    assert '/* BF_TOWER_OF_MISTRAL_V051 */' in html
    assert '/* BF_MONSTERS_NEST_V050 */' in html
    assert '/* BF_REMAINS_OF_MIRZA_V049 */' in html
print('PASS v0.52 packaged opt-in source-backed Juggernaut and earlier offline content, v7')
