
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'flora/src/main/resources'
A=RES/'assets/chromusflora'

def read(p):return json.loads(p.read_text())

def verify():
    errors=[];checks=0
    def check(ok,label):
        nonlocal checks
        checks+=1
        if not ok:errors.append(label)
    species=[t['id'] for t in read(RES/'chromusflora/catalog.json')['trees']]
    art=read(ROOT/'atelier/joinery/species.json')
    check(set(art['species'])==set(species),'Art assignment coverage')
    unique=set()
    for name in species:
        top=Image.open(A/f'textures/block/door/{name}/top.png').convert('RGBA')
        bottom=Image.open(A/f'textures/block/door/{name}/bottom.png').convert('RGBA')
        sprite=Image.open(A/f'textures/item/door/{name}.png').convert('RGBA')
        check(top.tobytes()==sprite.crop((0,0,64,64)).tobytes(),'Upper half differs from full door: '+name)
        check(bottom.tobytes()==sprite.crop((0,64,64,128)).tobytes(),'Lower half differs from full door: '+name)
        unique.add(hashlib.sha256(sprite.tobytes()).hexdigest())
        for half in ['bottom','top']:
            for hinge in ['left','right']:
                for opened in ['', '_open']:
                    suffix=half+'_'+hinge+opened
                    model=read(A/f'models/block/{name}_door_{suffix}.json')
                    check(model.get('parent')=='minecraft:block/door_'+suffix and 'elements' not in model,'Non-native door geometry: '+name+suffix)
        for pose in ['bottom','top','open']:
            model=read(A/f'models/block/{name}_trapdoor_{pose}.json')
            check(model.get('parent')=='minecraft:block/template_orientable_trapdoor_'+pose,'Non-native hatch geometry: '+name+pose)
        table=read(A/f'models/block/{name}_crafting_table.json')
        check(len(table['elements'])<=21,'Furniture mesh budget: '+name)
        states=read(A/f'blockstates/{name}_chest.json')['variants']
        check(set(states)=={f'facing={face},type={kind}' for face in ['north','east','south','west'] for kind in ['single','left','right']},'Chest states incomplete: '+name)
        for kind in ['single','left','right']:
            model=read(A/f'models/block/{name}_chest_{kind}.json')
            check(model['elements']==[],'Static chest would overlap animated renderer: '+name)
        item=read(A/f'models/item/{name}_chest.json')
        check(len(item['elements'])==3,'Closed chest item geometry: '+name)
    check(len(unique)==83,'All full door artworks must be distinct')
    shared={p.relative_to(RES).as_posix():p for p in RES.rglob('*') if p.is_file()}
    modern=ROOT/'versions/26.3/src/main/resources'
    targets={'26.2':shared,'26.3':shared|{p.relative_to(modern).as_posix():p for p in modern.rglob('*') if p.is_file()}}
    for version,files in targets.items():
        for kind,pattern in [('chest',['###','# #','###']),('crafting_table',['##','##'])]:
            vanilla=read(files[f'data/minecraft/recipe/{kind}.json'])
            check(vanilla['group']==kind and vanilla['category']=='misc',version+' vanilla grouping '+kind)
            check(vanilla['key']['#']=={'fabric:type':'fabric:difference','base':'#minecraft:planks','subtracted':'#chromusflora:planks'},version+' overlapping vanilla ingredient '+kind)
            check(f'data/chromusflora/recipe/{kind}.json' not in files,version+' duplicate old fallback '+kind)
            check(f'data/chromusflora/advancement/recipes/{kind}.json' not in files,version+' stale fallback advancement '+kind)
            for name in species:
                recipe=read(files[f'data/chromusflora/recipe/{name}_{kind}.json'])
                check(recipe['group']==kind and recipe['category']=='misc',version+' grouping '+name+'_'+kind)
                check(recipe['key']=={'#':'chromusflora:'+name+'_planks'} and recipe['pattern']==pattern,version+' material '+name+'_'+kind)
                check(recipe['result']=={'id':'chromusflora:'+name+'_'+kind,'count':1},version+' output '+name+'_'+kind)
            fallback=read(files[f'data/chromusflora/recipe/vanilla_{kind}.json'])
            check(fallback['ingredients']==['#chromusflora:'+kind+'s'] and fallback['result']['id']=='minecraft:'+kind,version+' vanilla conversion '+kind)
    return {'status':'PASS' if not errors else 'FAIL','assertions':checks,'errors':errors,'wood_families':len(species),'unique_door_faces':len(unique),'scope':'Pixel identity, resource contracts and recipe partition; no recipe manager or Minecraft execution.'}

if __name__=='__main__':
    report=verify();out=ROOT/'verification/release-0.1.4/joinery-checks.json'
    out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
