"""Queued BB then Curse must use the existing normal-hit path, with synthetic progress."""
from pathlib import Path
import ast,hashlib,shutil,sys
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
HOOK='window.BFGlobalCurseBBLockV5900?.blockBurst?.(p.id);'
assert HOOK in (R/'prepare_source_aware_auto_v041.py').read_text()
assert 'python3 test_bf_queued_curse_dispatch.py' in (R/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:print('PASS queued-Curse source: optional existing status API at action dispatch');raise SystemExit(0)
html=(A/'index.html').read_text()
r28=hashlib.sha256(html.encode('utf8')).hexdigest()=='bbb6c33bbf0a1813c0b1f5a0222829291741bba820bf7e75385dda9b01efca1c'
if r28:
 # R28 has three p-dispatch sites (ordinary, mixed remainder, sequential)
 # and one first-actor dispatch site. Each must retain Curse-before-Auto-before-action.
 dispatch=HOOK+'window.BF041SmartAuto?.reconsider?.(p);await performUnit(p,token);'
 first=HOOK.replace('(p.id)','(first.id)')
 assert html.count(HOOK)==3 and html.count(dispatch)==3
 assert html.count(first)==1
 assert html.count(first+'window.BF041SmartAuto?.reconsider?.(first);await performUnit(first,token);')==1
 assert html.count('for(const p of rest){if(token!==epoch||!livingEnemies().length)break;if(!bfR15Owned(p))continue;'+dispatch)==1
 assert html.count("async function sequential(p){if(token!==epoch||!livingEnemies().length||!bfR15Owned(p))return;const kind=p.action?.kind,tier=kind==='burst'?bfR14Tier(p):null;"+dispatch)==1
 assert html.count('if(!await bfR21TryNormalRound(token)&&!await bfR26TryMixedRound(token)&&!await bfR25TryMixedRound(token))for(const p of liveParty()){if(!livingEnemies().length)break;'+dispatch)==1
else:
 assert html.count(HOOK)==1
assert HOOK+'window.BF041SmartAuto?.reconsider?.(p);await performUnit(p,token);' in html
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
tree=ast.parse((R/'test_bf_paralysis_action_lock_v6000.py').read_text())
names=next(ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.Tuple) and n.elts and isinstance(n.elts[0],ast.Constant) and n.elts[0].value=='bf_home_nav.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE)
 p.evaluate('()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}')
 p.set_content(html);p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js','bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js','bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js','bf9300_single_hit_critical_combat.js','bf9500_multihit_critical_combat.js'):p.add_script_tag(path=str(A/name))
 p.locator('.bf-navbar [data-bf-goto="quest"]').click()
 p.evaluate('()=>{for(const u of S.party){u.active=u.id===0;u.action=null;u.hp=1000;u.maxHp=1000}S.party[0].bb=100;S.selected=0;S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:1,atk:1}];document.getElementById("speed").value="4";window.__freshQueuedCurse=JSON.stringify(S);update()}')
 for unit,cure in ((10011,False),(20041,False),(10011,True)):
  p.evaluate('(id)=>{S=JSON.parse(__freshQueuedCurse);S.party[0].unitId=id;update()}',unit)
  p.locator('#burst').click();assert p.evaluate('S.party[0].action.kind')=='burst'
  assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,5)')
  if cure:assert p.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20220).removed')==[5]
  before=p.evaluate(SNAPSHOT);round_before=p.evaluate('S.round')
  p.evaluate('async()=>{const old=Math.random;Math.random=()=>0;try{await BF_debug.execute()}finally{Math.random=old}}')
  assert p.evaluate('S.round')==round_before+1
  if not cure:
   hits=p.evaluate('BFGlobalSingleHitCriticalV9300.snapshot().recent.concat(BFGlobalMultiHitCriticalV9500.snapshot().recent)')
   assert any(e['unitId']==unit and (e.get('critical') is True or e.get('criticals',0)>0) for e in hits),('normal critical handlers missed queued Curse fallback',hits)
   assert any(e['unitId']==unit for e in p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().recent'))
   assert p.evaluate('S.enemies[0].hp')<100000 and p.evaluate('S.party[0].bb')==100
  else:assert p.evaluate('S.party[0].bb')<100
  assert_unchanged(p,before,(unit,cure));print('PASS queued BB',unit,'cured',cure,'actual turn, critical/reference-crystal path or restored BB, unchanged P/storage',flush=True)
 assert not errors,errors;b.close()
