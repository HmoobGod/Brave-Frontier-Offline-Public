"""v71 original source ATK BB skill levels in signed offline Android APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf7100_original_atk_bb_levels.js' in z.namelist()
 js=z.read('assets/bf7100_original_atk_bb_levels.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_ATK_BB_LEVELS_V7100' in js and len(js.encode())<65536
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 html=z.read('assets/index.html').decode('utf8')
 if __import__('hashlib').sha256(html.encode('utf8')).hexdigest()=='bbb6c33bbf0a1813c0b1f5a0222829291741bba820bf7e75385dda9b01efca1c':
  assert html.count('BFGlobalOriginalAtkBBLevelsV7100?.boostFor(p.unitId,p)')==1
 else:
  assert html.count('BFGlobalOriginalAtkBBLevelsV7100?.boostFor(p.unitId)')==1
 if __import__('hashlib').sha256(html.encode('utf8')).hexdigest()=='bbb6c33bbf0a1813c0b1f5a0222829291741bba820bf7e75385dda9b01efca1c':
  assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==1
  assert html.count('function bfR16Outgoing(p,foe,total)')==1
  assert html.count('return api?.scaleDamage(total,element,foe.element)??total;')==1
  assert 'bfR16Outgoing(p,foe,prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst)+(burst?bfR16BurstBonus(p):0)))' in html
 else:
  assert html.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
 assert 'bf_global_offline_demo_v7' in html
g=(R/'app/build.gradle').read_text('utf8')
versions=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(versions)==1
version=versions[0].split("'")[1]
assert version.endswith('.00.0-demo') and int(version.split('.')[0])>=71
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v71 source ATK BB levels, signed offline APK, v7 saved progress identity')
