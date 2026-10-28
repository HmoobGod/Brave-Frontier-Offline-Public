"""v142: signed Android APK retains all 106 source-exact live 2022 quest scalar values."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parent
S=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
with zipfile.ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 html=z.read('assets/index.html').decode('utf8')
 d=json.JSONDecoder();key='window.BF_QUEST_CATALOG=';index=html.index(key)+len(key)
 quests,_=d.raw_decode(html[index:])
 for m in re.finditer(r'window\.BF_QUEST_CATALOG\.push\(',html):
  i=m.end();j=html.index(');',i)
  rows,_=d.raw_decode('['+html[i:j]+']')
  quests.extend(rows)
 byId={q['missionId']:q for q in quests}
 assert len(quests)==len(byId)==106
 for row in S['records']:
  q=byId[row[0]]
  assert [q['missionId'],q['dungeonId'],q['requires'],q['battles'],q['energy'],q['exp'],q['zel'],q['karma']]==row,row[0]
 assert 'P.exp+=QUEST.exp;P.zel+=QUEST.zel;P.karma+=QUEST.karma;' in html
 assert 'bf_global_offline_demo_v7' in html
print('PASS v142 signed APK: original 2022 106-quest reward/prerequisite parity, unchanged v7 saves')
