"""Sprites dos inimigos e chefões dos biomas Cidade Abandonada, Catedral e Subterrâneo.

Mesmo estilo dos da floresta (enemy_sprites.py): corpo redondo + detalhes, desenhados em unidades do raio.
Os chefões reaproveitam o desenho de um inimigo do bioma e ganham acessórios (coroa, chapéu, asas...) ou têm
um desenho próprio. Registrados em enemy_sprites.DRAWERS no fim de enemy_sprites.py.
"""
import math

from icons import _arc, _shade, OUT
import cat_parts as cp

WHITE = (240, 240, 245)
GOLD = (235, 195, 70)
GOLD_D = (170, 130, 40)


def _eye(p, x, y, col, rad=0.13):
    if cp.DEAD[0]:
        cp.x_eye(p, x, y, rad)
        return
    p.circle(x, y, rad, col, outline=False)
    if p.r >= 12:
        p.circle(x + rad * 0.3, y - rad * 0.3, rad * 0.35, WHITE, outline=False)


# ===========================================================================
# Cidade Abandonada
# ===========================================================================
def draw_espectro(p, col, frame, eye=(120, 220, 255)):
    """Espectro: lençol fantasmagórico ondulado, olhos vazios brilhando e correntes."""
    bob = 0.08 if frame % 2 else -0.08
    pts = _arc(0, -0.2 + bob, 0.95, 180, 360, 10)
    for i in range(7):                                                        # barra ondulada
        x = 0.95 - i * 0.317
        pts.append((x, 0.9 + bob + (0.25 if i % 2 else 0)))
    cp.ears(p, 0, -0.2 + bob, 0.95, col, inner=_shade(col, 0.8), spread=38, size=0.45)   # fantasma-gato
    p.poly(pts, col)
    p.poly(_arc(0, -0.2 + bob, 0.7, 200, 340, 8), _shade(col, 1.15), outline=False)
    for x in (-0.3, 0.3):
        p.circle(x, -0.25 + bob, 0.2, (20, 20, 35), outline=False)
        p.circle(x, -0.25 + bob, 0.08, eye, outline=False)
    cp.muzzle(p, 0, 0.05 + bob, 0.3, nose=(20, 20, 35), whisker=_shade(col, 0.7))   # focinho e bigodes
    for sx in (-1, 1):                                                        # correntes
        for k in range(3):
            p.circle(0.9 * sx + 0.15 * k * sx, 0.1 + bob + k * 0.22, 0.09, (150, 150, 160))


def draw_medico(p, col, frame):
    """Médico da Peste: manto escuro, chapéu de aba larga, máscara de bico longo e lanterna."""
    sway = 0.08 if frame % 2 else -0.08
    p.poly([(-0.95, -0.2), (-1.15, 1.2), (1.15, 1.2), (0.95, -0.2)], (45, 40, 45))   # manto
    p.line(-0.9, 0.2, -1.45, 0.75 + sway, (45, 40, 45), 0.2)                  # braço com lanterna
    p.line(-1.45, 0.75 + sway, -1.45, 1.0 + sway, (120, 110, 90), 0.04)
    p.circle(-1.45, 1.15 + sway, 0.2, (255, 200, 90))
    cp.tail(p, (70, 60, 70), base=(-0.95, 0.9), tip=(40, 35, 40))             # gato da peste: cauda
    p.circle(0, -0.25, 0.75, (205, 190, 160))                                 # máscara
    p.poly([(0.45, -0.35), (1.95, 0.25), (0.45, 0.15)], (205, 190, 160))      # bico
    p.line(0.6, -0.05, 1.7, 0.2, _shade((205, 190, 160), 0.7), 0.04)
    for x in (-0.15, 0.3):                                                    # lentes vermelhas
        p.circle(x, -0.35, 0.17, (60, 50, 45))
        p.circle(x, -0.35, 0.11, (220, 60, 50), outline=False)
    p.poly([(-1.35, -0.75), (1.35, -0.75), (0.75, -0.95), (-0.75, -0.95)], (35, 30, 35))   # aba do chapéu
    p.poly([(-0.6, -0.95), (-0.5, -1.65), (0.5, -1.65), (0.6, -0.95)], (35, 30, 35))
    p.line(-0.58, -1.05, 0.58, -1.05, (110, 30, 40), 0.1)
    for sx in (-1, 1):                                                        # orelhas pretas furando a aba
        p.poly([(0.62 * sx, -0.92), (1.05 * sx, -1.5), (1.15 * sx, -0.85)], (70, 60, 70))
    for sy in (-0.04, 0.08):                                                  # bigodes saindo da máscara
        p.line(0.5, 0.05 + sy, 0.95, 0.12 + sy * 2.5, (235, 230, 220), 0.035)


def draw_prefeito(p, col, frame):
    """Prefeito Oco: o espectro de cartola, monóculo e faixa de ouro do cargo."""
    draw_espectro(p, col, frame, eye=(255, 220, 120))
    bob = 0.08 if frame % 2 else -0.08
    p.poly([(-0.85, -0.95 + bob), (0.85, -0.95 + bob), (0.6, -1.05 + bob), (-0.6, -1.05 + bob)], (30, 30, 40))
    p.poly([(-0.5, -1.0 + bob), (-0.45, -1.85 + bob), (0.45, -1.85 + bob), (0.5, -1.0 + bob)], (30, 30, 40))
    p.line(-0.48, -1.15 + bob, 0.48, -1.15 + bob, (150, 40, 50), 0.12)
    p.circle(0.3, -0.25 + bob, 0.2, GOLD, outline=False)                      # monóculo
    p.circle(0.3, -0.25 + bob, 0.13, (20, 20, 35), outline=False)
    p.circle(0.3, -0.25 + bob, 0.06, (255, 220, 120), outline=False)
    p.lines([(-0.7, 0.05 + bob), (0.0, 0.55 + bob), (0.7, 0.05 + bob)], GOLD, 0.1)   # corrente do cargo
    p.circle(0.0, 0.62 + bob, 0.14, GOLD)


# ===========================================================================
# Catedral
# ===========================================================================
def draw_fatuo(p, col, frame):
    """Fogo-fátuo: chama azulada flutuante com núcleo claro e cauda tremulando."""
    flick = 0.15 if frame % 2 else -0.15
    p.poly([(-0.7, 0.3), (-1.2 + flick, 1.3), (-0.2, 0.75), (0.2, 1.4 + flick), (0.6, 0.6)], _shade(col, 0.8),
           outline=False)
    p.circle(0, 0, 1.0, col, outline=False)
    p.poly([(-0.55, -0.6), (0.0 + flick, -1.7), (0.55, -0.6)], col, outline=False)
    p.circle(0, 0.05, 0.6, _shade(col, 1.3), outline=False)
    p.circle(0, 0.1, 0.3, WHITE, outline=False)
    _eye(p, -0.22, -0.05, (30, 40, 90), 0.1)
    _eye(p, 0.22, -0.05, (30, 40, 90), 0.1)


def draw_cultista(p, col, frame):
    """Cultista: manto com capuz, rosto na sombra com olhos acesos e uma vela negra."""
    sway = 0.06 if frame % 2 else -0.06
    p.poly([(-0.8, -0.3), (-1.1, 1.2), (1.1, 1.2), (0.8, -0.3)], col)          # manto
    p.line(0, 0.0, 0, 1.15, _shade(col, 0.6), 0.06)
    p.line(0.75, 0.25, 1.25, 0.1 + sway, col, 0.22)                           # braço
    p.line(1.3, 0.05 + sway, 1.3, -0.5 + sway, (40, 35, 40), 0.14)            # vela
    p.poly([(1.2, -0.5 + sway), (1.3, -0.85 + sway), (1.4, -0.5 + sway)], (255, 170, 60), outline=False)
    cp.tail(p, _shade(col, 0.8), base=(-0.9, 0.95), up=False)                 # cauda saindo do manto
    cp.ears(p, 0, -0.45, 0.8, col, inner=_shade(col, 0.6), spread=36, size=0.55)   # capuz com orelhas
    p.circle(0, -0.45, 0.8, col)                                               # capuz
    p.circle(0, -0.35, 0.52, (25, 15, 20), outline=False)                      # sombra
    cp.slit_eye(p, -0.18, -0.38, (255, 120, 60), 0.1)                         # olhos de gato acesos
    cp.slit_eye(p, 0.18, -0.38, (255, 120, 60), 0.1)
    for sx in (-1, 1):                                                         # bigodes na sombra
        p.line(0.25 * sx, -0.15, 0.55 * sx, -0.1, (90, 70, 80), 0.035)
    p.poly([(-0.15, 0.25), (0.0, 0.5), (0.15, 0.25)], GOLD, outline=False)     # pingente


def draw_bispo(p, col, frame):
    """Bispo de Ossos: esqueleto de mitra e manto roxo rasgado, com um báculo dourado."""
    p.poly([(-0.85, 0.0), (-1.05, 1.3), (1.05, 1.3), (0.85, 0.0)], (90, 50, 110))   # manto
    p.line(1.0, 1.3, 1.25, -1.2, GOLD, 0.1)                                   # báculo
    p.lines(_arc(1.05, -1.25, 0.28, 0, 230, 8), GOLD, 0.1)
    from enemy_sprites import draw_esqueleto
    draw_esqueleto(p, col, frame)
    p.poly([(-0.6, -0.95), (-0.4, -1.95), (0.0, -2.2), (0.4, -1.95), (0.6, -0.95)], (235, 225, 210))   # mitra
    p.line(0, -1.9, 0, -1.1, GOLD, 0.08)
    p.line(-0.22, -1.55, 0.22, -1.55, GOLD, 0.08)


# ===========================================================================
# Subterrâneo
# ===========================================================================
def draw_gosma(p, col, frame):
    """Gosma: gota gelatinosa que achata e estica, com brilho, olhos e um osso boiando dentro."""
    squash = 0.12 if frame % 2 else -0.06
    pts = _arc(0, 0.35, 1.05 + squash, 180, 360, 12, 1.25 - squash)
    pts += [(1.05 + squash, 0.75), (0.5, 0.85), (0.0, 0.8), (-0.55, 0.88), (-1.05 - squash, 0.75)]
    p.poly(pts, col)
    p.circle(0.1, 0.25, 0.25, (230, 225, 200), outline=False)                 # osso boiando
    p.line(-0.1, 0.35, 0.35, 0.15, (230, 225, 200), 0.09)
    p.circle(-0.45, -0.45 + squash, 0.22, _shade(col, 1.45), outline=False)    # brilho
    _eye(p, -0.3, -0.15, (20, 40, 25), 0.12)
    _eye(p, 0.3, -0.15, (20, 40, 25), 0.12)
    p.circle(0.6, 1.0, 0.12, col)                                             # pingos
    p.circle(-0.75, 1.0, 0.09, col)


def draw_titan_gosma(p, col, frame):
    """Titã de Gosma: gosma gigante com uma caveira e moedas dentro."""
    draw_gosma(p, col, frame)
    p.circle(-0.15, 0.5, 0.28, (230, 225, 200), outline=False)                 # caveira dentro
    p.circle(-0.23, 0.47, 0.07, (40, 50, 40), outline=False)
    p.circle(-0.07, 0.47, 0.07, (40, 50, 40), outline=False)
    for x, y in ((0.55, 0.55), (0.35, 0.7)):
        p.circle(x, y, 0.09, GOLD, outline=False)
    for x in (-0.6, 0.0, 0.6):                                                # coroa de pingos
        p.circle(x, -1.0 + abs(x) * 0.3, 0.15, _shade(col, 1.2))


DRAWERS = {
    'espectro': draw_espectro,
    'medico': draw_medico,
    'prefeito': draw_prefeito,
    'fatuo': draw_fatuo,
    'cultista': draw_cultista,
    'bispo': draw_bispo,
    'gosma': draw_gosma,
    'titan_gosma': draw_titan_gosma,
}
FLIPPABLE = {"rato", "cao", "bruto", "carnical", "rei_rato", "lorde_bandido", "medico", "cavaleiro", "cultista",
             "armadura", "inquisidor", "bispo", "goblin", "rei_goblin", "verme", "wyrm", "arcanjo"}
FRAMES = {k: 2 for k in DRAWERS}
