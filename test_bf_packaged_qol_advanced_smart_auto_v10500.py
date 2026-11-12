"""v105 APK packages opt-in advanced Smart Auto without altering original save/signing."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10500_qol_advanced_smart_auto.js').decode('utf8')
 assert 'BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500' in data
 assert 'window.BF041SmartAuto=freeze({...smart,kindFor})' in data
 # Source-provider exceptions must return null, never the regular HP% fallback.
 assert 'try{\n   const element=window.BFGlobalElementalCombatV6900;' in data
 assert 'return ranked[0]?.foe||undefined;\n   }catch(_){return null;}' in data
 assert 'return chosen===undefined?baseTarget(enemies):chosen;' in data
 # Packaged player-only Smart Auto target improvements, no synthetic waves.
 assert "['wounded-threat','Finish wounded high-ATK threat (<=50% HP)']" in data
 assert "['wounded-armor','Finish wounded low-DEF foe (<=50% HP)']" in data
 assert "const wounded=live.filter(e=>e.hp/e.maxHp<=0.5);" in data
 assert "if(!wounded.length)return baseTarget(enemies);" in data
 assert "if(enemies.some(e=>e&&(!Number.isFinite(e.hp)||e.hp<0))||" in data
 assert "b.atk-a.atk||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot:" in data
 assert "a.def-b.def||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot);" in data
 # The signed APK must contain the actual player-only resistance-aware
 # targeting branch, not just the Chromium test or a source-only note.
 assert 'const allAlliesTyped=types.length===allies.length;' in data
 assert 'else if(factor===0.5)resisted++;' in data
 assert "if(!allAlliesTyped||ranked.some(row=>!row.known))return undefined;" in data
 assert 'advantages.sort((a,b)=>b.count-a.count||' in data
 assert 'ranked.sort((a,b)=>a.resisted-b.resisted||' in data
 assert data.count('a.foe.hp-b.foe.hp||a.foe.slot-b.foe.slot);')==2
 assert 'Source-listed six-element circle (bf6900)' in data
 # BB/support provider errors preserve the existing player's baseline action.
 assert 'let source;\n   try{' in data
 assert '}catch(_){return previous;}' in data
 # Optional status providers cannot crash an owned player Auto decision.
 # Optional original 2022 heal-all BB can supersede low-HP Guard only
 # when explicitly enabled for a real player-owned caster, with known
 # unblocked Curse/Paralysis, source skill and valid squad state.
 assert "healBeforeGuard:false" in data
 assert "healBeforeGuard:raw?.healBeforeGuard===true" in data
 assert "config.healBeforeGuard&&Number.isSafeInteger(unit.unitId)" in data
 assert "paralysis.paralyzed(unit.id)!==false" in data
 assert "curse.cursed(unit.id)!==false" in data
 assert "bb?.target!=='support'" in data
 assert "originalSupport(unit.unitId)?.kind!=='heal_all'" in data
 assert "S.party[p.id]!==p" in data
 assert "if(living.some(p=>p.hp<p.maxHp&&p.hp/p.maxHp<=config.heal/100))" in data
 assert "'bf10500-heal-before-guard'" in data
 assert "healFirst.addEventListener('change'" in data
 assert 'guardAllowed=active()&&config.guard>0&&' in data
 assert 'if(guardAllowed){' in data
 assert "return 'guard';\n   }\n   // Unknown Curse status" in data
 assert "if(window.BFGlobalCurseBBLockV5900?.cursed(unit.id))return 'attack';" in data
 assert "}catch(_){return 'attack';}" in data
 assert '!Number.isSafeInteger(S.totalWaves)||S.totalWaves<1' in data
 assert 'S.totalWaves!==row.verifiedWaveCount' in data
 assert 'assets/bf10400_qol_evolution_needs.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10400_qol_evolution_needs.js")')<java.index('readPackagedText("bf10500_qol_advanced_smart_auto.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(105,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v105 packaged opt-in advanced Smart Auto, original v7 and Android signing')

with ZipFile(R/"app/build/outputs/apk/debug/app-debug.apk") as z:
 assert z.read("assets/bf_auto_sbb_demo.js")== (R/"app/src/main/assets/bf_auto_sbb_demo.js").read_bytes()
assert java.index('readPackagedText("bf10500_qol_advanced_smart_auto.js")')<java.index('readPackagedText("bf_auto_sbb_demo.js")')<java.index('readPackagedText("bf_sbb_fallback_dispatch.js")')
