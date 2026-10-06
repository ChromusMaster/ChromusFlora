from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'flora/src/main/resources'
CAT=json.loads((RES/'chromusflora/catalog.json').read_text())
SPECIES=[t['id'] for t in CAT['trees']]
STYLE=json.loads((ROOT/'atelier/wood/door-style-map.json').read_text())
FUNC=RES/'data/chromusflora/function/test/doors_trapdoors.mcfunction'
CLEAR=RES/'data/chromusflora/function/test/clear_doors_trapdoors.mcfunction'
INDEX=ROOT/'docs/DOOR_TRAPDOOR_TEST_INDEX.md'

def main():
    errors=[]; checks=0
    def check(ok,msg):
        nonlocal checks; checks+=1
        if not ok: errors.append(msg)
    check(len(SPECIES)==83,'catalog must contain 83 species')
    check(set(STYLE['assignments'])==set(SPECIES),'style map species mismatch')
    check(len(STYLE['families'])==14,'style map family count')
    text=FUNC.read_text(encoding='utf-8')
    for name in SPECIES:
        check(f'chromusflora:{name}_door[' in text, 'gallery missing door '+name)
        check(f'chromusflora:{name}_trapdoor[' in text, 'gallery missing trapdoor '+name)
        check(f'chromusflora:{name}_planks' in text, 'gallery missing pedestal '+name)
        check((RES/f'assets/chromusflora/models/item/{name}_door.json').exists(), 'missing 2D door item model '+name)
        check((RES/f'assets/chromusflora/textures/item/door/{name}.png').exists(), 'missing door item sprite '+name)
    check(CLEAR.exists(),'missing gallery cleanup function')
    report={'status':'PASS' if not errors else 'FAIL','assertions':checks,'species':len(SPECIES),'families':len(STYLE['families']),'errors':errors}
    out=ROOT/'verification/release-0.1.4'
    out.mkdir(parents=True,exist_ok=True)
    (out/'door-gallery-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if not errors else 1)
if __name__=='__main__': main()
