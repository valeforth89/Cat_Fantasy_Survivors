"""Inimigos e chefões redesenhados sem o corpo de "bolinha" (que só fazia sentido no visual antigo).

Cada um tem silhueta própria: patas, tronco, pescoço, cauda... em vista de lado (olhando para a direita; o
jogo espelha quando andam para a esquerda). Os humanoides continuam sendo gatos (cat_parts.py).
Coordenadas em unidades do raio do inimigo (_Pen de icons.py); o sprite tem espaço até ±2,4.
Registrados em enemy_sprites.DRAWERS (substituem os desenhos antigos de mesmo nome).
"""
import math

from icons import _arc, _shade, OUT
import cat_parts as cp

WHITE = (240, 240, 245)
GOLD = (235, 195, 70)
GOLD_D = (170, 130, 40)
BONE = (230, 222, 205)


def oval(p, cx, cy, rx, ry, col, outline=True, a0=0, a1=360, n=18):
    p.poly(_arc(cx, cy, rx, a0, a1, n, ry), col, outline)


def eye(p, x, y, col, rad=0.12):
    if cp.DEAD[0]:
        cp.x_eye(p, x, y, rad)
        return
    p.circle(x, y, rad, col, outline=False)
    if p.r >= 12:
        p.circle(x + rad * 0.3, y - rad * 0.3, rad * 0.35, WHITE, outline=False)


def limb(p, pts, col, w=0.2):
    p.lines(pts, _shade(col, 0.7), w + 0.07)
    p.lines(pts, col, w)


def crown(p, x, y, w=0.45, h=0.4, col=GOLD, gem=(200, 40, 60)):
    pts = [(x - w, y), (x - w, y - h), (x - w * 0.5, y - h * 0.45), (x, y - h * 1.1), (x + w * 0.5, y - h * 0.45),
           (x + w, y - h), (x + w, y)]
    p.poly(pts, col)
    p.circle(x, y - h * 0.3, 0.08, gem, outline=False)


def _step(frame, a=0.12):
    return a if frame % 2 else -a


# ===========================================================================
# Floresta
# ===========================================================================
def draw_morcego(p, col, frame):
    """Morcego: asas de membrana com dedos, corpinho peludo, orelhonas e presas."""
    f = 0.0 if frame % 2 == 0 else 0.85
    wing, bone = _shade(col, 0.72), _shade(col, 0.45)
    for sx in (-1, 1):
        sh = (0.3 * sx, -0.15)
        tips = [(0.95 * sx, -1.05 + f), (1.7 * sx, -0.95 + f), (2.2 * sx, -0.3 + f * 0.6)]
        pts = [sh, tips[0], tips[1], tips[2], (1.75 * sx, 0.05 + f * 0.4), (1.35 * sx, -0.05 + f * 0.45),
               (1.0 * sx, 0.3 + f * 0.25), (0.6 * sx, 0.15), (0.35 * sx, 0.35)]
        p.poly(pts, wing)
        for t in tips:
            p.line(sh[0], sh[1], t[0], t[1], bone, 0.06)
    oval(p, 0, 0.2, 0.42, 0.55, col)                                          # corpinho
    p.line(-0.12, 0.72, -0.18, 0.9, bone, 0.07)                               # pezinhos
    p.line(0.12, 0.72, 0.18, 0.9, bone, 0.07)
    for sx in (-1, 1):                                                        # orelhonas
        p.poly([(0.08 * sx, -0.65), (0.45 * sx, -1.35), (0.5 * sx, -0.5)], col)
        p.poly([(0.2 * sx, -0.66), (0.42 * sx, -1.12), (0.44 * sx, -0.6)], (200, 120, 140), outline=False)
    p.circle(0, -0.42, 0.4, col)                                              # cabeça
    eye(p, -0.17, -0.48, (255, 70, 70), 0.11)
    eye(p, 0.17, -0.48, (255, 70, 70), 0.11)
    p.circle(0, -0.28, 0.12, _shade(col, 1.35), outline=False)               # focinho
    for sx in (-1, 1):
        p.poly([(0.05 * sx, -0.18), (0.11 * sx, 0.0), (0.16 * sx, -0.18)], WHITE, outline=False)


def draw_javali(p, col, frame, eye_col=(230, 50, 40)):
    """Javali de lado: corpo pesado, patas curtas, crina espetada, focinho achatado e presas."""
    st = _step(frame, 0.1)
    dark = _shade(col, 0.55)
    p.lines([(-1.2, -0.1), (-1.45, 0.05), (-1.4, 0.25)], dark, 0.07)               # rabinho
    for x, s in ((-0.75, st), (0.55, -st)):                                         # patas de longe
        limb(p, [(x, 0.35), (x + s, 1.05)], dark, 0.22)
    for i in range(7):                                                              # crina
        a = math.radians(205 + i * 20)
        bx, by = -0.1 + math.cos(a) * 1.05, 0.05 + math.sin(a) * 0.62
        p.poly([(bx - 0.12, by + 0.05), (bx - 0.05, by - 0.42), (bx + 0.12, by + 0.05)], dark)
    oval(p, -0.1, 0.05, 1.15, 0.68, col)                                            # corpo
    for x, s in ((-0.5, -st), (0.8, st)):                                           # patas de perto
        limb(p, [(x, 0.45), (x + s, 1.1)], col, 0.24)
        p.circle(x + s, 1.12, 0.12, OUT, outline=False)
    p.poly([(0.55, -0.55), (1.3, -0.3), (1.5, 0.3), (0.8, 0.55)], _shade(col, 1.05))   # cabeça
    oval(p, 1.5, 0.05, 0.16, 0.27, _shade(col, 1.35))                               # focinho
    p.circle(1.52, -0.02, 0.05, OUT, outline=False)
    p.circle(1.52, 0.12, 0.05, OUT, outline=False)
    p.poly([(1.2, 0.35), (1.05, -0.1), (1.32, 0.3)], WHITE)                          # presa
    p.poly([(0.7, -0.5), (0.8, -1.0), (1.0, -0.45)], col)                            # orelha
    eye(p, 1.05, -0.2, eye_col, 0.1)
    p.line(0.9, -0.36, 1.18, -0.3, OUT, 0.07)                                       # sobrancelha brava


def draw_ent(p, col, frame):
    """Ent Ancestral: tronco que anda sobre raízes, braços de galho e copa frondosa."""
    st = _step(frame, 0.1)
    bark = (115, 82, 52)
    dark = _shade(bark, 0.65)
    leaf, leaf2 = col, _shade(col, 0.7)
    for sx, s in ((-1, st), (1, -st)):                                              # raízes-pernas
        limb(p, [(0.3 * sx, 0.8), (0.65 * sx + s, 1.3), (0.95 * sx + s, 1.4)], bark, 0.2)
    for sx in (-1, 1):                                                              # braços de galho
        limb(p, [(0.4 * sx, -0.25), (1.15 * sx, -0.65), (1.6 * sx, -0.35)], bark, 0.15)
        p.line(1.15 * sx, -0.65, 1.35 * sx, -1.05, bark, 0.09)
        p.circle(1.65 * sx, -0.35, 0.28, leaf2)
        p.circle(1.35 * sx, -1.1, 0.24, leaf)
    p.poly([(-0.55, 1.0), (-0.42, -0.2), (-0.55, -0.9), (0.55, -0.9), (0.42, -0.2), (0.55, 1.0)], bark)   # tronco
    for x in (-0.3, 0.0, 0.28):                                                     # casca
        p.line(x, -0.75, x + 0.05, 0.85, dark, 0.05)
    for (x, y, r, c) in ((-0.65, -1.15, 0.52, leaf2), (0.65, -1.15, 0.52, leaf2), (0.0, -1.5, 0.66, leaf),
                         (-0.35, -1.0, 0.45, leaf), (0.4, -1.05, 0.45, leaf)):     # copa
        p.circle(x, y, r, c)
    for (x, y) in ((-0.25, -1.65), (0.3, -1.45), (-0.6, -1.25)):
        p.circle(x, y, 0.1, _shade(leaf, 1.35), outline=False)
    oval(p, 0, -0.35, 0.36, 0.2, (40, 28, 20), outline=False)                       # cavidade dos olhos
    eye(p, -0.15, -0.35, (255, 230, 90), 0.09)
    eye(p, 0.15, -0.35, (255, 230, 90), 0.09)
    oval(p, 0, 0.15, 0.18, 0.12, (40, 28, 20), outline=False)                       # boca oca
    p.circle(-0.3, 0.55, 0.12, (90, 140, 70), outline=False)                        # musgo


def draw_aranha(p, col, frame):
    """Rainha Aranha: abdômen grande com marca, tórax, oito patas articuladas, olhos e quelíceras."""
    sh = _step(frame, 0.12)
    leg, leg2 = _shade(col, 0.5), _shade(col, 0.38)
    for i in range(4):                                                              # patas de longe (para cima)
        bx = 0.3 + i * 0.12
        kx = -0.55 + i * 0.55
        limb(p, [(bx, -0.05), (kx, -0.95 + (sh if i % 2 else -sh)), (kx - 0.3 + i * 0.25, 0.1)], leg2, 0.09)
    oval(p, -0.65, 0.2, 0.92, 0.72, _shade(col, 0.85))                              # abdômen
    p.poly([(-0.85, -0.15), (-0.6, 0.05), (-0.85, 0.25), (-1.1, 0.05)], (200, 50, 60), outline=False)   # marca
    p.circle(-0.85, 0.5, 0.1, (200, 50, 60), outline=False)
    oval(p, 0.45, 0.0, 0.5, 0.4, col)                                               # tórax
    for i in range(4):                                                              # patas de perto (para baixo)
        bx = 0.25 + i * 0.13
        kx = -0.4 + i * 0.6
        limb(p, [(bx, 0.2), (kx, -0.2 + (-sh if i % 2 else sh)), (kx - 0.15 + i * 0.2, 1.05)], leg, 0.1)
    p.circle(0.95, -0.05, 0.28, _shade(col, 1.1))                                   # cabeça
    for (x, y) in ((1.0, -0.2), (1.12, -0.12), (0.9, -0.15), (1.05, 0.0)):
        eye(p, x, y, (255, 60, 60), 0.06)
    p.poly([(1.12, 0.1), (1.3, 0.35), (1.05, 0.2)], WHITE)                          # quelíceras
    p.poly([(0.98, 0.15), (1.08, 0.42), (0.9, 0.2)], WHITE)


# ===========================================================================
# Cidade Abandonada
# ===========================================================================
def _cat_torso(p, fur, shirt, frame, pants=(70, 58, 52), boots=(45, 35, 30), head=(0.08, -0.72, 0.55)):
    """Corpo de gato humanoide em pé: pernas, tronco com roupa e cauda (a cabeça é desenhada por quem chama)."""
    st = _step(frame, 0.1)
    cp.tail(p, fur, base=(-0.55, 0.6), tip=_shade(fur, 0.8))
    for x, s in ((-0.28, st), (0.3, -st)):
        limb(p, [(x, 0.7), (x + s, 1.3)], pants, 0.24)
        oval(p, x + s + 0.08, 1.38, 0.2, 0.1, boots)
    p.poly([(-0.6, -0.3), (0.62, -0.3), (0.5, 0.85), (-0.48, 0.85)], shirt)          # tronco
    return st


def draw_bruto(p, col, frame, eye_col=(60, 40, 30)):
    """Gato bandido brutamontes: colete de couro, lenço, juba no queixo, cicatriz e porrete com pregos."""
    vest = (100, 66, 44)
    st = _cat_torso(p, col, vest, frame)
    p.line(-0.48, 0.55, 0.5, 0.55, (50, 35, 25), 0.12)                              # cinto
    p.circle(0.0, 0.55, 0.07, GOLD, outline=False)
    limb(p, [(0.55, -0.15), (0.95, 0.25), (1.25, -0.05 + st)], col, 0.2)             # braço
    p.line(1.25, -0.05 + st, 1.55, -1.1 + st, (110, 75, 45), 0.2)                   # porrete
    for t in (0.35, 0.6, 0.85):
        x, y = 1.25 + 0.3 * t, -0.05 + st - 1.05 * t
        p.line(x - 0.12, y, x + 0.12, y, (170, 170, 180), 0.05)
    hx, hy, hr = 0.08, -0.72, 0.55
    cp.ears(p, hx, hy, hr, col, inner=(190, 120, 120), spread=42, size=0.55)
    p.circle(hx, hy, hr, col)                                                       # cabeça
    p.poly(_arc(hx, hy + 0.05, hr, 25, 155, 8), (90, 60, 45))                        # juba no queixo
    p.poly(_arc(hx, hy - 0.08, hr * 1.02, 195, 345, 10), (150, 40, 40))             # lenço
    p.line(hx - 0.5, hy - 0.2, hx - 0.85, hy + 0.05, (150, 40, 40), 0.1)
    eye(p, hx - 0.18, hy - 0.05, eye_col, 0.08)
    eye(p, hx + 0.22, hy - 0.05, eye_col, 0.08)
    p.line(hx + 0.08, hy - 0.2, hx + 0.36, hy - 0.14, OUT, 0.06)
    cp.muzzle(p, hx + 0.04, hy + 0.15, 0.24, nose=(150, 80, 90))
    p.line(hx + 0.3, hy + 0.05, hx + 0.42, hy + 0.3, (170, 90, 80), 0.04)            # cicatriz


def draw_lorde_bandido(p, col, frame):
    """Lorde Bandido: o brutamontes com chapéu de pena, tapa-olho e brinco de ouro."""
    p.poly([(-0.7, -0.25), (-1.05, 1.0), (0.2, 1.0), (0.3, -0.2)], (110, 30, 40))   # capa
    draw_bruto(p, col, frame)
    hx, hy = 0.08, -0.72
    p.poly([(hx - 0.95, hy - 0.4), (hx + 0.95, hy - 0.4), (hx + 0.65, hy - 0.62), (hx - 0.65, hy - 0.62)],
           (60, 40, 35))                                                            # aba
    p.poly(_arc(hx, hy - 0.62, 0.48, 180, 360, 8), (60, 40, 35))
    p.lines([(hx - 0.2, hy - 1.0), (hx - 0.7, hy - 1.4), (hx - 1.05, hy - 1.35)], (200, 60, 50), 0.1)   # pena
    for sx in (-1, 1):                                                              # orelhas furando a aba
        p.poly([(hx + 0.45 * sx, hy - 0.6), (hx + 0.78 * sx, hy - 1.05), (hx + 0.85 * sx, hy - 0.55)], col)
    p.circle(hx + 0.22, hy - 0.05, 0.13, (25, 20, 20), outline=False)               # tapa-olho
    p.line(hx - 0.1, hy - 0.3, hx + 0.55, hy - 0.05, (25, 20, 20), 0.04)
    p.circle(hx - 0.5, hy + 0.25, 0.07, GOLD)                                       # brinco


def draw_carnical(p, col, frame):
    """Gato carniçal: corcunda, pele pálida, trapos, braços compridos com garras e orelhas compridas."""
    dark = _shade(col, 0.6)
    reach = _step(frame, 0.1)
    rags = (80, 70, 60)
    cp.tail(p, col, base=(-0.7, 0.45), tip=dark)
    limb(p, [(-0.35, 0.55), (-0.15, 0.95), (-0.45 + reach, 1.35)], dark, 0.17)      # pernas dobradas
    limb(p, [(0.2, 0.6), (0.45, 0.95), (0.2 - reach, 1.35)], col, 0.17)
    p.poly([(-0.75, 0.0), (-0.45, -0.55), (0.35, -0.5), (0.55, 0.3), (0.3, 0.75), (-0.55, 0.7)], rags)   # tronco curvado
    p.poly([(-0.55, 0.7), (-0.4, 0.95), (-0.2, 0.72), (0.05, 0.98), (0.3, 0.75)], rags)
    for i in range(3):                                                              # vértebras
        p.circle(-0.55 + i * 0.25, -0.5 - i * 0.05, 0.07, dark, outline=False)
    for y in (-0.1, 0.25):                                                          # braços compridos
        limb(p, [(0.35, y), (1.05, y + 0.15 + reach), (1.45, y + 0.45 + reach)], col, 0.12)
        for k in (-0.12, 0.0, 0.12):
            p.line(1.45, y + 0.45 + reach, 1.65, y + 0.6 + reach + k, (230, 230, 210), 0.035)
    hx, hy = 0.6, -0.55
    cp.ears(p, hx, hy, 0.45, col, inner=dark, spread=50, size=0.8)
    p.circle(hx, hy, 0.45, col)                                                     # cabeça projetada
    eye(p, hx + 0.2, hy - 0.08, (200, 255, 120), 0.09)
    eye(p, hx - 0.08, hy - 0.1, (200, 255, 120), 0.08)
    p.poly([(hx + 0.05, hy + 0.2), (hx + 0.45, hy + 0.15), (hx + 0.25, hy + 0.35)], (60, 30, 30))   # boca
    for x in (0.12, 0.22, 0.32):
        p.line(hx + x, hy + 0.17, hx + x, hy + 0.24, WHITE, 0.03)
    cp.muzzle(p, hx + 0.25, hy + 0.05, 0.2, nose=(90, 50, 60), whisker=(200, 210, 180))


def draw_cavaleiro(p, col, frame):
    """Cavaleiro Sem Cabeça: armadura amassada, fogo azul no pescoço, elmo de gato no braço e espada."""
    steel, dark = col, _shade(col, 0.6)
    flick = _step(frame, 0.1)
    st = _step(frame, 0.08)
    cp.tail(p, (60, 60, 75), base=(-0.5, 0.65), tip=(90, 170, 255))
    for x, s in ((-0.28, st), (0.3, -st)):                                          # grevas
        limb(p, [(x, 0.7), (x + s, 1.32)], _shade(steel, 0.85), 0.24)
        oval(p, x + s + 0.08, 1.4, 0.2, 0.1, dark)
    p.line(0.6, -0.1, 1.55, -1.3, (200, 205, 215), 0.13)                            # espada
    p.line(0.45, -0.25, 0.85, 0.1, GOLD_D, 0.09)
    p.poly([(-0.62, -0.45), (0.62, -0.45), (0.5, 0.8), (-0.5, 0.8)], steel)          # couraça
    p.line(0, -0.4, 0, 0.75, dark, 0.05)
    p.line(-0.48, 0.45, 0.48, 0.45, dark, 0.08)
    for sx in (-1, 1):                                                              # ombreiras
        oval(p, 0.62 * sx, -0.35, 0.3, 0.22, _shade(steel, 1.1))
    oval(p, 0, -0.55, 0.25, 0.1, (40, 40, 50))                                      # pescoço vazio
    p.poly([(-0.2, -0.58), (0.0 + flick, -1.45), (0.2, -0.58)], (90, 170, 255))     # fogo fantasma
    p.poly([(-0.1, -0.6), (0.04 + flick, -1.1), (0.12, -0.6)], (200, 235, 255), outline=False)
    cp.ears(p, -0.85, 0.3, 0.36, _shade(steel, 0.95), inner=dark, size=0.7)         # elmo de gato no braço
    p.circle(-0.85, 0.3, 0.36, _shade(steel, 0.95))
    p.line(-1.1, 0.27, -0.6, 0.27, (30, 30, 40), 0.06)
    p.circle(-0.78, 0.27, 0.04, (120, 200, 255), outline=False)


def draw_zumbi(p, col, frame):
    """Gato zumbi: roupa rasgada, braços esticados, cicatriz costurada, olho caído e cauda."""
    skin, dark = col, _shade(col, 0.55)
    sway = _step(frame, 0.1)
    cloth = (95, 80, 110)
    st = _cat_torso(p, skin, cloth, frame, pants=(70, 62, 80), boots=(50, 44, 52))
    p.poly([(-0.48, 0.85), (-0.32, 1.05), (-0.15, 0.85), (0.05, 1.05), (0.2, 0.85), (0.42, 1.0), (0.5, 0.85)],
           cloth)                                                                   # barra rasgada
    p.circle(-0.25, 0.3, 0.1, (90, 140, 70), outline=False)                         # mancha de podridão
    for y in (-0.2, 0.1):                                                           # braços esticados
        limb(p, [(0.45, y), (1.45, y + sway)], skin, 0.17)
        p.circle(1.5, y + sway, 0.13, _shade(skin, 0.9))
    hx, hy = 0.15, -0.72
    cp.ears(p, hx, hy, 0.52, skin, inner=(150, 90, 100), tilt=-6)
    p.circle(hx, hy, 0.52, skin)                                                    # cabeça
    p.lines([(hx - 0.35, hy - 0.3), (hx - 0.1, hy - 0.1), (hx + 0.1, hy - 0.35)], dark, 0.05)   # cicatriz
    eye(p, hx + 0.25, hy - 0.05, (250, 240, 140), 0.11)
    p.circle(hx - 0.05, hy + 0.05, 0.09, (60, 40, 40), outline=False)               # olho caído
    cp.muzzle(p, hx + 0.12, hy + 0.2, 0.2, nose=(120, 70, 80), whisker=(200, 210, 170))


# ===========================================================================
# Catedral
# ===========================================================================
def draw_gargula(p, col, frame, eye_col=(255, 140, 60), big=False):
    """Gárgula agachada: asas de morcego de pedra, ancas dobradas, chifres, focinho e garras."""
    wing = _shade(col, 0.72)
    up = 0.15 if frame % 2 else 0.0
    dark = _shade(col, 0.6)
    for sx in (-1, 1):                                                              # asas
        p.poly([(0.2 * sx - 0.1, -0.35), (1.45 * sx - 0.1, -1.35 - up), (1.3 * sx - 0.1, -0.7),
                (1.75 * sx - 0.1, -0.45 - up), (1.05 * sx - 0.1, -0.05), (0.4 * sx - 0.1, 0.2)], wing)
    p.lines([(-0.55, 0.65), (-1.2, 0.85), (-1.45, 0.6)], dark, 0.1)                 # cauda
    p.poly([(-1.45, 0.6), (-1.6, 0.4), (-1.3, 0.48)], dark)
    limb(p, [(-0.45, 0.45), (-0.15, 0.85), (-0.5, 1.2)], dark, 0.22)                # ancas
    oval(p, -0.05, 0.25, 0.65, 0.55, col)                                           # tronco
    limb(p, [(0.25, 0.5), (0.55, 0.85), (0.3, 1.2)], col, 0.22)
    for (x, y) in ((-0.5, 1.22), (0.32, 1.22)):                                     # garras
        for k in (-0.1, 0.05, 0.2):
            p.line(x + k, y, x + k + 0.08, y + 0.12, (60, 60, 70), 0.04)
    limb(p, [(0.4, 0.1), (0.85, 0.4), (0.85, 0.75)], col, 0.15)                     # braço
    hx, hy = 0.4, -0.45
    hr = 0.5 if big else 0.42
    for sx in (-1, 1):                                                              # chifres
        h = 1.35 if big else 1.0
        p.lines([(hx + 0.2 * sx, hy - 0.3), (hx + 0.45 * sx, hy - 0.7 * h), (hx + 0.3 * sx, hy - 0.95 * h)],
                _shade(col, 1.3), 0.11 if big else 0.09)
    p.circle(hx, hy, hr, _shade(col, 1.05))                                         # cabeça
    p.poly([(hx + 0.2, hy - 0.05), (hx + 0.75, hy + 0.1), (hx + 0.6, hy + 0.3), (hx + 0.15, hy + 0.25)],
           _shade(col, 1.1))                                                        # focinho
    p.poly([(hx + 0.35, hy + 0.27), (hx + 0.4, hy + 0.42), (hx + 0.46, hy + 0.27)], WHITE, outline=False)
    eye(p, hx + 0.1, hy - 0.12, eye_col, 0.09)
    eye(p, hx + 0.38, hy - 0.1, eye_col, 0.08)
    for (x1, y1, x2, y2) in ((-0.4, 0.0, -0.15, 0.3), (0.1, 0.45, 0.3, 0.6)):        # rachaduras
        p.line(x1, y1, x2, y2, dark, 0.04)


def draw_grande_gargula(p, col, frame):
    """Grande Gárgula: gárgula maior com runas acesas e chifres enormes."""
    draw_gargula(p, col, frame, eye_col=(255, 60, 40), big=True)
    for x, y in ((-0.3, 0.1), (0.1, 0.35), (-0.1, 0.55)):
        p.circle(x, y, 0.07, (255, 140, 60), outline=False)


def draw_armadura(p, col, frame):
    """Armadura viva: elmo de gato com fresta acesa, couraça, grevas, escudo com cruz e espada."""
    st = _step(frame, 0.08)
    steel, dark = col, _shade(col, 0.6)
    p.line(0.6, -0.05, 1.5, -1.0 + st, (200, 205, 215), 0.11)                       # espada
    for x, s in ((-0.28, st), (0.3, -st)):                                          # grevas
        limb(p, [(x, 0.7), (x + s, 1.32)], _shade(steel, 0.9), 0.24)
        oval(p, x + s + 0.08, 1.4, 0.2, 0.1, dark)
    p.poly([(-0.62, -0.4), (0.62, -0.4), (0.5, 0.82), (-0.5, 0.82)], steel)          # couraça
    p.line(0, -0.35, 0, 0.75, dark, 0.05)
    p.line(-0.48, 0.45, 0.48, 0.45, dark, 0.08)
    for sx in (-1, 1):
        oval(p, 0.62 * sx, -0.3, 0.3, 0.22, _shade(steel, 1.1))
    hx, hy = 0.05, -0.85
    cp.ears(p, hx, hy, 0.45, _shade(steel, 1.1), inner=dark, spread=44, size=0.65)
    p.circle(hx, hy, 0.45, _shade(steel, 1.1))                                      # elmo
    p.line(hx - 0.3, hy + 0.02, hx + 0.32, hy + 0.02, (25, 25, 35), 0.1)            # fresta
    p.line(hx - 0.2, hy + 0.02, hx + 0.22, hy + 0.02, (140, 220, 255), 0.04)
    oval(p, -0.75, 0.25 + st, 0.38, 0.5, (110, 40, 45))                             # escudo
    p.line(-0.75, -0.05 + st, -0.75, 0.55 + st, GOLD, 0.07)
    p.line(-0.98, 0.18 + st, -0.52, 0.18 + st, GOLD, 0.07)


def draw_serafim(p, col, frame, eye_col=(255, 80, 80)):
    """Serafim caído: gato de manto escuro, asas negras rasgadas e olhos acesos."""
    flap = 0.12 if frame % 2 else -0.05
    for sx in (-1, 1):                                                              # asas em camadas
        for k in range(3):
            y = -1.0 + k * 0.38 - flap
            p.poly([(0.35 * sx, -0.4 + k * 0.22), (1.95 * sx, y), (1.5 * sx, y + 0.38)], _shade(col, 0.6 + k * 0.12))
    p.poly([(-0.5, -0.35), (0.5, -0.35), (0.95, 1.3), (-0.95, 1.3)], col)           # manto
    p.poly([(-0.95, 1.3), (-0.6, 1.1), (-0.3, 1.32), (0.0, 1.1), (0.3, 1.32), (0.6, 1.1), (0.95, 1.3)],
           _shade(col, 0.8))
    p.line(0, -0.3, 0, 1.2, _shade(col, 0.6), 0.05)
    p.line(-0.45, 0.35, 0.45, 0.35, (150, 140, 160), 0.06)
    hx, hy = 0, -0.75
    face = _shade(col, 1.6)
    cp.ears(p, hx, hy, 0.48, face, inner=_shade(col, 1.2), spread=40, size=0.55)
    p.circle(hx, hy, 0.48, face)                                                    # cabeça
    cp.slit_eye(p, hx - 0.17, hy - 0.05, eye_col, 0.1)
    cp.slit_eye(p, hx + 0.17, hy - 0.05, eye_col, 0.1)
    cp.muzzle(p, hx, hy + 0.15, 0.24, nose=(150, 90, 110), whisker=_shade(col, 0.7))


def draw_arcanjo(p, col, frame):
    """Arcanjo Caído: serafim maior, auréola rachada e uma espada de fogo negro."""
    draw_serafim(p, col, frame, eye_col=(255, 210, 90))
    for k in range(10):                                                             # auréola quebrada
        if k in (3, 4):
            continue
        a0 = k * 36
        p.lines(_arc(0, -1.55, 0.5, a0, a0 + 30, 3, 0.16), GOLD, 0.08)
    p.line(0.55, 0.3, 1.45, -1.15, (60, 30, 70), 0.15)                              # espada sombria
    p.line(0.55, 0.3, 1.45, -1.15, (200, 120, 255), 0.05)
    p.line(0.4, 0.05, 0.8, 0.35, GOLD, 0.08)


# ===========================================================================
# Subterrâneo
# ===========================================================================
def draw_golem(p, col, frame, glow=(255, 150, 60)):
    """Golem de pedra: tronco de blocos, cabeça pequena, braços com punhos enormes, pernas grossas e núcleo aceso."""
    st = _step(frame, 0.08)
    dark, light = _shade(col, 0.75), _shade(col, 1.12)
    for x, s in ((-0.45, st), (0.4, -st)):                                          # pernas
        p.poly([(x - 0.25, 0.6), (x + 0.25, 0.6), (x + 0.28 + s, 1.35), (x - 0.28 + s, 1.35)], dark)
    for sx in (-1, 1):                                                              # braços e punhos
        p.poly([(0.7 * sx, -0.55), (1.15 * sx, -0.35), (1.25 * sx, 0.35 + st * sx), (0.85 * sx, 0.4)], dark)
        p.poly([(0.95 * sx, 0.3 + st * sx), (1.5 * sx, 0.35 + st * sx), (1.55 * sx, 0.95 + st * sx),
                (0.95 * sx, 1.0 + st * sx)], _shade(col, 0.9))
    p.poly([(-0.85, -0.65), (-0.3, -0.85), (0.4, -0.85), (0.9, -0.55), (0.75, 0.7), (-0.75, 0.7)], col)   # tronco
    for (x1, y1, x2, y2) in ((-0.5, -0.4, -0.2, 0.1), (0.35, -0.6, 0.55, -0.1), (-0.2, 0.35, 0.3, 0.5)):
        p.line(x1, y1, x2, y2, dark, 0.05)
    p.poly([(-0.85, -0.65), (-0.3, -0.85), (0.1, -0.75), (-0.5, -0.45)], (80, 120, 60), outline=False)   # musgo
    p.poly([(-0.3, -0.85), (-0.25, -1.3), (0.35, -1.32), (0.4, -0.85)], light)        # cabeça
    p.line(-0.15, -1.08, 0.0, -1.08, glow, 0.07)                                    # olhos em fenda
    p.line(0.12, -1.08, 0.27, -1.08, glow, 0.07)
    p.circle(0.0, 0.0, 0.2, glow, outline=False)                                    # núcleo
    p.circle(0.0, 0.0, 0.1, (255, 240, 200), outline=False)


def draw_golem_cristal(p, col, frame):
    """Golem de Cristal: golem com cristais azuis brotando dos ombros e da cabeça."""
    draw_golem(p, col, frame, glow=(140, 230, 255))
    for x, y, h in ((-0.75, -0.62, 0.7), (-0.4, -0.85, 0.85), (0.5, -0.82, 0.8), (0.85, -0.55, 0.6),
                    (0.05, -1.3, 0.5)):
        p.poly([(x - 0.14, y), (x, y - h), (x + 0.14, y)], (150, 220, 255))
        p.line(x, y, x, y - h * 0.7, (220, 245, 255), 0.04)


DRAWERS = {
    'morcego': draw_morcego,
    'javali': draw_javali,
    'ent': draw_ent,
    'aranha': draw_aranha,
    'zumbi': draw_zumbi,
    'bruto': draw_bruto,
    'lorde_bandido': draw_lorde_bandido,
    'carnical': draw_carnical,
    'cavaleiro': draw_cavaleiro,
    'gargula': draw_gargula,
    'grande_gargula': draw_grande_gargula,
    'armadura': draw_armadura,
    'serafim': draw_serafim,
    'arcanjo': draw_arcanjo,
    'golem': draw_golem,
    'golem_cristal': draw_golem_cristal,
}
# vista de lado: viram para o lado em que andam
FLIPPABLE = {"lobo", "javali", "aranha", "guardiao", "zumbi", "rato", "cao", "bruto", "lorde_bandido", "rei_rato",
             "carnical", "cavaleiro", "gargula", "grande_gargula", "armadura", "arcanjo", "besouro", "matriarca",
             "goblin", "rei_goblin"}
FRAMES = {k: 2 for k in DRAWERS}
