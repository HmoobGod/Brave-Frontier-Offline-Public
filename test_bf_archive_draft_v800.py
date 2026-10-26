"""v8.00: synthetic archive draft of recovered 2022 standard units, save isolation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
code=(A/'bf800_archive_draft.js').read_text('utf8')
combat=(A/'bf300_tactical_rounds.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(code.encode('utf8'))<65536 and len(combat.encode('utf8'))<65536
assert code.count('/* BF_GLOBAL_ARCHIVE_DRAFT_V800 */')==1
assert 'localStorage' not in code+combat and 'saveProgress(' not in code+combat
assert java.index('readPackagedText("bf300_tactical_rounds.js")')<java.index('readPackagedText("bf800_archive_draft.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
   removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
    'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
    'bf110_quest_journal.js','bf120_historical_encounters.js',
    'bf_global_unit_archive.js','bf150_source_crosscheck.js',
    'bf200_historical_wave_lab.js','bf250_squad_training.js',
    'bf500_source_bb_evidence.js','bf700_original_normal_hits.js',
    'bf300_tactical_rounds.js','bf400_original_battle_dossier.js',
    'bf800_archive_draft.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7 and page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFArchiveDraftV800.archiveCount')==2291
 assert page.evaluate('BFArchiveDraftV800.eligibleCount')>=25
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 assert page.evaluate('BFArchiveDraftV800.canStart()') is False
 assert page.evaluate('BFArchiveDraftV800.start()') is False
 assert page.evaluate('BFArchiveDraftV800.add(999999)') is False
 assert page.evaluate('BFArchiveDraftV800.add(10012)') is True
 assert page.evaluate('BFArchiveDraftV800.add(10012)') is False
 assert page.evaluate('BFArchiveDraftV800.selected')==[10012]
 assert page.evaluate('P.roster.includes(10012)') is False
 assert page.evaluate('BFArchiveDraftV800.canStart()') is True
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([10012],1)') is True
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([10012,10012],1)') is False
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([999999],1)') is False
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([],1)') is False
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([10012],200)') is False
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf800-search').fill('Vargas')
 assert 'Vargas' in page.locator('#bf800-results').inner_text()
 assert page.locator('#bf800-selected .bf800-entry').count()==1
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('#bf800-start').click()
 session=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert session['mode']=='archive-draft' and session['draftUnitIds']==[10012]
 assert session['missionId']==1 and session['party'][0]['sourceId']==-10012
 assert session['party'][0]['unitId']==10012
 assert session['party'][0]['name']==page.evaluate('BFGlobalUnitArchive.find(10012).name')
 assert page.evaluate('BFTacticalRoundsV300.canStartDraft([10012],1)') is False
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 snap=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert snap['rounds']==1
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==session
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Archive draft may not recruit units, change battle or modify save'
 assert page.evaluate('BFArchiveDraftV800.remove(10012)') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 assert page.evaluate('BFArchiveDraftV800.add(10011)') is True
 assert page.evaluate('BFArchiveDraftV800.clear()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[]
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.mode')=='owned'
 assert page.evaluate('BFTacticalRoundsV300.snapshot.draftUnitIds')==[]
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert not errors,errors
 browser.close()
print('PASS v8.00: archive draft uses unowned 2022 forms, respects unlocks, supports undo and leaves v7 saved data unchanged')
