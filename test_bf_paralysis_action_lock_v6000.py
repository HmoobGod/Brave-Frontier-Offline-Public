"""v60 Paralysis action blocking and source-indexed cure on demo roster."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6000_paralysis_action_lock.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_PARALYSIS_ACTION_LOCK_V6000 */')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
data=json.loads((R/'source_data/bf_global_2022_status_cure_evidence_v5700.json').read_text('utf8'))
assert data['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
cures={x['itemId']:x['codes'] for x in data['cures']}
assert cures[20200]==[1] and cures[20210]==[2,3,4]
assert cures[20220]==[5] and cures[20230]==[6]
assert cures[50200]==[1,2,3,4,5,6]
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5600_source_life_potion.js")')<j.index('readPackagedText("bf6000_paralysis_action_lock.js")')
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
 'bf5900_curse_bb_lock.js','bf6000_paralysis_action_lock.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 st=p.evaluate('BFGlobalParalysisActionLockV6000.snapshot()')
 assert st['actionHooked'] is True and st['enemyHooked'] is True
 assert st['paralyzedSlots']==[]
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    hp:S.party.map(p=>p.hp),bb:S.party.map(p=>p.bb),
    enemies:S.enemies.map(e=>e.hp)})""")
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,6)') is True
 assert p.evaluate('BFGlobalParalysisActionLockV6000.paralyzed(0)') is True
 assert p.evaluate('BFGlobalParalysisActionLockV6000.canExecute(0)') is False
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.free(0)') is False
 assert p.evaluate('BFGlobalDemoPotionV4200.usePotion(0)') is False
 p.evaluate("""()=>{S.party[0].action={kind:'attack',target:0};}""")
 assert p.evaluate("""async ()=>{
    const before=S.enemies.map(e=>e.hp).join(',');
    await window.performUnit(S.party[0],-1);
    return S.enemies.map(e=>e.hp).join(',')===before;}""") is True
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[6]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.expireAfterTurn()')==[0]
 assert p.evaluate('BFGlobalParalysisActionLockV6000.canExecute(0)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,6)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(1,20230).removed')==[6]
 assert p.evaluate('BFGlobalParalysisActionLockV6000.canExecute(1)') is True
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    hp:S.party.map(p=>p.hp),bb:S.party.map(p=>p.bb),
    enemies:S.enemies.map(e=>e.hp)})""")
 assert before['save']==after['save'] and before['progress']==after['progress']
 assert before['clears']==after['clears'] and before['hp']==after['hp']
 assert before['bb']==after['bb'] and before['enemies']==after['enemies']
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,6)') is False
 assert p.evaluate('BFGlobalParalysisActionLockV6000.snapshot().paralyzedSlots')==[]
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalParalysisActionLockV6000.snapshot().paralyzedSlots')==[]
 p.add_script_tag(path=str(A/'bf6000_paralysis_action_lock.js'))
 assert p.evaluate('BFGlobalParalysisActionLockV6000.snapshot().actionHooked') is True
 assert not errors,errors
 b.close()
print('PASS v60 source Paralysis skips action, blocks item actors, 3-turn expiry, cure, v7 save integrity')
