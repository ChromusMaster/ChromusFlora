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
