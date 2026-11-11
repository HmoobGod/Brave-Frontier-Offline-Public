"""v100: saved current squads and validated, save-compatible manual loadouts."""
from pathlib import Path
import shutil,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf10000_qol_squad_presets.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_SQUAD_PRESETS_V10000')==1
assert len(js.encode())<65536
assert "P.squad=slot.squad.slice()" in js
assert "try{saved=!!saveProgress();}catch(_){saved=false;}" in js
assert "committedSquad(slot.squad)" in js
assert "localStorage.getItem('bf_global_offline_demo_v7')" in js
assert 'P.squad=previous' in js
assert 'localStorage.setItem(key' in js
assert "localStorage.setItem('bf_global_offline_demo_v7'" not in js
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const values={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>values[k]??null,setItem:(k,v)=>values[k]=String(v),
    removeItem:k=>delete values[k],key:i=>Object.keys(values)[i]??null,
    get length(){return Object.keys(values).length}}});
 }""")
 p.set_content('<html><body><div id="squadpicker"></div></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011,20011,30011],squad:[10011,20011],
     questClears:{1:2},exp:9};
   window.S={busy:false};
   window.__savePossible=true;window.__resetCalls=0;window.__renderCalls=0;
   window.saveRecoveryPending=false;
   window.saveProgress=()=>{
     if(!window.__savePossible)return false;
     localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
     return true;};
   window.reset=()=>{window.__resetCalls++;};
   window.renderProgress=()=>{window.__renderCalls++;};
   saveProgress();
 }""")
 base=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf10000_qol_squad_presets.js'))
 api='BFGlobalQoLSquadPresetsV10000'
 assert p.locator('#bf10000-squad-presets').count()==1
 assert p.evaluate(api+'.info().length')==5
 assert p.evaluate(api+'.savePreset(0,"Farming")') is True
 assert p.evaluate(api+'.savePreset(0,"Farming")') is True
 assert p.evaluate(api+'.info()[0].name')=='Farming'
 assert p.evaluate(api+'.info()[0].ids')==[10011,20011]
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==base
 p.evaluate('P.squad=[30011]')
 assert p.evaluate(api+'.savePreset(1,"Boss")') is True
 assert p.evaluate(api+'.info()[1].ids')==[30011]
 assert p.evaluate(api+'.applyPreset(0)') is True
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert json.loads(p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')"))['squad']==[10011,20011]
 after=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 # An adapter may say success without committing the selected squad.
 # In that case neither P nor the live battle is allowed to change.
 p.evaluate("""()=>{window.__squadOriginalSave=window.saveProgress;
   window.saveProgress=()=>true;}""")
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 assert 'not verified' in p.locator('#bf10000-status').text_content()
 # Even a plausible v7 record for the wrong squad is not a receipt.
 p.evaluate("""()=>{window.saveProgress=()=>{
   localStorage.setItem('bf_global_offline_demo_v7',
     JSON.stringify({version:7,squad:[10011,20011]}));return true;};}""")
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 p.evaluate("raw=>localStorage.setItem('bf_global_offline_demo_v7',raw)",after)
 p.evaluate('window.saveProgress=window.__squadOriginalSave')
 p.evaluate('window.__savePossible=false')
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 # A failing storage adapter can THROW rather than return false. The active
 # team, canonical v7 save and battle reset counter must still be unchanged.
 p.evaluate("""()=>{window.__savePossible=true;
   window.__squadOriginalSave=window.saveProgress;
   window.saveProgress=()=>{throw new Error('synthetic canonical save failure')};}""")
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 assert 'save unavailable' in p.locator('#bf10000-status').text_content()
 p.evaluate('window.saveProgress=window.__squadOriginalSave')
 # Native Auto may have a gap with S.busy=false between scheduled turns.
 # Applying another squad must NEVER reset the live battle or save a team
 # during that gap. An Auto-owned result is no longer a live turn.
 p.evaluate("""()=>{window.__savePossible=true;S.busy=false;
   S.auto=true;S.over=false;
   document.getElementById('bf10000-slot').value='1';
   BFGlobalQoLSquadPresetsV10000.refresh();}""")
 assert p.locator('#bf10000-apply').is_disabled()
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 # The preset panel is collapsed; text_content reads the status even while hidden.
 assert 'Stop Auto Battle' in p.locator('#bf10000-status').text_content()
 p.evaluate('S.over=true')
 p.evaluate(api+'.refresh()')
 assert not p.locator('#bf10000-apply').is_disabled()
 # Unsaved archived victory: a preset reset would abandon the result screen
 # and its unpaid clear. Even a stale success-looking UI is not a receipt.
 p.evaluate("""()=>{
   S.auto=false;S.mode='archive';S.phase='Victory';S.over=true;
   window.QUEST={missionId:1};
   window.BFGlobalBattleResultsV3000={
     snapshot:()=>({missionId:1,done:true,victory:true,archive:true,stored:true}),
     committedClearCount:id=>JSON.parse(localStorage.getItem(
       'bf_global_offline_demo_v7')).questClears[id]??0
   };
   P.questClears[1]=3;
   BFGlobalQoLSquadPresetsV10000.refresh();
 }""")
 assert p.locator('#bf10000-apply').is_disabled()
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert 'Victory is not saved' in p.locator('#bf10000-status').text_content()
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 # A genuinely committed receipt restores the normal manual preset action.
 p.evaluate("""()=>{P.questClears[1]=2;
   BFGlobalQoLSquadPresetsV10000.refresh();}""")
 assert not p.locator('#bf10000-apply').is_disabled()
 # Throwing or absent optional results cannot authorize resetting Victory.
 p.evaluate("""()=>{
   BFGlobalBattleResultsV3000={snapshot:()=>{throw Error('receipt unavailable')}};
   BFGlobalQoLSquadPresetsV10000.refresh();
 }""")
 assert p.locator('#bf10000-apply').is_disabled()
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate('window.__resetCalls')==1
 p.evaluate("""()=>{
   delete window.BFGlobalBattleResultsV3000;
   BFGlobalQoLSquadPresetsV10000.refresh();
 }""")
 assert p.locator('#bf10000-apply').is_disabled()
 assert p.evaluate(api+'.applyPreset(1)') is False
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==after
 p.evaluate("""()=>{delete window.QUEST;S.auto=false;S.over=false;
   delete S.mode;delete S.phase;}""")
 p.evaluate('''()=>{window.__savePossible=true;window.S.busy=true;}''')
 assert p.evaluate(api+'.applyPreset(1)') is False
 p.evaluate('''()=>{window.S.busy=false;P.roster=[10011,30011];}''')
 assert p.evaluate(api+'.applyPreset(0)') is False
 assert p.evaluate(api+'.info()[0].available') is False
 # Deleting a preset never alters the currently active squad.
 assert p.evaluate(api+'.deletePreset(0)') is True
 assert p.evaluate(api+'.info()[0].name') is None
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate(api+'.savePreset(6,"No")') is False
 assert p.evaluate(api+'.applyPreset(-1)') is False
 p.add_script_tag(path=str(A/'bf10000_qol_squad_presets.js'))
 assert p.locator('#bf10000-squad-presets').count()==1
 assert p.evaluate('P.version')==7
 assert not errors,errors
 b.close()
print('PASS v100 five squad presets: owned-only, save rollback on failure, busy gate, deletion and v7 schema')
