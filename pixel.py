"""Estilo pixel art: fonte pixelada, pixelização do mundo e conversão dos sprites.

- PixelFont: fonte Jersey 10 (pixel) com as mesmas medidas da fonte antiga (o layout das telas não muda).
- pixelate_world(): o mundo da run (chão, inimigos, efeitos) é reduzido para 1/PX e ampliado sem
  suavização, então tudo o que é desenhado com primitivas vira pixel art de verdade.
- pixelize(): pega um desenho em baixa resolução, coloca contorno escuro de 1 pixel, luz no alto à
  esquerda e sombra embaixo à direita (volume), e amplia em blocos de PX.
- grade(): acabamento de cor escuro/gótico (vinheta) inspirado em Blasphemous / Last Faith.
"""
import os
import sys

import pygame

from data import W, H

PX = 2                       # tamanho do "pixel" do mundo em pixels de tela
OUTLINE = (14, 10, 16)       # contorno dos sprites (quase preto, levemente arroxeado)

# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------
FONT_FILE = "Jersey10-Regular.ttf"


def _font_path():
    bases = [os.path.dirname(os.path.abspath(__file__))]
    if getattr(sys, "frozen", False):
        bases.insert(0, getattr(sys, "_MEIPASS", ""))
        bases.append(os.path.dirname(os.path.abspath(sys.executable)))
    for b in bases:
        p = os.path.join(b, FONT_FILE)
        if os.path.exists(p):
            return p
    return None


# tamanho da fonte antiga -> (tamanho da Jersey 10, pixels cortados em cima, altura final)
# medidas escolhidas para a largura do texto ficar igual à da fonte padrão do pygame
_SIZES = {20: 18, 26: 23, 56: 50, 110: 98}


class PixelFont:
    """Fonte pixelada com a mesma interface usada no jogo (render, size, get_linesize, get_height)."""

    def __init__(self, old_size):
        self.old = pygame.font.SysFont(None, old_size) if _font_path() is None else None
        path = _font_path()
        if path is None:   # sem o arquivo da fonte: usa a antiga (o jogo continua funcionando)
            self.f = self.old
            self.top, self.h = 0, self.f.get_linesize()
            return
        size = _SIZES.get(old_size, int(old_size * 0.9))
        self.f = pygame.font.Font(path, size)
        # a Jersey tem bastante espaço acima das letras: corta para a altura parecida com a antiga
        cap = self.f.render("HÊÃÉ", False, (255, 255, 255)).get_bounding_rect()   # acentos das maiúsculas cabem
        desc = self.f.render("gjpqy", False, (255, 255, 255)).get_bounding_rect()
        self.top = max(0, cap.top - max(1, size // 10))
        self.h = max(cap.bottom, desc.bottom) - self.top + max(1, size // 12)

    def render(self, text, aa=True, color=(255, 255, 255), bg=None):
        surf = self.f.render(text, aa, color) if bg is None else self.f.render(text, aa, color, bg)
        if self.top == 0 and surf.get_height() <= self.h:
            return surf
        out = pygame.Surface((surf.get_width(), self.h), pygame.SRCALPHA)
        if bg is not None:
            out.fill(bg)
        out.blit(surf, (0, -self.top))
        return out

    def size(self, text):
        return self.f.size(text)[0], self.h

    def get_linesize(self):
        return self.h

    def get_height(self):
        return self.h

    def __getattr__(self, name):   # set_bold, etc.
        return getattr(self.f, name)


def make_fonts():
    return {"small": PixelFont(20), "normal": PixelFont(26), "big": PixelFont(56), "title": PixelFont(110)}


# ---------------------------------------------------------------------------
# Mundo: pixelização + acabamento de cor
# ---------------------------------------------------------------------------
_LOW = {}


_VIGNETTE = {}


def vignette(size=(W, H), strength=150):
    key = (size, strength)
    v = _VIGNETTE.get(key)
    if v is None:
        w, h = size
        low = pygame.Surface((w // 8, h // 8), pygame.SRCALPHA)
        lw, lh = low.get_size()
        for y in range(lh):
            for x in range(lw):
                dx, dy = (x + 0.5) / lw * 2 - 1, (y + 0.5) / lh * 2 - 1
                d = (dx * dx * 0.85 + dy * dy) ** 0.5
                a = max(0.0, min(1.0, (d - 0.55) / 0.75))
                low.set_at((x, y), (8, 4, 14, int(strength * a * a)))
        v = _VIGNETTE[key] = pygame.transform.smoothscale(low, size)
    return v


def grade(surf):
    """Acabamento gótico: cores um pouco mais frias/escuras e vinheta nas bordas."""
    surf.fill((226, 218, 232), special_flags=pygame.BLEND_RGB_MULT)
    surf.blit(vignette(surf.get_size()), (0, 0))


def pixelate_world(surf, desat=70):
    """Mundo em blocos de PX, um pouco dessaturado (tons sóbrios) e com vinheta."""
    rect = surf.get_rect()
    low = pygame.transform.scale(surf, (rect.w // PX, rect.h // PX))
    if desat and hasattr(pygame.transform, "grayscale"):
        g = pygame.transform.grayscale(low)
        g.set_alpha(desat)
        low.blit(g, (0, 0))
    surf.blit(pygame.transform.scale(low, (rect.w // PX * PX, rect.h // PX * PX)), (0, 0))
    grade(surf)


# ---------------------------------------------------------------------------
# Sprites: contorno + volume em baixa resolução, ampliados em blocos
# ---------------------------------------------------------------------------
def _shift(mask, dx, dy):
    m = pygame.Mask(mask.get_size())
    m.draw(mask, (dx, dy))
    return m


def outline_mask(mask, diag=False):
    """Pixels vazios encostados no desenho (contorno de 1 pixel)."""
    grown = pygame.Mask(mask.get_size())
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diag:
        dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in dirs:
        grown.draw(mask, (dx, dy))
    grown.erase(mask, (0, 0))
    return grown


def pixelize(low, px=PX, outline=OUTLINE, light=True):
    """Sprite desenhado em baixa resolução -> contorno, luz/sombra e ampliação em blocos de px.

    O desenho precisa ter 1 pixel livre em volta (o contorno ocupa a borda)."""
    low = low.copy()
    mask = pygame.mask.from_surface(low, 140)   # sombras semitransparentes não ganham contorno
    if light:
        # sombra: pixels da borda de baixo/direita (o vizinho de baixo/direita está vazio)
        below = _shift(mask, -1, -1)
        shade = mask.copy()
        shade.erase(below, (0, 0))
        low.blit(shade.to_surface(setcolor=(0, 0, 0, 85), unsetcolor=(0, 0, 0, 0)), (0, 0))
        # luz: pixels da borda de cima/esquerda
        above = _shift(mask, 1, 1)
        lit = mask.copy()
        lit.erase(above, (0, 0))
        lit.erase(shade, (0, 0))
        low.blit(lit.to_surface(setcolor=(255, 240, 220, 55), unsetcolor=(0, 0, 0, 0)), (0, 0))
    if outline:
        ring = outline_mask(mask)
        low.blit(ring.to_surface(setcolor=(*outline[:3], 255), unsetcolor=(0, 0, 0, 0)), (0, 0))
    if px == 1:
        return low
    return pygame.transform.scale(low, (low.get_width() * px, low.get_height() * px))


# ---------------------------------------------------------------------------
# Cenário: ladrilhos e objetos convertidos para pixel art
# ---------------------------------------------------------------------------
_BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def pixel_sprite(surf, px=PX, outline=OUTLINE, light=True):
    """Objeto do cenário (árvore, pedra, casa...): meia resolução, contorno e volume."""
    w, h = surf.get_width() // px, surf.get_height() // px
    low = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    low.blit(pygame.transform.scale(surf, (w, h)), (1, 1))
    out = pixelize(low, px, outline=outline, light=light)
    big = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    big.blit(out, (-px, -px))   # mesmo tamanho/âncora do original (o contorno da borda pode cortar 1 px)
    return big


# ---------------------------------------------------------------------------
# Interface: ícones em blocos e cantos "de pixel" nos retângulos arredondados
# ---------------------------------------------------------------------------
_orig_rect = pygame.draw.rect


def _pixel_rect(surface, color, rect, width=0, border_radius=0, *args, **kw):
    """pygame.draw.rect com cantos arredondados vira cantos em degraus (estilo pixel art)."""
    if not border_radius or border_radius <= 0 or args or any(v not in (-1, None) for v in kw.values()):
        return _orig_rect(surface, color, rect, width, border_radius, *args, **kw)
    r = pygame.Rect(rect)
    c = 2 if border_radius <= 5 else 4
    if r.w <= 2 * c + 1 or r.h <= 2 * c + 1:
        return _orig_rect(surface, color, r, width)
    if width <= 0:   # preenchido: cruz + degrau intermediário
        _orig_rect(surface, color, (r.x + c, r.y, r.w - 2 * c, r.h))
        _orig_rect(surface, color, (r.x, r.y + c, r.w, r.h - 2 * c))
        h = c // 2
        if h:
            _orig_rect(surface, color, (r.x + h, r.y + h, r.w - 2 * h, r.h - 2 * h))
        return r
    w = width
    if w >= c:
        c = w + 1
    _orig_rect(surface, color, (r.x + c, r.y, r.w - 2 * c, w))
    _orig_rect(surface, color, (r.x + c, r.bottom - w, r.w - 2 * c, w))
    _orig_rect(surface, color, (r.x, r.y + c, w, r.h - 2 * c))
    _orig_rect(surface, color, (r.right - w, r.y + c, w, r.h - 2 * c))
    b = max(1, c - w)
    for x, y in ((r.x + w, r.y + w), (r.right - w - b, r.y + w), (r.x + w, r.bottom - w - b),
                 (r.right - w - b, r.bottom - w - b)):
        _orig_rect(surface, color, (x, y, b, b))
    return r


def install():
    """Liga o estilo pixel nos retângulos arredondados de todo o jogo (chamado uma vez ao iniciar)."""
    pygame.draw.rect = _pixel_rect


install()


# ---------------------------------------------------------------------------
# Texturas de chão desenhadas direto em pixel (ruído em faixas + pontilhado)
# ---------------------------------------------------------------------------
def _lattice(rnd, n):
    return [[rnd.random() for _ in range(n)] for _ in range(n)]


def tile_noise(w, h, rnd, cells=(4, 8, 16), weights=(0.55, 0.3, 0.15)):
    """Ruído suave que repete sem emenda (w x h), valores 0..1."""
    layers = [(_lattice(rnd, c), c, wt) for c, wt in zip(cells, weights)]
    out = [[0.0] * w for _ in range(h)]
    for grid, c, wt in layers:
        for y in range(h):
            fy = y / h * c
            y0 = int(fy)
            ty = fy - y0
            ty = ty * ty * (3 - 2 * ty)
            r0, r1 = grid[y0 % c], grid[(y0 + 1) % c]
            row = out[y]
            for x in range(w):
                fx = x / w * c
                x0 = int(fx)
                tx = fx - x0
                tx = tx * tx * (3 - 2 * tx)
                a = r0[x0 % c] + (r0[(x0 + 1) % c] - r0[x0 % c]) * tx
                b = r1[x0 % c] + (r1[(x0 + 1) % c] - r1[x0 % c]) * tx
                row[x] += (a + (b - a) * ty) * wt
    return out


def banded(noise, cols, dither=0.06, bias=0.0):
    """Mapa de ruído -> superfície com poucas cores (faixas) e pontilhado Bayer nas transições."""
    h, w = len(noise), len(noise[0])
    lo = min(min(r) for r in noise)
    hi = max(max(r) for r in noise)
    span = (hi - lo) or 1
    n = len(cols)
    surf = pygame.Surface((w, h))
    surf.lock()
    for y in range(h):
        brow = _BAYER[y % 4]
        row = noise[y]
        for x in range(w):
            v = (row[x] - lo) / span + bias + (brow[x % 4] / 15 - 0.5) * dither * 2
            k = max(0, min(n - 1, int(v * n)))
            surf.set_at((x, y), cols[k])
    surf.unlock()
    return surf


def shades(col, fs):
    return [tuple(max(0, min(255, int(c * f))) for c in col) for f in fs]


# ---------------------------------------------------------------------------
# Ícones em pixel art: símbolo reduzido para uma grade pequena (14-20 px), poucas cores, contorno de 1 px,
# moldura com chanfro (luz em cima, sombra embaixo) e ampliação inteira sem suavizar
# ---------------------------------------------------------------------------
ICON_ART = 18   # resolução "de arte" alvo dos ícones


def _palette(low, maxc=6):
    """Cores principais do desenho (posterizadas), da mais frequente para a menos."""
    count = {}
    w, h = low.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = low.get_at((x, y))
            if a < 110:
                continue
            k = (r >> 4, g >> 4, b >> 4)
            count[k] = count.get(k, 0) + a
    keys = sorted(count, key=count.get, reverse=True)
    pal = []
    for k in keys:   # junta tons muito parecidos
        c = (k[0] * 16 + 8, k[1] * 16 + 8, k[2] * 16 + 8)
        if all(sum((c[i] - p[i]) ** 2 for i in range(3)) > 900 for p in pal):
            pal.append(c)
        if len(pal) >= maxc:
            break
    return pal


def _quantize(low, pal):
    w, h = low.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            r, g, b, a = low.get_at((x, y))
            if a < 110 or not pal:
                continue
            best = min(pal, key=lambda p: (p[0] - r) ** 2 + (p[1] - g) ** 2 + (p[2] - b) ** 2)
            out.set_at((x, y), (*best, 255))
    return out


def icon_frame(n, bg):
    """Moldura do ícone em n x n pixels: fundo, chanfro e borda escura com cantos recortados."""
    f = pygame.Surface((n, n), pygame.SRCALPHA)
    hi = tuple(min(255, c + 45) for c in bg)
    lo = tuple(int(c * 0.6) for c in bg)
    edge = (14, 10, 16)
    _orig_rect(f, bg, (1, 1, n - 2, n - 2))
    _orig_rect(f, hi, (2, 1, n - 4, 1))         # luz em cima
    _orig_rect(f, hi, (1, 2, 1, n - 4))         # e à esquerda
    _orig_rect(f, lo, (2, n - 2, n - 4, 1))     # sombra embaixo
    _orig_rect(f, lo, (n - 2, 2, 1, n - 4))     # e à direita
    _orig_rect(f, edge, (2, 0, n - 4, 1))
    _orig_rect(f, edge, (2, n - 1, n - 4, 1))
    _orig_rect(f, edge, (0, 2, 1, n - 4))
    _orig_rect(f, edge, (n - 1, 2, 1, n - 4))
    for x, y in ((1, 1), (n - 2, 1), (1, n - 2), (n - 2, n - 2)):
        f.set_at((x, y), edge)
    return f


def pixel_icon(symbol, bg, size, frame=True):
    """symbol: desenho grande (fundo transparente) -> ícone pixel art de size x size."""
    k = max(1, round(size / ICON_ART))
    n = max(8, size // k)
    inner = n - 2 if frame else n
    low = pygame.transform.smoothscale(symbol, (inner, inner))
    sym = _quantize(low, _palette(low))
    mask = pygame.mask.from_surface(sym, 1)
    out = icon_frame(n, bg) if frame else pygame.Surface((n, n), pygame.SRCALPHA)
    off = (n - inner) // 2
    dark = tuple(int(c * 0.35) for c in bg) if frame else OUTLINE
    ring = outline_mask(mask)
    out.blit(ring.to_surface(setcolor=(*dark, 255), unsetcolor=(0, 0, 0, 0)), (off, off))
    # volume: borda de baixo/direita do símbolo um pouco mais escura
    below = _shift(mask, -1, -1)
    shade = mask.copy()
    shade.erase(below, (0, 0))
    sym.blit(shade.to_surface(setcolor=(0, 0, 0, 70), unsetcolor=(0, 0, 0, 0)), (0, 0))
    out.blit(sym, (off, off))
    if n * k != size or k > 1:
        out = pygame.transform.scale(out, (n * k, n * k))
        if n * k != size:
            out = pygame.transform.scale(out, (size, size))
    return out
