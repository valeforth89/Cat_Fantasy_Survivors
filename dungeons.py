"""Masmorras (portal vermelho no acampamento): Cavern, Catacomb e Dungeon.

Diferente das fases comuns:
- O mapa é um CORREDOR longo: a party anda até o fim, enfrentando os encontros do caminho.
- Só aparecem Super Elites e Esquadrões de Elite, com monstros sorteados de TODOS os tipos do jogo
  (data.ENEMY_TYPES, menos o chefão): monstros novos já entram no sorteio automaticamente.
- No fim do corredor há um chefão aleatório (aparência de um dos chefões das fases), mais forte, com 5 classes.
- Duração média: ~1 min a 1 min 30 s.
- Cada masmorra tem uma recompensa principal: Cavern = muito gold, Catacomb = fragmentos de classe,
  Dungeon = fragmentos de acessório sortidos. Cada uma dropa 5 acessórios próprios (1 de cada tipo).
- Níveis infinitos: concluir o nível N libera o N+1 (mais difícil, mais recompensa). Cada masmorra tem o seu.
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

LENGTH = 3800              # comprimento do corredor (px): ~1 min a 1 min 30 s com as lutas
HALF_H = 250               # metade da altura do corredor
START_X = 0
ENCOUNTER_GAP = 760        # distância entre os encontros
ENCOUNTER_FIRST = 620
TRIGGER_AHEAD = 760        # o encontro aparece quando o herói chega a esta distância dele
BOSS_TRIGGER = 900
BOSS_HP = 1.6              # o chefão das masmorras é mais forte que o das fases
BOSS_CLASSES = 5
SCALE_TIME = 90.0          # crescimento dos inimigos fixo (equivale a 1:30 de uma fase)

# id: nome EN, nome PT, descrição EN, descrição PT, recompensa, acessórios, paleta
DUNGEONS = {
    "cavern": dict(
        name=("Cavern", "Caverna"),
        desc=("A damp cave full of crystals and glittering ore. Every elite carries gold.",
              "Uma caverna úmida cheia de cristais e minério brilhante. Todo elite carrega gold."),
        reward="gold", reward_name=("Lots of gold", "Muito gold"),
        drops=["r_blunt_dmg", "b_thorns", "t_quake", "e_guard"],
        pal=dict(floor=(58, 52, 48), floor2=(66, 60, 54), wall=(40, 36, 34), wall2=(30, 27, 26),
                 edge=(84, 76, 68), accent=(90, 200, 220), accent2=(230, 190, 80)),
        color=(230, 190, 80)),
    "catacomb": dict(
        name=("Catacomb", "Catacumba"),
        desc=("Endless halls of bones and candles. The dead keep the memories of every class.",
              "Corredores sem fim de ossos e velas. Os mortos guardam as memórias de todas as classes."),
        reward="frag", reward_name=("Class fragments", "Fragmentos de classe"),
        drops=["r_holy_dmg", "b_siphon", "t_relic", "e_dawn"],
        pal=dict(floor=(70, 66, 60), floor2=(78, 74, 66), wall=(48, 44, 42), wall2=(36, 33, 32),
                 edge=(110, 104, 94), accent=(235, 225, 200), accent2=(255, 190, 90)),
        color=(200, 180, 255)),
    "dungeon": dict(
        name=("Dungeon", "Masmorra"),
        desc=("An old prison with chains and torches. Its jailers hoard accessory fragments.",
              "Uma prisão antiga com correntes e tochas. Os carcereiros guardam fragmentos de acessório."),
        reward="accfrag", reward_name=("Accessory fragments", "Fragmentos de acessório"),
        drops=["r_iron", "b_executioner", "t_chalice", "e_hunt"],
        pal=dict(floor=(54, 54, 62), floor2=(62, 62, 70), wall=(36, 36, 44), wall2=(26, 26, 32),
                 edge=(80, 80, 92), accent=(255, 150, 60), accent2=(150, 150, 165)),
        color=(120, 220, 230)),
}
ORDER = list(DUNGEONS)


def name(did, lang="en"):
    return DUNGEONS[did]["name"][1 if lang == "pt" else 0]


def mults(level):
    """Multiplicadores do nível (1, 2, 3 ...): sem limite."""
    n = max(0, level - 1)
    return dict(hp=1 + 0.30 * n, dmg=1 + 0.15 * n, res=1 + 0.20 * n, reward=1 + 0.20 * n)


def clear_reward(did, level):
    """Recompensa fixa por concluir (além do que os inimigos dropam)."""
    r = mults(level)["reward"]
    kind = DUNGEONS[did]["reward"]
    if kind == "gold":
        return dict(gold=int(round(15 * r)))
    if kind == "frag":
        return dict(frags=int(round(6 * r)))
    return dict(accfrags=1 + level // 3)


def reward_lines(did, level, lang="en"):
    """Texto da recompensa principal (para a tela de seleção)."""
    pt = lang == "pt"
    r = mults(level)["reward"]
    cr = clear_reward(did, level)
    kind = DUNGEONS[did]["reward"]
    if kind == "gold":
        return [f"Cada elite derruba moedas de gold (x{r:.2f}); o chefão derruba muitas." if pt else
                f"Every elite drops gold coins (x{r:.2f}); the boss drops a lot of them.",
                f"Concluir: +{cr['gold']} gold." if pt else f"Clear: +{cr['gold']} gold."]
    if kind == "frag":
        return ["Fragmentos de classe dos elites e do chefão em dobro." if pt else
                "Class fragments from elites and the boss are doubled.",
                f"Concluir: +{cr['frags']} fragmentos de classes aleatórias." if pt else
                f"Clear: +{cr['frags']} fragments of random classes."]
    return ["Super Elites: 35% de chance de 1 fragmento de acessório; esquadrões: 7% cada; chefão: 3." if pt else
            "Super Elites: 35% chance of 1 accessory fragment; squad elites: 7% each; boss: 3.",
            f"Concluir: +{cr['accfrags']} fragmento(s) de acessório (anel, bracelete, berloque ou emblema)." if pt else
            f"Clear: +{cr['accfrags']} accessory fragment(s) (ring, bracer, trinket or emblem)."]


def encounters():
    """Posições x dos encontros do corredor (antes da sala do chefão)."""
    out = []
    x = ENCOUNTER_FIRST
    while x < LENGTH - BOSS_TRIGGER - 200:
        out.append(x)
        x += ENCOUNTER_GAP
    return out


def monster_pool(roster=None):
    """Monstros das fases já liberadas (de todos os biomas; os novos entram sozinhos quando liberados)."""
    from data import BIOMES, ROLES, ROLE_FROM
    out = []
    for b in BIOMES:
        for pos, sid in enumerate(b["stages"]):
            if roster is not None and not roster.stage_unlocked(sid):
                break
            for r in ROLES:
                k = b["enemies"][r]
                if pos >= ROLE_FROM.get(r, (0, 0))[0] and k not in out:
                    out.append(k)
    return out or ["morcego", "lobo", "javali"]


# ------------------------------------------------------------------ cenário (corredor)
class DungeonScenery:
    """Corredor horizontal: chão com ladrilhos, paredes em cima e embaixo e decoração do tema."""

    def __init__(self, did, seed=None):
        self.did = did
        self.pal = DUNGEONS[did]["pal"]
        self.seed = random.randrange(1 << 30) if seed is None else seed
        rnd = random.Random(self.seed)
        self.tile = self._make_floor(rnd)
        self.wall_tile = self._make_wall(rnd)
        self.decor = []   # (x, lado, tipo)
        x = 120
        while x < LENGTH + 300:
            self.decor.append((x + rnd.uniform(-40, 40), rnd.choice((-1, 1)), rnd.randrange(3)))
            x += rnd.uniform(110, 200)
        self.floor_decor = [(V(rnd.uniform(-100, LENGTH + 200), rnd.uniform(-HALF_H + 30, HALF_H - 30)),
                             rnd.randrange(3)) for _ in range(int(LENGTH / 60))]

    # ------------------------------------------------------------------ texturas em pixel art
    def _make_floor(self, rnd):
        """Chão (256x256, repete sem emenda) desenhado direto em pixel art, no tema da masmorra."""
        import pixel
        p = self.pal
        lw = 256 // pixel.PX
        put = lambda x, y, c: low.set_at((x % lw, y % lw), c)
        if self.did == "cavern":   # rocha úmida em placas, fendas, pedrinhas, minério e cristais
            low = pixel.banded(pixel.tile_noise(lw, lw, rnd, (4, 8, 16)),
                               pixel.shades(p["floor"], (0.66, 0.8, 0.94, 1.06, 1.18)), 0.1)
            ridge = pixel.tile_noise(lw, lw, rnd, (5, 10), (0.6, 0.4))
            lo_, hi_ = min(min(r) for r in ridge), max(max(r) for r in ridge)
            for y in range(lw):
                for x in range(lw):
                    v = (ridge[y][x] - lo_) / ((hi_ - lo_) or 1)
                    if abs(v - 0.5) < 0.022:
                        low.set_at((x, y), _shade(p["floor"], 0.45))
                    elif 0.5 < v < 0.55:
                        low.set_at((x, y), _shade(low.get_at((x, y)), 1.12))
                    elif v < 0.08:
                        low.set_at((x, y), (44, 56, 70) if (x + 2 * y) % 13 else (110, 140, 160))   # poça
            for _ in range(70):
                x, y = rnd.randrange(lw), rnd.randrange(lw)
                c = _shade(p["edge"], rnd.uniform(0.8, 1.1))
                put(x, y, c)
                put(x + 1, y, c)
                put(x, y - 1, _shade(c, 1.25))
                put(x, y + 1, _shade(p["floor"], 0.5))
            for _ in range(24):
                put(rnd.randrange(lw), rnd.randrange(lw), p["accent2"] if rnd.random() < 0.6 else p["accent"])
        else:   # lajes: catacumba (claras, com ossos e cera) e prisão (blocos escuros com musgo e manchas)
            cat = self.did == "catacomb"
            tex = pixel.tile_noise(lw, lw, rnd, (8, 16), (0.6, 0.4))
            lo_, hi_ = min(min(r) for r in tex), max(max(r) for r in tex)
            low = pygame.Surface((lw, lw))
            grout = _shade(p["floor"], 0.5)
            SW, SH = (16, 16) if cat else (24, 16)
            rows = lw // SH + 1
            tones = {(i, j): rnd.uniform(0.88, 1.08) for i in range(lw + 2) for j in range(rows + 1)}
            cuts = {}   # prisão: lajes de larguras irregulares em cada fileira (somam a largura do ladrilho)
            for j in range(rows):
                xs, x = [], 0
                while x < lw:
                    w_ = rnd.randint(14, 30)
                    if lw - (x + w_) < 12:
                        w_ = lw - x
                    xs.append((x, w_))
                    x += w_
                cuts[j] = xs
            for y in range(lw):
                j = y // SH
                for x in range(lw):
                    if cat:
                        i, lx, SWc = x // SW, x % SW, SW
                    else:
                        i, (x0, SWc) = next((k, cc) for k, cc in enumerate(cuts[j]) if cc[0] <= x < cc[0] + cc[1])
                        lx = x - x0
                    ly = y % SH
                    base = p["floor2"] if (i + j) % 2 else p["floor"]
                    v = (tex[y][x] - lo_) / ((hi_ - lo_) or 1)
                    k = tones[(i, j)] * (0.92 + 0.16 * v + (pixel._BAYER[y % 4][x % 4] / 15 - 0.5) * 0.05)
                    c = _shade(base, k)
                    if lx == 0 or ly == 0:
                        c = grout
                    elif lx == 1 or ly == 1:
                        c = _shade(c, 1.18)
                    elif lx == SWc - 1 or ly == SH - 1:
                        c = _shade(c, 0.74)
                    low.set_at((x, y), c)
            stains = pixel.tile_noise(lw, lw, rnd, (3, 6), (0.7, 0.3))
            lo_, hi_ = min(min(r) for r in stains), max(max(r) for r in stains)
            for y in range(lw):
                for x in range(lw):
                    v = (stains[y][x] - lo_) / ((hi_ - lo_) or 1)
                    if v < 0.15 and (x + y) % 2 == 0:
                        c = low.get_at((x, y))
                        low.set_at((x, y), (60, 70, 50) if not cat and (x * y) % 7 == 0 else _shade(c, 0.8))
            for _ in range(10):   # trincas
                x, y = rnd.randrange(lw), rnd.randrange(lw)
                for _k in range(rnd.randint(5, 12)):
                    put(x, y, grout)
                    x += rnd.choice((-1, 0, 1, 1))
                    y += rnd.choice((-1, 0, 1))
            if cat:
                for _ in range(26):   # cera e lascas de osso
                    x, y = rnd.randrange(lw), rnd.randrange(lw)
                    put(x, y, (226, 216, 192))
                    if rnd.random() < 0.5:
                        put(x + 1, y, (226, 216, 192))
                for _ in range(2):    # laje com caveira entalhada
                    cx, cy = rnd.randrange(lw // SW) * SW + SW // 2, rnd.randrange(lw // SH) * SH + SH // 2
                    for (dx, dy) in ((-2, -1), (2, -1), (-1, 2), (0, 2), (1, 2)):
                        put(cx + dx, cy + dy, grout)
                    for dx in range(-3, 4):
                        put(cx + dx, cy - 4, _shade(p["floor"], 0.7))
            else:
                for _ in range(40):   # palha e musgo nas juntas
                    x, y = rnd.randrange(lw), rnd.randrange(lw)
                    if rnd.random() < 0.5:
                        for k in range(3):
                            put(x + k, y, (156, 134, 72))
                    else:
                        put(x, y, (70, 96, 58))
        return pygame.transform.scale(low, (lw * pixel.PX, lw * pixel.PX))

    def _make_wall(self, rnd):
        """Faixa de parede (192x64, repete na horizontal) em pixel art."""
        import pixel
        p = self.pal
        w, h = 192 // pixel.PX, 64 // pixel.PX
        low = pygame.Surface((w, h))
        if self.did == "cavern":   # rocha em estratos com luz em cima, minério e cristais
            low = pixel.banded(pixel.tile_noise(w, w, rnd, (3, 6, 12)), pixel.shades(p["wall"], (0.7, 0.85, 1.0, 1.18, 1.35)),
                               0.12).subsurface((0, 0, w, h)).copy()
            for y in range(4, h, 7):   # estratos
                for x in range(w):
                    if (x + y * 3) % 9:
                        low.set_at((x, (y + int(2 * math.sin(x / 7))) % h), _shade(p["wall"], 0.6))
            for _ in range(14):
                low.set_at((rnd.randrange(w), rnd.randrange(h)), p["accent2"] if rnd.random() < 0.5 else p["accent"])
        elif self.did == "catacomb":   # ossuário: fileiras de caveiras e de ossos empilhados
            low.fill(p["wall2"])
            bone, bone_d, bone_l = p["accent"], _shade(p["accent"], 0.7), _shade(p["accent"], 1.05)
            hole = (30, 26, 24)
            for row in range(4):
                y0 = row * 8
                if row % 2 == 0:   # caveiras de gato
                    for x0 in range(0 if row % 4 == 0 else 6, w, 12):
                        pygame.draw.rect(low, bone_d, (x0 + 1, y0 + 2, 9, 6))
                        pygame.draw.rect(low, bone, (x0 + 2, y0 + 1, 7, 6))
                        low.set_at((x0 + 2, y0), bone)          # orelhinhas
                        low.set_at((x0 + 8, y0), bone)
                        low.set_at((x0 + 4, y0 + 3), hole)
                        low.set_at((x0 + 7, y0 + 3), hole)
                        low.set_at((x0 + 5, y0 + 5), hole)
                        low.set_at((x0 + 3, y0 + 1), bone_l)
                else:              # ossos deitados
                    for x0 in range(rnd.randrange(4), w, 9):
                        pygame.draw.line(low, bone_d, (x0, y0 + 4), (x0 + 7, y0 + 4))
                        pygame.draw.line(low, bone, (x0, y0 + 3), (x0 + 7, y0 + 3))
                        for e in (x0, x0 + 7):
                            low.set_at((e, y0 + 2), bone)
                            low.set_at((e, y0 + 5), bone_d)
        else:   # prisão: blocos grandes com bisel, rejunte, musgo e escorrido de umidade
            low.fill(_shade(p["wall2"], 0.9))
            for row in range(4):
                off = 0 if row % 2 else 8
                for col in range(-1, w // 16 + 1):
                    x0, y0 = col * 16 + off, row * 8
                    base = _shade(p["wall"], rnd.uniform(0.85, 1.15))
                    pygame.draw.rect(low, base, (x0 + 1, y0 + 1, 14, 6))
                    pygame.draw.line(low, _shade(base, 1.25), (x0 + 1, y0 + 1), (x0 + 14, y0 + 1))
                    pygame.draw.line(low, _shade(base, 0.7), (x0 + 1, y0 + 6), (x0 + 14, y0 + 6))
            for _ in range(5):   # escorrido de umidade e musgo
                x = rnd.randrange(w)
                for y in range(rnd.randint(6, h)):
                    c = low.get_at((x, y))
                    low.set_at((x, y), _shade(c, 0.8))
                low.set_at((x, 0), (70, 100, 60))
        pygame.draw.line(low, _shade(p["edge"], 1.1), (0, h - 1), (w, h - 1))   # rodapé
        pygame.draw.line(low, _shade(p["wall2"], 0.7), (0, h - 2), (w, h - 2))
        return pygame.transform.scale(low, (w * pixel.PX, h * pixel.PX))

    # ------------------------------------------------------------------ objetos das paredes e do chão
    def _sprite(self, key, build):
        cache = self.__dict__.setdefault("_sprites", {})
        if key not in cache:
            import pixel
            cache[key] = pixel.pixel_sprite(build())
        return cache[key]

    def _wall_sprite(self, kind):
        """Objeto preso na parede (desenhado de frente, centro = meio da faixa da parede)."""
        p = self.pal
        S = lambda w, h: pygame.Surface((w, h), pygame.SRCALPHA)

        def build():
            if self.did == "cavern":
                if kind == 0:   # aglomerado de cristais
                    s = S(64, 64)
                    col = p["accent"]
                    for dx, hh, ang, w in ((-10, 22, -0.4, 5), (8, 18, 0.35, 5), (0, 32, 0.0, 6), (-4, 12, -0.8, 4)):
                        bx, by = 32 + dx, 56
                        tx, ty = bx + math.sin(ang) * hh, by - math.cos(ang) * hh
                        nx = math.cos(ang) * w
                        pygame.draw.polygon(s, _shade(col, 1.25), [(bx - nx, by), (tx, ty), (bx, by)])
                        pygame.draw.polygon(s, _shade(col, 0.6), [(bx, by), (tx, ty), (bx + nx, by)])
                    pygame.draw.polygon(s, _shade(p["wall"], 1.2), [(12, 60), (18, 52), (46, 52), (52, 60)])
                    return s
                if kind == 1:   # estalactites
                    s = S(64, 64)
                    for dx, hh, w in ((-12, 26, 7), (2, 40, 9), (14, 20, 6)):
                        col = _shade(p["edge"], 1.0 + dx / 60)
                        pts = [(32 + dx - w, 0), (32 + dx, hh), (32 + dx + w, 0)]
                        pygame.draw.polygon(s, col, pts)
                        pygame.draw.polygon(s, _shade(col, 1.25), [(32 + dx - w, 0), (32 + dx, hh), (32 + dx - 2, 0)])
                        pygame.draw.circle(s, (150, 190, 220), (32 + dx, hh + 4), 1)
                    return s
                s = S(64, 48)   # veio de ouro
                pygame.draw.polygon(s, _shade(p["wall"], 1.3), [(6, 40), (16, 14), (40, 8), (58, 30), (50, 44)])
                pygame.draw.polygon(s, _shade(p["wall"], 1.6), [(16, 14), (40, 8), (34, 18)])
                for (x, y) in ((22, 22), (30, 28), (38, 20), (44, 32), (26, 34)):
                    pygame.draw.polygon(s, p["accent2"], [(x - 3, y + 2), (x - 1, y - 2), (x + 3, y - 1), (x + 3, y + 2)])
                    s.set_at((x, y - 1), (255, 245, 180))
                return s
            if self.did == "catacomb":
                bone = p["accent"]
                if kind == 0:   # nicho em arco com caveiras empilhadas
                    s = S(56, 56)
                    pygame.draw.rect(s, _shade(p["wall"], 1.3), (6, 8, 44, 46), border_top_left_radius=22,
                                     border_top_right_radius=22)
                    pygame.draw.rect(s, (22, 18, 18), (11, 13, 34, 38), border_top_left_radius=17,
                                     border_top_right_radius=17)
                    for (x, y) in ((20, 42), (36, 42), (28, 30)):
                        for sx in (-1, 1):
                            pygame.draw.polygon(s, bone, [(x + 3 * sx, y - 4), (x + 6 * sx, y - 9), (x + 7 * sx, y - 2)])
                        pygame.draw.circle(s, bone, (x, y), 6)
                        pygame.draw.circle(s, (30, 26, 24), (x - 2, y), 1)
                        pygame.draw.circle(s, (30, 26, 24), (x + 2, y), 1)
                    return s
                if kind == 1:   # velas em cima de um crânio
                    s = S(48, 48)
                    pygame.draw.circle(s, bone, (24, 40), 7)
                    pygame.draw.circle(s, (30, 26, 24), (21, 40), 2)
                    pygame.draw.circle(s, (30, 26, 24), (27, 40), 2)
                    for x, hh in ((18, 10), (24, 15), (30, 8)):
                        pygame.draw.rect(s, (236, 228, 208), (x - 2, 33 - hh, 4, hh))
                        pygame.draw.line(s, (250, 246, 236), (x - 2, 33 - hh), (x - 2, 31), 1)
                    return s
                s = S(72, 52)   # túmulo na parede com corpo enrolado e teia
                pygame.draw.rect(s, _shade(p["wall"], 1.3), (4, 10, 64, 38), border_top_left_radius=12,
                                 border_top_right_radius=12)
                pygame.draw.rect(s, (22, 18, 18), (9, 15, 54, 30), border_top_left_radius=9, border_top_right_radius=9)
                pygame.draw.ellipse(s, (170, 156, 128), (14, 28, 44, 12))
                for x in range(20, 54, 7):
                    pygame.draw.line(s, (130, 118, 96), (x, 29), (x + 3, 39), 1)
                for k in range(4):
                    pygame.draw.line(s, (210, 210, 220, 160), (9, 15), (9 + k * 6, 15 + (3 - k) * 5), 1)
                return s
            if kind == 0:   # tocha: suporte de ferro e cabo de madeira (a chama é animada)
                s = S(32, 48)
                pygame.draw.rect(s, (60, 58, 64), (11, 30, 10, 6))
                pygame.draw.line(s, (90, 88, 96), (11, 30), (20, 30), 1)
                pygame.draw.polygon(s, (100, 68, 42), [(13, 34), (19, 34), (17, 18), (15, 18)])
                pygame.draw.rect(s, (60, 58, 64), (13, 16, 6, 4))
                return s
            if kind == 1:   # corrente com algemas
                s = S(32, 56)
                for k in range(6):
                    y = 4 + k * 7
                    pygame.draw.ellipse(s, p["accent2"], (12 if k % 2 else 13, y, 7 if k % 2 else 5, 8), 2)
                pygame.draw.circle(s, p["accent2"], (16, 50), 5, 2)
                pygame.draw.circle(s, _shade(p["accent2"], 1.3), (14, 48), 1)
                return s
            s = S(64, 60)   # porta de cela em arco com grades
            pygame.draw.rect(s, _shade(p["wall"], 1.35), (6, 6, 52, 52), border_top_left_radius=24,
                             border_top_right_radius=24)
            pygame.draw.rect(s, (14, 14, 18), (12, 12, 40, 46), border_top_left_radius=19, border_top_right_radius=19)
            for x in range(16, 50, 7):
                pygame.draw.line(s, p["accent2"], (x, 14), (x, 57), 2)
                pygame.draw.line(s, _shade(p["accent2"], 1.3), (x - 1, 14), (x - 1, 57), 1)
            pygame.draw.line(s, p["accent2"], (12, 30), (52, 30), 2)
            return s

        return self._sprite(("wall", kind), build)

    def _floor_sprite(self, kind):
        p = self.pal
        S = lambda w, h: pygame.Surface((w, h), pygame.SRCALPHA)

        def build():
            if self.did == "cavern":
                if kind == 0:   # pedrinhas
                    s = S(30, 18)
                    for (x, y) in ((4, 10), (12, 7), (20, 10)):
                        c = _shade(p["edge"], 0.9)
                        pygame.draw.polygon(s, c, [(x, y + 4), (x + 1, y), (x + 5, y - 1), (x + 6, y + 4)])
                        pygame.draw.line(s, _shade(c, 1.3), (x + 1, y), (x + 5, y - 1), 1)
                    return s
                if kind == 1:   # cristalzinho
                    s = S(22, 22)
                    for (x, hh, ang) in ((10, 15, 0.0), (6, 8, -0.5), (15, 7, 0.6)):
                        tx, ty = x + math.sin(ang) * hh, 20 - math.cos(ang) * hh
                        pygame.draw.polygon(s, _shade(p["accent"], 1.2), [(x - 2, 20), (tx, ty), (x, 20)])
                        pygame.draw.polygon(s, _shade(p["accent"], 0.6), [(x, 20), (tx, ty), (x + 2, 20)])
                    return s
                s = S(26, 24)   # cogumelos que brilham
                glow = S(26, 24)
                pygame.draw.circle(glow, (*p["accent"], 45), (13, 12), 11)
                s.blit(glow, (0, 0))
                for x, y, r in ((8, 13, 4), (16, 9, 6)):
                    pygame.draw.line(s, (220, 215, 200), (x, y), (x, y + 7), 2)
                    pygame.draw.circle(s, p["accent"], (x, y), r, draw_bottom_left=False, draw_bottom_right=False)
                return s
            if self.did == "catacomb":
                bone = p["accent"]
                if kind == 0:   # ossos e caveirinha
                    s = S(32, 18)
                    pygame.draw.line(s, bone, (3, 12), (17, 10), 3)
                    for e in ((3, 12), (17, 10)):
                        pygame.draw.circle(s, bone, e, 2)
                    for sx in (-1, 1):
                        pygame.draw.polygon(s, bone, [(24 + 2 * sx, 5), (24 + 5 * sx, 0), (24 + 5 * sx, 6)])
                    pygame.draw.circle(s, bone, (24, 9), 5)
                    pygame.draw.circle(s, (30, 26, 24), (22, 9), 1)
                    pygame.draw.circle(s, (30, 26, 24), (26, 9), 1)
                    return s
                if kind == 1:   # velas no chão
                    s = S(28, 26)
                    glow = S(28, 26)
                    pygame.draw.circle(glow, (*p["accent2"], 45), (14, 10), 12)
                    s.blit(glow, (0, 0))
                    pygame.draw.ellipse(s, (226, 218, 196), (3, 19, 22, 6))
                    for x, hh in ((8, 8), (15, 13), (21, 6)):
                        pygame.draw.rect(s, (236, 230, 212), (x - 2, 22 - hh, 4, hh))
                        pygame.draw.ellipse(s, p["accent2"], (x - 2, 16 - hh, 4, 7))
                    return s
                s = S(28, 16)   # pó de ossos
                for k in range(6):
                    pygame.draw.circle(s, _shade(bone, 0.8), (4 + k * 4, 8 + (k % 2) * 3), 2)
                return s
            if kind == 0:   # monte de palha
                s = S(32, 18)
                for k in range(9):
                    x = 4 + k * 3
                    pygame.draw.line(s, (160, 138, 74) if k % 2 else (130, 110, 60), (x, 15), (x + 4 - k % 3 * 3, 6), 1)
                return s
            if kind == 1:   # balde amassado
                s = S(22, 22)
                pygame.draw.polygon(s, (110, 110, 120), [(4, 6), (18, 6), (16, 19), (6, 19)])
                pygame.draw.ellipse(s, (60, 60, 68), (4, 3, 14, 6))
                pygame.draw.line(s, (150, 150, 160), (5, 7), (6, 18), 1)
                pygame.draw.arc(s, (90, 90, 100), (4, -2, 14, 12), 0, math.pi, 1)
                return s
            s = S(30, 16)   # mancha escura e corrente solta
            pygame.draw.ellipse(s, (60, 30, 30, 140), (2, 4, 18, 9))
            for k in range(4):
                pygame.draw.ellipse(s, p["accent2"], (12 + k * 4, 6 + (k % 2), 5, 4), 1)
            return s

        return self._sprite(("floor", kind), build)

    # interface igual à do cenário da floresta
    def collide(self, u):
        u.pos.y = max(-HALF_H + u.r, min(HALF_H - u.r, u.pos.y))
        u.pos.x = max(START_X - 180, min(LENGTH + 260, u.pos.x))

    def clamp(self, e):
        e.pos.y = max(-HALF_H + e.r * 0.6, min(HALF_H - e.r * 0.6, e.pos.y))
        e.pos.x = max(START_X - 200, min(LENGTH + 300, e.pos.x))

    def free_pos(self, pos, margin=30):
        p = V(pos)
        p.y = max(-HALF_H + margin, min(HALF_H - margin, p.y))
        p.x = max(START_X - 150, min(LENGTH + 240, p.x))
        return p

    def draw_ground(self, s, cam, W, H):
        s.fill(self.pal["wall2"])
        top = int(-HALF_H - cam.y)
        bot = int(HALF_H - cam.y)
        prev = s.get_clip()
        s.set_clip(pygame.Rect(0, top, W, bot - top))
        T = self.tile.get_width()
        ox, oy = int(-cam.x % T), int(-cam.y % T)
        for x in range(ox - T, W, T):
            for y in range(oy - T, H, T):
                s.blit(self.tile, (x, y))
        shade = pygame.Surface((W, 18), pygame.SRCALPHA)   # sombra das paredes no chão
        for k in range(9):
            pygame.draw.rect(shade, (0, 0, 0, 90 - k * 10), (0, k * 2, W, 2))
        s.blit(shade, (0, top))
        s.blit(pygame.transform.flip(shade, False, True), (0, bot - 18))
        s.set_clip(prev)
        for p, kind in self.floor_decor:   # objetos do chão
            sp = p - cam
            if -30 < sp.x < W + 30 and top < sp.y < bot:
                img = self._floor_sprite(kind)
                s.blit(img, (sp.x - img.get_width() / 2, sp.y - img.get_height() / 2))
        self._draw_walls(s, cam, W, top, bot)
        gx = LENGTH - cam.x   # portal da sala do chefão: arco de pedra com runas acesas no chão
        if -200 < gx < W + 200:
            t = pygame.time.get_ticks() / 1000
            glow = 0.6 + 0.4 * math.sin(t * 3)
            col = tuple(int(c * glow) for c in self.pal["accent"])
            for y in range(top + 6, bot - 6, 12):
                pygame.draw.rect(s, col, (gx - 3, y, 6, 6))
            for y0 in (top - 64, bot):
                pygame.draw.rect(s, _shade(self.pal["edge"], 1.1), (gx - 18, y0, 36, 64))
                pygame.draw.rect(s, _shade(self.pal["edge"], 1.4), (gx - 18, y0, 6, 64))
                pygame.draw.rect(s, _shade(self.pal["wall2"], 0.8), (gx - 18, y0, 36, 64), 2)
                pygame.draw.circle(s, col, (gx, y0 + 32), 5)
        sx = START_X - 200 - cam.x   # parede do começo
        if -60 < sx < W + 60:
            pygame.draw.rect(s, self.pal["wall"], (sx - 40, top, 40, bot - top))
            for y in range(top, bot, 16):
                pygame.draw.line(s, self.pal["wall2"], (sx - 40, y), (sx, y), 2)

    def _draw_walls(self, s, cam, W, top, bot):
        p = self.pal
        wh = self.wall_tile.get_height()
        tw = self.wall_tile.get_width()
        ox = int(-cam.x % tw)
        for x in range(ox - tw, W, tw):
            s.blit(self.wall_tile, (x, top - wh))
            s.blit(self.wall_tile, (x, bot))
        pygame.draw.line(s, p["edge"], (0, top), (W, top), 2)
        pygame.draw.line(s, p["edge"], (0, bot), (W, bot), 2)
        t = pygame.time.get_ticks() / 1000
        for x, side, kind in self.decor:
            sx = x - cam.x
            if not -60 < sx < W + 60:
                continue
            img = self._wall_sprite(kind)
            if self.did == "cavern" and kind == 1:   # estalactites caem do teto / estalagmites sobem do chão
                if side < 0:
                    s.blit(img, (sx - img.get_width() / 2, top - 4))
                else:
                    s.blit(pygame.transform.flip(img, False, True), (sx - img.get_width() / 2, bot - img.get_height() + 4))
                continue
            cy = top - wh / 2 if side < 0 else bot + wh / 2
            s.blit(img, (sx - img.get_width() / 2, cy - img.get_height() / 2))
            if self.did == "dungeon" and kind == 0:   # chama da tocha
                fl = math.sin(t * 9 + x) * 2
                fx, fy = sx, cy - img.get_height() / 2 + 14
                glow = pygame.Surface((90, 90), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*p["accent"], 40), (45, 45), 44)
                s.blit(glow, (fx - 45, fy - 45))
                pygame.draw.polygon(s, p["accent"], [(fx - 6, fy + 4), (fx + fl, fy - 14), (fx + 6, fy + 4)])
                pygame.draw.polygon(s, (255, 230, 140), [(fx - 3, fy + 3), (fx + fl * 0.5, fy - 6), (fx + 3, fy + 3)])
            elif self.did == "catacomb" and kind == 1:   # chamas das velas
                base_y = cy - img.get_height() / 2
                glow = pygame.Surface((70, 70), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*p["accent2"], 35), (35, 35), 34)
                s.blit(glow, (sx - 35, base_y - 10))
                for dx, hh in ((-6, 10), (0, 15), (6, 8)):
                    f = 3 + math.sin(t * 9 + x + dx) * 1
                    pygame.draw.ellipse(s, p["accent2"], (sx + dx - 2, base_y + 33 - hh - 7 - f, 4, 4 + f))
            elif self.did == "dungeon" and kind == 2:   # olhos na escuridão da cela (piscam)
                if int(t * 0.7 + x) % 5 != 0:
                    ey = cy + 4
                    for ex in (-5, 5):
                        pygame.draw.rect(s, (255, 200, 80), (sx + ex - 1, ey, 3, 2))

    def draw_trees(self, s, cam, W, H):
        pass


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def preview(did, w, h):
    """Miniatura do corredor para a tela de seleção."""
    sc = DungeonScenery(did, seed=7)
    big = pygame.Surface((1280, 720))
    sc.draw_ground(big, V(400, -360), 1280, 720)
    # pixel art: reduzir exatamente pela metade mantém 1 amostra por bloco 2x2 (nítido); depois recorta o centro
    half = pygame.transform.scale(big, (640, 360))
    x0 = max(0, (640 - w) // 2)
    y0 = max(0, min(360 - h, 40))
    if w <= 640 and h <= 360:
        return half.subsurface((x0, y0, w, h)).copy()
    return pygame.transform.scale(half, (w, h))
