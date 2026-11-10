"""Inimigos e chefões do Inferno (0.0.31).

Mesma linguagem visual dos outros biomas (creatures.py / beasts.py): proporções "chibi", cabeça grande, patas
grossas; os humanoides são gatos (demônios-gato com chifres). Coordenadas em unidades do raio (_Pen de icons.py),
olhando para a direita; espaço até ±2,4. Registrados em enemy_sprites.DRAWERS.
"""
import math

from icons import _arc, _shade, OUT
import cat_parts as cp
from beasts import oval, eye, limb, crown, _step
from creatures import _quad

WHITE = (240, 240, 245)
GOLD = (235, 195, 70)
FIRE = (255, 140, 40)
FIRE_L = (255, 220, 110)
HORN = (60, 40, 40)
BONE = (230, 222, 205)


def _flame(p, x, y, h, w, frame, col=FIRE, core=FIRE_L, lean=0.0):
    """Labareda: duas pontas tremendo + miolo claro."""
    f = 0.12 if frame % 2 else -0.08
    p.poly([(x - w, y), (x - w * 0.4 + lean, y - h * 0.65 - f * h), (x + lean * 1.3, y - h - f * h * 0.5),
            (x + w * 0.5 + lean, y - h * 0.55 + f * h), (x + w, y)], col, outline=False)
    p.poly([(x - w * 0.45, y), (x + lean * 0.8, y - h * 0.6), (x + w * 0.45, y)], core, outline=False)


def _horns(p, hx, hy, hr, col=HORN, big=False):
    """Chifres curvos e grossos de demônio (saem do alto da cabeça e curvam para fora)."""
    k = 1.3 if big else 1.0
    for sx in (-1, 1):
        bx, by = hx + hr * 0.42 * sx, hy - hr * 0.72
        pts = [(bx - hr * 0.24 * sx, by + hr * 0.1), (bx - hr * 0.12 * sx, by - hr * 0.42 * k),
               (bx + hr * 0.22 * sx, by - hr * 0.78 * k), (bx + hr * 0.6 * sx, by - hr * 0.8 * k),
               (bx + hr * 0.36 * sx, by - hr * 0.52 * k), (bx + hr * 0.24 * sx, by - hr * 0.2 * k),
               (bx + hr * 0.3 * sx, by + hr * 0.14)]
        p.poly(pts, col)
        p.line(bx, by - hr * 0.3 * k, bx + hr * 0.25 * sx, by - hr * 0.62 * k, _shade(col, 1.7), 0.04)


def _bat_wings(p, col, frame, x=0.0, y=-0.2, span=1.0, up=0.0):
    """Asas de morcego atrás do corpo."""
    f = 0.25 if frame % 2 else -0.05
    wing, bone = _shade(col, 0.75), _shade(col, 0.45)
    for sx in (-1, 1):
        sh = (x + 0.25 * sx, y)
        tips = [(x + 0.7 * sx * span, y - (0.95 + up) * span + f), (x + 1.35 * sx * span, y - (0.75 + up) * span + f),
                (x + 1.7 * sx * span, y - 0.15 * span + f * 0.6)]
        pts = [sh, tips[0], tips[1], tips[2], (x + 1.3 * sx * span, y + 0.15 * span), (x + 0.95 * sx * span,
               y + 0.05 * span), (x + 0.6 * sx * span, y + 0.35 * span)]
        p.poly(pts, wing)
        for t in tips:
            p.line(sh[0], sh[1], t[0], t[1], bone, 0.05)


def _spade_tail(p, col, base=(-0.6, 0.55), sway=0.0):
    pts = [base, (base[0] - 0.55, base[1] + 0.1 + sway), (base[0] - 0.9, base[1] - 0.25 - sway),
           (base[0] - 0.95, base[1] - 0.65)]
    p.lines(pts, _shade(col, 0.7), 0.15)
    p.lines(pts, col, 0.09)
    tx, ty = pts[-1]
    p.poly([(tx - 0.18, ty + 0.05), (tx, ty - 0.3), (tx + 0.18, ty + 0.05), (tx, ty - 0.05)], col)


def _demon_head(p, hx, hy, hr, fur, eye_col, horn=HORN, big_horns=False, fangs=True, brow=True):
    cp.ears(p, hx, hy, hr, fur, inner=(140, 40, 50), spread=55, size=0.45)
    _horns(p, hx, hy, hr, horn, big_horns)
    p.circle(hx, hy, hr, fur)
    cp.slit_eye(p, hx - 0.2 * hr / 0.6, hy - 0.03, eye_col, 0.12 * hr / 0.6)
    cp.slit_eye(p, hx + 0.24 * hr / 0.6, hy - 0.03, eye_col, 0.12 * hr / 0.6)
    if brow:
        p.line(hx - 0.42 * hr / 0.6, hy - 0.24, hx - 0.08, hy - 0.12, OUT, 0.08)
        p.line(hx + 0.44 * hr / 0.6, hy - 0.24, hx + 0.1, hy - 0.12, OUT, 0.08)
    cp.muzzle(p, hx + 0.02, hy + 0.22 * hr / 0.6, 0.24 * hr / 0.6, nose=(60, 20, 25), whisker=_shade(fur, 0.55))
    if fangs:
        for x in (-0.06, 0.1):
            p.poly([(hx + x, hy + 0.3 * hr / 0.6), (hx + x + 0.035, hy + 0.4 * hr / 0.6),
                    (hx + x + 0.07, hy + 0.3 * hr / 0.6)], WHITE, outline=False)


# ===========================================================================
# Inimigos
# ===========================================================================
def draw_diabrete(p, col, frame, big=False):
    """Diabrete: gatinho-demônio voador, asas de morcego, chifrinhos, rabo de ponta de lança e tridente."""
    bob = -0.08 if frame % 2 else 0.06
    _bat_wings(p, col, frame, 0.0, -0.15 + bob, 0.95 if not big else 1.25)
    _spade_tail(p, col, (-0.5, 0.45 + bob), sway=_step(frame, 0.1))
    oval(p, 0.0, 0.35 + bob, 0.55, 0.45, col)                                   # corpinho
    oval(p, 0.05, 0.45 + bob, 0.3, 0.22, _shade(col, 1.3), outline=False)        # barriga
    for x in (-0.25, 0.25):                                                      # perninhas penduradas
        limb(p, [(x, 0.7 + bob), (x + 0.05, 1.05 + bob)], _shade(col, 0.8), 0.14)
    # tridente na mão da frente
    tc = GOLD if big else (110, 100, 100)
    p.line(0.55, 0.9 + bob, 0.95, -0.75 + bob, (90, 60, 40), 0.08)
    for dx in (-0.16, 0.0, 0.16):
        p.line(0.95 + dx, -0.72 + bob, 0.98 + dx * 1.1, -1.1 + bob, tc, 0.06)
    p.line(0.78, -0.72 + bob, 1.13, -0.72 + bob, tc, 0.07)
    limb(p, [(0.35, 0.25 + bob), (0.65, 0.35 + bob)], col, 0.13)
    _demon_head(p, 0.05, -0.45 + bob, 0.6, col, (255, 230, 80), fangs=True, brow=False)
    p.poly([(0.0, -0.18 + bob), (0.25, -0.12 + bob), (0.1, -0.05 + bob)], (60, 20, 25), outline=False)   # sorriso


def draw_cao_inferno(p, col, frame, heads=1):
    """Cão infernal: quadrúpede escuro de juba de fogo, olhos acesos, rachaduras de brasa e cauda em chamas."""
    if heads >= 3:   # Cérbero: mais duas cabeças (atrás e acima da principal), um pouco mais escuras
        hc = _shade(col, 0.8)
        for bx, by, sc in ((0.2, -1.05, 0.85), (0.95, -1.35, 0.8)):
            for x0 in (-0.2, 0.15):
                p.poly([(bx + x0 - 0.15, by - 0.3), (bx + x0, by - 0.8 * sc), (bx + x0 + 0.18, by - 0.34)], hc)
            limb(p, [(bx - 0.25, by + 0.4), (bx - 0.4, by + 0.9)], hc, 0.3)        # pescoço
            p.circle(bx, by, 0.5 * sc, hc)
            p.poly([(bx + 0.25, by - 0.05), (bx + 0.75 * sc, by + 0.02), (bx + 0.75 * sc, by + 0.24),
                    (bx + 0.25, by + 0.28)], _shade(hc, 1.35))
            p.circle(bx + 0.75 * sc, by + 0.07, 0.08, OUT, outline=False)
            eye(p, bx + 0.18, by - 0.1, (255, 170, 40), 0.12)
            p.line(bx + 0.02, by - 0.27, bx + 0.32, by - 0.18, OUT, 0.06)
            _flame(p, bx - 0.35, by + 0.15, 0.4, 0.12, frame)
    hx, hy, st = _quad(p, col, frame, (255, 170, 40), head=0.6, snout=0.5, ear="up", tail="thin",
                       belly=_shade(col, 1.5))
    for (x1, y1, x2, y2) in ((-0.55, 0.0, -0.3, 0.3), (0.0, -0.1, 0.2, 0.25), (-0.2, 0.35, 0.1, 0.45)):
        p.line(x1, y1, x2, y2, FIRE, 0.06)                                       # rachaduras de brasa
    for k in range(4):                                                           # juba de fogo no pescoço e costas
        _flame(p, hx - 0.65 + k * 0.28 - 0.5, hy + 0.35 - (0.1 if k else 0), 0.55 - k * 0.06, 0.15, frame + k)
    _flame(p, -1.6, -0.55, 0.5, 0.14, frame + 1, lean=-0.1)                       # ponta do rabo
    p.poly([(hx + 0.6, hy + 0.3), (hx + 0.66, hy + 0.48), (hx + 0.72, hy + 0.3)], WHITE, outline=False)   # canino
    p.line(hx + 0.05, hy - 0.3, hx + 0.38, hy - 0.2, OUT, 0.07)
    if heads >= 3:   # Cérbero: coleira de espinhos
        for k in range(3):
            x = hx - 0.7 + k * 0.25
            p.poly([(x, hy + 0.55), (x + 0.06, hy + 0.35), (x + 0.12, hy + 0.55)], (170, 170, 180))


def draw_demonio(p, col, frame, armor=False, eye_col=(255, 220, 60)):
    """Demônio chifrudo: gato-demônio grandão e musculoso, chifres de carneiro, tanga, asinhas e um machado."""
    st = _step(frame, 0.1)
    dark, light = _shade(col, 0.68), _shade(col, 1.25)
    _bat_wings(p, col, frame, 0.0, -0.45, 0.8, up=0.1)
    _spade_tail(p, col, (-0.6, 0.75), sway=st)
    for x, s in ((-0.38, st), (0.4, -st)):                                       # pernas grossas com cascos
        limb(p, [(x, 0.6), (x + s, 1.25)], dark, 0.32)
        p.poly([(x + s - 0.22, 1.25), (x + s + 0.25, 1.25), (x + s + 0.2, 1.45), (x + s - 0.2, 1.45)], HORN)
    p.poly([(-0.85, -0.45), (0.85, -0.45), (0.7, 0.75), (-0.7, 0.75)], col)       # tronco
    p.line(-0.05, -0.3, -0.05, 0.45, dark, 0.05)                                  # peitoral
    p.line(-0.5, 0.05, 0.4, 0.05, dark, 0.04)
    p.poly([(-0.72, 0.55), (0.72, 0.55), (0.45, 1.0), (0.0, 0.85), (-0.45, 1.0)], (70, 45, 35))   # tanga
    if armor:   # ombreiras e peitoral de obsidiana
        for sx in (-1, 1):
            p.poly([(0.55 * sx, -0.55), (1.15 * sx, -0.5), (1.2 * sx, -0.1), (0.7 * sx, -0.05)], (55, 45, 60))
            p.poly([(0.85 * sx, -0.55), (1.0 * sx, -0.85), (1.05 * sx, -0.52)], (200, 190, 200))
        p.poly([(-0.6, -0.4), (0.6, -0.4), (0.5, 0.4), (-0.5, 0.4)], (65, 52, 70))
        p.circle(0.0, 0.0, 0.14, FIRE, outline=False)
    # braço de trás e braço da frente com o machado
    limb(p, [(-0.75, -0.3), (-1.05, 0.2), (-0.95, 0.55)], col, 0.24)
    sw = 0.12 if frame % 2 else -0.08
    limb(p, [(0.75, -0.3), (1.15, 0.05), (1.35, -0.3 + sw)], col, 0.24)
    p.line(1.35, 0.6 + sw, 1.45, -1.25 + sw, (90, 60, 40), 0.1)                   # cabo
    blade = (190, 190, 200) if not armor else (60, 50, 70)
    p.poly([(1.45, -1.25 + sw), (2.15, -1.45 + sw), (2.3, -0.75 + sw), (1.45, -0.7 + sw)], blade)
    if armor:
        p.line(1.6, -1.15 + sw, 2.15, -1.25 + sw, FIRE, 0.05)
    _demon_head(p, 0.05, -0.95, 0.55, col, eye_col, big_horns=True)


def draw_salamandra(p, col, frame):
    """Salamandra: lagarto chibi alaranjado, crista de fogo nas costas, manchas brilhando e rabo comprido."""
    st = _step(frame, 0.12)
    wig = 0.1 if frame % 2 else -0.1
    dark, light = _shade(col, 0.6), _shade(col, 1.3)
    p.lines([(-0.6, 0.35), (-1.2, 0.45 + wig), (-1.7, 0.2 - wig), (-2.05, 0.35)], dark, 0.28)   # rabo
    p.lines([(-0.6, 0.35), (-1.2, 0.45 + wig), (-1.7, 0.2 - wig), (-2.05, 0.35)], col, 0.2)
    _flame(p, -2.05, 0.3, 0.45, 0.12, frame, lean=-0.1)
    limb(p, [(-0.45, 0.4), (-0.6 + st, 0.85)], dark, 0.2)                          # patas de longe
    limb(p, [(0.45, 0.4), (0.4 - st, 0.85)], dark, 0.2)
    oval(p, -0.05, 0.25, 0.85, 0.42, col)                                         # corpo baixo e comprido
    oval(p, 0.1, 0.42, 0.55, 0.16, light, outline=False)                           # barriga
    for k in range(4):                                                            # crista de fogo
        _flame(p, -0.6 + k * 0.35, -0.08 - (0.06 if k in (1, 2) else 0), 0.55 if k in (1, 2) else 0.4, 0.15,
               frame + k)
    for x, y in ((-0.5, 0.18), (0.0, 0.1), (0.38, 0.25)):                          # manchas acesas
        p.circle(x, y, 0.08, FIRE_L, outline=False)
    for x, s in ((-0.3, -st), (0.55, st)):                                         # patas de perto
        limb(p, [(x, 0.45), (x + s, 0.88)], col, 0.22)
        oval(p, x + s + 0.06, 0.92, 0.15, 0.08, light)
    hx, hy = 0.95, -0.05
    p.circle(hx, hy, 0.48, col)                                                   # cabeça
    p.poly([(hx + 0.2, hy - 0.2), (hx + 0.85, hy - 0.05), (hx + 0.85, hy + 0.2), (hx + 0.2, hy + 0.3)], col)
    p.line(hx + 0.3, hy + 0.17, hx + 0.82, hy + 0.12, dark, 0.05)                  # boca
    p.circle(hx + 0.78, hy - 0.04, 0.05, OUT, outline=False)
    eye(p, hx + 0.12, hy - 0.15, (255, 240, 120), 0.14)


def draw_bruxo(p, col, frame, eye_col=(255, 120, 60)):
    """Bruxo infernal: gato-demônio de manto roxo, chifres furando o capuz, livro e uma bola de fogo na mão."""
    bob = 0.06 if frame % 2 else -0.04
    dark = _shade(col, 0.65)
    fur = (45, 25, 35)
    cp.tail(p, fur, base=(-0.8, 0.9), tip=_shade(fur, 0.8))
    pts = [(-0.75, -0.25 + bob), (0.75, -0.25 + bob)]                             # manto que vira fumaça
    for i in range(6):
        x = 0.8 - i * 0.32
        pts.append((x * 0.95, 1.25 + (0.18 if i % 2 else 0) - i * 0.02))
    p.poly(pts, col)
    p.line(0.0, -0.2 + bob, 0.0, 1.2, (230, 90, 50), 0.08)                         # faixa de brasa
    for x in (-0.4, 0.4):
        p.line(x, 0.0 + bob, x * 0.85, 1.1, dark, 0.05)
    p.poly([(-0.95, 0.2 + bob), (-0.55, 0.05 + bob), (-0.45, 0.6 + bob), (-0.9, 0.7 + bob)], (110, 60, 40))   # livro
    p.line(-0.72, 0.15 + bob, -0.68, 0.62 + bob, (230, 200, 120), 0.04)
    limb(p, [(0.6, 0.0 + bob), (1.0, 0.15 + bob), (1.25, -0.1 + bob)], col, 0.2)  # braço com a bola de fogo
    fl = 0.08 if frame % 2 else -0.08
    p.circle(1.4, -0.35 + bob, 0.36 + fl * 0.5, (255, 110, 40), outline=False)
    p.circle(1.4, -0.35 + bob, 0.22, FIRE_L, outline=False)
    _flame(p, 1.4, -0.6 + bob, 0.45, 0.18, frame)
    hx, hy, hr = 0.0, -0.72 + bob, 0.6
    _horns(p, hx, hy, hr, (40, 25, 30), big=True)
    p.circle(hx, hy, hr * 1.12, col)                                              # capuz
    p.poly(_arc(hx, hy - 0.05, hr * 1.12, 200, 340, 8), dark, outline=False)        # sombra do capuz
    p.circle(hx + 0.04, hy + 0.08, hr * 0.78, fur, outline=False)                  # rosto
    cp.slit_eye(p, hx - 0.17, hy + 0.04, (255, 200, 60), 0.19)
    cp.slit_eye(p, hx + 0.25, hy + 0.04, (255, 200, 60), 0.19)
    cp.muzzle(p, hx + 0.05, hy + 0.24, 0.24, nose=(30, 15, 20), whisker=(255, 180, 140))


# ===========================================================================
# Chefões
# ===========================================================================
def draw_principe_diabrete(p, col, frame):
    """Príncipe Diabrete: o diabrete de capa, coroa e tridente de ouro (e asas maiores)."""
    p.poly([(-0.45, -0.1), (-1.1, 1.05), (0.45, 1.05), (0.4, -0.1)], (90, 20, 40))   # capa
    draw_diabrete(p, col, frame, big=True)
    bob = -0.08 if frame % 2 else 0.06
    crown(p, 0.05, -1.05 + bob, 0.36, 0.34)


def draw_cerbero(p, col, frame):
    """Cérbero: o cão infernal de três cabeças e coleira de espinhos."""
    draw_cao_inferno(p, col, frame, heads=3)


def draw_colosso_magma(p, col, frame):
    """Colosso de Magma: golem de basalto rachado com lava escorrendo, chifres e fogo na cabeça."""
    st = _step(frame, 0.08)
    rock, dark = (70, 55, 55), (45, 35, 35)
    for x, s in ((-0.45, st), (0.4, -st)):                                         # pernas
        p.poly([(x - 0.27, 0.6), (x + 0.27, 0.6), (x + 0.3 + s, 1.38), (x - 0.3 + s, 1.38)], dark)
        p.line(x - 0.05 + s * 0.5, 0.75, x + 0.08 + s * 0.8, 1.2, FIRE, 0.05)
    for sx in (-1, 1):                                                             # braços e punhos de lava
        p.poly([(0.72 * sx, -0.6), (1.2 * sx, -0.4), (1.3 * sx, 0.35 + st * sx), (0.85 * sx, 0.42)], dark)
        p.poly([(0.95 * sx, 0.3 + st * sx), (1.6 * sx, 0.35 + st * sx), (1.65 * sx, 1.0 + st * sx),
                (0.95 * sx, 1.05 + st * sx)], rock)
        p.line(1.05 * sx, 0.55 + st * sx, 1.5 * sx, 0.7 + st * sx, FIRE, 0.07)
    p.poly([(-0.9, -0.7), (-0.3, -0.9), (0.4, -0.9), (0.95, -0.6), (0.8, 0.72), (-0.8, 0.72)], rock)   # tronco
    for (x1, y1, x2, y2) in ((-0.55, -0.45, -0.2, 0.15), (-0.2, 0.15, 0.1, 0.55), (0.35, -0.65, 0.55, -0.1),
                             (0.1, -0.3, 0.45, 0.2)):
        p.line(x1, y1, x2, y2, FIRE, 0.08)
        p.line(x1, y1, x2, y2, FIRE_L, 0.03)
    p.circle(0.0, 0.0, 0.25, (255, 120, 40), outline=False)                        # núcleo
    p.circle(0.0, 0.0, 0.13, FIRE_L, outline=False)
    p.poly([(-0.32, -0.9), (-0.28, -1.35), (0.38, -1.37), (0.42, -0.9)], _shade(rock, 1.15))   # cabeça
    for sx in (-1, 1):                                                             # chifres
        p.poly([(0.05 + 0.3 * sx, -1.3), (0.15 + 0.6 * sx, -1.75), (0.05 + 0.42 * sx, -1.25)], HORN)
    p.line(-0.15, -1.12, 0.0, -1.12, FIRE_L, 0.08)                                 # olhos
    p.line(0.12, -1.12, 0.27, -1.12, FIRE_L, 0.08)
    _flame(p, 0.05, -1.35, 0.7, 0.28, frame)


def draw_general_demonio(p, col, frame):
    """General Demônio: demônio de armadura de obsidiana, olhos de brasa e machado negro."""
    p.poly([(-0.55, -0.6), (-1.2, 1.3), (0.2, 1.3), (0.3, -0.6)], (120, 25, 30))    # capa
    draw_demonio(p, col, frame, armor=True, eye_col=(255, 90, 40))


def draw_rei_demonio(p, col, frame):
    """Rei Demônio: gato-demônio enorme de asas abertas, coroa de chifres e ouro, capa real e espada em chamas."""
    st = _step(frame, 0.08)
    fur = (70, 30, 45)
    _bat_wings(p, (60, 25, 45), frame, 0.0, -0.55, 1.3, up=0.2)
    p.poly([(-0.75, -0.55), (-1.35, 1.4), (1.2, 1.4), (0.75, -0.55)], (110, 25, 60))   # capa real
    p.poly([(-0.75, -0.55), (0.75, -0.55), (0.6, -0.25), (-0.6, -0.25)], (240, 230, 225))   # gola de arminho
    _spade_tail(p, fur, (-0.7, 0.9), sway=st)
    for x, s in ((-0.32, st), (0.35, -st)):                                         # pernas
        limb(p, [(x, 0.75), (x + s, 1.3)], (45, 30, 40), 0.28)
        p.poly([(x + s - 0.2, 1.3), (x + s + 0.24, 1.3), (x + s + 0.2, 1.48), (x + s - 0.18, 1.48)], (30, 22, 28))
    p.poly([(-0.65, -0.3), (0.65, -0.3), (0.55, 0.85), (-0.55, 0.85)], (55, 40, 60))   # armadura
    p.line(-0.55, 0.45, 0.55, 0.45, GOLD, 0.07)
    p.circle(0.0, 0.1, 0.15, (200, 40, 80), outline=False)                          # joia
    # espada em chamas
    sw = 0.1 if frame % 2 else -0.06
    limb(p, [(0.6, -0.15), (1.0, 0.15), (1.25, -0.05 + sw)], fur, 0.22)
    p.line(1.15, 0.05 + sw, 1.42, -0.15 + sw, GOLD, 0.1)                            # guarda
    p.poly([(1.22, -0.1 + sw), (1.5, -0.25 + sw), (2.1, -1.75 + sw), (1.9, -1.85 + sw)], (60, 40, 60))
    for k in range(3):
        _flame(p, 1.55 + k * 0.17, -0.45 - k * 0.45 + sw, 0.45, 0.13, frame + k, lean=0.12)
    hx, hy, hr = 0.0, -0.95, 0.62
    _demon_head(p, hx, hy, hr, fur, (255, 60, 60), horn=(35, 25, 30), big_horns=True)
    crown(p, hx, hy - hr * 0.8, 0.42, 0.42, gem=(255, 60, 60))


DRAWERS = {
    "diabrete": draw_diabrete, "cao_inferno": draw_cao_inferno, "demonio": draw_demonio,
    "salamandra": draw_salamandra, "bruxo": draw_bruxo,
    "principe_diabrete": draw_principe_diabrete, "cerbero": draw_cerbero, "colosso_magma": draw_colosso_magma,
    "general_demonio": draw_general_demonio, "rei_demonio": draw_rei_demonio,
}
FLIPPABLE = {"diabrete", "cao_inferno", "demonio", "salamandra", "bruxo", "principe_diabrete", "cerbero",
             "general_demonio", "rei_demonio"}
FRAMES = {k: 2 for k in DRAWERS}
