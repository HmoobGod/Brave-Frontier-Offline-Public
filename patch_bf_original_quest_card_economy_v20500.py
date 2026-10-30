"""v205: source-backed quest-card details; no change to save, rewards, or combat."""
from pathlib import Path
import argparse

APP = Path(__file__).resolve().parent / 'app/src/main/assets/index.html'
BEFORE_CARD = "const info=document.createElement('small');info.textContent=unlocked?`${q.battles} battles · ${q.exp} EXP · ${q.zel} Zel`:`Clear Mission ${q.requires} to unlock`;"
AFTER_CARD = "const info=document.createElement('small');info.textContent=`${q.battles} battles · ${q.exp} EXP · ${q.zel} Zel · ${q.karma} Karma · ${q.energy} source Energy${unlocked?'':` · Clear Mission ${q.requires} to unlock`}`;"
BEFORE_INFO = "${QUEST.battles} battles · ${QUEST.exp} EXP / ${QUEST.zel} Zel / ${QUEST.karma} Karma · ${QUEST.background}"
AFTER_INFO = "${QUEST.battles} battles · ${QUEST.energy} source Energy (not charged in demo) · ${QUEST.exp} EXP / ${QUEST.zel} Zel / ${QUEST.karma} Karma · ${QUEST.background}"

def patch(text):
    if AFTER_CARD in text and AFTER_INFO in text and BEFORE_CARD not in text and BEFORE_INFO not in text:
        return text
    if text.count(BEFORE_CARD) != 1 or text.count(BEFORE_INFO) != 1:
        raise ValueError('v205 original quest-card source anchors missing or changed')
    return text.replace(BEFORE_CARD, AFTER_CARD, 1).replace(BEFORE_INFO, AFTER_INFO, 1)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--html', type=Path, default=APP)
    args = p.parse_args()
    current = args.html.read_text('utf8')
    updated = patch(current)
    if current != updated:
        args.html.write_text(updated, encoding='utf8')
    print('PASS v205: shows original Energy and Karma; save/rewards unchanged')

if __name__ == '__main__':
    main()
