from pathlib import Path
import hashlib,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/bf-a5/assets/index.html')
s=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='fa48e14f9b8ae1594392fa7397ab2cc2eb8e3f52d56d29eb410108a2d16945ec','A5 base mismatch'
def edit(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b,1)
# Keep source IDs for catalog and recipe resolution; never alter original form rows.
edit('function awardDemoRewards(){','''function ownedCopyRows(includeUnowned=false){
 const owned=new Set(P.roster),rows=STARTERS.filter(u=>includeUnowned||owned.has(u.id));
 for(const id of P.roster){const base=ownedCopyBase(id,P[OWNED_COPY_META]);if(base!==null&&base!==id)rows.push({...UNIT_BY_ID.get(base),id,sourceBaseId:base});}
 return rows;
}
function copyNextRecipes(id){
 const base=ownedCopyBase(id,P[OWNED_COPY_META]),form=effectiveUnit(id)?.id;
 return EVO_RECIPES.filter(r=>r.baseId===base&&(r.fromId||r.baseId)===form);
}
// Disposable candidate only. All copy-bearing manual mutations use the existing canonical save.
function copyCommitProgress(mutator){
 if(saveRecoveryPending||S?.busy||S?.auto&&!S.over)return false;
 const before=P;let rawBefore,next,expected;
 try{rawBefore=localStorage.getItem(SAVE_KEY);if(rawBefore!==JSON.stringify(before))return false;
  next=JSON.parse(rawBefore);if(!mutator(next))return false;
  parseProgress(next);if(new TextEncoder().encode(JSON.stringify(next,null,2)).length>1048576)return false;
  expected=JSON.stringify(next);
 }catch(_){return false;}
 P=next;let ok=false,observed;
 try{ok=saveProgress()===true;observed=localStorage.getItem(SAVE_KEY);}catch(_){}
 if(ok&&P===next&&JSON.stringify(P)===expected&&observed===expected)return true;
 P=before;saveEnabled=false;
 try{if(observed===expected){localStorage.setItem(SAVE_KEY,rawBefore);observed=localStorage.getItem(SAVE_KEY);}if(observed===rawBefore)return false;}catch(_){}
 saveRecoveryPending=true;return false;
}
function customDuplicateSummon(){
 if(saveRecoveryPending||S?.busy||S?.auto&&!S.over||P.version!==7||!Number.isSafeInteger(P.summonTokens)||P.summonTokens<1||P.summonHistory.length>=100)return {ok:false};
 const draw=Math.random();if(!Number.isFinite(draw)||draw<0||draw>=1||!RECRUIT_IDS.length)return {ok:false};
 const sourceId=RECRUIT_IDS[Math.floor(draw*RECRUIT_IDS.length)];let id=sourceId;
 const ok=copyCommitProgress(next=>{
  if(next.roster.includes(sourceId)){
   const meta=next[OWNED_COPY_META]||{nextId:OWNED_COPY_FIRST,baseById:{}};id=meta.nextId;
   if(!Number.isSafeInteger(id)||id<OWNED_COPY_FIRST||id>OWNED_COPY_LAST||next.roster.includes(id))return false;
   meta.baseById[String(id)]=sourceId;meta.nextId=id+1;next[OWNED_COPY_META]=meta;
  }
  next.roster.push(id);next.unitExp[id]=0;next.summonTokens--;next.summonHistory.push(sourceId);return true;
 });
 return ok?{ok:true,id,sourceId}:{ok:false};
}
function awardDemoRewards(){''')
edit('for(const unit of STARTERS){if(!P.squad.includes(unit.id))continue;','for(const unit of ownedCopyRows()){if(!P.squad.includes(unit.id))continue;')
edit('let rows=STARTERS.filter(base=>P.roster.includes(base.id));','let rows=ownedCopyRows();')
edit('!EVO_RECIPES.some(r=>r.baseId===base.id&&(r.fromId||r.baseId)===effectiveUnit(base.id).id)','!copyNextRecipes(base.id).length')
edit('EVO_RECIPES.filter(r=>P.roster.includes(r.baseId)&&(r.fromId||r.baseId)===effectiveUnit(r.baseId).id).flatMap(r=>Object.keys(r.materials))','P.roster.flatMap(id=>copyNextRecipes(id).flatMap(r=>Object.keys(r.materials)))')
edit('const owned=STARTERS.filter(u=>P.roster.includes(u.id));','const owned=ownedCopyRows();')
edit('const sequence=EVO_RECIPES.filter(r=>r.baseId===baseId);','const sourceBase=ownedCopyBase(baseId,P[OWNED_COPY_META]);const sequence=EVO_RECIPES.filter(r=>r.baseId===sourceBase);')
# Display independent identifiers wherever an action targets a copy.
edit("heading.textContent=unit.name+' · Lv.'+lv+' · ★'+unit.rarity;","heading.textContent=unit.name+' · Lv.'+lv+' · ★'+unit.rarity+(base.id>=OWNED_COPY_FIRST?' · Copy #'+base.id:'');")
edit('heading.textContent=`${current.name} · ★${current.rarity} · Lv.${level}`;','heading.textContent=`${current.name} · ★${current.rarity} · Lv.${level}`+(baseId>=OWNED_COPY_FIRST?\' · Copy #\'+baseId:\'\');')
edit("if(S?.busy||!P.roster.includes(baseId)||![1,5].includes(times))return false;","if(S?.busy||!P.roster.includes(baseId)||![1,5].includes(times)||P[OWNED_COPY_META]&&(saveRecoveryPending||S?.auto&&!S.over))return false;")
edit(' P.trainingShards-=times;P.trainingSpent+=times;P.zel-=cost;\n P.unitExp[baseId]=current+amount;\n saveProgress();reset();renderProgress();',''' if(P[OWNED_COPY_META]){
  if(!copyCommitProgress(next=>{next.trainingShards-=times;next.trainingSpent+=times;next.zel-=cost;next.unitExp[baseId]=current+amount;return true;}))return false;
 }else{P.trainingShards-=times;P.trainingSpent+=times;P.zel-=cost;P.unitExp[baseId]=current+amount;saveProgress();}
 reset();renderProgress();''')
edit('  button.onclick=()=>{\n   // Verify the actual current form','   const renderedProgress=P;\n   button.onclick=()=>{\n    // Verify the actual current form')
edit('if(S?.busy||effectiveUnit(baseId).id!==(r.fromId||r.baseId)','if(S?.busy||!P.roster.includes(baseId)||P[OWNED_COPY_META]&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)||effectiveUnit(baseId)?.id!==(r.fromId||r.baseId)')
edit('   P.zel-=r.demoZel;for(const [id,n] of Object.entries(r.materials))P.materials[id]-=n;\n   P.evolutions[baseId]=r.evolvedId;P.unitExp[baseId]=0;\n   saveProgress();reset();renderProgress();','''    if(P[OWNED_COPY_META]){
     if(!copyCommitProgress(next=>{next.zel-=r.demoZel;for(const [id,n] of Object.entries(r.materials))next.materials[id]-=n;next.evolutions[baseId]=r.evolvedId;next.unitExp[baseId]=0;return true;}))return;
    }else{P.zel-=r.demoZel;for(const [id,n] of Object.entries(r.materials))P.materials[id]-=n;P.evolutions[baseId]=r.evolvedId;P.unitExp[baseId]=0;saveProgress();}
    reset();renderProgress();''')
edit("P.roster.length+'/'+ALL_IDS.length+' owned'","(P[OWNED_COPY_META]?P.roster.length+' owned copies':P.roster.length+'/'+ALL_IDS.length+' owned')")
edit(' for(const unit of STARTERS){\n  const owned=P.roster.includes(unit.id),chosen=P.squad.includes(unit.id)',' for(const unit of ownedCopyRows(true)){\n  const owned=P.roster.includes(unit.id),chosen=P.squad.includes(unit.id)')
edit('name.textContent=visible.name;','name.textContent=visible.name+(unit.id>=OWNED_COPY_FIRST?\' · Copy #\'+unit.id:\'\');')
edit('   check.onchange=()=>{\n    if(S?.busy||!P.roster.includes(unit.id))','   check.onchange=()=>{\n    if(S?.busy||!P.roster.includes(unit.id))') if False else None
edit('  check.onchange=()=>{\n   if(S?.busy||!P.roster.includes(unit.id)){check.checked=!check.checked;return}', '''  const renderedProgress=P;
  check.onchange=()=>{
   if(S?.busy||!P.roster.includes(unit.id)||P[OWNED_COPY_META]&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)){check.checked=!check.checked;return}
   if(P[OWNED_COPY_META]){
    const nextSquad=check.checked?[...new Set([...P.squad,unit.id])]:P.squad.filter(id=>id!==unit.id);
    if(nextSquad.length<1||nextSquad.length>6||!copyCommitProgress(next=>{next.squad=nextSquad;return true;})){check.checked=!check.checked;return;}
    reset();renderProgress();msg('Saved squad change; battle restarted.');return;
   }''')
# Do not expose acquisition to any normal build. Candidate tests call the function directly.
# Preserve native unique-only token and personal-Gem button behaviors.
edit('${P.roster.length}/${ALL_IDS.length} owned · ${remaining.length} recruits left','${P[OWNED_COPY_META]?P.roster.length+\' owned copies\':P.roster.length+\'/\'+ALL_IDS.length+\' owned\'} · ${remaining.length} recruits left')
# Reject high-ID Imp keys even if imported save lacks duplicate metadata.
edit('if(copies&&out._bfImpsV171&&Object.keys(out._bfImpsV171.amounts).some(k=>Number(k)>=OWNED_COPY_FIRST&&!Object.hasOwn(copies.baseById,k)))','if(out._bfImpsV171&&Object.keys(out._bfImpsV171.amounts).some(k=>Number(k)>=OWNED_COPY_FIRST&&(!copies||!Object.hasOwn(copies.baseById,k))))')
p.write_text(s);print('A6 index',hashlib.sha256(p.read_bytes()).hexdigest())
