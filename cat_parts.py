"""Partes de gato para os inimigos humanoides (zumbi, esqueleto, bandido, padre, médico da peste...).

Os monstros com forma de gente viram "gatos": orelhas pontudas na cabeça (ou no capuz/elmo), focinho com
bigodes e uma cauda. Animais e monstros (morcego, lobo, aranha, gárgula, gosma...) continuam como eram.
Coordenadas em unidades do raio do sprite (_Pen de icons.py), olhando para a direita.
"""
import math

from icons import _shade

PINK = (220, 130, 140)
WHISKER = (235, 230, 220)


def ears(p, cx, cy, rad, col, inner=PINK, spread=40, size=0.62, tilt=0.0):
    """Duas orelhas triangulares no alto de uma cabeça redonda (centro cx, cy e raio rad)."""
    for sx in (-1, 1):
        a = math.radians(-90 + sx * spread + tilt)
        a0 = math.radians(-90 + sx * (spread - 24) + tilt)
        a1 = math.radians(-90 + sx * (spread + 26) + tilt)
        tip = (cx + math.cos(a) * rad * (1 + size), cy + math.sin(a) * rad * (1 + size))
        b0 = (cx + math.cos(a0) * rad * 0.92, cy + math.sin(a0) * rad * 0.92)
        b1 = (cx + math.cos(a1) * rad * 0.92, cy + math.sin(a1) * rad * 0.92)
        p.poly([b0, tip, b1], col)
        if inner:
            mid = ((b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2)
            it = (mid[0] + (tip[0] - mid[0]) * 0.72, mid[1] + (tip[1] - mid[1]) * 0.72)
            ib0 = (mid[0] + (b0[0] - mid[0]) * 0.5, mid[1] + (b0[1] - mid[1]) * 0.5)
            ib1 = (mid[0] + (b1[0] - mid[0]) * 0.5, mid[1] + (b1[1] - mid[1]) * 0.5)
            p.poly([ib0, it, ib1], inner, outline=False)


def muzzle(p, x, y, w=0.28, nose=PINK, whisker=WHISKER):
    """Narizinho triangular e bigodes (centro do focinho em x, y)."""
    p.poly([(x - 0.07, y - 0.04), (x + 0.07, y - 0.04), (x, y + 0.05)], nose, outline=False)
    for sy in (-0.06, 0.06):
        p.line(x + 0.12, y + sy, x + 0.12 + w, y + sy * 2.2, whisker, 0.035)
        p.line(x - 0.12, y + sy, x - 0.12 - w, y + sy * 2.2, whisker, 0.035)


def tail(p, col, base=(-0.7, 0.75), up=True, w=0.17, tip=None):
    """Cauda curvada saindo de trás do corpo."""
    bx, by = base
    pts = [(bx, by), (bx - 0.55, by - 0.05), (bx - 0.85, by - 0.4), (bx - 0.85, by - 0.85)] if up else \
        [(bx, by), (bx - 0.55, by + 0.15), (bx - 0.95, by + 0.1)]
    p.lines(pts, _shade(col, 0.7), w + 0.08)
    p.lines(pts, col, w)
    if tip:
        p.circle(pts[-1][0], pts[-1][1], w * 0.7, tip, outline=False)


def bone_tail(p, col, base=(-0.6, 0.85)):
    """Cauda de ossinhos (esqueletos)."""
    bx, by = base
    for k in range(5):
        a = math.radians(200 - k * 22)
        x = bx - 0.25 - k * 0.18
        y = by - k * k * 0.04
        p.circle(x, y, 0.09, col)


DEAD = [False]   # True enquanto desenha o sprite do inimigo morto (olhos viram X)
X_COL = (30, 20, 26)


def x_eye(p, x, y, rad):
    """Olho de morto: um X."""
    k = max(rad, 0.1) * 1.15
    w = max(0.05, rad * 0.45)
    p.line(x - k, y - k, x + k, y + k, X_COL, w)
    p.line(x - k, y + k, x + k, y - k, X_COL, w)


def slit_eye(p, x, y, col, rad=0.12):
    """Olho de gato: íris colorida com pupila em fenda."""
    if DEAD[0]:
        x_eye(p, x, y, rad)
        return
    p.circle(x, y, rad, col, outline=False)
    p.line(x, y - rad * 0.8, x, y + rad * 0.8, (20, 16, 24), max(0.03, rad * 0.35))
