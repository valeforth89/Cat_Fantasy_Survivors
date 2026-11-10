"""Cenários dos biomas novos: Cidade Abandonada, Catedral e Subterrâneo (5 variações cada, como a floresta).

Cada paleta (uma por fase) diz o tema e as cores; o Scenery (scenery.py) usa estas funções para gerar:
- o ladrilho do chão (repete sem emenda),
- os obstáculos (como as árvores da floresta: só a party colide) com o raio de colisão de cada um,
- a decoração do chão (não bloqueia).
"""
import math
import random

import pygame

TILE = 512


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


# ------------------------------------------------------------------ paletas (índice = fase 5..19)
TOWN = [
    dict(theme="town", ground=(101, 86, 67), ground2=(89, 75, 58), stone=(120, 113, 103), roof=(140, 60, 45),
         wall=(170, 150, 120), weed=(90, 120, 60), obstacles=(2, 4)),
    dict(theme="town", ground=(106, 89, 68), ground2=(94, 79, 60), stone=(129, 120, 107), roof=(60, 90, 140),
         wall=(180, 160, 130), weed=(90, 120, 60), obstacles=(2, 4), market=True),
    dict(theme="town", ground=(84, 87, 73), ground2=(73, 77, 65), stone=(103, 106, 96), roof=(80, 70, 70),
         wall=(140, 140, 125), weed=(110, 130, 80), obstacles=(2, 4), graves=True),
    dict(theme="town", ground=(60, 53, 48), ground2=(49, 44, 41), stone=(82, 77, 73), roof=(40, 34, 32),
         wall=(90, 80, 72), weed=(70, 70, 50), obstacles=(3, 5), burnt=True),
    dict(theme="town", ground=(53, 56, 73), ground2=(44, 48, 63), stone=(77, 82, 103), roof=(60, 50, 80),
         wall=(110, 110, 140), weed=(60, 90, 80), obstacles=(3, 5), night=True),
]
CATHEDRAL = [
    dict(theme="cathedral", ground=(111, 108, 103), ground2=(97, 94, 91), accent=(150, 40, 50),
         pillar=(185, 180, 170), glass=[(200, 60, 70), (70, 130, 210), (240, 200, 70)], obstacles=(2, 4),
         carpet=True),
    dict(theme="cathedral", ground=(97, 87, 85), ground2=(85, 75, 74), accent=(170, 30, 40),
         pillar=(170, 155, 150), glass=[(200, 60, 70), (230, 120, 60)], obstacles=(2, 4), banners=True),
    dict(theme="cathedral", ground=(94, 97, 108), ground2=(82, 85, 96), accent=(60, 90, 160),
         pillar=(170, 175, 190), glass=[(200, 60, 70), (70, 130, 210), (240, 200, 70), (90, 180, 110),
                                       (160, 90, 200)], obstacles=(2, 4), shards=True),
    dict(theme="cathedral", ground=(82, 79, 75), ground2=(70, 66, 64), accent=(90, 60, 110),
         pillar=(125, 120, 112), glass=[(120, 100, 150)], obstacles=(3, 5), crypt=True),
    dict(theme="cathedral", ground=(86, 81, 100), ground2=(73, 68, 88), accent=(120, 70, 160),
         pillar=(140, 130, 160), glass=[(160, 90, 200), (90, 60, 140)], obstacles=(3, 5), tower=True),
]
UNDERGROUND = [
    dict(theme="underground", ground=(77, 64, 53), ground2=(66, 55, 46), rock=(110, 96, 84), crystal=(230, 200, 120),
         obstacles=(2, 4), mine=True),
    dict(theme="underground", ground=(71, 64, 51), ground2=(60, 55, 44), rock=(104, 94, 80), crystal=(240, 200, 80),
         obstacles=(2, 4), gold=True),
    dict(theme="underground", ground=(53, 66, 57), ground2=(44, 57, 49), rock=(84, 100, 90), crystal=(120, 220, 140),
         obstacles=(3, 5), slime=True),
    dict(theme="underground", ground=(49, 55, 73), ground2=(42, 46, 64), rock=(80, 88, 112), crystal=(140, 220, 255),
         obstacles=(3, 5), crystals=True),
    dict(theme="underground", ground=(55, 40, 36), ground2=(44, 33, 31), rock=(80, 62, 58), crystal=(255, 130, 50),
         obstacles=(3, 5), lava=True),
]
# (pixel art: chão mais escuro, tons sóbrios no estilo gótico)
import scenery_inferno as _inf   # noqa: E402  (Inferno, fases 20-24)

PALETTES = TOWN + CATHEDRAL + UNDERGROUND + _inf.INFERNO


# ------------------------------------------------------------------ chão
# ------------------------------------------------------------------ obstáculos
def _house(pal, rnd, burnt=False):
    """Casa abandonada: enxaimel, telhado de telhas em fileiras com buraco, chaminé, porta de tábuas e janelas."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (10, 74, 102, 30))
    wall = _shade(pal["wall"], 0.6 if burnt else 1.0)
    beam = (70, 48, 34) if not burnt else (34, 28, 24)
    body = pygame.Rect(22, 50, 76, 44)
    pygame.draw.rect(s, wall, body)
    for y in range(body.y + 6, body.bottom, 7):   # reboco gasto
        for x in range(body.x + 3 + (y % 2) * 4, body.right - 3, 9):
            if rnd.random() < 0.35:
                pygame.draw.line(s, _shade(wall, 0.85), (x, y), (x + 3, y), 1)
    for x in (body.x, body.x + 25, body.x + 50, body.right - 4):   # vigas
        pygame.draw.rect(s, beam, (x, body.y, 4, body.h))
    pygame.draw.rect(s, beam, (body.x, body.y, body.w, 4))
    pygame.draw.line(s, beam, (body.x + 4, body.bottom - 2), (body.x + 25, body.y + 4), 2)
    pygame.draw.rect(s, _shade(pal["stone"], 0.9), (body.x - 2, body.bottom - 6, body.w + 4, 8))   # alicerce
    roof = pal["roof"] if not burnt else _shade(pal["roof"], 0.5)
    pts = [(12, 56), (60, 14), (108, 56)]
    pygame.draw.polygon(s, roof, pts)
    for k in range(6):   # fileiras de telhas
        y = 22 + k * 6
        half = (y - 14) * 1.0
        pygame.draw.line(s, _shade(roof, 0.7), (60 - half, y + 2), (60 + half, y + 2), 1)
        for x in range(int(60 - half) + (k % 2) * 3, int(60 + half), 6):
            pygame.draw.line(s, _shade(roof, 0.78), (x, y - 3), (x, y + 2), 1)
    pygame.draw.line(s, _shade(roof, 1.3), (12, 56), (60, 14), 2)
    pygame.draw.polygon(s, _shade(roof, 0.55), pts, 2)
    pygame.draw.rect(s, _shade(pal["stone"], 0.85), (78, 18, 10, 24))   # chaminé
    pygame.draw.rect(s, _shade(pal["stone"], 0.6), (76, 16, 14, 4))
    if burnt or rnd.random() < 0.6:   # buraco no telhado com caibros aparecendo
        hole = [(44, 36), (58, 30), (66, 44), (50, 48)]
        pygame.draw.polygon(s, (26, 22, 20), hole)
        pygame.draw.line(s, beam, (46, 46), (62, 32), 2)
    door = pygame.Rect(52, 70, 16, 24)   # porta de tábuas
    pygame.draw.rect(s, (92, 62, 40), door)
    for x in (door.x + 5, door.x + 10):
        pygame.draw.line(s, (62, 42, 28), (x, door.y + 1), (x, door.bottom - 1), 1)
    pygame.draw.circle(s, (200, 170, 80), (door.right - 3, door.centery), 1)
    win = (255, 200, 90) if pal.get("night") else (34, 30, 36)
    for wx in (30, 78):
        pygame.draw.rect(s, win, (wx, 60, 12, 11))
        pygame.draw.line(s, beam, (wx + 6, 60), (wx + 6, 70), 1)
        pygame.draw.rect(s, (90, 60, 40), (wx - 4, 59, 4, 13))   # venezianas
        pygame.draw.rect(s, (90, 60, 40), (wx + 12, 59, 4, 13))
    pygame.draw.line(s, (120, 85, 55), (76, 58), (94, 72), 3)   # tábua pregada na janela
    if burnt:
        for _ in range(5):
            x = rnd.uniform(26, 94)
            pygame.draw.line(s, (20, 18, 16), (x, 52), (x + rnd.uniform(-6, 6), 92), 3)
    return s


def _well(pal):
    """Poço de pedra: anel de tijolos com luz e sombra, água escura, telhadinho de tábuas, manivela, corda e balde."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    st = pal["stone"]
    hi, lo, dk = _shade(st, 1.2), _shade(st, 0.75), _shade(st, 0.55)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 36, c + 6, 74, 26))
    pygame.draw.ellipse(s, lo, (c - 28, c - 6, 56, 34))                       # parede do poço
    pygame.draw.rect(s, lo, (c - 28, c + 2, 56, 10))
    for row in range(2):                                                      # tijolos
        for k in range(7):
            x = c - 28 + k * 8 + (4 if row else 0)
            pygame.draw.rect(s, st if (k + row) % 2 else _shade(st, 0.9), (x, c + 4 + row * 6, 7, 5))
            pygame.draw.line(s, hi, (x, c + 4 + row * 6), (x + 6, c + 4 + row * 6), 1)
    pygame.draw.ellipse(s, st, (c - 28, c - 12, 56, 24))                      # borda de cima
    pygame.draw.ellipse(s, hi, (c - 28, c - 12, 56, 24), 2)
    pygame.draw.ellipse(s, (18, 22, 32), (c - 20, c - 8, 40, 16))             # água escura
    pygame.draw.line(s, (90, 110, 140), (c - 8, c - 2), (c + 2, c - 2), 1)    # reflexo
    wood, wood_d = (110, 76, 48), (70, 48, 30)
    for x in (c - 24, c + 22):                                                # postes
        pygame.draw.rect(s, wood, (x, c - 38, 5, 34))
        pygame.draw.line(s, wood_d, (x + 4, c - 38), (x + 4, c - 4), 1)
    pygame.draw.line(s, wood_d, (c - 22, c - 30), (c + 26, c - 30), 3)        # eixo com manivela
    pygame.draw.lines(s, (90, 90, 96), False, [(c + 27, c - 30), (c + 32, c - 30), (c + 32, c - 24)], 2)
    pygame.draw.line(s, (180, 160, 120), (c, c - 30), (c, c - 14), 1)         # corda e balde
    pygame.draw.polygon(s, wood, [(c - 4, c - 14), (c + 4, c - 14), (c + 3, c - 6), (c - 3, c - 6)])
    pygame.draw.line(s, (90, 90, 96), (c - 4, c - 11), (c + 4, c - 11), 1)
    roof = pal["roof"]
    pts = [(c - 34, c - 34), (c, c - 54), (c + 34, c - 34)]                   # telhadinho de tábuas
    pygame.draw.polygon(s, roof, pts)
    for k in range(1, 4):
        y = c - 54 + k * 5
        w = k * 8.5
        pygame.draw.line(s, _shade(roof, 0.7), (c - w, y), (c + w, y), 1)
    pygame.draw.line(s, _shade(roof, 1.3), pts[0], pts[1], 2)
    pygame.draw.polygon(s, _shade(roof, 0.55), pts, 2)
    return s


def _cart(pal, rnd):
    """Carroça abandonada: tábuas, rodas com raios (uma quebrada), varais, sacos e caixotes; no mercado, toldo listrado."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    wood, wood_d, wood_l = (122, 86, 54), (78, 54, 34), (150, 110, 72)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 44, c + 10, 88, 22))
    pygame.draw.line(s, wood_d, (c + 26, c + 6), (c + 52, c - 4), 4)          # varais
    pygame.draw.line(s, wood_d, (c + 26, c + 12), (c + 54, c + 4), 3)
    bed = pygame.Rect(c - 36, c - 8, 64, 22)                                  # caçamba de tábuas
    pygame.draw.rect(s, wood, bed)
    for y in (bed.y + 7, bed.y + 14):
        pygame.draw.line(s, wood_d, (bed.x, y), (bed.right, y), 1)
    pygame.draw.line(s, wood_l, bed.topleft, bed.topright, 2)
    for x in (bed.x + 2, bed.right - 4):
        pygame.draw.rect(s, (90, 90, 96), (x, bed.y, 2, bed.h))               # ferragens
    pygame.draw.rect(s, wood_d, bed, 1)
    for wx, broken in ((c - 24, False), (c + 18, True)):                      # rodas com raios
        pygame.draw.circle(s, wood_d, (wx, c + 18), 11, 3)
        for a in range(0, 360, 45):
            if broken and 90 < a < 250:
                continue
            pygame.draw.line(s, wood, (wx, c + 18), (wx + math.cos(math.radians(a)) * 9, c + 18 + math.sin(math.radians(a)) * 9), 1)
        pygame.draw.circle(s, (90, 90, 96), (wx, c + 18), 2)
        if broken:
            pygame.draw.arc(s, (0, 0, 0, 0), (wx - 12, c + 6, 24, 24), 1.8, 4.0, 4)
    if pal.get("market"):   # toldo listrado com estacas e caixotes de fruta
        for x in (bed.x + 2, bed.right - 4):
            pygame.draw.line(s, wood_d, (x, bed.y), (x, bed.y - 26), 2)
        for k in range(5):
            col = (190, 60, 56) if k % 2 else (232, 220, 192)
            pygame.draw.polygon(s, col, [(bed.x - 2 + k * 14, bed.y - 34), (bed.x + 12 + k * 14, bed.y - 34),
                                         (bed.x + 12 + k * 14, bed.y - 26), (bed.x + 5 + k * 14, bed.y - 22),
                                         (bed.x - 2 + k * 14, bed.y - 26)])
        for k, fc in enumerate(((200, 60, 50), (230, 180, 60), (120, 170, 70))):
            pygame.draw.rect(s, wood_l, (bed.x + 4 + k * 20, bed.y - 8, 16, 9))
            for q in range(3):
                pygame.draw.circle(s, fc, (bed.x + 8 + k * 20 + q * 4, bed.y - 9), 2)
    else:
        sack = (196, 176, 130)                                                # sacos e caixote
        for x in (bed.x + 8, bed.x + 22):
            pygame.draw.ellipse(s, sack, (x, bed.y - 12, 14, 16))
            pygame.draw.line(s, _shade(sack, 0.7), (x + 7, bed.y - 12), (x + 7, bed.y - 8), 2)
        crate = pygame.Rect(bed.x + 38, bed.y - 14, 18, 15)
        pygame.draw.rect(s, wood_l, crate)
        pygame.draw.line(s, wood_d, crate.topleft, crate.bottomright, 2)
        pygame.draw.rect(s, wood_d, crate, 1)
    return s


def _grave(pal):
    """Túmulo: lápide arredondada com cruz entalhada e epitáfio, trinca, musgo, monte de terra, flores e vela."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    st = pal["stone"]
    hi, lo, dk = _shade(st, 1.22), _shade(st, 0.75), _shade(st, 0.5)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 28, c + 8, 56, 18))
    pygame.draw.ellipse(s, (82, 66, 50), (c - 20, c + 4, 40, 18))             # monte de terra
    pygame.draw.ellipse(s, (100, 82, 62), (c - 16, c + 5, 30, 8))
    stone = pygame.Rect(c - 16, c - 30, 32, 38)
    pygame.draw.rect(s, st, stone, border_top_left_radius=14, border_top_right_radius=14)
    pygame.draw.rect(s, hi, (stone.x, stone.y + 8, 5, stone.h - 8))
    pygame.draw.rect(s, lo, (stone.right - 5, stone.y + 8, 5, stone.h - 8))
    pygame.draw.rect(s, dk, stone, 2, border_top_left_radius=14, border_top_right_radius=14)
    pygame.draw.line(s, dk, (c, c - 24), (c, c - 10), 2)                      # cruz entalhada
    pygame.draw.line(s, dk, (c - 6, c - 19), (c + 6, c - 19), 2)
    for y in (c - 4, c + 1):                                                  # epitáfio
        pygame.draw.line(s, lo, (c - 8, y), (c + 8, y), 1)
    pygame.draw.lines(s, dk, False, [(c + 9, c - 28), (c + 6, c - 20), (c + 10, c - 12)], 1)   # trinca
    pygame.draw.line(s, (90, 125, 65), (c - 14, c + 6), (c - 8, c + 6), 2)    # musgo
    for (x, col) in ((c - 18, (200, 70, 90)), (c - 13, (230, 210, 120))):     # flores
        pygame.draw.line(s, (80, 110, 60), (x, c + 14), (x, c + 8), 1)
        pygame.draw.circle(s, col, (x, c + 7), 2)
    pygame.draw.rect(s, (232, 224, 202), (c + 14, c + 6, 4, 8))               # vela
    pygame.draw.ellipse(s, (255, 200, 90), (c + 14, c, 4, 6))
    return s


def _stone_cols(base):
    return _shade(base, 1.18), base, _shade(base, 0.78), _shade(base, 0.58)


def _ivy(s, rnd, x, y0, y1, n=6):
    """Hera / musgo subindo pela pedra."""
    for k in range(n):
        yy = y1 - (y1 - y0) * k / n
        xx = x + math.sin(k * 1.3) * 3
        pygame.draw.circle(s, (70, 100, 55) if k % 2 else (90, 125, 65), (xx, yy), 2)


def _pillar(pal, rnd, broken=False):
    """Coluna gótica: base em degraus, feixe de colunas (central + duas finas) com luz e sombra, blocos,
    capitel com folhas entalhadas, hera e trincas. Quebrada: fuste partido e pedaços caídos."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    hi, mid, lo, dk = _stone_cols(pal["pillar"])
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 38, c + 6, 78, 28))
    pygame.draw.rect(s, lo, (c - 30, c + 10, 60, 10))                        # degraus da base
    pygame.draw.rect(s, mid, (c - 26, c + 2, 52, 10))
    pygame.draw.line(s, hi, (c - 26, c + 2), (c + 25, c + 2), 2)
    pygame.draw.line(s, hi, (c - 30, c + 10), (c + 29, c + 10), 1)
    top = c - 10 if broken else c - 48
    for dx, w in ((-14, 8), (14, 8)):                                       # colunetas laterais
        r = pygame.Rect(c + dx - w // 2, top + 6, w, c + 2 - top - 6)
        pygame.draw.rect(s, lo, r)
        pygame.draw.line(s, mid, (r.x + 1, r.y), (r.x + 1, r.bottom), 2)
    shaft = pygame.Rect(c - 10, top, 20, c + 2 - top)                       # fuste central
    pygame.draw.rect(s, mid, shaft)
    pygame.draw.rect(s, hi, (shaft.x, shaft.y, 6, shaft.h))
    pygame.draw.rect(s, lo, (shaft.right - 5, shaft.y, 5, shaft.h))
    for yy in range(top + 12, c, 12):                                       # juntas dos blocos
        pygame.draw.line(s, dk, (shaft.x, yy), (shaft.right, yy), 1)
    if broken:
        jag = [(c - 18, top + 6), (c - 12, top - 8), (c - 4, top - 2), (c + 3, top - 14), (c + 10, top - 4),
               (c + 18, top + 6)]
        pygame.draw.polygon(s, mid, jag + [(c + 18, top + 10), (c - 18, top + 10)])
        pygame.draw.lines(s, hi, False, jag[:4], 2)
        for (x, y, w, h) in ((c + 24, c + 12, 22, 12), (c - 46, c + 14, 16, 10)):   # pedaços caídos
            pygame.draw.rect(s, mid, (x, y, w, h))
            pygame.draw.line(s, hi, (x, y), (x + w, y), 2)
            pygame.draw.rect(s, dk, (x, y, w, h), 1)
        for k in range(5):
            pygame.draw.circle(s, lo, (c + rnd.uniform(-34, 36), c + 22 + rnd.uniform(-3, 3)), 2)
    else:
        cap = [(c - 22, top), (c + 22, top), (c + 16, top + 10), (c - 16, top + 10)]   # capitel
        pygame.draw.polygon(s, mid, cap)
        pygame.draw.rect(s, hi, (c - 25, top - 6, 50, 7))                   # ábaco
        pygame.draw.rect(s, dk, (c - 25, top - 6, 50, 7), 1)
        for x in (-14, -5, 4, 13):                                          # folhas entalhadas
            pygame.draw.polygon(s, lo, [(c + x, top + 9), (c + x + 3, top + 1), (c + x + 6, top + 9)])
            pygame.draw.line(s, hi, (c + x + 3, top + 2), (c + x + 3, top + 7), 1)
    _ivy(s, rnd, c - 9, c - 18, c, 7)                                        # hera
    pygame.draw.lines(s, dk, False, [(c + 4, top + 20), (c + 1, top + 28), (c + 5, top + 34)], 1)   # trinca
    return s


def _statue(pal):
    """Estátua de anjo-gato rezando sobre um pedestal com placa: capuz com orelhas, asas dobradas, manto em
    dobras, auréola, musgo escorrendo e trincas."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    hi, mid, lo, dk = _stone_cols(_shade(pal["pillar"], 0.95))
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 34, c + 8, 68, 26))
    ped = pygame.Rect(c - 22, c + 2, 44, 18)                                # pedestal
    pygame.draw.rect(s, lo, ped)
    pygame.draw.rect(s, mid, (ped.x + 3, ped.y - 4, ped.w - 6, 6))
    pygame.draw.line(s, hi, (ped.x + 3, ped.y - 4), (ped.right - 4, ped.y - 4), 2)
    pygame.draw.rect(s, (150, 130, 80), (c - 9, ped.y + 6, 18, 7))          # placa de bronze
    pygame.draw.line(s, (100, 85, 50), (c - 6, ped.y + 9), (c + 6, ped.y + 9), 1)
    for sx in (-1, 1):                                                      # asas dobradas (penas em camadas)
        for k in range(3):
            pts = [(c + 5 * sx, c - 34 + k * 6), (c + (24 - k * 3) * sx, c - 44 + k * 10),
                   (c + (20 - k * 3) * sx, c - 6 + k * 2), (c + 8 * sx, c - 6)]
            pygame.draw.polygon(s, (hi if sx < 0 else lo) if k == 0 else mid, pts)
            pygame.draw.polygon(s, dk, pts, 1)
    robe = [(c - 13, c - 2), (c - 9, c - 30), (c + 9, c - 30), (c + 13, c - 2)]   # manto
    pygame.draw.polygon(s, mid, robe)
    pygame.draw.polygon(s, hi, [(c - 13, c - 2), (c - 9, c - 30), (c - 3, c - 30), (c - 5, c - 2)])
    for x in (-4, 3, 8):                                                    # dobras
        pygame.draw.line(s, lo, (c + x, c - 20), (c + x + 1, c - 3), 1)
    pygame.draw.polygon(s, hi, [(c - 4, c - 26), (c + 4, c - 26), (c + 2, c - 16), (c - 2, c - 16)])   # mãos rezando
    head = (c, c - 37)
    for sx in (-1, 1):                                                      # orelhas de gato no capuz
        pygame.draw.polygon(s, mid, [(c + 3 * sx, c - 43), (c + 8 * sx, c - 53), (c + 9 * sx, c - 40)])
    pygame.draw.circle(s, mid, head, 8)
    pygame.draw.circle(s, hi, (head[0] - 2, head[1] - 2), 5)
    pygame.draw.line(s, dk, (c - 4, c - 37), (c - 1, c - 37), 1)            # olhos fechados
    pygame.draw.line(s, dk, (c + 1, c - 37), (c + 4, c - 37), 1)
    pygame.draw.ellipse(s, (210, 190, 110), (c - 11, c - 56, 22, 7), 2)     # auréola
    for x, h in ((-6, 14), (5, 10)):                                         # musgo escorrendo
        pygame.draw.line(s, (80, 110, 60), (c + x, c - 30), (c + x, c - 30 + h), 1)
    pygame.draw.lines(s, dk, False, [(c + 7, c - 46), (c + 4, c - 40), (c + 7, c - 35)], 1)   # trinca
    return s


def _coffin(pal):
    """Sarcófago de pedra: tampa entalhada com a figura de um cavaleiro-gato, tampa aberta numa fresta e velas."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    hi, mid, lo, dk = _stone_cols(_shade(pal["pillar"], 0.85))
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 30, c + 12, 60, 20))
    box = pygame.Rect(c - 18, c - 30, 36, 50)
    pygame.draw.rect(s, lo, box.move(0, 4))                                 # caixa
    pygame.draw.rect(s, dk, (box.x, box.bottom - 2, box.w, 6))
    lid = box.move(4, -4)                                                   # tampa deslocada (fresta escura)
    pygame.draw.rect(s, (20, 16, 20), (box.x, box.y + 2, 6, box.h))
    pygame.draw.rect(s, mid, lid)
    pygame.draw.line(s, hi, lid.topleft, lid.topright, 2)
    pygame.draw.line(s, hi, lid.topleft, lid.bottomleft, 2)
    pygame.draw.rect(s, dk, lid, 1)
    fx = lid.centerx                                                        # efígie entalhada
    pygame.draw.circle(s, hi, (fx, lid.y + 9), 5)
    for sx in (-1, 1):
        pygame.draw.polygon(s, hi, [(fx + 2 * sx, lid.y + 6), (fx + 5 * sx, lid.y + 1), (fx + 5 * sx, lid.y + 7)])
    pygame.draw.polygon(s, lo, [(fx - 7, lid.y + 15), (fx + 7, lid.y + 15), (fx + 5, lid.bottom - 4), (fx - 5, lid.bottom - 4)])
    pygame.draw.line(s, hi, (fx, lid.y + 16), (fx, lid.bottom - 8), 2)       # espada sobre o peito
    pygame.draw.line(s, hi, (fx - 4, lid.y + 20), (fx + 4, lid.y + 20), 2)
    for (x, y, h) in ((c - 26, c + 8, 10), (c + 28, c + 4, 14)):            # velas
        pygame.draw.rect(s, (230, 222, 200), (x - 2, y - h, 4, h))
        pygame.draw.line(s, (240, 235, 220), (x - 2, y - h), (x - 2, y - h + 4), 1)
        pygame.draw.ellipse(s, (255, 200, 90), (x - 2, y - h - 6, 4, 6))
    return s


def _candelabra(pal):
    """Candelabro de ferro alto com três velas acesas e cera escorrendo."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    iron, iron_l = (52, 48, 56), (96, 90, 104)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 18, c + 12, 36, 12))
    pygame.draw.polygon(s, iron, [(c - 12, c + 18), (c + 12, c + 18), (c + 3, c + 8), (c - 3, c + 8)])   # pé
    pygame.draw.line(s, iron, (c, c + 8), (c, c - 30), 3)                   # haste
    pygame.draw.line(s, iron_l, (c - 1, c + 6), (c - 1, c - 28), 1)
    pygame.draw.circle(s, iron, (c, c - 8), 4)
    pygame.draw.lines(s, iron, False, [(c - 20, c - 30), (c - 18, c - 22), (c, c - 18), (c + 18, c - 22),
                                       (c + 20, c - 30)], 3)               # braços
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    for x in (c - 20, c, c + 20):
        pygame.draw.circle(glow, (255, 190, 90, 45), (x, c - 46), 12)
    s.blit(glow, (0, 0))
    for x, h in ((c - 20, 10), (c, 14), (c + 20, 9)):
        pygame.draw.rect(s, iron, (x - 4, c - 32, 8, 3))                    # pratinhos
        pygame.draw.rect(s, (232, 224, 202), (x - 2, c - 32 - h, 5, h))
        pygame.draw.line(s, (250, 246, 232), (x - 2, c - 32 - h), (x - 2, c - 34), 1)
        pygame.draw.line(s, (232, 224, 202), (x + 3, c - 32 - h + 3), (x + 3, c - 30), 1)   # cera escorrendo
        pygame.draw.ellipse(s, (255, 210, 110), (x - 2, c - 40 - h, 5, 8))
        pygame.draw.ellipse(s, (255, 250, 220), (x - 1, c - 37 - h, 3, 4))
    return s


def _pew(pal):
    """Banco de igreja de madeira escura, com encosto entalhado (um deles tombado)."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    wood, wood_d, wood_l = (92, 58, 40), (62, 38, 26), (122, 80, 54)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 46, c + 4, 92, 20))
    pygame.draw.rect(s, wood, (c - 42, c - 22, 84, 14))                     # encosto
    for x in range(c - 36, c + 40, 12):
        pygame.draw.polygon(s, wood_d, [(x, c - 20), (x + 4, c - 16), (x, c - 12), (x - 4, c - 16)])
    pygame.draw.line(s, wood_l, (c - 42, c - 22), (c + 41, c - 22), 2)
    pygame.draw.rect(s, wood_l, (c - 44, c - 8, 88, 8))                     # assento
    pygame.draw.line(s, wood_d, (c - 44, c), (c + 43, c), 2)
    for x in (c - 40, c + 36):                                              # laterais com arco
        pygame.draw.rect(s, wood_d, (x, c - 26, 6, 40))
        pygame.draw.circle(s, wood, (x + 3, c - 26), 4)
    pygame.draw.line(s, wood_d, (c - 10, c - 22), (c - 4, c - 8), 1)         # rachadura
    return s


def _stalagmite(pal, rnd):
    """Estalagmites: pontas de rocha em camadas, com faixas minerais, face de luz, gotas e cascalho na base."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 36, c + 6, 74, 26))
    for dx, h, w in ((-18, 38, 13), (16, 30, 11), (0, 58, 17), (-8, 20, 8), (26, 16, 7)):
        col = _shade(pal["rock"], rnd.uniform(0.88, 1.12))
        base_y = c + 16
        pts = [(c + dx - w, base_y), (c + dx - w * 0.35, base_y - h * 0.6), (c + dx, base_y - h),
               (c + dx + w * 0.4, base_y - h * 0.55), (c + dx + w, base_y)]
        pygame.draw.polygon(s, col, pts)
        pygame.draw.polygon(s, _shade(col, 1.25), [pts[0], pts[1], pts[2], (c + dx - w * 0.1, base_y)])   # face de luz
        for k in range(1, 4):                                                 # faixas minerais
            y = base_y - h * k / 4.5
            half = w * (1 - k / 4.5)
            pygame.draw.line(s, _shade(col, 0.8), (c + dx - half, y), (c + dx + half, y + 1), 1)
        pygame.draw.polygon(s, _shade(col, 0.55), pts, 2)
    for _ in range(6):                                                        # cascalho
        x = c + rnd.uniform(-30, 30)
        pygame.draw.polygon(s, _shade(pal["rock"], 0.85), [(x, c + 20), (x + 3, c + 16), (x + 6, c + 20)])
    cr = pal["crystal"]
    pygame.draw.circle(s, (150, 190, 220), (c + 1, c - 40), 2)                # gota
    pygame.draw.circle(s, cr, (c - 18, c - 2), 2)                             # pontinho de minério
    return s


def _boulder(pal, rnd):
    """Rochedo de pedras angulosas com faces de luz e sombra (e veios de ouro/gosma conforme a fase)."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 80), (c - 40, c + 4, 82, 28))
    rocks = ((-14, 4, 24), (14, 2, 22), (0, -14, 22), (24, 14, 12), (-28, 14, 10))
    for dx, dy, r in rocks:
        base = _shade(pal["rock"], rnd.uniform(0.85, 1.1))
        n = 6
        pts = []
        for k in range(n):
            a = math.radians(k * 360 / n + rnd.uniform(-18, 18))
            rr = r * rnd.uniform(0.8, 1.05)
            pts.append((c + dx + math.cos(a) * rr, c + dy + math.sin(a) * rr * 0.85))
        pygame.draw.polygon(s, base, pts)
        top = [p for p in pts if p[1] <= c + dy] + [(c + dx, c + dy)]
        if len(top) >= 3:
            pygame.draw.polygon(s, _shade(base, 1.2), top)   # face de cima pega luz
        pygame.draw.line(s, _shade(base, 0.7), (c + dx - r * 0.5, c + dy + r * 0.3), (c + dx + r * 0.4, c + dy + r * 0.5), 2)
        pygame.draw.polygon(s, _shade(base, 0.55), pts, 2)
    if pal.get("gold"):   # veio de ouro
        for _ in range(5):
            x, y = c + rnd.uniform(-22, 22), c + rnd.uniform(-22, 8)
            pygame.draw.line(s, (240, 200, 80), (x, y), (x + 4, y + 2), 2)
    if pal.get("slime"):
        pygame.draw.ellipse(s, (110, 200, 120), (c - 20, c - 30, 30, 10))
        pygame.draw.line(s, (110, 200, 120), (c - 8, c - 22), (c - 8, c - 12), 3)
    return s


def _crystal(pal, rnd):
    """Aglomerado de cristais: prismas facetados (face clara e escura) brotando de uma base de rocha."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    col = pal["crystal"]
    light, dark = _shade(col, 1.3), _shade(col, 0.62)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 32, c + 8, 64, 22))
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    for y in range(0, 120, 2):   # brilho pontilhado em volta
        for x in range(0, 120, 2):
            d = ((x - c) ** 2 + (y - c + 14) ** 2) ** 0.5
            if d < 46 and ((x // 2 + y // 2) % 2 == 0) and d > 18:
                pygame.draw.rect(glow, (*col, int(50 * (1 - d / 46))), (x, y, 2, 2))
    s.blit(glow, (0, 0))
    base = _shade(pal["rock"], 0.9)
    pygame.draw.polygon(s, base, [(c - 30, c + 16), (c - 22, c + 4), (c + 20, c + 2), (c + 32, c + 16)])
    pygame.draw.polygon(s, _shade(base, 0.6), [(c - 30, c + 16), (c - 22, c + 4), (c + 20, c + 2), (c + 32, c + 16)], 2)
    shards = ((-16, 30, -0.4, 7), (14, 26, 0.35, 7), (0, 48, 0.0, 9), (-6, 20, -0.75, 5), (24, 16, 0.8, 5))
    for dx, h, ang, w in shards:
        bx, by = c + dx, c + 8
        tx, ty = bx + math.sin(ang) * h, by - math.cos(ang) * h
        nx, ny = math.cos(ang) * w, math.sin(ang) * w
        sh = 0.75 * h   # onde começa a ponta
        mx, my = bx + math.sin(ang) * sh, by - math.cos(ang) * sh
        left = [(bx - nx, by - ny), (mx - nx, my - ny), (tx, ty), (bx, by)]
        right = [(bx, by), (tx, ty), (mx + nx, my + ny), (bx + nx, by + ny)]
        pygame.draw.polygon(s, light, left)
        pygame.draw.polygon(s, dark, right)
        pygame.draw.polygon(s, _shade(col, 0.4), [(bx - nx, by - ny), (mx - nx, my - ny), (tx, ty),
                                                  (mx + nx, my + ny), (bx + nx, by + ny)], 2)
        pygame.draw.line(s, (255, 255, 255), (bx - nx * 0.4, by - ny * 0.4 - 2), (mx - nx * 0.4, my - ny * 0.4), 1)
    return s


def _support(pal):
    """Escora da mina: vigas com veios e pregos, mão-francesa, lanterna pendurada acesa e trilho embaixo."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    pygame.draw.ellipse(s, (0, 0, 0, 70), (c - 38, c + 10, 78, 20))
    wood, dark, light = (124, 88, 52), (80, 55, 32), (156, 116, 74)
    for x in (c - 28, c + 22):                                                # pilares
        pygame.draw.rect(s, wood, (x, c - 32, 8, 50))
        pygame.draw.line(s, light, (x, c - 32), (x, c + 18), 2)
        pygame.draw.line(s, dark, (x + 5, c - 28), (x + 6, c + 10), 1)
        pygame.draw.rect(s, dark, (x, c - 32, 8, 50), 1)
    pygame.draw.rect(s, wood, (c - 34, c - 40, 70, 10))                       # viga de cima
    pygame.draw.line(s, light, (c - 34, c - 40), (c + 35, c - 40), 2)
    pygame.draw.rect(s, dark, (c - 34, c - 40, 70, 10), 1)
    for x in (c - 30, c - 24, c + 24, c + 30):
        pygame.draw.circle(s, (70, 70, 76), (x, c - 35), 1)                   # pregos
    for sx, x0 in ((1, c - 20), (-1, c + 22)):                               # mãos-francesas
        pygame.draw.line(s, wood, (x0, c - 18), (x0 + 12 * sx, c - 30), 4)
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 190, 90, 50), (c + 4, c - 12), 16)
    s.blit(glow, (0, 0))
    pygame.draw.line(s, (60, 60, 64), (c + 4, c - 30), (c + 4, c - 18), 1)   # lanterna
    pygame.draw.rect(s, (60, 58, 64), (c, c - 18, 9, 11))
    pygame.draw.rect(s, (255, 206, 110), (c + 2, c - 16, 5, 7))
    pygame.draw.line(s, (60, 58, 64), (c - 1, c - 19), (c + 9, c - 19), 2)
    for y in (c + 14, c + 20):                                                # trilho
        pygame.draw.line(s, (120, 120, 130), (c - 40, y), (c + 40, y), 2)
    for x in range(c - 36, c + 40, 10):
        pygame.draw.line(s, dark, (x, c + 12), (x, c + 22), 3)
    return s


def _lava_pool(pal):
    """Poço de lava: borda de rocha em crosta, lava em faixas de cor, núcleo claro, bolhas e brilho."""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = 60
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    for y in range(0, 120, 2):
        for x in range(0, 120, 2):
            d = ((x - c) / 50) ** 2 + ((y - c) / 32) ** 2
            if 0.7 < d < 1.3 and (x // 2 + y // 2) % 2 == 0:
                pygame.draw.rect(glow, (255, 120, 40, int(70 * (1.3 - d))), (x, y, 2, 2))
    s.blit(glow, (0, 0))
    rim = _shade(pal["rock"], 0.7)
    pygame.draw.ellipse(s, rim, (c - 40, c - 22, 80, 46))                     # borda de crosta
    for a in range(0, 360, 30):
        x, y = c + math.cos(math.radians(a)) * 38, c + math.sin(math.radians(a)) * 21
        pygame.draw.polygon(s, _shade(rim, 1.2), [(x - 5, y + 2), (x, y - 4), (x + 5, y + 2)])
    for k, col in enumerate(((190, 50, 20), (230, 90, 30), (255, 150, 50), (255, 210, 110))):
        f = 1 - k * 0.22
        pygame.draw.ellipse(s, col, (c - 32 * f, c - 16 * f, 64 * f, 32 * f))
    for (x, y, r) in ((c - 14, c - 4, 3), (c + 10, c + 4, 2), (c + 4, c - 8, 2)):   # bolhas
        pygame.draw.circle(s, (255, 230, 160), (x, y), r, 1)
    pygame.draw.lines(s, (120, 30, 20), False, [(c - 24, c + 2), (c - 10, c + 8), (c + 6, c + 6)], 1)   # crosta boiando
    return s


def make_obstacles(pal, seed):
    """[(sprite, raio de colisão)] dos obstáculos da fase."""
    rnd = random.Random(seed + 17)
    th = pal["theme"]
    if th == "inferno":
        return _inf.obstacles(pal, seed)
    if th == "town":
        burnt = pal.get("burnt")
        out = [(_house(pal, rnd, burnt), 36), (_house(pal, rnd, burnt), 36), (_well(pal), 26), (_cart(pal, rnd), 30)]
        if pal.get("graves"):
            out += [(_grave(pal), 18), (_grave(pal), 18)]
        return out
    if th == "cathedral":
        out = [(_pillar(pal, rnd), 22), (_pillar(pal, rnd, broken=True), 22), (_statue(pal), 24),
               (_candelabra(pal), 12), (_pew(pal), 26)]
        if pal.get("crypt"):
            out += [(_coffin(pal), 18), (_coffin(pal), 18)]
        return out
    out = [(_stalagmite(pal, rnd), 24), (_boulder(pal, rnd), 28)]
    if pal.get("mine"):
        out.append((_support(pal), 28))
    if pal.get("crystals") or pal.get("gold"):
        out += [(_crystal(pal, rnd), 22), (_crystal(pal, rnd), 22)]
    if pal.get("lava"):
        out += [(_lava_pool(pal), 30), (_crystal(pal, rnd), 22)]
    return out


# ------------------------------------------------------------------ decoração (não bloqueia)
def make_decor(pal, rnd):
    out = {}
    th = pal["theme"]
    if th == "inferno":
        return _inf.decor(pal, rnd)

    def surf(w, h):
        return pygame.Surface((w, h), pygame.SRCALPHA)

    if th == "town":
        wood, wood_d, wood_l = (130, 92, 58), (82, 58, 36), (160, 118, 78)
        s = surf(28, 26)                                                      # caixote de tábuas com pregos
        pygame.draw.ellipse(s, (0, 0, 0, 60), (2, 18, 24, 7))
        pygame.draw.rect(s, wood, (3, 4, 22, 18))
        for y in (9, 15):
            pygame.draw.line(s, wood_d, (3, y), (24, y), 1)
        pygame.draw.line(s, wood_d, (4, 5), (23, 20), 2)
        pygame.draw.line(s, wood_l, (3, 4), (24, 4), 2)
        for (x, y) in ((5, 6), (22, 6), (5, 19), (22, 19)):
            s.set_at((x, y), (60, 60, 66))
        pygame.draw.rect(s, wood_d, (3, 4, 22, 18), 1)
        out["crate"] = s
        s = surf(24, 26)                                                      # barril de aduelas com aros
        pygame.draw.ellipse(s, (0, 0, 0, 60), (2, 19, 20, 6))
        pygame.draw.rect(s, (120, 80, 50), (4, 6, 16, 16), border_radius=4)
        for x in (8, 12, 16):
            pygame.draw.line(s, (92, 60, 38), (x, 7), (x, 21), 1)
        pygame.draw.line(s, (150, 104, 68), (5, 7), (5, 20), 2)
        for y in (9, 18):
            pygame.draw.line(s, (70, 70, 76), (4, y), (19, y), 2)
        pygame.draw.ellipse(s, (100, 66, 40), (4, 3, 16, 7))
        pygame.draw.ellipse(s, (70, 70, 76), (4, 3, 16, 7), 1)
        out["barrel"] = s
        s = surf(34, 20)                                                      # entulho de tijolos
        st = pal["stone"]
        for (x, y, w, h, col) in ((2, 10, 10, 6, (150, 80, 60)), (11, 7, 11, 7, st), (21, 11, 10, 6, (150, 80, 60)),
                                  (14, 13, 7, 5, _shade(st, 0.85))):
            pygame.draw.rect(s, col, (x, y, w, h))
            pygame.draw.line(s, _shade(col, 1.25), (x, y), (x + w - 1, y), 1)
            pygame.draw.rect(s, _shade(col, 0.55), (x, y, w, h), 1)
        out["rubble"] = s
        s = surf(32, 14)                                                      # tábua quebrada com prego
        pygame.draw.polygon(s, wood, [(2, 9), (24, 3), (27, 5), (24, 7), (29, 7), (5, 12)])
        pygame.draw.line(s, wood_l, (3, 9), (24, 4), 1)
        pygame.draw.line(s, (90, 90, 96), (12, 6), (12, 2), 1)
        out["plank"] = s
        s = surf(26, 22)                                                      # mato com florzinha
        for i in range(7):
            col = [pal["weed"], _shade(pal["weed"], 1.3), _shade(pal["weed"], 0.75)][i % 3]
            pygame.draw.line(s, col, (4 + i * 3, 21), (4 + i * 3 + rnd.uniform(-3, 3), rnd.uniform(5, 12)), 2)
        pygame.draw.circle(s, (230, 220, 120), (16, 6), 2)
        out["weed"] = s
        s = surf(28, 20)                                                      # saco rasgado com grãos
        pygame.draw.ellipse(s, (0, 0, 0, 50), (2, 13, 24, 6))
        pygame.draw.ellipse(s, (196, 176, 130), (3, 3, 18, 15))
        pygame.draw.line(s, (150, 132, 96), (12, 3), (12, 8), 2)
        for k in range(5):
            s.set_at((20 + k, 14 + (k % 2)), (225, 205, 140))
        out["sack"] = s
        if pal.get("market"):
            s = surf(28, 20)                                                  # cesto de frutas tombado
            pygame.draw.ellipse(s, (150, 110, 64), (2, 8, 16, 11))
            for y in (11, 15):
                pygame.draw.line(s, (110, 78, 44), (3, y), (17, y), 1)
            for k, fc in enumerate(((200, 60, 50), (230, 180, 60), (120, 170, 70), (200, 60, 50))):
                pygame.draw.circle(s, fc, (8 + k * 5, 7 + (k % 2) * 6), 3)
                s.set_at((7 + k * 5, 6 + (k % 2) * 6), (255, 255, 255))
            out["fruit"] = s
        if pal.get("graves"):
            s = surf(32, 18)                                                  # ossos e caveirinha de gato
            bone = (222, 214, 194)
            pygame.draw.line(s, bone, (3, 13), (17, 11), 3)
            for p_ in ((3, 13), (17, 11)):
                pygame.draw.circle(s, bone, p_, 2)
            for sx in (-1, 1):
                pygame.draw.polygon(s, bone, [(24 + 2 * sx, 5), (24 + 5 * sx, 0), (24 + 5 * sx, 6)])
            pygame.draw.circle(s, bone, (24, 9), 5)
            pygame.draw.circle(s, (34, 28, 30), (22, 9), 1)
            pygame.draw.circle(s, (34, 28, 30), (26, 9), 1)
            out["bones"] = s
        if pal.get("burnt"):
            s = surf(24, 18)                                                  # brasas em cinzas
            pygame.draw.ellipse(s, (60, 56, 54), (1, 5, 22, 11))
            for k in range(6):
                x, y = rnd.uniform(4, 19), rnd.uniform(7, 13)
                pygame.draw.circle(s, (40, 32, 30), (x, y), 2)
                s.set_at((int(x), int(y)), (255, 130 + k * 15, 40))
            out["embers"] = s
        if pal.get("night"):
            s = surf(24, 40)                                                  # poste de lampião
            glow = surf(24, 24)
            pygame.draw.circle(glow, (255, 210, 120, 70), (12, 10), 11)
            s.blit(glow, (0, 0))
            pygame.draw.line(s, (40, 40, 46), (12, 39), (12, 14), 3)
            pygame.draw.line(s, (40, 40, 46), (8, 39), (16, 39), 3)
            pygame.draw.polygon(s, (40, 40, 46), [(7, 6), (17, 6), (15, 3), (9, 3)])
            pygame.draw.rect(s, (255, 220, 140), (8, 7, 8, 8))
            pygame.draw.line(s, (40, 40, 46), (12, 7), (12, 14), 1)
            pygame.draw.rect(s, (40, 40, 46), (8, 14, 8, 2))
            out["lamp"] = s
    elif th == "cathedral":
        s = surf(30, 30)                                                      # velas no chão (3 alturas)
        glow = surf(30, 30)
        pygame.draw.circle(glow, (255, 190, 90, 40), (15, 12), 13)
        s.blit(glow, (0, 0))
        pygame.draw.ellipse(s, (226, 218, 196), (3, 22, 24, 6))               # poça de cera
        for x, h in ((7, 9), (14, 15), (21, 7)):
            pygame.draw.rect(s, (236, 230, 212), (x - 2, 25 - h, 5, h))
            pygame.draw.line(s, (250, 248, 236), (x - 2, 25 - h), (x - 2, 23), 1)
            pygame.draw.line(s, (216, 208, 186), (x + 2, 27 - h), (x + 2, 24), 1)
            pygame.draw.ellipse(s, (255, 196, 90), (x - 2, 18 - h, 5, 8))
            pygame.draw.ellipse(s, (255, 248, 210), (x - 1, 21 - h, 3, 4))
        out["candle"] = s
        s = surf(36, 20)                                                      # entulho: blocos angulosos
        hi, mid, lo, dk = _stone_cols(pal["pillar"])
        for (x, y, w, h) in ((2, 9, 12, 8), (12, 5, 10, 9), (22, 10, 11, 7), (16, 13, 6, 5)):
            pygame.draw.rect(s, mid, (x, y, w, h))
            pygame.draw.line(s, hi, (x, y), (x + w - 1, y), 1)
            pygame.draw.line(s, lo, (x + w - 1, y), (x + w - 1, y + h - 1), 1)
            pygame.draw.rect(s, dk, (x, y, w, h), 1)
        out["rubble"] = s
        bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
        for k, gc in enumerate(pal["glass"]):                                  # luz colorida dos vitrais
            s = surf(64, 40)                                                  # (janela projetada no chão, pontilhada)
            for y in range(0, 40, 2):
                for x in range(0, 64, 2):
                    dx, dy = (x - 31) / 32, (y - 19) / 20
                    d = dx * dx + dy * dy
                    if d < 1 and bayer[(y // 2) % 4][(x // 2) % 4] / 16 < 0.75 - d * 0.6:
                        bar = (x // 2) % 8 == 0 or (y // 2) % 6 == 0   # caixilhos do vitral
                        col = (*gc, 55) if bar else (*gc, 95)
                        pygame.draw.rect(s, col, (x, y, 2, 2))
            out[f"light{k}"] = s
        if pal.get("carpet") or pal.get("banners"):
            s = surf(52, 30)                                                  # tapete gasto com franjas
            acc = pal["accent"]
            pygame.draw.rect(s, acc, (6, 4, 40, 22))
            pygame.draw.rect(s, (190, 160, 80), (8, 6, 36, 18), 2)
            pygame.draw.rect(s, _shade(acc, 0.7), (14, 11, 24, 8))
            pygame.draw.polygon(s, (190, 160, 80), [(26, 10), (30, 15), (26, 20), (22, 15)])
            for y in range(6, 25, 3):                                         # franjas
                pygame.draw.line(s, (210, 190, 140), (2, y), (6, y), 1)
                pygame.draw.line(s, (210, 190, 140), (46, y), (50, y), 1)
            pygame.draw.polygon(s, (0, 0, 0, 0), [(38, 26), (46, 18), (46, 26)])   # canto rasgado
            out["carpet"] = s
        if pal.get("shards"):
            s = surf(26, 20)                                                  # cacos de vitral
            for k in range(4):
                x, y = rnd.uniform(3, 20), rnd.uniform(3, 15)
                pygame.draw.polygon(s, pal["glass"][k % len(pal["glass"])], [(x, y), (x + 6, y + 2), (x + 2, y + 6)])
            out["shards"] = s
        if pal.get("crypt"):
            s = surf(34, 24)                                                  # caveira de gato e ossos
            bone = (222, 214, 194)
            pygame.draw.line(s, bone, (3, 19), (20, 15), 3)
            pygame.draw.circle(s, bone, (3, 19), 2)
            pygame.draw.circle(s, bone, (20, 15), 2)
            for sx in (-1, 1):
                pygame.draw.polygon(s, bone, [(21 + 3 * sx, 6), (21 + 6 * sx, 0), (21 + 7 * sx, 8)])
            pygame.draw.circle(s, bone, (21, 11), 7)
            pygame.draw.rect(s, bone, (17, 15, 9, 5))
            pygame.draw.circle(s, (34, 28, 30), (18, 10), 2)
            pygame.draw.circle(s, (34, 28, 30), (24, 10), 2)
            pygame.draw.polygon(s, (34, 28, 30), [(20, 14), (22, 14), (21, 15)])
            for x in (18, 21, 24):
                pygame.draw.line(s, (150, 140, 120), (x, 17), (x, 19), 1)
            out["skull"] = s
        if pal.get("tower"):
            s = surf(26, 14)                                                  # pena negra
            pygame.draw.ellipse(s, (40, 30, 50), (2, 3, 22, 8))
            pygame.draw.line(s, (90, 80, 100), (2, 7), (24, 7), 1)
            out["feather"] = s
    else:
        rock = pal["rock"]
        s = surf(26, 16)                                                      # pedrinhas angulosas
        for (x, y) in ((3, 9), (10, 6), (17, 9), (12, 11)):
            col = _shade(rock, rnd.uniform(0.8, 1.1))
            pygame.draw.polygon(s, col, [(x, y + 4), (x + 1, y), (x + 5, y - 1), (x + 6, y + 4)])
            pygame.draw.line(s, _shade(col, 1.3), (x + 1, y), (x + 5, y - 1), 1)
        out["pebbles"] = s
        s = surf(36, 20)                                                      # poça com borda e reflexo
        liquid = (110, 200, 120) if pal.get("slime") else (255, 120, 40) if pal.get("lava") else (52, 70, 98)
        pygame.draw.ellipse(s, _shade(rock, 0.6), (0, 2, 36, 17))
        pygame.draw.ellipse(s, liquid, (3, 4, 30, 12))
        pygame.draw.line(s, _shade(liquid, 1.5), (9, 7), (17, 7), 1)
        pygame.draw.line(s, _shade(liquid, 1.3), (20, 11), (25, 11), 1)
        out["puddle"] = s
        s = surf(28, 26)                                                      # cogumelos que brilham
        mc = (110, 220, 200) if not pal.get("lava") else (255, 160, 80)
        glow = surf(28, 26)
        pygame.draw.circle(glow, (*mc, 50), (14, 12), 12)
        s.blit(glow, (0, 0))
        for x, y, r in ((8, 14, 5), (17, 9, 7), (22, 17, 3)):
            pygame.draw.line(s, (220, 215, 200), (x, y), (x, y + 8), 2)
            pygame.draw.circle(s, mc, (x, y), r, draw_bottom_left=False, draw_bottom_right=False)
            pygame.draw.line(s, _shade(mc, 0.6), (x - r, y), (x + r, y), 1)
            s.set_at((x - r // 2, y - r // 2), (255, 255, 255))
        out["shroom"] = s
        s = surf(22, 22)                                                      # cristalzinho facetado
        cr = pal["crystal"]
        for (x, h, ang) in ((10, 16, 0.0), (6, 9, -0.5), (15, 8, 0.6)):
            tx, ty = x + math.sin(ang) * h, 20 - math.cos(ang) * h
            pygame.draw.polygon(s, _shade(cr, 1.25), [(x - 2, 20), (tx, ty), (x, 20)])
            pygame.draw.polygon(s, _shade(cr, 0.65), [(x, 20), (tx, ty), (x + 2, 20)])
        out["shard"] = s
        if pal.get("mine"):
            s = surf(60, 24)                                                  # trilho com dormentes e pregos
            for x in range(4, 60, 11):
                pygame.draw.rect(s, (100, 70, 45), (x, 3, 5, 18))
                pygame.draw.line(s, (130, 96, 62), (x, 3), (x, 20), 1)
            for y in (7, 16):
                pygame.draw.line(s, (130, 130, 140), (0, y), (60, y), 2)
                pygame.draw.line(s, (180, 180, 190), (0, y - 1), (60, y - 1), 1)
            out["rails"] = s
            s = surf(32, 24)                                                  # carrinho de mina tombado
            pygame.draw.ellipse(s, (0, 0, 0, 60), (2, 17, 28, 6))
            pygame.draw.polygon(s, (90, 90, 98), [(3, 6), (27, 6), (24, 18), (6, 18)])
            pygame.draw.line(s, (130, 130, 140), (3, 6), (27, 6), 2)
            pygame.draw.line(s, (60, 60, 66), (8, 6), (9, 18), 1)
            pygame.draw.line(s, (60, 60, 66), (22, 6), (21, 18), 1)
            for x in (9, 21):
                pygame.draw.circle(s, (50, 50, 56), (x, 19), 3)
            for k in range(3):
                pygame.draw.circle(s, _shade(rock, 0.9), (11 + k * 5, 5), 3)
            out["minecart"] = s
        if pal.get("gold"):
            s = surf(20, 16)                                                  # pepitas com brilho
            for k in range(3):
                x, y = 4 + k * 6, 8 + (k % 2) * 3
                pygame.draw.polygon(s, (220, 176, 60), [(x - 3, y + 2), (x - 1, y - 2), (x + 3, y - 1), (x + 3, y + 2)])
                s.set_at((x, y - 1), (255, 240, 170))
            out["nugget"] = s
        if pal.get("slime") or pal.get("lava"):
            s = surf(32, 18)                                                  # ossos derretidos
            bone = (222, 214, 194)
            pygame.draw.line(s, bone, (3, 12), (18, 9), 3)
            pygame.draw.circle(s, bone, (3, 12), 2)
            pygame.draw.circle(s, bone, (18, 9), 2)
            pygame.draw.circle(s, bone, (25, 10), 5)
            pygame.draw.circle(s, (34, 28, 30), (23, 10), 1)
            pygame.draw.circle(s, (34, 28, 30), (27, 10), 1)
            out["bones"] = s
    return out


def decor_kinds(decor):
    """Lista ponderada de decorações (as comuns mais vezes)."""
    common = {"weed", "rubble", "pebbles", "candle", "puddle", "light0", "embers", "crack"}
    out = []
    for k in decor:
        out += [k] * (3 if k in common else 1)
    return out


# ==================================================================================================
# Chão em pixel art de verdade (desenhado direto em baixa resolução, como a floresta)
# ==================================================================================================
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
    """Rachadura: caminho aleatório de pixels."""
    for _ in range(steps):
        _put(low, x, y, col)
        if glow and rnd.random() < 0.5:
            _put(low, x + 1, y, glow)
        x += rnd.choice((-1, 0, 1, 1))
        y += rnd.choice((-1, 0, 1))


def ground_town(pal, rnd):
    """Rua de paralelepípedos: pedras arredondadas e irregulares com luz/sombra, rejunte de terra, musgo e poças."""
    px = _px()
    lw = TILE // px.PX
    dirt = _shade(pal["ground"], 0.72)
    low = px.banded(px.tile_noise(lw, lw, rnd, (8, 16)), px.shades(dirt, (0.7, 0.85, 1.0)), 0.1)
    stone = pal["stone"]
    wet = _noise01(px, lw, rnd, (6, 12))
    y = 0
    while y < lw:
        h = rnd.choice((9, 10, 11))
        x = rnd.randrange(0, 8)
        while x < lw + 8:
            w = rnd.randint(9, 14)
            yo = rnd.choice((0, 0, 1))
            if rnd.random() < 0.94:   # algumas pedras faltando (só terra e mato)
                base = _shade(stone, rnd.uniform(0.8, 1.1))
                hi, lo, mid = _shade(base, 1.25), _shade(base, 0.62), _shade(base, 0.9)
                x0, y0, x1, y1 = x + 1, y + 1 + yo, x + w - 2, y + h - 2 + yo
                for yy in range(y0, y1 + 1):
                    for xx in range(x0, x1 + 1):
                        corner = (xx in (x0, x1)) and (yy in (y0, y1))
                        if corner:
                            continue   # cantos arredondados
                        c = base
                        if yy == y0 or (xx == x0 and yy < y1):
                            c = hi
                        elif yy == y1 or xx == x1:
                            c = lo
                        elif (xx * 7 + yy * 13) % 9 == 0:
                            c = mid
                        _put(low, xx, yy, c)
                _put(low, x0 + 1, y0 + 1, _shade(hi, 1.1))   # brilho
            else:
                for _ in range(5):
                    _put(low, x + rnd.randint(1, w - 2), y + h - 2 - rnd.randint(0, 3), pal["weed"])
            x += w
        y += h
    moss = _shade(pal["weed"], 0.8)
    water, shine = _shade(pal["stone"], 0.55), _shade(pal["stone"], 1.0)
    for yy in range(lw):   # poças nas partes baixas (escuras, com reflexo) e musgo nas frestas
        for xx in range(lw):
            v = wet[yy][xx]
            c = low.get_at((xx, yy))
            if v < 0.07:
                low.set_at((xx, yy), (water[0] - 10, water[1] - 6, water[2] + 12) if (xx + 3 * yy) % 23 else shine)
            elif v < 0.085:
                low.set_at((xx, yy), _shade(dirt, 0.7))   # borda molhada
            elif v > 0.78 and c[:3] == tuple(dirt[:3]):
                low.set_at((xx, yy), moss)
    for _ in range(120):
        _put(low, rnd.randrange(lw), rnd.randrange(lw), _shade(pal["weed"], 1.2))
    return low


def ground_cathedral(pal, rnd):
    """Piso gótico em losangos claros e escuros: bisel, textura, desgaste, trincas, lajes quebradas e rosáceas."""
    px = _px()
    lw = TILE // px.PX
    a, b = _shade(pal["ground"], 0.95), _shade(pal["ground2"], 0.78)
    tex = _noise01(px, lw, rnd, (16, 32))
    wear = _noise01(px, lw, rnd, (4, 8))
    low = pygame.Surface((lw, lw))
    D = 16   # meia diagonal do losango
    grout = _shade(pal["ground2"], 0.45)
    for y in range(lw):
        for x in range(lw):
            u, v = (x + y) % (2 * D), (x - y) % (2 * D)
            iu, iv = (x + y) // (2 * D), (x - y) // (2 * D)
            base = a if (iu + iv) % 2 == 0 else b
            k = 0.88 + 0.22 * (tex[y][x] + (px._BAYER[y % 4][x % 4] / 15 - 0.5) * 0.3)
            c = _shade(base, k)
            if u == 0 or v == 0:
                c = grout
            elif u == 1 or v == 1:
                c = _shade(base, 1.2)          # luz no alto (bisel)
            elif u == 2 * D - 1 or v == 2 * D - 1:
                c = _shade(base, 0.7)          # sombra embaixo
            if wear[y][x] > 0.78 and (x + y) % 2 == 0 and c is not grout:
                c = _shade(c, 0.86)
            low.set_at((x, y), c)
    accent = pal["accent"]
    for _ in range(rnd.choice((1, 2))):   # rosácea de pedra embutida (rara)
        cx, cy = rnd.randrange(lw), rnd.randrange(lw)
        for ang in range(0, 360, 8):
            r = 9 + (2 if ang % 45 == 0 else 0)
            _put(low, cx + int(math.cos(math.radians(ang)) * r), cy + int(math.sin(math.radians(ang)) * r),
                 _shade(accent, 0.8))
        for ang in range(0, 360, 45):
            for r in range(2, 9):
                _put(low, cx + int(math.cos(math.radians(ang)) * r), cy + int(math.sin(math.radians(ang)) * r),
                     _shade(accent, 0.6))
        _put(low, cx, cy, _shade(accent, 1.2))
    dirt = _shade(pal["ground2"], 0.4)
    for _ in range(2):   # lajes quebradas (buraco com entulho)
        cx, cy = rnd.randrange(lw), rnd.randrange(lw)
        for yy in range(-3, 4):
            for xx in range(-4, 5):
                if abs(xx) + abs(yy) < 5 + rnd.random():
                    _put(low, cx + xx, cy + yy, dirt)
        for _k in range(4):
            q = (cx + rnd.randint(-4, 4), cy + rnd.randint(-3, 3))
            _put(low, q[0], q[1], _shade(pal["ground"], 0.8))
            _put(low, q[0], q[1] - 1, _shade(pal["ground"], 1.1))
    for _ in range(30):   # trincas
        _walk(low, rnd, rnd.randrange(lw), rnd.randrange(lw), rnd.randint(6, 16), grout)
    for _ in range(90):   # cera de vela e poeira
        _put(low, rnd.randrange(lw), rnd.randrange(lw), (215, 205, 180) if rnd.random() < 0.4 else _shade(b, 1.25))
    return low


def ground_underground(pal, rnd):
    """Chão de caverna: rocha em faixas, rachaduras (de lava na Forja), pedrinhas, minério e umidade."""
    px = _px()
    lw = TILE // px.PX
    g = pal["ground"]
    low = px.banded(px.tile_noise(lw, lw, rnd, (8, 16, 32)), px.shades(g, (0.62, 0.76, 0.9, 1.02, 1.14)), 0.1)
    rock = pal["rock"]
    lava = pal.get("lava")
    ridge = _noise01(px, lw, rnd, (10, 20))
    seam = (200, 70, 30) if lava else _shade(g, 0.42)
    for y in range(lw):   # placas de rocha separadas por fendas (linhas do ruído)
        for x in range(lw):
            v = ridge[y][x]
            if abs(v - 0.5) < 0.022:
                low.set_at((x, y), seam)
            elif abs(v - 0.5) < 0.05 and v > 0.5:
                c = low.get_at((x, y))
                low.set_at((x, y), _shade(c, 1.15))   # borda de cima da placa pega luz
    for _ in range(50 if lava else 24):   # rachaduras
        col = (255, 120, 40) if lava else _shade(g, 0.45)
        _walk(low, rnd, rnd.randrange(lw), rnd.randrange(lw), rnd.randint(10, 22), col,
              glow=(255, 200, 90) if lava else None)
    for _ in range(280):   # pedrinhas com luz em cima e sombra embaixo
        x, y = rnd.randrange(lw), rnd.randrange(lw)
        c = _shade(rock, rnd.uniform(0.8, 1.1))
        _put(low, x, y, c)
        _put(low, x + 1, y, c)
        _put(low, x, y - 1, _shade(c, 1.25))
        _put(low, x, y + 1, _shade(g, 0.5))
        _put(low, x + 1, y + 1, _shade(g, 0.5))
    cr = pal["crystal"]
    for _ in range(100):   # pontinhos de minério
        _put(low, rnd.randrange(lw), rnd.randrange(lw), cr if rnd.random() < 0.6 else _shade(cr, 0.7))
    if pal.get("slime"):
        for _ in range(160):
            _put(low, rnd.randrange(lw), rnd.randrange(lw), (90, 170, 100))
    return low


def make_ground_pixel(pal, rnd):
    """Ladrilho do chão já em pixel art (TILE x TILE na tela)."""
    px = _px()
    th = pal["theme"]
    low = ground_town(pal, rnd) if th == "town" else ground_cathedral(pal, rnd) if th == "cathedral" else \
        _inf.ground(pal, rnd) if th == "inferno" else ground_underground(pal, rnd)
    if pal.get("night"):   # véu escuro azulado
        veil = pygame.Surface(low.get_size(), pygame.SRCALPHA)
        veil.fill((20, 25, 60, 55))
        low.blit(veil, (0, 0))
    return pygame.transform.scale(low, (low.get_width() * px.PX, low.get_height() * px.PX))
