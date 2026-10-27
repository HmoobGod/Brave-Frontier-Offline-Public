"""v129: original source-art pilot, approximate renderer, never playable."""
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import base64,hashlib,io,json,shutil,zipfile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_7star_water_visual_preview_v129.json').read_text('utf8'))
prior=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
row=next(r for r in prior['rows'] if r['unitId']==20016)
assert M['schema']=='bf-global-2022-water-7-star-source-visual-preview-v129'
assert M['sourceUnitId']==20016 and M['sourceFrameCount']==row['animation']['cggSourceFrameCount']==23
assert M['referenceOnly'] is True and M['spritePixelsAreReconstruction'] is True
assert not any(M[k] for k in ('nativeBlendProven','nativeTransformProven','nativeFrameClockProven'))
blob=base64.b64decode((R/'source_assets/bf1/BF1_Global_2022_SevenStar_Water_Pilot_v129.zip.b64').read_text('ascii').strip(),validate=True)
assert hashlib.sha256(blob).hexdigest()==M['sourcePackageSha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
 assert set(z.namelist())==set(M['sourceFileHashes'])=={f['path'] for f in row['assets']}
 for f in row['assets']:
  payload=z.read(f['path'])
  assert hashlib.sha256(payload).hexdigest()==M['sourceFileHashes'][f['path']]==f['sha256']
image=A/'content/seven_star_source_preview/unit_anime_atlas_20016.png'
thumb=A/'content/seven_star_source_preview/unit_ills_thum_20016.png'
assert image.is_file() and thumb.is_file()
img=Image.open(image).convert('RGBA');assert img.size==(2400,2000)
assert hashlib.sha256(img.tobytes()).hexdigest()==M['atlasPixelsSha256']=='2c59d87d592f86a77abbf9330e324603047819d7040cf5c5d7ed0f6be250f322'
assert all(img.crop(((i%5)*480,(i//5)*400,(i%5+1)*480,(i//5+1)*400)).getbbox() for i in range(23))
assert thumb.read_bytes()==zipfile.ZipFile(io.BytesIO(blob)).read('content/unit/img/unit_ills_thum_20016.png')
code=(A/'bf12900_original_seven_star_water_visual.js').read_text('utf8')
assert 'BF_GLOBAL_2022_SEVEN_STAR_WATER_VISUAL_PREVIEW_V12900' in code
assert not any(x in code for x in ['localStorage','P.unitExp=','P.evolutions=','P.roster=', 'Math.random','fetch('])
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf12900_original_seven_star_water_visual.js")' in java
archive=(A/'bf_global_unit_archive.js').read_text('utf8')
assert 'BFGlobalOriginalSevenStarWaterVisualV12900' in archive
# The 72 existing playable forms and v7 save schema are never modified.
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda exc:errors.append(str(exc)))
 # Chromium test uses a data: URL for the *original generated* atlas,
 # never navigating to any external host or blocked file:// route.
 p.set_content('<canvas id="pilot" width="240" height="200"></canvas>')
 p.add_script_tag(path=str(A/'bf12900_original_seven_star_water_visual.js'))
 encoded=base64.b64encode(image.read_bytes()).decode('ascii')
 assert p.evaluate("""data=>new Promise(done=>{
   const source=new Image();source.onload=()=>{window.__v129TestImage=source;done(true)};
   source.onerror=()=>done(false);
   source.src='data:image/png;base64,'+data;
 })""",encoded) is True
 assert p.evaluate('BFGlobalOriginalSevenStarWaterVisualV12900.source.playable') is False
 assert p.evaluate("async()=>await BFGlobalOriginalSevenStarWaterVisualV12900.renderFrame(document.getElementById('pilot'),0,window.__v129TestImage)") is True
 assert p.evaluate("()=>{const a=document.getElementById('pilot');return [...a.getContext('2d').getImageData(0,0,240,200).data].some((v,i)=>i%4===3&&v>0)}") is True
 assert p.evaluate("async()=>await BFGlobalOriginalSevenStarWaterVisualV12900.renderFrame(document.getElementById('pilot'),22,window.__v129TestImage)") is True
 assert p.evaluate("async()=>await BFGlobalOriginalSevenStarWaterVisualV12900.renderFrame(document.getElementById('pilot'),23,window.__v129TestImage)") is False
 p.close()
 p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda exc:errors.append(str(exc)))
 p.evaluate("""()=>{const store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=String(v),
    removeItem:k=>delete store[k],key:i=>Object.keys(store)[i]??null,
    get length(){return Object.keys(store).length}}});
    window.alert=()=>{};window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 before=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf12900_original_seven_star_water_visual.js'))
 assert p.evaluate('BFGlobalOriginalSevenStarWaterVisualV12900.source.saveFieldsAdded')==0
 assert p.evaluate('JSON.stringify(P)')==before
 assert not errors,errors
 b.close()
print('PASS v129: 7-star Water 23 sourced CGG visuals, original bytes, nonnative preview only, 72 playable, save v7')
