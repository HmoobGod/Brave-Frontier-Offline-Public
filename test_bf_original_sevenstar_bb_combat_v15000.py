"""v150: six source-verified original 2022 Global 7★ BB timelines in throwaway DEMO combat.

Never unlock 7★, replace live unit skills, write real saves or imply native damage.
"""
from pathlib import Path
import hashlib,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_sevenstar_starter_bb_v150.json').read_text('utf8'))
S=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
assert M['schema']=='bf-global-2022-sevenstar-starter-bb-source-v150'
assert M['sourceZipSha256']==S['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert M['unitCount']==6 and M['hitEventCount']==71
assert M['sourceUsesFirstDamageGroupOnly'] is True
assert M['nativeDamageMultiplierVerified'] is False and M['gameplayUnlock'] is False
assert len(M['originalSourceFiles']['skill'])==9 and len(M['originalSourceFiles']['level'])==4
rows=M['rows'];ids=[10016,20016,30016,40016,50016,60016]
assert [r['unitId'] for r in rows]==ids
reference={x['unitId']:x for x in S['rows']}
tuple_list=[]
for rec in rows:
 uid=rec['unitId'];r=reference[uid]
 assert r['skills']['bbId']==uid and r['rarity']==7
 assert (r['unitCost'],r['unitMaxLevel'],r['expPatternId'])==(38,120,10)
 assert r['animation']['nativeRendererProven'] is False
 assert rec['bbId']==uid and (rec['skillType'],rec['targetType'],rec['targetArea'])==('1','2','2')
 assert rec['sourceLv1EffectCode']==2500 and rec['sourceLv1FirstParam']==150 and rec['sourceLv1SecondParam']==80
 assert len(rec['sourceLevels'])==10 and all(x[1]==2500 and x[3:]==[80,0,0,0,0] for x in rec['sourceLevels'])
 assert [x[2] for x in rec['sourceLevels']]==[150,160,170,180,190,200,210,220,230,250]
 assert rec['hitShareTotal']==100 and sum(e[1] for e in rec['hitEvents'])==100
 assert all(len(e)==4 and e[0]>=0 and e[1]>0 for e in rec['hitEvents'])
 assert len(rec['hitEvents'])>=10
 assert ','.join(':'.join(map(str,e)) for e in rec['hitEvents'])==rec['damageFramesRaw']
 raw='|'.join(str(x[0])+':'+str(x[1])+':'+','.join(map(str,x[2:])) for x in rec['sourceLevels'])
 assert raw==rec['activeSkillInfoByLevelRaw']
 tuple_list.append([uid,rec['skillType'],rec['targetType'],rec['targetArea'],rec['effectFramesRaw'],rec['damageFramesRaw'],rec['activeSkillInfoByLevelRaw']])
canonical=json.dumps(tuple_list,separators=(',',':'),ensure_ascii=True).encode('utf8')
assert hashlib.sha256(canonical).hexdigest()==M['canonicalTupleSha256']=='f1f47eacbddef11dd724737f6e1669de2c16e42a2cf9ab8bd6f3bd09f0f4ba64'
assert sum(len(x['hitEvents']) for x in rows)==71
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert 'const BF_VERIFIED_BB_SCOPES=Object.freeze({' in html
assert 'const BF_ORIGINAL_BB_POWER=Object.freeze({' in html
# Modify HTML IN MEMORY in an isolated Chromium page only; the signed APK and
# source app HTML are neither changed nor injected with real 7★ actors.
scopes={str(x['unitId']):{'name':'Original 7★ source BB (test-only)',
 'target':'all_enemies','skillId':x['bbId']} for x in rows}
power={str(x['unitId']):{'name':'Original 7★ source BB (test-only)',
 'target':'all_enemies','base':150,'levels':[s[2] for s in x['sourceLevels']],
 'secondaryUnmodeled':False} for x in rows}
for token,records in [('const BF_VERIFIED_BB_SCOPES=Object.freeze({',scopes),
                      ('const BF_ORIGINAL_BB_POWER=Object.freeze({',power)]:
 assert html.count(token)==1
 replacement=','.join(json.dumps(key)+':'+json.dumps(value,separators=(',',':')) for key,value in records.items())+','
 html=html.replace(token,token+replacement,1)
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {const db={};
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content(html,wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 assert page.evaluate('UNIT_BY_ID.size')==72
 assert page.evaluate('ids=>ids.every(id=>!UNIT_BY_ID.has(id))',ids) is True
 output=page.evaluate("""async data => {
   const originalP=JSON.stringify(P),stored=localStorage.getItem('bf_global_offline_demo_v7');
   const results=[];
   for(const x of data){
     BF_debug.reset();const prior=UNIT_BY_ID.get(x.id-1);
     if(!prior||UNIT_BY_ID.has(x.id)||BF_ARCHIVE_BB_HITS[String(x.id)])throw Error('original sevenstar is not test-only');
     UNIT_BY_ID.set(x.id,{...prior,id:x.id,rarity:7,name:'SOURCE ONLY 7★ #'+x.id,stats:{...x.base}});
     BF_ARCHIVE_BB_HITS[String(x.id)]={unitId:x.id,bbId:x.id,
       groups:[x.events],groupWeights:[100],offensiveCandidate:true};
     const ally=S.party[0];ally.active=true;ally.unitId=x.id;ally.name='SOURCE ONLY 7★';
     ally.hp=x.base.hp;ally.maxHp=x.base.hp;ally.atk=x.base.atk;
     ally.def=x.base.def;ally.rec=x.base.rec;ally.bb=100;
     ally.action={kind:'burst',target:0};
     S.enemies=[{slot:0,name:'Dummy A',hp:999999,maxHp:999999,atk:10,def:0,element:'Water'},
        {slot:1,name:'Dummy B',hp:999999,maxHp:999999,atk:10,def:0,element:'Earth'}];
     S.mode='archive';S.over=false;S.target=0;
     wait=()=>Promise.resolve();
     const bb=bfOriginalBB(x.id),multiplier=bbDamageMultiplier(ally,true);
     const hits=archivedBraveBurstEvents(x.id);
     await performUnit(ally,epoch);
     results.push({id:x.id,target:bb?.target,multiplier,events:hits?.length,
       weights:hits?.reduce((n,h)=>n+h[1],0),
       damages:S.enemies.map(e=>999999-e.hp),gauge:ally.bb});
     ally.unitId=prior.id;ally.name=prior.name;changeAnim(ally,'idle');
     // Flush active animation before unregistering this temporary 7-star.
     BF_debug.reset();
     await new Promise(resolve=>requestAnimationFrame(resolve));
     UNIT_BY_ID.delete(x.id);delete BF_ARCHIVE_BB_HITS[String(x.id)];
   }
   return {results,remainingForms:UNIT_BY_ID.size,
     allSource7starAbsent:data.every(x=>!UNIT_BY_ID.has(x.id)),
     pUnchanged:JSON.stringify(P)===originalP,
     savedUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===stored};
 }""",[{'id':x['unitId'],'base':reference[x['unitId']]['base'],
          'events':x['hitEvents']} for x in rows])
 assert output['remainingForms']==72 and output['allSource7starAbsent'],output
 assert output['pUnchanged'] and output['savedUnchanged'],output
 for found,x in zip(output['results'],rows):
  assert found['id']==x['unitId'] and found['target']=='all_enemies',found
  # 2.5x is a deliberately synthetic DEMO multiplier for source BB Lv1
  # first parameter 150. It is NOT proven native Brave Frontier damage.
  assert found['multiplier']==2.5 and found['events']==len(x['hitEvents']),found
  assert found['weights']==100 and all(d>0 for d in found['damages']),found
  assert found['gauge']==0,found
 assert not errors,errors
 browser.close()
print('PASS v150: 6 original 2022 7star BB source timelines (71 hits) run ephemeral all-enemy DEMO combat; 72 real units and v7 saves untouched')
