"""v132: source-preserving original 6★ Thunder #40025 2 alpha layers + 1 horizontal flip.
Independent raster recreation; no inference about unrelated BF1 CGG semantics.
"""
from pathlib import Path
from PIL import Image
import base64,csv,hashlib,io,json,math,zipfile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_other_six_star_v038.json').read_text('utf8'))
packed=base64.b64decode((R/'source_assets/bf1/BF1_Global_2022_Other_Six_Star.zip.b64').read_text('ascii'))
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(packed)==manifest['sourcePackSha256']
uid=40025
old='54a3adb6dafe3fd52a6797223b12354f1d8ce403972e92e69fd6af614f773c07'
new='7273c43cead5d10c1ba47b59888379a808411c3ed7a3fa1894a277e970ccc90b'
assert old!=new
with zipfile.ZipFile(io.BytesIO(packed)) as z:
 for filename,digest in manifest['records'][str(uid)]['sourceFilesSha256'].items():
  assert sha(z.read(filename))==digest,filename
 sprite=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 rows=[[int(x) for x in row if x.strip()] for row in
       csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
 assert len(rows)==27
 atlas=Image.new('RGBA',(2400,400*math.ceil(len(rows)/5)),(0,0,0,0))
 transformations=[];total_layers=0
 for fi,row in enumerate(rows):
  assert row[0]==0 and len(row)==2+row[1]*11
  frame=Image.new('RGBA',(480,400),(0,0,0,0))
  for li in range(row[1]):
   total_layers+=1
   dx,dy,flip,blend,opacity,rotate,x,y,w,h,page=row[2+11*li:13+11*li]
   assert (blend,rotate,page)==(0,0,0)
   assert flip in (0,1) and opacity in (50,100)
   assert 0<=x and 0<=y and 0<w and 0<h and x+w<=sprite.width and y+h<=sprite.height
   tile=sprite.crop((x,y,x+w,y+h))
   if flip==1:
    transformations.append((fi,li,'flip',1))
    tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if opacity!=100:
    transformations.append((fi,li,'opacity',opacity))
    tile.putalpha(tile.getchannel('A').point(lambda alpha:round(alpha*opacity/100)))
   frame.alpha_composite(tile,(220+dx,190+dy))
  atlas.alpha_composite(frame,((fi%5)*480,(fi//5)*400))
 assert total_layers==232
 assert transformations==[(6,6,'opacity',50),(15,1,'flip',1),(24,0,'opacity',50)],transformations
 out=io.BytesIO();atlas.save(out,format='PNG',optimize=True)
 assert sha(out.getvalue())==new
 assert sha((A/'content/other_six_star/unit_anime_atlas_40025.png').read_bytes())==new
 for n,digest in {
    10025:'44273ed1d068b019aeb7831e53691283413a33353b550b5d3f8a090370cfdeff',
    20025:'e54782dbc6e5634eb6c49135a95b3486009e8704d5fbc6bbdee009a815394734',
    30025:'53295c806e6390e05a74e7ed124e709e9c677753070fc44eb1e3c262131623b5',
    50025:'93a419d6f0f2be0dcf23d83f07445e5d4e7e297a5c95cc39ca4448cb811f5e65',
    60025:'d4ab800085681df9fc5bbb6e20ed36df998c6b5fc541797ce35425fb5f49d3df'
 }.items():
  assert sha((A/f'content/other_six_star/unit_anime_atlas_{n}.png').read_bytes())==digest,n
source=(R/'prepare_original_other_six_star.py').read_text('utf8')
assert 'BF_GLOBAL_6STAR_THUNDER_FLIP_OPACITY_V13200' in source
assert "uid==40025" in source and 'FLIP_LEFT_RIGHT' in source
assert "tile.getchannel('A').point" in source
assert "BF_GLOBAL_6STAR_OPACITY_FIX_V13100" in source
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert html.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
print('PASS v132: original 6star Thunder #40025: 1 horizontal flip + 2 half-alpha CGG layers; five other atlases + v7 save unchanged')
