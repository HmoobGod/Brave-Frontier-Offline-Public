"""v170: personal offline Gem payouts are opt-in, source-gated, and canonical v7."""
import json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
s=(A/'index.html').read_text('utf8')
manifest=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
gate=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
assert manifest['total']==106 and len(manifest['records'])==106
assert gate['currentPlayableFinales']==22
assert s.count('BF_GLOBAL_GEMS_PERSONAL_V17000')==1
assert s.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert 'bf170ApplyQuestReward(previousQuestClearCount,QUEST.missionId)' in s
assert 'bf_global_offline_demo_v7' in s
assert 'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING' in s
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
 p.evaluate("""()=>{const db={};
  window.__gemDB=db;window.__gemWrites=[];window.__gemQuota=false;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,
   setItem:(k,v)=>{if(window.__gemQuota)throw Error('disk full');
     window.__gemWrites.push(k);db[k]=String(v)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}
  }});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(s,wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf17000_personal_gem_rewards_ui.js'))
 assert p.locator('#bf17000-gem-rewards').count()==1
 assert 'Gem balance: 0' in p.locator('#bf17000-gem-rewards p').first.text_content()
 assert p.evaluate('P.version')==7
 assert p.evaluate('QUESTS.length')==106
 assert p.evaluate('BF170_QUEST_IDS.length')==106
 assert p.evaluate('BF160_ORIGINAL_GEM_FINAL_IDS.length')==22
 assert p.evaluate('window.BFGlobalCustomGemsV17000.snapshot().mode')=='original'
 assert p.evaluate('P._bfGemV170Custom.balance')==0
 assert p.evaluate('window.BFGlobalCustomGemsV17000.claimDaily()') is False
 # Original reward mode continues existing 2022 first-clear evidence, no wallet.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==0
 assert p.evaluate('P._bfGemV161Pending')==[12]
 assert p.evaluate('P._bfGemV170Custom.legacyClears')==[12]
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is True
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is False
 assert p.evaluate('BFGlobalCustomGemsV17000.claimDaily()') is True
 assert p.evaluate('BFGlobalCustomGemsV17000.claimDaily()') is False
 assert p.evaluate('P._bfGemV170Custom.balance')==1100
 assert p.evaluate('P._bfGemV170Custom.dailyClaims')==1
 # First regular quest receives 25 and repeat receives exactly 1 per run.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===10);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1125
 # Claude F5/F10: actual in-browser Gem panel follows the successful save.
 assert 'Gem balance: 1,125' in p.locator('#bf17000-gem-rewards p').first.text_content()
 p.evaluate('awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1126
 assert p.evaluate('P._bfGemV170Custom.firstPaid')==[10]
 # A source-authenticated live dungeon finale receives 100 first, 1 replay.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===23);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1226
 assert p.evaluate('P._bfGemV161Pending')==[12,23]
 p.evaluate('awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1227
 assert p.evaluate('P._bfGemV170Custom.replaysPaid')==2
 assert p.evaluate('P._bfGemV170Custom.firstPaid')==[10,23]
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV170Custom.balance")==1227
 assert p.evaluate('P._bfGemV160.balance')==0
 # Previously completed owner v124 quests are quarantined; subsequent
 # replay gives one Gem but never a mistaken first-clear bonus.
 p.evaluate("""()=>{const old=JSON.parse(JSON.stringify(P));
   old.questClears={'12':2,'23':1,'10':4};delete old._bfGemV170Custom;
   delete old._bfGemV160;delete old._bfGemV161Pending;
   window.__oldOwnerV124=old;P=parseProgress(old);
 }""")
 assert p.evaluate('P._bfGemV170Custom.balance')==0
 assert p.evaluate('P._bfGemV170Custom.legacyClears')==[10,12,23]
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===23);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1
 assert p.evaluate('P._bfGemV170Custom.firstPaid')==[]
 # No custom rewards for archived but non-playable Amdahl missions.
 assert p.evaluate('bf170ApplyQuestReward(0,404)') is False
 assert p.evaluate('P._bfGemV170Custom.balance')==1
 # Corrupt / fabricated balance must fail parser closed.
 for x in ('balance','firstPaid','dailyClaims','legacyClears'):
  assert p.evaluate("""field=>{const bad=JSON.parse(JSON.stringify(P));
   bad._bfGemV170Custom[field]=field==='balance'?999999:
      field==='dailyClaims'?-1:field==='firstPaid'?[404]:[404];
   try{parseProgress(bad);return false}catch(_){return true}
  }""",x),x
 before=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.evaluate('window.__gemQuota=true')
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is False
 assert p.evaluate('P._bfGemV170Custom.balance')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before
 p.evaluate('window.__gemQuota=false')
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is True
 assert p.evaluate('P._bfGemV170Custom.balance')==1001
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("original")') is True
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===33);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==1001
 assert p.evaluate('P._bfGemV170Custom.legacyClears')==[10,12,23,33]
 # Claude F6: first-clear memory may advance under quota failure, but
 # neither the quest nor its 25 Gems is persisted. After restoring the last
 # committed canonical save, a new successful first clear earns 25, not 1.
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
 saved=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 initial=p.evaluate('P._bfGemV170Custom.balance')
 p.evaluate('window.__gemQuota=true;QUEST=QUESTS.find(q=>q.missionId===11);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==initial+25
 assert p.evaluate('P.questClears[11]')==1
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==saved
 assert ('Gem balance: '+format(initial,',')) in p.locator('#bf17000-gem-rewards p').first.text_content()
 p.evaluate("raw=>{window.__gemQuota=false;P=parseProgress(JSON.parse(raw));}",saved)
 assert p.evaluate('P.questClears[11]||0')==0
 assert p.evaluate('P._bfGemV170Custom.balance')==initial
 p.evaluate('awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.balance')==initial+25
 assert p.evaluate('P._bfGemV170Custom.replaysPaid')==1
 assert ('Gem balance: '+format(initial+25,',')) in p.locator('#bf17000-gem-rewards p').first.text_content()
 # Claude F7: exact Gregorian dates only; no Feb 31 or non-leap Feb 29.
 for bad_date in ('2025-02-31','2025-02-29','2026-11-31'):
  assert p.evaluate('''s=>{const data=JSON.parse(JSON.stringify(P));
    data._bfGemV170Custom.lastDailyDate=s;
    try{parseProgress(data);return false;}catch(_){return true}
  }''',bad_date)
 assert p.evaluate('''()=>{const data=JSON.parse(JSON.stringify(P));
  data._bfGemV170Custom.lastDailyDate='2028-02-29';
  return parseProgress(data)._bfGemV170Custom.lastDailyDate;
 }''')== '2028-02-29'
 assert set(p.evaluate('window.__gemWrites'))=={'bf_global_offline_demo_v7'}
 assert not errs,errs
 b.close()
print('PASS v170: authentic 106 quests, 22 finales; 25/100 first clears, 1/replay, welcome 1000, daily 100, v124 migration, atomic canonical v7 and original mode')
