"""Heróis em pixel art: sempre um gato usando o capacete/chapéu e a arma da classe.

A aparência do gato (pelagem, padrão, cor das marcas, olhos, cauda e orelhas) é de cada personagem: sorteada
ao recrutar e editável na tela da party (como a criação de personagem de um RPG). Capacete/chapéu, arma e a
cor da túnica são da classe e não mudam.

O gato é desenhado em baixa resolução (com as mesmas funções de chapéu e arma de icons.py), recebe contorno e
volume (pixel.pixelize) e é ampliado em blocos. Os sprites ficam em cache.
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

import pixel
from data import CLASSES
from icons import STYLE, FRONT_GRIP, _Pen, _shade

# ---------------------------------------------------------------------------
# Opções de aparência: (nome em inglês, nome em português, valor)
# ---------------------------------------------------------------------------
FUR_COLORS = [
    ("Ginger", "Laranja", (226, 138, 58)),
    ("Cream", "Creme", (232, 204, 156)),
    ("Grey", "Cinza", (148, 148, 158)),
    ("Blue", "Azulado", (112, 124, 148)),
    ("Black", "Preto", (50, 46, 56)),
    ("White", "Branco", (236, 232, 226)),
    ("Brown", "Marrom", (122, 84, 58)),
    ("Chocolate", "Chocolate", (86, 56, 42)),
    ("Red", "Ruivo", (190, 86, 46)),
    ("Silver", "Prateado", (196, 200, 208)),
    ("Lilac", "Lilás", (176, 156, 176)),
    ("Golden", "Dourado", (214, 170, 80)),
]
PATTERNS = [
    ("Solid", "Liso"),
    ("Tabby", "Rajado"),
    ("Tuxedo", "Smoking"),
    ("Spotted", "Malhado"),
    ("Points", "Siamês"),
    ("Bicolor", "Bicolor"),
]
EYE_COLORS = [
    ("Green", "Verde", (120, 220, 120), None),
    ("Gold", "Dourado", (240, 200, 70), None),
    ("Blue", "Azul", (110, 180, 250), None),
    ("Amber", "Âmbar", (240, 140, 60), None),
    ("Copper", "Cobre", (200, 110, 60), None),
    ("Violet", "Violeta", (180, 120, 240), None),
    ("Red", "Vermelho", (230, 70, 70), None),
    ("Odd eyes", "Bicolores", (110, 180, 250), (240, 200, 70)),
]
TAILS = [("Long", "Longa"), ("Fluffy", "Peluda"), ("Short", "Curta")]
EARS = [("Pointed", "Pontudas"), ("Folded", "Dobradas"), ("Tufted", "Com tufos")]

# campos editáveis na tela de aparência: (chave, rótulo EN, rótulo PT, lista de opções)
FIELDS = [
    ("fur", "Fur color", "Cor da pelagem", FUR_COLORS),
    ("pattern", "Pattern", "Padrão", PATTERNS),
    ("mark", "Marking color", "Cor das marcas", FUR_COLORS),
    ("eyes", "Eye color", "Cor dos olhos", EYE_COLORS),
    ("tail", "Tail", "Cauda", TAILS),
    ("ears", "Ears", "Orelhas", EARS),
]
KEYS = [f[0] for f in FIELDS]

PINK = (236, 140, 150)
NOSE_DARK = (70, 50, 60)
WHITE_FUR = (246, 244, 240)
_CACHE = {}
SUPPRESS_OUTLINE = False   # o acampamento contorna a camada de objetos inteira (sem contorno duplo nos gatos)


def option_name(key, value, lang="en"):
    opts = dict((f[0], f[3]) for f in FIELDS)[key]
    o = opts[value % len(opts)]
    return o[1] if lang == "pt" else o[0]


def clean_look(look):
    """Aparência válida (campos que faltam ou fora da faixa viram 0)."""
    out = {}
    look = look if isinstance(look, dict) else {}
    for key, _en, _pt, opts in FIELDS:
        try:
            out[key] = int(look.get(key, 0)) % len(opts)
        except (TypeError, ValueError):
            out[key] = 0
    return out


def random_look(rnd=None):
    rnd = rnd or random
    look = {key: rnd.randrange(len(opts)) for key, _e, _p, opts in FIELDS}
    if rnd.random() < 0.35:   # muitos gatos têm marcas num tom da própria pelagem
        look["mark"] = look["fur"]
    return look


def look_from_name(name):
    """Aparência fixa derivada do nome (saves antigos, antes da customização)."""
    h = 0
    for ch in str(name or ""):
        h = (h * 31 + ord(ch)) & 0xFFFFFF
    return random_look(random.Random(h))


def look_key(look):
    return tuple(clean_look(look)[k] for k in KEYS)


# ---------------------------------------------------------------------------
# NPCs do acampamento: aparência fixa
# ---------------------------------------------------------------------------
NPC_LOOKS = {
    "smith": dict(fur=7, pattern=2, mark=5, eyes=3, tail=2, ears=0),      # chocolate de smoking, rabo curto
    "jeweler": dict(fur=10, pattern=4, mark=7, eyes=5, tail=1, ears=1),   # lilás siamês, olhos violeta
}


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------
def _colors(look):
    fur = FUR_COLORS[look["fur"]][2]
    mark = FUR_COLORS[look["mark"]][2]
    if look["mark"] == look["fur"]:   # marcas no mesmo tom: um pouco mais escuras
        mark = _shade(fur, 0.68 if sum(fur) > 200 else 1.45)
    dark = _shade(fur, 0.72)
    light = tuple(min(255, int(c + (255 - c) * 0.55)) for c in fur)
    return fur, dark, mark, light


def _ear(p, x0, fur, inner, kind, tip):
    if kind == 1:   # dobrada: orelhinha baixa e redonda
        p.poly([(x0 - 0.34, -0.62), (x0 + 0.0, -1.08), (x0 + 0.36, -0.68), (x0 + 0.1, -0.86)], fur)
        return
    p.poly([(x0 - 0.36, -0.55), (x0 + 0.02, -1.42), (x0 + 0.38, -0.62)], fur)
    p.poly([(x0 - 0.18, -0.68), (x0 + 0.02, -1.15), (x0 + 0.2, -0.72)], inner, outline=False)
    if kind == 2:   # tufos na ponta (lince)
        p.line(x0 + 0.02, -1.4, x0 + 0.06, -1.72, tip, 0.12)


def _tail(p, kind, fur, dark, mark, pattern, sway=0.0):
    if kind == 2:   # curta (bobtail): um pompom
        p.circle(-0.78, 1.32 + sway * 0.15, 0.3, dark)
        p.circle(-0.76, 1.3 + sway * 0.15, 0.22, mark if pattern in (3, 4) else fur, outline=False)
        return
    w = 0.46 if kind == 1 else 0.34
    pts = [(-0.55, 1.35), (-1.25, 1.25), (-1.6, 0.8), (-1.55, 0.35), (-1.3, 0.15)]
    if sway:   # andando: a ponta da cauda balança
        pts = [(x - sway * 0.25 * (i / 4) ** 1.5, y + sway * 0.12 * i) for i, (x, y) in enumerate(pts)]
    p.lines(pts, dark, w)
    p.lines(pts[:-1], fur, w - 0.14)
    if pattern == 4:     # siamês: cauda escura
        p.lines(pts[1:], mark, w - 0.14)
    elif pattern == 1:   # rajado: anéis
        for x, y in ((-1.25, 1.25), (-1.58, 0.65)):
            p.circle(x, y, (w - 0.14) / 2, mark, outline=False)
    elif pattern in (2, 5):   # smoking / bicolor: ponta branca
        p.circle(-1.32, 0.17, (w - 0.1) / 2, WHITE_FUR, outline=False)
    if kind == 1:   # peluda: tufo na ponta
        p.circle(-1.33, 0.12, 0.26, fur)


WALK_FRAMES = 4


def _draw_cat(s, cid, c, R, ang, look, hat_on=True, tunic=None, weapon_on=True, walk=None, gear=None):
    """Gato olhando para a direita (o espelho para a esquerda é feito fora). c = centro da cabeça.

    walk = quadro do ciclo de caminhada (0..3) ou None (parado): patinhas alternando para frente/trás e
    levantando, corpo subindo e descendo, cauda balançando e a mão da arma acompanhando o passo."""
    fur, dark, mark, light = _colors(look)
    pattern = look["pattern"]
    body_c, legs_c, feet_c = gear or (None, None, None)   # roupa, calça e bota do ferreiro (cor do item)
    tunic = body_c or tunic or CLASSES[cid]["color"]
    hat, weapon, offhand = STYLE.get(cid, (None, None, None)) if cid else (None, None, None)
    if not weapon_on:
        weapon = offhand = None
    ground = _Pen(s, c, R)                 # os pés ficam no chão
    if walk is None:
        ph, bob = None, 0.0
    else:
        ph = walk * math.pi / 2
        bob = 0.12 * abs(math.sin(ph))     # o corpo sobe quando um pé passa pelo outro
    p = _Pen(s, V(c) - V(0, bob * R), R)
    rad = math.radians(ang)
    aim = V(math.cos(rad), math.sin(rad))
    paw = WHITE_FUR if pattern in (2, 5) else mark if pattern == 4 else fur
    foot = feet_c or paw                   # bota: as patinhas do chão na cor da bota

    swing = math.sin(ph) if ph is not None else 0.0
    _tail(p, look["tail"], fur, dark, mark, pattern, sway=swing)
    if offhand:   # mão de trás + arma secundária
        offhand(_Pen(s, p.pt(-0.55, 1.05 - swing * 0.06), R * 0.95, ang - 25 - swing * 8))
    # corpo: túnica na cor da classe, com cinto
    p.circle(-0.05, 1.12, 0.68, tunic)
    if legs_c:   # calça: a parte de baixo do corpo (abaixo do cinto) na cor da calça
        arc = [(-0.05 + 0.68 * math.cos(a), 1.12 + 0.68 * math.sin(a))
               for a in [math.asin(0.06 / 0.68) + k * (math.pi - 2 * math.asin(0.06 / 0.68)) / 10 for k in range(11)]]
        p.poly(arc, legs_c, outline=False)
    p.poly([(-0.72, 1.18), (0.62, 1.18), (0.6, 1.32), (-0.7, 1.32)], _shade(tunic, 0.6), outline=False)
    p.circle(-0.05, 1.25, 0.1, (235, 195, 70), outline=False)
    if pattern == 2:   # smoking: peitinho branco na gola
        p.poly([(0.05, 0.62), (0.4, 0.62), (0.22, 0.95)], WHITE_FUR, outline=False)
    # patinhas (andando: uma vai para frente enquanto a outra vai para trás e levanta ao passar)
    if ph is None:
        ground.circle(-0.38, 1.72, 0.24, foot)
        ground.circle(0.28, 1.72, 0.24, foot)
    else:
        st = 0.4 * math.cos(ph)
        lift_a = 0.32 * max(0.0, math.sin(ph))
        lift_b = 0.32 * max(0.0, -math.sin(ph))
        legc = legs_c or _shade(fur, 0.85)
        for bx, dx, lift in ((-0.38, -st, lift_b), (0.28, st, lift_a)):   # pé de trás, pé da frente
            x, y = bx + dx, 1.78 - lift
            ground.line(bx * 0.7, 1.45 - bob, x, y - 0.08, legc, 0.3)    # perninha saindo da túnica
            ground.circle(x, y, 0.24, foot)
    # cabeça
    p.circle(0, 0, 1.0, fur)
    if pattern == 1:     # rajado: listras na testa e nas bochechas
        for x in (-0.3, 0.02, 0.34):
            p.line(x, -0.95, x + 0.05, -0.58, mark, 0.14)
        p.line(-0.98, 0.15, -0.62, 0.2, mark, 0.12)
        p.line(-0.95, 0.42, -0.62, 0.4, mark, 0.12)
    elif pattern == 3:   # malhado: manchas
        p.circle(-0.45, -0.38, 0.42, mark, outline=False)
        p.circle(0.55, 0.5, 0.24, mark, outline=False)
    elif pattern == 4:   # siamês: máscara escura no rosto
        p.circle(0.38, 0.32, 0.6, mark, outline=False)
    elif pattern == 5:   # bicolor: metade de baixo do rosto branca
        p.poly([(-0.9, 0.35), (-0.2, 0.05), (0.35, -0.1), (0.98, 0.1), (0.75, 0.7), (0.0, 1.0), (-0.75, 0.7)],
               WHITE_FUR, outline=False)
    muzzle = WHITE_FUR if pattern in (2, 5) else light
    if pattern == 2:
        p.poly([(0.05, -0.55), (0.3, -0.55), (0.62, 0.2), (0.42, 0.8), (0.0, 0.6)], WHITE_FUR, outline=False)
    p.circle(0.42, 0.42, 0.36, muzzle, outline=False)      # focinho
    # olhos (vista 3/4 para a direita)
    _en, _pt, ec, ec2 = EYE_COLORS[look["eyes"]]
    for i, ex in enumerate((0.05, 0.62)):
        col = ec2 if (ec2 and i == 1) else ec
        p.circle(ex, 0.0, 0.22, col, outline=False)
        p.line(ex + 0.03, -0.14, ex + 0.03, 0.14, (20, 16, 24), 0.12)
    p.circle(0.68, 0.36, 0.1, NOSE_DARK if sum(fur) < 200 or pattern == 4 else PINK, outline=False)   # nariz
    # orelhas por cima do chapéu (orelhinhas aparecendo é parte do charme)
    if hat and hat_on:
        hat(p)
    ear_fur = mark if pattern == 4 else fur
    _ear(p, -0.62, ear_fur, PINK, look["ears"], dark)
    _ear(p, 0.5, ear_fur, PINK, look["ears"], dark)
    # arma na mão da frente
    if weapon:
        hy = 1.1 + swing * 0.07                             # a mão da arma acompanha o passo
        if cid in FRONT_GRIP:
            weapon(_Pen(s, p.pt(0.55, hy - 0.1) + aim * R * 0.6, R, ang))
        else:
            weapon(_Pen(s, p.pt(0.62, hy), R, ang - 30 + swing * 6))
        p.circle(0.62, hy, 0.22, paw)                       # patinha segurando


def cat_sprite(cid, r, facing=(1, 0), look=None, outline=None, hat_on=True, tunic=None, weapon_on=True, walk=None,
               gear=None):
    """Surface do gato (centro da surface = centro do corpo antigo). Usa cache."""
    look = clean_look(look)
    f = V(facing)
    if f.length_squared() < 1e-6:
        f = V(1, 0)
    left = f.x < -0.05
    if left:
        f = V(-f.x, f.y)
    ang = int(round(math.degrees(math.atan2(f.y, f.x)) / 22.5)) * 22.5   # 16 direções (8 por lado)
    pf = max(1, int(round(r / 7.0)))                                      # tamanho do pixel na tela
    outline = None if SUPPRESS_OUTLINE else (outline or pixel.OUTLINE)
    if walk is not None:
        walk = int(walk) % WALK_FRAMES
    gear = tuple(tuple(g) if g else None for g in gear) if gear else None
    key = (cid, int(r), look_key(look), left, ang, outline, pf, hat_on, tunic, weapon_on, walk, gear)
    surf = _CACHE.get(key)
    if surf is not None:
        return surf
    R = r * 0.95 / pf                  # raio da cabeça em pixels de baixa resolução
    size = int(R * 7) + 4
    low = pygame.Surface((size, size), pygame.SRCALPHA)
    head = V(size / 2, size / 2 - R * 0.45)
    _draw_cat(low, cid, head, R, ang, look, hat_on, tunic, weapon_on, walk, gear)
    surf = pixel.pixelize(low, pf, outline=outline)
    if left:
        surf = pygame.transform.flip(surf, True, False)
    if len(_CACHE) > 5000:
        _CACHE.clear()
    _CACHE[key] = surf
    return surf


_WALK = {}


def walk_frame(key, pos, r):
    """Quadro da caminhada de quem está em pos (key = qualquer identificador estável), ou None se parado.

    O passo avança pela distância andada (anda mais rápido = pés mais rápidos)."""
    st = _WALK.get(key)
    pos = V(pos)
    if st is None:
        if len(_WALK) > 400:
            _WALK.clear()
        st = _WALK[key] = [pos, 0.0, 0]
    d = (pos - st[0]).length()
    st[0] = pos
    if d > 40:          # teleporte / troca de tela: não conta como passo
        d = 0.0
    if d > 0.25:
        st[1] += d
        st[2] = 5       # alguns quadros de tolerância (o movimento pode ter quadros sem deslocamento)
    elif st[2] > 0:
        st[2] -= 1
    if st[2] <= 0:
        return None
    return int(st[1] / max(6.0, r * 1.3)) % WALK_FRAMES   # ~1 ciclo de passos a cada 70 px andados


def draw_cat(s, cid, center, r, facing=(1, 0), look=None, outline=None, shadow=True, **kw):
    surf = cat_sprite(cid, r, facing, look, outline, **kw)
    c = V(center)
    if shadow:
        sh = pygame.Surface((int(r * 2.2), int(r * 0.7)), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), sh.get_rect())
        s.blit(sh, (c.x - sh.get_width() / 2, c.y + r * 0.95 - sh.get_height() / 2))
    s.blit(surf, (c.x - surf.get_width() / 2, c.y - surf.get_height() / 2))
