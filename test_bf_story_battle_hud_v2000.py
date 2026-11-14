"""v20.00 real playable quest HUD, source stages, post-victory next-mission and save safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
src=(A/'bf2000_story_battle_hud.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_STORY_BATTLE_HUD_V2000 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and src.count('saveProgress();')==1
assert java.index('readPackagedText("bf110_quest_journal.js")')<java.index('readPackagedText("bf2000_story_battle_hud.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf2000_story_battle_hud.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf2000-run').is_visible()
 s=page.evaluate('BFGlobalStoryBattleV2000.snapshot()')
 assert s['missionId']==1 and s['archive'] and s['total']==3,s
 assert s['current']==1 and s['completed']==0 and s['nextId'] is None,s
 assert 'DEMO' in page.locator('#bf2000-foot').inner_text()
 assert page.locator('#bf2000-waves span').count()==3
 # v426: the live HUD reports only verified in-memory DEMO foe HP totals.
 # No battle action, original 2022 formation inference or v7 save writes.
 hp_probe=page.evaluate("""() => {
  const prior=S.enemies,oldP=JSON.stringify(P),oldS=JSON.stringify(S);
  const oldSave=localStorage.getItem('bf_global_offline_demo_v7');
  const result={};
  try {
    S.enemies=[{slot:0,hp:42,maxHp:100},{slot:1,hp:12,maxHp:40}];
    let state=BFGlobalStoryBattleV2000.refresh();
    result.first=[state.enemyHp,state.enemyMaxHp];
    result.firstLabel=document.getElementById('bf2000-state').textContent;
    S.enemies[1].hp=0;
    state=BFGlobalStoryBattleV2000.refresh();
    result.afterKo=[state.enemyHp,state.enemyMaxHp];
    S.enemies[0].maxHp=0;
    state=BFGlobalStoryBattleV2000.refresh();
    result.invalid=[state.enemyHp,state.enemyMaxHp];
    result.invalidLabel=document.getElementById('bf2000-state').textContent;
    S.enemies[0].maxHp=100;S.enemies[0].hp=NaN;
    state=BFGlobalStoryBattleV2000.refresh();
    result.nonFinite=[state.enemyHp,state.enemyMaxHp];
  } finally {
    S.enemies=prior;
    BFGlobalStoryBattleV2000.refresh();
  }
  result.unchanged=JSON.stringify(P)===oldP&&JSON.stringify(S)===oldS&&
    localStorage.getItem('bf_global_offline_demo_v7')===oldSave;
  return result;
 }""")
 assert hp_probe['first']==[54,140],hp_probe
 assert 'DEMO enemy HP 54/140' in hp_probe['firstLabel'],hp_probe
 assert hp_probe['afterKo']==[42,140],hp_probe
 assert hp_probe['invalid']==[None,None] and 'DEMO enemy HP unavailable' in hp_probe['invalidLabel'],hp_probe
 assert hp_probe['nonFinite']==[None,None] and hp_probe['unchanged'],hp_probe
 # v440: the player-facing HUD reports ALL verified live DEMO ally HP.
 # Invalid/partial active ally data cannot be represented as a false total.
 ally_probe=page.evaluate("""()=>{
   const beforeParty=S.party, beforeS=JSON.stringify(S), beforeP=JSON.stringify(P),
      beforeSave=localStorage.getItem('bf_global_offline_demo_v7'),
      api=BFGlobalStoryBattleV2000,result={};
   try{
     S.party=[{id:0,active:true,hp:50,maxHp:100},
              {id:1,active:true,hp:20,maxHp:40}];
     let state=api.refresh();
     result.valid=[state.allyHp,state.allyMaxHp];
     result.validText=document.getElementById('bf2000-state').textContent;
     S.party[1].hp=0;state=api.refresh();
     result.ko=[state.allyHp,state.allyMaxHp];
     S.party[0].hp=NaN;state=api.refresh();
     result.nan=[state.allyHp,state.allyMaxHp];
     result.nanText=document.getElementById('bf2000-state').textContent;
     S.party[0].hp=50;S.party[1].maxHp=0;
     state=api.refresh();result.zeroMax=[state.allyHp,state.allyMaxHp];
     S.party[1].maxHp=40;S.party[1].hp=41;
     state=api.refresh();result.overMax=[state.allyHp,state.allyMaxHp];
     S.party=[{id:0,active:false,hp:1,maxHp:20}];
     state=api.refresh();result.noActive=[state.allyHp,state.allyMaxHp];
   }finally{S.party=beforeParty;api.refresh();}
   result.unchanged=JSON.stringify(S)===beforeS&&JSON.stringify(P)===beforeP&&
     localStorage.getItem('bf_global_offline_demo_v7')===beforeSave;
   return result;
 }""")
 assert ally_probe['valid']==[70,140] and 'DEMO ally HP 70/140' in ally_probe['validText'],ally_probe
 assert ally_probe['ko']==[50,140],ally_probe
 for key in ('nan','zeroMax','overMax','noActive'):
  assert ally_probe[key]==[None,None],(key,ally_probe)
 assert 'DEMO ally HP unavailable' in ally_probe['nanText'],ally_probe
 assert ally_probe['unchanged'],ally_probe
 for width in (320,390,540):
  page.set_viewport_size({'width':width,'height':844})
  for selector in ('#bf2000-battle','#bf2000-next','#bf2000-retry-save'):
   assert page.locator(selector).evaluate('(e)=>e.getBoundingClientRect().height')>=44,(width,selector)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size({'width':390,'height':844})
 # v359: direct real core execute() next-wave and final-reward gates.
 # No mocks of the native engine; only disposable source-provider corruption.
 page.add_script_tag(path=str(A/'bf14300_original_quest_energy.js'))
 wave_guard=page.evaluate("""async()=>{
   const provider=window.BFOriginalGlobalQuestEnergyV14300,
     player=JSON.stringify(P),save=localStorage.getItem('bf_global_offline_demo_v7'),
     originalMode=document.getElementById('mode').value,
     result={};
   const mismatched=id=>{
     const row=[...provider.lookup(id)];row[3]+=1;return row;
   };
   const emptyWave=()=>{for(const e of S.enemies)e.hp=0;
     for(const p of liveParty())p.action={kind:'guard',target:0};};
   try{
     // v360: corrupt source before combat must disarm player Auto and leave
     // full-health enemies, player HP, wave, round, and save untouched.
     reset();window.BFOriginalGlobalQuestEnergyV14300={
       source:provider.source,lookup:mismatched};
     const enemiesBefore=JSON.stringify(S.enemies.map(e=>e.hp)),
       partyBefore=JSON.stringify(S.party.map(p=>p.hp));
     for(const p of liveParty())p.action={kind:'guard',target:0};
     S.auto=true;E.auto.checked=true;
     await execute();
     result.precombatBlocked=S.wave===0&&S.round===1&&!S.over&&!S.busy&&
       !S.auto&&!E.auto.checked&&
       JSON.stringify(S.enemies.map(e=>e.hp))===enemiesBefore&&
       JSON.stringify(S.party.map(p=>p.hp))===partyBefore&&
       S.party.every(p=>p.action===null);
     // The post-attack v359 gate must still work if source changes AFTER
     // precombat validation, rather than merely passing this new early gate.
     reset();let midLookups=0;
     window.BFOriginalGlobalQuestEnergyV14300={
       source:provider.source,
       lookup:id=>++midLookups===1?provider.lookup(id):mismatched(id)};
     emptyWave();await execute();
     result.midBlocked=S.wave===0&&!S.over&&!S.busy&&!S.auto&&midLookups>=2;
     // A source with a forged header must fail even when its row is correct.
     reset();window.BFOriginalGlobalQuestEnergyV14300={
       source:{...provider.source,sourceSha256:'0'.repeat(64)},
       lookup:id=>provider.lookup(id)};
     emptyWave();await execute();
     result.forgedHeaderBlocked=S.wave===0&&!S.over&&!S.busy&&!S.auto;
     // A throwing source lookup must also stop before a final-wave clear.
     reset();S.wave=S.totalWaves-1;let throwLookups=0;
     window.BFOriginalGlobalQuestEnergyV14300={
       source:provider.source,
       lookup:id=>{if(++throwLookups>1)throw Error('synthetic source fault');
         return provider.lookup(id)}};
     emptyWave();await execute();
     result.throwingFinalBlocked=!S.over&&!S.busy&&throwLookups>=2&&
       (P.questClears?.[QUEST.missionId]||0)===0;
     reset();S.wave=S.totalWaves-1;let finalLookups=0;
     window.BFOriginalGlobalQuestEnergyV14300={
       source:provider.source,
       lookup:id=>++finalLookups===1?provider.lookup(id):mismatched(id)};
     emptyWave();await execute();
     result.finalBlocked=!S.over&&!S.busy&&finalLookups>=2&&
       (P.questClears?.[QUEST.missionId]||0)===0;
     window.BFOriginalGlobalQuestEnergyV14300=provider;
     reset();emptyWave();await execute();
     result.goodAdvance=S.wave===1&&S.totalWaves===3&&!S.over;
     document.getElementById('mode').value='training';
     reset();window.BFOriginalGlobalQuestEnergyV14300={
       source:provider.source,lookup:()=>{throw Error('synthetic source fault')}};
     emptyWave();await execute();
     result.trainingUnchanged=S.mode==='training'&&S.wave===1&&!S.over;
     result.playerSame=JSON.stringify(P)===player;
     result.saveSame=localStorage.getItem('bf_global_offline_demo_v7')===save;
     return result;
   }finally{
     window.BFOriginalGlobalQuestEnergyV14300=provider;
     document.getElementById('mode').value=originalMode;
     reset();BFGlobalStoryBattleV2000.refresh();
   }
 }""")
 assert wave_guard=={'precombatBlocked':True,'midBlocked':True,'finalBlocked':True,
   'forgedHeaderBlocked':True,'throwingFinalBlocked':True,
   'goodAdvance':True,'trainingUnchanged':True,'playerSame':True,
   'saveSame':True},wave_guard
 assert page.locator('#bf2000-next').is_disabled()
 before=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('()=>{S.wave=1;BFGlobalStoryBattleV2000.refresh()}')
 assert page.evaluate('BFGlobalStoryBattleV2000.snapshot().current')==2
 assert page.locator('#bf2000-waves span[data-completed="true"]').count()==1
 page.evaluate('()=>{S.wave=0;BFGlobalStoryBattleV2000.refresh()}')
 after=page.evaluate("""()=>({p:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Passive quest HUD must not touch persisted progress'
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 # Actual reward handler is reused. Bypassing combat here is a smoke fixture, not a
 # measured full-play victory; full native demo combat has separate regression gates.
 # Exercise a real core victory with a synthetic canonical-v7 quota error.
 # No separate save format or mocked reward engine: only setItem is denied.
 persisted=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 page.evaluate("""()=>{window.__hudOldSet=localStorage.setItem.bind(localStorage);
   window.__hudDenySave=true;
   localStorage.setItem=(key,value)=>{
     if(__hudDenySave&&key==='bf_global_offline_demo_v7')
       throw new DOMException('Synthetic storage quota','QuotaExceededError');
     return __hudOldSet(key,value);
   };
   finish(true);S.over=true;S.phase='Victory';
   BFGlobalStoryBattleV2000.refresh();
 }""")
 unsaved=page.evaluate('BFGlobalStoryBattleV2000.snapshot()')
 assert unsaved['won'] and unsaved['clears']>=1 and not unsaved['stored'],unsaved
 assert unsaved['nextId'] is None,unsaved
 assert page.locator('#bf2000-next').is_disabled()
 assert 'SAVE REQUIRED' in page.locator('#bf2000-state').inner_text()
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 assert page.evaluate('QUEST.missionId')==1
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==persisted
 # The player must explicitly retry; failed retries never unlock Next.
 assert page.locator('#bf2000-retry-save').is_visible()
 page.locator('#bf2000-retry-save').click()
 assert page.locator('#bf2000-next').is_disabled()
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==persisted
 page.evaluate('()=>{__hudDenySave=false}')
 page.locator('#bf2000-retry-save').click()
 assert page.locator('#bf2000-retry-save').is_hidden()
 s=page.evaluate('BFGlobalStoryBattleV2000.refresh()')
 assert s['won'] and s['stored'] and s['clears']>=1 and s['nextId']==2,s
 # v331: v3000 loads AFTER this HUD on the real Android page. Its read-only
 # canonical receipt gate must disable the HUD's separate Next button even
 # when saveEnabled is stale/true. This isolated v20 page injects that API.
 receipt=page.evaluate("""()=>{
   const prior=window.BFGlobalBattleResultsV3000,
         before=JSON.stringify(P),
         saved=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     window.BFGlobalBattleResultsV3000={
       committedClearCount:()=>0
     };
     const stale=BFGlobalStoryBattleV2000.refresh();
     const staleBlocked=!stale.stored&&stale.nextId===null&&
       !BFGlobalStoryBattleV2000.advance()&&
       document.getElementById('bf2000-next').disabled;
     window.BFGlobalBattleResultsV3000={
       committedClearCount:()=>{throw Error('synthetic receipt failure')}
     };
     const throwsBlocked=!BFGlobalStoryBattleV2000.refresh().stored&&
       !BFGlobalStoryBattleV2000.advance();
     window.BFGlobalBattleResultsV3000={
       committedClearCount:id=>P.questClears[id]
     };
     const restored=BFGlobalStoryBattleV2000.refresh();
     const valid=restored.stored&&restored.nextId===2&&
       !document.getElementById('bf2000-next').disabled;
     return {staleBlocked,throwsBlocked,valid,
       playerSame:JSON.stringify(P)===before,
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved,
       mission:QUEST.missionId};
   }finally{
     if(prior===undefined)delete window.BFGlobalBattleResultsV3000;
     else window.BFGlobalBattleResultsV3000=prior;
     BFGlobalStoryBattleV2000.refresh();
   }
 }""")
 assert receipt=={'staleBlocked':True,'throwsBlocked':True,'valid':True,
                 'playerSame':True,'saveSame':True,'mission':1},receipt
 # The battle HUD and results must use the NEW campaign-wide source order.
 # An already cleared later selection must not skip an earlier open mission,
 # even if the older local slice would have pointed after that later stage.
 ledger=page.evaluate("""()=>{const current=QUEST,high=QUESTS.find(q=>q.missionId===10);
   const old=P.questClears[10],lastId=QUESTS[QUESTS.length-1].missionId;
   const last=P.questClears[lastId];
   try{
     QUEST=high;P.questClears[10]=1;
     const global=BFGrandGaiaCampaignV100.nextPlayable();
     const same=BFGlobalStoryBattleV2000.snapshot().nextId;
     P.questClears[lastId]=-1;
     const corruptCampaign=BFGrandGaiaCampaignV100.nextPlayable();
     const corruptHUD=BFGlobalStoryBattleV2000.snapshot().nextId;
     return {global:global?.missionId,same,corruptCampaign,corruptHUD};
   }finally{
     QUEST=current;
     if(old===undefined)delete P.questClears[10];
     else P.questClears[10]=old;
     if(last===undefined)delete P.questClears[lastId];
     else P.questClears[lastId]=last;
   }
 }""")
 assert ledger=={'global':2,'same':2,'corruptCampaign':None,'corruptHUD':None},ledger
 assert page.evaluate('BFGlobalStoryBattleV2000.refresh().nextId')==2
 assert page.locator('#bf2000-next').is_enabled()
 assert page.locator('#bf2000-waves span[data-completed="true"]').count()==3
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 page.evaluate('S.busy=false')
 page.locator('#bf2000-next').click()
 assert page.evaluate('QUEST.missionId')==2
 assert page.evaluate('P.questClears[1]')>=1
 assert page.evaluate('P.version')==7
 assert page.evaluate('JSON.parse(localStorage.getItem("bf_global_offline_demo_v7")).version')==7
 assert page.evaluate('BFGlobalStoryBattleV2000.snapshot().total')==page.evaluate('QUEST.battles')
 page.locator('#mode').select_option('training')
 assert page.evaluate('BFGlobalStoryBattleV2000.refresh().archive') is False
 assert 'training mode' in page.locator('#bf2000-details').inner_text()
 assert page.evaluate('BFGlobalStoryBattleV2000.advance()') is False
 assert not errors,errors
 browser.close()
print('PASS v20.00: actual quest battle wave HUD, 2022 archive labels, live state, victory advance, training isolation, save v7')
