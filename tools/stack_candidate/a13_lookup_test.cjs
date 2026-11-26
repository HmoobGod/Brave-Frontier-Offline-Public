/* Extract actual native functions and catalogue, no fabricated game functions. */
const fs=require('node:fs'),path=require('node:path');const root=process.argv[2];if(!root)throw Error('Asset dir required');const s=fs.readFileSync(path.join(root,'index.html'),'utf8');
const prior=fs.readFileSync(path.join(__dirname,'a6_test.cjs'),'utf8');const init=prior.slice(prior.indexOf('function extract(mark)'),prior.indexOf('const mem=new Map()'));
const fixture=new Function('s',init+'\nreturn {window,recipes,a,init};')(s);
const api=new Function('window','recipes',fixture.init+fixture.a+`\nlet P=defaultProgress();\nreturn {get:()=>P,look:id=>effectiveUnit(id),copy:id=>stackOwnedUnit(id),source:id=>UNIT_BY_ID.get(id),stub:f=>effectiveUnit=f};`)(fixture.window,fixture.recipes);
let n=0;function check(v,name){if(!v)throw Error(name);console.log('PASS',name);n++}
const p=api.get(),unowned=10012,base=10021,id=1000000001,orphan=1000000002;
check(!p.roster.includes(unowned)&&api.look(unowned)===api.source(unowned)&&!!api.look(unowned),'original unowned archive form remains resolvable');
p.roster.push(base,id);p._bfUnitInstancesV1={nextId:orphan+1,baseById:{[id]:base,[orphan]:base}};p.unitExp[id]=0;
check(api.copy(id)===api.source(base)&&api.look(id)===undefined,'unevolved copy uses only owned resolver');
p.evolutions[id]=10022;
check(api.copy(id)===api.source(10022)&&api.copy(base)===api.source(base),'evolved copy keeps source and original distinct');
check(api.copy(String(id))===undefined,'string alias to evolved copy rejected');
p.evolutions[orphan]=10022;check(api.copy(orphan)===undefined,'unowned forged high ID rejected even with evolution and mapping');
p.evolutions[1000000001.5]=10022;check(api.copy(1000000001.5)===undefined,'fractional high ID rejected');
check(api.copy(10000000000)===undefined,'out-of-range copy rejected');
const roster=p.roster;p.roster=null;check(api.copy(id)===undefined,'missing roster refuses copy');p.roster=roster;
const before=api.copy(id);api.stub(x=>({id:x,name:'legacy fixture'}));check(api.copy(unowned).name==='legacy fixture'&&api.copy(id)===before,'legacy dynamic lookup and copy path remain independent');
console.log('TOTAL',n);
