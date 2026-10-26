"""v106 integration gate: all optional QoL modules remain isolated from original v7 gameplay.

A static contract intentionally runs before browser tests and Android compilation.
This is a safety test only, not a new original gameplay mechanic.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
JAVA=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
YAML=(ROOT/'.github/workflows/build-debug-apk.yml').read_text('utf8')
GRADLE=(ROOT/'app/build.gradle').read_text('utf8')
MANIFEST=(ROOT/'app/src/main/AndroidManifest.xml').read_text('utf8')

MODULES=[
 ('bf9700_qol_rotating_backups.js','BF_GLOBAL_QOL_ROTATING_BACKUPS_V9700'),
 ('bf9800_qol_cleared_quest_repeat.js','BF_GLOBAL_QOL_CLEARED_QUEST_REPEAT_V9800'),
 ('bf9900_qol_battle_speed.js','BF_GLOBAL_QOL_BATTLE_SPEED_V9900'),
 ('bf10000_qol_squad_presets.js','BF_GLOBAL_QOL_SQUAD_PRESETS_V10000'),
 ('bf10100_qol_viewed_dialogue.js','BF_GLOBAL_QOL_VIEWED_DIALOGUE_SKIP_V10100'),
 ('bf10200_qol_unit_flags.js','BF_GLOBAL_QOL_UNIT_FLAGS_V10200'),
 ('bf10300_qol_battle_details.js','BF_GLOBAL_QOL_BATTLE_DETAILS_V10300'),
 ('bf10400_qol_evolution_needs.js','BF_GLOBAL_QOL_EVOLUTION_NEEDS_V10400'),
 ('bf10500_qol_advanced_smart_auto.js','BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500'),
]
assert len(MODULES)==len(set(name for name,_ in MODULES))==9
prior=JAVA.index('readPackagedText("bf9500_multihit_critical_combat.js")')
for name,marker in MODULES:
 script=(ASSETS/name).read_text('utf8')
 assert script.count(marker)==1,(name,'not unique')
 assert len(script.encode('utf8'))<65536,(name,'Android 64 KiB bound')
 invocation=f'readPackagedText("{name}")'
 assert JAVA.count(invocation)==1,(name,'not loaded exactly once')
 current=JAVA.index(invocation)
 assert current>prior,(name,'load order')
 prior=current
 assert not any(t in script for t in
    ('XMLHttpRequest','sendBeacon(', 'navigator.sendBeacon','fetch(')),name
 assert not re.search(r'localStorage\.(setItem|removeItem)\s*\(\s*["\x27]bf_global_offline_demo_v7',script),name
 assert not re.search(r'\bP\s*\.\s*version\s*=(?!=)',script),name
 assert "test_bf_"+{
   'bf9700_qol_rotating_backups.js':'qol_rotating_backups_v9700',
   'bf9800_qol_cleared_quest_repeat.js':'qol_cleared_quest_repeat_v9800',
   'bf9900_qol_battle_speed.js':'qol_battle_speed_v9900',
   'bf10000_qol_squad_presets.js':'qol_squad_presets_v10000',
   'bf10100_qol_viewed_dialogue.js':'qol_viewed_dialogue_v10100',
   'bf10200_qol_unit_flags.js':'qol_unit_flags_v10200',
   'bf10300_qol_battle_details.js':'qol_battle_details_v10300',
   'bf10400_qol_evolution_needs.js':'qol_evolution_needs_v10400',
   'bf10500_qol_advanced_smart_auto.js':'qol_advanced_smart_auto_v10500',
 }[name]+".py" in YAML,name
# In explicitly read-only QoL, forbid direct changes to the original progress
# object and any direct save API calls; legitimate squad application is excluded.
for name,_ in MODULES:
 if name.startswith(('bf10000_',)):
  continue
 script=(ASSETS/name).read_text('utf8')
 assert 'saveProgress(' not in script,(name,'unexpected save API')
 assert not re.search(r'\bP\.(?:squad|roster|materials|questClears|unitExp|exp|zel|karma)\s*=(?!=)',script),name

squads=(ASSETS/'bf10000_qol_squad_presets.js').read_text('utf8')
assert 'if(!saveProgress())' in squads
assert 'P.squad=previous' in squads
repeat=(ASSETS/'bf9800_qol_cleared_quest_repeat.js').read_text('utf8')
assert 'results.replayBattle()' in repeat
assert 's.clears<=session.lastClear' in repeat
backup=(ASSETS/'bf9700_qol_rotating_backups.js').read_text('utf8')
assert 'const limit=3,maxBytes=512*1024;' in backup
assert 'window.BFAndroid?.exportSaveFile' in backup
locks=(ASSETS/'bf10200_qol_unit_flags.js').read_text('utf8')
assert 'advisoryOnly:true' in locks
assert "applicationId 'org.bravefrontier.offline'" in GRADLE
assert 'bf-development-debug.keystore' in GRADLE
assert 'BF_DEBUG_KEYSTORE_B64' in YAML
assert 'android.permission.INTERNET' not in MANIFEST
assert 'bf_global_offline_demo_v7' in (ASSETS/'index.html').read_text('utf8')
assert re.search(r"versionName '10[5-9]\.00\.0-demo'",GRADLE)
print('PASS v106 all nine QoL source modules: original v7, load order, local only, signing/CI and save invariants')
