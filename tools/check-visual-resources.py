import collections
import hashlib
import json
from pathlib import Path
from PIL import Image
from scan import nbt


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
NEIGHBORS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def verify():
    errors = []
    textures = sorted((RES / 'assets/chromusflora/textures/block/wood').rglob('*.png'))
    for path in textures:
        image = Image.open(path).convert('RGBA')
        if image.size != (64, 64) or image.getextrema()[3] != (255, 255):
            errors.append('Invalid wood tile: ' + str(path))
        if any(image.getpixel((0, i)) != image.getpixel((63, i)) or
               image.getpixel((i, 0)) != image.getpixel((i, 63)) for i in range(64)):
            errors.append('Non-periodic edge: ' + str(path))
    if len(textures) != 332 or len({hashlib.sha256(p.read_bytes()).hexdigest() for p in textures}) != 332:
        errors.append('Expected 332 distinct wood textures')
    catalog = json.loads((RES / 'chromusflora/catalog.json').read_text())
    species = [tree['id'] for tree in catalog['trees']]
    door_textures = sorted((RES / 'assets/chromusflora/textures/block/door').rglob('*.png'))
    trapdoor_textures = sorted((RES / 'assets/chromusflora/textures/block/trapdoor').rglob('*.png'))
    if len(door_textures) != len(species) * 2:
        errors.append('Expected two dedicated door textures per tree family')
    if len(trapdoor_textures) != len(species):
        errors.append('Expected one dedicated trapdoor texture per tree family')
    for name in species:
        for path in [RES / f'assets/chromusflora/textures/block/door/{name}/bottom.png',
                     RES / f'assets/chromusflora/textures/block/door/{name}/top.png',
                     RES / f'assets/chromusflora/textures/block/trapdoor/{name}/main.png']:
            if not path.exists():
                errors.append('Missing dedicated wood detail texture: ' + str(path))
                continue
            image = Image.open(path).convert('RGBA')
            if image.size != (64, 64) or image.getextrema()[3] != (255, 255):
                errors.append('Invalid door/trapdoor texture: ' + str(path))
        door_model = json.loads((RES / f'assets/chromusflora/models/block/{name}_door_bottom_left.json').read_text())
        trap_model = json.loads((RES / f'assets/chromusflora/models/block/{name}_trapdoor_bottom.json').read_text())
        if door_model['textures'] != {'bottom': f'chromusflora:block/door/{name}/bottom', 'top': f'chromusflora:block/door/{name}/top'}:
            errors.append('Door model still uses raw plank UVs: ' + name)
        if trap_model['textures'] != {'texture': f'chromusflora:block/trapdoor/{name}/main'}:
            errors.append('Trapdoor model still uses raw plank UVs: ' + name)
        item_def_path = RES / f'assets/chromusflora/items/{name}_door.json'
        item_model_path = RES / f'assets/chromusflora/models/item/{name}_door.json'
        item_texture_path = RES / f'assets/chromusflora/textures/item/door/{name}.png'
        if not item_def_path.exists() or not item_model_path.exists() or not item_texture_path.exists():
            errors.append('Missing dedicated door inventory asset: ' + name)
        else:
            item_def = json.loads(item_def_path.read_text())
            item_model = json.loads(item_model_path.read_text())
            if item_def != {'model': {'type': 'minecraft:model', 'model': f'chromusflora:item/{name}_door'}}:
                errors.append('Door item does not use dedicated 2D item model: ' + name)
            if item_model != {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'chromusflora:item/door/{name}'}}:
                errors.append('Door item model is not generated sprite model: ' + name)
            ii = Image.open(item_texture_path).convert('RGBA')
            if ii.size != (64, 128):
                errors.append('Door inventory texture must be 64x128: ' + name)
    style_catalog = json.loads((ROOT / 'atelier/wood/door-style-map.json').read_text())
    assignments = style_catalog.get('assignments', {})
    families = style_catalog.get('families', {})
    if set(assignments) != set(species):
        errors.append('Door style map does not cover exactly the catalog species')
    if len(families) != 14:
        errors.append('Expected 14 reviewed door/trapdoor visual families')
    if any(entry.get('family') not in families for entry in assignments.values()):
        errors.append('Unknown door/trapdoor family in style map')
    door_hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in door_textures}
    trapdoor_hashes = {hashlib.sha256(p.read_bytes()).hexdigest() for p in trapdoor_textures}
    if len(door_hashes) != len(door_textures):
        errors.append('Door textures are not all distinct')
    if len(trapdoor_hashes) != len(trapdoor_textures):
        errors.append('Trapdoor textures are not all distinct')
    for name in species:
        planks = RES / f'assets/chromusflora/textures/block/wood/{name}/planks.png'
        ph = hashlib.sha256(planks.read_bytes()).hexdigest()
        for path in [RES / f'assets/chromusflora/textures/block/door/{name}/bottom.png',
                     RES / f'assets/chromusflora/textures/block/door/{name}/top.png',
                     RES / f'assets/chromusflora/textures/block/trapdoor/{name}/main.png']:
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == ph:
                errors.append('Door/trapdoor texture is still a raw plank copy: ' + str(path))
    rows = []
    for path in sorted((RES / 'data/chromusflora/worldgen/configured_feature/forms').rglob('*.json')):
        config = json.loads(path.read_text())['config']
        template = RES / ('data/chromusflora/structure/' + config['canopy_location'].split(':')[1] + '.nbt')
        obj = nbt(template)
        cells = {tuple(b['pos']): obj['palette'][b['state']] for b in obj['blocks']}
        logs = {p for p, s in cells.items() if s['Name'] in ('minecraft:oak_log', 'minecraft:red_wool')}
        roots = {p for p, s in cells.items() if s['Name'] == 'minecraft:red_wool'}
        leaves = {p for p, s in cells.items() if s['Name'] == 'minecraft:oak_leaves'}
        reached = set(roots)
        queue = collections.deque(roots)
        while queue:
            p = queue.popleft()
            for d in NEIGHBORS:
                q = tuple(p[i] + d[i] for i in range(3))
                if q in logs and q not in reached:
                    reached.add(q)
                    queue.append(q)
        if reached != logs:
            errors.append('Disconnected branch: ' + str(path))
        distance = {p: 0 for p in logs}
        queue = collections.deque(logs)
        while queue:
            p = queue.popleft()
            if distance[p] >= 6:
                continue
            for d in NEIGHBORS:
                q = tuple(p[i] + d[i] for i in range(3))
                if q in leaves and q not in distance:
                    distance[q] = distance[p] + 1
                    queue.append(q)
        if not leaves or not leaves <= distance.keys():
            errors.append('Unsupported foliage: ' + str(path))
        marker = next(p for p, s in cells.items() if s['Name'] == 'minecraft:white_wool')
        horizontal = [p for p in logs if cells[p].get('Properties', {}).get('axis') in ('x', 'z')]
        extent = max(max(abs(p[0] - marker[0]), abs(p[2] - marker[2])) for p in logs | leaves)
        if extent > 15:
            errors.append('Crown exceeds the 15-block horizontal budget: ' + str(path))
        small = path.name == 'small.json'
        if not small and not horizontal:
            errors.append('Missing oriented branches: ' + str(path))
        if small and (len(logs) != 1 or config['height'] != 2):
            errors.append('Small tree changed: ' + str(path))
        rows.append({'form': path.relative_to(RES).as_posix(), 'logs': len(logs),
                     'leaves': len(leaves), 'horizontal_logs': len(horizontal),
                     'horizontal_radius': extent, 'connected': reached == logs})
    return {'status': 'PASS' if not errors else 'FAIL', 'wood_tiles': len(textures),
            'door_textures': len(door_textures), 'trapdoor_textures': len(trapdoor_textures),
            'tree_forms': len(rows), 'branched_forms': sum(r['horizontal_logs'] > 0 for r in rows),
            'max_horizontal_radius': max(r['horizontal_radius'] for r in rows),
            'errors': errors, 'forms': rows,
            'limitations': ['Static pixel and voxel checks; no game render, chunk generation or build execution.',
                            'Exact edge colors do not guarantee absence of perceptible repetition or shader artifacts.']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'verification/visual-resources.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'forms'}, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
