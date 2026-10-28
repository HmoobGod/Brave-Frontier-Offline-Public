"""v146: source-verified 2022 Global Death Magress 5-star sprite fidelity.

Independently reproduce the exact v124 old sprite, new vertical flips and
opacity from the original owner-supplied CGG/PNG. Leave other five intact.
"""
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
expected_flips={(24,1),(24,8),(25,8),(25,12),
                (26,8),(26,9),(26,11),(26,12)}
expected_alpha={
 (26,0):60,(26,1):60,(26,2):60,(26,3):60,
 (26,4):60,(26,5):60,(26,6):60,(26,7):60,
 (26,8):60,(26,9):60,(26,11):80,(26,12):80,
 (26,13):80,(27,0):30,(27,1):30,(27,2):30,
 (27,3):30,(28,0):40}
assert len(expected_flips)==8 and len(expected_alpha)==18
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for filename,digest in M['records'][str(uid)]['sourceFilesSha256'].items():
  assert sha(z.read(filename))==digest,filename
 sheet=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 assert sheet.size==(512,512)
 rows=[[int(t) for t in r if t.strip()] for r in
       csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
 assert len(rows)==30
 old_img=Image.new('RGBA',(2400,2400),(0,0,0,0))
 new_img=Image.new('RGBA',old_img.size,(0,0,0,0))
 flips=set();alphas={};num_layers=0
 for fi,row in enumerate(rows):
  assert row[0]==0 and len(row)==2+row[1]*11
  before=Image.new('RGBA',(480,400),(0,0,0,0))
  after=before.copy()
  for li in range(row[1]):
   num_layers+=1
   dx,dy,flip,blend,opacity,rotation,x,y,w,h,page=row[2+li*11:13+li*11]
   assert (blend,rotation,page)==(0,0,0)
   assert flip in (0,2) and opacity in (30,40,60,80,100)
   assert x>=0 and y>=0 and w>0 and h>0 and x+w<=sheet.width and y+h<=sheet.height
   assert 0<=220+dx and 0<=190+dy and 220+dx+w<=480 and 190+dy+h<=400
   tile=sheet.crop((x,y,x+w,y+h))
   old_tile=tile if opacity==100 else tile.resize(
        (max(1,round(w*opacity/100)),max(1,round(h*opacity/100))),Image.Resampling.NEAREST)
   before.alpha_composite(old_tile,(220+dx,190+dy))
   if flip==2:
    flips.add((fi,li));tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   if opacity!=100:
    alphas[(fi,li)]=opacity
    tile.putalpha(tile.getchannel('A').point(lambda a:round(a*opacity/100)))
   after.alpha_composite(tile,(220+dx,190+dy))
  position=((fi%5)*480,(fi//5)*400)
  old_img.alpha_composite(before,position)
  new_img.alpha_composite(after,position)
 assert num_layers==251
 assert flips==expected_flips,(flips,expected_flips)
 assert alphas==expected_alpha,(alphas,expected_alpha)
 assert len(flips | set(alphas))==22
 def digest(img):
  b=io.BytesIO();img.save(b,format='PNG',optimize=True)
  return sha(b.getvalue())
 assert digest(old_img)==old,'original v124 atlas not reproducible'
 assert digest(new_img)==new,'new CGG source rendering changed'
 assert sha((A/f'content/five_star_evolution/unit_anime_atlas_{uid}.png').read_bytes())==new
 for unaffected,expected in {
   10014:'5bb571fb4e5dedd8f73571cd66722320f14d220acbd64c66a383cb645914c6be',
   20014:'b9760f2c651ae4690d0cb4ae88e80f3271d6239fd1f2aeb9bf906e3a645f7f3d',
   30014:'0d358473737b353d5b99719457fe94a1776f17caaf87841f274de272c324feea',
   40014:'8eff7c31a1ebd67da807d3fc6004fdf594b0e8b02d404f1e6e03184fca3d5d08',
   50014:'b498a6f2b48f5e02ed90fe3e53801835b417b9463bcaa4bd787497383614d068'
 }.items():
  assert sha((A/f'content/five_star_evolution/unit_anime_atlas_{unaffected}.png').read_bytes())==expected,unaffected
 script=(R/'prepare_original_five_star_starters.py').read_text('utf8')
 assert 'BF_GLOBAL_5STAR_DARK_SOURCE_CGG_V14600' in script
 assert 'if id==60014:' in script
 assert 'Image.Transpose.FLIP_TOP_BOTTOM' in script
 html=(A/'index.html').read_text('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
 print('PASS v146: Death Magress 5-star 251 original layers; 8 flips, 18 alpha, 22 affected positions, other five unchanged, v7 save preserved')
