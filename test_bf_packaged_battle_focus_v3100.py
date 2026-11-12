"""v31.00 Android APK includes safe tactical focus and preserves existing offline state."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 for name in ('bf3100_battle_focus.js','bf3000_battle_results.js',
              'bf2100_battle_command_tray.js','bf2900_original_event_expressions.js'):
  assert 'assets/'+name in files,name
 src=z.read('assets/bf3100_battle_focus.js').decode('utf8')
 assert src.count('/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */')==1
 assert len(src.encode('utf8'))<65536
 assert 'if(living.some(e=>!Number.isFinite(e[key])))return null' in src
 assert 'const eligible=new Map(strategies.map' in src
 # One-turn eligibility depends on BOTH native queued player actions
 # and foreground visibility; the previous signature was too narrow.
 assert 'const occupied=Array.isArray(S.party)?S.party.map(p=>p?.action!=null):null;' in src
 assert 'JSON.stringify([s,[...eligible],occupied,document.hidden])' in src
 assert "if(b.id==='bf3100-run-turn'){" in src
 assert "S.party.some(p=>p?.action!=null);" in src
 assert "oneTurn.id='bf3100-run-turn';" in src
 assert 'oneTurn.addEventListener(\'click\',()=>runFocusedTurn());' in src
 assert 'strategy?!eligible.get(strategy):!s.target' in src
 # The rebuilt APK, not just a checked-in source tree, must contain the
 # opt-in manual action that really queues a target through native controls.
 # Two opt-in 50%-HP player-only finishing tactics must use real native
 # targeting and queue controls, never imagined 2022 enemy formations.
 assert "['wounded-threat','FINISH WOUNDED THREAT']" in src
 assert "['wounded-armor','FINISH WOUNDED LOW DEF']" in src
 assert "const wounded=living.filter(e=>e.hp/e.maxHp<=0.5);" in src
 assert "if(S.mode!=='archive'||living.some(e=>e.hp>e.maxHp))return null;" in src
 assert "if(!wounded.length)return null;" in src
 assert "b.atk-a.atk||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot:" in src
 assert "a.def-b.def||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot);" in src
 assert "['element-safe','FEWEST RESISTS']" in src
 assert "if(kind==='element-safe'){" in src
 assert 'if(types.some(type=>!type))return null;' in src
 assert 'if(!targetType)return null;' in src
 assert "else if(factor!==1)throw Error('unverified-element-matchup');" in src
 assert 'ranked.sort((a,b)=>a.resisted-b.resisted||' in src
 assert "a.foe.hp-b.foe.hp||a.foe.slot-b.foe.slot);" in src
 assert "return f?Object.freeze({slot:f.slot,name:f.name,hp:f.hp," in src
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf3000_battle_results.js")')<j.index('readPackagedText("bf3100_battle_focus.js")')
print('PASS v31.00 targeting through existing demo combat controls with intact offline identity')
