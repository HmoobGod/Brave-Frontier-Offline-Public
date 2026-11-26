"""A12 refactor: preserve v070-owned blocks and native nav byte budget."""
import hashlib, pathlib, sys
root=pathlib.Path(sys.argv[1]);base=pathlib.Path(sys.argv[2]);here=pathlib.Path(__file__).resolve().parent
p=root/'index.html';s=p.read_text();nav=base/'bf_home_nav.js';n=nav.read_text()
def replace(s,a,b):
 if s.count(a)!=1:raise ValueError(('anchor mismatch',a[:100],s.count(a)))
 return s.replace(a,b,1)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='f92b02561f3750264665993dd904230fbdd1686bc5779295b76c81be904c26dc'
assert hashlib.sha256(nav.read_bytes()).hexdigest()=='9dec0e6b0859ea9cc0feac2b534a1179a1514b623ccab3ba6524cf17de655e30'
s=replace(s,"  // Archive-only forms are source IDs, not owned instance IDs.\n  const u=effectiveUnit(base.id)||UNIT_BY_ID.get(base.id);if(!u)continue;const op=document.createElement('option');","  const u=effectiveUnit(base.id),op=document.createElement('option');")
s=replace(s,'function renderHitInspector(){','''// Read-only inspector fallback for archive-only form IDs; never used by ownership or combat.
function stackInspectorUnit(id){return effectiveUnit(id)||UNIT_BY_ID.get(id);}
function renderHitInspector(){
 const effectiveUnit=stackInspectorUnit;''')
# Keep the generator-owned block AND selection restore byte-identical.
original=(base/'index.html').read_text();block=original.split(' /* BF_PLAYABLE_HIT_INSPECTOR_V070 */',1)[1].split(' const uid=Number(E.hitunit.value)',1)[0]
assert s.count(' /* BF_PLAYABLE_HIT_INSPECTOR_V070 */'+block)==1
n=replace(n,'  let activeId = null;','  let activeId=null,c=window.BFStackCopies?.mount(results,refresh);')
n=replace(n,'    const {owned, filtered, unresolved}=ownedUnits();','    if(c)activeId=c.before(activeId);\n    const {owned, filtered, unresolved}=ownedUnits();')
n=replace(n,'    if (activeId != null && filtered.some(row => row.id === activeId)) showDetail(activeId);','    c?.group(filtered,activeId);\n    if (activeId != null && filtered.some(row => row.id === activeId)) showDetail(activeId);')
n=replace(n,"    for (const card of results.querySelectorAll('button[data-bf-unit-id]')) card.setAttribute('aria-pressed', String(Number(card.dataset.bfUnitId) === id));", "    for (const card of results.querySelectorAll('button[data-bf-unit-id]')) card.setAttribute('aria-pressed', String(Number(card.dataset.bfUnitId) === id));\n    c?.select(id);")
n=replace(n,'const recipe=EVO_RECIPES.find(row=>row.baseId===id);','const recipe=EVO_RECIPES.find(row=>row.baseId===(c?c.base(id):id));')
# Preserve legacy label while shortening redundant whitespace/comment only in touched scope.
n=replace(n,"form.textContent='Base roster ID '+id+", "form.textContent=(c?'Owned ID ':'Base roster ID ')+id+")
n=replace(n,'    // The recovered evolution relationship is shown as a preview only.\n    // Its source stats are not computed by the demo battle formula and this\n    // panel never consumes Zel, catalysts, levels or changes saved forms.','    // Read-only evolution preview; no resource or save changes.')
assert len(n.encode())<=131072
p.write_text(s);(root/'bf_home_nav.js').write_text(n);(root/'bf_stack_copies.js').write_bytes((here/'bf_stack_copies.js').read_bytes())
print('A12 nav/module bytes',len(n.encode()),(root/'bf_stack_copies.js').stat().st_size)
