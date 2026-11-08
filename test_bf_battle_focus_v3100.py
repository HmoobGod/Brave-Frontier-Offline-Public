"""v31.00 deterministic demo foe priority and queued squad attacks through existing controls."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3100_battle_focus.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3000_battle_results.js")')<java.index('readPackagedText("bf3100_battle_focus.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
 'bf110_quest_journal.js','bf2000_story_battle_hud.js',
 'bf2100_battle_command_tray.js','bf2200_original_event_reader.js',
 'bf2300_morgan_event_dialogue.js','bf2400_st_lamia_event_dialogue.js',
 'bf2500_story_event_prompt.js','bf2600_original_event_portraits.js',
 'bf2700_original_event_stage.js','bf2800_dialogue_speaker_cues.js',
 'bf2900_original_event_expressions.js','bf3000_battle_results.js',
 'bf3100_battle_focus.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf3100-focus').is_visible()
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().canQueue') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("invalid")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("low","fake")') is False
 # Original source-gated mission selection, no fabricated foe wave table.
 page.evaluate('()=>{P.questClears[1]=1;renderQuestList();BFQuestAreas.choose(QUESTS.find(q=>q.missionId===2))}')
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('S.enemies.length')==3
 page.evaluate("""()=>{const es=S.enemies;
 es[0].hp=390;es[0].maxHp=5000;es[0].atk=800;es[0].def=50;
 es[1].hp=75;es[1].maxHp=100;es[1].atk=100;es[1].def=180;
 es[2].hp=760;es[2].maxHp=2000;es[2].atk=300;es[2].def=5;update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-hp").slot')==1
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-hp-percent").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("highest-atk").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-def").slot')==2
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is True
 assert page.evaluate('S.target')==0
 assert page.locator('#bf3100-options button').count()==5
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp-percent")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===0)')
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='lowest-hp-percent'
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===1)')
 page.evaluate('S.party[0].bb=100;update()')
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-def","burst")') is True
 assert page.evaluate('S.party[0].action.kind')=='burst'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===2)')
 # Any invalid living foe must block the WHOLE manual focus plan rather
 # than silently skipping it and targeting an ambiguous native button.
 # Keep synthetic corruption in one synchronous browser task, so the
 # normal battle renderer never observes these deliberately invalid rows.
 results=page.evaluate("""()=>{const original=S.enemies;
   const seed=original[0],strategies=['lowest-hp','lowest-hp-percent','highest-atk','lowest-def'];
   try{
     S.enemies=[
       {...seed,slot:0,name:'Zero max',hp:5,maxHp:0,atk:9999,def:-99},
       {...seed,slot:1,name:'Infinite HP',hp:Infinity,maxHp:100,atk:9998,def:-98},
       {...seed,slot:-1,name:'Bad slot',hp:2,maxHp:100,atk:9997,def:-97},
       {...seed,slot:3,name:'Valid target',hp:175,maxHp:200,atk:50,def:50}
     ];
     const valid=strategies.map(kind=>BFGlobalBattleFocusV3100.lookup(kind)?.slot);
     S.enemies=S.enemies.slice(0,3);
     const invalid=strategies.map(kind=>BFGlobalBattleFocusV3100.lookup(kind));
     const rejected=BFGlobalBattleFocusV3100.focus('highest-atk')===false;
     return {valid,invalid,rejected};
   }finally{S.enemies=original;}
 }""")
 assert results['valid']==[None,None,None,None],results
 assert results['invalid']==[None,None,None,None],results
 assert results['rejected'],results
 # Targeting and queued orders must remain untouched if ANY living record
 # is corrupt, including text-coerced Infinity or a duplicate valid slot.
 # Validate all four focus strategies and actual queueFocus player controls.
 gated=page.evaluate("""()=>{const original=S.enemies,seed=original[0];
   const originalTarget=S.target;
   const savedActions=S.party.map(p=>JSON.stringify(p.action));
   const cases=[
     [{...seed,slot:0,hp:5,maxHp:0},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:0,hp:'Infinity',maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:0,hp:Infinity,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:1,hp:5,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:-1,hp:5,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}]
   ];
   try{
     return cases.map(foes=>{
       S.enemies=foes;
       const looked=['lowest-hp','lowest-hp-percent','highest-atk','lowest-def']
         .map(k=>BFGlobalBattleFocusV3100.lookup(k));
       const focused=BFGlobalBattleFocusV3100.focus('lowest-hp');
       const queued=BFGlobalBattleFocusV3100.queueFocus('highest-atk','burst');
       return {looked,focused,queued,targetUnchanged:S.target===originalTarget,
         actionsUnchanged:savedActions.every((a,i)=>a===JSON.stringify(S.party[i].action))};
     });
   }finally{S.enemies=original;S.target=originalTarget;}
 }""")
 assert len(gated)==5,gated
 assert all(x['looked']==[None]*4 and x['focused'] is False and
            x['queued'] is False and x['targetUnchanged'] and
            x['actionsUnchanged'] for x in gated),gated
 # With an entirely valid roster, percentage ranking still differs from
 # absolute HP ranking; ties retain the prior lower-slot ordering.
 ranks=page.evaluate("""()=>{const original=S.enemies,seed=original[0];
   try{
     S.enemies=[
       {...seed,slot:0,hp:10,maxHp:20},
       {...seed,slot:1,hp:100,maxHp:1000},
       {...seed,slot:2,hp:600,maxHp:1000},
       {...seed,slot:3,hp:50,maxHp:500}
     ];
     return {absolute:BFGlobalBattleFocusV3100.lookup('lowest-hp')?.slot,
       relative:BFGlobalBattleFocusV3100.lookup('lowest-hp-percent')?.slot};
   }finally{S.enemies=original;}
 }""")
 assert ranks=={'absolute':0,'relative':1},ranks
 assert page.evaluate('P.version')==7
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 # The fixture explicitly selects a mission, so compare save for implicit writes, not transient P.lastMission.
 assert after['save']==before['save']
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.locator('#auto').uncheck()
 page.evaluate('finish(false)')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("lowest-def")') is False
 assert not errors,errors
 browser.close()
print('PASS v31.00: four manual focus strategies, full living-roster preflight, native queue/BB and v7 save isolation')
