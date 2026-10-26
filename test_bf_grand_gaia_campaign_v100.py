"""v1.00: 106-quest, three-region Grand Gaia offline demo campaign regression.

Exercise the actual quest-unlock/save/reward handlers with simulated victories.
Original enemy identities, damage, AI, energy consumption and drops remain
unverified; THIS IS NOT a replay of the native original battles.
"""
from pathlib import Path
import shutil,json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
html=(ASSETS/'index.html').read_text('utf-8')
assert 'bf_global_offline_demo_v7' in html
for mark in ('BF_ORIGINAL_MORGAN_QUESTS_V080','BF_STLAMIA_QUESTS_V090',
             'BF_EXTENDED_PLAYABLE_ATTACK_FRAMES_V065'):
    assert '/* '+mark+' */' in html,mark
java=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf090_st_lamia_map.js")') < java.index(
    'readPackagedText("bf100_grand_gaia_campaign.js")')
overlay=(ASSETS/'bf100_grand_gaia_campaign.js').read_text('utf8')
assert overlay.count('/* BF_GRAND_GAIA_CAMPAIGN_V100 */')==1
assert 'localStorage' not in overlay and 'saveProgress(' not in overlay
assert 'Enemy' not in overlay or 'DEMO' in overlay

with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,
      executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
      args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':390,'height':844})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.evaluate("""() => {
     const db={};
     Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}}});
     window.alert=()=>{};window.confirm=()=>true;
     HTMLMediaElement.prototype.load=()=>{};
     HTMLMediaElement.prototype.pause=()=>{};
     HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""")
  page.set_content(html,wait_until='load',timeout=90000)
  assert page.evaluate('P.version')==7
  assert page.evaluate('QUESTS.length')==106
  assert page.evaluate('BF_QUEST_CATALOG.length')==106 if page.evaluate("typeof BF_QUEST_CATALOG!=='undefined'") else True
  page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
  page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
  page.add_script_tag(path=str(ASSETS/'bf080_morgan_map.js'))
  page.add_script_tag(path=str(ASSETS/'bf090_st_lamia_map.js'))
  page.add_script_tag(path=str(ASSETS/'bf100_grand_gaia_campaign.js'))
  page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
  assert page.evaluate('BFGlobalQuestText.missions.length')==106
  assert page.evaluate('BFGlobalQuestText.dungeons.length')==23
  assert page.evaluate('BFMistralMap.entries.length')==9
  assert page.evaluate('BFMorganMapV080.entries.length')==7
  assert page.evaluate('BFStLamiaMapV090.entries.length')==7
  assert page.evaluate('BFGrandGaiaCampaignV100.missionCount')==106
  assert page.evaluate('BFGrandGaiaCampaignV100.dungeonCount')==23
  assert page.locator('[data-bf-campaign-region]').count()==3
  assert page.evaluate('BFGrandGaiaCampaignV100.summary().total')==106
  assert page.evaluate('BFGrandGaiaCampaignV100.summary().cleared')==0
  assert page.evaluate('BFMorganMapV080.isUnlocked(200)') is False
  assert page.evaluate('BFStLamiaMapV090.isUnlocked(300)') is False
  first=page.evaluate("""() => ({
     roster:JSON.stringify(P.roster), squad:JSON.stringify(P.squad),
     unitExp:JSON.stringify(P.unitExp),version:P.version
  })""")
  # No enemy combat is faked in this test; invoke the real victory/reward logic.
  report=page.evaluate("""() => {
     const log=[], checkpoints=[];
     for(let i=0;i<QUESTS.length;i++){
        const q=QUESTS[i];
        if(!questUnlocked(q))return {error:'mission locked',id:q.missionId,index:i,log};
        QUEST=q;P.lastMission=q.missionId;E.mode.value='archive';reset();
        if(S.totalWaves!==q.battles)return {error:'battle count',id:q.missionId};
        const past={exp:P.exp,zel:P.zel,karma:P.karma,clears:P.clears};
        finish(true);
        if((P.questClears?.[q.missionId]||0)<1)return {error:'clear record missing',id:q.missionId};
        if(P.exp-past.exp!==q.exp || P.zel-past.zel!==q.zel ||
           P.karma-past.karma!==q.karma || P.clears-past.clears!==1)
           return {error:'demo reward mismatch',id:q.missionId,
             got:[P.exp-past.exp,P.zel-past.zel,P.karma-past.karma,P.clears-past.clears],
             expected:[q.exp,q.zel,q.karma,1]};
        log.push(q.missionId);
        if([33,69,105].includes(i))checkpoints.push({
          at:log.length,campaign:BFGrandGaiaCampaignV100.summary(),
          morgan:BFMorganMapV080.isUnlocked(200),
          lamia:BFStLamiaMapV090.isUnlocked(300)
        });
     }
     const serialized=localStorage.getItem('bf_global_offline_demo_v7');
     const restored=serialized?JSON.parse(serialized):null;
     return {log,checkpoints,state:{
        version:P.version,clears:P.clears,exp:P.exp,zel:P.zel,karma:P.karma,
        roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
        unitExp:JSON.stringify(P.unitExp),savedVersion:restored?.version,
        saveClears:restored?Object.keys(restored.questClears||{}).length:0
     }};
  }""")
  assert 'error' not in report,report
  assert len(report['log'])==106
  assert len(set(report['log']))==106
  assert [a['at'] for a in report['checkpoints']]==[34,70,106]
  assert [a['campaign']['cleared'] for a in report['checkpoints']]==[34,70,106]
  assert report['checkpoints'][0]['morgan'] is True
  assert report['checkpoints'][0]['lamia'] is False
  assert report['checkpoints'][1]['lamia'] is True
  state=report['state']
  assert state['version']==state['savedVersion']==7
  assert state['clears']==state['saveClears']==106
  assert state['roster']==first['roster'] and state['squad']==first['squad']
  # Successful quest clears legitimately grant DEMO EXP to owned squad units.
  prior_exp=json.loads(first['unitExp'])
  later_exp=json.loads(state['unitExp'])
  assert set(prior_exp)==set(later_exp)
  assert all(later_exp[k]>=prior_exp[k] for k in prior_exp)
  assert any(later_exp[k]>prior_exp[k] for k in prior_exp)
  page.wait_for_function("()=>document.querySelector('#bf100-campaign .bf100-overall')?.textContent.includes('106 / 106')")
  assert page.evaluate('BFGrandGaiaCampaignV100.summary().dungeons')==23
  assert page.locator('#bf100-campaign progress').count()==3
  assert page.evaluate("Array.from(document.querySelectorAll('#bf100-campaign progress')).every(x=>x.value===x.max)") is True
  page.locator('[data-bf-campaign-region="morgan"]').click()
  assert page.locator('#bf080-morgan-map').is_visible()
  page.locator('[data-bf-campaign-region="stlamia"]').click()
  assert page.locator('#bf090-stlamia-map').is_visible()
  page.locator('[data-bf-campaign-region="mistral"]').click()
  assert page.locator('.bf-mistral-map').is_visible()
  assert page.evaluate('P.version')==7
  assert not errors,errors
  browser.close()
print('PASS v1.00: all 106 source-quest demo clears, 3 region maps, 23 dungeons, v7 save and rewards')
