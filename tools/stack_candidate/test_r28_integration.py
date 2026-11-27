#!/usr/bin/env python3
import pathlib,sys,subprocess
from verify_progression_r28 import directory
root=pathlib.Path(sys.argv[1]).resolve();here=pathlib.Path(__file__).resolve().parent
directory(root,'prepared')
for test in ['test_r28_home.py','test_r28_combat.py']:
 subprocess.run([sys.executable,str(here/test),str(root),str(root),str(here/'native-order.txt')],check=True)
print('PASS integration preview: 20 Home/progression and 28 combat checks')
