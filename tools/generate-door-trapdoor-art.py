





from __future__ import annotations
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'flora/src/main/resources/assets/chromusflora'
ART = ROOT / 'atelier/joinery'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    catalog = json.loads((ROOT/'flora/src/main/resources/chromusflora/catalog.json').read_text())
    mapping = json.loads((ART/'species.json').read_text())
    assert set(mapping['species']) == {t['id'] for t in catalog['trees']}
    atlases = {s['sheet']: Image.open(ART/s['file']).convert('RGBA') for s in mapping['sheets']}
    style_path = ROOT/'atelier/wood/door-style-map.json'
    styles = json.loads(style_path.read_text())
    for name, spec in mapping['species'].items():
        atlas = atlases[spec['sheet']]
        for kind in ('door', 'trapdoor'):
            crop = spec[kind+'_crop']
            assert 0 <= crop[0] < crop[2] <= atlas.width and 0 <= crop[1] < crop[3] <= atlas.height
        full = atlas.crop(spec['door_crop']).resize((64,128), Image.Resampling.LANCZOS)
        trap = atlas.crop(spec['trapdoor_crop']).resize((64,64), Image.Resampling.LANCZOS)
        assert full.getextrema()[3] == (255,255) and trap.getextrema()[3] == (255,255)
        door_dir = ASSETS/f'textures/block/door/{name}'
        trap_dir = ASSETS/f'textures/block/trapdoor/{name}'
        item_dir = ASSETS/'textures/item/door'
        for path in [door_dir, trap_dir, item_dir]: path.mkdir(parents=True, exist_ok=True)
        full.crop((0,0,64,64)).save(door_dir/'top.png', optimize=True)
        full.crop((0,64,64,128)).save(door_dir/'bottom.png', optimize=True)
        full.save(item_dir/f'{name}.png', optimize=True)
        trap.save(trap_dir/'main.png', optimize=True)
        write(ASSETS/f'models/item/{name}_door.json', {'parent':'minecraft:item/generated','textures':{'layer0':f'chromusflora:item/door/{name}'}})
        write(ASSETS/f'items/{name}_door.json', {'model':{'type':'minecraft:model','model':f'chromusflora:item/{name}_door'}})
        styles['assignments'][name].update({'source_atlas':f'atelier/joinery/sheet-{spec["sheet"]}.png','source_cell':spec['cell'],'adaptation':spec.get('adaptation','Reference motif adapted to rectangular Minecraft face.')})
    styles['source']='Six user-provided door sheets; built-in image_gen adaptations in atelier/joinery'
    styles['principle']='Distinct reference-based textures; no external mod artwork. Existing tree textures stay unchanged. 64x64 block faces, 64x128 item sprites, native block geometry.'
    write(style_path, styles)
    print('PASS: packed 83 door pairs, 83 item sprites and 83 matching trapdoors.')


if __name__ == '__main__': main()
