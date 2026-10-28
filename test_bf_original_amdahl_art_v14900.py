"""v149 source-verified 2022 Amdahl offline art and read-only map inspector."""
from pathlib import Path
import hashlib,json,zipfile,shutil,base64,io
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_amdahl_original_art_v149.json').read_text('utf8'))
Q=json.loads((R/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
P=R/'source_assets/bf1/amdahl/BF1_Global_2022_Amdahl_Original_Art_v149.zip.b64'
sha=lambda x:hashlib.sha256(x).hexdigest()
packed=base64.b64decode(P.read_text('ascii'))
assert sha(packed)==M['packagedZipSha256']
assert len(M['sourceImages'])==9 and len(M['dungeons'])==7
with zipfile.ZipFile(io.BytesIO(packed)) as z:
 for name,metadata in M['sourceImages'].items():
  src=z.read(name);dst=(A/name).read_bytes()
  assert src==dst and sha(dst)==metadata['sha256'] and len(src)==metadata['bytes']
js=(A/'bf14900_original_amdahl_art.js').read_text('utf8')
assert 0<len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_AMDAHL_ORIGINAL_ART_VIEW_V14900')==1
assert 'sourceYear:2022' in js and 'originalGameplayEnabled:false' in js
assert "ownerSourceSha256:'65790b0c0e9099fedb347e4a0c53f76bde7ebe3ea0cb7b9089557cf51c759179'" in js
assert 'saveProgress(' not in js and 'localStorage.' not in js and 'BFAndroid' not in js
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('bf100_grand_gaia_campaign.js') < java.index('bf14900_original_amdahl_art.js')
assert 'bf_global_offline_demo_v7' in (A/'index.html').read_text('utf8')
assert Q['area']['playableNow'] is False
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  path=(A/urlsplit(route.request.url).path.lstrip('/')).resolve()
  if not path.is_relative_to(A.resolve()) or not path.is_file():
   route.fulfill(status=404,body=b'');return
  ext=path.suffix.lower();mime='image/jpeg' if ext=='.jpg' else 'image/png' if ext=='.png' else 'text/javascript'
  route.fulfill(status=200,body=path.read_bytes(),content_type=mime)
 page.route('http://bf-original.test/**',serve)
 page.set_content('<!doctype html><html><head><base href="http://bf-original.test/"></head><body><div id="bf100-campaign"></div></body></html>')
 page.evaluate('''()=>{window.BFGrandGaiaCampaignV100={};window.P={version:7,squad:[10011],questClears:{365:1}};
   window.S={busy:false,party:[{unitId:10011}]};window.QUESTS=Array.from({length:106},(_,i)=>({missionId:i+1}));
   const saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>saved[k]??null,setItem:(k,v)=>saved[k]=String(v)}})}''')
 original=page.evaluate('''()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})''')
 page.add_script_tag(path=str(A/'bf14900_original_amdahl_art.js'))
 assert page.locator('#bf14900-amdahl-art').count()==1
 assert page.evaluate('BFAmdahlOriginalArtV14900.entries.length')==7
 assert page.evaluate('BFAmdahlOriginalArtV14900.source.originalGameplayEnabled') is False
 assert page.locator('[data-bf14900-dungeon]').count()==7
 assert page.evaluate('BFAmdahlOriginalArtV14900.lookup(460).name')=='Amdahl Castle'
 assert page.evaluate('BFAmdahlOriginalArtV14900.lookup(9999)') is None
 page.locator('#bf14900-amdahl-art summary').click()
 page.locator('[data-bf14900-dungeon="460"]').click()
 assert 'Amdahl Castle' in page.locator('#bf14900-selected').inner_text()
 assert 'not in the playable' in page.locator('#bf14900-selected').inner_text()
 assert page.locator('#bf14900-selected img').evaluate('(e)=>e.complete && e.naturalWidth>0') is True
 assert page.locator('#bf14900-amdahl-art div > img').first.evaluate('(e)=>e.complete && e.naturalWidth>0') is True
 assert page.evaluate('BFAmdahlOriginalArtV14900.preview(9999)') is False
 after=page.evaluate('''()=>({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7')})''')
 assert after==original
 assert not errors,errors
 browser.close()
print('PASS v149 original Amdahl 2022 world+seven battle JPEG maps, source coords, 7 responsive pins, no save/quest mutations')
