"""v134: verify real Android APK contains restored original Dark 4-star sprite."""
from pathlib import Path
import zipfile,hashlib
A=Path(__file__).resolve().parent/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(A) as z:
 p=z.read('assets/content/more_second_evolution/unit_anime_atlas_60013.png')
 assert list(p[:8])==[137,80,78,71,13,10,26,10]
 assert hashlib.sha256(p).hexdigest()=='b12bdb2eea55eec3ec6ffe734923ad07ebccda10aca0e8ab5235c6a0d0c0cd40'
 for uid,expected in {
  20023:'5982e1ed6d9011fbdb79f0882a6385b29b61a24a605ec1442f14ed564f07b07e',
  30023:'fe75fceff32d3357c9aecf078248ce78033c60de72ba853419c00b08f0fc0c46',
  50023:'daf0a9eff2edc1d44602f041d7ae4f0ae4ca7db940d362dcb382155c61e97a46'
 }.items():
  assert hashlib.sha256(z.read(f'assets/content/more_second_evolution/unit_anime_atlas_{uid}.png')).hexdigest()==expected,uid
 html=z.read('assets/index.html').decode('utf8')
 assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
 assert 'bf_global_offline_demo_v7' in html
print('PASS v134 packaged original 4-star Black Magress source layer corrections, current v7 save preserved')
