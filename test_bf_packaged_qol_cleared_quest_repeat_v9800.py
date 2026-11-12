"""v98 APK packages additive bounded quest repeat without changing native rules."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    names=set(z.namelist())
    assert 'assets/bf9800_qol_cleared_quest_repeat.js' in names
    assert 'assets/bf9700_qol_rotating_backups.js' in names
    src=z.read('assets/bf9800_qol_cleared_quest_repeat.js').decode('utf8')
    assert src.count('BF_GLOBAL_QOL_CLEARED_QUEST_REPEAT_V9800')==1
    assert 'results.replayBattle()' in src
    assert 'try{replayed=!!results.replayBattle();}' in src
    assert 'catch(_){replayed=false;}' in src
    assert "try{auto.click();}" in src
    assert "catch(_){return false;}" in src
    assert "finally{internalToggle=false;}" in src
    assert 'const receipt=results.committedClearCount;' in src
    assert 'return receipt(s.missionId)===s.clears;' in src
    assert 'function safeResultSnapshot(){' in src
    assert 'const s=results.snapshot();' in src
    assert "for(const key of ['missionId','clears','done','victory','archive'," in src
    assert 'out[key]=s[key];' in src
    assert "stop('Stopped: battle results unavailable',false)" in src
    assert "stop('Stopped: native mission replay failed',false)" in src
    assert 's.clears<=session.lastClear' in src
    assert "finish.id='bf9800-finish-current'" in src
    assert 'finishAfterCurrent:true' not in src
    assert 'session.finishAfterCurrent=true' in src
    assert "stop('Finished current battle by player request',true)" in src
    assert src.index('if(session.finishAfterCurrent)')<src.index('return playAgain();',src.index('session.completed++;'))
    assert 'sourceQuestMatches' in src and 'campaign.waveReadiness' in src
    assert "typeof campaign.sourceEconomyReadiness!=='function'" in src
    assert 'campaign.sourceEconomyReadiness()!==true' in src
    assert '!Number.isSafeInteger(S.totalWaves)' in src
    assert 'S.totalWaves!==row.verifiedWaveCount' in src
    assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf9700_qol_rotating_backups.js")')<java.index('readPackagedText("bf9800_qol_cleared_quest_repeat.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
manifest=(R/'app/src/main/AndroidManifest.xml').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in gradle for v in range(98,200))
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert "bf-development-debug.keystore" in gradle
assert 'android.permission.INTERNET' not in manifest
print('PASS v98 packaged auto repeat, stable signing/package/v7 save and v97 backup module')
