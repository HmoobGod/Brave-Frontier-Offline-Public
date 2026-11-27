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
r28=hashlib.sha256(html.encode('utf8')).hexdigest()=='bbb6c33bbf0a1813c0b1f5a0222829291741bba820bf7e75385dda9b01efca1c'
assert 'bf_global_offline_demo_v7' in html
assert 'const BF_VERIFIED_BB_SCOPES=Object.freeze({' in html
assert 'const BF_ORIGINAL_BB_POWER=Object.freeze({' in html
if not r28:
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
 if r28:page.route('**/*',lambda route:route.abort())
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
 if r28:
  # Reuse the existing R28 combat suite's disposable progression fixture and
  # canonical commit path. No production catalog/skill injection or ownership bypass.
  for f in (R/'tools/stack_candidate/native-order.txt').read_text('utf8').splitlines():
   page.add_script_tag(content=(A/f).read_text('utf8'))
  assert page.evaluate('UNIT_BY_ID.size')==84
  assert page.evaluate("""()=>{const ids=[10016,10017,20016,20017,30016,30017,40016,40017,50016,50017,60016,60017];return Object.keys(BF_R13_FORMS).map(Number).join(',')===ids.join(',')&&ids.every(id=>UNIT_BY_ID.get(id)===BF_R13_FORMS[id]);}""")
  page.evaluate("document.getElementById('mode').value='archive';document.getElementById('bf-r19-enable').checked=false;reset();saveProgress();document.getElementById('speed').value='5'")
  assert page.evaluate('copyCommitProgress(next=>{next.zel=100000000;next.karma=1000000000;return true})') is True
  page.evaluate('renderProgress();(()=>{let k=document.getElementById("bf-r7-currency"),q=document.getElementById("bf-r7-amount");k.value="karma";q.value="160000";q.oninput();document.getElementById("bf-r7-trade").click()})()')
  page.evaluate("""()=>{const e=document.getElementById('bf-merit-offer');e.value='80000056';e.onchange();const q=document.getElementById('bf-merit-qty');q.value='12';q.oninput();document.getElementById('bf-merit-buy').click()}""")
  assert page.evaluate('bfMeritTotals(P[BF_MERIT_KEY]).inventory[110100]===12') is True
  assert page.evaluate("""()=>copyCommitProgress(next=>{next.evolutions=Object.fromEntries([1,2,3,4,5,6].map(i=>[i*10000+11,i*10000+16]));next[BF_MASTERY_KEY]=Object.fromEntries([1,2,3,4,5,6].map(i=>[i*10000+11,[i*10000+16,1,0]]));next[BF_MERIT_KEY].used={...(next[BF_MERIT_KEY].used||{}),110100:6};return true})""") is True
  page.evaluate('reset()')
  assert page.evaluate('bfMeritTotals(P[BF_MERIT_KEY]).inventory[110100]===6') is True
  assert page.evaluate('ids=>ids.every((id,i)=>S.party[i].unitId===id&&bfR14Actor(S.party[i])&&bfMasteryBattleBB(S.party[i])===1)',ids) is True
  output=page.evaluate("""async data=>{
   const originalP=JSON.stringify(P),stored=localStorage.getItem('bf_global_offline_demo_v7');
   const catalog=[...UNIT_BY_ID.entries()],skills=JSON.stringify(BF_R14_SKILLS),hitTable=JSON.stringify(BF_ARCHIVE_BB_HITS);
   const results=[];
   for(const x of data){
    BF_debug.reset();const ally=S.party[x.slot];
    if(!bfR14Actor(ally)||ally.unitId!==x.id||S.r19?.enabled===true)throw Error('Owned BB fixture unavailable '+x.id);
    ally.bb=100;ally.action={kind:'burst',target:0,r14Tier:'bb'};
    S.enemies=[{slot:0,name:'Dummy A',hp:999999,maxHp:999999,atk:10,def:0,element:'Water'},
     {slot:1,name:'Dummy B',hp:999999,maxHp:999999,atk:10,def:0,element:'Earth'}];
    S.mode='archive';S.over=false;S.target=0;
    const skill=bfR14Skill(ally,'bb');
    if(!skill||!bfR14Ready(ally,'bb')||skill.id!==x.id||skill.level!==1)throw Error('BB not ready '+x.id);
    const projected=x.events.map(e=>[e[0],e[1],0,0]);
    if(JSON.stringify(skill.events)!==JSON.stringify(projected))throw Error('BB tick/share mismatch '+x.id);
    if(JSON.stringify(BF_R14_SKILLS[x.id][0].levels)!==JSON.stringify(x.levels))throw Error('BB level table mismatch '+x.id);
    const multiplier=1+skill.modifier/100;
    // The prototype damage formula consumes RNG. Validate observed positive
    // damage on both targets rather than rerolling an expected exact amount.
    wait=()=>Promise.resolve();
    await performUnit(ally,epoch);
    results.push({id:x.id,targetCount:S.enemies.length,multiplier,flat:skill.flat,level:skill.level,events:skill.events.length,weights:skill.events.reduce((n,h)=>n+h[1],0),damages:S.enemies.map(e=>999999-e.hp),gauge:ally.bb});
    BF_debug.reset();await new Promise(resolve=>requestAnimationFrame(resolve));
    if(UNIT_BY_ID.size!==catalog.length||!catalog.every(([id,u])=>UNIT_BY_ID.get(id)===u)||JSON.stringify(BF_R14_SKILLS)!==skills||JSON.stringify(BF_ARCHIVE_BB_HITS)!==hitTable||JSON.stringify(P)!==originalP||localStorage.getItem('bf_global_offline_demo_v7')!==stored)throw Error('Production catalog, skills or fixture save changed '+x.id);
   }
   return {results,remainingForms:UNIT_BY_ID.size,allSource7starPresent:data.every(x=>UNIT_BY_ID.get(x.id)===BF_R13_FORMS[x.id]),pUnchanged:JSON.stringify(P)===originalP,savedUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===stored};
  }""",[{'id':x['unitId'],'slot':i,'events':x['hitEvents'],'levels':[s[2] for s in x['sourceLevels']]} for i,x in enumerate(rows)])
  assert output['remainingForms']==84 and output['allSource7starPresent'],output
  assert output['pUnchanged'] and output['savedUnchanged'],output
  assert len(output['results'])==6,output
  for found,x in zip(output['results'],rows):
   assert found['id']==x['unitId'] and found['targetCount']==2,found
   assert found['multiplier']==2.5 and found['events']==len(x['hitEvents']),found
   assert found['flat']==80 and found['level']==1,found
   assert found['weights']==100 and all(d>0 for d in found['damages']),found
   assert found['gauge']==0,found
 else:
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
if r28:
 print('PASS v150 R28: six owned production 7star BB Lv1 attacks, 71 source tick/share rows, both targets damaged, gauge consumed, catalog and disposable v7 fixture unchanged')
else:
 print('PASS v150: 6 original 2022 7star BB source timelines (71 hits) run ephemeral all-enemy DEMO combat; 72 real units and v7 saves untouched')
