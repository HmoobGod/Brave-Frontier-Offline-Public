"""v62 Injury ATK penalty during DEMO player action, status isolation and save integrity."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6200_injury_attack.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_INJURY_ATTACK_V6200 */')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
data=json.loads((R/'source_data/bf_global_2022_status_cure_evidence_v5700.json').read_text('utf8'))
assert data['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
cures={x['itemId']:x['codes'] for x in data['cures']}
assert cures[20200]==[1] and cures[20210]==[2,3,4]
assert cures[20220]==[5] and cures[20230]==[6]
assert cures[50200]==[1,2,3,4,5,6]
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6100_weakness_defense.js")')<j.index('readPackagedText("bf6200_injury_attack.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
 'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
 'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
 'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
 'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
 'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js',
 'bf3000_battle_results.js','bf3100_battle_focus.js','bf3200_combat_journal.js',
 'bf3300_story_playback.js','bf3400_source_scene_placement.js',
 'bf3500_dialogue_timeline.js','bf3600_event_composite.js',
 'bf3700_cinematic_reader.js','bf3800_source_battle_backdrop.js',
 'bf3900_story_battle_handoff.js','bf4000_next_chapter_intro.js',
 'bf4100_live_quest_banner.js','bf4500_item_turn_reservations.js',
 'bf4200_demo_potion_command.js','bf4300_source_party_heal.js',
 'bf4400_source_atk_item.js','bf4600_source_bb_gauge_item.js',
 'bf4700_source_full_revive.js','bf4800_demo_auto_item_guard.js',
 'bf4900_source_def_item.js','bf5000_source_party_atk_item.js',
 'bf5100_source_double_atk_item.js','bf5200_source_double_def_item.js',
 'bf5300_source_party_def_item.js','bf5400_source_hope_light.js',
 'bf5500_source_strong_life.js','bf5600_source_life_potion.js',
 'bf5700_original_ailment_state.js','bf5800_poison_turn.js',
 'bf5900_curse_bb_lock.js','bf6000_paralysis_action_lock.js',
 'bf6100_weakness_defense.js','bf6200_injury_attack.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 st=p.evaluate('BFGlobalInjuryAttackV6200.snapshot()')
 assert st['performHooked'] and st['enemyHooked']
 assert st['source']['statusCode']==4 and st['source']['penaltyPercent']==50
 assert st['injuredSlots']==[]
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
  hp:S.party.map(x=>x.hp),atk:S.party.map(x=>x.atk),def:S.party.map(x=>x.def)})""")
 base=p.evaluate('S.party.map(x=>x.atk)')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)') is True
 token=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,4)')
 assert type(token) is int
 assert p.evaluate('BFGlobalInjuryAttackV6200.injured(0)') is True
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(0)')==(base[0]+1)//2
 result=p.evaluate("""async()=>BFGlobalInjuryAttackV6200.withInjuryAttack(0,
   async()=>({injured:S.party[0].atk,other:S.party[1].atk}))""")
 assert result=={'injured':(base[0]+1)//2,'other':base[1]}
 assert p.evaluate('S.party.map(x=>x.atk)')==base
 assert p.evaluate("""async()=>{
   try{await BFGlobalInjuryAttackV6200.withInjuryAttack(0,async()=>{
     throw Error('injury-probe-abort')})}catch(e){return e.message==='injury-probe-abort'}
   return false
 }""") is True
 assert p.evaluate('S.party.map(x=>x.atk)')==base
 # Stronger ATK item remains owned by the prior implementation; injury
 # temporarily affects the current action, not the permanent unit base.
 assert p.evaluate('BFGlobalSourceDoubleAtkV5100.useDoubleAtk(1,3)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,4)') is True
 during=p.evaluate("""async()=>BFGlobalInjuryAttackV6200.withInjuryAttack(3,
   async()=>effectivePlayerAtk(S.party[3]))""")
 # Original -50% Injury stacks subtractively with positive +100% ATK:
 # effective = (1 + 100% - 50%) x unbuffed ATK, not 2 x half ATK.
 assert during==int(base[3]*1.5+0.5)
 assert p.evaluate('S.party[3].atk')==base[3]
 assert p.evaluate('effectivePlayerAtk(S.party[3])')==base[3]*2
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[4]
 assert p.evaluate('BFGlobalInjuryAttackV6200.injured(3)') is False
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,2)') is True
 assert p.evaluate('BFGlobalInjuryAttackV6200.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalInjuryAttackV6200.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2,4]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalInjuryAttackV6200.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalInjuryAttackV6200.expireAfterTurn()')==[0]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2]
 assert p.evaluate('BFGlobalInjuryAttackV6200.effectiveAttack(0)')==base[0]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,4)')!=token
 assert p.evaluate('BFGlobalInjuryAttackV6200.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2,4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20210).removed')==[2,4]
 assert p.evaluate('BFGlobalInjuryAttackV6200.injured(0)') is False
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
  hp:S.party.map(x=>x.hp),atk:S.party.map(x=>x.atk),def:S.party.map(x=>x.def)})""")
 assert before==after,(before,after)
 p.evaluate('S.party[2].hp=0')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,4)') is False
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)') is False
 assert p.evaluate('BFGlobalInjuryAttackV6200.snapshot().injuredSlots')==[]
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalInjuryAttackV6200.snapshot().injuredSlots')==[]
 p.evaluate('()=>{window.__bf62prior=window.performUnit;return true}')
 p.add_script_tag(path=str(A/'bf6200_injury_attack.js'))
 assert p.evaluate('window.__bf62prior===window.performUnit') is True
 assert not errors,errors
 b.close()
print('PASS v62 Injury -50% ATK action-only, buff preserved, separate status expiry, exact stat/save restoration')
