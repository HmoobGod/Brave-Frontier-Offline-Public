"""v114 original 2022 Global unitMaxLevel: 72 playable forms, live safe caps."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_2022_playable_level_caps_v114.json').read_text('utf8'))
ls=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
assert manifest['schema']=='bf-global-2022-playable-max-levels-v114'
assert manifest['supportedForms']==ls['totalForms']==72
assert manifest['provenance']['archiveSha256']==ls['source']['zipSha256']
assert manifest['provenance']['unitMaster1Sha256']==ls['source']['unitMasters'][0]['sha256']
assert manifest['provenance']['unitMaster2Sha256']==ls['source']['unitMasters'][1]['sha256']
assert manifest['provenance']['originalField']=='unitMaxLevel'
f=manifest['firstStarterCapByElement']
assert f=={str(e):([12,40,60,80,100] if e<=4 else [30,40,60,80,100]) for e in range(1,7)}
assert manifest['secondStarterCap']==[30,40,60,80,100]
assert manifest['alternateCap']==[30,40]
expected={}
for e in range(1,7):
 for i in range(5):
  expected[e*10000+11+i]=f[str(e)][i]
  expected[e*10000+21+i]=manifest['secondStarterCap'][i]
 for i in range(2):
  expected[e*10000+41+i]=manifest['alternateCap'][i]
assert len(expected)==72
assert set(expected)=={x['unitId'] for x in ls['rows']}
js=(A/'bf11400_original_unit_level_caps.js').read_text('utf8')
v111=(A/'bf11100_original_starter_leader_combat.js').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_UNIT_LEVEL_CAPS_V11400')==1
assert 'window.BFGlobalOriginalUnitLevelCapsV11400?.apply?.(unit,i)' in v111
assert v111.index('BFGlobalOriginalUnitLevelCapsV11400?.apply?')<v111.index('return apply(unit,i)')
assert len(js.encode('utf8'))<65536
assert not any(t in js for t in ['localStorage','saveProgress(', 'P.unitExp=', 'P.roster=', 'P.squad=', 'Math.random','fetch(', 'XMLHttpRequest'])
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11200_all_playable_leader_source.js")')<java.index('readPackagedText("bf11400_original_unit_level_caps.js")')

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=browser.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda exc:errors.append(str(exc)))
 core=(A/'index.html').read_text('utf8')
 assert 'function playerUnit(i){' in core
 assert 'const grow=demoLevel(P.unitExp[uid])-1;' in core
 assert 'atk:src.stats.atk+grow*12' in core
 p.set_content(core,wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('typeof reset')=='function'
 for name in ('bf11000_source_starter_leader_skills.js',
              'bf11100_original_starter_leader_combat.js',
              'bf11200_all_playable_leader_source.js',
              'bf11400_original_unit_level_caps.js'):
  p.add_script_tag(path=str(A/name))
 api='BFGlobalOriginalUnitLevelCapsV11400'
 assert p.evaluate(api+'.source.forms')==72
 for unit,cap in expected.items():
  assert p.evaluate(f'{api}.lookup({unit})')==cap,unit
 assert p.evaluate(api+'.lookup(999999)') is None
 assert p.evaluate(api+'.lookup(10010)') is None
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.source.forms')==30
 assert p.locator('#bf11400-original-level-caps').count()==1
 # Existing saved experience remains untouched: high DEMO levels are only
 # capped in the newly created archive battle party, before v111 LS buffs.
 p.evaluate("""()=>{
   document.getElementById('mode').value='archive';
   for(const id of [10011,20011,30011,40011,50011,60011])P.unitExp[id]=30000;
 }""")
 assert p.evaluate('demoLevel(P.unitExp[10011])')>40
 before=p.evaluate("""()=>({
   player:JSON.stringify(P),
   local:(()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}})()
 })""")
 p.evaluate('reset()')
 rows=p.evaluate("""()=>S.party.map(u=>({
   unitId:u.unitId,baseId:u.baseId,level:u.level,hp:u.hp,maxHp:u.maxHp,
   atk:u.atk,def:u.def,rec:u.rec
 }))""")
 assert [u['level'] for u in rows]==[12,12,12,12,30,30],rows
 for idx,row in enumerate(rows):
  src=p.evaluate(f'()=>effectiveUnit(P.squad[{idx}]).stats')
  grow=row['level']-1
  hp,atk,defense,rec=(src['hp']+grow*30,src['atk']+grow*12,
                       src['def']+grow*8,src['rec']+grow*6)
  if idx==0:atk=atk*125//100
  assert (row['maxHp'],row['hp'],row['atk'],row['def'],row['rec'])==(
    hp,hp,atk,defense,rec),(idx,row,src)
 audit=p.evaluate(api+'.snapshot()')
 assert audit['squadCappedThisBattle']==6
 assert audit['rows'][0]['originalMaxLevel']==12
 assert audit['rows'][4]['originalMaxLevel']==30
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().rows[0].effectiveAtk')==rows[0]['atk']
 # Repeated reset must not stack effects or alter the saved experience.
 p.evaluate('reset()')
 assert p.evaluate('S.party.map(u=>[u.level,u.hp,u.atk,u.def,u.rec])')==[
   [u['level'],u['hp'],u['atk'],u['def'],u['rec']] for u in rows]
 assert p.evaluate(api+'.snapshot().squadCappedThisBattle')==6
 # Original 3★ evolved form level cap 40; preserve 25% ATK in v111.
 p.evaluate('P.evolutions[10011]=10012;reset()')
 evolved=p.evaluate('S.party[0]')
 src=p.evaluate('effectiveUnit(10011).stats')
 assert evolved['unitId']==10012 and evolved['level']==40
 assert evolved['atk']==(src['atk']+39*12)*125//100
 assert evolved['maxHp']==src['hp']+39*30
 assert p.evaluate(api+'.snapshot().rows[0].originalMaxLevel')==40
 # Training is unchanged and retains original pre-v114 DEMO level.
 p.evaluate('document.getElementById("mode").value="training";reset()')
 assert p.evaluate('S.party[0].level')==p.evaluate('demoLevel(P.unitExp[10011])')
 assert p.evaluate(api+'.snapshot().squadCappedThisBattle')==0
 # Source 6★ level 100 is not clipped to 99 by this patch; the legacy
 # DEMO max 99 remains a separate experience progression limitation.
 p.evaluate('P.evolutions[10011]=10015;document.getElementById("mode").value="archive";reset()')
 assert p.evaluate('S.party[0].level')==p.evaluate('demoLevel(P.unitExp[10011])')
 assert p.evaluate(api+'.lookup(10015)')==100
 # Restore original pre-test squad evolution selection without save write.
 p.evaluate('delete P.evolutions[10011];reset()')
 after=p.evaluate("""()=>({
   player:JSON.stringify(P),
   local:(()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}})()
 })""")
 assert before==after,(before,after)
 p.locator('#bf11400-original-level-caps').evaluate('(el)=>el.open=true')
 p.evaluate(api+'.refresh()')
 assert p.locator('#bf11400-level-rows li').count()==6
 p.add_script_tag(path=str(A/'bf11400_original_unit_level_caps.js'))
 assert p.locator('#bf11400-original-level-caps').count()==1
 assert not errors,errors
 browser.close()
print('PASS v114 source 72 original 2022 unit level caps; live archive-only caps before LS, resets, training, save v7')
