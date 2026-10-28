"""v147: original 2022 7-star Water normal attack, non-saving battle-engine smoke.

This is a TEST-ONLY actor, never a playable roster/evolution or native damage claim.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import base64,csv,hashlib,io,json,shutil,zipfile

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
pilot=json.loads((R/'source_data/bf_global_7star_water_visual_preview_v129.json').read_text('utf8'))
row=next(x for x in M['rows'] if x['unitId']==20016)
assert M['schema']=='bf-global-2022-7-8-starter-source-readiness-v127'
assert M['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert (row['unitId'],row['previousFormId'],row['rarity'],row['unitCost'],row['unitMaxLevel'],row['expPatternId'])==(20016,20015,7,38,120,10)
assert row['base']=={'hp':4080,'atk':1320,'def':1080,'rec':1360}
assert row['lordAtMax']=={'hp':6320,'atk':2280,'def':2050,'rec':2450}
assert row['animation']['cggSourceFrameCount']==23
assert row['animation']['nativeRendererProven'] is False
assert pilot['sourceUnitId']==20016 and pilot['referenceOnly'] is True
assert pilot['nativeFrameClockProven'] is False and pilot['spritePixelsAreReconstruction'] is True
path=R/'source_assets/bf1/BF1_Global_2022_SevenStar_Water_Pilot_v129.zip.b64'
packed=base64.b64decode(path.read_text('ascii').strip(),validate=True)
assert hashlib.sha256(packed).hexdigest()==pilot['sourcePackageSha256']
expected={x['path']:x['sha256'] for x in row['assets']}
with zipfile.ZipFile(io.BytesIO(packed)) as archive:
 assert set(archive.namelist())==set(expected)
 for f,digest in expected.items():
  assert hashlib.sha256(archive.read(f)).hexdigest()==digest,(f,digest)
 attack=[[int(v) for v in entry if v.strip()] for entry in
        csv.reader(io.StringIO(archive.read('content/unit/cgs/unit_atk_cgs_20016.csv').decode('utf-8-sig')))]
 assert len(attack)==14
 assert all(len(x)==4 and x[0]>=0 and x[3]>0 and x[0]<23 for x in attack)
# These four-integer hit rows match the original owner-supplied 2022 F_UNIT_MST.
damage=[[10,8,2,1],[13,8,2,1],[25,25,2,2],[28,15,2,2],
        [31,10,2,2],[34,9,2,2],[37,9,2,2],[40,8,2,2],[43,8,2,2]]
assert len(damage)==9 and sum(x[1] for x in damage)==100
normal_js=(A/'bf12500_full_original_normal_hits.js').read_text('utf8')
cgg_js=(A/'bf12800_original_starter_cgg_cgs.js').read_text('utf8')
assert 'BF_GLOBAL_ORIGINAL_NORMAL_HIT_ARCHIVE_V12500' in normal_js
assert 'BF_GLOBAL_ORIGINAL_STARTER_CGG_CGS_V12800' in cgg_js
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 assert page.evaluate('UNIT_BY_ID.size')==72
 assert page.evaluate('UNIT_BY_ID.has(20016)') is False
 page.add_script_tag(path=str(A/'bf12500_full_original_normal_hits.js'))
 page.add_script_tag(path=str(A/'bf12800_original_starter_cgg_cgs.js'))
 assert page.evaluate('async()=>await BFGlobalOriginalStarterCggV12800.ready') is True
 page.wait_for_function('()=>!!window.BFGlobalOriginalNormalHitArchiveV12500?.lookup?.(20016)',timeout=30000)
 profile=page.evaluate("""() => ({
   cgg:BFGlobalOriginalStarterCggV12800.lookup(20016)?.cggFrameCount,
   attack:BFGlobalOriginalStarterCggV12800.lookup(20016)?.sequences?.atk,
   events:BFGlobalOriginalNormalHitArchiveV12500.lookup(20016)?.events,
   originalArchive:BFGlobalOriginalNormalHitArchiveV12500.count,
   sevenStarLive:UNIT_BY_ID.has(20016)
 })""")
 assert profile['cgg']==23 and profile['attack']==attack
 assert profile['events']==damage and profile['originalArchive']==2258
 assert profile['sevenStarLive'] is False
 result=page.evaluate("""async({attack,damage,stats}) => {
   const originalSave=JSON.stringify(P);
   const stored=localStorage.getItem('bf_global_offline_demo_v7');
   BF_debug.reset();
   const earlier=UNIT_BY_ID.get(20015);
   if(!earlier)return {error:'missing original 6-star base'};
   const temporary={...earlier,id:20016,rarity:7,
      name:'7-star Water SOURCE-ONLY test actor',
      stats:{...stats},frameCount:23,
      animation:{...earlier.animation,atk:attack}};
   UNIT_BY_ID.set(20016,temporary);
   if(BF_ARCHIVE_NORMAL_HITS['20016'])return {error:'unexpected production 7star combat'};
   BF_ARCHIVE_NORMAL_HITS['20016']={
      unitId:20016,weightsTotal:100,events:damage};
   const actor=S.party[0];
   actor.active=true;actor.unitId=20016;actor.name=temporary.name;
   actor.hp=stats.hp;actor.maxHp=stats.hp;
   actor.atk=stats.atk;actor.def=stats.def;actor.rec=stats.rec;
   actor.bb=0;actor.action={kind:'attack',target:0};
   S.enemies=[{slot:0,name:'Ephemeral target (no quest)',hp:999999,
      maxHp:999999,atk:10,def:0,element:'Water'}];
   S.mode='archive';S.over=false;S.target=0;
   const start=S.enemies[0].hp;
   wait=()=>Promise.resolve();
   await performUnit(actor,epoch);
   const result={unitId:actor.unitId,sourceRarity:temporary.rarity,
      normalEvents:damage.length,weightedShare:damage.reduce((n,e)=>n+e[1],0),
      sourceAttackKeys:attack.length,
      simulatedDamage:start-S.enemies[0].hp,
      DEMOBurstGauge:actor.bb,
      saveVersion:P.version};
   // The canvas animation loop reads UNIT_BY_ID for every live party actor.
   // Reset the disposable battle (and invalidate its epoch) BEFORE dropping
   // its temporary 7-star actor, otherwise the next rAF may render an ID
   // that no longer exists and raise a nondeterministic page error.
   BF_debug.reset();
   await new Promise(resolve => requestAnimationFrame(resolve));
   UNIT_BY_ID.delete(20016);
   delete BF_ARCHIVE_NORMAL_HITS['20016'];
   result.temporaryUnitGone=!UNIT_BY_ID.has(20016);
   result.playerUnchanged=JSON.stringify(P)===originalSave;
   result.localSaveUnchanged=localStorage.getItem('bf_global_offline_demo_v7')===stored;
   return result;
 }""",{'attack':attack,'damage':damage,'stats':row['base']})
 assert result.get('unitId')==20016 and result['sourceRarity']==7,result
 assert result['normalEvents']==9 and result['weightedShare']==100,result
 assert result['sourceAttackKeys']==14,result
 assert result['simulatedDamage']>0 and result['DEMOBurstGauge']==34,result
 assert result['saveVersion']==7 and result['temporaryUnitGone'],result
 assert result['playerUnchanged'] and result['localSaveUnchanged'],result
 assert not errors,errors
 browser.close()
print('PASS v147: source-authenticated 7-star Water nine original hit events and 14 CGS steps execute in ephemeral 2022 DEMO battle without crashes or saved roster/XP/state changes')
