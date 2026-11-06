"""Archived #20401 in actual DEMO normal/BB attacks, synthetic state only."""
import ast
import gzip
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / 'app/src/main/assets'
evidence = json.loads((ROOT / 'source_data/bf_global_2022_party_atk_item_evidence_v5000.json').read_text())
item = next(x for x in evidence['items'] if x['itemId'] == 20401)
assert item['rawName'] == '強靭薬'
assert (item['battleEffectGroupId'], item['targetType'], item['itemTargetArea'], item['skillTypeId']) == (400, 1, 1, 5)
assert item['passiveSkillInfo'] == '0,50,0,0,0,3' and item['itemMaxEquipped'] == 10
catalog = json.loads(gzip.decompress((ROOT / 'source_data/bf_global_2022_battle_item_effect_catalog_v5000.json.gz').read_bytes()))
assert next(r for r in catalog['rows'] if r[0] == '20401') == ['20401', '400', '1', '1', '5', '0,50,0,0,0,3', '10']
src = (A / 'bf4400_source_atk_item.js').read_text()
assert "itemId:20401,name:'強靭薬'" in src
assert all(x not in src for x in ('localStorage', 'saveProgress(', 'BFAndroid'))
assert len(src.encode()) < 65536
assert 'python3 test_bf_source_atk_50_item.py --source-only' in (ROOT / '.github/workflows/source-atk-50-item.yml').read_text()
assert (ROOT / '.github/workflows/build-debug-apk.yml').read_text().count('python3 test_bf_source_atk_50_item.py') == 1
if '--source-only' in sys.argv:
    print('PASS source: #20401 matches two archived records; no persistent-state API')
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

# Use the existing production dependency order, including shared reservations,
# party +50% and single +100%. Never substitute a combat implementation.
tree = ast.parse((ROOT / 'test_bf_source_double_atk_item_v5100.py').read_text())
modules = next(ast.literal_eval(n) for n in ast.walk(tree)
               if isinstance(n, ast.Tuple) and n.elts and
               isinstance(n.elts[0], ast.Constant) and n.elts[0].value == 'bf_home_nav.js')
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    for width in (320, 359, 393, 540):
        context = browser.new_context(viewport={'width': width, 'height': 844}, service_workers='block')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.route('**/*', lambda route: route.abort())
        page.evaluate("""()=>{
          window.__atk50Data=Object.create(null);window.__atk50Writes=0;
          const db=window.__atk50Data;
          Object.defineProperty(window,'localStorage',{value:{
            getItem:k=>db[k]??null,setItem:(k,v)=>{window.__atk50Writes++;db[k]=String(v)},
            removeItem:k=>{window.__atk50Writes++;delete db[k]},
            clear:()=>{window.__atk50Writes++;Object.keys(db).forEach(k=>delete db[k])},
            key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
          }});
          window.alert=()=>{};window.confirm=()=>false;
          HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((A / 'index.html').read_text(), wait_until='load', timeout=90000)
        page.add_style_tag(path=str(A / 'bf_home_nav.css'))
        for name in modules:
            page.add_script_tag(path=str(A / name))
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        state = '()=>JSON.stringify({player:P,storage:window.__atk50Data,writes:window.__atk50Writes})'
        before = page.evaluate(state)
        assert page.evaluate('BFGlobalSourceAtkItemV4400.source.itemId') == 20400
        assert page.evaluate('BFGlobalSourceAtkItemV4400.snapshot().selectedSource.itemId') == 20400
        profile = page.evaluate('BFGlobalSourceAtkItemV4400.sources[20401]')
        assert profile['effectGroupId'] == item['battleEffectGroupId']
        for key in ('itemId', 'targetType', 'itemTargetArea', 'skillTypeId', 'passiveSkillInfo', 'itemMaxEquipped'):
            assert profile[key] == item[key], key
        assert page.evaluate('Object.isFrozen(BFGlobalSourceAtkItemV4400.sources[20401])')
        for value in (None, 0, 50400, 20401.5, '20401'):
            assert page.evaluate('(id)=>BFGlobalSourceAtkItemV4400.useAtkItem(1,0,id)', value) is False
        for flag in ('busy', 'over', 'auto'):
            page.evaluate('(flag)=>S[flag]=true', flag)
            assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,0,20401)') is False
            page.evaluate('(flag)=>S[flag]=false', flag)
        # Never replace any active buff, even a weaker one: keep legacy policy.
        for pct in (30, 50, 100):
            page.evaluate('(pct)=>S.party[0].atkBuff={pct,untilRound:S.round+2}', pct)
            assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,0,20401)') is False
        page.evaluate('S.party[0].atkBuff=null; S.party[0].hp=0')
        assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,0,20401)') is False
        page.evaluate("""()=>{
          for(const ally of S.party){ally.hp=100000;ally.maxHp=100000;ally.action=null;}
          S.party[0].atk=1001;
          S.enemies=[{...S.enemies[0],hp:100000,maxHp:100000,def:100}];
          window.__atk50Fresh=JSON.stringify(S);
        }""")
        attack = """async kind=>{
          S.enemies[0].hp=100000;S.target=0;seed=12345;
          S.party[0].bb=100;S.party[0].action={kind,target:0};
          await performUnit(S.party[0],epoch);
          S.party[0].action=null;
          return 100000-S.enemies[0].hp;
        }"""
        normal = page.evaluate(attack, 'attack')
        burst = page.evaluate(attack, 'burst')
        assert normal > 0 and burst > 0
        page.evaluate('BFGlobalSourceAtkItemV4400.refresh()')
        # Open the production panel's ancestors and use real DOM events.
        page.locator('#bf4400-item').evaluate("el=>{for(let p=el;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true}")
        page.locator('#bf4400-strength').select_option('20401')
        page.locator('#bf4400-actor').select_option('1')
        page.locator('#bf4400-recipient').select_option('0')
        page.locator('#bf4400-use').click()
        assert page.evaluate('currentAtkBoost(S.party[0])') == 50
        assert page.evaluate('effectivePlayerAtk(S.party[0])') == 1502
        assert page.evaluate('S.party[1].action.kind') == 'guard'
        assert page.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining') == 0
        assert page.locator('#bf4400-strength').is_disabled()
        assert page.evaluate(attack, 'attack') > normal
        assert page.evaluate(attack, 'burst') > burst
        assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(2,3)') is False
        page.evaluate('S.party[1].action=null')
        assert page.evaluate('BFGlobalSourcePartyAtkItemV5000.usePartyAtk(1)') is False
        assert page.evaluate('BFGlobalSourceDoubleAtkV5100.useDoubleAtk(1,0)') is False
        page.evaluate('S.party[1].action={kind:"attack",target:0};BFGlobalItemTurnReservationsV4500.enforce()')
        assert page.evaluate('S.party[1].action.kind') == 'guard'
        for round_number in (2, 3):
            page.evaluate('(n)=>S.round=n', round_number)
            assert page.evaluate('currentAtkBoost(S.party[0])') == 50
        page.evaluate('S.round=4')
        assert page.evaluate('currentAtkBoost(S.party[0])') == 0
        assert page.evaluate('effectivePlayerAtk(S.party[0])') == 1001
        assert page.evaluate(state) == before
        # A separate in-memory battle resets default selection and shared stock.
        page.evaluate('S=JSON.parse(window.__atk50Fresh);BFGlobalSourceAtkItemV4400.refresh()')
        assert page.evaluate('BFGlobalSourceAtkItemV4400.snapshot().selectedSource.itemId') == 20400
        assert page.evaluate('BFGlobalSourceAtkItemV4400.snapshot().remaining') == 1
        assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,0)') is True
        assert page.evaluate('currentAtkBoost(S.party[0])') == 30
        assert page.evaluate(state) == before
        # Other ATK commands keep their stronger-effect policy and own budget.
        page.evaluate('S=JSON.parse(window.__atk50Fresh);BFGlobalSourceAtkItemV4400.refresh()')
        assert page.evaluate('BFGlobalSourceAtkItemV4400.useAtkItem(1,0,20401)') is True
        assert page.evaluate('BFGlobalSourcePartyAtkItemV5000.usePartyAtk(2)') is True
        assert page.evaluate('currentAtkBoost(S.party[0])') == 50
        assert page.evaluate('BFGlobalSourceDoubleAtkV5100.useDoubleAtk(3,0)') is True
        assert page.evaluate('currentAtkBoost(S.party[0])') == 100
        assert page.evaluate(state) == before
        assert not errors, errors
        context.close()
        print('PASS', width, 'source +50% raises actual normal/BB damage; Guard/shared charge/expiry/default; progress unchanged')
    browser.close()
