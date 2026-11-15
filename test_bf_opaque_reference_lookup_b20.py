"""Exact opaque-token reverse lookup; never infers enemy identities."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
source=json.loads((R/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text())
script=(R/'app/src/main/assets/bf057_mission_evidence.js').read_text().replace('__BF_MISSION_EVIDENCE_ROWS__',json.dumps(source))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
 p=b.new_page();p.add_script_tag(content=script)
 for row in source['rows']:
  for pair in row['rawEncounterRef'].split(','):
   label,ref=pair.split(':')
   expected=[r['missionId'] for r in source['rows'] if pair in r['rawEncounterRef'].split(',')]
   assert p.evaluate('([a,b])=>BFOriginalMissionEvidence.findOpaqueReference(a,b)',[label,ref])==expected
 assert p.evaluate("BFOriginalMissionEvidence.findOpaqueReference('0','999999999')")==[]
 assert p.evaluate("BFOriginalMissionEvidence.findOpaqueReference(0,'1')") is None
 assert p.evaluate("BFOriginalMissionEvidence.findOpaqueReference('enemy','1')") is None
 assert p.evaluate("Object.isFrozen(BFOriginalMissionEvidence.findOpaqueReference('0','10102'))")
 assert p.evaluate('BFOriginalMissionEvidence.count')==34
 b.close()
print('PASS exact source opaque-token lookup, all rows, strict inputs, immutable results; no decoded identities')
