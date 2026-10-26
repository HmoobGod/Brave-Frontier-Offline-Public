"""v53 original #50600 party DEF +50% scope, stronger buff non-stacking and save isolation."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf5300_source_party_def_item.js').read_text('utf8')
assert src.count('/* BF_GLOBAL_SOURCE_PARTY_DEF_ITEM_V5300 */')==1
assert len(src.encode('utf8'))<65536
assert all(x not in src for x in ('localStorage','saveProgress(', 'BFAndroid'))
ref=json.loads((R/'source_data/bf_global_2022_def_item_evidence_v4900.json').read_text('utf8'))
assert ref['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
items={x['itemId']:x for x in ref['items']}
assert items[50600]['passiveSkillInfo']=='0,0,50,0,0,3'
assert (items[50600]['battleEffectGroupId'],items[50600]['itemTargetArea'])==(410,2)
assert items[50601]['passiveSkillInfo']=='0,0,100,0,0,3'
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf5200_source_double_def_item.js")')<j.index('readPackagedText("bf5300_source_party_def_item.js")')
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
 'bf5300_source_party_def_item.js'):
  p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 ref=p.evaluate('BFGlobalSourcePartyDefV5300.source')
 assert (ref['itemId'],ref['itemTargetArea'],ref['battleEffectGroupId'])==(50600,2,410)
 assert (ref['passiveSkillInfo'],ref['defPercent'],ref['duration'])==('0,0,50,0,0,3',50,3)
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().remaining')==1
 p.evaluate('S.party[2].hp=0')
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 bases=p.evaluate('S.party.map(x=>x.def)')
 assert p.evaluate('BFGlobalSourceDefItemV4900.useDefItem(0,3)') is True
 assert p.evaluate('BFGlobalSourceDoubleDefV5200.useDoubleDef(1,4)') is True
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().eligibleRecipients')==[0,1,5]
 assert p.evaluate('BFGlobalSourcePartyDefV5300.usePartyDef(5)') is True
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().remaining')==0
 assert p.evaluate('S.party[0].def')==(bases[0]*150+50)//100
 assert p.evaluate('S.party[1].def')==(bases[1]*150+50)//100
 assert p.evaluate('S.party[2].def')==bases[2]
 assert p.evaluate('S.party[3].def')==(bases[3]*130+50)//100
 assert p.evaluate('S.party[4].def')==bases[4]*2
 assert p.evaluate('S.party[5].def')==(bases[5]*150+50)//100
 assert p.evaluate('BFGlobalSourceDefItemV4900.snapshot().eligibleRecipients.includes(5)') is False
 assert p.evaluate('BFGlobalSourceDoubleDefV5200.snapshot().eligibleRecipients.includes(5)') is False
 assert p.evaluate('S.party[5].action.kind')=='guard'
 p.evaluate('S.party[5].action=null')
 assert p.evaluate('BFGlobalSourceBBGaugeItemV4600.useBBItem(5,0)') is False
 assert p.evaluate('BFGlobalItemTurnReservationsV4500.free(5)') is False
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
    progress:JSON.stringify(P),clears:JSON.stringify(P.questClears),
    wave:S.wave,round:S.round})""")
 assert before==after,(before,after)
 p.evaluate('S.round=3')
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().activeBuffs.length')==3
 p.evaluate('S.round=4')
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().activeBuffs.length')==0
 assert p.evaluate('BFGlobalSourceDefItemV4900.snapshot().activeBuffs.length')==0
 assert p.evaluate('BFGlobalSourceDoubleDefV5200.snapshot().activeBuffs.length')==0
 assert p.evaluate('S.party.map(x=>x.def)')==bases
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().available') is False
 assert p.locator('#bf5300-def').is_hidden()
 p.locator('#mode').select_option('archive')
 assert p.evaluate('BFGlobalSourcePartyDefV5300.snapshot().remaining')==1
 p.add_script_tag(path=str(A/'bf5300_source_party_def_item.js'))
 assert p.locator('#bf5300-def').count()==1
 assert not errors,errors
 b.close()
print('PASS v53 2022 party DEF +50%, 3 rounds, stronger buffs isolated, save untouched')
