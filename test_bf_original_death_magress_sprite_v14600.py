"""v146: independently reconstruct original 2022 Global 5-star Death Magress pixels."""
from pathlib import Path
from PIL import Image
import base64,csv,hashlib,io,json,math,zipfile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_six_five_star_v035.json').read_text('utf8'))
pack=base64.b64decode((R/'source_assets/bf1/BF1_Global_2022_Six_Five_Star.zip.b64').read_text('ascii'))
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(pack)==M['sourcePackSha256']
uid=60014
old='3301ac9b3bb828ed31d3146a128833602013ef0a236a6a6709e0f90b14548b0d'
new='e8582ed0a8a1eba005b208def14d97ba8f2892d38c83629941b536c2ac7b2b46'
record=M['records'][str(uid)]
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for file,digest in record['sourceFilesSha256'].items():
  assert sha(z.read(file))==digest,file
 sheet=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 assert sheet.size==(512,512)
 rows=[[int(v) for v in row if v.strip()] for row in
        csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
 assert len(rows)==30==record['frameCount']
 before=Image.new('RGBA',(2400,2400),(0,0,0,0))
 after=Image.new('RGBA',before.size,(0,0,0,0))
 got=[]
 for fi,row in enumerate(rows):
  assert row[0]==0 and len(row)==2+row[1]*11
  oldframe=Image.new('RGBA',(480,400),(0,0,0,0))
  newframe=Image.new('RGBA',(480,400),(0,0,0,0))
  for li in range(row[1]):
   dx,dy,flip,blend,alpha,rotation,x,y,w,h,page=row[2+11*li:13+11*li]
   assert (blend,rotation,page)==(0,0,0)
   assert flip in (0,2) and alpha in (30,40,60,80,100)
   assert x>=0 and y>=0 and w>0 and h>0 and x+w<=sheet.width and y+h<=sheet.height
   tile=sheet.crop((x,y,x+w,y+h))
   oldtile=tile
   if alpha!=100:
    oldtile=tile.resize((max(1,round(w*alpha/100)),max(1,round(h*alpha/100))),Image.Resampling.NEAREST)
   oldframe.alpha_composite(oldtile,(220+dx,190+dy))
   if flip:
    tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   if alpha!=100:
    tile.putalpha(tile.getchannel('A').point(lambda v:round(v*alpha/100)))
   newframe.alpha_composite(tile,(220+dx,190+dy))
   if flip or alpha!=100:
    got.append({'frame':fi,'layer':li,'orientationCode':flip,'scalePercent':alpha})
  pos=((fi%5)*480,(fi//5)*400)
  before.alpha_composite(oldframe,pos)
  after.alpha_composite(newframe,pos)
 assert len(got)==22,got
 assert got==record['unverifiedSpriteTransformLayers']
 assert sum(x['orientationCode']==2 for x in got)==8
 assert sum(x['scalePercent']!=100 for x in got)==18
 def digest(im):
  data=io.BytesIO();im.save(data,format='PNG',optimize=True)
  return sha(data.getvalue())
 assert digest(before)==old
 assert digest(after)==new
 assert sha((A/'content/five_star_evolution/unit_anime_atlas_60014.png').read_bytes())==new
 for n,h in {
  10014:'5bb571fb4e5dedd8f73571cd66722320f14d220acbd64c66a383cb645914c6be',
  20014:'b9760f2c651ae4690d0cb4ae88e80f3271d6239fd1f2aeb9bf906e3a645f7f3d',
  30014:'0d358473737b353d5b99719457fe94a1776f17caaf87841f274de272c324feea',
  40014:'8eff7c31a1ebd67da807d3fc6004fdf594b0e8b02d404f1e6e03184fca3d5d08',
  50014:'b498a6f2b48f5e02ed90fe3e53801835b417b9463bcaa4bd787497383614d068'
 }.items():
  assert sha((A/f'content/five_star_evolution/unit_anime_atlas_{n}.png').read_bytes())==h,n
script=(R/'prepare_original_five_star_starters.py').read_text('utf8')
assert 'BF_GLOBAL_DEATH_MAGRESS_CGG_ALPHA_FLIP_V14600' in script
assert 'if id==60014:' in script
assert 'Image.Transpose.FLIP_TOP_BOTTOM' in script
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
print('PASS v146: original 5-star Death Magress 8 vertical flips / 18 alpha layers, byte-exact old/new source graphics, 5 other 5-star assets and v7 save unchanged')
