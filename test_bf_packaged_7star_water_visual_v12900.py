"""v129: only check that the read-only original-image reconstruction is packaged."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
meta=json.loads((R/'source_data/bf_global_7star_water_visual_preview_v129.json').read_text())
name='app/build/outputs/apk/debug/app-debug.apk'
p=R/name
assert p.is_file(),name
with zipfile.ZipFile(p) as z:
 names=set(z.namelist())
 png='assets/content/seven_star_source_preview/unit_anime_atlas_20016.png'
 thumb='assets/content/seven_star_source_preview/unit_ills_thum_20016.png'
 js='assets/bf12900_original_seven_star_water_visual.js'
 assert {png,thumb,js}.issubset(names)
 from PIL import Image
 import io
 image=Image.open(io.BytesIO(z.read(png))).convert('RGBA')
 assert image.size==(2400,2000)
 assert hashlib.sha256(image.tobytes()).hexdigest()==meta['atlasPixelsSha256']
 code=z.read(js).decode('utf8')
 assert 'playable:false' in code and 'saveFieldsAdded:0' in code
 assert all(t not in code for t in ['P.unitExp=','P.roster=','P.evolutions='])
print('PASS packaged v129 7-star original-source art reconstruction, no playability or save change')
