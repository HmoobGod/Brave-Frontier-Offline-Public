"""v1.00: 106-quest, three-region Grand Gaia offline demo campaign regression.

Exercise the actual quest-unlock/save/reward handlers with simulated victories.
Original enemy identities, damage, AI, energy consumption and drops remain
unverified; THIS IS NOT a replay of the native original battles.
"""
from pathlib import Path
import shutil,json,re
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
# Pin every runtime wave count against the original 2022 mission-master
# source, not any mutable live QUESTS field or fabricated formation.
pinned=json.loads((ROOT/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
assert pinned['readOnly'] is True and pinned['year']==2022 and pinned['total']==106
assert pinned['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert pinned['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
source_rows=re.search(r'const verifiedWaveRows=Object\.freeze\((\[\[.*?\]\])\.map\(Object\.freeze\)\);',overlay)
assert source_rows,'pinned wave rows missing'
assert json.loads(source_rows.group(1))==[[r[0],r[1],r[3]] for r in pinned['records']]

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
  # Source-ordered next-playable lookup is read-only and respects real unlocks.
  initial_next=page.evaluate("""() => BFGrandGaiaCampaignV100.nextPlayable()""")
  assert initial_next is not None and initial_next['missionId']==page.evaluate('QUESTS[0].missionId')
  # Source-pinned 2022 Economy v143 is available in the packaged app after
  # v100 loads. Verify it protects next-mission routing against any changed
  # unlock, stamina or scalar reward field anywhere in the 106-row catalog.
  page.add_script_tag(path=str(ASSETS/'bf14300_original_quest_energy.js'))
  assert page.evaluate('BFOriginalGlobalQuestEnergyV14300.source.recordCount')==106
  assert page.evaluate('BFGrandGaiaCampaignV100.sourceEconomyReadiness()') is True
  economy_guard=page.evaluate("""() => {
    const api=BFGrandGaiaCampaignV100, q=QUESTS[QUESTS.length-1],
      save=localStorage.getItem('bf_global_offline_demo_v7'),
      progress=JSON.stringify(P), original=window.BFOriginalGlobalQuestEnergyV14300,
      fields=['requires','energy','exp','zel','karma'];
    const changes={};
    try {
      for(const field of fields){
        const old=q[field];
        try{
          q[field]=old+1;
          changes[field]=api.nextPlayable()===null &&
            api.sourceEconomyReadiness()===false;
        } finally {q[field]=old;}
      }
      window.BFOriginalGlobalQuestEnergyV14300={
        source:original.source,lookup:()=>{throw Error('source lookup broken')}};
      changes.exception=api.nextPlayable()===null;
      window.BFOriginalGlobalQuestEnergyV14300={
        source:{...original.source,sourceSha256:'changed'},lookup:original.lookup};
      changes.shaMismatch=api.nextPlayable()===null;
    } finally {window.BFOriginalGlobalQuestEnergyV14300=original;}
    return {changes,restored:api.sourceEconomyReadiness()===true&&
      api.nextPlayable()?.missionId===QUESTS[0].missionId,
      saveSame:localStorage.getItem('bf_global_offline_demo_v7')===save,
      progressSame:JSON.stringify(P)===progress};
  }""")
  assert economy_guard['changes']=={name:True for name in
    ('requires','energy','exp','zel','karma','exception','shaMismatch')},economy_guard
  assert economy_guard['restored'] and economy_guard['saveSame'] and economy_guard['progressSame']
  # A malformed later record must block selection of an otherwise valid first mission.
  # Restore the exact in-memory fixture without touching any persistent owner save.
  preflight=page.evaluate("""() => {
    const first=BFGrandGaiaCampaignV100.nextPlayable();
    const later=QUESTS[QUESTS.length-1].missionId;
    const original=P.questClears[later];
    try {
      P.questClears[later]=-1;
      const invalidLater=BFGrandGaiaCampaignV100.nextPlayable();
      P.questClears[later]=Number.NaN;
      const nonfiniteLater=BFGrandGaiaCampaignV100.nextPlayable();
      return {first,invalidLater,nonfiniteLater};
    } finally {
      if(original===undefined)delete P.questClears[later];
      else P.questClears[later]=original;
    }
  }""")
  assert preflight['first']['missionId']==initial_next['missionId']
  assert preflight['invalidLater'] is None and preflight['nonfiniteLater'] is None
  assert page.evaluate('BFGrandGaiaCampaignV100.nextPlayable().missionId')==initial_next['missionId']
  # Native Chromium: all 106 source wave counts are read-only metadata;
  # neither enemy formations nor native wave execution is certified.
  wave_report=page.evaluate("""() => {
    const api=BFGrandGaiaCampaignV100;
    const saved=localStorage.getItem('bf_global_offline_demo_v7');
    const player=JSON.stringify(P);
    const rows=QUESTS.map(q=>api.waveReadiness(q.missionId));
    const q=QUESTS[0],old=q.battles;
    let malformed;
    try{q.battles=0;malformed=api.waveReadiness(q.missionId);}
    finally{q.battles=old;}
    return {rows,malformed,unknown:api.waveReadiness(-1),
      playerSame:JSON.stringify(P)===player,
      saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
  }""")
  # Read-only source coverage must be explicit about native gameplay limits.
  expected_waves=sum(row[3] for row in pinned['records'])
  coverage=page.locator('#bf100-campaign .bf100-foot').text_content()
  assert f'106 missions · {expected_waves} wave counts' in coverage,coverage
  assert 'native multi-wave combat NOT verified' in coverage,coverage
  assert len(wave_report['rows'])==106
  assert all(row and row['verifiedWaveCount']>=1 and
             row['enemyFormationsVerified'] is False and
             row['dropsVerified'] is False and
             row['nativeMultiWaveEnabled'] is False
             for row in wave_report['rows'])
  assert wave_report['malformed'] is None and wave_report['unknown'] is None
  assert wave_report['playerSame'] and wave_report['saveSame']
  # Fail closed globally: corrupting an unrelated later mission must also
  # invalidate readiness for the first mission; duplicate IDs are ambiguous.
  corrupt=page.evaluate("""() => {
    const first=QUESTS[0],later=QUESTS[QUESTS.length-1],
      oldId=later.missionId,oldWaves=later.battles,
      progress=JSON.stringify(P),saved=localStorage.getItem('bf_global_offline_demo_v7');
    let duplicate,invalidLater;
    try {
      later.missionId=first.missionId;
      duplicate=BFGrandGaiaCampaignV100.waveReadiness(first.missionId);
      later.missionId=oldId;later.battles=0;
      invalidLater=BFGrandGaiaCampaignV100.waveReadiness(first.missionId);
    } finally {later.missionId=oldId;later.battles=oldWaves;}
    return {duplicate,invalidLater,
      restored:BFGrandGaiaCampaignV100.waveReadiness(first.missionId)!==null,
      playerSame:JSON.stringify(P)===progress,
      saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
  }""")
  assert corrupt=={'duplicate':None,'invalidLater':None,'restored':True,
                   'playerSame':True,'saveSame':True},corrupt
  # Even a plausible but incorrect count and a valid but wrong dungeon
  # must fail the source match for ALL missions, without saving anything.
  source_tamper=page.evaluate("""() => {
    const api=BFGrandGaiaCampaignV100,first=QUESTS[0],other=QUESTS[5],
      originalCount=other.battles,originalDungeon=other.dungeonId,
      originalPlayer=JSON.stringify(P),saved=localStorage.getItem('bf_global_offline_demo_v7');
    let alteredCount,alteredDungeon;
    try {
      other.battles=originalCount+1;
      alteredCount=api.waveReadiness(first.missionId);
      other.battles=originalCount;
      other.dungeonId=QUESTS[0].dungeonId;
      alteredDungeon=api.waveReadiness(first.missionId);
    } finally {other.battles=originalCount;other.dungeonId=originalDungeon;}
    return {alteredCount,alteredDungeon,
      restored:api.waveReadiness(first.missionId)?.verifiedWaveCount===first.battles,
      sourceYearUnchanged:JSON.stringify(P)===originalPlayer,
      saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
  }""")
  assert source_tamper=={'alteredCount':None,'alteredDungeon':None,'restored':True,
                         'sourceYearUnchanged':True,'saveSame':True},source_tamper
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
        const next=BFGrandGaiaCampaignV100.nextPlayable();
        if(i<QUESTS.length-1 && (!next || next.missionId!==QUESTS[i+1].missionId))
          return {error:'next playable mismatch',at:i,next};
        if(i===QUESTS.length-1 && next!==null)
          return {error:'completed campaign still playable',next};
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
  assert page.evaluate('BFGrandGaiaCampaignV100.nextPlayable()') is None
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
