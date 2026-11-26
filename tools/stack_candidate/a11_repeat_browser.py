import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]); errors=[]; n=0
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(e.stack or str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__db=db;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 p.add_style_tag(content=(A/'bf_home_nav.css').read_text())
 order=pathlib.Path(__file__).with_name('native-order.txt').read_text().splitlines()
 for f in order:
  before=len(errors);p.add_script_tag(content=(A/f).read_text())
  if len(errors)>before:print('MODULE ERROR',f,errors[before:],flush=True)
 print('INJECTED',len(order),'errors',len(errors),flush=True)
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 check(not errors,'exact native order startup')
 check(p.locator('#bf9800-repeat-count option').count()==300 and p.locator('#bf9800-repeat-count option').last.get_attribute('value')=='300','main repeat range 1-300')
 p.evaluate("""()=>{const id=RECRUIT_IDS[0],c=1000000001;P.roster.push(id,c);P.unitExp[id]=10000;P.unitExp[c]=15000;P._bfUnitInstancesV1={nextId:c+1,baseById:{[c]:id}};P.evolutions[c]=10022;P.squad=[c,id,...P.squad.slice(0,4)];if(!saveProgress())throw Error('fixture save');reset();renderProgress();BF_homeNav.go('quest');E.speed.value='5';E.speed.dispatchEvent(new Event('change'));E.auto.click()}""")
 p.wait_for_function('S.over===true',timeout=45000)
 assert p.evaluate('S.phase==="Victory"'), 'prerequisite victory failed'
 print('prerequisite',p.evaluate('({s:BFGlobalBattleResultsV3000.snapshot(),economy:BFGrandGaiaCampaignV100.sourceEconomyReadiness(),repeat:BFGlobalQoLQuestRepeatV9800.statusSnapshot()})'),flush=True)
 p.locator('#bf9800-auto-repeat summary').click(timeout=3000)
 p.locator('#bf9800-repeat-count').select_option('1')
 initial=p.evaluate('({copy:P.unitExp[1000000001],base:P.unitExp[RECRUIT_IDS[0]],clear:P.questClears[QUEST.missionId],token:P.summonTokens,reward:QUEST.exp})')
 p.locator('#bf9800-start').click(timeout=3000)
 check(p.evaluate('BFGlobalQoLQuestRepeatV9800.statusSnapshot().active && S.party[0].baseId===1000000001 && S.auto===true'),'actual one-repeat starts with copy leader')
 p.wait_for_function('!BFGlobalQoLQuestRepeatV9800.statusSnapshot().active',timeout=45000)
 print('repeat result',p.evaluate('({s:BFGlobalQoLQuestRepeatV9800.statusSnapshot(),phase:S.phase,auto:S.auto})'),flush=True)
 check(p.evaluate('BFGlobalQoLQuestRepeatV9800.statusSnapshot().completed===1 && S.phase==="Victory" && !S.auto'),'one actual additional clear and automatic stop')
 check(p.evaluate('(i)=>P.unitExp[1000000001]===i.copy+i.reward&&P.unitExp[RECRUIT_IDS[0]]===i.base+i.reward&&P.questClears[QUEST.missionId]===i.clear+1&&P.summonTokens===i.token+1',initial),'one repeat awards independent EXP and token')
 check(p.evaluate('localStorage.getItem(SAVE_KEY)===JSON.stringify(P)&&JSON.stringify(parseProgress(P))===JSON.stringify(P)'),'repeat save receipt exact')
 check(not errors,'no uncaught browser errors')
 print('TOTAL',n,flush=True);b.close()
