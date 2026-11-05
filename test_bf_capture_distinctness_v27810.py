"""Reconcile tracked v278.1-R2 receipt/visibility defect into existing capture audit."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import struct
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
SCENES={
 'v263_ui_screen_capture':[(s,s,None) for s in ('home','units','quest','summon','menu')],
 'v272_nested_ui_capture':[('squad-editor','units','squad'),('unit-box','units','box'),
  ('evolution','units','evolve'),('training','units','training'),
  ('quest-details','quest',None),('save-controls','menu',None)]}
IDS=['downloadsave','uploadsave','exportsave','importsave','undosave','wipesave']


def require(value, message):
    if not value:raise ValueError(message)


def validate(base):
    hashes=[]
    for folder,scenes in SCENES.items():
        root=base/folder
        manifest=json.loads((root/'capture-manifest.json').read_text())
        require(manifest.get('personalSaveLoaded') is False,'Personal save scope')
        require(manifest.get('missingAssetRequests')==[],'Missing asset requests')
        require(manifest.get('missingAssetCount',0)==0,'Missing asset count')
        require(manifest.get('externalRequestsBlocked')==[],'External requests')
        expected={(f'{w}x{h}-{name}.png',name,route,tab,w,h)
                  for w,h in ((320,740),(393,852)) for name,route,tab in scenes}
        rows=manifest['screenshots']
        require(len(rows)==len(expected),'Receipt count')
        seen=set()
        for row in rows:
            w,h=row['viewport']; name=row['screen']; filename=row['file']
            route=row.get('route',row.get('navigatorCurrent'))
            identity=(filename,name,route,row.get('unitTab'),w,h)
            require(identity in expected and identity not in seen,'Scene/route/viewport/filename')
            seen.add(identity)
            require(row.get('saveUnchanged') is True,'Save flag')
            require(row.get('entirePlayerUnchanged') is True and row.get('allStorageUnchanged') is True,'Full progress audit')
            require(type(row.get('storageWriteCalls')) is int and row['storageWriteCalls']==0,'Storage writes')
            data=(root/filename).read_bytes()
            require(data[:8]==b'\x89PNG\r\n\x1a\n' and data[12:16]==b'IHDR','PNG header')
            require(struct.unpack('>II',data[16:24])==(w*2,h*2),'PNG dimensions')
            digest=hashlib.sha256(data).hexdigest()
            require(digest==row['sha256'] and len(data)==row['bytes'],'PNG hash/length')
            hashes.append(digest)
            if name=='save-controls':
                vis=row.get('saveControlsVisibility',[])
                require([v['id'] for v in vis]==IDS,'Six save controls required')
                require(all(v.get('visible') is True and v.get('unobscured') is True and v.get('sampleCount')==5 for v in vis),'Save controls obscured')
        require(seen==expected,'Missing scene')
        require({p.name for p in root.glob('*.png')}=={x[0] for x in expected},'Stray/missing PNG')
    require(len(hashes)==22 and len(set(hashes))==22,'Duplicate screenshot evidence')
    return 22


def main():
    nav=(ROOT/'test_bf_nested_ui_capture_v27200.py').read_text()
    pre=(ROOT/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
    wf=(ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    require('saveControlsVisibility=save_visibility' in nav and 'elementFromPoint' in nav,'Visibility capture source')
    require('test_bf_capture_distinctness_v27810.py --source-only' in pre,'Source registration')
    require('python3 test_bf_capture_distinctness_v27810.py --validate' in wf,'Build registration')
    require(wf.index('python3 test_bf_nested_ui_capture_v27200.py --capture') < wf.index('python3 test_bf_capture_distinctness_v27810.py --validate'),'Gate order')
    if '--source-only' in sys.argv:
        print('PASS v278.1 source: capture visibility and distinctness gate registered');return
    require('--validate' in sys.argv,'Explicit --source-only or --validate required')
    base=ROOT/'source_audit_reports'
    require(validate(base)==22,'Capture count')
    # Adversarial checks operate exclusively on disposable copies of capture evidence.
    if '--adversarial' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='bf-capture-negative-') as temp:
            target=Path(temp)
            for folder in SCENES:shutil.copytree(base/folder,target/folder)
            path=target/'v272_nested_ui_capture/capture-manifest.json'
            original=json.loads(path.read_text())
            for field,bad in [('personalSaveLoaded',True),('missingAssetRequests',['fake']),('externalRequestsBlocked',['fake'])]:
                changed=copy.deepcopy(original);changed[field]=bad;path.write_text(json.dumps(changed))
                try:validate(target)
                except ValueError:pass
                else:raise ValueError('Missed negative '+field)
            changed=copy.deepcopy(original)
            row=next(r for r in changed['screenshots'] if r['file']=='320x740-save-controls.png')
            shot=target/'v272_nested_ui_capture'/row['file']
            data=(target/'v263_ui_screen_capture/320x740-menu.png').read_bytes()
            shot.write_bytes(data);row['sha256']=hashlib.sha256(data).hexdigest();row['bytes']=len(data)
            path.write_text(json.dumps(changed))
            try:validate(target)
            except ValueError as error:require('Duplicate' in str(error),'Wrong duplicate rejection')
            else:raise ValueError('Rehashed duplicate accepted')
        print('PASS four adversarial mutations rejected, originals untouched')
    print('PASS 22 distinct screenshots, exact scenes/dimensions/hashes, visible save controls, unchanged progress')

if __name__=='__main__':main()
