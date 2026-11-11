"""v1.10: original 106-quest journal searches, access gates and v7 preservation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
js=(A/'bf110_quest_journal.js').read_text('utf-8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert js.count('/* BF_GLOBAL_QUEST_JOURNAL_V110 */')==1
assert 'localStorage' not in js and 'saveProgress(' not in js
assert 'questUnlocked(row.q)' in js and 'BFQuestAreas.choose(row.q)' in js
assert java.index('readPackagedText("bf101_story_continue.js")') < java.index('readPackagedText("bf110_quest_journal.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
   const store={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=String(v),
     removeItem:k=>{delete store[k]},key:i=>Object.keys(store)[i]??null,
     get length(){return Object.keys(store).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf-8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for path in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js'):
  page.add_script_tag(path=str(A/path))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalQuestJournalV110.total')==106
 assert page.locator('#bf110-journal').count()==1
 before=page.evaluate("""()=>({p:JSON.stringify(P),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'journal refresh must never modify saved data'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf110-journal summary').click()
 assert page.locator('[data-bf-journal-entry]').count()==20
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==106
 # The authenticated original description should be searchable without mutation.
 original_description=page.evaluate('BFGlobalQuestText.sourceFor(QUESTS[0]).mission.description')
 assert isinstance(original_description,str) and len(original_description.strip())>10
 page.locator('#bf110-search').fill(original_description.strip())
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==1
 assert page.locator('[data-bf-journal-entry="1"]').count()==1
 page.locator('#bf110-search').fill('')
 # New read-only story completion, direct-next action and sortable source fields.
 assert page.evaluate('BFGlobalQuestJournalV110.nextAvailableMission')==1
 assert '/106 cleared' in page.locator('#bf110-progress').text_content()
 assert 'MISSION 1' in page.locator('#bf110-next').text_content()
 p_before_sort=page.evaluate('JSON.stringify(P)')
 page.locator('#bf110-sort').select_option('energy')
 assert int(page.locator('[data-bf-journal-entry]').first.get_attribute(
   'data-bf-journal-entry'))==page.evaluate('''()=>QUESTS.slice().sort((a,b)=>
     a.energy-b.energy||a.missionId-b.missionId)[0].missionId''')
 page.locator('#bf110-sort').select_option('exp')
 assert int(page.locator('[data-bf-journal-entry]').first.get_attribute(
   'data-bf-journal-entry'))==page.evaluate('''()=>QUESTS.slice().sort((a,b)=>
     b.exp-a.exp||a.missionId-b.missionId)[0].missionId''')
 page.locator('#bf110-sort').select_option('story')
 assert page.evaluate('JSON.stringify(P)')==p_before_sort
 page.locator('#bf110-region').select_option('morgan')
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==36
 page.locator('#bf110-search').fill('burning desert')
 # Source-description search may match multiple original Morgan mission descriptions.
 expected_burning=page.evaluate("""() => QUESTS.filter(q => {
   if(q.dungeonId<200 || q.dungeonId>=300)return false;
   const source=BFGlobalQuestText.sourceFor(q);
   return [String(q.missionId),source.mission.name,source.dungeon.name,
     source.mission.description].some(text=>text.toLocaleLowerCase().includes('burning desert'));
 }).length""")
 assert expected_burning>=1
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==expected_burning
 assert page.locator('[data-bf-journal-entry="200"]').count()==1
 page.locator('[data-bf-journal-preview="200"]').click()
 assert 'The Burning Desert' in page.locator('#bf110-preview').text_content()
 assert page.locator('[data-bf-journal-open="200"]').is_disabled()
 # Locked entries must not be selectable even via the public API.
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(200)') is False
 assert page.evaluate('QUEST.missionId')!=200
 page.locator('#bf110-region').select_option('all')
 page.locator('#bf110-search').fill('')
 page.locator('#bf110-state').select_option('available')
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')>=1
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(1)') is True
 assert page.evaluate('QUEST.missionId')==1
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.evaluate('BFGlobalQuestJournalV110.nextAvailableMission')==200
 assert '34/106 cleared' in page.locator('#bf110-progress').text_content()
 page.evaluate('S.busy=true')
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_disabled()
 page.evaluate('S.busy=false')
 # An unsaved archive victory, including a failed quota-limited save,
 # must not navigate through either NEXT UNCLEARED or journal OPEN.
 page.evaluate("""() => {
   window.__journalOldResults=window.BFGlobalBattleResultsV3000;
   window.__journalOldSetItem=localStorage.setItem;
   localStorage.setItem=()=>{throw new DOMException('Quota exceeded','QuotaExceededError')};
   window.BFGlobalBattleResultsV3000={committedClearCount:()=>0};
   S.mode='archive';S.over=true;S.phase='Victory';S.busy=false;
 }""")
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_disabled()
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(200)') is False
 assert page.evaluate('QUEST.missionId')==1
 page.evaluate("""() => {
   localStorage.setItem=window.__journalOldSetItem;
   window.BFGlobalBattleResultsV3000=window.__journalOldResults;
   S.over=false;S.phase='Idle';S.auto=false;
 }""")
 # Between-turn player Auto still owns navigation even with S.busy=false.
 page.evaluate("()=>{S.mode='archive';S.auto=true;S.over=false;S.busy=false}")
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_disabled()
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(200)') is False
 page.evaluate("()=>{S.auto=false}")
 # Auto Repeat can also own navigation while S.busy is briefly false.
 page.evaluate("""() => {
   window.__journalOldRepeat=window.BFGlobalQoLQuestRepeatV9800;
   window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:true})};
 }""")
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_disabled()
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(200)') is False
 # A present but broken repeat provider is fail-closed too.
 page.evaluate("""() => {
   window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{throw Error('broken repeat provider')}};
 }""")
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_disabled()
 assert page.evaluate('BFGlobalQuestJournalV110.chooseMission(200)') is False
 assert page.evaluate('QUEST.missionId')==1
 page.evaluate('()=>{window.BFGlobalQoLQuestRepeatV9800=window.__journalOldRepeat}')
 page.evaluate('BFGlobalQuestJournalV110.refresh()')
 assert page.locator('#bf110-next').is_enabled()
 page.locator('#bf110-next').click()
 assert page.evaluate('QUEST.missionId')==200
 assert page.locator('#bf080-morgan-map').is_visible()
 page.locator('#bf110-region').select_option('morgan')
 page.locator('#bf110-search').fill('burning desert')
 page.locator('#bf110-state').select_option('available')
 assert page.locator('[data-bf-journal-open="200"]').is_enabled()
 page.locator('[data-bf-journal-open="200"]').click()
 assert page.evaluate('QUEST.missionId')==200
 assert page.locator('#bf080-morgan-map').is_visible()
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 page.locator('#bf110-region').select_option('stlamia')
 page.locator('#bf110-search').fill('300')
 page.locator('#bf110-state').select_option('available')
 assert page.locator('[data-bf-journal-open="300"]').is_enabled()
 page.locator('[data-bf-journal-open="300"]').click()
 assert page.evaluate('QUEST.missionId')==300
 assert page.locator('#bf090-stlamia-map').is_visible()
 page.locator('#bf110-region').select_option('all')
 page.locator('#bf110-search').fill('')
 page.locator('#bf110-state').select_option('cleared')
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==70
 assert '70/106 cleared' in page.locator('#bf110-progress').text_content()
 page.locator('#bf110-sort').select_option('clears')
 assert page.evaluate('BFGlobalQuestJournalV110.matchingCount')==70
 assert page.locator('#bf110-progress').count()==1
 page.locator('#bf110-more').click()
 assert page.locator('[data-bf-journal-entry]').count()==40
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v1.10 journal: 106 original English missions, gates/search/regions, v7 passive safety')
