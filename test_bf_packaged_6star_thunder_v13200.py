"""v132: signed APK contains source-correct original 6★ Thunder art; save format intact."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parent
apk=R/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(apk) as z:
 png=z.read('assets/content/other_six_star/unit_anime_atlas_40025.png')
 assert list(png[:8])==[137,80,78,71,13,10,26,10]
 assert hashlib.sha256(png).hexdigest()=='7273c43cead5d10c1ba47b59888379a808411c3ed7a3fa1894a277e970ccc90b'
 assert hashlib.sha256(z.read('assets/content/other_six_star/unit_anime_atlas_30025.png')).hexdigest()== '53295c806e6390e05a74e7ed124e709e9c677753070fc44eb1e3c262131623b5'
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert html.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
print('PASS v132 packaged source-correct Thunder six-star original art in signed APK; v7 save unchanged')
