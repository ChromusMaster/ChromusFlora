import collections
import hashlib
import math
import random


LOGS = (1, 2, 4, 5)
NEIGHBORS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def connected_line(cells, start, end, thick=False):
    current = list(start)
    delta = [end[i] - start[i] for i in range(3)]
    length = max(abs(v) for v in delta)
    for step in range(1, length + 1):
        target = [round(start[i] + delta[i] * step / length) for i in range(3)]
        for axis in sorted(range(3), key=lambda i: -abs(delta[i])):
            while current[axis] != target[axis]:
                current[axis] += 1 if target[axis] > current[axis] else -1
                pos = tuple(current)
                if cells.get(pos) != 1:
                    cells[pos] = (4, 2, 5)[axis]
                if thick and step < length // 2:
                    below = (pos[0], pos[1] - 1, pos[2])
                    if below[1] > 0 and cells.get(below) != 1:
                        cells[below] = (4, 2, 5)[axis]
    return tuple(current)


def foliage(cells, point, radii, rng, hanging=False):
    rx, ry, rz = radii
    for dx in range(-math.ceil(rx), math.ceil(rx) + 1):
        for dy in range(-math.ceil(ry), math.ceil(ry) + 1):
            for dz in range(-math.ceil(rz), math.ceil(rz) + 1):
                d = (dx / rx) ** 2 + (dy / ry) ** 2 + (dz / rz) ** 2
                p = (point[0] + dx, point[1] + dy, point[2] + dz)
                if p[1] > 0 and d <= 1 and (d < 0.65 or rng.random() > 0.14):
                    cells.setdefault(p, 3)
                    if hanging and dy == 0 and d > 0.65:
                        for drop in range(1, rng.randint(2, 4)):
                            cells.setdefault((p[0], p[1] - drop, p[2]), 3)


def canopy(tree, variant, tier):
    rng = random.Random(int(hashlib.sha256((variant + tier + 'branches-v10').encode()).hexdigest()[:16], 16))
    giant = tier == 'giant'
    shape = tree['shape']
    crown_height = (22 if giant else 9) + rng.randint(0, 2)
    reach = 8 if giant else 4
    cells = {(x, 0, z): 1 for x in range(-int(giant), int(giant) + 1)
             for z in range(-int(giant), int(giant) + 1)}
    bend_x, bend_z = rng.choice((-1, 1)), rng.choice((-1, 1))
    spine = [(0, 0, 0)]
    for y in range(1, crown_height):
        drift = min(2 if giant else 1, y // (8 if giant else 6))
        point = (bend_x * drift, y, bend_z * (drift if shape != 'conifer' else 0))
        connected_line(cells, spine[-1], point)
        spine.append(point)
        if giant and y < 5:
            for x in (-1, 0, 1):
                for z in (-1, 0, 1):
                    cells[(x, y, z)] = 2
    angle0 = rng.uniform(0, math.tau)
    if shape == 'conifer':
        levels = range(2, crown_height - 1, 3 if giant else 2)
        for level in levels:
            length = max(2, round(reach * (1 - 0.7 * level / crown_height)))
            for i in range(5 if giant else 4):
                angle = angle0 + i * math.tau / (5 if giant else 4) + level * 0.33
                root = spine[level]
                end = (root[0] + round(math.cos(angle) * length), level + 1,
                       root[2] + round(math.sin(angle) * length))
                connected_line(cells, root, end)
                for fraction in (0.45, 0.8, 1.0):
                    p = tuple(round(root[j] + (end[j] - root[j]) * fraction) for j in range(3))
                    foliage(cells, (p[0], p[1] + 1, p[2]), (2.2, 1.7, 2.2), rng)
        foliage(cells, spine[-1], (2, 2, 2), rng)
    elif shape == 'palm':
        for i in range(8):
            angle = angle0 + i * math.tau / 8
            root = spine[-3 - i % 2]
            tip = (root[0] + round(math.cos(angle) * reach), root[1] - rng.randint(1, 3),
                   root[2] + round(math.sin(angle) * reach))
            mid = (round((root[0] + tip[0]) / 2), root[1] + 2, round((root[2] + tip[2]) / 2))
            connected_line(cells, root, mid)
            connected_line(cells, mid, tip)
            for p in (mid, tip):
                foliage(cells, p, (2.4, 1.4, 2.4), rng)
        foliage(cells, spine[-1], (2.7, 2, 2.7), rng)
    elif shape == 'fungus':
        root = spine[-4]
        for i in range(8):
            angle = angle0 + i * math.tau / 8
            tip = (root[0] + round(math.cos(angle) * reach * 0.7), root[1] + rng.randint(0, 2),
                   root[2] + round(math.sin(angle) * reach * 0.7))
            connected_line(cells, root, tip)
            foliage(cells, (tip[0], tip[1] + 1, tip[2]), (3.2, 2.2, 3.2), rng)
        foliage(cells, spine[-1], (4 if giant else 3, 2.5, 4 if giant else 3), rng)
    else:
        count = 8 if giant else 5
        for i in range(count):
            level = 2 + round(i * (crown_height - 7) / max(1, count - 1))
            root = spine[level]
            angle = angle0 + i * 2.39996 + rng.uniform(-0.2, 0.2)
            length = reach - rng.randint(0, 2)
            rise = rng.randint(4, 7) if giant else rng.randint(2, 4)
            if shape == 'candelabra':
                rise += 2
            mid = (root[0] + round(math.cos(angle) * length * 0.55), level + rise // 3,
                   root[2] + round(math.sin(angle) * length * 0.55))
            tip = (root[0] + round(math.cos(angle) * length), min(crown_height, level + rise),
                   root[2] + round(math.sin(angle) * length))
            connected_line(cells, root, mid, giant)
            connected_line(cells, mid, tip)
            radii = (3.3, 2.5, 3.1) if giant else (2.5, 2, 2.4)
            foliage(cells, (tip[0], tip[1] + 1, tip[2]), radii, rng, shape == 'weeping')
            for side in (-1, 1):
                split_angle = angle + side * 0.8
                fork = (mid[0] + round(math.cos(split_angle) * length * 0.6), tip[1] - side,
                        mid[2] + round(math.sin(split_angle) * length * 0.6))
                connected_line(cells, mid, fork)
                foliage(cells, (fork[0], fork[1] + 1, fork[2]), radii, rng, shape == 'weeping')
        foliage(cells, spine[-1], (3.5, 2.8, 3.5) if giant else (2.7, 2, 2.7), rng)
    logs = {p for p, state in cells.items() if state in LOGS}
    distances = {p: 0 for p in logs}
    queue = collections.deque(logs)
    while queue:
        p = queue.popleft()
        if distances[p] >= 6:
            continue
        for d in NEIGHBORS:
            q = tuple(p[i] + d[i] for i in range(3))
            if cells.get(q) == 3 and q not in distances:
                distances[q] = distances[p] + 1
                queue.append(q)
    cells = {p: state for p, state in cells.items() if state != 3 or p in distances}
    low_x = min(p[0] for p in cells) - 1
    low_z = min(p[2] for p in cells) - 1
    cells = {(x - low_x, y, z - low_z): state for (x, y, z), state in cells.items()}
    cells[(-low_x, max(p[1] for p in cells) + 2, -low_z)] = 0
    return cells
