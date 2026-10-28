"""v139: source-authenticated 2014 enemy AI decisions in isolated playable practice.

Not a claim of authentic 2022 Global runtime AI or native damage/target RNG.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
js=(A/'bf200_historical_wave_lab.js').read_text('utf8')
assert 'BF_GLOBAL_ARCHIVE_TRIALS_V200' in js
assert 'function sourceEnemyPlan2014(foes)' in js
assert "ref?.source" in js and "ref.lookup(current.wave+1,slot)" in js
assert "original.actionsPerTurn?.min!==1" in js
assert "original.action?.percent!==100" in js
assert "original.action?.targetCondition!=='random'" in js
assert "nativeRandomTargetImplemented:false" in js
assert 'sourceAttacks.reduce((n,a)=>n+a.syntheticHarm,0)' in js
assert 'random target NOT simulated.' in js
assert not any(q in js for q in ('saveProgress(', 'localStorage.', 'BFAndroid', 'fetch('))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""() => {
    const db={};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
      removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
      get length(){return Object.keys(db).length}}});
    window.alert=()=>{};window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};
    HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf120_historical_encounters.js',
              'bf_global_unit_archive.js','bf150_source_crosscheck.js',
              'bf200_historical_wave_lab.js','bf8700_original_basics_ai_reference.js'):
   p.add_script_tag(path=str(A/name))
 assert p.evaluate('BFArchiveTrialsV200.missions')==21
 assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.source.confirmed2022') is False
 assert p.evaluate('P.version')==7
 original=p.evaluate("""() => ({
   p:JSON.stringify(P),session:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 assert p.evaluate('BFArchiveTrialsV200.startPractice(1)') is True
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 wave1=p.evaluate('BFArchiveTrialsV200.practice')
 assert wave1['wave']==1 and wave1['hp']==11992,wave1
 assert any('2014 source AI: Mossy #30030 ATTACK 100% (1 action)' in s for s in wave1['recent'])
 assert any('random target NOT simulated' in s for s in wave1['recent'])
 assert p.evaluate('BFArchiveTrialsV200.perform("attack")') is True
 assert p.evaluate('BFArchiveTrialsV200.practice.wave')==2
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 wave2=p.evaluate('BFArchiveTrialsV200.practice')
 assert wave2['hp']==11976,wave2
 assert any('Sparky #40030 ATTACK 100% (1 action)' in s and
            'Mossy #30030 ATTACK 100% (1 action)' in s for s in wave2['recent'])
 # KO one enemy: a dead foe must never take a source AI action.
 assert p.evaluate('BFArchiveTrialsV200.perform("attack")') is True
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 partial=p.evaluate('BFArchiveTrialsV200.practice')
 assert any('2014 source AI: Mossy #30030 ATTACK 100% (1 action)' in s and
            'Sparky' not in s for s in partial['recent'])
 assert p.evaluate('BFArchiveTrialsV200.perform("attack")') is True
 assert p.evaluate('BFArchiveTrialsV200.practice.wave')==3
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 boss=p.evaluate('BFArchiveTrialsV200.practice')
 assert any('2014 source AI: King Mossy #30031 ATTACK 100% (1 action)' in s for s in boss['recent'])
 # Fail closed on a missing 2014 source adapter; old practice mechanics remain.
 p.evaluate('delete window.BFHistoricalBasicsAIReferenceV8700')
 assert p.evaluate('BFArchiveTrialsV200.perform("guard")') is True
 no_source=p.evaluate('BFArchiveTrialsV200.practice')
 assert no_source['recent'][-1].startswith('Synthetic enemy reply:')
 assert not no_source['recent'][-2].startswith('2014 source AI:')
 assert p.evaluate('BFArchiveTrialsV200.startPractice(99999)') is False
 after=p.evaluate("""() => ({
   p:JSON.stringify(P),session:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 assert original==after, 'isolated original 2014 AI practice must never mutate owner save or live combat'
 assert not errors, errors
 b.close()
print('PASS v139: 2014 Basics-of-Battle source AI decisions execute in practice across 3 waves, KO filtering, fallback, unchanged v7 save')
