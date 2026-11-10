"""Cenário das florestas: chão de grama, mato/flores/pedras decorativos e árvores que bloqueiam a party.

O mundo é infinito: ele é dividido em blocos (chunks) gerados na hora a partir de uma semente, então o mesmo
lugar sempre tem as mesmas árvores durante a run. Só os personagens da party colidem com as árvores
(os inimigos passam por baixo das copas, para a horda não travar).
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

import pixel
import scenery_biomes as sb

CHUNK = 512
TILE = 512                 # ladrilho do chão (grande para a repetição não aparecer)
SAFE_RADIUS = 220          # sem árvores perto do ponto onde a party começa
TREE_HIT = 24              # raio de colisão do tronco/base da árvore

# paleta por fase (Floresta I .. V): grama, grama escura, folhas, folhas escuras, tronco, flores
PALETTES = [
    dict(grass=(62, 104, 52), dark=(52, 90, 45), light=(78, 124, 62), leaf=(52, 120, 58), leaf2=(38, 92, 46),
         trunk=(100, 70, 45), flowers=[(235, 220, 90), (240, 240, 245), (220, 120, 160)], trees=(2, 4)),
    dict(grass=(55, 96, 48), dark=(45, 82, 42), light=(70, 114, 58), leaf=(44, 108, 52), leaf2=(32, 82, 42),
         trunk=(90, 64, 42), flowers=[(230, 200, 80), (200, 220, 245)], trees=(3, 5)),
    dict(grass=(48, 80, 46), dark=(38, 66, 40), light=(60, 96, 54), leaf=(40, 90, 50), leaf2=(28, 66, 38),
         trunk=(80, 60, 44), flowers=[(210, 210, 220), (170, 140, 200)], trees=(3, 5), webs=True),
    dict(grass=(52, 76, 60), dark=(42, 64, 52), light=(64, 90, 72), leaf=(46, 84, 66), leaf2=(32, 62, 50),
         trunk=(74, 62, 54), flowers=[(190, 200, 215), (150, 170, 200)], trees=(3, 6)),
    dict(grass=(66, 62, 52), dark=(54, 50, 44), light=(80, 74, 60), leaf=(90, 50, 80), leaf2=(64, 34, 60),
         trunk=(70, 52, 50), flowers=[(170, 60, 90), (120, 200, 110)], trees=(3, 6), dead=True),
]


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


ALL_PALETTES = PALETTES + sb.PALETTES   # Floresta, Cidade, Catedral, Subterrâneo e Inferno (I-V cada)


class Scenery:
    def __init__(self, stage_index=0, seed=None):
        self.pal = ALL_PALETTES[max(0, min(len(ALL_PALETTES) - 1, stage_index))]
        self.theme = self.pal.get("theme", "forest")
        self.seed = random.randrange(1 << 30) if seed is None else seed
        self.chunks = {}
        if self.theme == "forest":
            self.ground = self._make_ground()
            self.tree_sprites = [self._make_tree(v) for v in range(3)]
            self.tree_hits = [TREE_HIT] * 3
            self.decor_sprites = self._make_decor()
            self.decor_kinds = (["tuft"] * 6 + ["bush"] * 2 +
                                [f"flower{k}" for k in range(len(self.pal["flowers"]))] * 2 + ["rock"] +
                                ["shroom", "stump", "log"])
        else:   # Cidade, Catedral e Subterrâneo: obstáculos e decoração do tema (scenery_biomes.py)
            rnd = random.Random(self.seed)
            self.ground = sb.make_ground_pixel(self.pal, rnd)   # chão desenhado direto em pixel art
            obs = sb.make_obstacles(self.pal, self.seed)
            self.tree_sprites = [o[0] for o in obs]
            self.tree_hits = [o[1] for o in obs]
            self.decor_sprites = sb.make_decor(self.pal, random.Random(self.seed + 999))
            self.decor_kinds = sb.decor_kinds(self.decor_sprites)
        self.max_hit = max(self.tree_hits)
        # pixel art: chão pontilhado e objetos com contorno escuro
        self.tree_sprites = [pixel.pixel_sprite(t) for t in self.tree_sprites]
        self.decor_sprites = {k: pixel.pixel_sprite(v, outline=None, light=False) for k, v in self.decor_sprites.items()}

    # ------------------------------------------------------------------ geração
    def _make_ground(self):
        """Ladrilho de grama em pixel art (repete sem emenda): ruído em faixas, tufos, folhas e terra."""
        rnd = random.Random(self.seed)
        px = pixel.PX
        lw = TILE // px
        g = self.pal["grass"]
        cols = pixel.shades(g, (0.6, 0.74, 0.87, 1.0, 1.1))
        low = pixel.banded(pixel.tile_noise(lw, lw, rnd, (8, 16, 32)), cols, 0.09)
        dirt = _shade(self.pal["trunk"], 0.8)
        mud = pixel.tile_noise(lw, lw, rnd, (10, 20, 40), (0.5, 0.35, 0.15))
        lo = min(min(r) for r in mud)
        hi = max(max(r) for r in mud)
        for y in range(lw):   # manchas de terra nos pontos mais "baixos" do ruído (trilhas)
            for x in range(lw):
                v = (mud[y][x] - lo) / ((hi - lo) or 1)
                if v < 0.09 or (v < 0.14 and pixel._BAYER[y % 4][x % 4] < 8):
                    low.set_at((x, y), _shade(dirt, 0.85 + 0.15 * ((x * 7 + y * 3) % 3) / 2))
        light, dark = _shade(g, 1.35), _shade(g, 0.5)
        for _ in range(560):   # tufos de grama: 2-3 lâminas com sombra embaixo
            x, y = rnd.randrange(lw), rnd.randrange(lw)
            for dx, hgt in ((-1, 2), (0, 3), (1, 2)):
                if rnd.random() < 0.8:
                    for k in range(hgt):
                        low.set_at(((x + dx) % lw, (y - k) % lw), light if k else _shade(g, 1.15))
            low.set_at((x % lw, (y + 1) % lw), dark)
        leaf_cols = [_shade(self.pal["trunk"], 1.3), (150, 110, 50), _shade(g, 0.45)]
        for _ in range(240):    # folhas secas e pedrinhas
            x, y = rnd.randrange(lw), rnd.randrange(lw)
            low.set_at((x, y), rnd.choice(leaf_cols))
        return pygame.transform.scale(low, (lw * px, lw * px))

    def _make_tree(self, variant):
        """Árvore: raízes e tronco com casca, copa em tufos de folhas com luz em cima e sombra embaixo.
        Floresta V: árvore seca retorcida com galhos bifurcados e musgo pendurado."""
        rnd = random.Random(self.seed + 17 * (variant + 1))
        size = 120
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        trunk = self.pal["trunk"]
        t_hi, t_lo = _shade(trunk, 1.3), _shade(trunk, 0.6)
        pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 42, c + 2, 88, 40))           # sombra
        for sx in (-1, 1):                                                        # raízes
            pygame.draw.polygon(s, trunk, [(c + 6 * sx, c + 12), (c + 18 * sx, c + 26), (c + 4 * sx, c + 22)])
            pygame.draw.line(s, t_lo, (c + 8 * sx, c + 16), (c + 16 * sx, c + 25), 1)
        pygame.draw.polygon(s, trunk, [(c - 9, c + 24), (c - 7, c - 4), (c + 7, c - 4), (c + 9, c + 24)])   # tronco
        pygame.draw.polygon(s, t_hi, [(c - 9, c + 24), (c - 7, c - 4), (c - 3, c - 4), (c - 4, c + 24)])
        pygame.draw.line(s, t_lo, (c + 4, c - 2), (c + 6, c + 22), 2)
        for y in (c + 4, c + 12):                                                 # casca
            pygame.draw.line(s, t_lo, (c - 3, y), (c + 1, y + 3), 1)
        if self.pal.get("dead"):   # árvore seca retorcida
            def branch(x, y, ang, L, w, depth):
                ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
                pygame.draw.line(s, _shade(trunk, 0.9), (x, y), (ex, ey), max(1, w))
                pygame.draw.line(s, t_hi, (x - 1, y), (ex - 1, ey), 1)
                if depth:
                    for d in (-0.5, 0.45):
                        branch(ex, ey, ang + d + rnd.uniform(-0.2, 0.2), L * 0.65, w - 2, depth - 1)
                elif rnd.random() < 0.5:
                    pygame.draw.circle(s, self.pal["leaf"], (ex, ey), 3)
            for ang in (-2.2, -1.6, -1.0):
                branch(c, c - 2, ang + rnd.uniform(-0.15, 0.15), rnd.uniform(18, 24), 5, 2)
            for k in range(3):                                                    # musgo pendurado
                x = c + rnd.uniform(-26, 26)
                y = c - rnd.uniform(14, 30)
                pygame.draw.line(s, (110, 120, 80), (x, y), (x, y + rnd.uniform(6, 12)), 1)
            return s
        leaf, leaf2 = self.pal["leaf"], self.pal["leaf2"]
        leaf_hi = _shade(leaf, 1.25)
        clumps = [(rnd.uniform(-20, 20), rnd.uniform(-34, -6), rnd.uniform(12, 17)) for _ in range(7)]
        clumps.sort(key=lambda b: b[1])
        for dx, dy, r in clumps:                                                  # contorno escuro dos tufos
            pygame.draw.circle(s, leaf2, (c + dx, c + dy + 2), r + 2)
        for dx, dy, r in clumps:                                                  # tufo: base, luz e sombra
            cx, cy = c + dx, c + dy
            pygame.draw.circle(s, leaf, (cx, cy), r)
            pygame.draw.circle(s, _shade(leaf, 0.82), (cx + r * 0.25, cy + r * 0.3), r * 0.7)
            pygame.draw.circle(s, leaf, (cx - r * 0.1, cy - r * 0.1), r * 0.7)
            pygame.draw.circle(s, leaf_hi, (cx - r * 0.35, cy - r * 0.4), r * 0.35)
            for _k in range(4):                                                   # folhinhas
                a = rnd.uniform(0, math.tau)
                q = (cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.7)
                pygame.draw.line(s, leaf2 if q[1] > cy else leaf_hi, q, (q[0] + 2, q[1] - 2), 2)
        if variant == 2 and not self.pal.get("webs"):                             # frutinhas / flores
            fc = self.pal["flowers"][0]
            for _k in range(5):
                pygame.draw.circle(s, fc, (c + rnd.uniform(-24, 22), c + rnd.uniform(-36, -8)), 2)
        if self.pal.get("webs") and variant == 0:   # teias na Floresta III
            for k in range(6):
                a = k * math.tau / 6
                pygame.draw.line(s, (220, 220, 230, 150), (c - 14, c - 18), (c - 14 + math.cos(a) * 20,
                                                                              c - 18 + math.sin(a) * 20), 1)
            for rr in (7, 13, 19):
                pygame.draw.circle(s, (220, 220, 230, 120), (c - 14, c - 18), rr, 1)
        return s

    def _make_decor(self):
        """Mato, arbustos com frutinhas, flores, pedras com musgo, cogumelos, toco e tronco caído (não bloqueiam)."""
        rnd = random.Random(self.seed + 999)
        out = {}
        light, dark = self.pal["light"], self.pal["dark"]
        s = pygame.Surface((30, 26), pygame.SRCALPHA)                              # mato alto em 3 tons
        pygame.draw.ellipse(s, (0, 0, 0, 50), (3, 20, 24, 6))
        for i in range(10):
            x = 4 + i * 2.4
            h = rnd.uniform(10, 22)
            col = [_shade(dark, 0.9), light, _shade(light, 1.3)][i % 3]
            pygame.draw.line(s, col, (x, 24), (x + rnd.uniform(-4, 4), 24 - h), 2)
        out["tuft"] = s
        s = pygame.Surface((46, 36), pygame.SRCALPHA)                              # arbusto com frutinhas
        pygame.draw.ellipse(s, (0, 0, 0, 60), (4, 24, 40, 11))
        for dx, dy, r in ((13, 20, 10), (24, 15, 12), (34, 20, 9), (22, 23, 10)):
            pygame.draw.circle(s, self.pal["leaf2"], (dx, dy + 1), r + 2)
            pygame.draw.circle(s, self.pal["leaf"], (dx, dy), r)
            pygame.draw.circle(s, _shade(self.pal["leaf"], 1.25), (dx - r * 0.35, dy - r * 0.4), r * 0.35)
        berry = self.pal["flowers"][-1]
        for (x, y) in ((16, 16), (28, 12), (33, 22), (20, 24)):
            pygame.draw.circle(s, berry, (x, y), 2)
            pygame.draw.circle(s, (255, 255, 255), (x - 1, y - 1), 1)
        out["bush"] = s
        for k, fc in enumerate(self.pal["flowers"]):                               # flores com pétalas e folhas
            s = pygame.Surface((24, 20), pygame.SRCALPHA)
            for i in range(3):
                x, y = 4 + i * 7, 6 + (i % 2) * 5
                pygame.draw.line(s, dark, (x, y + 2), (x, y + 10), 1)
                pygame.draw.line(s, light, (x, y + 7), (x + 3, y + 5), 1)
                for a in range(0, 360, 72):
                    pygame.draw.circle(s, fc, (x + math.cos(math.radians(a)) * 2, y + math.sin(math.radians(a)) * 2), 1)
                pygame.draw.circle(s, (250, 230, 120), (x, y), 1)
            out[f"flower{k}"] = s
        s = pygame.Surface((28, 22), pygame.SRCALPHA)                              # pedra com musgo e trinca
        pygame.draw.ellipse(s, (0, 0, 0, 60), (3, 13, 24, 8))
        pygame.draw.polygon(s, (112, 112, 110), [(3, 15), (6, 6), (14, 3), (23, 6), (25, 15)])
        pygame.draw.polygon(s, (146, 146, 142), [(6, 7), (14, 4), (20, 6), (12, 9)])
        pygame.draw.line(s, (80, 80, 80), (15, 9), (18, 14), 1)
        pygame.draw.line(s, (90, 130, 70), (5, 13), (11, 15), 2)
        out["rock"] = s
        s = pygame.Surface((26, 22), pygame.SRCALPHA)                              # cogumelos
        for (x, y, r, col) in ((7, 13, 5, (190, 60, 50)), (17, 10, 6, (190, 60, 50)), (12, 16, 3, (210, 180, 130))):
            pygame.draw.line(s, (232, 224, 205), (x, y), (x, y + 6), 2)
            pygame.draw.circle(s, col, (x, y), r, draw_bottom_left=False, draw_bottom_right=False)
            pygame.draw.circle(s, (250, 240, 230), (x - r // 2, y - r // 2), 1)
        out["shroom"] = s
        s = pygame.Surface((30, 24), pygame.SRCALPHA)                              # toco com anéis
        tr = self.pal["trunk"]
        pygame.draw.ellipse(s, (0, 0, 0, 60), (2, 15, 26, 8))
        pygame.draw.rect(s, tr, (6, 8, 18, 12))
        pygame.draw.line(s, _shade(tr, 1.3), (7, 9), (7, 19), 2)
        pygame.draw.ellipse(s, _shade(tr, 1.5), (6, 4, 18, 8))
        pygame.draw.ellipse(s, _shade(tr, 1.1), (10, 6, 10, 4), 1)
        pygame.draw.line(s, (90, 130, 70), (18, 18), (22, 14), 2)
        out["stump"] = s
        s = pygame.Surface((48, 20), pygame.SRCALPHA)                              # tronco caído
        pygame.draw.ellipse(s, (0, 0, 0, 60), (3, 12, 42, 7))
        pygame.draw.rect(s, tr, (6, 5, 34, 10))
        pygame.draw.line(s, _shade(tr, 1.3), (6, 6), (39, 6), 2)
        pygame.draw.line(s, _shade(tr, 0.6), (6, 14), (39, 14), 1)
        pygame.draw.ellipse(s, _shade(tr, 1.5), (36, 4, 8, 11))
        pygame.draw.ellipse(s, _shade(tr, 1.1), (38, 7, 4, 5), 1)
        for x in (12, 22, 30):
            pygame.draw.line(s, _shade(tr, 0.7), (x, 8), (x + 3, 11), 1)
        pygame.draw.circle(s, (190, 60, 50), (18, 4), 2)
        out["log"] = s
        return out

    def chunk(self, cx, cy):
        key = (cx, cy)
        ch = self.chunks.get(key)
        if ch is not None:
            return ch
        rnd = random.Random(hash((self.seed, cx, cy)))
        x0, y0 = cx * CHUNK, cy * CHUNK
        trees = []
        lo, hi = self.pal.get("trees") or self.pal["obstacles"]
        for _ in range(rnd.randint(lo, hi)):
            for _try in range(8):
                p = V(x0 + rnd.uniform(30, CHUNK - 30), y0 + rnd.uniform(30, CHUNK - 30))
                if p.length() < SAFE_RADIUS:
                    continue
                if all((p - t[0]).length() > 110 for t in trees):
                    trees.append((p, rnd.randrange(len(self.tree_sprites))))
                    break
        decor = []
        kinds = self.decor_kinds
        for _ in range(rnd.randint(10, 18)):
            decor.append((V(x0 + rnd.uniform(0, CHUNK), y0 + rnd.uniform(0, CHUNK)), rnd.choice(kinds)))
        ch = (trees, decor)
        if len(self.chunks) > 400:
            self.chunks.clear()
        self.chunks[key] = ch
        return ch

    def _chunks_around(self, pos, radius):
        x0, x1 = int((pos.x - radius) // CHUNK), int((pos.x + radius) // CHUNK)
        y0, y1 = int((pos.y - radius) // CHUNK), int((pos.y + radius) // CHUNK)
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                yield self.chunk(cx, cy)

    def trees_near(self, pos, radius):
        """(posição, raio de colisão) dos obstáculos perto de pos."""
        for trees, _ in self._chunks_around(pos, radius + self.max_hit):
            for t in trees:
                hit = self.tree_hits[t[1]]
                if (t[0] - pos).length_squared() < (radius + hit) ** 2:
                    yield t[0], hit

    # ------------------------------------------------------------------ colisão
    def collide(self, u):
        """Empurra um personagem para fora das árvores (ele desliza pela borda do tronco)."""
        for tp, hit in self.trees_near(u.pos, u.r + 4):
            d = u.pos - tp
            m = u.r + hit
            dist2 = d.length_squared()
            if dist2 < m * m:
                if dist2 < 1e-6:
                    d = V(1, 0)
                    dist2 = 1.0
                u.pos = tp + d * (m / math.sqrt(dist2))

    def free_pos(self, pos, margin=30):
        """Posição livre de árvores (para drops que o herói precisa alcançar)."""
        p = V(pos)
        for tp, hit in self.trees_near(p, margin):
            d = p - tp
            m = hit + margin
            if d.length_squared() < m * m:
                p = tp + (d.normalize() if d.length_squared() > 1e-6 else V(1, 0)) * m
        return p

    # ------------------------------------------------------------------ desenho
    def draw_ground(self, s, cam, W, H):
        ox, oy = int(-cam.x % TILE), int(-cam.y % TILE)
        for x in range(ox - TILE, W, TILE):
            for y in range(oy - TILE, H, TILE):
                s.blit(self.ground, (x, y))
        center = cam + V(W / 2, H / 2)
        rad = max(W, H) / 2 + 80
        for _, decor in self._chunks_around(center, rad):
            for p, kind in decor:
                sp = p - cam
                if -40 < sp.x < W + 40 and -40 < sp.y < H + 40:
                    img = self.decor_sprites[kind]
                    s.blit(img, (sp.x - img.get_width() / 2, sp.y - img.get_height() / 2))

    def draw_trees(self, s, cam, W, H):
        center = cam + V(W / 2, H / 2)
        rad = max(W, H) / 2 + 100
        items = []
        for trees, _ in self._chunks_around(center, rad):
            for p, v in trees:
                sp = p - cam
                if -80 < sp.x < W + 80 and -100 < sp.y < H + 80:
                    items.append((sp, v))
        items.sort(key=lambda it: it[0].y)
        for sp, v in items:
            img = self.tree_sprites[v]
            s.blit(img, (sp.x - img.get_width() / 2, sp.y - img.get_height() / 2 - 14))
