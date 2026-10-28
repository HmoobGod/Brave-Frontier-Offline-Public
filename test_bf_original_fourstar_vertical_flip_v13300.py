"""v133: exact 2022 Global CGG vertical-flip source recovery for three playable 4-stars."""
from pathlib import Path
from PIL import Image
import base64,csv,hashlib,io,json,math,zipfile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
manifest=json.loads((R/'source_data/bf_global_more_second_stage_v034.json').read_text('utf8'))
packed=base64.b64decode((R/'source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64').read_text('ascii'))
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(packed)==manifest['sourcePackSha256']
expected={
 20023:({'before':'392cb6a8a89f50b29bf3ead1ae154e118df13dff2ab280edf66560d025a8b619',
          'after':'5982e1ed6d9011fbdb79f0882a6385b29b61a24a605ec1442f14ed564f07b07e',
          'flips':[(6,2),(7,2),(9,0),(10,0)],'frames':15}),
 30023:({'before':'75f2e25cc127ea4585f0dbe32f0067f83080eeb7cfff9898fea7b5b126fbb63d',
          'after':'fe75fceff32d3357c9aecf078248ce78033c60de72ba853419c00b08f0fc0c46',
          'flips':[(7,0),(8,0),(9,1),(11,1)],'frames':14}),
 50023:({'before':'7eec053bf05f90eca64b4776743655162389f47af2c370b935ded4008ff66d82',
          'after':'daf0a9eff2edc1d44602f041d7ae4f0ae4ca7db940d362dcb382155c61e97a46',
          'flips':[(9,0),(10,0)],'frames':16})
}
with zipfile.ZipFile(io.BytesIO(packed)) as z:
 for uid,v in expected.items():
  ref=manifest['records'][str(uid)]
  for filename,digest in ref['sourceFilesSha256'].items():
   assert sha(z.read(filename))==digest,(uid,filename)
  sprite=Image.open(io.BytesIO(z.read(f'content/unit/img/unit_anime_{uid}.png'))).convert('RGBA')
  rows=[[int(x) for x in row if x.strip()] for row in
        csv.reader(io.StringIO(z.read(f'content/unit/cgg/unit_cgg_{uid}.csv').decode('utf-8-sig')))]
  assert len(rows)==v['frames']
  atlas=Image.new('RGBA',(2400,400*math.ceil(len(rows)/5)),(0,0,0,0))
  flipped=[];old=Image.new('RGBA',atlas.size,(0,0,0,0))
  for fi,row in enumerate(rows):
   assert row[0]==0 and len(row)==2+11*row[1]
   frame=Image.new('RGBA',(480,400),(0,0,0,0))
   before=Image.new('RGBA',frame.size,(0,0,0,0))
   for li in range(row[1]):
    dx,dy,flip,blend,opacity,rotation,x,y,w,h,page=row[2+11*li:13+11*li]
    assert (blend,opacity,rotation,page)==(0,100,0,0)
    assert flip in (0,2)
    assert 0<=x and 0<=y and w>0 and h>0 and x+w<=sprite.width and y+h<=sprite.height
    tile=sprite.crop((x,y,x+w,y+h))
    before.alpha_composite(tile,(220+dx,190+dy))
    if flip:
     flipped.append((fi,li))
     tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    frame.alpha_composite(tile,(220+dx,190+dy))
   dst=((fi%5)*480,(fi//5)*400)
   old.alpha_composite(before,dst)
   atlas.alpha_composite(frame,dst)
  assert flipped==v['flips'],(uid,flipped)
  def digest(im):
   out=io.BytesIO();im.save(out,format='PNG',optimize=True)
   return sha(out.getvalue())
  assert digest(old)==v['before'],uid
  assert digest(atlas)==v['after'],uid
  assert sha((A/f'content/more_second_evolution/unit_anime_atlas_{uid}.png').read_bytes())==v['after'],uid
 for uid,digest in {
  10023:'baaacec6c344a462a92b384650eae720e204bdab1201a0b83a9bbc67e26c57c1',
  40023:'8f70adee36e64feb15682d6b5722d46325b58049f67d87dc407dd9862cd90dfa',
  60013:'b12bdb2eea55eec3ec6ffe734923ad07ebccda10aca0e8ab5235c6a0d0c0cd40'
 }.items():
  assert sha((A/f'content/more_second_evolution/unit_anime_atlas_{uid}.png').read_bytes())==digest,uid
source=(R/'prepare_original_more_second_stage.py').read_text('utf8')
assert 'BF_GLOBAL_4STAR_VERTICAL_FLIP_SOURCE_V13300' in source
assert 'Image.Transpose.FLIP_TOP_BOTTOM' in source
html=(A/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
assert 'bf_global_offline_demo_v7' in html
print('PASS v133: 10 original vertical-flip layers on playable 4-star Water/Earth/Light; 3 other atlases and v7 saves unaffected')
