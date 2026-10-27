"""v117: check ACTUAL generated playable unit stats against original 2022 Global masters.

The v116 catalog is independently sourced from the owner's original 2022
F_UNIT_MST_1/2. This test checks each unit that the built game really loads,
not just the archive's own row count. No gameplay patch or save mutation.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
v116=json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text('utf8'))
v112=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
v115=json.loads((R/'source_data/bf_global_2022_playable_level_caps_v115.json').read_text('utf8'))
assert v116['unitCount']==v112['totalForms']==v115['supportedForms']==72
assert {x['unitId'] for x in v116['rows']}=={x['unitId'] for x in v112['rows']}
assert v116['source']['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda exc:errors.append(str(exc)))
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('typeof UNIT_BY_ID')=='object'
 original=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf11600_original_lord_stats_data.js'))
 audit=p.evaluate("""()=>{
   const source=window.BFGlobalOriginalLordStatsDataV11600;
   if(!source||source.unitCount!==72)return {error:'missing source'};
   let found=0,matched=0,missing=[],mismatches=[],names=[];
   for(const row of source.rows){
     const current=UNIT_BY_ID.get(row.unitId);
     if(!current){missing.push(row.unitId);continue;}
     found++;
     names.push(current.name);
     for(const k of ['hp','atk','def','rec']){
       if(!Number.isSafeInteger(current.stats?.[k])||
          current.stats[k]!==row.base[k]){
         mismatches.push({id:row.unitId,k,current:current.stats?.[k],
                          original2022:row.base[k]});
       }else matched++;
     }
   }
   return {found,matched,missing,mismatches,distinctNames:new Set(names).size};
 }""")
 assert audit['found']==72,audit
 assert audit['matched']==72*4,audit
 assert audit['missing']==[] and audit['mismatches']==[],audit
 assert audit['distinctNames']==72,audit
 assert p.evaluate('JSON.stringify(P)')==original
 assert not errors,errors
 b.close()
print('PASS v117 actual generated playable catalog: all 72 original 2022 source base stat sets, 288/288 exact, save v7 unchanged')
