#!/usr/bin/env python3
"""Produce REVIEW-ONLY diff against exact pinned main; never edits the checkout.
No git writes, workflows, builds, deployment, or installation. The output is
not approved for activation; only apply after explicit authorization/review.
"""
import argparse, difflib, hashlib, pathlib, subprocess
MAIN='676133c46bbdeee5ea259757acf0b036f5fbcaa5'
SOURCES={'.github/workflows/build-debug-apk.yml':'e1e4d43e38995dc20b17b1f1e511f4fdaa9dfee0','app/build.gradle':'69db756d20a771824377bd10a09595969ebbe80f'}
BASE_BLOBS={'app/src/main/assets/index.html':'4ef5f1a1a4c3c0817828f29c0646a51a98843c77','app/src/main/assets/bf_home_nav.js':'f4938e429ccac82904ff1d95c15a798cf9be9a5e','app/src/main/assets/bf10200_qol_unit_flags.js':'5a03ea249342c35d65a9c6e3f3d6ea7072885d7f','app/src/main/assets/bf10000_qol_squad_presets.js':'6ff5641b203a6f8e48073a18013d1d262bf6d116','app/src/main/assets/bf9800_qol_cleared_quest_repeat.js':'8b4aa3a67a171aab18dba9a5f3a31cc850fce7cd'}
TOOL='tools/stack_candidate/'
ANCHOR='          python3 prepare_original_amdahl_art_v149.py\n      - name: Test save recovery and offline combat'
INSERT='''          python3 prepare_original_amdahl_art_v149.py
      - name: Prepare exact STACK source candidate (no owner data)
        run: |
          python3 tools/stack_candidate/verify_stack_a10.py --assets-dir app/src/main/assets --expect baseline --require-main-repeat
          python3 tools/stack_candidate/prepare_stack_a8.py --assets-dir app/src/main/assets --apply
          python3 tools/stack_candidate/verify_stack_a11.py --assets-dir app/src/main/assets --mode prepared
      - name: Test save recovery and offline combat'''
PIP='          python -m pip install playwright\n          node research/test_bf_capture_import_v366.js'
TESTS='''          python -m pip install playwright
          python3 tools/stack_candidate/a8_browser.py app/src/main/assets
          python3 tools/stack_candidate/a9_browser.py app/src/main/assets
          python3 tools/stack_candidate/a11_repeat_browser.py app/src/main/assets
          node research/test_bf_capture_import_v366.js'''
GRADLE='''
// STACK admission: preserve every existing preparation dependency; do not
// attempt partial generation here. Verify before variant asset merging.
// Explicit true requires the full exact prepared candidate. Without it,
// reject any STACK residue and keep ordinary legacy generation permitted.
afterEvaluate {
    def stackPrepared = project.findProperty('bfStackPrepared')?.toString() == 'true'
    def verifyStackGeneratedAssets = tasks.register('verifyStackGeneratedAssets', Exec) {
        dependsOn tasks.named('preBuild')
        workingDir rootProject.projectDir
        commandLine System.getProperty('os.name').toLowerCase().contains('windows') ? 'py' : 'python3',
            'tools/stack_candidate/verify_stack_a11.py', '--assets-dir', 'app/src/main/assets',
            '--mode', stackPrepared ? 'prepared' : 'legacy'
    }
    tasks.matching { it.name.startsWith('merge') && it.name.endsWith('Assets') }.configureEach {
        dependsOn verifyStackGeneratedAssets
    }
}
'''
def one(s,a,b):
    if s.count(a)!=1:raise ValueError('Anchor changed: '+a[:100])
    return s.replace(a,b,1)
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def change_workflow(s):
    s=one(s,ANCHOR,INSERT);s=one(s,PIP,TESTS)
    for variant,task in [('debug','assembleDebug'),('diagnostic','assembleDiagnostic')]:
        old='        run: gradle --no-daemon '+task+' -PciVersionCode=$((100000 + ${{ github.run_number }}))'
        new="        env:\n          ORG_GRADLE_PROJECT_bfStackPrepared: 'true'\n"+old+"\n      - name: Verify STACK "+variant+" packaged asset identity\n        run: python3 tools/stack_candidate/verify_stack_a10.py --apk app/build/outputs/apk/"+variant+"/app-"+variant+".apk --require-main-repeat"
        s=one(s,old,new)
    return s

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();root=a.checkout.resolve();out=a.output.resolve()
    if out==root or root in out.parents:raise SystemExit('Output must be outside checkout')
    if git(root,'rev-parse','HEAD')!=MAIN or git(root,'status','--porcelain'):raise SystemExit('Need exact clean main checkout; no edits made')
    for path,sha in {**SOURCES,**BASE_BLOBS}.items():
        if git(root,'rev-parse','HEAD:'+path)!=sha:raise SystemExit('Unexpected Git blob '+path)
    changes=[]
    for path,sha in SOURCES.items():
        data=(root/path).read_bytes()
        if blob(data)!=sha:raise SystemExit('Working source bytes mismatch '+path)
        old=data.decode('utf8');new=change_workflow(old) if path.endswith('.yml') else old+GRADLE
        changes.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path))
    if a.output.exists():raise SystemExit('Refusing to overwrite existing review diff')
    a.output.write_text(''.join(changes),encoding='utf8');print('Review diff written outside checkout; no Git or build actions')
if __name__=='__main__':main()
