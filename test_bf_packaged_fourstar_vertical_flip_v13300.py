"""v133 signed APK sprite fidelity for three existing 4-star playable units."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parent
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
expected={
 20023:'5982e1ed6d9011fbdb79f0882a6385b29b61a24a605ec1442f14ed564f07b07e',
 30023:'fe75fceff32d3357c9aecf078248ce78033c60de72ba853419c00b08f0fc0c46',
 50023:'daf0a9eff2edc1d44602f041d7ae4f0ae4ca7db940d362dcb382155c61e97a46'
}
with zipfile.ZipFile(APK) as z:
 for uid,digest in expected.items():
  png=z.read(f'assets/content/more_second_evolution/unit_anime_atlas_{uid}.png')
  assert list(png[:8])==[137,80,78,71,13,10,26,10]
  assert hashlib.sha256(png).hexdigest()==digest,uid
 html=z.read('assets/index.html').decode('utf8')
 assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
 assert 'bf_global_offline_demo_v7' in html
print('PASS v133 packaged source-flipped three 4-star originals, v7 save unchanged')
