"""Animações em pixel art das habilidades (heróis, elites e monstros).

Tudo é desenhado em código, em baixa resolução (1 pixel = 2 pixels de tela, como o resto do mundo), e guardado
em cache. Cada habilidade ganha um "visual" escolhido pelo nome, pelo elemento e pela arma da classe:
flechas, kunai, machados, bolas de fogo, notas musicais, pilares de luz, meteoros, armadilhas...

Uso:
    look = skill_fx.look_for(spec)               # visual de uma habilidade
    skill_fx.projectile_sprite(look, r, vel, t)  # sprite do projétil (já girado)
    skill_fx.impact(look, radius)                # quadros de uma explosão / impacto
    skill_fx.swoosh(look, radius, arc, ang)      # quadros de um golpe em arco
    skill_fx.thrust(look, length, width, ang)    # quadros de uma estocada / raio
    skill_fx.cone(look, radius, arc, ang)        # quadros de um sopro em cone
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

import pixel

PX = 2
OUT = pixel.OUTLINE

# paletas (escuro, médio, claro) por elemento
PAL = {
    "fire": ((150, 40, 20), (240, 110, 40), (255, 215, 100)),
    "ice": ((60, 110, 170), (140, 200, 250), (235, 250, 255)),
    "lightning": ((150, 120, 30), (250, 220, 70), (255, 255, 210)),
    "water": ((30, 80, 160), (70, 150, 230), (195, 230, 255)),
    "wind": ((60, 140, 90), (140, 220, 160), (230, 255, 235)),
    "earth": ((90, 60, 35), (160, 115, 70), (215, 180, 120)),
    "poison": ((60, 110, 30), (130, 200, 60), (215, 250, 140)),
    "holy": ((170, 130, 40), (250, 215, 100), (255, 250, 225)),
    "arcane": ((90, 50, 160), (170, 110, 240), (235, 210, 255)),
    "gravity": ((50, 30, 80), (120, 70, 170), (200, 160, 240)),
    "time": ((70, 90, 130), (150, 180, 215), (235, 240, 225)),
    "sound": ((160, 70, 130), (240, 140, 200), (255, 225, 240)),
    "smoke": ((70, 70, 80), (140, 140, 150), (215, 215, 220)),
    "dark": ((40, 20, 60), (110, 55, 150), (205, 150, 245)),
    "blood": ((110, 20, 25), (200, 40, 45), (255, 140, 130)),
    None: ((90, 95, 110), (185, 190, 205), (248, 248, 252)),
}
WOOD = ((80, 50, 30), (130, 85, 50), (175, 125, 80))
STEEL = PAL[None]

_CACHE = {}


def _cache(key, fn):
    v = _CACHE.get(key)
    if v is None:
        if len(_CACHE) > 2500:
            _CACHE.clear()
        v = _CACHE[key] = fn()
    return v


def pal(el):
    return PAL.get(el, PAL[None])


def _rgba(c, a):
    return (int(c[0]), int(c[1]), int(c[2]), max(0, min(255, int(a))))


def _bake(low, outline=None, light=False):
    return pixel.pixelize(low, PX, outline=outline, light=light)


def _rot(pts, ang, c):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]


# ---------------------------------------------------------------------------
# Escolha do visual de cada habilidade
# ---------------------------------------------------------------------------
_PROJ_WORDS = [
    (("shuriken",), "shuriken"), (("kunai",), "kunai"),
    (("bone",), "bone"), (("bile",), "bile"), (("bomb",), "bomb"),
    (("axe",), "axe"), (("javelin", "spear", "lance"), "javelin"), (("sword",), "sword"),
    (("knife", "knives", "dagger", "viper", "blades"), "dagger"),
    (("note", "melodic", "harp", "echo", "song"), "note"),
    (("arrow", "shot", "snipe", "volley", "headshot", "deadeye", "mark", "multishot", "bow"), "arrow"),
    (("stone", "rock", "toss"), "stone"),
    (("ki ", "ki wave", "aura blast", "wave", "fist"), "ki"),
    (("ruby",), "gem"),
]
_IMPACT_WORDS = [
    (("meteor", "comet", "megaflare", "flare"), "meteor"),
    (("hail", "arrow rain", "arrow storm", "javelin rain", "volley of"), "rain"),
    (("trap", "snare"), "trap"),
    (("jump", "leap", "dive", "vault", "landslide", "slam", "stomp", "pound", "quake", "earthquake",
      "earthshaker", "earthbreaker", "titan", "doton", "landing"), "quake"),
    (("ambush", "shadow strike", "death mark", "backstab", "mug", "mutilate", "garrote", "kidney",
      "rend", "execute", "crosscut", "cleaver", "chop", "skull", "rampage", "executioner", "furious",
      "splitter", "heavy chop"), "cut"),
    (("punch", "jab", "uppercut", "fist", "palm", "blow", "counter", "knockout", "snap", "tiger", "pressure",
      "demolish", "heaven", "bash", "pommel", "overpower", "liver", "shockwave", "stunning"), "fist"),
    (("challenge", "roar", "provoke", "shout", "cry"), "taunt"),
    (("judgment", "smite", "holy", "light", "pillar", "divine", "pulse", "broil", "condemn", "holyja"), "pillar"),
    (("smoke",), "smoke"),
    (("old", "stop", "time"), "clock"),
    (("gravity", "graviga"), "gravity"),
]
_EL_PROJ = {"fire": "fireball", "ice": "ice", "water": "water", "wind": "wind", "arcane": "arcane",
            "holy": "holy", "poison": "poison", "lightning": "bolt", "sound": "note", "earth": "stone",
            "gravity": "dark", "time": "arcane", "smoke": "stone", "dark": "dark"}
_EL_IMPACT = {"fire": "fire", "ice": "ice", "lightning": "lightning", "water": "water", "wind": "wind",
              "earth": "quake", "poison": "poison", "holy": "pillar", "arcane": "rune", "gravity": "gravity",
              "time": "clock", "sound": "sound", "smoke": "smoke", "dark": "gravity"}


def _match(low, table):
    for words, key in table:
        for w in words:
            if w in low:
                return key
    return None


def look_for(sp):
    """Visual (dict) de uma especificação de habilidade."""
    if not sp:
        return dict(proj="orb", impact="hit", el=None, cut=False)
    key = (sp.get("name"), sp.get("cid"), sp.get("kind"), sp.get("element"), tuple(sp.get("cycle") or ()))
    return _cache(("look",) + key, lambda: _look(sp))


def _look(sp):
    name = (sp.get("name") or "").lower()
    el = sp.get("element") or ((sp.get("cycle") or [None])[0])
    phys = sp.get("dmgtype") == "phys" and not el
    proj = _match(name + " ", _PROJ_WORDS)
    if proj in ("arrow", None) and el in _EL_PROJ and proj != "arrow":
        proj = _EL_PROJ[el]
    if proj is None:
        proj = "stone" if phys else _EL_PROJ.get(el, "arcane")
    imp = _match(name, _IMPACT_WORDS)
    if imp == "pillar" and el not in (None, "holy"):
        imp = None
    if imp is None or (imp in ("cut", "fist") and el and sp.get("kind") == "strike" and sp.get("target") != "nearest"):
        imp = _EL_IMPACT.get(el) or ("hit" if not phys else "fist")
    if sp.get("taunt"):
        imp = "taunt"
    weapon_cut = any(w in name for w in ("blade", "slash", "cleave", "edge", "swing", "sweep", "spin", "cut",
                                         "riposte", "whirl", "fan of", "flurry", "decimate", "storm"))
    return dict(proj=proj, impact=imp, el=el, cycle=tuple(sp.get("cycle") or ()), cut=weapon_cut,
                fists=any(w in name for w in ("punch", "kick", "palm", "fist", "jab", "chi", "phoenix")))


def el_of(look, n=0):
    cyc = look.get("cycle") or ()
    return cyc[n % len(cyc)] if cyc else look.get("el")


# ---------------------------------------------------------------------------
# Projéteis
# ---------------------------------------------------------------------------
SPIN = {"shuriken", "axe", "sword", "bone", "stone", "bomb"}


def projectile_sprite(look, r, vel, t, el=None, hostile=False):
    kind = look.get("proj", "orb")
    el = el if el is not None else look.get("el")
    if kind in SPIN:
        ang = (t * (900 if kind == "shuriken" else 600)) % 360
    else:
        ang = math.degrees(math.atan2(vel.y, vel.x)) if vel.length_squared() > 1e-6 else 0.0
    step = 15 if kind in SPIN else 11.25
    abucket = int(round(ang / step)) % int(360 / step)
    frame = int(t * 12) % 3
    sz = max(3, min(14, int(round(r))))
    return _cache(("proj", kind, el, sz, abucket, frame, hostile),
                  lambda: _proj(kind, el, sz, math.radians(abucket * step), frame, hostile))


def _proj(kind, el, r, ang, frame, hostile):
    L = max(4, int(r * 1.2))                # meio comprimento (flechas, adagas...) em pixels baixos
    n = L * 2 + 8
    r = max(2.0, r / PX * 1.25)             # raio dos orbes/pedras em pixels baixos (~ raio de acerto)
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    d, m, li = pal(el)
    P = lambda pts: _rot(pts, ang, c)
    outline = OUT
    if kind == "arrow":
        tip = pal(el)[1] if el else (215, 220, 230)
        pygame.draw.line(low, WOOD[1], P([(-L, 0)])[0], P([(L - 3, 0)])[0], 1)
        pygame.draw.polygon(low, tip, P([(L, 0), (L - 4, -2), (L - 4, 2)]))
        pygame.draw.polygon(low, (230, 70, 60) if not el else li, P([(-L, 0), (-L + 4, 0), (-L + 2, -2), (-L - 1, -2)]))
        pygame.draw.polygon(low, (240, 235, 225) if not el else m, P([(-L, 0), (-L + 4, 0), (-L + 2, 2), (-L - 1, 2)]))
        if el:
            for k in range(3):
                q = P([(-L - 2 - k * 2 - frame, (k % 2) * 2 - 1)])[0]
                low.set_at((int(q[0]), int(q[1])), _rgba(li if k == 0 else m, 255 - k * 60))
    elif kind == "kunai":
        pygame.draw.polygon(low, (80, 85, 100), P([(L, 0), (0, -2), (-2, 0), (0, 2)]))
        pygame.draw.line(low, (200, 205, 215), P([(L - 1, 0)])[0], P([(0, 0)])[0], 1)
        pygame.draw.line(low, (60, 40, 30), P([(-2, 0)])[0], P([(-L + 3, 0)])[0], 2)
        pygame.draw.circle(low, (90, 90, 100), P([(-L + 2, 0)])[0], 2, 1)
    elif kind == "shuriken":
        R = max(3, L * 0.6)
        pts = []
        for k in range(8):
            rr = R if k % 2 == 0 else R * 0.35
            a = k * math.pi / 4
            pts.append((math.cos(a) * rr, math.sin(a) * rr))
        pygame.draw.polygon(low, (150, 155, 170), P(pts))
        pygame.draw.circle(low, (50, 50, 60), c, max(1, R * 0.22))
    elif kind == "dagger":
        bl = (200, 205, 220) if el is None else m
        pygame.draw.polygon(low, bl, P([(L, 0), (0, -2), (0, 2)]))
        pygame.draw.line(low, (90, 70, 40), P([(0, -3)])[0], P([(0, 3)])[0], 1)
        pygame.draw.line(low, (110, 60, 40), P([(-1, 0)])[0], P([(-L * 0.6, 0)])[0], 2)
    elif kind == "axe":
        R = L * 0.8
        pygame.draw.line(low, WOOD[1], P([(-R, 0)])[0], P([(R, 0)])[0], 2)
        pygame.draw.polygon(low, (190, 195, 205), P([(R * 0.4, 0), (R * 0.9, -R * 0.7), (R * 1.05, 0),
                                                     (R * 0.9, R * 0.15)]))
        pygame.draw.polygon(low, (150, 155, 170), P([(-R * 0.3, 0), (-R * 0.7, -R * 0.55), (-R * 0.85, 0)]))
    elif kind == "javelin":
        tipc = m if el else (200, 205, 215)
        pygame.draw.line(low, WOOD[2] if not el else d, P([(-L - 2, 0)])[0], P([(L - 4, 0)])[0], 1)
        pygame.draw.polygon(low, tipc, P([(L + 1, 0), (L - 4, -2), (L - 6, 0), (L - 4, 2)]))
        if el:
            for k in range(4):
                q = P([(-L + k * 3 - frame, (k % 2) * 2 - 1)])[0]
                low.set_at((int(q[0]), int(q[1])), _rgba(li, 220))
    elif kind == "sword":
        R = L * 0.9
        pygame.draw.polygon(low, (215, 220, 230), P([(R, 0), (-R * 0.2, -1.5), (-R * 0.2, 1.5)]))
        pygame.draw.line(low, (180, 140, 60), P([(-R * 0.2, -3)])[0], P([(-R * 0.2, 3)])[0], 1)
        pygame.draw.line(low, (90, 60, 40), P([(-R * 0.25, 0)])[0], P([(-R * 0.6, 0)])[0], 2)
    elif kind == "bone":
        R = L * 0.75
        pygame.draw.line(low, (235, 230, 210), P([(-R, 0)])[0], P([(R, 0)])[0], 2)
        for sx in (-R, R):
            for sy in (-1.3, 1.3):
                pygame.draw.circle(low, (240, 236, 220), P([(sx, sy)])[0], 1.6)
    elif kind == "bile":
        pygame.draw.circle(low, (110, 150, 50), c, max(2, r * 0.7))
        pygame.draw.circle(low, (170, 210, 80), (c[0] - 1, c[1] - 1), max(1, r * 0.35))
        for k in range(3):
            q = P([(-r - 2 - k * 2, (k - 1) * 1.5)])[0]
            low.set_at((int(q[0]), int(q[1])), (120, 160, 60, 200 - k * 50))
    elif kind == "bomb":
        rr = max(2.5, r * 0.75)
        pygame.draw.circle(low, (45, 45, 55), c, rr)
        pygame.draw.circle(low, (110, 110, 125), (c[0] - rr * 0.35, c[1] - rr * 0.35), max(1, rr * 0.3))
        top = (c[0] + rr * 0.5, c[1] - rr * 0.9)
        pygame.draw.line(low, (150, 120, 80), top, (top[0] + 2, top[1] - 2), 1)
        sc = [(255, 230, 120), (255, 150, 60), (255, 255, 220)][frame]
        pygame.draw.circle(low, sc, (top[0] + 2.5, top[1] - 2.5), 1.2 + (frame == 2))
    elif kind == "note":
        col = m if el else (240, 140, 200)
        x0 = c[0] - 1 + (frame - 1)
        pygame.draw.circle(low, col, (x0 - 1, c[1] + 2), max(2, r * 0.45))
        pygame.draw.line(low, col, (x0 + r * 0.35, c[1] + 2), (x0 + r * 0.35, c[1] - r * 0.9), 1)
        pygame.draw.line(low, col, (x0 + r * 0.35, c[1] - r * 0.9), (x0 + r * 0.9, c[1] - r * 0.55), 2)
        outline = (60, 20, 50)
    elif kind == "stone":
        rr = max(2, r * 0.7)
        pts = [(math.cos(a) * rr * (0.8 + 0.25 * ((k * 7) % 3) / 2), math.sin(a) * rr * (0.8 + 0.25 * ((k * 5) % 3) / 2))
               for k, a in enumerate([i * math.tau / 6 for i in range(6)])]
        base = pal(el)[1] if el in ("earth", "smoke") else (150, 140, 125)
        pygame.draw.polygon(low, base, P(pts))
        pygame.draw.circle(low, (205, 195, 175), P([(-rr * 0.3, -rr * 0.3)])[0], max(1, rr * 0.3))
    elif kind == "gem":
        pygame.draw.polygon(low, (230, 50, 70), P([(r, 0), (0, -r * 0.7), (-r * 0.6, 0), (0, r * 0.7)]))
        pygame.draw.line(low, (255, 180, 190), P([(r * 0.5, 0)])[0], P([(-r * 0.2, 0)])[0], 1)
        _trail(low, P, r, (255, 120, 140), frame)
        outline = (60, 10, 20)
    elif kind == "ki":
        col = li
        for k, rr in enumerate((r * 1.2, r * 0.9)):
            pts = [(math.cos(a) * rr, math.sin(a) * rr * 1.4) for a in [(-70 + i * 14) * math.pi / 180 for i in range(11)]]
            pygame.draw.lines(low, (m if k == 0 else col), False, P(pts), 2)
        outline = None
    else:   # orbes de energia: fogo, gelo, água, vento, arcano, sagrado, veneno, raio, sombrio, orbe
        outline = None
        _orb(low, c, P, kind, el, r, frame)
    if hostile:   # projéteis inimigos: brilho vermelho embaixo para dar para ver que machucam
        g = pygame.Surface(low.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(g, (230, 40, 40, 110), c, max(3, r * 0.9) + 1)
        g.blit(low, (0, 0))
        low = g
    return _bake(low, outline=outline, light=outline is not None)


def _trail(low, P, r, col, frame):
    for k in range(4):
        q = P([(-r - 1 - k * 2 - frame, ((k + frame) % 3) - 1)])[0]
        low.set_at((int(q[0]), int(q[1])), _rgba(col, 230 - k * 50))


def _orb(low, c, P, kind, el, r, frame):
    d, m, li = pal(el if el else {"fireball": "fire", "ice": "ice", "water": "water", "wind": "wind",
                                  "arcane": "arcane", "holy": "holy", "poison": "poison", "bolt": "lightning",
                                  "dark": "dark"}.get(kind))
    rr = max(2, r * 0.75)
    if kind == "fireball":
        for k in range(5):   # cauda de chamas
            q = P([(-rr - k * 1.6, math.sin(k * 1.7 + frame) * 1.5)])[0]
            pygame.draw.circle(low, _rgba(m if k < 2 else d, 230 - k * 40), q, max(1, rr * (1 - k * 0.17)))
        pygame.draw.circle(low, m, c, rr)
        pygame.draw.circle(low, li, P([(rr * 0.2, 0)])[0], max(1, rr * 0.55))
    elif kind == "ice":
        pygame.draw.polygon(low, m, P([(rr * 1.7, 0), (0, -rr * 0.7), (-rr * 1.2, 0), (0, rr * 0.7)]))
        pygame.draw.line(low, li, P([(rr * 1.2, 0)])[0], P([(-rr * 0.6, 0)])[0], 1)
        _trail(low, P, rr, li, frame)
    elif kind == "water":
        pygame.draw.polygon(low, m, P([(rr * 1.3, 0), (0, -rr), (-rr * 0.9, -rr * 0.5), (-rr * 0.9, rr * 0.5), (0, rr)]))
        pygame.draw.circle(low, li, P([(rr * 0.3, -rr * 0.3)])[0], max(1, rr * 0.3))
        _trail(low, P, rr, m, frame)
    elif kind == "wind":
        pts = [(math.cos(a) * rr * 1.3, math.sin(a) * rr * 1.6) for a in [(-80 + i * 16) * math.pi / 180 for i in range(11)]]
        pygame.draw.lines(low, m, False, P(pts), 2)
        pts2 = [(x - 2, y * 0.6) for x, y in pts]
        pygame.draw.lines(low, li, False, P(pts2), 1)
    elif kind == "bolt":
        pts = [(rr * 1.6, 0), (rr * 0.5, -rr * 0.5), (rr * 0.2, rr * 0.4), (-rr * 0.6, -rr * 0.2), (-rr * 1.5, rr * 0.3)]
        pygame.draw.lines(low, m, False, P(pts), 2)
        pygame.draw.lines(low, li, False, P(pts), 1)
    elif kind == "holy":
        pygame.draw.circle(low, _rgba(m, 150), c, rr * 1.3)
        for k in range(4):
            a = k * math.pi / 2 + frame * 0.3
            pygame.draw.line(low, li, c, (c[0] + math.cos(a) * rr * 1.6, c[1] + math.sin(a) * rr * 1.6), 1)
        pygame.draw.circle(low, li, c, max(1, rr * 0.6))
    elif kind == "poison":
        pygame.draw.circle(low, m, c, rr)
        pygame.draw.circle(low, li, (c[0] - rr * 0.3, c[1] - rr * 0.3), max(1, rr * 0.35))
        _trail(low, P, rr, d, frame)
    elif kind == "dark":
        for k in range(4):
            a = k * math.pi / 2 + frame * 0.5
            pygame.draw.circle(low, _rgba(d, 200), (c[0] + math.cos(a) * rr * 0.8, c[1] + math.sin(a) * rr * 0.8),
                               max(1, rr * 0.5))
        pygame.draw.circle(low, m, c, rr * 0.8)
        pygame.draw.circle(low, li, c, max(1, rr * 0.35))
    else:   # arcano / orbe
        pygame.draw.circle(low, _rgba(m, 140), c, rr * 1.3)
        pygame.draw.circle(low, m, c, rr)
        pygame.draw.circle(low, li, c, max(1, rr * 0.45))
        for k in range(3):
            a = k * math.tau / 3 + frame * 0.7
            low.set_at((int(c[0] + math.cos(a) * rr * 1.7), int(c[1] + math.sin(a) * rr * 1.7)), _rgba(li, 255))


# ---------------------------------------------------------------------------
# Impactos / explosões (quadros de animação)
# ---------------------------------------------------------------------------
NF = 7   # quadros por animação


def impact(look, radius, el=None):
    kind = look.get("impact", "hit") if isinstance(look, dict) else look
    el = el if el is not None else (look.get("el") if isinstance(look, dict) else None)
    rb = max(8, int(round(radius / 4.0)) * 4)   # mesmo raio da área de dano
    return _cache(("imp", kind, el, rb), lambda: [_impact(kind, el, rb, i / (NF - 1)) for i in range(NF)])


def _impact(kind, el, radius, p):
    R = radius / PX                                     # raio em pixels baixos
    tall = kind in ("pillar", "lightning", "meteor", "rain")
    w = int(R * 2 + 8)
    h = int(R * 2 + 8 + (R * 2.2 if tall else 0))
    low = pygame.Surface((w, h), pygame.SRCALPHA)
    c = (w / 2, h - R - 4)
    rnd = random.Random(int(radius) * 31 + hash(kind) % 997)
    d, m, li = pal(el if el else {"fist": None, "cut": None, "hit": None}.get(kind))
    fade = 1 - max(0.0, (p - 0.55) / 0.45)              # some no fim
    grow = min(1.0, p / 0.45)
    outline = None
    if kind not in ("rain",):
        # área de dano: o círculo cheio mostra exatamente até onde o golpe acerta
        fp = pygame.Surface(low.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(fp, _rgba(m, 55 * fade * (1 - p * 0.6)), c, R)
        pygame.draw.circle(fp, _rgba(li, 170 * fade), c, R, 1)
        low.blit(fp, (0, 0))
    if kind in ("fire", "meteor"):
        if False:   # (a queda agora é desenhada durante o aviso: falling())
            q = p / 0.35
            pos = (c[0] + R * 1.4 * (1 - q), c[1] - R * 3 * (1 - q))
            for k in range(6):
                pygame.draw.circle(low, _rgba(PAL["fire"][1], 220 - k * 35),
                                   (pos[0] + k * 2.2, pos[1] - k * 4), max(1, R * 0.28 - k * 0.6))
            pygame.draw.circle(low, (110, 80, 60), pos, max(2, R * 0.25))
            pygame.draw.circle(low, _rgba(PAL["fire"][2], 120), c, max(2, R * 0.9), 1)
        else:
            q = p
            g = min(1.0, q / 0.4)
            f = 1 - max(0.0, (q - 0.5) / 0.5)
            fd, fm, fl = PAL["fire"]
            for k in range(14):   # labaredas
                a = rnd.uniform(0, math.tau)
                dist = rnd.uniform(0.2, 1.0) * R * g
                pygame.draw.circle(low, _rgba(fm if k % 3 else fd, 230 * f),
                                   (c[0] + math.cos(a) * dist, c[1] + math.sin(a) * dist * 0.8),
                                   max(1, R * 0.32 * (1 - q * 0.6)))
            pygame.draw.circle(low, _rgba(fl, 240 * f), c, max(1, R * 0.5 * g * (1 - q * 0.5)))
            for k in range(5):   # fumaça subindo no fim
                a = rnd.uniform(0, math.tau)
                pygame.draw.circle(low, _rgba((70, 60, 60), 160 * q * f),
                                   (c[0] + math.cos(a) * R * 0.5, c[1] - R * q * 0.8 + math.sin(a) * R * 0.3),
                                   max(1, R * 0.22))
    elif kind == "lightning":
        x = c[0]
        pts, y = [], 2.0
        while y < c[1]:
            pts.append((x + rnd.uniform(-R * 0.25, R * 0.25), y))
            y += max(3.0, R * 0.45)
        pts.append(c)
        if p < 0.6:
            pygame.draw.lines(low, m, False, pts, 3)
            pygame.draw.lines(low, li, False, pts, 1)
        pygame.draw.circle(low, _rgba(li, 110 * fade * (1 - p)), c, max(1, R * grow * 0.6))
        pygame.draw.circle(low, _rgba(m, 220 * fade), c, max(2, R * grow), 2)
        for k in range(8):
            a = rnd.uniform(0, math.tau)
            r0 = R * (0.4 + 0.7 * p)
            q0 = (c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0)
            q1 = (q0[0] + math.cos(a + 0.6) * 3, q0[1] + math.sin(a + 0.6) * 3)
            pygame.draw.line(low, _rgba(li, 255 * fade), q0, q1, 1)
    elif kind == "ice":
        for k in range(10):   # cristais saindo do chão
            a = k * math.tau / 10 + rnd.uniform(-0.2, 0.2)
            L = R * rnd.uniform(0.55, 1.0) * grow
            base = (c[0] + math.cos(a) * R * 0.15, c[1] + math.sin(a) * R * 0.12)
            tip = (c[0] + math.cos(a) * L, c[1] + math.sin(a) * L * 0.75)
            nrm = (-math.sin(a) * 2, math.cos(a) * 2)
            pygame.draw.polygon(low, _rgba(m, 240 * fade), [tip, (base[0] + nrm[0], base[1] + nrm[1]),
                                                             (base[0] - nrm[0], base[1] - nrm[1])])
            pygame.draw.line(low, _rgba(li, 255 * fade), base, tip, 1)
        pygame.draw.circle(low, _rgba(li, 120 * fade), c, max(1, R * 0.95 * grow), 1)
        outline = (30, 50, 90) if fade > 0.6 else None
    elif kind in ("quake",):
        dd, dm, dl = PAL["earth"] if el in (None, "earth") else pal(el)
        pygame.draw.circle(low, _rgba(dd, 150 * fade), c, max(2, R * grow), 2)
        for k in range(7):   # pedras subindo
            a = rnd.uniform(0, math.tau)
            dist = rnd.uniform(0.2, 0.9) * R
            lift = math.sin(min(1.0, p * 1.6) * math.pi) * R * 0.5
            q = (c[0] + math.cos(a) * dist, c[1] + math.sin(a) * dist - lift * rnd.uniform(0.4, 1))
            sz = max(1.5, R * rnd.uniform(0.08, 0.16))
            pygame.draw.rect(low, _rgba(dm, 255 * fade), (q[0] - sz, q[1] - sz, sz * 2, sz * 2))
        for k in range(5):   # rachaduras
            a = k * math.tau / 5 + 0.3
            pygame.draw.line(low, _rgba((40, 30, 20), 220 * fade), c,
                             (c[0] + math.cos(a) * R * 0.85 * grow, c[1] + math.sin(a) * R * 0.85 * grow), 1)
        for k in range(8):   # poeira
            a = k * math.tau / 8
            pygame.draw.circle(low, _rgba(dl, 140 * fade), (c[0] + math.cos(a) * R * grow, c[1] + math.sin(a) * R * grow),
                               max(1, R * 0.18))
        outline = OUT if fade > 0.5 else None
    elif kind == "water":
        pygame.draw.circle(low, _rgba(m, 180 * fade), c, max(2, R * grow), 2)
        for k in range(12):
            a = rnd.uniform(math.pi, math.tau)
            sp_ = rnd.uniform(0.4, 1.0)
            t = p
            q = (c[0] + math.cos(a) * R * sp_ * t, c[1] + math.sin(a) * R * sp_ * t * 1.2 + R * 1.5 * t * t)
            pygame.draw.circle(low, _rgba(li if k % 2 else m, 240 * fade), q, max(1, R * 0.1))
    elif kind == "wind":
        for k in range(3):
            rr = R * (0.35 + 0.3 * k) * grow
            a0 = p * 5 + k * 2
            pts = [(c[0] + math.cos(a0 + i * 0.35) * rr, c[1] + math.sin(a0 + i * 0.35) * rr * 0.7) for i in range(9)]
            pygame.draw.lines(low, _rgba(li if k == 1 else m, 230 * fade), False, pts, 2)
    elif kind == "pillar":   # coluna de luz
        hh = c[1] - 2
        wdt = R * 0.55 * (1 - abs(p - 0.4))
        pygame.draw.rect(low, _rgba(m, 120 * fade), (c[0] - wdt, c[1] - hh, wdt * 2, hh))
        pygame.draw.rect(low, _rgba(li, 220 * fade), (c[0] - wdt * 0.4, c[1] - hh, wdt * 0.8, hh))
        pygame.draw.circle(low, _rgba(m, 200 * fade), c, max(2, R * grow), 2)
        for k in range(6):   # brilhos subindo
            x = c[0] + rnd.uniform(-R * 0.8, R * 0.8)
            y = c[1] - (rnd.uniform(0, 1) + p) % 1 * hh
            pygame.draw.line(low, _rgba(li, 255 * fade), (x - 1, y), (x + 1, y), 1)
            pygame.draw.line(low, _rgba(li, 255 * fade), (x, y - 1), (x, y + 1), 1)
    elif kind == "rune":   # círculo de runas arcano
        rr = R * grow
        pygame.draw.circle(low, _rgba(m, 220 * fade), c, max(2, rr), 2)
        pygame.draw.circle(low, _rgba(li, 180 * fade), c, max(1, rr * 0.7), 1)
        for k in range(8):
            a = k * math.tau / 8 + p * 2
            q = (c[0] + math.cos(a) * rr * 0.85, c[1] + math.sin(a) * rr * 0.85)
            pygame.draw.rect(low, _rgba(li, 255 * fade), (q[0] - 1, q[1] - 1, 2 + (k % 2), 2))
        pygame.draw.circle(low, _rgba(li, 160 * fade * (1 - grow * 0.5)), c, max(1, R * 0.4 * (1 - p)))
    elif kind == "gravity":
        rr = R * (1 - p * 0.8)
        pygame.draw.circle(low, _rgba(d, 170 * fade), c, max(2, rr))
        pygame.draw.circle(low, _rgba(m, 220 * fade), c, max(2, rr), 2)
        for k in range(10):
            a = k * math.tau / 10 + p * 4
            r0 = R * (1.1 - p)
            pygame.draw.line(low, _rgba(li, 230 * fade), (c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0),
                             (c[0] + math.cos(a + 0.4) * r0 * 0.7, c[1] + math.sin(a + 0.4) * r0 * 0.7), 1)
        pygame.draw.circle(low, (20, 10, 30, int(230 * fade)), c, max(1, R * 0.2))
    elif kind == "clock":
        rr = R * 0.85 * grow
        pygame.draw.circle(low, _rgba(d, 90 * fade), c, max(2, rr))
        pygame.draw.circle(low, _rgba(li, 230 * fade), c, max(2, rr), 2)
        for k in range(12):
            a = k * math.tau / 12
            pygame.draw.line(low, _rgba(m, 220 * fade), (c[0] + math.cos(a) * rr * 0.8, c[1] + math.sin(a) * rr * 0.8),
                             (c[0] + math.cos(a) * rr * 0.95, c[1] + math.sin(a) * rr * 0.95), 1)
        a1, a2 = -math.pi / 2 + p * 6, -math.pi / 2 + p * 1.2
        pygame.draw.line(low, _rgba(li, 255 * fade), c, (c[0] + math.cos(a1) * rr * 0.75, c[1] + math.sin(a1) * rr * 0.75), 1)
        pygame.draw.line(low, _rgba(li, 255 * fade), c, (c[0] + math.cos(a2) * rr * 0.5, c[1] + math.sin(a2) * rr * 0.5), 2)
    elif kind == "sound":
        for k in range(3):
            rr = R * min(1.0, p * 1.4 + k * 0.22)
            pygame.draw.circle(low, _rgba(m if k % 2 else li, 230 * fade * (1 - k * 0.2)), c, max(2, rr), 2)
        for k in range(3):   # notinhas
            a = k * math.tau / 3 + p * 2
            q = (c[0] + math.cos(a) * R * 0.6, c[1] + math.sin(a) * R * 0.6 - p * R * 0.4)
            pygame.draw.circle(low, _rgba(li, 255 * fade), q, 1.5)
            pygame.draw.line(low, _rgba(li, 255 * fade), (q[0] + 1, q[1]), (q[0] + 1, q[1] - 4), 1)
    elif kind in ("poison", "smoke"):
        cols = PAL[kind]
        for k in range(10):
            a = rnd.uniform(0, math.tau)
            dist = rnd.uniform(0.1, 0.85) * R * grow
            q = (c[0] + math.cos(a) * dist, c[1] + math.sin(a) * dist * 0.75 - (p * R * 0.3 if kind == "smoke" else 0))
            pygame.draw.circle(low, _rgba(cols[k % 3], 200 * fade), q, max(1, R * (0.32 if kind == "smoke" else 0.18)))
        if kind == "poison":
            for k in range(4):
                q = (c[0] + rnd.uniform(-R * 0.6, R * 0.6), c[1] - p * R * rnd.uniform(0.3, 0.8))
                pygame.draw.circle(low, _rgba(cols[2], 230 * fade), q, 1.5, 1)
    elif kind == "rain":   # flechas/lanças caindo do céu
        for k in range(5):
            t0 = k * 0.02
            q = max(0.0, min(1.0, (p - t0) / 0.12 + 0.5))   # as flechas chegam junto com o dano
            x = c[0] + (k - 2) * R * 0.38
            yend = c[1] + ((k * 7) % 5 - 2) * R * 0.3
            y = yend - (1 - q) * R * 2.5
            pygame.draw.line(low, WOOD[1], (x - 2, y - 6), (x, y), 1)
            pygame.draw.polygon(low, (210, 215, 225), [(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 2)])
            if q >= 1:
                pygame.draw.circle(low, _rgba((180, 160, 120), 160 * fade), (x, yend + 1), 2)
        if p > 0.3:
            pygame.draw.circle(low, _rgba((230, 220, 190), 130 * fade), c, R, 1)
        outline = OUT
    elif kind == "trap":
        sh = min(1.0, 0.5 + p / 0.2)
        jaw = R * 0.7
        for sgn in (-1, 1):
            y = c[1] + sgn * jaw * (1 - sh) * 0.6
            pygame.draw.line(low, (120, 120, 130), (c[0] - jaw, y), (c[0] + jaw, y), 2)
            for k in range(5):
                x = c[0] - jaw + k * jaw / 2
                pygame.draw.polygon(low, (200, 200, 210), [(x - 1.5, y), (x + 1.5, y), (x, y - sgn * 3)])
        pygame.draw.circle(low, _rgba((150, 30, 30), 180 * fade * sh), c, max(1, R * 0.3))
        outline = OUT if fade > 0.3 else None
    elif kind == "cut":   # X de cortes
        for sgn in (-1, 1):
            q = min(1.0, p / 0.35)
            a = math.radians(45 * sgn)
            L = R * 0.95 * q
            pygame.draw.line(low, _rgba(STEEL[2], 255 * fade), (c[0] - math.cos(a) * L, c[1] - math.sin(a) * L),
                             (c[0] + math.cos(a) * L, c[1] + math.sin(a) * L), 2)
        for k in range(5):
            a = rnd.uniform(0, math.tau)
            pygame.draw.circle(low, _rgba(PAL["blood"][1], 220 * fade), (c[0] + math.cos(a) * R * 0.5 * p,
                                                                        c[1] + math.sin(a) * R * 0.5 * p), 1)
    elif kind == "taunt":   # grito: ondas vermelhas
        for k in range(3):
            rr = R * min(1.0, p * 1.3 + k * 0.18)
            pygame.draw.circle(low, _rgba((240, 80, 60) if k % 2 == 0 else (255, 170, 120), 220 * fade), c,
                               max(2, rr), 2)
        pygame.draw.rect(low, _rgba((255, 230, 120), 255 * fade), (c[0] - 1, c[1] - R * 0.35, 3, R * 0.4))
        pygame.draw.rect(low, _rgba((255, 230, 120), 255 * fade), (c[0] - 1, c[1] + R * 0.12, 3, 3))
    else:   # fist / hit: estrela de impacto e poeira
        col = li if el else (255, 245, 210)
        n = 8
        for k in range(n):
            a = k * math.tau / n + 0.2
            r0 = R * 0.25 * grow
            r1 = R * (0.6 if k % 2 else 0.95) * grow
            pygame.draw.line(low, _rgba(col, 255 * fade), (c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0),
                             (c[0] + math.cos(a) * r1, c[1] + math.sin(a) * r1), 2 if k % 2 == 0 else 1)
        pygame.draw.circle(low, _rgba(m if el else (255, 230, 160), 180 * fade * (1 - p)), c, max(1, R * 0.35))
        pygame.draw.circle(low, _rgba((170, 160, 140), 140 * fade), c, max(2, R * grow), 1)
    return _bake(low, outline=outline, light=False), (c[0] * PX, c[1] * PX)


# ---------------------------------------------------------------------------
# Golpe em arco (swoosh), estocada e cone
# ---------------------------------------------------------------------------
def _ab(ang, step=15):
    return int(round(ang / step)) % int(360 / step) * step


def swoosh(look, radius, arc, ang, el=None):
    el = el if el is not None else look.get("el")
    rb, ab = max(12, int(round(radius / 4.0)) * 4), max(20, min(360, int(round(arc / 10.0)) * 10))
    fists = look.get("fists", False)
    return _cache(("sw", el, rb, ab, _ab(ang), fists),
                  lambda: [_swoosh(el, rb, ab, math.radians(_ab(ang)), i / (NF - 2), fists) for i in range(NF - 1)])


def _swoosh(el, radius, arc, ang, p, fists):
    R = radius / PX
    n = int(R * 2 + 8)
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    d, m, li = pal(el) if el else ((150, 160, 185), (215, 222, 238), (255, 255, 255))
    full = arc >= 360
    half = math.radians(arc) / 2
    a0 = ang - half if not full else ang
    span = math.radians(arc)
    head = min(1.0, p / 0.25)                 # a ponta percorre o arco logo no 1º quadro (o dano é na hora)
    tail = max(0.0, (p - 0.4) / 0.6)          # o rastro some atrás
    # área que o golpe acerta: o setor (ou o círculo, no giro de 360°) com o raio do alcance
    if head > tail:
        a_s, a_e = a0 + span * tail, a0 + span * head
        pts = [c] + [(c[0] + math.cos(a_s + (a_e - a_s) * i / 16) * R, c[1] + math.sin(a_s + (a_e - a_s) * i / 16) * R)
                     for i in range(17)]
        sec = pygame.Surface(low.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(sec, _rgba(m, 40 * (1 - tail)), pts)
        low.blit(sec, (0, 0))
    steps = 18
    for i in range(steps):
        u = i / steps
        if u < tail or u > head:
            continue
        a = a0 + span * u
        thick = (u - tail) / max(0.05, head - tail)        # mais grosso perto da ponta
        w = 1 + thick * R * 0.22
        r_out = R * 0.98
        r_in = r_out - w
        q0 = (c[0] + math.cos(a) * r_in, c[1] + math.sin(a) * r_in)
        q1 = (c[0] + math.cos(a) * r_out, c[1] + math.sin(a) * r_out)
        a2 = a + span / steps + 0.02
        q2 = (c[0] + math.cos(a2) * r_out, c[1] + math.sin(a2) * r_out)
        q3 = (c[0] + math.cos(a2) * r_in, c[1] + math.sin(a2) * r_in)
        alpha = 120 + 135 * thick
        pygame.draw.polygon(low, _rgba(m if thick < 0.7 else li, alpha), [q0, q1, q2, q3])
    if head > 0.05:   # brilho da ponta
        a = a0 + span * head
        q = (c[0] + math.cos(a) * R * 0.92, c[1] + math.sin(a) * R * 0.92)
        pygame.draw.circle(low, _rgba(li, 255 * (1 - tail)), q, max(1.5, R * 0.07))
        if fists:   # golpes de punho/chute: estrelinha de impacto na ponta
            for k in range(4):
                b = k * math.pi / 2 + 0.4
                pygame.draw.line(low, _rgba((255, 240, 200), 255 * (1 - tail)), q,
                                 (q[0] + math.cos(b) * 3, q[1] + math.sin(b) * 3), 1)
    return _bake(low), (c[0] * PX, c[1] * PX)


def thrust(look, length, width, ang, el=None, beam=None):
    el = el if el is not None else look.get("el")
    beam = beam if beam is not None else bool(el) and look.get("proj") not in ("javelin",)
    lb, wb = max(20, int(round(length / 6.0)) * 6), max(6, int(round(width / 4.0)) * 4)
    return _cache(("th", el, lb, wb, _ab(ang), beam),
                  lambda: [_thrust(el, lb, wb, math.radians(_ab(ang)), i / (NF - 2), beam) for i in range(NF - 1)])


def _thrust(el, length, width, ang, p, beam):
    L, Wd = length / PX, width / PX
    n = int(L * 2 + Wd + 10)
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    d, m, li = pal(el) if el else ((140, 150, 170), (215, 222, 238), (255, 255, 255))
    P = lambda pts: _rot(pts, ang, c)
    ext = min(1.0, 0.6 + p * 2)               # a estocada já sai quase inteira (o dano é na hora)
    fade = 1 - max(0.0, (p - 0.45) / 0.55)
    tipx = L * ext
    hw = Wd / 2
    if beam:   # raio mágico: faixa da largura do golpe com núcleo claro
        pygame.draw.polygon(low, _rgba(m, 150 * fade), P([(0, -hw), (tipx, -hw), (tipx, hw), (0, hw)]))
        pygame.draw.polygon(low, _rgba(li, 230 * fade), P([(0, -hw * 0.2), (tipx, -hw * 0.35), (tipx, hw * 0.35),
                                                           (0, hw * 0.2)]))
        pygame.draw.circle(low, _rgba(li, 230 * fade), P([(tipx, 0)])[0], max(1.5, hw * 0.8))
    else:      # estocada: faixa da largura do golpe (hitbox) + rastro e a ponta da lança/lâmina
        band = pygame.Surface(low.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(band, _rgba(m, 60 * fade), P([(0, -hw), (tipx, -hw), (tipx, hw), (0, hw)]))
        low.blit(band, (0, 0))
        for k, (yy, col) in enumerate(((-hw * 0.5, m), (0, li), (hw * 0.5, m))):
            x0 = tipx * (0.15 + 0.25 * abs(k - 1))
            pygame.draw.line(low, _rgba(col, 220 * fade), P([(x0, yy * (1 - ext * 0.4))])[0], P([(tipx - 3, yy * 0.3)])[0],
                             1 if k != 1 else 2)
        tip = (255, 255, 255) if not el else li
        pygame.draw.polygon(low, _rgba(tip, 255 * fade), P([(tipx + 3, 0), (tipx - 4, -max(2, hw * 0.5)),
                                                            (tipx - 2, 0), (tipx - 4, max(2, hw * 0.5))]))
    return _bake(low), (c[0] * PX, c[1] * PX)


CONE_STYLE = {"fire": "flame", "ice": "shard", "wind": "gust", "sound": "wave", "water": "wave", "smoke": "puff",
              "time": "wave", "arcane": "spark", "poison": "puff", "lightning": "spark", "holy": "spark",
              "earth": "puff", "gravity": "wave", None: "puff"}


def cone(look, radius, arc, ang, el=None):
    el = el if el is not None else look.get("el")
    rb, ab = max(20, int(round(radius / 6.0)) * 6), max(20, min(360, int(round(arc / 10.0)) * 10))
    return _cache(("cone", el, rb, ab, _ab(ang)),
                  lambda: [_cone(el, rb, ab, math.radians(_ab(ang)), i / (NF - 1)) for i in range(NF)])


def _cone(el, radius, arc, ang, p):
    R = radius / PX
    n = int(R * 2 + 8)
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    d, m, li = pal(el)
    style = CONE_STYLE.get(el, "puff")
    half = math.radians(arc) / 2
    fade = 1 - max(0.0, (p - 0.5) / 0.5)
    rnd = random.Random(radius * 7 + arc)
    front = R * min(1.0, 0.75 + p * 1.5)      # o cone cobre a área quase toda no 1º quadro (dano na hora)
    sec = pygame.Surface(low.get_size(), pygame.SRCALPHA)   # área do cone (hitbox)
    pts = [c] + [(c[0] + math.cos(ang - half + 2 * half * i / 16) * front, c[1] + math.sin(ang - half + 2 * half * i / 16) * front)
                 for i in range(17)]
    pygame.draw.polygon(sec, _rgba(m, 60 * fade), pts)
    if p > 0.35:
        pygame.draw.polygon(sec, _rgba(li, 120 * fade), pts, 1)
    low.blit(sec, (0, 0))
    if style == "wave":
        for k in range(3):
            rr = front * (1 - k * 0.22)
            if rr <= 2:
                continue
            pts = [(c[0] + math.cos(ang - half + 2 * half * i / 10) * rr, c[1] + math.sin(ang - half + 2 * half * i / 10) * rr)
                   for i in range(11)]
            pygame.draw.lines(low, _rgba(li if k == 0 else m, 230 * fade * (1 - k * 0.25)), False, pts, 2)
    else:
        for k in range(26):
            a = ang + rnd.uniform(-half, half)
            sz = max(1.0, R * 0.035 * (0.7 + rnd.random()))
            dist = (front - sz * 3) * rnd.uniform(0.25, 1.0)   # tudo dentro do cone (hitbox)
            a = ang + rnd.uniform(-half, half) * max(0.0, 1 - sz * 2.5 / max(1.0, dist))
            q = (c[0] + math.cos(a) * dist, c[1] + math.sin(a) * dist)
            col = (li, m, d)[k % 3]
            if style == "flame":
                pygame.draw.circle(low, _rgba(col, 230 * fade), q, sz * 1.8)
            elif style == "shard":
                pygame.draw.line(low, _rgba(col, 240 * fade), q, (q[0] + math.cos(a) * sz * 2.5, q[1] + math.sin(a) * sz * 2.5), 1)
            elif style == "gust":
                pygame.draw.line(low, _rgba(col, 220 * fade), q, (q[0] + math.cos(a) * sz * 2.5, q[1] + math.sin(a) * sz * 2.5), 1)
            elif style == "spark":
                pygame.draw.rect(low, _rgba(col, 255 * fade), (q[0], q[1], 1 + (k % 2), 1 + (k % 2)))
            else:   # puff (fumaça / poeira / veneno)
                pygame.draw.circle(low, _rgba(col, 160 * fade), q, sz * 2.0)
    return _bake(low), (c[0] * PX, c[1] * PX)


# ---------------------------------------------------------------------------
# Cura e bônus (no alvo)
# ---------------------------------------------------------------------------
def heal_anim():
    return _cache(("heal",), lambda: [_heal(i / (NF - 1)) for i in range(NF)])


def _heal(p):
    n = 28
    low = pygame.Surface((n, n + 12), pygame.SRCALPHA)
    c = (n / 2, n / 2 + 8)
    fade = 1 - max(0.0, (p - 0.5) / 0.5)
    pygame.draw.ellipse(low, (110, 230, 120, int(150 * fade)), (c[0] - 11 * min(1, p * 2), c[1] + 4, 22 * min(1, p * 2), 7), 1)
    for k, (dx, ph) in enumerate(((-6, 0.0), (5, 0.25), (0, 0.5), (-2, 0.7))):
        q = (p + ph) % 1.0
        y = c[1] + 2 - q * 18
        col = (140, 250, 150) if k % 2 else (230, 255, 230)
        a = int(255 * fade * (1 - q * 0.5))
        pygame.draw.rect(low, (*col, a), (c[0] + dx - 1, y - 3, 2, 6))
        pygame.draw.rect(low, (*col, a), (c[0] + dx - 3, y - 1, 6, 2))
    return _bake(low, outline=(20, 70, 30), light=False), (c[0] * PX, c[1] * PX)


BUFF_GLYPH = {"dmg": "sword", "speed": "wing", "haste": "hourglass", "dr": "shield"}


def buff_anim(effects):
    keys = [BUFF_GLYPH.get(k, "star") for k in (effects or {})][:2] or ["star"]
    return _cache(("buff", tuple(keys)), lambda: [_buff(keys, i / (NF - 1)) for i in range(NF)])


def _glyph(low, kind, x, y, a):
    gold, white = (250, 210, 80, a), (255, 250, 230, a)
    if kind == "sword":
        pygame.draw.line(low, white, (x, y - 5), (x, y + 2), 2)
        pygame.draw.line(low, gold, (x - 2, y + 2), (x + 2, y + 2), 1)
        pygame.draw.line(low, (140, 90, 50, a), (x, y + 3), (x, y + 5), 1)
    elif kind == "wing":
        pygame.draw.polygon(low, white, [(x - 4, y + 2), (x + 3, y - 4), (x + 4, y - 1), (x, y + 3)])
        pygame.draw.line(low, gold, (x - 2, y + 1), (x + 3, y - 3), 1)
    elif kind == "hourglass":
        pygame.draw.polygon(low, gold, [(x - 3, y - 4), (x + 3, y - 4), (x, y), (x + 3, y + 4), (x - 3, y + 4), (x, y)])
        pygame.draw.line(low, white, (x - 1, y + 3), (x + 1, y + 3), 1)
    elif kind == "shield":
        pygame.draw.polygon(low, (150, 190, 255, a), [(x - 4, y - 4), (x + 4, y - 4), (x + 4, y), (x, y + 5), (x - 4, y)])
        pygame.draw.line(low, white, (x, y - 3), (x, y + 3), 1)
    else:
        pygame.draw.polygon(low, gold, [(x, y - 4), (x + 1, y - 1), (x + 4, y), (x + 1, y + 1), (x, y + 4),
                                        (x - 1, y + 1), (x - 4, y), (x - 1, y - 1)])


def _buff(keys, p):
    n = 30
    low = pygame.Surface((n, n + 14), pygame.SRCALPHA)
    c = (n / 2, n / 2 + 10)
    fade = 1 - max(0.0, (p - 0.55) / 0.45)
    rr = 6 + p * 8
    pygame.draw.ellipse(low, (250, 210, 80, int(200 * fade)), (c[0] - rr, c[1] + 3 - rr * 0.3, rr * 2, rr * 0.6), 1)
    for k, g in enumerate(keys):
        dx = 0 if len(keys) == 1 else (-5 if k == 0 else 5)
        _glyph(low, g, c[0] + dx, c[1] - 4 - p * 12, int(255 * fade))
    return _bake(low, outline=(50, 35, 10), light=False), (c[0] * PX, c[1] * PX)


# ---------------------------------------------------------------------------
# Marcadores de status em cima dos inimigos (Provocado / Enfraquecido)
# ---------------------------------------------------------------------------
def marker(kind):
    return _cache(("mark", kind), lambda: _marker(kind))


def _marker(kind):
    low = pygame.Surface((9, 11), pygame.SRCALPHA)
    if kind == "taunt":
        pygame.draw.rect(low, (240, 70, 50), (3, 1, 3, 6))
        pygame.draw.rect(low, (240, 70, 50), (3, 8, 3, 2))
        pygame.draw.line(low, (255, 170, 140), (4, 2), (4, 5), 1)
    else:   # weaken: setinha para baixo roxa
        pygame.draw.polygon(low, (190, 110, 240), [(1, 4), (8, 4), (4, 9)])
        pygame.draw.rect(low, (190, 110, 240), (3, 1, 3, 4))
        pygame.draw.line(low, (240, 200, 255), (4, 2), (4, 6), 1)
    return _bake(low, outline=OUT, light=False)


# ---------------------------------------------------------------------------
# Elementos contínuos: aura, órbita, nuvem e invocações
# ---------------------------------------------------------------------------
def particle(kind, el, size, frame):
    """Partícula pequena (chama, runa, bolha, faísca, folha de vento...)."""
    return _cache(("pt", kind, el, size, frame), lambda: _particle(kind, el, size, frame))


def _particle(kind, el, size, frame):
    n = size * 2 + 4
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    d, m, li = pal(el)
    outline = None
    if kind == "flame":
        h = size * (1.0 + 0.25 * (frame % 2))
        pygame.draw.polygon(low, m, [(c[0] - size * 0.7, c[1] + size * 0.6), (c[0] + size * 0.7, c[1] + size * 0.6),
                                     (c[0] + (frame - 1) * 0.8, c[1] - h)])
        pygame.draw.polygon(low, li, [(c[0] - size * 0.3, c[1] + size * 0.6), (c[0] + size * 0.3, c[1] + size * 0.6),
                                      (c[0], c[1] - h * 0.4)])
    elif kind == "rune":
        pygame.draw.rect(low, li, (c[0] - 1, c[1] - size * 0.8, 2, size * 1.6))
        pygame.draw.line(low, m, (c[0] - size * 0.6, c[1] - size * 0.3 + frame), (c[0] + size * 0.6, c[1] + size * 0.3 - frame), 1)
    elif kind == "bubble":
        rr = max(1, size * (0.5 + 0.25 * frame))
        pygame.draw.circle(low, m, c, rr, 1)
        low.set_at((int(c[0] - rr * 0.4), int(c[1] - rr * 0.4)), li)
    elif kind == "spike":
        pygame.draw.polygon(low, (170, 170, 180), [(c[0] - size * 0.6, c[1] + size * 0.4), (c[0] + size * 0.6, c[1] + size * 0.4),
                                                   (c[0], c[1] - size * 0.7)])
        outline = OUT
    elif kind == "swirl":
        pts = [(c[0] + math.cos(a) * size * (0.3 + a / 7), c[1] + math.sin(a) * size * (0.3 + a / 7) * 0.7)
               for a in [i * 0.6 + frame for i in range(9)]]
        pygame.draw.lines(low, li, False, pts, 1)
    else:   # spark
        pygame.draw.rect(low, li, (c[0] - 1, c[1] - 1, 2, 2))
        pygame.draw.line(low, m, (c[0] - size * 0.8, c[1]), (c[0] + size * 0.8, c[1]), 1)
        pygame.draw.line(low, m, (c[0], c[1] - size * 0.8), (c[0], c[1] + size * 0.8), 1)
    return _bake(low, outline=outline, light=False)


CLOUD_PART = {"fire": "flame", "poison": "bubble", "water": "swirl", "wind": "swirl", "holy": "rune",
              "arcane": "rune", "time": "rune", "earth": "bubble", "smoke": "bubble", "sound": "spark",
              "lightning": "spark", "ice": "spark", "gravity": "swirl", None: "spike"}


def draw_cloud(s, pos, r, el, t, life_frac, seed=0, name=""):
    """Área persistente animada (chão em chamas, nuvem tóxica, redemoinho, círculo de runas, estrepes...)."""
    d, m, li = pal(el)
    key = ("cl", el, int(r))
    base = _CACHE.get(key)
    if base is None:
        rr = int(r)
        surf = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
        cc = (rr + 2, rr + 2)
        pygame.draw.circle(surf, (*m, 55), cc, rr)
        pygame.draw.circle(surf, (*li, 90), cc, rr, 2)
        base = _CACHE[key] = surf
    a = max(0.0, min(1.0, life_frac * 3))
    if a < 1:
        b = base.copy()
        b.set_alpha(int(255 * a))
        s.blit(b, (pos[0] - base.get_width() / 2, pos[1] - base.get_height() / 2))
    else:
        s.blit(base, (pos[0] - base.get_width() / 2, pos[1] - base.get_height() / 2))
    kind = "spike" if "caltrop" in name.lower() else CLOUD_PART.get(el, "bubble")
    rnd = random.Random(seed)
    n = max(5, min(16, int(r / 9)))
    for k in range(n):
        ang = rnd.uniform(0, math.tau)
        dist = math.sqrt(rnd.uniform(0.02, 1.0)) * r * 0.9
        if kind in ("swirl", "rune"):
            ang += t * (1.2 if kind == "swirl" else 0.4) * (1 if k % 2 else -1)
        q = (pos[0] + math.cos(ang) * dist, pos[1] + math.sin(ang) * dist)
        if kind in ("bubble", "flame"):
            q = (q[0], q[1] - ((t * 0.8 + k * 0.37) % 1.0) * 10)
        fr = int(t * 8 + k) % 3
        sp = particle(kind, el, 3 if kind != "flame" else 4, fr)
        if a < 1:
            sp = sp.copy()
            sp.set_alpha(int(255 * a))
        s.blit(sp, (q[0] - sp.get_width() / 2, q[1] - sp.get_height() / 2))


AURA_PART = {"holy": "rune", "arcane": "rune", "fire": "flame", None: "spark"}


def draw_aura(s, pos, r, el, t):
    d, m, li = pal(el)
    key = ("au", el, int(r))
    base = _CACHE.get(key)
    if base is None:
        rr = int(r)
        surf = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*m, 30), (rr + 2, rr + 2), rr)
        pygame.draw.circle(surf, (*li, 110), (rr + 2, rr + 2), rr, 2)
        base = _CACHE[key] = surf
    s.blit(base, (pos[0] - base.get_width() / 2, pos[1] - base.get_height() / 2))
    kind = AURA_PART.get(el, "spark")
    n = max(6, int(r / 10))
    for k in range(n):
        a = t * 1.6 + k * math.tau / n
        q = (pos[0] + math.cos(a) * r * 0.93, pos[1] + math.sin(a) * r * 0.93)
        sp = particle(kind, el, 3, int(t * 8 + k) % 3)
        s.blit(sp, (q[0] - sp.get_width() / 2, q[1] - sp.get_height() / 2))


def orbit_sprite(look, t, k):
    """Lâmina girando ou orbe arcano (órbitas)."""
    el = look.get("el")
    if el in (None,) or look.get("proj") in ("sword", "dagger", "axe"):
        return projectile_sprite(dict(proj="sword"), 7, V(1, 0), t * 1.4 + k * 0.3)
    return projectile_sprite(dict(proj="arcane", el=el), 7, V(1, 0), t + k * 0.2, el=el)


def minion_sprite(name, r, color, el, facing_right, t):
    """Invocações: lobo, falcão, espíritos elementais, clone de sombra..."""
    low_name = (name or "").lower()
    frame = int(t * 8) % 2
    kind = "wolf" if "wolf" in low_name else "bird" if ("falcon" in low_name or "garuda" in low_name) else \
        "spirit"
    return _cache(("min", kind, int(r), color, el, facing_right, frame),
                  lambda: _minion(kind, int(r), color, el, facing_right, frame))


def _minion(kind, r, color, el, right, frame):
    if kind == "wolf":
        import enemy_sprites
        return enemy_sprites.sprite("lobo", max(8, r), (150, 150, 165), right, frame)
    n = r * 2 + 8
    low = pygame.Surface((n, n), pygame.SRCALPHA)
    c = (n / 2, n / 2)
    col = tuple(color)
    li = tuple(min(255, int(v * 0.5 + 128)) for v in col)
    dk = tuple(int(v * 0.55) for v in col)
    R = r / PX * 1.1
    if kind == "bird":
        wing = R * (0.9 if frame else 0.3)
        pygame.draw.ellipse(low, col, (c[0] - R * 0.7, c[1] - R * 0.35, R * 1.4, R * 0.7))
        pygame.draw.polygon(low, dk, [(c[0] - R * 0.2, c[1]), (c[0] + R * 0.3, c[1]), (c[0], c[1] - wing - 1)])
        pygame.draw.polygon(low, (230, 190, 80), [(c[0] + R * 0.7, c[1] - 1), (c[0] + R * 1.05, c[1]), (c[0] + R * 0.7, c[1] + 1)])
        low.set_at((int(c[0] + R * 0.45), int(c[1] - R * 0.15)), (20, 20, 20))
    else:   # espírito elemental: chama/gota com olhinhos
        for k in range(3):
            q = (c[0] - R * 0.5 - k * R * 0.35, c[1] + math.sin(frame * 2 + k) * 1.2)
            pygame.draw.circle(low, (*col, 200 - k * 50), q, max(1, R * (0.55 - k * 0.12)))
        pygame.draw.circle(low, col, c, R * 0.8)
        pygame.draw.circle(low, li, (c[0] - R * 0.2, c[1] - R * 0.25), max(1, R * 0.35))
        for sx in (0.15, 0.45):
            low.set_at((int(c[0] + R * sx), int(c[1] - R * 0.05)), (20, 16, 30))
            low.set_at((int(c[0] + R * sx), int(c[1] + R * 0.12)), (20, 16, 30))
    surf = _bake(low, outline=OUT, light=True)
    if not right:
        surf = pygame.transform.flip(surf, True, False)
    return surf


def falling(look, radius, el=None):
    """Meteoro / cometa caindo durante o aviso de uma área com atraso (cai bem quando o dano acontece)."""
    el = el if el is not None else look.get("el")
    rb = max(8, int(round(radius / 4.0)) * 4)
    return _cache(("fall", el, rb), lambda: [_falling(el, rb, i / 9) for i in range(10)])


def _falling(el, radius, p):
    R = radius / PX
    w, h = int(R * 2 + 8 + R * 1.6), int(R * 2 + 8 + R * 3.2)
    low = pygame.Surface((w, h), pygame.SRCALPHA)
    c = (w / 2 - R * 0.8, h - R - 4)
    fd, fm, fl = PAL["fire"] if el in (None, "fire") else pal(el)
    pos = (c[0] + R * 1.6 * (1 - p), c[1] - R * 3.2 * (1 - p))
    for k in range(6):
        pygame.draw.circle(low, _rgba(fm if k < 3 else fd, 230 - k * 35), (pos[0] + k * 2.4, pos[1] - k * 4.6),
                           max(1, R * 0.26 - k * 0.5))
    pygame.draw.circle(low, (110, 80, 60), pos, max(2, R * 0.24))
    pygame.draw.circle(low, (160, 120, 90), (pos[0] - 1, pos[1] - 1), max(1, R * 0.1))
    pygame.draw.circle(low, _rgba((20, 10, 10), 60 + 90 * p), c, max(2, R * (0.3 + 0.5 * p)))   # sombra crescendo
    return _bake(low, outline=None), (c[0] * PX, c[1] * PX)


# ---------------------------------------------------------------------------
# Status (debuffs) em quem está afetado: sangrando, envenenado, queimando, congelando, atordoado, lento
# ---------------------------------------------------------------------------
def _dot_sprite(kind, frame):
    return _cache(("st", kind, frame), lambda: _dot(kind, frame))


def _dot(kind, frame):
    low = pygame.Surface((9, 9), pygame.SRCALPHA)
    c = (4.5, 4.5)
    outline = None
    if kind == "blood":      # gota de sangue
        pygame.draw.polygon(low, (200, 30, 40), [(4, 2), (5, 5), (4, 6), (3, 5)])
        low.set_at((4, 4), (255, 120, 120))
        outline = (60, 5, 10)
    elif kind == "poison":   # bolha verde
        pygame.draw.circle(low, (140, 220, 70), c, 1.5 + frame * 0.6, 1)
        low.set_at((3, 3), (230, 255, 170))
    elif kind == "flame":
        pygame.draw.polygon(low, (250, 120, 40), [(2, 7), (7, 7), (4.5 + (frame - 1) * 0.6, 1 + frame * 0.4)])
        pygame.draw.polygon(low, (255, 220, 110), [(3.5, 7), (5.5, 7), (4.5, 4)])
    elif kind == "frost":
        pygame.draw.line(low, (210, 240, 255), (4, 1), (4, 7), 1)
        pygame.draw.line(low, (210, 240, 255), (1, 4), (7, 4), 1)
        if frame % 2:
            pygame.draw.line(low, (150, 210, 255), (2, 2), (6, 6), 1)
            pygame.draw.line(low, (150, 210, 255), (6, 2), (2, 6), 1)
    elif kind == "star":     # estrelinha de atordoado
        pygame.draw.polygon(low, (255, 230, 90), [(4, 0), (5, 3), (8, 4), (5, 5), (4, 8), (3, 5), (0, 4), (3, 3)])
        outline = (80, 60, 10)
    elif kind == "slow":     # ondinha azul (lento)
        pygame.draw.lines(low, (130, 190, 255), False, [(1, 5), (3, 3 + frame % 2), (5, 5), (7, 3)], 1)
    return _bake(low, outline=outline, light=False)


def draw_status(s, pos, r, sts, t, seed=0):
    """Animações leves dos debuffs no alvo (pos = centro na tela, r = raio)."""
    if not sts:
        return
    x, y = pos[0], pos[1]
    ph = (seed % 97) * 0.173
    if "bleeding" in sts:    # gotas caindo
        for k in range(3):
            q = (t * 1.6 + ph + k / 3) % 1.0
            spr = _dot_sprite("blood", 0)
            dx = (k - 1) * r * 0.55
            spr2 = spr.copy() if q > 0.7 else spr
            if q > 0.7:
                spr2.set_alpha(int(255 * (1 - q) / 0.3))
            s.blit(spr2, (x + dx - 9, y - r * 0.2 + q * r * 1.3 - 9))
    if "poisoned" in sts:    # bolhas verdes subindo
        for k in range(3):
            q = (t * 1.1 + ph + k / 3) % 1.0
            spr = _dot_sprite("poison", int(q * 3) % 3)
            s.blit(spr, (x + math.sin(q * 6 + k * 2) * r * 0.5 - 9, y - q * r * 1.8 - 9))
    if "burning" in sts:     # chamas lambendo o corpo
        for k in range(3):
            q = (t * 2.2 + ph + k / 3) % 1.0
            spr = _dot_sprite("flame", int(t * 10 + k) % 3)
            s.blit(spr, (x + (k - 1) * r * 0.6 - 9, y + r * 0.3 - q * r * 1.2 - 9))
    if "chilled" in sts:     # brilhinhos de gelo em volta
        for k in range(3):
            a = t * 1.5 + ph + k * math.tau / 3
            spr = _dot_sprite("frost", int(t * 6 + k) % 2)
            s.blit(spr, (x + math.cos(a) * r * 0.9 - 9, y + math.sin(a) * r * 0.5 - 9))
    if "stunned" in sts:     # estrelinhas girando em cima da cabeça
        for k in range(3):
            a = t * 5 + k * math.tau / 3
            spr = _dot_sprite("star", 0)
            s.blit(spr, (x + math.cos(a) * r * 0.7 - 9, y - r - 6 + math.sin(a) * 3 - 9))
    elif "slowed" in sts:    # ondinhas azuis nos pés
        for k in range(2):
            spr = _dot_sprite("slow", int(t * 4 + k) % 2)
            s.blit(spr, (x + (k - 0.5) * r * 0.9 - 9, y + r * 0.7 - 9))


def blit_anim(s, frames, prog, pos):
    """Desenha o quadro da animação (prog 0..1) centrado em pos (frames = [(surf, centro)])."""
    if not frames:
        return
    i = min(len(frames) - 1, int(prog * len(frames)))
    surf, c = frames[i]
    s.blit(surf, (pos[0] - c[0], pos[1] - c[1]))
