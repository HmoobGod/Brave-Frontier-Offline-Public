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
 # Rename and duplicate only the local preset metadata; never touch v7.
 assert p.evaluate(api+'.renamePreset(0,"Farming Prime")') is True
 assert p.evaluate(api+'.info()[0].name')=='Farming Prime'
 assert p.evaluate(api+'.duplicatePreset(0)') is True
 assert p.evaluate(api+'.info()[1].ids')==[10011,20011]
 assert p.evaluate(api+'.info()[1].name')=='Farming Prime Copy'
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==base
 assert p.evaluate('window.__resetCalls')==0
 assert p.evaluate(api+'.deletePreset(1)') is True
 assert p.evaluate(api+'.renamePreset(1,"Empty")') is False
 assert p.evaluate(api+'.duplicatePreset(1)') is False
 assert p.evaluate(api+'.renamePreset(0,"  ")') is False
 assert p.evaluate(api+'.info()[0].name')=='Farming Prime'
 p.evaluate('P.squad=[30011]')
 assert p.evaluate(api+'.savePreset(1,"Boss")') is True
 assert p.evaluate(api+'.info()[1].ids')==[30011]
 p.evaluate("document.getElementById('bf10000-slot').value='0'")
 p.evaluate(api+'.refresh()')
 preview=p.locator('#bf10000-preview').text_content()
 assert 'Add #10011, #20011' in preview,preview
 assert 'Remove #30011' in preview,preview
 assert p.evaluate('P.squad')==[30011]
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==base
 assert p.evaluate(api+'.applyPreset(0)') is True
 assert p.evaluate('P.squad')==[10011,20011]
 assert p.evaluate('window.__resetCalls')==1
 p.evaluate(api+'.refresh()')
 assert 'Already active' in p.locator('#bf10000-preview').text_content()
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
 # v450: a damaged live roster/team must fail closed, even if a local
 # preset still exists. In particular, refresh must not call .slice() on
 # a non-array P.squad or .includes() on a non-array P.roster.
 stored=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 # The older tests intentionally left a roster missing one active unit.
 # Save and restore it, but use a genuinely valid baseline to test recovery.
 original_live=p.evaluate("JSON.stringify({roster:P.roster,squad:P.squad})")
 p.evaluate("()=>{P.roster=[10011,20011,30011];P.squad=[10011,20011]}")
 old=p.evaluate("JSON.stringify({roster:P.roster,squad:P.squad})")
 resets=p.evaluate('window.__resetCalls')
 p.locator('#bf10000-squad-presets > summary').click()
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  for selector in ('#bf10000-squad-presets > summary',
                   '#bf10000-slot','#bf10000-name',
                   '#bf10000-save','#bf10000-apply',
                   '#bf10000-delete','#bf10000-rename','#bf10000-copy',
                   '#bf10000-up','#bf10000-down'):
   rect=p.locator(selector).bounding_box()
   assert rect and rect['height']>=44,(width,selector,rect)
 p.set_viewport_size({'width':390,'height':844})
 for mutation in (
   "()=>{P.squad='corrupt'}",
   "()=>{P.squad=[10011,10011]}",
   "()=>{P.squad=[10011,99999]}",
   "()=>{P.squad=[10011,20011];P.roster=null}",
   "()=>{P.roster='invalid'}",
 ):
  p.evaluate("(v)=>{const state=JSON.parse(v);P.roster=state.roster;P.squad=state.squad}",old)
  p.evaluate(mutation)
  p.evaluate(api+'.refresh()')
  assert p.locator('#bf10000-apply').is_disabled(),mutation
  assert p.locator('#bf10000-save').is_disabled(),mutation
  assert 'Preview unavailable' in p.locator('#bf10000-preview').text_content(),mutation
  assert p.evaluate(api+'.applyPreset(1)') is False,mutation
  assert p.evaluate(api+'.savePreset(1,"unsafe")') is False,mutation
  assert p.evaluate('window.__resetCalls')==resets,mutation
  assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==stored,mutation
 p.evaluate("(v)=>{const state=JSON.parse(v);P.roster=state.roster;P.squad=state.squad}",old)
 p.evaluate(api+'.refresh()')
 assert 'Preview unavailable' not in p.locator('#bf10000-preview').text_content()
 p.evaluate("(v)=>{const state=JSON.parse(v);P.roster=state.roster;P.squad=state.squad}",original_live)
 p.evaluate(api+'.refresh()')
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==stored
 p.add_script_tag(path=str(A/'bf10000_qol_squad_presets.js'))
 assert p.locator('#bf10000-squad-presets').count()==1
 assert p.evaluate('P.version')==7
 # Real native app: organizing slots never applies a team or writes canonical v7.
 q=b.new_page(viewport={'width':390,'height':844})
 q.on('pageerror',lambda e:errors.append(str(e)))
 q.evaluate("""()=>{
   const data={};window.__writes=[];window.__failPreset=false;
   Object.defineProperty(window,'localStorage',{value:{
     getItem:k=>data[k]??null,setItem:(k,v)=>{
       if(window.__failPreset&&k.includes('qol_squad_presets'))throw Error('storage full');
       window.__writes.push(k);data[k]=String(v);
     },removeItem:k=>delete data[k],key:i=>Object.keys(data)[i]??null,
     get length(){return Object.keys(data).length}},configurable:true});
   window.alert=()=>{};window.confirm=()=>true;
 }""")
 q.set_content((A/'index.html').read_text(),wait_until='load')
 q.add_style_tag(path=str(A/'bf_home_nav.css'))
 q.add_script_tag(path=str(A/'bf_home_nav.js'))
 q.add_script_tag(path=str(A/'bf10000_qol_squad_presets.js'))
 q.evaluate("BF_homeNav.go('units')")
 q.locator('#bf10000-squad-presets').evaluate('(e)=>e.open=true')
 assert q.evaluate(api+'.savePreset(0,"First")')
 assert q.evaluate(api+'.savePreset(1,"Second")')
 baseline=q.evaluate("JSON.stringify({p:P,s:S,quest:QUEST.missionId,raw:localStorage.getItem('bf_global_offline_demo_v7')})")
 q.evaluate('window.__writes=[]')
 q.locator('#bf10000-slot').select_option('0')
 q.locator('#bf10000-name').fill('Unfinished name')
 assert q.locator('#bf10000-up').is_disabled()
 q.locator('#bf10000-down').focus()
 q.keyboard.press('Enter')
 assert q.locator('#bf10000-slot').input_value()=='1'
 assert q.locator('#bf10000-name').input_value()=='Unfinished name'
 assert q.evaluate(api+'.info().map(s=>s.name)')==['Second','First',None,None,None]
 # Move into an empty slot with Space, preserving the entire displaced preset.
 q.locator('#bf10000-down').focus();q.keyboard.press('Space')
 assert q.evaluate(api+'.info().map(s=>s.name)')==['Second',None,'First',None,None]
 saved=q.evaluate('JSON.stringify('+api+'.info())')
 raw=q.evaluate('localStorage.getItem('+api+'.key)')
 q.evaluate('window.__failPreset=true')
 assert q.evaluate(api+'.movePreset(2,-1)') is False
 assert q.evaluate('JSON.stringify('+api+'.info())')==saved
 assert q.locator('#bf10000-slot').input_value()=='2'
 assert q.locator('#bf10000-name').input_value()=='Unfinished name'
 assert q.evaluate('localStorage.getItem('+api+'.key)')==raw
 assert 'Could not move' in q.locator('#bf10000-status').text_content()
 q.evaluate('window.__failPreset=false')
 for call in ('movePreset(0,-1)','movePreset(4,1)','movePreset(1,1)',
              'movePreset(2,0)','movePreset(2,"1")','movePreset(0.5,1)'):
  assert q.evaluate(api+'.'+call) is False,call
 q.evaluate('S.busy=true;'+api+'.refresh()')
 assert q.locator('#bf10000-up').is_disabled()
 assert q.locator('#bf10000-down').is_disabled()
 assert q.evaluate(api+'.movePreset(2,1)') is False
 q.evaluate('S.busy=false;'+api+'.refresh()')
 # Both endpoints and mobile geometry, with no horizontal overflow.
 assert q.evaluate(api+'.movePreset(2,1)')
 assert q.evaluate(api+'.movePreset(3,1)')
 assert q.locator('#bf10000-down').is_disabled()
 for width in (320,390,540):
  q.set_viewport_size({'width':width,'height':844})
  for selector in ('#bf10000-up','#bf10000-down'):
   assert q.locator(selector).bounding_box()['height']>=44
  assert q.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 assert q.evaluate("JSON.stringify({p:P,s:S,quest:QUEST.missionId,raw:localStorage.getItem('bf_global_offline_demo_v7')})")==baseline
 assert q.evaluate('window.__writes')==[q.evaluate(api+'.key')]*4
 # Reinitialize the module to read persisted ordering without native save calls.
 q.evaluate("delete window.BFGlobalQoLSquadPresetsV10000;document.querySelector('#bf10000-squad-presets').remove()")
 q.add_script_tag(path=str(A/'bf10000_qol_squad_presets.js'))
 assert q.evaluate(api+'.info().map(s=>s.name)')==['Second',None,None,None,'First']
 assert q.evaluate('window.__writes')==[q.evaluate(api+'.key')]*4
 assert not errors,errors
 b.close()
print('PASS v100 five squad presets: owned-only, save rollback on failure, busy gate, deletion and v7 schema')
