"""v137: authenticated original 2022 Global Legend Stone (110100) acquisition references.

No retroactive exchange grants or historical date cutoffs on an offline game.
"""
from pathlib import Path
import json,hashlib,collections,base64,gzip
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_2022_legend_stone_exchange_v137.json').read_text('utf8'))
assert m['schema']=='bf-global-2022-legend-stone-source-acquisition-v137'
assert m['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert m['sourceFileSha256']=={
 'exchangeHall':'00fc854cdcf3f507ac0544a6e6774af5afad22cf89e0c1b535d11258ab3b54e9',
 'catalystComment':'662441185b6d03d9c55b8cd46c60156c6523e5b9df214cfdc1b63e27e325331e',
 'itemMaster':'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
 'evolutions':'fbaae982125b78e5a203095d0bb6d8892d210c4a632aa9e2e24f70ba0e480deb'}
assert m['sourceItem']=={
 'itemId':'110100','itemName':'神越の魂石','itemType':'4',
 'itemThumbnail':'item_thum_111000.png','itemMaxStack':'999'}
assert 'Farmable Locations' in m['farmableLocationsText']
assert 'Mission Exchange Hall' in m['farmableLocationsText']
assert m['sourceTypes']=={'evolutionMaterialType':2,'exchangeItemType':4}
e=m['exchangeHall']; ex=e['historicalNamedRows']; recent=e['last2022Rows']
assert e['allItemId110100Rows']==66 and e['namedLegendStoneRows']==len(ex)==59
assert e['otherNameRows']==7
assert len(recent)==4
assert [r[0] for r in recent]==[80000056,80000057,80000058,80000059]
assert [r[4][:7] for r in recent]==['2022-01','2022-02','2022-03','2022-04']
assert all(row[1:4]==[4000,99,'4:110100:1:0'] for row in recent)
assert recent[-1][5]=='2022-05-01 07:59:59'
assert all(row in ex for row in recent)
assert not e['sourceCostCurrencyVerified'] and e['archiveScheduleOnly']
refs=m['originalTypedEvolutionReferences']; starters=m['sixStarter7And8Evolutions']
assert len(refs)==279 and len({r[0] for r in refs})==279
assert len(starters)==12 and all(r in refs for r in starters)
assert {r[0] for r in starters}=={el*10000+rarity for el in range(1,7) for rarity in (15,16)}
assert all(r[1]==r[0]+1 and r[4]>0 for r in starters)
# Original 2022 packaged unit-evolution typed records provide an independent join.
v130=json.loads((R/'source_data/bf_global_2022_starter_typed_evolution_v130.json').read_text('utf8'))
assert len(v130['rows'])==12
for row in v130['rows']:
 target,previous,rarity,_,_,zel,karma,mats=row
 assert [previous,target,zel,karma,next(pos for pos,typ,uid in mats if typ==2 and uid==110100)] in starters,row
assert hashlib.sha256(json.dumps([ex,refs,starters],separators=(',',':')).encode()).hexdigest()==m['canonicalTuplesSha256']=='1eb4ede7ead65cb2e8816cf6ef8578c0b68d186aa43b65a89b97f20cccd9215a'
# No economic/inventory save or gameplay mutations.
assert not m['liveAcquisitionEnabled'] and not m['playerInventoryMigrated'] and m['historicalAvailabilityNotAnOfflineGate']
html=(R/'app/src/main/assets/index.html').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html and 'bf13700_legend_stone_exchange.js' not in java
assert not (R/'app/src/main/assets/bf13700_legend_stone_exchange.js').exists()
print('PASS v137: 2022 Legend Stone 4 monthly exchanges, 59 named offers, 279 source evo uses, 12 starter joins, v7 unchanged')
