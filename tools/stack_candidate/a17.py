#!/usr/bin/env python3
"""B7: restore ordinary evolution import recipe, keep copy resolution separate."""
import hashlib,pathlib,sys
from a13 import readmanifest,one
HERE=pathlib.Path(__file__).resolve().parent
NAME='index.html'
OLD="const recipe=EVO_RECIPES.find(r=>r.baseId===ownedCopyBase(Number(bid),copies) && r.evolvedId===value);if(copies&&String(Number(bid))!==bid)throw new Error('Invalid evolution identity');\n   if(!recipe || !out.roster.includes(Number(bid)))throw new Error('Unknown evolution');"
NEW="""let resolvedRecipe;
   if(Number(bid)>=OWNED_COPY_FIRST){
    resolvedRecipe=EVO_RECIPES.find(r=>r.baseId===ownedCopyBase(Number(bid),copies) && r.evolvedId===value);
   }else{
    const recipe=EVO_RECIPES.find(r=>r.baseId===Number(bid) && r.evolvedId===value);
    resolvedRecipe=recipe;
   }
   if(copies&&String(Number(bid))!==bid)throw new Error('Invalid evolution identity');
   if(!resolvedRecipe || !out.roster.includes(Number(bid)))throw new Error('Unknown evolution');"""
def transform(root):
 for n,h in readmanifest(HERE/'a16-hashes.txt').items():
  if hashlib.sha256((root/n).read_bytes()).hexdigest()!=h:raise ValueError('A16 input mismatch '+n)
 p=root/NAME;s=p.read_text('utf8');p.write_text(one(s,OLD,NEW),encoding='utf8')
 print('A17 live legacy evolution recipe; canonical copy branch preserved')
if __name__=='__main__':transform(pathlib.Path(sys.argv[1]))
