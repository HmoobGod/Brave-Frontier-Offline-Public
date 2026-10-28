"""v165 signed APK invariants for real v124 synthetic save migration."""
from pathlib import Path
import hashlib, json, zipfile
R=Path(__file__).resolve().parent
raw=(R/'source_data/bf165_real_signed_v124_first_clear_save.json').read_text('utf8').rstrip('\n')
assert hashlib.sha256(raw.encode()).hexdigest()=='503165ae5b5f476a92f8a0e9f4d2197b8e2aa41a3a3462d23e1e202bec953170'
assert '_bfGemV160' not in json.loads(raw)
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 html=z.read('assets/index.html').decode('utf8')
 backup=z.read('assets/bf9700_qol_rotating_backups.js').decode('utf8')
 assert 'BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER' in html
 assert 'BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING' in html
 assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
 assert 'bf9700-export-current' in backup
 assert 'BraveFrontier-v7-current-' in backup
 assert 'BFAndroid?.exportSaveFile' in backup
 assert 'localStorage.setItem(SAVE_KEY,JSON.stringify(P))' in html
print('PASS v165 signed APK: canonical v7 save parser, conservative legacy Gem ledger, current-save external export')
