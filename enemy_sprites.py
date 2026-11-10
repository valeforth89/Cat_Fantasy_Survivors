"""Sprites dos inimigos em pixel art: registro dos desenhos (DRAWERS) e cache dos sprites prontos.

Cada desenho é feito em baixa resolução e pixelizado (pixel.pixelize) uma vez só, e fica guardado em cache (por
tipo, tamanho, cor, lado e quadro de animação), para não pesar com centenas de inimigos na tela. Os desenhos
ficam em beasts.py, biome_sprites.py, creatures.py e inferno_sprites.py (registrados no fim deste arquivo);
aqui ficam só o esqueleto e o boneco de treino.
"""
import math

import pygame

import pixel

from icons import _Pen, _arc, _shade, OUT
import cat_parts as cp

WHITE = (240, 240, 245)
_CACHE = {}


def draw_esqueleto(p, col, frame):
    """Caveira com mandíbula, costelas aparentes, braços de osso e uma espada enferrujada."""
    bone, dark = col, _shade(col, 0.55)
    step = 0.12 if frame % 2 else -0.12
    for sx in (-1, 1):                                                      # pernas de osso
        p.line(0.25 * sx, 0.7, 0.35 * sx + step * sx, 1.45, bone, 0.13)
    cp.bone_tail(p, bone)                                                   # gato: cauda de ossinhos
    p.line(-0.75, 0.1, -1.35, 0.55 - step, bone, 0.13)                      # braço de trás
    p.circle(0, 0.55, 0.62, _shade(bone, 0.85))                             # caixa torácica
    for i in range(3):                                                      # costelas
        y = 0.35 + i * 0.17
        p.line(-0.45, y, 0.45, y, dark, 0.06)
    p.line(0, 0.15, 0, 1.0, dark, 0.07)                                     # coluna
    cp.ears(p, 0, -0.35, 0.78, bone, inner=dark)                            # caveira de gato: orelhas
    p.circle(0, -0.35, 0.78, bone)                                          # caveira
    p.poly([(-0.42, 0.12), (0.42, 0.12), (0.32, 0.45), (-0.32, 0.45)], bone)   # mandíbula
    for i in range(4):                                                      # dentes
        x = -0.24 + i * 0.16
        p.line(x, 0.14, x, 0.36, dark, 0.04)
    p.circle(-0.3, -0.42, 0.22, (25, 20, 25), outline=False)               # órbitas
    p.circle(0.3, -0.42, 0.22, (25, 20, 25), outline=False)
    if cp.DEAD[0]:
        cp.x_eye(p, -0.3, -0.42, 0.15)
        cp.x_eye(p, 0.3, -0.42, 0.15)
    else:
        p.circle(-0.3, -0.42, 0.07, (255, 90, 60), outline=False)              # brilho nos olhos
        p.circle(0.3, -0.42, 0.07, (255, 90, 60), outline=False)
    p.poly([(-0.09, -0.14), (0.09, -0.14), (0.0, 0.02)], (25, 20, 25), outline=False)   # nariz de gato
    for sx in (-1, 1):                                                      # presas
        p.poly([(0.13 * sx, 0.14), (0.21 * sx, 0.14), (0.17 * sx, 0.3)], (250, 245, 235), outline=False)
    p.line(0.75, 0.1, 1.25, 0.45 + step, bone, 0.13)                        # braço da frente
    p.line(1.2, 0.5, 1.75, -0.55, (150, 120, 90), 0.14)                     # espada enferrujada
    p.line(1.05, 0.3, 1.45, 0.62, (110, 90, 70), 0.1)                       # guarda


def draw_dummy(p, col, frame):
    """Boneco de treino de palha: poste de madeira, braços de pau com palha nas pontas, corpo de saco amarrado
    com corda, alvo pintado no peito e cabeça de saco com olhos costurados em X."""
    wood, wood_d = (130, 92, 52), (90, 62, 34)
    straw, straw_d = (232, 200, 104), (190, 150, 60)
    sack, sack_d = _shade(col, 1.0), _shade(col, 0.7)
    tilt = 0.05 if frame % 2 else -0.05
    p.line(0.0, 0.5, 0.0, 1.75, wood, 0.2)                                    # poste
    p.line(-0.45, 1.75, 0.45, 1.75, wood_d, 0.14)                             # base
    p.line(-1.6, -0.15 + tilt, 1.6, -0.15 - tilt, wood, 0.17)                 # braços (pau atravessado)
    for sx in (-1, 1):                                                        # palha saindo das pontas
        y0 = -0.15 - tilt * sx
        for k, dy in enumerate((-0.28, -0.1, 0.08, 0.26)):
            p.line(1.55 * sx, y0, (1.95 + 0.08 * (k % 2)) * sx, y0 + dy * 1.3, straw if k % 2 else straw_d, 0.07)
    p.circle(0, 0.2, 0.92, sack)                                              # corpo (saco de palha)
    for x, y in ((-0.55, 0.8), (-0.2, 1.02), (0.25, 1.02), (0.6, 0.78)):      # palha saindo por baixo
        p.line(x, y - 0.12, x * 1.15, y + 0.28, straw_d, 0.07)
    p.line(-0.85, 0.55, 0.85, 0.55, wood_d, 0.07)                             # corda na cintura
    p.circle(0.0, 0.12, 0.42, (240, 235, 220), outline=False)                 # alvo pintado
    p.circle(0.0, 0.12, 0.3, (200, 50, 50), outline=False)
    p.circle(0.0, 0.12, 0.17, (240, 235, 220), outline=False)
    p.circle(0.0, 0.12, 0.07, (200, 50, 50), outline=False)
    p.circle(0, -0.95, 0.55, sack)                                            # cabeça
    for x, y in ((-0.3, -1.45), (-0.05, -1.55), (0.22, -1.47)):               # palha no topo da cabeça
        p.line(x, y + 0.12, x * 1.4, y - 0.18, straw, 0.07)
    p.line(-0.3, -0.62, 0.3, -0.62, wood_d, 0.07)                             # corda no pescoço
    for ex in (-0.2, 0.2):                                                    # olhos costurados em X
        p.line(ex - 0.08, -1.08, ex + 0.08, -0.92, OUT, 0.05)
        p.line(ex - 0.08, -0.92, ex + 0.08, -1.08, OUT, 0.05)
    p.line(-0.18, -0.78, 0.18, -0.78, sack_d, 0.05)                           # boca costurada


DRAWERS = {
    'dummy': draw_dummy,
    'esqueleto': draw_esqueleto,
}
FLIPPABLE = {"lobo", "javali", "esqueleto", "zumbi"}     # viram para o lado em que andam
FRAMES = {"dummy": 2, "morcego": 2, "aranha": 2, "esqueleto": 2, "zumbi": 2}


def sprite(kind, r, color, facing_right=True, frame=0, dead=False):
    """Surface com o sprite (centro = meio da surface). Usa cache. dead=True: olhos em X, caído de lado."""
    r = max(4, int(r))
    frame = 0 if dead else frame % FRAMES.get(kind, 1)
    flip = (not facing_right) and kind in FLIPPABLE
    key = (kind, r, tuple(color), flip, frame, dead)
    surf = _CACHE.get(key)
    if surf is None:
        # pixel art: desenha em meia resolução, contorna, dá volume e amplia em blocos de 2x2
        # mesma grade de pixel art dos heróis gatos (cats.cat_sprite): o tamanho do "pixel" cresce com o sprite,
        # então monstros grandes, elites e chefões ficam com a mesma densidade de detalhe dos personagens
        pf = max(pixel.PX, int(round(r / 7.5)))
        rl = r / pf
        size = int(rl * 5) + 4
        low = pygame.Surface((size, size), pygame.SRCALPHA)
        cp.DEAD[0] = dead
        try:
            DRAWERS.get(kind, DRAWERS["javali"])(_Pen(low, (size / 2, size / 2), rl), color, frame)
        finally:
            cp.DEAD[0] = False
        if dead:   # caído de lado e um pouco mais escuro
            low = pygame.transform.rotate(low, -90 if not flip else 90)
            low.fill((175, 165, 170, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surf = pixel.pixelize(low, pf)
        if flip:
            surf = pygame.transform.flip(surf, True, False)
        if len(_CACHE) > 3000:
            _CACHE.clear()
        _CACHE[key] = surf
    return surf


_FLASH = {}


def flash_sprite(kind, r, color, facing_right=True, frame=0):
    """Silhueta branca do sprite (o inimigo pisca ao levar dano), no mesmo grid de pixel art. Usa cache."""
    base = sprite(kind, r, color, facing_right, frame)
    surf = _FLASH.get(id(base))
    if surf is None or surf[0] is not base:
        w = base.copy()
        w.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
        w.fill((255, 255, 255, 190), special_flags=pygame.BLEND_RGBA_MIN)
        if len(_FLASH) > 1500:
            _FLASH.clear()
        surf = _FLASH[id(base)] = (base, w)
    return surf[1]


def draw_enemy(s, kind, center, r, color, facing_right=True, frame=0):
    surf = sprite(kind, r, color, facing_right, frame)
    s.blit(surf, (center[0] - surf.get_width() / 2, center[1] - surf.get_height() / 2))


# inimigos e chefões dos biomas novos (Cidade Abandonada, Catedral, Subterrâneo)
import biome_sprites as _bs   # noqa: E402

DRAWERS.update(_bs.DRAWERS)
FLIPPABLE |= _bs.FLIPPABLE
FRAMES.update(_bs.FRAMES)

# 0.0.24.2: monstros e chefões sem corpo de "bolinha" (silhuetas de verdade, beasts.py)
import beasts as _bt   # noqa: E402

DRAWERS.update(_bt.DRAWERS)
FLIPPABLE |= _bt.FLIPPABLE
FRAMES.update(_bt.FRAMES)

# 0.0.29: redesenho dos que destoavam (proporções "chibi" como os heróis; goblins e inquisidor viram gatos)
import creatures as _cr   # noqa: E402

DRAWERS.update(_cr.DRAWERS)
FLIPPABLE |= _cr.FLIPPABLE
FRAMES.update(_cr.FRAMES)

# 0.0.31: Inferno (diabretes, cães infernais, demônios, salamandras, bruxos e os chefões do bioma)
import inferno_sprites as _inf   # noqa: E402

DRAWERS.update(_inf.DRAWERS)
FLIPPABLE |= _inf.FLIPPABLE
FRAMES.update(_inf.FRAMES)
