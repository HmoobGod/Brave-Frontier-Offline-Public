"""v1.01 APK integrity: additive 106-mission story continuation."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 files=set(z.namelist())
 script=z.read('assets/bf101_story_continue.js').decode('utf-8')
 assert script.count('/* BF_GRAND_GAIA_CONTINUE_V101 */')==1
 assert 'QUESTS.length!==106' in script and 'questUnlocked(q)' in script
 assert 'CONTINUE STORY' in script
 # Player-initiated NEXT mission Auto: original 2022 wave COUNT and
 # whole-source economy both required; only native mission/Auto controls.
 assert "autoButton.id='bf101-continue-auto'" in script
 assert 'function canContinueAuto(q)' in script
 assert '(auto.disabled&&!S.over)' in script
 assert 'auto.disabled||auto.checked' in script
 assert 'function sourceReadyForAuto(q)' in script
 assert 'source.sourceEconomyReadiness()!==true' in script
 assert 'source.waveReadiness(q.missionId)' in script
 assert 'function continueAuto()' in script
 assert 'try{selected=BFQuestAreas.choose(q)===true;}' in script
 assert 'try{auto.click();}' in script
 assert 'function disarmContinueAuto()' in script
 assert 'S.auto=false;' in script
 assert 'function sourceEconomyPreview(q)' in script
 assert 'window.BFOriginalGlobalQuestEnergyV14300' in script
 assert 'row.some((v,i)=>!Number.isSafeInteger(v)||v<0||v!==expected[i])' in script
 assert '2022 source reference:' in script
 assert 'DEMO credits EXP/Zel/Karma on clear; stamina not enforced' in script
 assert 'unattendedOwnsNavigation' in script
 assert "repeat.statusSnapshot()?.active===true" in script
 assert 'function uncommittedVictory()' in script
 assert 'window.BFGlobalBattleResultsV3000' in script
 assert 'results.committedClearCount(q.missionId)!==count' in script
 assert 'uncommittedVictory()' in script
 assert 'localStorage' not in script and 'saveProgress(' not in script
 for name in ('bf100_grand_gaia_campaign.js','bf090_st_lamia_map.js','bf080_morgan_map.js'):
  assert 'assets/'+name in files
 assert len(z.read('assets/bf_home_nav.js')) <= 128 * 1024
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf-8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.index('readPackagedText("bf100_grand_gaia_campaign.js")')<java.index('readPackagedText("bf101_story_continue.js")')
gradle=(R/'app/build.gradle').read_text('utf-8')
assert "versionName '" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf-8')
print('PASS v1.01 packaged three-region Continue Story, existing save v7')
