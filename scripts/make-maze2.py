# Builds src/lib/maze2.json from maze.json: Spectrum on top, Prisma (flipped) at the bottom,
# loopbrug docked on the south bump of Spectrum (column 28). Run: python scripts/make-maze2.py
import json
m = json.load(open('src/lib/maze.json'))
C, R = 50, 53          # new size
DX = 0                 # Spectrum column shift
PX = 6                 # Prisma+bridge column shift: bridge centre 22 lines up with Spectrum column 28
PR = 2                 # Prisma+bridge row shift: bridge starts below the bump (orig Spectrum row 52)
cells = [['.'] * C for _ in range(R)]
h = [[0] * C for _ in range(R + 1)]
v = [[0] * (C + 1) for _ in range(R)]

def put(g, r, c, val):
    g[r][c] = max(g[r][c], val)

# Spectrum (orig rows 26..52): shift up 26, right DX
for r in range(26, 53):
    for c in range(44):
        if m['cells'][r][c] != '.': cells[r - 26][c + DX] = m['cells'][r][c]
for e in range(26, 54):
    for c in range(44): put(h, e - 26, c + DX, int(m['h'][e][c]))
for r in range(26, 53):
    for c in range(45): put(v, r - 26, c + DX, int(m['v'][r][c]))
h[0][22 + DX] = 2  # old bridge doorway in Spectrum's top wall: close it

# Prisma + bridge (orig rows 0..25): flip vertically, row r -> 50 - r
for r in range(26):
    for c in range(44):
        if m['cells'][r][c] != '.': cells[50 + PR - r][c + PX] = m['cells'][r][c]
    for c in range(45): put(v, 50 + PR - r, c + PX, int(m['v'][r][c]))
for e in range(26):
    for c in range(44): put(h, 51 + PR - e, c + PX, int(m['h'][e][c]))
for c in (21, 22, 23):  # bridge end, now docking on Spectrum's south wall
    h[27][c + PX] = int(m['h'][26][c])


# Lengthen the route through Spectrum: the bridge now docks right next to the exit, so the
# original maze lets you skip most of it. Hill-climb (doors and walls may move):
# close a wall on the solution path, reopen the wall across the cut that makes the route longest.
import random
random.seed(1)
ENTRY, EXIT = (26, 28), (19, 7)
sp = {(r, c) for r in range(27) for c in range(C) if cells[r][c] != '.'}
def edge(a, b):  # (grid, r, c) holding the wall between adjacent cells a, b
    (r1, c1), (r2, c2) = sorted((a, b))
    return (h, r2, c2) if c1 == c2 else (v, r2, c2)
def wall_val(a, b):  # what a closed wall here looks like: as the original, or thick if flanked by thick wall
    g, r, c = edge(a, b)
    if orig[id(g), r, c]: return orig[id(g), r, c]
    nb = [(r, c - 1), (r, c + 1)] if g is h else [(r - 1, c), (r + 1, c)]
    return 2 if any(0 <= y < len(g) and 0 <= x < len(g[0]) and g[y][x] == 2 for y, x in nb) else 1
def nbrs(p):
    for d in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        q = (p[0] + d[0], p[1] + d[1])
        if q in sp: yield q
def is_open(a, b):
    g, r, c = edge(a, b); return g[r][c] == 0
def bfs(src, skip=None):
    dist, par, todo = {src: 0}, {src: None}, [src]
    for p in todo:
        for q in nbrs(p):
            if q not in dist and is_open(p, q) and {p, q} != skip:
                dist[q], par[q] = dist[p] + 1, p; todo.append(q)
    return dist, par
def route_len(): return bfs(ENTRY)[0][EXIT]
orig = {(id(g), r, c): g[r][c] for g in (h, v) for r in range(len(g)) for c in range(len(g[0]))}
before = route_len()
for _ in range(50000):
    dist, par = bfs(ENTRY)
    path, p = [], EXIT
    while par[p]: path.append((p, par[p])); p = par[p]
    a, b = random.choice(path)           # b is nearer the entry
    dA, _ = bfs(ENTRY, {a, b})
    dB, _ = bfs(EXIT, {a, b})
    best, opts = -1, []
    for x in dA:
        for y in nbrs(x):
            if y in dB and not is_open(x, y):
                n = dA[x] + 1 + dB[y]
                if n > best: best, opts = n, []
                if n == best: opts.append((x, y))
    if not opts: continue
    x, y = random.choice(opts)
    g, r, c = edge(a, b); g[r][c] = wall_val(a, b)
    g, r, c = edge(x, y); g[r][c] = 0
print('route through Spectrum: %d -> %d steps of %d cells' % (before, route_len(), len(sp)))
cells = [''.join(r) for r in cells]
labels = []
for x, y, s, t, g in m['labels']:
    if t == 'PRISMA': x, y = PX, 54.36
    elif t == 'SPECTRUM': x, y = DX, -0.3
    elif y < 26: x, y = x + PX, round(51 + PR - y + 0.72 * s, 2)
    else: x, y = round(x + DX, 2), round(y - 26, 2)
    labels.append([x, y, s, t, g])
out = {'cols': C, 'rows': R, 'fills': m['fills'], 'cells': cells,
       'h': [''.join(map(str, r)) for r in h], 'v': [''.join(map(str, r)) for r in v], 'labels': labels}
json.dump(out, open('src/lib/maze2.json', 'w'))

# self-check: from the start, the exit (only opening to outside) is reachable
D = {(-1, 0): lambda r, c: h[r][c], (1, 0): lambda r, c: h[r + 1][c],
     (0, -1): lambda r, c: v[r][c], (0, 1): lambda r, c: v[r][c + 1]}
is_cell = lambda r, c: 0 <= r < R and 0 <= c < C and cells[r][c] != '.'
seen, stack, outs, edges = set(), [(49, 25)], [], 0
while stack:
    p = stack.pop()
    if p in seen: continue
    seen.add(p)
    for (dr, dc), w in D.items():
        if w(*p) == 0:
            q = (p[0] + dr, p[1] + dc)
            if is_cell(*q): stack.append(q)
            else: outs.append(p)
total = sum(is_cell(r, c) for r in range(R) for c in range(C))
print('reached', len(seen), 'of', total, 'cells; openings to outside from', outs)
assert len(seen) == total and len(outs) == 1
