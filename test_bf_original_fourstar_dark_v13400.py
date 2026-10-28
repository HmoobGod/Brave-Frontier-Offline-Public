"""v134: source-exact 4-star Dark #60013 vertical flips and opacity proportions."""
from pathlib import Path
from PIL import Image
import base64,csv,hashlib,io,json,math,zipfile
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_more_second_stage_v034.json').read_text('utf8'))
data=base64.b64decode((R/'source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64').read_text('ascii'))
sha=lambda data:hashlib.sha256(data).hexdigest()
assert sha(data)==M['sourcePackSha256']
old='d556d3f64fe120cd2f9aeac296d92405d140d50860073362244909882bd309cf'
new='b12bdb2eea55eec3ec6ffe734923ad07ebccda10aca0e8ab5235c6a0d0c0cd40'
uid=60013
with zipfile.ZipFile(io.BytesIO(data)) as z:
 for filename,digest in M['records'][str(uid)]['sourceFilesSha256'].items():
  assert sha(z.read(filename))==digest,filename
 sheet=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
 rows=[[int(q) for q in row if q.strip()] for row in
       csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
 assert len(rows)==29
 original=Image.new('RGBA',(2400,2400),(0,0,0,0))
 corrected=Image.new('RGBA',original.size,(0,0,0,0))
 source_flips=[];source_opacity=[];parts=0
 for fi,row in enumerate(rows):
  assert row[0]==0 and len(row)==2+row[1]*11
  old_frame=Image.new('RGBA',(480,400),(0,0,0,0))
  new_frame=Image.new('RGBA',(480,400),(0,0,0,0))
  for li in range(row[1]):
   parts+=1
   dx,dy,flip,blend,opacity,rotate,x,y,w,h,page=row[2+11*li:13+11*li]
   assert (blend,rotate,page)==(0,0,0)
   assert flip in (0,2) and opacity in (30,50,70,100)
   assert x>=0 and y>=0 and w>0 and h>0 and x+w<=sheet.width and y+h<=sheet.height
   tile=sheet.crop((x,y,x+w,y+h))
   oldtile=tile
   if opacity!=100:
    source_opacity.append((fi,li,opacity))
    oldtile=tile.resize((max(1,round(w*opacity/100)),max(1,round(h*opacity/100))),Image.Resampling.NEAREST)
   old_frame.alpha_composite(oldtile,(220+dx,190+dy))
   if flip:
    source_flips.append((fi,li))
    tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   if opacity!=100:
    tile.putalpha(tile.getchannel('A').point(lambda alpha:round(alpha*opacity/100)))
   new_frame.alpha_composite(tile,(220+dx,190+dy))
  dst=((fi%5)*480,(fi//5)*400)
  original.alpha_composite(old_frame,dst)
  corrected.alpha_composite(new_frame,dst)
 assert parts==223
 assert source_flips==[(23,0),(24,0),(24,4),(24,5),(25,0),(26,0)]
 assert source_opacity==[(26,0,50),(26,1,50),(26,2,50),(26,3,70),(27,0,30)]
 def digest(im):
  out=io.BytesIO();im.save(out,format='PNG',optimize=True)
  return sha(out.getvalue())
 assert digest(original)==old
 assert digest(corrected)==new
 assert sha((A/'content/more_second_evolution/unit_anime_atlas_60013.png').read_bytes())==new
 for uid,digest in {
  10023:'baaacec6c344a462a92b384650eae720e204bdab1201a0b83a9bbc67e26c57c1',
  20023:'5982e1ed6d9011fbdb79f0882a6385b29b61a24a605ec1442f14ed564f07b07e',
  30023:'fe75fceff32d3357c9aecf078248ce78033c60de72ba853419c00b08f0fc0c46',
  40023:'8f70adee36e64feb15682d6b5722d46325b58049f67d87dc407dd9862cd90dfa',
  50023:'daf0a9eff2edc1d44602f041d7ae4f0ae4ca7db940d362dcb382155c61e97a46'
 }.items():
  assert sha((A/f'content/more_second_evolution/unit_anime_atlas_{uid}.png').read_bytes())==digest,uid
gen=(R/'prepare_original_more_second_stage.py').read_text('utf8')
assert 'BF_GLOBAL_4STAR_DARK_ALPHA_FLIP_V13400' in gen
assert 'BF_GLOBAL_4STAR_VERTICAL_FLIP_SOURCE_V13300' in gen
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
print('PASS v134: Dark 4star Black Magress 6 source vertical flips + 5 opacity fields; 5 other atlases and v7 saves unchanged')
