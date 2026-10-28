"""v146: signed Android APK contains source-correct five-star Death Magress atlas."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parent
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 png=z.read('assets/content/five_star_evolution/unit_anime_atlas_60014.png')
 assert list(png[:8])==[137,80,78,71,13,10,26,10]
 assert hashlib.sha256(png).hexdigest()=='e8582ed0a8a1eba005b208def14d97ba8f2892d38c83629941b536c2ac7b2b46'
 for id,sha in {
   10014:'5bb571fb4e5dedd8f73571cd66722320f14d220acbd64c66a383cb645914c6be',
   20014:'b9760f2c651ae4690d0cb4ae88e80f3271d6239fd1f2aeb9bf906e3a645f7f3d',
   30014:'0d358473737b353d5b99719457fe94a1776f17caaf87841f274de272c324feea',
   40014:'8eff7c31a1ebd67da807d3fc6004fdf594b0e8b02d404f1e6e03184fca3d5d08',
   50014:'b498a6f2b48f5e02ed90fe3e53801835b417b9463bcaa4bd787497383614d068'
 }.items():
  assert hashlib.sha256(z.read(f'assets/content/five_star_evolution/unit_anime_atlas_{id}.png')).hexdigest()==sha,id
 html=z.read('assets/index.html').decode('utf8')
 assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
 assert 'bf_global_offline_demo_v7' in html
print('PASS v146 packaged five-star Death Magress original art, all other five-star art and v7 save schema unchanged')
