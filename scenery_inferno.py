"""Cenário do Inferno (fases 20-24): chão de basalto rachado com lava, obstáculos e decoração.

Mesmo formato dos outros biomas (scenery_biomes.py): paleta por fase, ladrilho do chão em pixel art (repete sem
emenda), obstáculos [(sprite 120x120, raio de colisão)] e decoração do chão (não bloqueia).
Variações: I = portões cobertos de cinza; II = planície rachada com ossos; III = rios de magma;
IV = fortaleza de obsidiana (piso de tijolos); V = trono do Rei Demônio (runas roxas).
"""
import math
import random

import pygame

TILE = 512

INFERNO = [
    dict(theme="inferno", ground=(74, 52, 48), rock=(96, 74, 68), lava=(255, 110, 40), accent=(255, 170, 60),
         obstacles=(2, 4), ash=True),
    dict(theme="inferno", ground=(68, 44, 40), rock=(92, 66, 60), lava=(255, 100, 35), accent=(230, 210, 180),
         obstacles=(2, 4), bones=True),
    dict(theme="inferno", ground=(58, 36, 34), rock=(84, 58, 52), lava=(255, 120, 40), accent=(255, 200, 90),
         obstacles=(3, 5), magma=True),
    dict(theme="inferno", ground=(46, 38, 46), rock=(70, 60, 74), lava=(255, 90, 40), accent=(255, 140, 50),
         obstacles=(3, 5), fortress=True),
    dict(theme="inferno", ground=(44, 28, 42), rock=(70, 48, 70), lava=(240, 70, 60), accent=(200, 90, 255),
         obstacles=(3, 5), throne=True),
]


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _px():
    import pixel
    return pixel


def _put(low, x, y, col):
    w, h = low.get_size()
    low.set_at((x % w, y % h), col)


def _noise01(px, lw, rnd, cells):
    n = px.tile_noise(lw, lw, rnd, cells)
    lo = min(min(r) for r in n)
    hi = max(max(r) for r in n)
    span = (hi - lo) or 1
    return [[(v - lo) / span for v in row] for row in n]


def _walk(low, rnd, x, y, steps, col, glow=None):
    for _ in range(steps):
        _put(low, x, y, col)
        if glow and rnd.random() < 0.5:
            _put(low, x + 1, y, glow)
        x += rnd.choice((-1, 0, 1, 1))
        y += rnd.choice((-1, 0, 1))


# ------------------------------------------------------------------ chão
def ground(pal, rnd):
    """Basalto em placas separadas por fendas de lava; cinza, brasas e (por fase) rios de magma, tijolos ou runas."""
    px = _px()
    lw = TILE // px.PX
    g = pal["ground"]
    lava, lava_l = pal["lava"], _shade(pal["lava"], 1.25)
    low = px.banded(px.tile_noise(lw, lw, rnd, (8, 16, 32)), px.shades(g, (0.6, 0.74, 0.88, 1.0, 1.12)), 0.1)
    if pal.get("fortress") or pal.get("throne"):   # piso de tijolos de obsidiana com rejunte aceso
        brick = _shade(pal["rock"], 0.85)
        for y in range(lw):
            row = y // 8
            for x in range(lw):
                xo = (x + (6 if row % 2 else 0)) % 12
                c = low.get_at((x, y))
                if y % 8 == 0 or xo == 0:
                    c = _shade(lava, 0.35) if (x * 3 + y * 5) % 11 else _shade(lava, 0.75)
                elif y % 8 == 1:
                    c = _shade(brick, 1.25)
                else:
                    c = _shade(brick, 0.85 + 0.2 * (px._BAYER[y % 4][x % 4] / 15))
                low.set_at((x, y), c)
    bricks = pal.get("fortress") or pal.get("throne")
    ridge = _noise01(px, lw, rnd, (5, 10))
    river = _noise01(px, lw, rnd, (4, 8)) if pal.get("magma") else None
    for y in range(lw):   # placas de basalto separadas por fendas de lava
        for x in range(lw):
            v = ridge[y][x]
            if bricks:
                pass
            elif abs(v - 0.5) < 0.012:
                low.set_at((x, y), lava if (x + y) % 5 else lava_l)
            elif abs(v - 0.5) < 0.03 and v > 0.5:
                low.set_at((x, y), _shade(low.get_at((x, y)), 1.18))
            if river is not None:   # rios de magma (largos, com borda de crosta)
                rv = river[y][x]
                if abs(rv - 0.5) < 0.022:
                    low.set_at((x, y), lava_l if abs(rv - 0.5) < 0.008 else lava)
                elif abs(rv - 0.5) < 0.034:
                    low.set_at((x, y), _shade(g, 0.45))
    for _ in range(16):   # rachaduras com brilho
        _walk(low, rnd, rnd.randrange(lw), rnd.randrange(lw), rnd.randint(8, 20), _shade(lava, 0.85),
              glow=_shade(lava, 0.55))
    for _ in range(220):   # pedrinhas de basalto
        x, y = rnd.randrange(lw), rnd.randrange(lw)
        c = _shade(pal["rock"], rnd.uniform(0.8, 1.1))
        _put(low, x, y, c)
        _put(low, x, y - 1, _shade(c, 1.25))
        _put(low, x, y + 1, _shade(g, 0.5))
    for _ in range(120):   # brasas
        _put(low, rnd.randrange(lw), rnd.randrange(lw), pal["accent"] if rnd.random() < 0.5 else lava)
    if pal.get("ash"):   # cinza clara espalhada
        ash = _noise01(px, lw, rnd, (6, 12))
        for y in range(lw):
            for x in range(lw):
                if ash[y][x] > 0.72 and (px._BAYER[y % 4][x % 4] / 15) < (ash[y][x] - 0.72) * 4:
                    low.set_at((x, y), (120, 110, 108) if (x + y) % 3 else (150, 140, 136))
    if pal.get("bones"):
        for _ in range(60):   # lascas de osso
            x, y = rnd.randrange(lw), rnd.randrange(lw)
            _put(low, x, y, (220, 210, 190))
            _put(low, x + 1, y, (190, 180, 160))
    if pal.get("throne"):   # círculos de runas roxas
        for _ in range(2):
            cx, cy = rnd.randrange(lw), rnd.randrange(lw)
            acc = pal["accent"]
            for ang in range(0, 360, 6):
                r = 11
                _put(low, cx + int(math.cos(math.radians(ang)) * r), cy + int(math.sin(math.radians(ang)) * r),
                     _shade(acc, 0.8))
            for k in range(5):   # estrela de 5 pontas
                a0, a1 = math.radians(-90 + k * 144), math.radians(-90 + (k + 1) * 144)
                for t in range(12):
                    f = t / 11
                    _put(low, cx + int((math.cos(a0) * (1 - f) + math.cos(a1) * f) * 10),
                         cy + int((math.sin(a0) * (1 - f) + math.sin(a1) * f) * 10), acc)
    return low


# ------------------------------------------------------------------ obstáculos
def _canvas():
    return pygame.Surface((120, 120), pygame.SRCALPHA)


def _glow(s, c, r, col, alpha=60):
    g = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    for y in range(0, s.get_height(), 2):
        for x in range(0, s.get_width(), 2):
            d = math.hypot(x - c[0], y - c[1])
            if d < r and (x // 2 + y // 2) % 2 == 0:
                pygame.draw.rect(g, (*col, int(alpha * (1 - d / r))), (x, y, 2, 2))
    s.blit(g, (0, 0))


def _spikes(pal, rnd):
    """Espinhos de obsidiana: lâminas pretas brilhantes com faces roxas e brasa na base."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 90), (c - 36, c + 8, 74, 24))
    _glow(s, (c, c + 18), 36, pal["lava"], 50)
    for dx, h, w, lean in ((-20, 34, 9, -0.35), (16, 40, 10, 0.3), (0, 60, 13, 0.0), (-6, 24, 7, -0.6),
                           (28, 20, 6, 0.6)):
        base_y = c + 18
        tx, ty = c + dx + math.sin(lean) * h, base_y - math.cos(lean) * h
        left = [(c + dx - w, base_y), (tx, ty), (c + dx, base_y)]
        right = [(c + dx, base_y), (tx, ty), (c + dx + w, base_y)]
        pygame.draw.polygon(s, (52, 40, 62), left)
        pygame.draw.polygon(s, (28, 22, 34), right)
        pygame.draw.line(s, (130, 100, 160), (c + dx - w * 0.4, base_y - 2), (tx, ty), 1)   # brilho de vidro
        pygame.draw.polygon(s, (14, 10, 18), [(c + dx - w, base_y), (tx, ty), (c + dx + w, base_y)], 2)
    for _ in range(5):
        x = c + rnd.uniform(-30, 30)
        pygame.draw.circle(s, pal["lava"], (int(x), c + 20), 1)
    return s


def _brimstone(pal, rnd):
    """Rochedo de enxofre: pedras amareladas e fumegantes com crosta escura."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 40, c + 4, 82, 28))
    for dx, dy, r in ((-14, 4, 22), (14, 2, 20), (0, -12, 20), (24, 14, 11), (-27, 14, 10)):
        base = (190, 160, 70) if rnd.random() < 0.6 else _shade(pal["rock"], 1.1)
        base = _shade(base, rnd.uniform(0.85, 1.05))
        pts = []
        for k in range(6):
            a = math.radians(k * 60 + rnd.uniform(-18, 18))
            rr = r * rnd.uniform(0.8, 1.05)
            pts.append((c + dx + math.cos(a) * rr, c + dy + math.sin(a) * rr * 0.85))
        pygame.draw.polygon(s, base, pts)
        top = [p for p in pts if p[1] <= c + dy] + [(c + dx, c + dy)]
        if len(top) >= 3:
            pygame.draw.polygon(s, _shade(base, 1.22), top)
        pygame.draw.polygon(s, _shade(base, 0.5), pts, 2)
    for k in range(3):   # fumaça
        pygame.draw.circle(s, (150, 140, 120, 90), (c - 10 + k * 10, c - 34 - k * 6), 5 + k)
    return s


def _brazier(pal):
    """Braseiro do inferno: bacia de ferro com chifres, pés de garra e fogo alto."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 26, c + 14, 52, 16))
    _glow(s, (c, c - 20), 46, (255, 130, 50), 70)
    iron, iron_d, iron_l = (62, 56, 64), (36, 32, 40), (110, 100, 112)
    for sx in (-1, 1):   # pés
        pygame.draw.line(s, iron_d, (c + 6 * sx, c - 2), (c + 20 * sx, c + 22), 4)
    pygame.draw.line(s, iron, (c, c - 2), (c, c + 22), 5)
    pygame.draw.polygon(s, iron, [(c - 26, c - 16), (c + 26, c - 16), (c + 16, c), (c - 16, c)])   # bacia
    pygame.draw.line(s, iron_l, (c - 26, c - 16), (c + 26, c - 16), 2)
    pygame.draw.polygon(s, iron_d, [(c - 26, c - 16), (c + 26, c - 16), (c + 16, c), (c - 16, c)], 2)
    for sx in (-1, 1):   # chifres
        pygame.draw.polygon(s, (200, 190, 175), [(c + 22 * sx, c - 16), (c + 32 * sx, c - 30), (c + 26 * sx, c - 14)])
    lava = pal["lava"]
    for k, (col, h, w) in enumerate((((200, 50, 20), 42, 22), (lava, 34, 17), ((255, 210, 110), 20, 9))):
        pts = [(c - w, c - 16), (c - w * 0.5, c - 16 - h * 0.6), (c - w * 0.1, c - 16 - h), (c + w * 0.3, c - 16 - h * 0.7),
               (c + w * 0.6, c - 16 - h * 0.85), (c + w, c - 16)]
        pygame.draw.polygon(s, col, pts)
    return s


def _skulls(pal, rnd):
    """Pilha de caveiras (de gato, com orelhinhas) e ossos."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 34, c + 8, 70, 22))
    bone, bone_d, hole = (226, 216, 196), (170, 160, 140), (40, 28, 30)
    for (x, y) in ((-16, 12), (14, 12), (0, 12), (-8, 0), (10, 0), (1, -11)):
        cx, cy = c + x, c + y
        for sx in (-1, 1):
            pygame.draw.polygon(s, bone, [(cx + 3 * sx, cy - 6), (cx + 7 * sx, cy - 12), (cx + 8 * sx, cy - 3)])
        pygame.draw.circle(s, bone, (cx, cy), 8)
        pygame.draw.rect(s, bone, (cx - 5, cy + 3, 10, 5))
        pygame.draw.circle(s, bone_d, (cx, cy), 8, 1)
        pygame.draw.circle(s, hole, (cx - 3, cy - 1), 2)
        pygame.draw.circle(s, hole, (cx + 3, cy - 1), 2)
        pygame.draw.polygon(s, hole, [(cx - 1, cy + 3), (cx + 1, cy + 3), (cx, cy + 4)])
    for k in range(3):
        x = c - 28 + k * 22
        pygame.draw.line(s, bone, (x, c + 22), (x + 14, c + 18), 3)
    return s


def _obelisk(pal):
    """Obelisco demoníaco: pedra escura com runas acesas e um olho no topo."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 90), (c - 26, c + 14, 52, 16))
    acc = pal["accent"]
    _glow(s, (c, c - 10), 40, acc, 45)
    rock = _shade(pal["rock"], 0.9)
    pygame.draw.polygon(s, _shade(rock, 0.8), [(c - 22, c + 22), (c + 22, c + 22), (c + 18, c + 12), (c - 18, c + 12)])
    pts = [(c - 13, c + 12), (c - 9, c - 40), (c, c - 50), (c + 9, c - 40), (c + 13, c + 12)]
    pygame.draw.polygon(s, rock, pts)
    pygame.draw.polygon(s, _shade(rock, 1.25), [(c - 13, c + 12), (c - 9, c - 40), (c, c - 50), (c - 2, c + 12)])
    pygame.draw.polygon(s, _shade(rock, 0.45), pts, 2)
    for k, y in enumerate((c - 30, c - 18, c - 6, c + 4)):   # runas
        if k % 2:
            pygame.draw.line(s, acc, (c - 4, y), (c + 4, y + 4), 2)
            pygame.draw.line(s, acc, (c + 4, y), (c - 4, y + 4), 2)
        else:
            pygame.draw.line(s, acc, (c, y - 2), (c, y + 5), 2)
            pygame.draw.line(s, acc, (c - 4, y + 1), (c + 4, y + 1), 2)
    pygame.draw.ellipse(s, (255, 230, 120), (c - 5, c - 44, 10, 6))   # olho
    pygame.draw.line(s, (40, 10, 10), (c, c - 44), (c, c - 39), 2)
    return s


def _cage(pal):
    """Gaiola de ferro pendurada numa forca de chifres, com correntes."""
    s = _canvas()
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 30, c + 14, 60, 16))
    iron, iron_d = (80, 72, 80), (40, 36, 42)
    pygame.draw.rect(s, iron_d, (c - 26, c - 46, 6, 70))                       # poste
    pygame.draw.line(s, iron, (c - 23, c - 46), (c + 16, c - 46), 5)           # braço
    pygame.draw.line(s, iron, (c + 10, c - 44), (c + 10, c - 30), 2)           # corrente
    for x in range(c - 2, c + 23, 6):                                          # gaiola
        pygame.draw.line(s, iron, (x, c - 30), (x, c + 4), 2)
    pygame.draw.ellipse(s, iron_d, (c - 4, c - 34, 28, 8), 2)
    pygame.draw.ellipse(s, iron_d, (c - 4, c, 28, 8), 2)
    pygame.draw.circle(s, (226, 216, 196), (c + 10, c - 6), 5)                 # caveira dentro
    pygame.draw.circle(s, (40, 28, 30), (c + 8, c - 7), 1)
    pygame.draw.circle(s, (40, 28, 30), (c + 12, c - 7), 1)
    return s


def obstacles(pal, seed):
    from scenery_biomes import _lava_pool
    rnd = random.Random(seed + 23)
    out = [(_spikes(pal, rnd), 24), (_brimstone(pal, rnd), 28), (_skulls(pal, rnd), 24)]
    if pal.get("ash") or pal.get("bones"):
        out.append((_cage(pal), 22))
    if pal.get("magma") or pal.get("ash"):
        out += [(_lava_pool(pal), 30), (_lava_pool(pal), 30)]
    if pal.get("fortress") or pal.get("throne"):
        out += [(_brazier(pal), 20), (_obelisk(pal), 20), (_brazier(pal), 20)]
    if pal.get("bones"):
        out.append((_skulls(pal, rnd), 24))
    return out


# ------------------------------------------------------------------ decoração
def decor(pal, rnd):
    out = {}

    def surf(w, h):
        return pygame.Surface((w, h), pygame.SRCALPHA)

    rock = pal["rock"]
    s = surf(26, 16)                                                           # pedrinhas de basalto
    for (x, y) in ((3, 9), (10, 6), (17, 9), (12, 11)):
        col = _shade(rock, rnd.uniform(0.75, 1.0))
        pygame.draw.polygon(s, col, [(x, y + 4), (x + 1, y), (x + 5, y - 1), (x + 6, y + 4)])
        pygame.draw.line(s, _shade(col, 1.35), (x + 1, y), (x + 5, y - 1), 1)
    out["pebbles"] = s
    s = surf(24, 26)                                                           # labareda saindo do chão
    glow = surf(24, 26)
    pygame.draw.circle(glow, (255, 140, 60, 60), (12, 16), 11)
    s.blit(glow, (0, 0))
    pygame.draw.polygon(s, (220, 60, 20), [(5, 24), (8, 12), (11, 16), (13, 4), (16, 14), (19, 24)])
    pygame.draw.polygon(s, pal["lava"], [(8, 24), (11, 16), (13, 10), (15, 17), (16, 24)])
    pygame.draw.polygon(s, (255, 220, 120), [(10, 24), (12, 18), (14, 24)])
    out["flame"] = s
    s = surf(30, 14)                                                           # brasas no chão
    for (x, y) in ((4, 8), (10, 5), (15, 9), (22, 6), (26, 10)):
        pygame.draw.circle(s, _shade(rock, 0.6), (x, y), 3)
        s.set_at((x, y), pal["lava"])
        s.set_at((x + 1, y - 1), (255, 220, 120))
    out["embers"] = s
    s = surf(40, 20)                                                           # rachadura de lava
    pts = [(2, 12), (10, 9), (16, 13), (24, 8), (31, 11), (38, 6)]
    pygame.draw.lines(s, (200, 60, 20), False, pts, 4)
    pygame.draw.lines(s, (255, 200, 90), False, pts, 1)
    out["crack"] = s
    s = surf(34, 22)                                                           # caveira de gato e ossos
    bone = (222, 214, 194)
    pygame.draw.line(s, bone, (3, 18), (18, 14), 3)
    for sx in (-1, 1):
        pygame.draw.polygon(s, bone, [(23 + 3 * sx, 6), (23 + 6 * sx, 0), (23 + 7 * sx, 8)])
    pygame.draw.circle(s, bone, (23, 11), 7)
    pygame.draw.circle(s, (34, 28, 30), (20, 10), 2)
    pygame.draw.circle(s, (34, 28, 30), (26, 10), 2)
    out["skull"] = s
    if pal.get("ash"):
        s = surf(36, 16)                                                       # monte de cinza
        pygame.draw.ellipse(s, (110, 102, 100), (2, 4, 32, 11))
        pygame.draw.ellipse(s, (140, 132, 128), (8, 4, 18, 6))
        s.set_at((18, 9), (255, 120, 40))
        out["ash"] = s
    if pal.get("fortress") or pal.get("throne"):
        s = surf(44, 14)                                                       # corrente caída
        for k in range(6):
            pygame.draw.ellipse(s, (90, 84, 92), (2 + k * 7, 3 + (k % 2) * 2, 9, 7), 2)
        out["chain"] = s
    if pal.get("throne"):
        s = surf(30, 30)                                                       # vela de cera preta com chama roxa
        glow = surf(30, 30)
        pygame.draw.circle(glow, (*pal["accent"], 50), (15, 11), 12)
        s.blit(glow, (0, 0))
        for x, h in ((8, 10), (16, 15), (22, 7)):
            pygame.draw.rect(s, (40, 32, 42), (x - 2, 26 - h, 5, h))
            pygame.draw.ellipse(s, pal["accent"], (x - 2, 19 - h, 5, 8))
            pygame.draw.ellipse(s, (240, 210, 255), (x - 1, 22 - h, 3, 4))
        out["candle"] = s
    return out
