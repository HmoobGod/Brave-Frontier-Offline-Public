"""v0.70 full Mistral quest progression smoke: 34 unlocks, rewards, v7 save.

This fast integration gate calls the real victory handler with simulated wins.
It does NOT assert battles were played or enemy spawns are native original.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
HTML=(ROOT/'app/src/main/assets/index.html').read_text('utf-8')
with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':390,'height':844})
  errors=[]
  page.on('pageerror',lambda err:errors.append(str(err)))
  page.evaluate("""() => {
    const data={};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=String(v)},
      removeItem:k=>{delete data[k]},key:i=>Object.keys(data)[i]??null,
      get length(){return Object.keys(data).length}}});
    window.alert=()=>{};window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};
    HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""")
  page.set_content(HTML,wait_until='load',timeout=90000)
  ids=[1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,
       50,51,52,53,60,61,62,63,70,71,72,73,81,82,83,84,85]
  assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,34)')==ids
  results=page.evaluate("""() => {
    const rows=[],starting={...P};
    for (const q of QUESTS.slice(0,34)) {
      if (!questUnlocked(q))return {error:'locked',mission:q.missionId,requires:q.requires,rows};
      QUEST=q;P.lastMission=q.missionId;E.mode.value='archive';reset();
      if (S.totalWaves !== q.battles) return {error:'waves',mission:q.missionId};
      const previous={clears:P.clears,exp:P.exp,zel:P.zel,karma:P.karma};
      finish(true);
      const clearSave=localStorage.getItem('bf_global_offline_demo_v7');
      if (!clearSave)return {error:'missing local save',mission:q.missionId};
      const parsed=JSON.parse(clearSave);
      if (parsed.version!==7 || parsed.questClears?.[q.missionId]!==1)
        return {error:'save mismatch',mission:q.missionId};
      rows.push({
        missionId:q.missionId,requires:q.requires,battles:q.battles,
        deltaClears:P.clears-previous.clears,
        deltaExp:P.exp-previous.exp,deltaZel:P.zel-previous.zel,
        deltaKarma:P.karma-previous.karma, expectedExp:q.exp,
        expectedZel:q.zel,expectedKarma:q.karma
      });
    }
    return {rows,final:{version:P.version,clears:P.clears,exp:P.exp,
         zel:P.zel,karma:P.karma,owned:P.roster.slice(),
         squad:P.squad.slice(),completed:P.questClears}};
  }""")
  assert 'error' not in results,results
  assert len(results['rows'])==34
  for row in results['rows']:
    assert row['deltaClears']==1
    assert row['deltaExp']==row['expectedExp'],row
    assert row['deltaZel']==row['expectedZel'],row
    assert row['deltaKarma']==row['expectedKarma'],row
  final=results['final']
  assert final['version']==7 and final['clears']==34
  assert len(final['completed'])==34
  assert final['exp']==sum(row['expectedExp'] for row in results['rows'])
  assert final['zel']==sum(row['expectedZel'] for row in results['rows'])
  assert final['karma']==sum(row['expectedKarma'] for row in results['rows'])
  assert final['squad']==[10011,20011,30011,40011,50011,60011]
  assert len(final['owned'])==6
  assert not errors,errors
  browser.close()
print('PASS v0.70 all 34 original mission chains, honest simulated clears/rewards, save v7 progression')
