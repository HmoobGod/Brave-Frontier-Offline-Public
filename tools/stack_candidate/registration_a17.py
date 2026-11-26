#!/usr/bin/env python3
"""Review-only A17 contextual registration diff for exact clean main. Use normal Python, not -I."""
import argparse,difflib,pathlib
import registration_a11 as prior
MAIN=prior.MAIN
JAVA='app/src/main/java/org/bravefrontier/offline/MainActivity.java'
SOURCES={**prior.SOURCES,JAVA:'17c4b1c491c891f1e2cb5648bd7653687d1ecfbe'}
EXTRA_BLOBS={'app/src/main/assets/'+n:h for h,n in (l.split() for l in pathlib.Path(__file__).with_name('a13-extra-main-blobs.txt').read_text().splitlines())}
JAVA_OLD='                    view.evaluateJavascript(js, null);'
JAVA_NEW='''                    // STACK Unit Box helper is optional on legacy assets and uses the ordinary 64 KiB budget.
                    try {
                        String stackCopies = readPackagedText("bf_stack_copies.js");
                        view.evaluateJavascript(stackCopies, null);
                    } catch (IOException stackError) {
                        android.util.Log.w("BraveFrontier", "Optional STACK UI unavailable", stackError);
                    }
                    view.evaluateJavascript(js, null);'''
def changes(path,old):
 if path==JAVA:return prior.one(old,JAVA_OLD,JAVA_NEW)
 if path.endswith('build.gradle'):return old+prior.GRADLE.replace('verify_stack_a11.py','verify_stack_a17.py')
 new=prior.change_workflow(old)
 new=prior.one(new,'          python3 tools/stack_candidate/verify_stack_a10.py --assets-dir app/src/main/assets --expect baseline --require-main-repeat\n          python3 tools/stack_candidate/prepare_stack_a8.py --assets-dir app/src/main/assets --apply\n          python3 tools/stack_candidate/verify_stack_a11.py --assets-dir app/src/main/assets --mode prepared','''          python3 tools/stack_candidate/verify_stack_a17.py --assets-dir app/src/main/assets --mode baseline
          python3 tools/stack_candidate/prepare_stack_a17.py --assets-dir app/src/main/assets --apply
          python3 tools/stack_candidate/verify_stack_a17.py --assets-dir app/src/main/assets --mode prepared
          node --check app/src/main/assets/bf_stack_copies.js
          # This job checkout is ephemeral; source-only re-preparation is intentional.
          python3 tools/stack_candidate/reprepare_stack_a17.py --checkout . --execute-disposable''')
 new=prior.one(new,'          python3 tools/stack_candidate/a11_repeat_browser.py app/src/main/assets', '''          python3 tools/stack_candidate/a11_repeat_browser.py app/src/main/assets
          node tools/stack_candidate/a13_lookup_test.cjs app/src/main/assets''')
 for v in ['debug','diagnostic']:
  new=prior.one(new,'python3 tools/stack_candidate/verify_stack_a10.py --apk app/build/outputs/apk/'+v+'/app-'+v+'.apk --require-main-repeat','python3 tools/stack_candidate/verify_stack_a17.py --apk app/build/outputs/apk/'+v+'/app-'+v+'.apk --mode prepared')
 return new

def main():
 p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();root=a.checkout.resolve();out=a.output.resolve()
 if out==root or root in out.parents or out.exists():raise SystemExit('Need new output outside checkout')
 if prior.git(root,'rev-parse','HEAD')!=MAIN or prior.git(root,'status','--porcelain'):raise SystemExit('Need exact clean main checkout')
 for path,sha in {**SOURCES,**prior.BASE_BLOBS,**EXTRA_BLOBS}.items():
  if prior.git(root,'rev-parse','HEAD:'+path)!=sha:raise SystemExit('Unexpected blob '+path)
 diff=[]
 for path,sha in SOURCES.items():
  data=(root/path).read_bytes()
  if prior.blob(data)!=sha:raise SystemExit('Working bytes mismatch '+path)
  old=data.decode('utf8');new=changes(path,old);diff.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path))
 out.write_text(''.join(diff),encoding='utf8');print('Review-only diff written; no build or staging')
if __name__=='__main__':main()
