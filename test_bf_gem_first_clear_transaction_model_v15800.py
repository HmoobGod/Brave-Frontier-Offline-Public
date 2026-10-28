"""v158: research-only deterministic Gem first-clear transaction model.

No production logic or player save is mutated by this file.
The model deliberately chooses a conservative LEGACY policy (previously
cleared quests not paid retroactively); this is a candidate, not an endorsed
migration policy or proof of native 2022 payout behavior.
"""
from pathlib import Path
import hashlib,json,random
from copy import deepcopy

R=Path(__file__).resolve().parent
gates=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
gem=json.loads((R/'source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json').read_text('utf8'))
assert gates['originalRewardFinales']==29 and gates['currentPlayableFinales']==22
assert gates['amdahlUnplayableFinales']==7
allowed=frozenset(row[0] for row in gates['rows'] if row[4]==1)
unavailable=frozenset(row[0] for row in gates['rows'] if row[4]==0)
assert len(allowed)==22 and len(unavailable)==7 and not allowed&unavailable
assert gates['canonicalRowsSha256']=='0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8'
assert gem['corroboratedMissionCount']==29 and gem['currentlyPlayable']==22
assert gem['liveGemGrantsEnabled'] is False and gem['saveSchemaChanged'] is False

MAX_GEMS=999999 # model-only upper bound; not a proven native 2022 account cap
def new_snapshot(old):
    """Pure proposed *future* migration. Never rewrite v7 save here."""
    assert old.get('version')==7
    clears=old.get('questClears',{})
    assert isinstance(clears,dict)
    c={}
    for k,v in clears.items():
        mid=int(k)
        assert str(mid)==str(k) and mid>0 and isinstance(v,int) and not isinstance(v,bool) and v>=0
        c[str(mid)]=v
    # Legacy IDs are claimed to avoid ambiguous double credits, not rewarded.
    return {'modelVersion':1,'gems':0,'clears':c,
            'legacyFinales':sorted(i for i in allowed if c.get(str(i),0)>0),
            'paidFinales':[]}

def transaction(snapshot,mission,amount=1):
    """Pure clone-on-write; commit MUST atomically persist returned object."""
    old=deepcopy(snapshot)
    assert isinstance(mission,int) and not isinstance(mission,bool) and mission>0
    assert amount==1
    assert old['modelVersion']==1
    assert isinstance(old['gems'],int) and 0<=old['gems']<=MAX_GEMS
    assert all(isinstance(x,int) for x in old['paidFinales']+old['legacyFinales'])
    assert not set(old['paidFinales'])&set(old['legacyFinales'])
    assert set(old['paidFinales']+old['legacyFinales'])<=allowed
    before=old['clears'].get(str(mission),0)
    assert isinstance(before,int) and before>=0
    assert before<2**53-1
    old['clears'][str(mission)]=before+1
    paid=False
    if (mission in allowed and before==0 and
        mission not in old['paidFinales'] and
        mission not in old['legacyFinales'] and
        old['gems']<MAX_GEMS):
        old['gems']+=1
        old['paidFinales'].append(mission)
        old['paidFinales'].sort()
        paid=True
    return old,paid

old={'version':7,'questClears':{'12':1,'23':4,'1':11,'365':0}}
preserved=deepcopy(old)
init=new_snapshot(old)
assert old==preserved
assert init['gems']==0 and init['legacyFinales']==[12,23]
next_state,awarded=transaction(init,12)
assert not awarded and next_state['gems']==0 and next_state['clears']['12']==2
state,award=transaction(init,365)
assert award and state['gems']==1
twice,paid=transaction(state,365)
assert not paid and twice['gems']==1 and twice['clears']['365']==2
assert init['gems']==0 and init['clears']=={'12':1,'23':4,'1':11,'365':0}
same,paid=transaction(init,404)
assert not paid and same['gems']==0 and same['clears']['404']==1
notfinal,paid=transaction(init,1)
assert not paid and notfinal['gems']==0
# Crash before commit: local original persists, rerun a single award;
# crash after commit: duplicate event cannot pay again.
fresh=new_snapshot({'version':7,'questClears':{}})
staged,first=transaction(fresh,12)
assert first and staged['gems']==1 and fresh['gems']==0
stagedAgain,repeat=transaction(fresh,12)
assert repeat and stagedAgain==staged
committed=deepcopy(staged)
after,repaid=transaction(committed,12)
assert not repaid and after['gems']==1
# Fuzz 10,000 deterministic source-only practice transactions.
rng=random.Random(15800)
eligible=list(sorted(allowed));bonus=list(sorted(unavailable))
for _ in range(50):
    s=new_snapshot({'version':7,'questClears':{}})
    visits=set()
    for __ in range(200):
        mission=rng.choice(eligible+bonus+[1,10,90,20000])
        prev=deepcopy(s)
        s,paid=transaction(s,mission)
        assert s['clears'][str(mission)]==prev['clears'].get(str(mission),0)+1
        assert s['gems']-prev['gems']==int(paid)
        assert paid==(mission in allowed and mission not in visits)
        visits.add(mission)
        assert s['gems']==len(s['paidFinales'])
        assert len(s['paidFinales'])==len(set(s['paidFinales']))
# Reject unsafe save inputs (negative, bool and schema mismatch).
for bad in ({'version':7,'questClears':{'12':-1}},
            {'version':7,'questClears':{'12':True}},
            {'version':8,'questClears':{}},
            {'version':7,'questClears':{'x':1}}):
    try: new_snapshot(bad)
    except (AssertionError,ValueError): pass
    else: raise AssertionError(('accepted invalid progress',bad))
# Preserve no runtime Gem wallet or new app save fields in v158.
html=(R/'app/src/main/assets/index.html').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert 'bf15800' not in html and 'bf15800' not in java
assert not (R/'app/src/main/assets/bf15800_gem_transaction.js').exists()
print('PASS v158: read-only one-time Gem transaction candidate, 10k randomized quests, legacy quarantine, replay, crash, v7 unchanged')
