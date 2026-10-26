"""v63 Poison, Curse, Paralysis duration restarts after selective cure and reinfliction."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf5800_poison_turn.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_POISON_TURN_V5800 */')==1
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
 core=p.evaluate('BFGlobalOriginalAilmentStateV5700')
 assert p.evaluate('typeof BFGlobalOriginalAilmentStateV5700.tokenFor')=='function'
 assert p.evaluate('typeof BFGlobalOriginalAilmentStateV5700.removeCode')=='function'
 for name in ('bf5800_poison_turn.js','bf5900_curse_bb_lock.js',
              'bf6000_paralysis_action_lock.js'):
  content=(A/name).read_text('utf8')
  assert 'tokenFor(slot,' in content
  assert 'removeCode(slot,' in content
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears)})""")
 original=p.evaluate('S.party[0].hp')
 amount=p.evaluate('Math.max(1,Math.floor(S.party[0].maxHp/10))')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is True
 first=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,1)')
 assert p.evaluate('BFGlobalPoisonTurnV5800.processPoisonTurn()[0].round')==1
 assert p.evaluate('S.party[0].hp')==original-amount
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20200).removed')==[1]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,1)')!=first
 # Same actor must never take poison damage twice in a single round.
 assert p.evaluate('BFGlobalPoisonTurnV5800.processPoisonTurn()')==[]
 assert p.evaluate('S.party[0].hp')==original-amount
 for round_num in (2,3,4):
  p.evaluate('S.round++')
  tick=p.evaluate('BFGlobalPoisonTurnV5800.processPoisonTurn()')
  assert tick and tick[0]['round']==round_num
  assert p.evaluate('S.party[0].hp')==original-amount*(round_num)
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[]
 # After natural expiry, another Poison infliction in this same round must
 # not cause a fourth poison tick; historical tick provenance survives cure.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is True
 assert p.evaluate('BFGlobalPoisonTurnV5800.processPoisonTurn()')==[]
 assert p.evaluate('S.party[0].hp')==original-4*amount
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20200).removed')==[1]
 # Curse newly inflicted on same unit after an early cure must not inherit age.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,5)') is True
 old=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(1,5)')
 assert p.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(1,20220).removed')==[5]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,5)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(1,5)')!=old
 assert p.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(1)')==[5]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[1]
 # Paralysis must also receive a new 3-observed-round lifetime on reinflict.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,6)') is True
 old=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(2,6)')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(2,20230).removed')==[6]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,6)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(2,6)')!=old
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(2)')==[6]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[2]
 # A real source-item cure continues to remove all three Weakness/Sickness/Injury.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,2)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,3)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,4)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[2,3,4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(3)')==[]
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.snapshot().units')==[]
 assert not errors,errors
 b.close()
print('PASS v63 cure-reinflict resumes 3-turn poison/curse/paralysis, no double tick, preserve other codes and save')
