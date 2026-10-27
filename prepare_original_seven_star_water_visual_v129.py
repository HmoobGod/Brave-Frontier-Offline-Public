from pathlib import Path
import zipfile,io,base64,json,csv,hashlib
from PIL import Image, ImageChops
# 2022 original source files were extracted with pinned SHA from the owner's
# BF1 archive. Only original source pixels are read. Preview compositing is
# explicitly NON-NATIVE and is never used by playable unit logic.
ROOT=Path(__file__).resolve().parent
unit=20016
manifest=json.loads((ROOT/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
entry=next(x for x in manifest['rows'] if x['unitId']==unit)
blob=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_SevenStar_Water_Pilot_v129.zip.b64').read_text('ascii').strip(),validate=True)
assert hashlib.sha256(blob).hexdigest()=='0e23e955e2f7548000c6891f1718c9773d8f459a1aef165b1b34d8c772bae33d'
source=zipfile.ZipFile(io.BytesIO(blob))
names=sorted(source.namelist());assert names==sorted(x['path'] for x in entry['assets'])
for file in entry['assets']:
    data=source.read(file['path'])
    assert len(data)==file['bytes'] and hashlib.sha256(data).hexdigest()==file['sha256']
frame_source=[[int(s) for s in line if s.strip()] for line in csv.reader(io.StringIO(source.read(f'content/unit/cgg/unit_cgg_{unit}.csv').decode('utf-8-sig')))]
sheet=Image.open(io.BytesIO(source.read(f'content/unit/img/unit_anime_{unit}.png'))).convert('RGBA')
w,h=480,400
palette=[]
def composite(canvas,part,x,y,blend):
 # PIL alpha_composite clips negative positions safely by pre-cropping.
 x0=max(0,x);y0=max(0,y);x1=min(canvas.width,x+part.width);y1=min(canvas.height,y+part.height)
 if x0>=x1 or y0>=y1:return
 part=part.crop((x0-x,y0-y,x1-x,y1-y));box=(x0,y0,x1,y1)
 if blend==0:
  canvas.alpha_composite(part,(x0,y0))
 else:
  # Additive preview only. BFFrameAnimator's 2016 reference is nonnative.
  dst=canvas.crop(box)
  alpha=part.getchannel('A')
  contribution=ImageChops.multiply(part.convert('RGB'),Image.merge('RGB',(alpha,alpha,alpha)))
  rgb=ImageChops.add(dst.convert('RGB'),contribution,scale=1.0,offset=0)
  out=Image.merge('RGBA',(*rgb.split(),ImageChops.lighter(dst.getchannel('A'),alpha)))
  canvas.paste(out,(x0,y0))

for frame in frame_source:
 assert frame[0]==0 and len(frame)==2+11*frame[1]
 art=Image.new('RGBA',(w,h),(0,0,0,0))
 for j in range(frame[1]):
  dx,dy,flip,blend,opacity,rotate,sx,sy,bw,bh,page=frame[2+j*11:2+(j+1)*11]
  assert page==0 and 0<=sx<sheet.width and 0<=sy<sheet.height and sx+bw<=sheet.width and sy+bh<=sheet.height
  tile=sheet.crop((sx,sy,sx+bw,sy+bh))
  if flip in (1,3):tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  if flip in (2,3):tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  if rotate:tile=tile.rotate(-rotate,expand=True,resample=Image.Resampling.NEAREST)
  if opacity!=100:
   alpha=tile.getchannel('A').point(lambda q:int(q*opacity/100))
   tile.putalpha(alpha)
  composite(art,tile,220+dx,190+dy,blend)
 palette.append(art)
cols=5;rows=(len(palette)+cols-1)//cols
atlas=Image.new('RGBA',(w*cols,h*rows),(0,0,0,0))
for i,fr in enumerate(palette):atlas.alpha_composite(fr,((i%cols)*w,(i//cols)*h))
output=ROOT/'app/src/main/assets/content/seven_star_source_preview';output.mkdir(parents=True,exist_ok=True)
q=output/f'unit_anime_atlas_{unit}.png';atlas.save(q,format='PNG',optimize=True)
thumb=source.read(f'content/unit/img/unit_ills_thum_{unit}.png');(output/f'unit_ills_thum_{unit}.png').write_bytes(thumb)
sha_pixel=hashlib.sha256(atlas.tobytes()).hexdigest()
assert sha_pixel=='2c59d87d592f86a77abbf9330e324603047819d7040cf5c5d7ed0f6be250f322'
assert len(palette)==23 and all(bool(a.getbbox()) for a in palette)
print('Prepared v129 original 7-star Water static source-preview atlas; 23 populated frames; native rendering UNVERIFIED')
meta={'schema':'bf-global-2022-water-7-star-source-visual-preview-v129','sourceUnitId':unit,'sourcePackageSha256':hashlib.sha256(blob).hexdigest(),'sourceFrameCount':len(palette),'frameWidth':w,'frameHeight':h,'columns':cols,'originalArtWidth':sheet.width,'originalArtHeight':sheet.height,'atlasPixelsSha256':sha_pixel,'referenceOnly':True,'nativeBlendProven':False,'nativeTransformProven':False,'nativeFrameClockProven':False,'spritePixelsAreReconstruction':True,'saveFieldsAdded':0,'sourceFileHashes':{n:hashlib.sha256(source.read(n)).hexdigest() for n in names}}
reference=json.loads((ROOT/'source_data/bf_global_7star_water_visual_preview_v129.json').read_text('utf8'))
assert meta==reference, (meta,reference)
