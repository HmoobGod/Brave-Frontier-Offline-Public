"""v119: 2022 Global unit EXP patterns vs external candidate, strictly read-only.
This is a research gate, not a replacement for demoLevel or a v7 migration.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
CORE=R/'app/src/main/assets/index.html'
SOURCE=R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json'
RAW=('JYFGe9y6','5UvTp7q1','D9wXQI2V','grKTq15A')
# Pinned external DecompFrontier/server 7cc0ebd3, file blob c109ff50.
# These are accumulated need_exp candidate samples, not verified 2022 save semantics.
SAMPLES={
 10:{1:0,2:10,3:58,4:160,10:2492,12:4115,30:46442,40:97403,60:274185,80:568826,100:1000000},
 15:{1:0,2:15,3:87,4:240,10:3738,12:6173,30:69664,40:146108,60:411280,80:853241,100:1500000},
 20:{1:0,2:21,3:117,4:321,10:4985,12:8232,30:92883,40:194806,60:548366,80:1137652,100:1999997}}

def parse_mst(obj,check_samples=True):
    """Read all 804 original-shaped entries. Never silently accept missing levels."""
    root,pi,lv,need=RAW
    if not isinstance(obj,dict) or not isinstance(obj.get(root),list):raise ValueError('MST root missing')
    src={}
    for row in obj[root]:
        try:p,l,n=(int(row[k]) for k in (pi,lv,need))
        except (KeyError,TypeError,ValueError) as e:raise ValueError('Bad EXP row') from e
        if p not in (10,15,20,25) or l not in range(1,202) or n<0:raise ValueError('Bad EXP range')
        data=src.setdefault(p,{})
        if l in data:raise ValueError('Duplicate EXP level')
        data[l]=n
    if len(obj[root])!=804 or set(src)!={10,15,20,25}:raise ValueError('Incomplete source')
    curves={}
    for p,rows in src.items():
        if set(rows)!=set(range(1,202)):raise ValueError('Missing level')
        total=0;curve={}
        for l in range(1,202):
            n=rows[l]
            if (p==25 and n!=0) or (p!=25 and (n!=0 if l==1 else n<=0)):
                raise ValueError('Unexpected requirement')
            total+=n;curve[l]=(n,total)
        curves[p]=curve
        if check_samples and p in SAMPLES:
            for l,x in SAMPLES[p].items():
                if curve[l][1]!=x:raise ValueError('External sample drift')
    return curves

def fail_closed_test():
    entries=[{RAW[1]:str(p),RAW[2]:str(l),RAW[3]:str(0 if p==25 or l==1 else p)}
             for p in (10,15,20,25) for l in range(1,202)]
    fixture={RAW[0]:entries}
    assert len(parse_mst(fixture,False)[10])==201
    invalid={RAW[0]:[dict(x) for x in entries]}
    invalid[RAW[0]][0][RAW[2]]='2'
    try:parse_mst(invalid,False)
    except ValueError:pass
    else:raise AssertionError('Duplicate accepted')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',type=Path,help='Separate local DecompFrontier EXP-pattern JSON')
    ap.add_argument('--original-2022',type=Path,help='Independent 2022 EXP table, same raw structure')
    ap.add_argument('--report',type=Path,help='Create new report; never overwrite')
    args=ap.parse_args()
    if args.original_2022 and not args.candidate:ap.error('Original comparison requires candidate')
    fail_closed_test()
    manifest=json.loads(SOURCE.read_text('utf8'))
    rows=manifest['rows'];counts=Counter(r['expPatternId'] for r in rows)
    assert len(rows)==len({r['unitId'] for r in rows})==manifest['unitCount']==72
    assert counts=={10:42,15:24,20:6}
    assert manifest['source']['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
    report={'source':'2022 Global 72 original playable unit IDs',
            'pattern_counts':dict(counts),'saved_xp_changed':False,
            'original_2022_numeric_table_match':'not established',
            'external_table_activated_in_game':False}
    if args.candidate:
        cand=parse_mst(json.loads(args.candidate.read_text('utf8')))
        report['external_rows_checked']=sum(len(x) for x in cand.values())
        if args.original_2022:
            original=parse_mst(json.loads(args.original_2022.read_text('utf8')),False)
            for pid in (10,15,20):
                if any(cand[pid][lv]!=original[pid][lv] for lv in range(1,101)):
                    raise ValueError('2022 original EXP differs; do not activate')
            report['original_2022_numeric_table_match']='300/300 level requirements, pending version/application review'
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,
            executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
            args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':390,'height':844})
        errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.set_content(CORE.read_text('utf8'),wait_until='load',timeout=90000)
        assert page.evaluate('P.version')==7
        assert page.evaluate('typeof demoLevel')=='function'
        before=page.evaluate('JSON.stringify(P)')
        old_local=page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
        report['demo_vs_external_candidate_samples']={
          str(pid):[{'source_level':lv,'source_cumulative':exp,
                     'unchanged_demo_level':page.evaluate('(xp)=>demoLevel(xp)',exp)}
                    for lv,exp in samples.items()]
          for pid,samples in SAMPLES.items()}
        assert page.evaluate('JSON.stringify(P)')==before
        new_local=page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
        assert old_local==new_local
        assert not errors,errors
        browser.close()
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        with args.report.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print('PASS v119 read-only external EXP comparisons, 72 original IDs, unchanged P v7/local save; no activation')

if __name__=='__main__':
    main()
