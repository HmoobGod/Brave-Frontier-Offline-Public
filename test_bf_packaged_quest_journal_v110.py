"""v1.10 packaged original-quest journal, v7 and original region presence."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as apk:
 names=set(apk.namelist())
 assert 'assets/bf110_quest_journal.js' in names
 script=apk.read('assets/bf110_quest_journal.js').decode('utf-8')
 assert script.count('/* BF_GLOBAL_QUEST_JOURNAL_V110 */')==1
 assert "QUESTS.length!==106" in script
 assert 'BFGlobalQuestText.sourceFor' in script
 assert 'questUnlocked(row.q)' in script
 assert 'localStorage' not in script and 'saveProgress(' not in script
 for path in ('bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js'):
  assert 'assets/'+path in names
 assert 'bf_global_offline_demo_v7' in apk.read('assets/index.html').decode('utf-8')
 assert len(apk.read('assets/bf_home_nav.js'))<65536
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.index('readPackagedText("bf101_story_continue.js")')<java.index('readPackagedText("bf110_quest_journal.js")')
assert "versionName '" in (R/'app/build.gradle').read_text('utf-8')
print('PASS v1.10 journal APK, 3-region quest baseline and original save v7')
