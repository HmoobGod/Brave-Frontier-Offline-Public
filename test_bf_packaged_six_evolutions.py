"""Verify compiled Android package stages all six source-authentic Global evolutions."""
from pathlib import Path
import base64,hashlib,json,struct,zipfile,io,re
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
assert A.is_file(),A
M=json.loads((ROOT/'source_data/bf_global_six_evolutions_v032.json').read_text('utf-8'))
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Extra_Evolutions.zip.b64').read_text('ascii'))
assert hashlib.sha256(pack).hexdigest()==M['sourcePackSha256']
with zipfile.ZipFile(A) as apk,zipfile.ZipFile(io.BytesIO(pack)) as raw:
    files=set(apk.namelist());src=apk.read('assets/index.html').decode('utf-8')
    assert src.count('/* BF_GLOBAL_SIX_EVOLUTIONS_V032 */')==1
    assert 'bf_global_offline_demo_v7' in src
    assert 'const BF_VERIFIED_BB_V032=Object.freeze(' in src
    assert 'const BF_VERIFIED_SUPPORT_V032=Object.freeze(' in src
    assert 'const BF_VERIFIED_POWER_V032=Object.freeze(' in src
    assert src.count('if(unit.originalMaxLevel&&unit.originalUnitCost&&unit.originalLordStats)continue')==1
    dec=json.JSONDecoder()
    def embedded(mark):
        at=src.index(mark)+len(mark)
        return dec.raw_decode(src[at:])[0]
    evolved=embedded('window.BF_EVOLVED_UNITS=');recipes=embedded('const EVO_RECIPES=')
    bb=embedded('window.BF_ARCHIVE_BB_HITS=')
    assert len(evolved)==54 and len(recipes)==54 and len(bb)==72
    for key,unit in M['records'].items():
        uid=int(key)
        row=next(u for u in evolved if u['id']==uid)
        rec=next(u for u in recipes if u['evolvedId']==uid)
        assert row['name']==unit['name'] and row['stats']==unit['stats']
        assert rec['baseId']==unit['baseId'] and rec['archivedZel']==unit['sourceRecipe']['zel']
        assert rec['materials']==unit['sourceRecipe']['materials']
        assert bb[key]['offensiveCandidate']==(unit['bb']['target']!='support')
        for prefix in ('unit_anime_atlas_','unit_ills_thum_'):
            path=f'assets/content/extra_evolution/{prefix}{uid}.png'
            assert path in files,path
            data=apk.read(path)
            assert data[:8]==b'\x89PNG\r\n\x1a\n'
            width,height=struct.unpack('>II',data[16:24])
            if prefix.startswith('unit_anime'):
                assert (width,height)==(2400,((unit['frameCount']+4)//5)*400)
            else:
                original=raw.read(f'content/unit/img/unit_ills_thum_{uid}.png')
                assert data==original
    assert 'assets/bf_home_nav.js' in files
    assert len(apk.read('assets/bf_home_nav.js'))<=65536
print('PASS v0.32 APK: 6 authentic playable Global evolutions, CGG atlases, original portraits, scoped BBs, unchanged save v7')
