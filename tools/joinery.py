import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'flora/src/main/resources/assets/chromusflora'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def box(a, b, texture='wood'):
    x, y, z = a
    X, Y, Z = b
    uv = {'west': [z, 16-Y, Z, 16-y], 'east': [16-Z, 16-Y, 16-z, 16-y],
          'north': [16-X, 16-Y, 16-x, 16-y], 'south': [x, 16-Y, X, 16-y],
          'up': [x, z, X, Z], 'down': [x, 16-Z, X, 16-z]}
    return {'from': list(a), 'to': list(b), 'faces': {side: {'uv': coords, 'texture': '#' + texture} for side, coords in uv.items()}}


def textures(species):
    prefix='chromusflora:block/wood/'+species+'/'
    return {'wood':prefix+'planks','trim':prefix+'bark','light':prefix+'stripped',
            'hardware':'minecraft:block/iron_block','particle':prefix+'planks'}


def furniture_models(species):
    tex=textures(species)
    table=[box((1,0,1),(15,15,15))]
    for x in [0,14]:
        for z in [0,14]:table.append(box((x,0,z),(x+2,15,z+2),'trim'))
    table.append(box((0,15,0),(16,16,16),'trim'))
    for x in range(3):
        for z in range(3):table.append(box((2+x*4,16,2+z*4),(5.5+x*4,16.1,5.5+z*4),'light'))
    for x in [0,15.85]:
        table.append(box((x,8,5),(x+.15,12,6),'hardware'))
        table.append(box((x,11,3.5),(x+.15,12,7.5),'hardware'))
    write(ASSETS/f'models/block/{species}_crafting_table.json',{'parent':'minecraft:block/block','textures':tex,'elements':table})
    write(ASSETS/f'blockstates/{species}_crafting_table.json',{'variants':{'':{'model':'chromusflora:block/'+species+'_crafting_table'}}})
    states={}
    for kind in ['single','left','right']:
        left,right=(1,15) if kind=='single' else ((1,16) if kind=='left' else (0,15))
        elements=[box((left+.125,0,1.125),(right-.125,9.25,14.875)),box((left+.125,10.25,1.125),(right-.125,14,14.875),'light'),
                  box((left,9.25,1),(right,10.25,15),'trim')]
        for x in [left,right-1]:elements.append(box((x,0,1),(x+1,14,15),'trim'))
        latch=(7,9) if kind=='single' else ((14,16) if kind=='left' else (0,2))
        elements.append(box((latch[0],8,.5),(latch[1],12,1.15),'hardware'))
        model=f'{species}_chest_{kind}'
        write(ASSETS/f'models/block/{model}.json',{'parent':'minecraft:block/block','textures':tex,'elements':elements})
        for facing,angle in [('north',0),('east',90),('south',180),('west',270)]:
            states[f'facing={facing},type={kind}']={'model':'chromusflora:block/'+model,'y':angle}
    write(ASSETS/f'blockstates/{species}_chest.json',{'variants':states})
    write(ASSETS/f'items/{species}_crafting_table.json',{'model':{'type':'minecraft:model','model':'chromusflora:block/'+species+'_crafting_table'}})
    write(ASSETS/f'items/{species}_chest.json',{'model':{'type':'minecraft:model','model':'chromusflora:block/'+species+'_chest_single'}})


def generate():
    trees = json.loads((ROOT/'flora/src/main/resources/chromusflora/catalog.json').read_text())['trees']
    for tree in trees:
        furniture_models(tree['id'])
    return len(trees)


if __name__ == '__main__':
    print('Furniture families:', generate())
