"""v87: 2014 historical Basics exact AI/drop references; not native 2022 gameplay."""
from pathlib import Path
import json, shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
historical=json.loads((R/'source_data/bf_global_historical_encounters_v120.json').read_text('utf8'))
q=historical['missions'][0]
assert (q['id'],q['name'],q['gitBlobSha']) == (1,'Basics of Battle','797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe')
assert [(e['name'],e['unitId'],e['hp'],e['atk'],e['def'],e['aiId'])
        for w in q['waves'] for e in w['enemies']] == [
    ('Mossy',30030,300,290,50,1),
    ('Sparky',40030,300,320,0,1),
    ('Mossy',30030,300,290,50,1),
    ('King Mossy',30031,3000,320,30,1)]
js=(A/'bf8700_original_basics_ai_reference.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_HISTORICAL_BASICS_AI_REFERENCE_V8700')==1
assert all(term not in js for term in ('localStorage','saveProgress(', 'BFAndroid', 'fetch(', 'XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf200_historical_wave_lab.js")') < java.index('readPackagedText("bf8700_original_basics_ai_reference.js")')
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,
      executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
      args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':390,'height':844});errors=[]
    p.on('pageerror',lambda e:errors.append(str(e)))
    p.evaluate("""() => {
      const data={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),
        removeItem:k=>delete data[k],key:i=>Object.keys(data)[i]??null,
        get length(){return Object.keys(data).length}
      }});
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
    assert p.evaluate('P.version')==7
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.source.enemySlots')==4
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.source.confirmed2022') is False
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,0).element')=='earth'
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,0).element')=='thunder'
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(3,0).hp')==3000
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(3,0).zel.maxPerDrop')==120
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(3,0).karma.maxPerDrop')==75
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,1).treasure.zelAmount')==500
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,1).treasure.karmaAmount')==250
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,1).treasure.chestChancePercent')==100
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,0).unitDrop.percent')==100
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(3,0).unitDrop') is None
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,0).action.type')=='attack'
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,0).action.targetCondition')=='random'
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,0).action.percent')==100
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,0).ailmentResistancePercent.poison')==0
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(2,1).itemDropEntries')==0
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(0,0)') is None
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1,3)') is None
    assert p.evaluate('BFHistoricalBasicsAIReferenceV8700.lookup(1.5,0)') is None
    assert p.evaluate('Object.isFrozen(BFHistoricalBasicsAIReferenceV8700.lookup(1,0).action)') is True
    before=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
      save:localStorage.getItem('bf_global_offline_demo_v7')})""")
    p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    p.locator('#bf200-trials summary').first.click()
    assert p.locator('#bf8700-original-ai-evidence').is_visible()
    p.locator('#bf8700-original-ai-evidence summary').click()
    assert p.locator('#bf8700-source-rows p[data-source-key]').count()==4
    assert 'random target' in p.locator('#bf8700-source-rows').text_content()
    assert 'NOT confirmed for 2022 Global' in p.locator('#bf8700-source-rows').text_content()
    p.locator('#bf200-mission').select_option('200')
    assert p.locator('#bf8700-original-ai-evidence').is_hidden()
    p.locator('#bf200-mission').select_option('1')
    assert p.locator('#bf8700-original-ai-evidence').is_visible()
    p.add_script_tag(path=str(A/'bf8700_original_basics_ai_reference.js'))
    assert p.locator('#bf8700-original-ai-evidence').count()==1
    after=p.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
      save:localStorage.getItem('bf_global_offline_demo_v7')})""")
    assert before==after,'archived AI inspector cannot change gameplay or saves'
    assert not errors,errors
    b.close()
print('PASS v87 original 2014 AI/source reward descriptors, four slots, negative/fail-closed cases, UI and save isolation')
