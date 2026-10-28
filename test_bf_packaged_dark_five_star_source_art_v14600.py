"""v146: Android APK must contain original-source-corrected Death Magress art."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parent
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
expected='e8582ed0a8a1eba005b208def14d97ba8f2892d38c83629941b536c2ac7b2b46'
with zipfile.ZipFile(APK) as z:
 data=z.read('assets/content/five_star_evolution/unit_anime_atlas_60014.png')
 assert list(data[:8])==[137,80,78,71,13,10,26,10]
 assert hashlib.sha256(data).hexdigest()==expected
 for uid,digest in {
   10014:'5bb571fb4e5dedd8f73571cd66722320f14d220acbd64c66a383cb645914c6be',
   20014:'b9760f2c651ae4690d0cb4ae88e80f3271d6239fd1f2aeb9bf906e3a645f7f3d',
   30014:'0d358473737b353d5b99719457fe94a1776f17caaf87841f274de272c324feea',
   40014:'8eff7c31a1ebd67da807d3fc6004fdf594b0e8b02d404f1e6e03184fca3d5d08',
   50014:'b498a6f2b48f5e02ed90fe3e53801835b417b9463bcaa4bd787497383614d068'
 }.items():
  png=z.read(f'assets/content/five_star_evolution/unit_anime_atlas_{uid}.png')
  assert hashlib.sha256(png).hexdigest()==digest,uid
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
print('PASS v146 APK: original 5-star Death Magress flips and opacity correctly packaged, v7 saves untouched')
