"""v131 original source opacity frame is shipped, existing v7 APK unchanged."""
from pathlib import Path
import hashlib,zipfile
R=Path(__file__).resolve().parent
APK=R/'app/build/outputs/apk/debug/app-debug.apk'
with zipfile.ZipFile(APK) as z:
 png=z.read('assets/content/other_six_star/unit_anime_atlas_30025.png')
 assert hashlib.sha256(png).hexdigest()=='53295c806e6390e05a74e7ed124e709e9c677753070fc44eb1e3c262131623b5'
 assert png[:8]==b'\x89PNG\r\n\x1a\n'
 html=z.read('assets/index.html').decode('utf8')
 assert 'bf_global_offline_demo_v7' in html
 assert html.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
 assert all(f'assets/content/other_six_star/unit_anime_atlas_{uid}.png' in z.namelist() for uid in (10025,20025,30025,40025,50025,60025))
print('PASS v131 packaged source-correct 6-star Earth alternate atlas; existing original recipe / signed APK retained')
