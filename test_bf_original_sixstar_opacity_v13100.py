"""v131: source-backed 6★ #30025 alpha correction; isolate all 71 other attack atlases."""
from pathlib import Path
from PIL import Image
import base64,csv,hashlib,io,json,math,zipfile
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets';S=R/'source_assets/bf1'
manifest=json.loads((R/'source_data/bf_global_other_six_star_v038.json').read_text('utf8'))
packed=base64.b64decode((S/'BF1_Global_2022_Other_Six_Star.zip.b64').read_text('ascii'))
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(packed)==manifest['sourcePackSha256']
old='fb7c5d78417740e862c2c42de70a430efec0698f6e8000a04d1a3a0ba62f733e'
new='53295c806e6390e05a74e7ed124e709e9c677753070fc44eb1e3c262131623b5'
unchanged={10025:'44273ed1d068b019aeb7831e53691283413a33353b550b5d3f8a090370cfdeff',
 20025:'e54782dbc6e5634eb6c49135a95b3486009e8704d5fbc6bbdee009a815394734',
 40025:'7273c43cead5d10c1ba47b59888379a808411c3ed7a3fa1894a277e970ccc90b',
 50025:'93a419d6f0f2be0dcf23d83f07445e5d4e7e297a5c95cc39ca4448cb811f5e65',
 60025:'d4ab800085681df9fc5bbb6e20ed36df998c6b5fc541797ce35425fb5f49d3df'}
with zipfile.ZipFile(io.BytesIO(packed)) as z:
 uid=30025
 for file,digest in manifest['records'][str(uid)]['sourceFilesSha256'].items():
  assert sha(z.read(file))==digest
 sheet=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 frames=[[int(x) for x in row if x.strip()] for row in csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
 assert len(frames)==23
 target=Image.new('RGBA',(2400,2000),(0,0,0,0)); affected=[]
 for fi,row in enumerate(frames):
  assert len(row)==2+row[1]*11 and row[0]==0
  frame=Image.new('RGBA',(480,400),(0,0,0,0))
  for li in range(row[1]):
   dx,dy,flip,blend,opacity,rotation,sx,sy,w,h,page=row[2+li*11:13+li*11]
   assert (flip,blend,rotation,page)==(0,0,0,0)
   assert 0<opacity<=100 and sx>=0 and sy>=0 and sx+w<=sheet.width and sy+h<=sheet.height
   part=sheet.crop((sx,sy,sx+w,sy+h))
   if opacity!=100:
    affected.append([fi,li,opacity])
    part.putalpha(part.getchannel('A').point(lambda a:round(a*opacity/100)))
   frame.alpha_composite(part,(220+dx,190+dy))
  target.alpha_composite(frame,((fi%5)*480,(fi//5)*400))
 assert affected==[[19,i,50] for i in range(3,9)],affected
 buffer=io.BytesIO();target.save(buffer,format='PNG',optimize=True)
 assert sha(buffer.getvalue())==new
 assert sha((A/'content/other_six_star/unit_anime_atlas_30025.png').read_bytes())==new
 assert new!=old
 for n,expected in unchanged.items():
  assert sha((A/f'content/other_six_star/unit_anime_atlas_{n}.png').read_bytes())==expected,n
 source=(R/'prepare_original_other_six_star.py').read_text('utf8')
 assert 'BF_GLOBAL_6STAR_OPACITY_FIX_V13100' in source
 assert 'uid==30025' in source
 assert "tile.getchannel('A').point" in source
 assert "# Original column 4 is opacity" in source
 html=(A/'index.html').read_text('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert html.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
 assert 'const BF_VERIFIED_RAW_LEVELS_V038' in html
print('PASS v131: 30025 original 6-star frame19 6×50% CGG opacity source pixel correction; other 5 atlases unchanged, save v7')
