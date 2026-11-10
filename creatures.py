"""Redesenho (0.0.29) dos inimigos que destoavam do resto do jogo.

Mesma linguagem visual dos heróis gatos: cabeça grande, corpo pequeno e redondinho, patas grossas e curtas,
olhos expressivos e silhueta fácil de ler. Humanoides são gatos (agora também os goblins e o inquisidor);
animais e monstros ganham proporções "chibi" em vez de corpos finos e compridos.
Coordenadas em unidades do raio (_Pen de icons.py), olhando para a direita; espaço até ±2,4.
"""
import math

from icons import _arc, _shade, OUT
import cat_parts as cp
from beasts import oval, eye, limb, crown, _step, _cat_torso

WHITE = (240, 240, 245)
GOLD = (235, 195, 70)
BONE = (230, 222, 205)


# ===========================================================================
# Bichos de quatro patas (lobo, cão, rato, cervo)
# ===========================================================================
def _quad(p, col, frame, eye_col, head=0.62, snout=0.5, ear="up", tail="bushy", lean=False, belly=None):
    """Quadrúpede chibi de lado: corpo de feijão, 4 patinhas grossas, cabeçona com focinho e cauda."""
    st = _step(frame, 0.13)
    dark, light = _shade(col, 0.68), _shade(col, 1.3)
    bob = -0.04 if frame % 2 else 0.0
    # cauda
    if tail == "bushy":
        p.poly([(-0.75, -0.05), (-1.35, -0.75), (-1.7, -0.6), (-1.55, -0.2), (-0.85, 0.3)], dark)
        p.poly([(-1.35, -0.75), (-1.7, -0.6), (-1.55, -0.45)], light, outline=False)
    elif tail == "thin":
        p.lines([(-0.75, 0.05), (-1.3, -0.25), (-1.6, -0.6)], dark, 0.13)
    else:   # rabo de rato
        p.lines([(-0.8, 0.3), (-1.4, 0.15 + st), (-1.85, 0.4 - st), (-2.15, 0.25)], (215, 150, 155), 0.08)
    # patas de longe
    limb(p, [(-0.5, 0.3), (-0.55 + st, 0.95)], dark, 0.24)
    limb(p, [(0.4, 0.3), (0.42 - st, 0.95)], dark, 0.24)
    # corpo
    oval(p, -0.05, 0.12 + bob, 0.82, 0.5 if not lean else 0.42, col)
    if belly:
        oval(p, 0.15, 0.32 + bob, 0.5, 0.22, belly, outline=False)
    # patas de perto (com patinha clara)
    for x, s in ((-0.32, -st), (0.6, st)):
        limb(p, [(x, 0.35), (x + s, 0.98)], col, 0.26)
        oval(p, x + s + 0.05, 1.02, 0.17, 0.1, light)
    # cabeça
    hx, hy = 0.85, -0.42 + bob
    if ear == "up":
        for x0 in (-0.22, 0.18):
            p.poly([(hx + x0 - 0.17, hy - 0.38), (hx + x0 + 0.02, hy - 0.98), (hx + x0 + 0.22, hy - 0.42)], col)
            p.poly([(hx + x0 - 0.06, hy - 0.45), (hx + x0 + 0.03, hy - 0.8), (hx + x0 + 0.12, hy - 0.48)],
                   (200, 130, 140), outline=False)
    elif ear == "round":
        for x0, r0 in ((-0.25, 0.3), (0.2, 0.27)):
            p.circle(hx + x0, hy - 0.5, r0, _shade(col, 0.92))
            p.circle(hx + x0, hy - 0.5, r0 * 0.6, (225, 160, 170), outline=False)
    elif ear == "torn":   # orelhas rasgadas / caídas (cão sarnento)
        p.poly([(hx - 0.42, hy - 0.3), (hx - 0.35, hy - 0.95), (hx - 0.12, hy - 0.62), (hx - 0.08, hy - 0.4)], col)
        p.poly([(hx + 0.08, hy - 0.45), (hx + 0.55, hy - 0.7), (hx + 0.45, hy - 0.25)], dark)
    p.circle(hx, hy, head, col)
    # focinho
    sx0 = hx + head * 0.55
    p.poly([(sx0 - 0.1, hy - 0.08), (sx0 + snout, hy + 0.02), (sx0 + snout, hy + 0.26), (sx0 - 0.1, hy + 0.32)], light)
    p.circle(sx0 + snout, hy + 0.08, 0.1, OUT if ear != "round" else (210, 120, 130), outline=False)   # nariz
    p.line(sx0 + 0.05, hy + 0.3, sx0 + snout - 0.05, hy + 0.3, OUT, 0.05)                              # boca
    eye(p, hx + 0.2, hy - 0.12, eye_col, 0.13)
    return hx, hy, st


def draw_lobo(p, col, frame, eye_col=(255, 210, 60)):
    """Lobo: robusto, pelagem fofa no peito e cauda peluda, olhar de caçador e caninos à mostra."""
    hx, hy, _ = _quad(p, col, frame, eye_col, belly=_shade(col, 1.35))
    p.line(hx + 0.05, hy - 0.3, hx + 0.38, hy - 0.2, OUT, 0.07)                 # sobrancelha brava
    p.poly([(hx + 0.6, hy + 0.3), (hx + 0.66, hy + 0.48), (hx + 0.72, hy + 0.3)], WHITE, outline=False)   # canino
    for k in range(3):                                                         # juba no pescoço
        p.poly([(hx - 0.55 + k * 0.18, hy + 0.35), (hx - 0.5 + k * 0.18, hy + 0.7),
                (hx - 0.38 + k * 0.18, hy + 0.38)], _shade(col, 1.15), outline=False)


def draw_cao(p, col, frame, eye_col=(240, 200, 60)):
    """Cão sarnento: mais magro, orelhas rasgadas, costelas, coleira com corrente partida e baba."""
    hx, hy, st = _quad(p, col, frame, eye_col, head=0.56, ear="torn", tail="thin", lean=True)
    dark = _shade(col, 0.55)
    for i in range(3):                                                         # costelas
        p.line(-0.42 + i * 0.22, -0.02, -0.36 + i * 0.22, 0.34, dark, 0.05)
    p.circle(-0.55, -0.05, 0.12, (120, 110, 90), outline=False)                # falha no pelo
    p.line(hx - 0.42, hy + 0.35, hx + 0.1, hy + 0.55, (150, 50, 40), 0.13)    # coleira
    p.lines([(hx - 0.2, hy + 0.5), (hx - 0.3, hy + 0.8), (hx - 0.2, hy + 1.0)], (160, 160, 170), 0.06)
    p.line(hx + 0.72, hy + 0.36, hx + 0.74, hy + 0.58, (200, 230, 240), 0.05)  # baba


def draw_rato(p, col, frame):
    """Rato da peste: cabeçudo, orelhonas redondas, dentinhos, rabo pelado e feridas da peste."""
    hx, hy, _ = _quad(p, col, frame, (230, 50, 50), head=0.58, snout=0.42, ear="round", tail="rat")
    p.poly([(hx + 0.72, hy + 0.32), (hx + 0.86, hy + 0.32), (hx + 0.79, hy + 0.5)], WHITE)       # dentes
    for dy in (-0.06, 0.08):                                                   # bigodes
        p.line(hx + 0.75, hy + 0.15, hx + 1.25, hy + 0.1 + dy * 2.5, (70, 60, 55), 0.04)
    for x, y, r in ((-0.45, 0.0, 0.14), (-0.05, 0.3, 0.1), (0.25, -0.12, 0.08)):   # feridas da peste
        p.circle(x, y, r, (150, 175, 80), outline=False)
        p.circle(x - r * 0.3, y - r * 0.3, r * 0.4, (205, 225, 130), outline=False)


def draw_rei_rato(p, col, frame):
    """Rei Rato: o rato gordo de capa real, coroa torta e cetro de osso."""
    p.poly([(-0.75, -0.25), (-1.4, 0.9), (0.4, 0.9), (0.25, -0.25)], (140, 30, 40))   # capa
    p.poly([(-0.75, -0.25), (0.25, -0.25), (0.15, -0.05), (-0.65, -0.05)], (235, 230, 220))   # gola de arminho
    draw_rato(p, col, frame)
    crown(p, 0.9, -0.98, 0.32, 0.34)
    p.line(-0.2, 0.75, -0.45, -0.7, BONE, 0.1)                                 # cetro de osso
    p.circle(-0.47, -0.78, 0.15, BONE)


def draw_guardiao(p, col, frame):
    """Guardião Corrompido: cervo robusto tomado por vinhas, galhada com musgo e olhos verdes acesos."""
    fur = (110, 75, 60)
    hx, hy, _ = _quad(p, fur, frame, (120, 255, 120), head=0.55, snout=0.45, ear="up", tail="thin",
                      belly=(200, 175, 145))
    antler = (225, 212, 190)
    for sx, dx in ((-1, -0.12), (1, 0.12)):                                    # galhada
        bx = hx + dx
        p.lines([(bx, hy - 0.5), (bx + 0.25 * sx, hy - 1.15), (bx + 0.55 * sx, hy - 1.6)], antler, 0.11)
        p.line(bx + 0.22 * sx, hy - 1.0, bx + 0.6 * sx, hy - 1.15, antler, 0.09)
        p.line(bx + 0.42 * sx, hy - 1.38, bx + 0.35 * sx, hy - 1.8, antler, 0.08)
        p.circle(bx + 0.3 * sx, hy - 1.2, 0.1, (80, 140, 70), outline=False)  # musgo
    for x in (-0.45, -0.05, 0.35):                                             # vinhas corrompidas no corpo
        p.lines([(x - 0.15, -0.3), (x + 0.05, 0.05), (x - 0.05, 0.45)], col, 0.09)
        p.circle(x + 0.05, 0.05, 0.08, (255, 90, 120), outline=False)


# ===========================================================================
# Insetos e vermes do Subterrâneo
# ===========================================================================
def draw_besouro(p, col, frame, big=False):
    """Besouro da caverna: carapaça redonda e brilhante, cabeça com mandíbulas grandes e 3 patas grossas."""
    st = _step(frame, 0.12)
    leg = _shade(col, 0.45)
    bob = -0.03 if frame % 2 else 0.0
    for i in range(3):                                                         # patas de longe
        x = -0.55 + i * 0.5
        limb(p, [(x, 0.3), (x + 0.12, 0.72 + (st if i % 2 else -st)), (x + 0.35, 0.92)], _shade(leg, 0.8), 0.12)
    oval(p, -0.15, -0.05 + bob, 0.95, 0.78, col)                               # carapaça (domo)
    p.line(-0.15, -0.8 + bob, -0.15, 0.7 + bob, _shade(col, 0.55), 0.06)       # divisão dos élitros
    oval(p, -0.45, -0.38 + bob, 0.28, 0.18, _shade(col, 1.6), outline=False)   # brilho metálico
    p.circle(-0.6, -0.15 + bob, 0.06, _shade(col, 1.8), outline=False)
    p.circle(0.85, 0.15, 0.48, _shade(col, 0.7))                               # cabeça
    for dy, sgn in ((-0.05, -1), (0.32, 1)):                                   # mandíbulas
        p.poly([(1.2, 0.12 + dy * 0.5), (1.75, dy - 0.05 * sgn), (1.6, dy + 0.1), (1.25, 0.2 + dy * 0.4)],
               (90, 60, 40))
    p.lines([(0.95, -0.25), (1.2, -0.75), (1.55, -0.9)], leg, 0.06)            # antena
    p.circle(1.55, -0.9, 0.07, leg, outline=False)
    eye(p, 1.02, 0.02, (255, 220, 120), 0.12)
    for i in range(3):                                                         # patas de perto
        x = -0.6 + i * 0.5
        limb(p, [(x, 0.45), (x + 0.15, 0.85 + (-st if i % 2 else st)), (x + 0.4, 1.0)], leg, 0.13)
    if big:
        for x in (0.6, 0.85, 1.1):                                             # chifre-coroa
            p.poly([(x - 0.09, -0.22), (x, -0.62 - (0.16 if x == 0.85 else 0)), (x + 0.09, -0.22)], GOLD)


def draw_matriarca(p, col, frame):
    """Matriarca: besouro rainha com chifre-coroa e um cacho de ovos brilhantes nas costas."""
    for (x, y) in ((-1.45, 0.45), (-1.7, 0.1), (-1.3, 0.8), (-1.75, 0.6), (-1.5, -0.2)):
        p.circle(x, y, 0.24, (230, 220, 175))                                  # ovos
        p.circle(x - 0.07, y - 0.07, 0.08, (255, 250, 220), outline=False)
    draw_besouro(p, col, frame, big=True)


def _wyrm(p, col, frame, eye_col, crystal=(150, 220, 255), horns=False, fire=False):
    """Serpente de cristal chibi: corpo em S erguido, cabeça de dragãozinho e cristais nas costas."""
    wig = 0.12 if frame % 2 else -0.12
    dark, light = _shade(col, 0.7), _shade(col, 1.3)
    body = [(-1.65, 0.95), (-1.2, 0.98 + wig), (-0.75, 0.82 - wig), (-0.35, 0.52 + wig), (-0.05, 0.12)]
    for i, (x, y) in enumerate(body):                                          # gomos encostados, crescendo
        r = 0.3 + i * 0.065
        p.circle(x, y, r, _shade(col, 0.8 + i * 0.05))
        p.circle(x, y + r * 0.35, r * 0.55, light, outline=False)              # barriga clara
        if i >= 1:                                                             # cristais nas costas
            h = 0.35 + i * 0.08
            p.poly([(x - 0.1, y - r * 0.8), (x - 0.02, y - r - h), (x + 0.12, y - r * 0.8)], crystal)
            p.line(x, y - r * 0.85, x - 0.01, y - r - h * 0.6, (230, 250, 255), 0.04)
    hx, hy = 0.35, -0.45
    p.circle(hx, hy, 0.62, col)                                                # cabeça
    p.poly([(hx + 0.3, hy - 0.2), (hx + 1.15, hy - 0.05), (hx + 1.15, hy + 0.3), (hx + 0.3, hy + 0.4)], col)   # focinho
    p.poly([(hx + 0.35, hy + 0.18), (hx + 1.1, hy + 0.2), (hx + 1.05, hy + 0.32)], (90, 25, 35), outline=False)   # boca
    for k in range(3):                                                         # dentinhos
        x = hx + 0.5 + k * 0.2
        p.poly([(x, hy + 0.18), (x + 0.06, hy + 0.3), (x + 0.12, hy + 0.18)], WHITE, outline=False)
    p.circle(hx + 1.05, hy, 0.06, OUT, outline=False)                          # narina
    for k, (x, h) in enumerate(((-0.25, 0.75), (0.05, 0.95), (0.35, 0.7))):   # crista de cristal
        p.poly([(hx + x - 0.12, hy - 0.45), (hx + x, hy - 0.45 - h), (hx + x + 0.12, hy - 0.45)], crystal)
    if horns:
        for x in (-0.15, 0.25):
            p.lines([(hx + x, hy - 0.5), (hx + x - 0.3, hy - 0.9), (hx + x - 0.15, hy - 1.25)], (70, 45, 45), 0.12)
    eye(p, hx + 0.25, hy - 0.12, eye_col, 0.14)
    p.line(hx + 0.08, hy - 0.32, hx + 0.45, hy - 0.26, OUT, 0.07)               # sobrancelha brava
    if fire:
        flick = 0.12 if frame % 2 else -0.05
        p.poly([(hx + 1.1, hy + 0.15), (hx + 1.95 + flick, hy - 0.05), (hx + 1.7, hy + 0.3),
                (hx + 2.0 + flick, hy + 0.5), (hx + 1.1, hy + 0.35)], (255, 140, 40))
        p.poly([(hx + 1.15, hy + 0.22), (hx + 1.6 + flick, hy + 0.2), (hx + 1.15, hy + 0.32)], (255, 230, 120),
               outline=False)


def draw_verme(p, col, frame, eye=(255, 230, 120)):
    _wyrm(p, col, frame, eye)


def draw_wyrm(p, col, frame):
    """Wyrm das Profundezas: a serpente de cristal maior, com chifres, cristais de lava e fogo na boca."""
    _wyrm(p, col, frame, (255, 120, 40), crystal=(255, 150, 70), horns=True, fire=True)


# ===========================================================================
# Goblins (agora gatos-goblin: pelagem verde, orelhonas compridas)
# ===========================================================================
def draw_goblin(p, col, frame, eye_col=(255, 230, 90)):
    """Gato-goblin minerador: baixinho, orelhas compridas, capacete com lampião, macacão e picareta."""
    swing = 0.15 if frame % 2 else -0.1
    st = _cat_torso(p, col, (90, 110, 150), frame, pants=(80, 95, 130), boots=(70, 50, 35))   # macacão
    p.line(-0.42, -0.3, -0.3, 0.6, (60, 75, 110), 0.1)                        # alças
    p.line(0.42, -0.3, 0.3, 0.6, (60, 75, 110), 0.1)
    limb(p, [(0.5, -0.1), (0.85, 0.25), (1.15, 0.0 + swing)], col, 0.16)       # braço
    p.line(1.15, swing, 1.2, -1.05 + swing, (120, 80, 45), 0.1)               # cabo da picareta
    p.poly([(0.65, -0.95 + swing), (1.2, -1.2 + swing), (1.75, -0.88 + swing), (1.2, -1.02 + swing)], (175, 175, 185))
    hx, hy, hr = 0.08, -0.72, 0.58
    for sx in (-1, 1):                                                        # orelhonas de goblin
        p.poly([(hx + 0.35 * sx, hy - 0.35), (hx + 1.15 * sx, hy - 0.75), (hx + 0.55 * sx, hy + 0.02)], col)
        p.poly([(hx + 0.48 * sx, hy - 0.3), (hx + 0.95 * sx, hy - 0.6), (hx + 0.58 * sx, hy - 0.08)],
               (200, 130, 120), outline=False)
    p.circle(hx, hy, hr, col)                                                 # cabeçona
    p.poly(_arc(hx, hy - 0.12, hr * 1.04, 190, 350, 8), (185, 150, 60))       # capacete de mineiro
    p.line(hx - hr, hy - 0.15, hx + hr, hy - 0.15, (130, 100, 40), 0.08)
    p.circle(hx + 0.05, hy - 0.62, 0.15, (255, 220, 110))                     # lampião
    p.circle(hx + 0.05, hy - 0.62, 0.07, (255, 250, 220), outline=False)
    cp.slit_eye(p, hx - 0.15, hy + 0.02, eye_col, 0.11)
    cp.slit_eye(p, hx + 0.27, hy + 0.02, eye_col, 0.11)
    cp.muzzle(p, hx + 0.08, hy + 0.25, 0.26, nose=(120, 70, 70), whisker=(210, 230, 190))
    p.poly([(hx + 0.12, hy + 0.36), (hx + 0.18, hy + 0.48), (hx + 0.24, hy + 0.36)], WHITE, outline=False)   # dentinho


def draw_rei_goblin(p, col, frame):
    """Rei Goblin: o gato-goblin de capa roxa, coroa grande e um saco de ouro."""
    p.poly([(-0.6, -0.3), (-1.1, 1.3), (0.5, 1.3), (0.5, -0.3)], (100, 50, 130))   # capa
    p.circle(-1.15, 0.95, 0.42, (150, 120, 70))                               # saco de ouro
    p.circle(-1.15, 0.62, 0.12, GOLD, outline=False)
    for x, y in ((-1.3, 1.25), (-0.95, 1.3)):
        p.circle(x, y, 0.08, GOLD, outline=False)
    draw_goblin(p, col, frame, eye_col=(255, 120, 60))
    crown(p, 0.08, -1.25, 0.45, 0.45)


# ===========================================================================
# Catedral
# ===========================================================================
def draw_inquisidor(p, col, frame):
    """Alto Inquisidor (gato): manto vermelho, capuz alto com cruz, cara de poucos amigos e tocha acesa."""
    flick = 0.1 if frame % 2 else -0.1
    fur = (205, 205, 215)
    cp.tail(p, fur, base=(-0.85, 0.95), tip=_shade(fur, 0.8))
    p.poly([(-0.85, -0.1), (-1.1, 1.3), (1.1, 1.3), (0.85, -0.1)], col)       # manto
    p.line(0, -0.1, 0, 1.3, GOLD, 0.12)                                        # faixa
    p.poly([(-0.2, 0.3), (0.2, 0.3), (0.0, 0.6)], GOLD, outline=False)
    limb(p, [(0.75, 0.2), (1.2, 0.3), (1.45, -0.15)], col, 0.22)               # braço
    p.line(1.45, -0.15, 1.55, -0.95, (100, 70, 40), 0.11)                      # tocha
    p.poly([(1.38, -0.95), (1.55 + flick, -1.6), (1.72, -0.95)], (255, 150, 50))
    p.poly([(1.47, -0.95), (1.55 + flick * 0.5, -1.3), (1.63, -0.95)], (255, 230, 120), outline=False)
    hx, hy, hr = 0.0, -0.62, 0.62
    cp.ears(p, hx, hy, hr, fur, inner=(220, 150, 160), spread=55, size=0.55)  # orelhas aparecendo do capuz
    p.circle(hx, hy, hr, fur)                                                  # cabeça de gato
    cp.slit_eye(p, hx - 0.22, hy - 0.02, (230, 180, 60), 0.12)
    cp.slit_eye(p, hx + 0.24, hy - 0.02, (230, 180, 60), 0.12)
    p.line(hx - 0.4, hy - 0.22, hx - 0.08, hy - 0.12, OUT, 0.08)               # sobrancelhas severas
    p.line(hx + 0.42, hy - 0.22, hx + 0.1, hy - 0.12, OUT, 0.08)
    cp.muzzle(p, hx + 0.02, hy + 0.22, 0.3, nose=(200, 110, 120), whisker=(240, 240, 245))
    # capuz alto (capirote) por trás das orelhas, com a cruz dourada
    p.poly([(-0.42, -1.05), (0.0, -2.2), (0.42, -1.05)], (235, 225, 210))
    p.line(0, -1.9, 0, -1.2, GOLD, 0.08)
    p.line(-0.15, -1.6, 0.15, -1.6, GOLD, 0.08)


def draw_vitral(p, col, frame):
    """Golem de Vitral: construto de painéis de vidro colorido com caixilhos de chumbo e uma rosácea por cabeça."""
    lead = (45, 42, 55)
    cols = [(200, 60, 70), (70, 130, 210), (240, 200, 70), (90, 180, 110), (160, 90, 200), (240, 140, 60)]
    st = _step(frame, 0.08)
    glow = (255, 255, 230) if frame % 2 else (255, 240, 190)

    def pane(pts, c):
        p.poly(pts, c)
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        p.circle(cx - 0.05, cy - 0.05, 0.06, _shade(c, 1.6), outline=False)    # reflexo
    for i, (x, s) in enumerate(((-0.42, st), (0.38, -st))):                    # pernas de vitral
        pane([(x - 0.24, 0.55), (x + 0.24, 0.55), (x + 0.26 + s, 1.35), (x - 0.26 + s, 1.35)], cols[i + 3])
        p.line(x - 0.25 + s * 0.5, 0.95, x + 0.25 + s * 0.5, 0.95, lead, 0.06)
    for sx in (-1, 1):                                                         # braços em losangos
        pane([(0.75 * sx, -0.45), (1.3 * sx, -0.15), (1.35 * sx, 0.45 + st * sx), (0.85 * sx, 0.35)],
             cols[1 if sx < 0 else 5])
        pane([(1.05 * sx, 0.4 + st * sx), (1.5 * sx, 0.5 + st * sx), (1.4 * sx, 0.95 + st * sx),
              (1.0 * sx, 0.85 + st * sx)], cols[2])
    # tronco: moldura de pedra com painéis dentro
    p.poly([(-0.8, -0.6), (0.8, -0.6), (0.68, 0.65), (-0.68, 0.65)], (150, 140, 135))
    panes = [[(-0.68, -0.5), (0.0, -0.5), (0.0, 0.05), (-0.62, 0.05)], [(0.0, -0.5), (0.68, -0.5), (0.62, 0.05), (0.0, 0.05)],
             [(-0.62, 0.05), (0.0, 0.05), (0.0, 0.58), (-0.58, 0.58)], [(0.0, 0.05), (0.62, 0.05), (0.58, 0.58), (0.0, 0.58)]]
    for i, pts in enumerate(panes):
        pane(pts, cols[i])
    p.line(0, -0.5, 0, 0.58, lead, 0.07)
    p.line(-0.65, 0.05, 0.65, 0.05, lead, 0.07)
    p.circle(0, 0.05, 0.16, glow, outline=False)                               # núcleo de luz
    # cabeça: rosácea
    p.circle(0, -1.05, 0.55, (150, 140, 135))
    for k in range(8):
        a0 = k * 45
        p.poly([(0, -1.05)] + _arc(0, -1.05, 0.46, a0, a0 + 45, 3), cols[k % 6], outline=False)
    for k in range(8):
        a = math.radians(k * 45)
        p.line(0, -1.05, math.cos(a) * 0.46, -1.05 + math.sin(a) * 0.46, lead, 0.05)
    p.circle(0, -1.05, 0.18, glow, outline=False)
    eye(p, -0.08, -1.08, (40, 40, 60), 0.05)
    eye(p, 0.08, -1.08, (40, 40, 60), 0.05)
    for k in range(4):                                                         # cacos flutuando
        a = math.radians(frame * 25 + k * 90 + 20)
        x, y = math.cos(a) * 1.75, math.sin(a) * 0.9 - 0.4
        p.poly([(x, y - 0.12), (x + 0.1, y + 0.08), (x - 0.1, y + 0.06)], cols[k + 1])


def draw_espectro(p, col, frame, eye_col=(120, 220, 255)):
    """Espectro: gato-fantasma de capuz e manto esfarrapado que vira fumaça, olhos acesos e correntes."""
    bob = 0.08 if frame % 2 else -0.08
    dark = _shade(col, 0.72)
    # manto esfarrapado (afina em fumaça embaixo)
    pts = [(-0.85, -0.25 + bob), (0.85, -0.25 + bob)]
    for i in range(6):
        x = 0.85 - i * 0.34
        pts.append((x * (0.85 - i * 0.03), 1.0 + bob + (0.3 if i % 2 else 0) - i * 0.04))
    p.poly(pts, col)
    for x in (-0.4, 0.05, 0.45):                                               # dobras
        p.line(x, 0.0 + bob, x * 0.8, 0.85 + bob, dark, 0.05)
    for sx in (-1, 1):                                                         # mangas-garras
        p.poly([(0.75 * sx, -0.1 + bob), (1.35 * sx, 0.25 + bob), (1.2 * sx, 0.55 + bob), (0.8 * sx, 0.3 + bob)], col)
        for k in range(3):
            p.line(1.25 * sx, 0.45 + bob, 1.45 * sx, 0.55 + bob + k * 0.1, (200, 210, 230), 0.04)
    # capuz com orelhinhas de gato
    hx, hy = 0.0, -0.7 + bob
    cp.ears(p, hx, hy, 0.62, col, inner=dark, spread=40, size=0.5)
    p.circle(hx, hy, 0.65, col)
    p.circle(hx + 0.05, hy + 0.05, 0.46, (25, 22, 40), outline=False)          # rosto na sombra
    for x in (-0.15, 0.2):
        eye(p, hx + x, hy + 0.02, eye_col, 0.1)
    cp.muzzle(p, hx + 0.03, hy + 0.22, 0.26, nose=eye_col, whisker=(150, 160, 190))
    for sx in (-1, 1):                                                         # correntes
        for k in range(3):
            p.circle(0.6 * sx + 0.12 * k * sx, 0.35 + bob + k * 0.2, 0.08, (150, 150, 160))


DRAWERS = {
    "lobo": draw_lobo, "cao": draw_cao, "rato": draw_rato, "rei_rato": draw_rei_rato, "guardiao": draw_guardiao,
    "besouro": draw_besouro, "matriarca": draw_matriarca, "verme": draw_verme, "wyrm": draw_wyrm,
    "goblin": draw_goblin, "rei_goblin": draw_rei_goblin, "inquisidor": draw_inquisidor, "vitral": draw_vitral,
    "espectro": draw_espectro,
}
FLIPPABLE = {"lobo", "cao", "rato", "rei_rato", "guardiao", "besouro", "matriarca", "verme", "wyrm", "goblin",
             "rei_goblin", "inquisidor"}
FRAMES = {k: 2 for k in DRAWERS}
