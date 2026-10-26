"""v61 Weakness DEF effect in native DEMO enemy phase and status expiry."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf6100_weakness_defense.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_WEAKNESS_DEFENSE_V6100 */')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
data=json.loads((R/'source_data/bf_global_2022_status_cure_evidence_v5700.json').read_text('utf8'))
assert data['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
cures={x['itemId']:x['codes'] for x in data['cures']}
assert cures[20200]==[1] and cures[20210]==[2,3,4]
assert cures[20220]==[5] and cures[20230]==[6]
assert cures[50200]==[1,2,3,4,5,6]
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6000_paralysis_action_lock.js")')<j.index('readPackagedText("bf6100_weakness_defense.js")')
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
 'bf6100_weakness_defense.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 st=p.evaluate('BFGlobalWeaknessDefenseV6100.snapshot()')
 assert st['enemyHooked'] is True and st['weakenedSlots']==[]
 assert st['source']['statusCode']==2
 assert st['source']['penaltyPercent']==50
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
  hp:S.party.map(x=>x.hp),bb:S.party.map(x=>x.bb),
  atk:S.party.map(x=>x.atk),def:S.party.map(x=>x.def),
  enemies:S.enemies.map(x=>x.hp)})""")
 original=p.evaluate('S.party.map(x=>x.def)')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,2)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2]
 original_token=p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,2)')
 assert type(original_token) is int
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.weakened(0)') is True
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(0)')==(original[0]+1)//2
 # A separate living unit's DEF is untouched while Weakness is being applied.
 during=p.evaluate("""async ()=>{
   return BFGlobalWeaknessDefenseV6100.withWeaknessDefense(async ()=>({
     unit0:S.party[0].def,unit1:S.party[1].def
   }));}""")
 assert during['unit0']==(original[0]+1)//2
 assert during['unit1']==original[1]
 assert p.evaluate('S.party.map(x=>x.def)')==original
 # Exception paths must not leave temporary reduced DEF in the live roster.
 assert p.evaluate("""async ()=>{
   try{await BFGlobalWeaknessDefenseV6100.withWeaknessDefense(async ()=>{
     if(S.party[0].def===0)throw Error('zero DEF unexpected');
     throw Error('forced test abort');});
   }catch(e){return e.message==='forced test abort'}
   return false;
 }""") is True
 assert p.evaluate('S.party.map(x=>x.def)')==original
 # Existing original DEF-item effects must be restored exactly.
 assert p.evaluate('BFGlobalSourceDefItemV4900.useDefItem(1,3)') is True
 buffed=p.evaluate('S.party[3].def')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,2)') is True
 during=p.evaluate("""async ()=>BFGlobalWeaknessDefenseV6100.withWeaknessDefense(
   async ()=>S.party[3].def)""")
 # Original weakness -50% stacks subtractively with v49's +30% DEF.
 assert during==int(original[3]*.8+0.5)
 assert p.evaluate('S.party[3].def')==buffed
 # Source cure #20210 must remove only ailment codes 2-4.
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[2]
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.weakened(3)') is False
 assert p.evaluate('S.party[3].def')==buffed
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,4)') is True
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2,4]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2,4]
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.expireAfterTurn()')==[0]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,2)') is None
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.effectiveDefense(0)')==original[0]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20210).removed')==[4]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,2)') is True
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.tokenFor(0,2)')!=original_token
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.expireAfterTurn()')==[]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.codesFor(0)')==[2]
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20210).removed')==[2]
 # Existing DEF temporary item still has its independent expiry and exact base.
 p.evaluate('S.round++')
 assert p.evaluate('BFGlobalSourceDefItemV4900.snapshot().activeBuffs.length')==0
 assert p.evaluate('S.party.map(x=>x.def)')==original
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
  progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
  hp:S.party.map(x=>x.hp),bb:S.party.map(x=>x.bb),
  atk:S.party.map(x=>x.atk),def:S.party.map(x=>x.def),
  enemies:S.enemies.map(x=>x.hp)})""")
 assert before==after,(before,after)
 # KO and mode changes forbid status application; reset restores empty registry.
 p.evaluate('S.party[2].hp=0')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,2)') is False
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,2)') is False
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.snapshot().weakenedSlots')==[]
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalWeaknessDefenseV6100.snapshot().weakenedSlots')==[]
 p.evaluate('window.__bf61prior=window.enemyPhase')
 p.add_script_tag(path=str(A/'bf6100_weakness_defense.js'))
 assert p.evaluate('window.__bf61prior===window.enemyPhase') is True
 assert not errors,errors
 b.close()
print('PASS v61 Weakness -50% DEF only during enemy phase, restores buffs, expiry, cure, no saved mutation')
