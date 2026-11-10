"""Ícone provisório de cada classe: bolinha na cor da classe + chapéu + arma (desenhados com primitivas)."""
import math

import pygame
from pygame.math import Vector2 as V

from data import CLASSES

OUT = (20, 20, 26)
STEEL = (200, 205, 215)
WOOD = (130, 90, 55)
GOLD = (235, 195, 70)
WHITE = (240, 240, 245)
RED = (200, 50, 50)


def _shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


class _Pen:
    """Desenha em coordenadas relativas ao centro, em unidades do raio (y negativo = para cima)."""

    def __init__(self, s, center, r, angle=0.0):
        self.s, self.c, self.r, self.a = s, V(center), r, angle

    def pt(self, x, y):
        return self.c + V(x, y).rotate(self.a) * self.r

    def poly(self, pts, col, outline=True):
        p = [self.pt(x, y) for x, y in pts]
        pygame.draw.polygon(self.s, col, p)
        if outline and self.r >= 8:
            pygame.draw.polygon(self.s, OUT, p, 1)

    def circle(self, x, y, rad, col, outline=True):
        c = self.pt(x, y)
        rr = max(1, int(rad * self.r))
        pygame.draw.circle(self.s, col, c, rr)
        if outline and self.r >= 8:
            pygame.draw.circle(self.s, OUT, c, rr, 1)

    def line(self, x1, y1, x2, y2, col, w=0.12):
        pygame.draw.line(self.s, col, self.pt(x1, y1), self.pt(x2, y2), max(1, int(w * self.r)))

    def lines(self, pts, col, w=0.1):
        pygame.draw.lines(self.s, col, False, [self.pt(x, y) for x, y in pts], max(1, int(w * self.r)))


def _arc(cx, cy, rad, a0, a1, n=10, ry=None):
    ry = rad if ry is None else ry
    return [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * rad,
             cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * ry) for i in range(n + 1)]


# ---------------------------------------------------------------------------
# Chapéus
# ---------------------------------------------------------------------------
def hat_wizard(p, col, band=None, tall=1.5, brim=1.25, star=False):
    p.poly([(-0.62, -0.62), (0.62, -0.62), (0.28, -0.62 - tall * 0.7), (0.05, -0.62 - tall)], col)
    if band:
        p.poly([(-0.6, -0.62), (0.6, -0.62), (0.52, -0.82), (-0.52, -0.82)], band)
    p.poly(_arc(0, -0.6, brim, 180, 360, 12, 0.18) + _arc(0, -0.6, brim, 0, 180, 12, 0.18), _shade(col, 0.8))
    if star:
        p.circle(0.12, -0.62 - tall * 0.55, 0.12, GOLD, outline=False)


def hat_hood(p, col, pointed=True, trim=None, gem=None, horn=None):
    pts = _arc(0, -0.05, 1.12, 180, 360, 14)
    if pointed:
        pts = pts[:7] + [(0.15, -1.55)] + pts[7:]
    pts += [(1.12, 0.15), (0.72, 0.1)] + _arc(0, 0.1, 0.72, 0, -180, 10)[1:] + [(-1.12, 0.15)]
    p.poly(pts, col)
    if trim:
        for i in range(4):
            x = -0.75 + i * 0.5
            p.poly([(x - 0.18, -0.25 - abs(x) * 0.25), (x + 0.18, -0.25 - abs(x) * 0.25), (x, -0.5 - abs(x) * 0.2)],
                   trim, outline=False)
    if gem:
        p.circle(0, -0.78, 0.16, gem)
    if horn:
        p.poly([(-0.14, -0.95), (0.14, -0.95), (0.3, -1.6)], horn)


def hat_band(p, col, tails=True, knot=None):
    p.poly([(-0.98, -0.42), (0.98, -0.42), (0.92, -0.62), (-0.92, -0.62)], col)
    if tails:
        p.poly([(-0.9, -0.55), (-1.5, -0.25), (-1.4, -0.05), (-0.85, -0.42)], _shade(col, 0.85))
        p.poly([(-0.9, -0.5), (-1.55, -0.65), (-1.5, -0.45)], _shade(col, 0.85))
    if knot:
        p.circle(0, -1.05, 0.32, knot)


def hat_cap(p, col, feather=RED):
    p.poly([(-0.95, -0.5), (0.95, -0.5), (0.55, -1.0), (-0.1, -1.25), (-0.7, -1.0)], col)
    p.lines([(0.1, -1.05), (-0.5, -1.45), (-1.05, -1.55)], feather, 0.14)


def hat_cavalier(p, col, plume):
    p.poly(_arc(0, -0.75, 1.0, 180, 360, 12, 0.55), col)
    p.poly(_arc(0, -0.72, 1.45, 180, 360, 14, 0.2) + _arc(0, -0.72, 1.45, 0, 180, 14, 0.2), _shade(col, 0.8))
    p.lines([(0.3, -1.15), (-0.3, -1.65), (-1.1, -1.55), (-1.5, -1.1)], plume, 0.22)


def hat_mortarboard(p, col):
    p.poly(_arc(0, -0.75, 0.75, 180, 360, 10, 0.4), col)
    p.poly([(-1.25, -1.15), (0, -1.45), (1.25, -1.15), (0, -0.85)], col)
    p.lines([(0, -1.15), (0.9, -1.0), (0.95, -0.6)], GOLD, 0.1)


def hat_helmet(p, col, extra=None, visor=False):
    p.poly(_arc(0, -0.3, 1.04, 180, 360, 14) + [(1.04, -0.18), (-1.04, -0.18)], col)
    p.poly([(-1.3, -0.3), (1.3, -0.3), (1.25, -0.15), (-1.25, -0.15)], _shade(col, 0.75))
    if visor:
        p.line(-0.6, -0.5, 0.75, -0.5, OUT, 0.14)
    if extra == "crest":
        p.poly(_arc(0, -1.15, 0.75, 180, 360, 10, 0.35) + [(0.75, -1.1), (-0.75, -1.1)], RED)
    elif extra == "horns":
        p.poly([(-0.9, -0.75), (-1.55, -1.35), (-1.25, -0.6)], WHITE)
        p.poly([(0.9, -0.75), (1.55, -1.35), (1.25, -0.6)], WHITE)
    elif extra == "dragon":
        for i in range(3):
            x = -0.6 + i * 0.4
            p.poly([(x - 0.15, -1.1 + abs(x) * 0.2), (x + 0.15, -1.1 + abs(x) * 0.2), (x - 0.25, -1.55 + abs(x) * 0.2)],
                   (90, 140, 230))
        p.poly([(0.8, -0.55), (1.6, -0.95), (1.0, -0.3)], WHITE)
    elif extra == "cross":
        p.line(0, -0.9, 0, -0.35, GOLD, 0.16)
        p.line(-0.22, -0.7, 0.22, -0.7, GOLD, 0.16)
    elif extra == "plume":
        p.lines([(0, -1.15), (-0.4, -1.6), (-1.0, -1.5), (-1.3, -1.1)], (230, 60, 60), 0.24)
    elif extra == "halo":
        pygame.draw.ellipse(p.s, GOLD, pygame.Rect(p.pt(-0.7, -1.55).x, p.pt(-0.7, -1.55).y, 1.4 * p.r, 0.35 * p.r),
                            max(1, int(0.1 * p.r)))


def hat_circlet(p, col=GOLD, gem=(90, 200, 255), wings=False):
    p.lines(_arc(0, -0.25, 0.95, 200, 340, 10), col, 0.14)
    p.circle(0, -0.58, 0.16, gem)
    if wings:
        p.poly([(-0.85, -0.55), (-1.5, -1.05), (-1.25, -0.5)], WHITE)
        p.poly([(0.85, -0.55), (1.5, -1.05), (1.25, -0.5)], WHITE)


def hat_mitre(p, col):
    p.poly([(-0.6, -0.6), (0.6, -0.6), (0.62, -1.3), (0.05, -1.85), (-0.62, -1.3)], col)
    p.line(0, -1.55, 0, -0.75, GOLD, 0.13)
    p.line(-0.25, -1.25, 0.25, -1.25, GOLD, 0.13)


def hat_pelt(p, col):
    p.poly(_arc(0, -0.3, 1.1, 180, 360, 14) + [(1.1, -0.15), (-1.1, -0.15)], col)
    p.poly([(-0.85, -0.7), (-0.75, -1.45), (-0.3, -0.95)], col)
    p.poly([(0.85, -0.7), (0.75, -1.45), (0.3, -0.95)], col)
    p.poly([(-0.95, -0.95), (-1.6, -1.6), (-1.3, -0.75)], (220, 60, 50))
    p.poly([(0.95, -0.95), (1.6, -1.6), (1.3, -0.75)], (220, 60, 50))


# ---------------------------------------------------------------------------
# Armas  (eixo x = comprimento da arma)
# ---------------------------------------------------------------------------
def w_sword(p, blade=STEEL, length=1.35):
    p.line(-0.3, 0, 0.05, 0, WOOD, 0.2)
    p.poly([(0.05, -0.1), (length, -0.08), (length + 0.2, 0), (length, 0.08), (0.05, 0.1)], blade)
    p.line(0.05, -0.3, 0.05, 0.3, GOLD, 0.16)


def w_bow(p, size=1.0):
    size *= 0.85
    pts = [(0.4 * size * (1 - t * t), t * 0.95 * size) for t in [i / 8 - 1 for i in range(17)]]
    p.lines(pts, WOOD, 0.16)
    p.line(0, -0.95 * size, 0, 0.95 * size, WHITE, 0.05)


def w_staff(p, orb, hourglass=False, cross=False):
    p.line(-0.5, 0, 1.45, 0, WOOD, 0.16)
    if hourglass:
        p.poly([(1.4, -0.28), (1.4, 0.28), (1.95, -0.28), (1.95, 0.28)], GOLD)
    elif cross:
        p.line(1.45, 0, 2.0, 0, GOLD, 0.16)
        p.line(1.75, -0.25, 1.75, 0.25, GOLD, 0.16)
    else:
        p.circle(1.65, 0, 0.27, orb)


def w_book(p, col):
    p.poly([(-0.1, -0.38), (0.55, -0.38), (0.55, 0.38), (-0.1, 0.38)], col)
    p.poly([(0.42, -0.32), (0.5, -0.32), (0.5, 0.32), (0.42, 0.32)], WHITE, outline=False)
    p.circle(0.2, 0, 0.1, GOLD, outline=False)


def w_fist(p, col=STEEL, claws=False):
    p.circle(0.15, 0, 0.3, col)
    if claws:
        for y in (-0.18, 0, 0.18):
            p.line(0.4, y, 0.85, y * 1.4, STEEL, 0.08)


def w_spear(p, length=2.0, banner=None):
    p.line(-0.4, 0, length, 0, WOOD, 0.13)
    p.poly([(length - 0.05, -0.18), (length + 0.45, 0), (length - 0.05, 0.18)], STEEL)
    if banner:
        p.poly([(length - 0.25, 0.08), (length - 0.85, 0.08), (length - 0.85, 0.7), (length - 0.55, 0.5),
                (length - 0.25, 0.7)], banner)


def w_dagger(p, blade=STEEL, poison=False):
    p.line(-0.15, 0, 0.1, 0, WOOD, 0.18)
    p.poly([(0.1, -0.09), (0.75, 0), (0.1, 0.09)], (150, 230, 80) if poison else blade)


def w_shuriken(p):
    pts = []
    for i in range(8):
        rr = 0.42 if i % 2 == 0 else 0.13
        a = math.radians(i * 45)
        pts.append((0.45 + math.cos(a) * rr, math.sin(a) * rr))
    p.poly(pts, STEEL)


def w_axe(p, big=False):
    L = 1.5 if big else 1.2
    p.line(-0.3, 0, L, 0, WOOD, 0.16)
    h = 0.6 if big else 0.45
    p.poly([(L - 0.5, -0.05), (L - 0.65, -h), (L - 0.05, -h * 0.9), (L, -0.05)], STEEL)
    if big:
        p.poly([(L - 0.5, 0.05), (L - 0.65, h), (L - 0.05, h * 0.9), (L, 0.05)], STEEL)


def w_shield(p, col, emblem=None):
    p.circle(0, 0, 0.5, col)
    p.circle(0, 0, 0.18, emblem or GOLD, outline=False)


# ---------------------------------------------------------------------------
# Definição de cada classe: (chapéu, arma, segunda mão)
# ---------------------------------------------------------------------------
STYLE = {
    "freelancer": (lambda p: hat_band(p, (70, 110, 200)), lambda p: w_sword(p, length=1.0), None),
    "archer": (lambda p: hat_cap(p, (60, 140, 60)), lambda p: w_bow(p), None),
    "bard": (lambda p: hat_cavalier(p, (170, 60, 120), (250, 230, 110)), lambda p: w_bow(p, 0.85), None),
    "hunter": (lambda p: hat_hood(p, (70, 110, 50), pointed=False), lambda p: w_bow(p, 1.25), None),
    "thaumaturge": (lambda p: hat_wizard(p, (190, 80, 40), band=GOLD), lambda p: w_staff(p, (255, 140, 60)), None),
    "black_mage": (lambda p: hat_wizard(p, (45, 45, 120), tall=1.8, brim=1.45), lambda p: w_staff(p, (120, 90, 255)),
                   None),
    "time_mage": (lambda p: hat_wizard(p, (130, 90, 200), band=GOLD, star=True),
                  lambda p: w_staff(p, None, hourglass=True), None),
    "arcanist": (lambda p: hat_hood(p, (110, 70, 170), gem=(255, 230, 120)), lambda p: w_book(p, (110, 60, 160)), None),
    "summoner": (lambda p: hat_hood(p, (150, 50, 90), horn=(255, 230, 200)), lambda p: w_book(p, (160, 40, 70)), None),
    "scholar": (lambda p: hat_mortarboard(p, (40, 40, 60)), lambda p: w_book(p, (60, 120, 170)), None),
    "pugilist": (lambda p: hat_band(p, (210, 50, 50)), lambda p: w_fist(p), lambda p: w_fist(p)),
    "monk": (lambda p: hat_band(p, (240, 140, 40), tails=False, knot=(60, 40, 30)), lambda p: w_fist(p, claws=True),
             lambda p: w_fist(p, claws=True)),
    "white_monk": (lambda p: hat_band(p, WHITE), lambda p: w_fist(p, GOLD), lambda p: w_fist(p, GOLD)),
    "lancer": (lambda p: hat_helmet(p, (150, 160, 175)), lambda p: w_spear(p), None),
    "dragoon": (lambda p: hat_helmet(p, (60, 90, 170), extra="dragon"), lambda p: w_spear(p, 2.3), None),
    "templar": (lambda p: hat_helmet(p, (220, 220, 230), extra="cross"), lambda p: w_spear(p, 1.9, (240, 240, 250)),
                None),
    "rogue": (lambda p: hat_hood(p, (60, 70, 70), pointed=False), lambda p: w_dagger(p), lambda p: w_dagger(p)),
    "ninja": (lambda p: hat_band(p, (40, 40, 60)), lambda p: w_shuriken(p), lambda p: w_dagger(p)),
    "assassin": (lambda p: hat_hood(p, (50, 30, 45)), lambda p: w_dagger(p, poison=True),
                 lambda p: w_dagger(p, poison=True)),
    "conjurer": (lambda p: hat_circlet(p, GOLD, (90, 210, 160)), lambda p: w_staff(p, (90, 210, 160)), None),
    "white_mage": (lambda p: hat_hood(p, (245, 245, 250), trim=RED), lambda p: w_staff(p, (255, 250, 200)), None),
    "bishop": (lambda p: hat_mitre(p, (245, 245, 250)), lambda p: w_staff(p, None, cross=True), None),
    "gladiator": (lambda p: hat_helmet(p, (170, 170, 180), extra="crest"), lambda p: w_sword(p),
                  lambda p: w_shield(p, (150, 90, 50))),
    "paladin": (lambda p: hat_helmet(p, (230, 210, 140), extra="halo", visor=True), lambda p: w_sword(p, (255, 245, 200)),
                lambda p: w_shield(p, (240, 240, 250), RED)),
    "spellblade": (lambda p: hat_circlet(p, (200, 200, 220), (255, 90, 200), wings=True),
                   lambda p: w_sword(p, (255, 130, 230), 1.45), None),
    "marauder": (lambda p: hat_helmet(p, (110, 90, 80), extra="horns"), lambda p: w_axe(p), None),
    "warrior": (lambda p: hat_helmet(p, (160, 160, 170), extra="plume", visor=True), lambda p: w_axe(p, big=True), None),
    "berserker": (lambda p: hat_pelt(p, (120, 110, 100)), lambda p: w_axe(p), lambda p: w_axe(p)),
    "freelancer_t2": (lambda p: hat_band(p, (200, 150, 60), knot=GOLD), lambda p: w_sword(p, length=1.45),
                      lambda p: w_axe(p)),
    "warfarer": (lambda p: hat_circlet(p, GOLD, (255, 120, 60), wings=True), lambda p: w_sword(p, (255, 220, 150), 1.5),
                 lambda p: w_shield(p, (180, 120, 40), GOLD)),
}


FRONT_GRIP = {"archer", "bard", "hunter"}


def draw_class_icon(s, cid, center, r, facing=(1, 0), body=None, outline=WHITE, outline_w=None, eye=True, who=None,
                    shadow=None, look=None, walk=None, member=None):
    """Herói em pixel art: gato com o chapéu/capacete e a arma da classe (cats.py).

    look: aparência do gato (Member.look); who: nome (aparência fixa quando não há look); outline amarelo = herói (marcador dourado sob os pés)."""
    import cats
    if look is None:   # sem aparência própria: fixa pelo nome (ou pela classe)
        look = cats.look_from_name(who if who is not None else cid)
    if shadow is None:
        shadow = r >= 11
    c = V(center)
    if shadow and outline is not None and tuple(outline)[:3] in HERO_MARK:
        mk = pygame.Surface((int(r * 2.6), int(r * 0.9)), pygame.SRCALPHA)
        pygame.draw.ellipse(mk, (*tuple(outline)[:3], 150), mk.get_rect(), 2)
        s.blit(mk, (c.x - mk.get_width() / 2, c.y + r * 1.05 - mk.get_height() / 2))
    gear = None
    if member is not None:   # roupa, calça e bota do ferreiro mudam as cores do gato
        import crafting
        gear = crafting.gear_colors(member)
    cats.draw_cat(s, cid, c, r, facing, look, shadow=shadow, walk=walk, gear=gear)


HERO_MARK = {(250, 210, 70), (255, 215, 80), (240, 200, 60), (255, 220, 90)}


_OVER = {}


def _pixel_overlay(key, r, draw):
    """Desenho por cima de um inimigo (chapéu do elite, armas do chefão) na mesma grade de pixel art dos sprites:
    desenhado em baixa resolução, pixelizado uma vez e guardado em cache."""
    surf = _OVER.get(key)
    if surf is None:
        import pixel
        pf = max(pixel.PX, int(round(r / 7.5)))
        R = r / pf
        size = int(R * 7) + 6
        low = pygame.Surface((size, size), pygame.SRCALPHA)
        draw(low, (size / 2, size / 2), R)
        surf = pixel.pixelize(low, pf)
        if len(_OVER) > 2000:
            _OVER.clear()
        _OVER[key] = surf
    return surf


def _blit_center(s, surf, center):
    s.blit(surf, (center[0] - surf.get_width() / 2, center[1] - surf.get_height() / 2))


def draw_dual_weapons(s, cids, center, r, facing=(1, 0)):
    """Armas de duas classes, uma em cada mão (usado no chefão de 2 classes)."""
    f = V(facing)
    if f.length_squared() < 1e-6:
        f = V(1, 0)
    f = f.normalize()
    ang = int(round(math.degrees(math.atan2(f.y, f.x)) / 22.5)) * 22.5   # 16 direções (cache)
    cids = tuple(cids[:2])

    def draw(low, c, R):
        fa = V(math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        for i, cid in enumerate(cids):
            weapon = STYLE.get(cid, (None, None, None))[1]
            if not weapon:
                continue
            side = 1 if i == 0 else -1
            hand = V(c) + fa.rotate(65 * side) * R * 1.02
            weapon(_Pen(low, hand, R * 0.95, ang - 35 * side))
    _blit_center(s, _pixel_overlay(("dual", cids, int(r), ang), r, draw), center)


def draw_class_hat(s, cid, center, r):
    """Só o chapéu da classe, sobre algo de raio r centrado em center (usado nos inimigos de elite)."""
    hat = STYLE.get(cid, (None, None, None))[0]
    if hat:
        _blit_center(s, _pixel_overlay(("hat", cid, int(r)), r, lambda low, c, R: hat(_Pen(low, V(c), R))), center)
