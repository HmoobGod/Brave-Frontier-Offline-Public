"""Source #20601 DEF+50% in real DEMO combat; synthetic progress only."""
import ast
import gzip
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
ref=json.loads((ROOT/'source_data/bf_global_2022_def_item_evidence_v4900.json').read_text())
item=next(x for x in ref['items'] if x['itemId']==20601)
assert item['rawName']=='堅牢薬'
assert (item['battleEffectGroupId'],item['targetType'],item['itemTargetArea'],item['skillTypeId'])==(410,1,1,5)
assert item['passiveSkillInfo']=='0,0,50,0,0,3' and item['itemMaxEquipped']==10
catalog=json.loads(gzip.decompress((ROOT/'source_data/bf_global_2022_battle_item_effect_catalog_v5000.json.gz').read_bytes()))
assert next(r for r in catalog['rows'] if r[0]=='20601')==['20601','410','1','1','5','0,0,50,0,0,3','10']
src=(A/'bf4900_source_def_item.js').read_text()
assert "itemId:20601,name:'堅牢薬'" in src
assert all(x not in src for x in ('localStorage','saveProgress(', 'BFAndroid'))
assert len(src.encode())<65536
assert 'python3 test_bf_source_def_50_item.py --source-only' in (ROOT/'.github/workflows/source-def-50-item.yml').read_text()
assert (ROOT/'.github/workflows/build-debug-apk.yml').read_text().count('python3 test_bf_source_def_50_item.py')==1
if '--source-only' in sys.argv:
    print('PASS source: #20601 matches two archived records; no persistent-state API');raise SystemExit(0)

# Reuse the committed legacy integration fixture's actual module order.
tree=ast.parse((ROOT/'test_bf_source_def_item_v4900.py').read_text())
modules=next(ast.literal_eval(n.iter) for n in ast.walk(tree)
             if isinstance(n,ast.For) and isinstance(n.target,ast.Name)
             and n.target.id=='name' and isinstance(n.iter,ast.Tuple))
from playwright.sync_api import sync_playwright
chrome=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable')
assert chrome
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width in (320,359,393,540):
        context=browser.new_context(viewport={'width':width,'height':844},service_workers='block')
        page=context.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.route('**/*',lambda route:route.abort())
        page.evaluate("""()=>{
          window.__def50Data=Object.create(null);window.__def50Writes=0;
          const db=window.__def50Data;
          Object.defineProperty(window,'localStorage',{value:{
            getItem:k=>db[k]??null,setItem:(k,v)=>{window.__def50Writes++;db[k]=String(v)},
            removeItem:k=>{window.__def50Writes++;delete db[k]},
            clear:()=>{window.__def50Writes++;Object.keys(db).forEach(k=>delete db[k])},
            key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
          }});
          window.alert=()=>{};window.confirm=()=>false;
          HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
        page.add_style_tag(path=str(A/'bf_home_nav.css'))
        for name in modules:page.add_script_tag(path=str(A/name))
        for name in ('bf5000_source_party_atk_item.js','bf5100_source_double_atk_item.js',
                     'bf5200_source_double_def_item.js','bf5300_source_party_def_item.js',
                     'bf5400_source_hope_light.js','bf5500_source_strong_life.js','bf5600_source_life_potion.js',
                     'bf5700_original_ailment_state.js','bf5800_poison_turn.js','bf5900_curse_bb_lock.js',
                     'bf6000_paralysis_action_lock.js','bf6100_weakness_defense.js'):
            page.add_script_tag(path=str(A/name))
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        state="()=>JSON.stringify({player:P,storage:window.__def50Data,writes:window.__def50Writes})"
        before=page.evaluate(state)
        assert page.evaluate('BFGlobalSourceDefItemV4900.source.itemId')==20600
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().selectedSource.itemId')==20600
        profile=page.evaluate('BFGlobalSourceDefItemV4900.sources[20601]')
        for key in ('itemId','battleEffectGroupId','targetType','itemTargetArea','skillTypeId','passiveSkillInfo','itemMaxEquipped'):
            assert profile[key]==item[key],key
        assert page.evaluate('Object.isFrozen(BFGlobalSourceDefItemV4900.sources[20601])')
        for value in (None,0,50600,20601.5,'20601'):
            assert page.evaluate('(id)=>BFGlobalSourceDefItemV4900.useDefItem(0,3,id)',value) is False
        for flag in ('busy','over','auto'):
            page.evaluate('(flag)=>S[flag]=true',flag)
            assert page.evaluate('BFGlobalSourceDefItemV4900.useDefItem(0,3,20601)') is False
            page.evaluate('(flag)=>S[flag]=false',flag)
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().remaining')==1
        page.evaluate("""()=>{
          for(const p of S.party){if(p.active){p.hp=100000;p.maxHp=100000;p.guard=false;p.action=null;}}
          S.party[3].def=101;
          S.enemies=[{...S.enemies[0],hp:100000,maxHp:100000,atk:2000}];
        }""")
        # Existing DEMO enemy phase uses this actual party DEF; no engine replacement.
        page.evaluate('async()=>{for(let i=0;i<6;i++)S.party[i].active=i===3;seed=12345;await enemyPhase(epoch);for(const p of S.party)p.active=true;}')
        unbuffed=page.evaluate('100000-S.party[3].hp');assert unbuffed>0
        page.evaluate('S.party[3].hp=100000;BFGlobalSourceDefItemV4900.refresh()')
        page.locator('#bf4900-strength').select_option('20601',force=True)
        page.locator('#bf4900-actor').select_option('0',force=True)
        page.locator('#bf4900-recipient').select_option('3',force=True)
        assert not page.locator('#bf4900-use').is_disabled()
        page.locator('#bf4900-use').dispatch_event('click')
        assert page.evaluate('S.party[3].def')==152
        assert page.evaluate('S.party[0].action.kind')=='guard'
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().activeBuffs[0].itemId')==20601
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().remaining')==0
        assert page.locator('#bf4900-strength').is_disabled()
        assert page.evaluate('BFGlobalSourceDoubleDefV5200.snapshot().eligibleRecipients.includes(3)') is False
        assert page.evaluate('BFGlobalSourcePartyDefV5300.snapshot().eligibleRecipients.includes(3)') is False
        page.evaluate('async()=>{for(let i=0;i<6;i++)S.party[i].active=i===3;seed=12345;await enemyPhase(epoch);for(const p of S.party)p.active=true;}')
        buffed=page.evaluate('100000-S.party[3].hp');assert 0<buffed<unbuffed,(width,unbuffed,buffed)
        assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,2)') is True
        during=page.evaluate('async()=>BFGlobalWeaknessDefenseV6100.withWeaknessDefense(async()=>S.party[3].def)')
        assert during==101,'Weakness must subtract 50 percentage points from source +50%, not assume +30%'
        assert page.evaluate('S.party[3].def')==152
        assert page.evaluate('BFGlobalOriginalAilmentStateV5700.cure(3,20210).removed')==[2]
        assert page.evaluate('BFGlobalItemTurnReservationsV4500.free(0)') is False
        assert page.evaluate('BFGlobalSourceDefItemV4900.useDefItem(1,2,20600)') is False
        for round_ in (2,3):
            page.evaluate('(r)=>S.round=r',round_)
            assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().activeBuffs.length')==1
            assert page.evaluate('S.party[3].def')==152
        page.evaluate('S.round=4')
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().activeBuffs.length')==0
        assert page.evaluate('S.party[3].def')==101
        assert page.evaluate(state)==before,'Progress/storage mutation'
        # New battle instances restore the existing default and one shared charge.
        page.evaluate('S={...S,round:1,party:S.party.map(p=>({...p,action:null}))}')
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().selectedSource.itemId')==20600
        assert page.evaluate('BFGlobalSourceDefItemV4900.snapshot().remaining')==1
        assert page.evaluate('BFGlobalSourceDefItemV4900.useDefItem(0,3)') is True
        assert page.evaluate('S.party[3].def')==131
        assert page.evaluate(state)==before,'Legacy/default progress mutation'
        assert not errors,errors
        context.close()
        print('PASS',width,'source +50% lowers actual DEMO damage; guard/shared charge/exclusion/expiry; progress unchanged')
    browser.close()
