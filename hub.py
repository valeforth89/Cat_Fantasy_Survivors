"""Acampamento (HUB central): área fechada na floresta onde o herói anda entre as funções do jogo.

- Fogueira no centro (os membros ativos da party descansam em volta dela).
- Portal ao norte: seleção de fase (e Start run).
- Barraca: gerenciar a party.
- Forja + ferreiro: melhorar os equipamentos.
- Baú perto do portal: inventário (fragmentos, gold).
- Joalheiro: acessórios.
- Bonecos de palha: Sala de Treino (testar formações, builds e DPS/HPS).

Encostar no lugar (ao entrar na área dele), clicar nele ou apertar E / ENTER perto dele abre a tela.
"""
import math
import random

import pygame

import cats
import pixel
from pygame.math import Vector2 as V

from data import W, H, CLASSES, WHITE, GREY, YELLOW, DARK
from icons import draw_class_icon, _Pen, hat_hood, GOLD, STEEL, OUT
import i18n
from i18n import tr
from scenery import Scenery

HERO_R = 14
HERO_SPEED = 230
SPAWN = V(640, 545)
AREA = pygame.Rect(110, 120, W - 220, H - 205)   # onde o herói pode andar (as árvores fecham o resto)

# lugares: id -> (posição, raio de colisão, nome EN, nome PT, ação)
PLACES = {
    "fire": (V(640, 395), 30, "Campfire", "Fogueira", None),
    "portal": (V(640, 170), 42, "Portal - Stage select", "Portal - Seleção de fase", "stages"),
    "rift": (V(1040, 190), 36, "Red Portal - Dungeons", "Portal Vermelho - Masmorras", "dungeons"),
    "mastery": (V(292, 225), 26, "Altar of Mastery", "Altar da Maestria", "mastery"),
    "altar": (V(482, 205), 26, "Altar of Trophies", "Altar dos Troféus", "altar"),
    "chest": (V(800, 205), 24, "Chest - Inventory", "Baú - Inventário", "chest"),
    "tent": (V(400, 370), 58, "Tent - Party", "Barraca - Party", "party"),
    "forge": (V(905, 360), 62, "Forge", "Forja", None),
    "smith": (V(842, 455), 18, "Blacksmith - Equipment", "Ferreiro - Equipamentos", "smith"),
    "jeweler": (V(470, 560), 30, "Jeweler - Accessories", "Joalheiro - Acessórios", "jeweler"),
    "training": (V(1050, 540), 30, "Training Room", "Sala de Treino", "training"),
    "greed": (V(236, 478), 28, "Altar of Greed", "Altar da Ganância", "greed"),
}
# new player experience: lugares que só aparecem depois de liberados (roster.unlocks); os outros começam abertos
PLACE_UNLOCK = {"chest": "chest", "smith": "smith", "forge": "smith", "jeweler": "jeweler", "altar": "altar",
                "mastery": "mastery", "rift": "dungeons", "greed": "greed"}
# dica (tips.py) de cada lugar, mostrada na primeira vez que ele é usado
PLACE_TIP = {"portal": "stages", "tent": "party", "training": "training", "chest": "chest", "smith": "smith",
             "jeweler": "jeweler", "altar": "altar", "mastery": "mastery", "rift": "dungeons", "greed": "greed"}


def _shadow(s, rect, a=70):
    """Sombra translúcida (elipse) no chão."""
    r = pygame.Rect(rect)
    surf = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, a), surf.get_rect())
    s.blit(surf, r.topleft)


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


class Hub:
    def __init__(self, app):
        self.app = app
        self.scenery = Scenery(0, seed=4242)
        self.t = 0.0
        self.reset()
        rnd = random.Random(99)
        # árvores fechando a área (duas fileiras desencontradas nas bordas)
        self.trees = []
        for x in range(-10, W + 60, 70):
            self.trees.append((V(x, 46), rnd.randrange(3)))
            self.trees.append((V(x + 35, 92), rnd.randrange(3)))
            self.trees.append((V(x, H - 20), rnd.randrange(3)))
            self.trees.append((V(x + 35, H + 22), rnd.randrange(3)))
        for y in range(120, H - 40, 70):
            self.trees.append((V(30, y), rnd.randrange(3)))
            self.trees.append((V(78, y + 35), rnd.randrange(3)))
            self.trees.append((V(W - 30, y), rnd.randrange(3)))
            self.trees.append((V(W - 78, y + 35), rnd.randrange(3)))
        self.trees.sort(key=lambda t: t[0].y)
        # decoração do chão longe dos lugares
        self.decor = []
        kinds = ["tuft"] * 5 + ["flower0", "flower1", "rock", "bush", "shroom", "stump"]
        for _ in range(70):
            p = V(rnd.uniform(130, W - 130), rnd.uniform(130, H - 90))
            if all((p - pl[0]).length() > pl[1] + 50 for pl in PLACES.values()) and \
                    ((p.x - 640) / 290) ** 2 + ((p.y - 395) / 190) ** 2 > 1:
                self.decor.append((p, rnd.choice(kinds)))

    def reset(self):
        """Herói volta para perto da fogueira (ao entrar no acampamento)."""
        self.pos = V(SPAWN)
        self.facing = V(0, -1)
        self.inside = {k for k, pl in PLACES.items() if (self.pos - pl[0]).length() <= pl[1] + HERO_R + 12}

    # ------------------------------------------------------------------ lógica
    def open(self, key):
        app = self.app
        action = PLACES[key][4]
        if action == "stages":
            app.stage_cursor = app.roster.stage
            app.rift_pick = None   # Endless Rift: o nível começa no mais alto liberado
            app.go("stages")
        elif action == "party":
            app.go("party")
        elif action == "smith":
            app.inv_mode = "smith"
            app.go("inventory")
        elif action == "chest":
            app.inv_mode = "chest"
            app.go("inventory")
        elif action == "jeweler":
            app.go("jeweler")
        elif action == "altar":
            app.go("altar")
        elif action == "mastery":
            app.go("mastery")
        elif action == "greed":
            app.go("greed")
        elif action == "training":
            app.start_training()
        elif action == "dungeons":
            app.dg_pick = None   # a seleção sempre começa no nível mais alto liberado de cada masmorra
            app.go("dungeons")

    def near(self):
        """Lugar com ação mais próximo dentro do alcance de interação (ou None)."""
        best = None
        for k, (p, r, *_rest) in self.places().items():
            if PLACES[k][4] is None:
                continue
            d = (self.pos - p).length()
            if d <= r + HERO_R + 14 and (best is None or d < best[0]):
                best = (d, k)
        return best[1] if best else None

    def update(self, dt, keys):
        self.t += dt
        d = V(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            d.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            d.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            d.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            d.x += 1
        if d.length_squared() > 0:
            d = d.normalize()
            self.facing = d
            self.pos += d * HERO_SPEED * dt
        # colisão com os lugares e com as bordas
        for k, (p, r, *_rest) in self.places().items():
            to = self.pos - p
            m = r + HERO_R
            if 0 < to.length_squared() < m * m:
                self.pos = p + to.normalize() * m
        self.pos.x = max(AREA.left, min(AREA.right, self.pos.x))
        self.pos.y = max(AREA.top, min(AREA.bottom, self.pos.y))
        # encostar: abre ao ENTRAR na área do lugar
        now = {k for k, pl in self.places().items() if (self.pos - pl[0]).length() <= pl[1] + HERO_R + 12}
        entered = [k for k in now - self.inside if PLACES[k][4]]
        self.inside = now
        if entered and d.length_squared() > 0:
            self.open(entered[0])

    def event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.app.go("menu")
            elif ev.key in (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                k = self.near()
                if k:
                    self.open(k)
            elif ev.key in (pygame.K_F1, pygame.K_h):
                self.app.open_faq("hub")
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.faq_rect().collidepoint(ev.pos):
                self.app.open_faq("hub")
                return True
            if self.help_rect().collidepoint(ev.pos):   # "?": explicação do acampamento
                self.app.show_tip("welcome", force=True)
                return True
            if self.app.touch.enabled and self.menu_rect().collidepoint(ev.pos):   # celular: não há ESC
                self.app.go("menu")
                return True
            k = self.hover_place(V(ev.pos))
            if k:
                self.open(k)
        return True

    def visible(self, k):
        return self.app.roster.unlocked(PLACE_UNLOCK.get(k))

    def places(self):
        """Lugares que já existem no acampamento (os bloqueados ficam escondidos)."""
        return {k: v for k, v in PLACES.items() if self.visible(k)}

    def is_new(self, k):
        """Liberado mas ainda não usado (mostra o selo NEW)."""
        tid = PLACE_TIP.get(k)
        return k in PLACE_UNLOCK and tid is not None and tid not in self.app.roster.tips_seen

    def hover_place(self, mp):
        for k, (p, r, *_rest) in self.places().items():
            if PLACES[k][4] and (mp - p).length() <= r + 14:
                return k
        return None

    def faq_rect(self):
        return pygame.Rect(W - 120, 64, 96, 36)

    def help_rect(self):
        return pygame.Rect(W - 166, 64, 36, 36)

    def menu_rect(self):
        return pygame.Rect(W - 120, 108, 96, 36)

    # ------------------------------------------------------------------ desenho
    def _clearing(self):
        """Clareira de terra batida em volta da fogueira e trilha até o portal, em pixel art (pontilhada nas bordas)."""
        surf = self.__dict__.get("_clear_surf")
        if surf is not None:
            return surf
        px = pixel.PX
        lw, lh = W // px, H // px
        low = pygame.Surface((lw, lh), pygame.SRCALPHA)
        rnd = random.Random(7)
        cx, cy = 640 / px, 395 / px
        base, dark, light = (128, 102, 70), (104, 82, 56), (150, 124, 88)
        for y in range(lh):
            for x in range(lw):
                d = ((x - cx) / (300 / px)) ** 2 + ((y - cy) / (205 / px)) ** 2
                path = abs(x - cx) < 40 / px and 150 / px < y < cy   # trilha até o portal
                if path:
                    d = min(d, (abs(x - cx) / (40 / px)) ** 2 * 0.9)
                t = pixel._BAYER[y % 4][x % 4] / 16
                if d < 0.55 or (d < 1.0 and t < (1.0 - d) / 0.45 * 0.9):
                    c = base if (x * 7 + y * 3) % 5 else dark
                    if rnd.random() < 0.03:
                        c = light
                    low.set_at((x, y), (*c, 200 if d < 0.55 else 150))
        surf = self._clear_surf = pygame.transform.scale(low, (lw * px, lh * px))
        return surf

    def draw(self):
        app = self.app
        s = app.screen
        sc = self.scenery
        tw, th = sc.ground.get_size()   # ladrilho do chão no tamanho real (sem sobrepor pedaços)
        for x in range(0, W, tw):
            for y in range(0, H, th):
                s.blit(sc.ground, (x, y))
        s.blit(self._clearing(), (0, 0))
        for p, kind in self.decor:
            img = sc.decor_sprites[kind]
            s.blit(img, (p.x - img.get_width() / 2, p.y - img.get_height() / 2))

        mp = V(app.mouse_pos())
        hot = self.hover_place(mp) or self.near()

        # objetos ordenados de cima para baixo (o herói entra na ordem pela posição y)
        draws = {"portal": self.draw_portal, "chest": self.draw_chest, "altar": self.draw_altar,
                 "mastery": self.draw_mastery, "rift": self.draw_rift, "forge": self.draw_forge, "tent": self.draw_tent,
                 "fire": self.draw_fire, "smith": self.draw_smith, "jeweler": self.draw_jeweler,
                 "training": self.draw_training, "greed": self.draw_greed}
        items = [(PLACES[k][0].y, fn) for k, fn in draws.items() if self.visible(k)] + [(self.pos.y, self.draw_hero)]
        # pixel art: os objetos vão para uma camada que recebe contorno escuro de uma vez só
        layer = self.__dict__.get("_layer")
        if layer is None:
            layer = self._layer = pygame.Surface((W, H), pygame.SRCALPHA)
        layer.fill((0, 0, 0, 0))
        cats.SUPPRESS_OUTLINE = True
        try:
            for _, fn in sorted(items, key=lambda it: it[0]):
                fn(layer)
        finally:
            cats.SUPPRESS_OUTLINE = False
        low = pygame.transform.scale(layer, (W // pixel.PX, H // pixel.PX))
        s.blit(pixel.pixelize(low, pixel.PX, light=False), (0, 0))
        for p, v in self.trees:   # árvores da borda por cima
            img = sc.tree_sprites[v]
            s.blit(img, (p.x - img.get_width() / 2, p.y - img.get_height() / 2 - 14))
        pixel.pixelate_world(s)   # pixel art: o acampamento vira blocos de 2x2

        # nomes dos lugares (o destacado mostra como abrir)
        for k, (p, r, en, pt, action) in self.places().items():
            if not action:
                continue
            name = pt if i18n.LANG == "pt" else en
            y = p.y - r - 22 if k not in ("tent", "forge") else p.y - r - 30
            if k == "smith":
                y = p.y + r + 14
            elif k == "portal":   # acima da pedra-chave do arco
                y = p.y - 94
            elif k == "rift":     # acima dos monólitos
                y = p.y - 84
            elif k == "greed":    # acima das orelhas do gato dourado
                y = p.y - 92
            col = YELLOW if k == hot else (235, 235, 240)
            surf = app.fonts["small"].render(name, True, col)
            box = surf.get_rect(center=(p.x, y)).inflate(12, 6)
            bg = pygame.Surface(box.size, pygame.SRCALPHA)
            bg.fill((15, 15, 22, 170))
            s.blit(bg, box)
            if k == hot:
                pygame.draw.rect(s, YELLOW, box, 1, border_radius=4)
            s.blit(surf, surf.get_rect(center=box.center))
            if self.is_new(k):   # lugar recém-liberado e ainda não usado
                pulse = 0.5 + 0.5 * math.sin(self.t * 5)
                nb = app.fonts["small"].render(i18n.L("NEW!", "NOVO!"), True, (30, 20, 10))
                nr = nb.get_rect(midbottom=(box.centerx, box.top - 3)).inflate(10, 4)
                pygame.draw.rect(s, (255, int(170 + 60 * pulse), 60), nr, border_radius=6)
                s.blit(nb, nb.get_rect(center=nr.center))

        # topo e rodapé
        app.text("CAMP", "big", YELLOW, (26, 16))
        fr = self.faq_rect()
        app.button(fr, "Wiki", fr.collidepoint(mp), (150, 200, 255))
        app.draw_help_button(self.help_rect(), mp)
        tip = "WASD move  ·  walk into or click a place to open it  ·  E / ENTER interact  ·  ESC main menu"
        if app.touch.enabled:
            mr = self.menu_rect()
            app.button(mr, "Menu", mr.collidepoint(mp))
            tip = i18n.L("Drag on the left side to walk  ·  tap a place to open it",
                         "Arraste no lado esquerdo para andar  ·  toque num lugar para abrir")
        surf = app.fonts["small"].render(tr(tip), True, (225, 225, 230))
        box = surf.get_rect(center=(W / 2, H - 16)).inflate(18, 8)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill((10, 10, 16, 190))
        s.blit(bg, box)
        s.blit(surf, surf.get_rect(center=box.center))
        app.draw_toast()

    def draw_hero(self, s):
        hero = self.app.roster.hero
        wf = cats.walk_frame(("hub", id(self)), self.pos, HERO_R)   # ciclo de passos enquanto anda
        draw_class_icon(s, hero.cls, self.pos, HERO_R, facing=self.facing, outline=YELLOW, who=hero.name, look=hero.look, member=hero,
                        walk=wf)

    def draw_fire(self, s):
        p = PLACES["fire"][0]
        t = self.t
        glow = pygame.Surface((300, 300), pygame.SRCALPHA)
        for r, a in ((140, 18), (100, 26), (65, 40)):
            pygame.draw.circle(glow, (255, 160, 60, a + int(6 * math.sin(t * 7))), (150, 150), r)
        s.blit(glow, (p.x - 150, p.y - 150))
        for k in range(8):   # pedras em volta
            a = k * math.tau / 8
            pygame.draw.circle(s, (120, 118, 112), p + V(math.cos(a) * 30, math.sin(a) * 20 + 6), 8)
            pygame.draw.circle(s, (80, 78, 74), p + V(math.cos(a) * 30, math.sin(a) * 20 + 6), 8, 2)
        pygame.draw.line(s, (100, 66, 40), p + V(-22, 10), p + V(22, -2), 8)   # lenha
        pygame.draw.line(s, (90, 58, 36), p + V(-22, -2), p + V(22, 10), 8)
        for k, (col, h, w) in enumerate((((230, 70, 30), 46, 22), ((255, 150, 40), 34, 16), ((255, 230, 120), 20, 9))):
            pts = []
            for i in range(9):
                a = math.pi + i * math.pi / 8
                fl = 1 + 0.18 * math.sin(t * 11 + i * 1.7 + k)
                rr = (h if i == 4 else h * 0.55 if i in (3, 5) else h * 0.3) * fl
                pts.append(p + V(math.cos(a) * w * (1 if i in (0, 8) else 0.7), math.sin(a) * rr + 2))
            pygame.draw.polygon(s, col, pts)
        for i in range(5):   # faíscas
            ph = (t * 0.8 + i * 0.37) % 1
            sp = p + V(math.sin(i * 2.3 + t * 2) * 12, -20 - ph * 70)
            pygame.draw.circle(s, (255, 200, 90), sp, max(1, int(3 * (1 - ph))))
        # membros ativos descansando em volta
        members = [m for m in self.app.roster.active() if not m.hero]
        for i, m in enumerate(members):
            a = math.radians(200 + i * 360 / max(1, len(members)) * 0.75)
            mp = p + V(math.cos(a) * 92, math.sin(a) * 62 + 8)
            draw_class_icon(s, m.cls, mp, 12, facing=p - mp, who=m.name, look=m.look, member=m)

    def draw_training(self, s):
        """Entrada da Sala de Treino: cerquinha de madeira, dois bonecos de palha e uma placa."""
        from enemy_sprites import draw_enemy
        p = PLACES["training"][0]
        _shadow(s, (p.x - 46, p.y + 16, 92, 18), 60)
        wood, dark = (126, 88, 50), (82, 56, 30)
        for dx in (-44, 44):
            pygame.draw.rect(s, wood, (p.x + dx - 4, p.y - 2, 8, 26))
            pygame.draw.rect(s, dark, (p.x + dx - 4, p.y - 2, 8, 26), 1)
        for dy in (4, 14):
            pygame.draw.line(s, wood, (p.x - 44, p.y + dy), (p.x + 44, p.y + dy), 4)
        frame = int(self.t * 2)
        draw_enemy(s, "dummy", (p.x - 20, p.y - 6), 11, (196, 170, 120), True, frame)
        draw_enemy(s, "dummy", (p.x + 22, p.y - 2), 9, (186, 160, 112), True, frame + 1)
        # placa
        pygame.draw.rect(s, dark, (p.x + 50, p.y - 12, 5, 36))
        sign = pygame.Rect(p.x + 36, p.y - 30, 34, 22)
        pygame.draw.rect(s, (160, 116, 66), sign, border_radius=3)
        pygame.draw.rect(s, dark, sign, 2, border_radius=3)
        pygame.draw.line(s, (60, 40, 22), (sign.x + 8, sign.centery), (sign.right - 8, sign.centery), 2)
        pygame.draw.circle(s, (200, 50, 50), (sign.centerx, sign.centery), 4)

    def _vortex(self, s, c, rx, ry, cols, spin, arms=3):
        """Redemoinho do portal: camadas de cor, braços em espiral girando e brilho no centro."""
        surf = pygame.Surface((int(rx * 2 + 4), int(ry * 2 + 4)), pygame.SRCALPHA)
        o = V(surf.get_width() / 2, surf.get_height() / 2)
        n = len(cols)
        for k, col in enumerate(cols):
            f = 1 - k / n
            pygame.draw.ellipse(surf, col, (o.x - rx * f, o.y - ry * f, rx * 2 * f, ry * 2 * f))
        hi = tuple(min(255, c + 70) for c in cols[-1][:3])
        for a in range(arms):   # braços em espiral
            pts = []
            for q in range(14):
                u = q / 13
                ang = spin + a * math.tau / arms + u * 4.2
                pts.append(o + V(math.cos(ang) * rx * (1 - u) * 0.95, math.sin(ang) * ry * (1 - u) * 0.95))
            pygame.draw.lines(surf, (*hi, 200), False, pts, 3)
        pygame.draw.ellipse(surf, (*hi, 230), (o.x - rx * 0.18, o.y - ry * 0.18, rx * 0.36, ry * 0.36))
        s.blit(surf, (c.x - o.x, c.y - o.y))

    def draw_portal(self, s):
        """Portal das fases: escadaria, arco de pedras talhadas com runas acesas, pilares e redemoinho violeta."""
        p = PLACES["portal"][0]
        t = self.t
        _shadow(s, (p.x - 66, p.y + 40, 132, 26), 70)
        stone, dark, light = (128, 124, 140), (82, 78, 94), (160, 156, 172)
        pygame.draw.rect(s, dark, (p.x - 64, p.y + 46, 128, 14))                     # degraus
        pygame.draw.rect(s, stone, (p.x - 56, p.y + 38, 112, 12))
        pygame.draw.line(s, light, (p.x - 56, p.y + 38), (p.x + 55, p.y + 38), 2)
        for x in range(-60, 61, 20):
            pygame.draw.line(s, (70, 66, 80), (p.x + x, p.y + 47), (p.x + x, p.y + 59), 1)
        c = p + V(0, 2)
        self._vortex(s, c, 34, 48, [(70, 40, 140, 230), (100, 60, 190, 230), (130, 90, 230, 230),
                                    (160, 130, 245, 230), (195, 175, 255, 235)], -t * 1.6)
        rune = 0.5 + 0.5 * math.sin(t * 2.5)
        for i in range(9):   # arco de pedras talhadas
            a0 = math.pi + i * math.pi / 9
            a1 = math.pi + (i + 1) * math.pi / 9
            pts = [c + V(math.cos(a0) * 40, math.sin(a0) * 54), c + V(math.cos(a0) * 56, math.sin(a0) * 72),
                   c + V(math.cos(a1) * 56, math.sin(a1) * 72), c + V(math.cos(a1) * 40, math.sin(a1) * 54)]
            pygame.draw.polygon(s, light if i % 2 else stone, pts)
            pygame.draw.polygon(s, OUT, pts, 1)
            m = c + V(math.cos((a0 + a1) / 2) * 48, math.sin((a0 + a1) / 2) * 63)
            pygame.draw.circle(s, (int(150 + 90 * rune), int(110 + 80 * rune), 255), m, 2)   # runa acesa
        for sx in (-1, 1):   # pilares
            col_r = pygame.Rect(c.x + sx * 48 - 8, c.y - 2, 16, 44)
            pygame.draw.rect(s, stone, col_r)
            pygame.draw.rect(s, light, (col_r.x, col_r.y, 4, col_r.h))
            pygame.draw.rect(s, OUT, col_r, 1)
            pygame.draw.rect(s, dark, (col_r.x - 3, col_r.bottom - 6, 22, 6))
        top = c + V(0, -72)   # pedra-chave com cristal
        pygame.draw.polygon(s, light, [top + V(-10, -4), top + V(10, -4), top + V(7, 12), top + V(-7, 12)])
        pygame.draw.polygon(s, OUT, [top + V(-10, -4), top + V(10, -4), top + V(7, 12), top + V(-7, 12)], 1)
        gem = [top + V(0, -2), top + V(5, 4), top + V(0, 10), top + V(-5, 4)]
        pygame.draw.polygon(s, (200, 160, 255), gem)
        pygame.draw.polygon(s, (250, 240, 255), [top + V(0, -2), top + V(5, 4), top + V(0, 4)])
        for i in range(5):   # pedrinhas flutuando em volta
            a = t * 0.9 + i * math.tau / 5
            q = c + V(math.cos(a) * 70, math.sin(a) * 26 - 4)
            pygame.draw.polygon(s, stone, [q + V(-4, 0), q + V(0, -4), q + V(4, 1), q + V(0, 4)])
        for i in range(8):   # faíscas sendo sugadas
            a = t * 2.2 + i * math.tau / 8
            rr = 1 - ((t * 0.6 + i / 8) % 1)
            q = c + V(math.cos(a) * 30 * rr, math.sin(a) * 44 * rr)
            pygame.draw.circle(s, (235, 215, 255), q, 2)

    def draw_rift(self, s):
        """Portal vermelho (masmorras): fenda entre monólitos de obsidiana, chão rachado em brasa e redemoinho rubro."""
        p = PLACES["rift"][0]
        t = self.t
        _shadow(s, (p.x - 56, p.y + 30, 112, 22), 75)
        pulse = 0.5 + 0.5 * math.sin(t * 3)
        for (dx, dy, ex, ey) in ((-10, 40, -46, 52), (8, 40, 40, 56), (0, 42, 4, 62), (-24, 46, -30, 60)):
            pygame.draw.line(s, (int(200 + 50 * pulse), 70, 40), p + V(dx, dy), p + V(ex, ey), 2)   # rachaduras
        c = p + V(0, 2)
        self._vortex(s, c, 26, 40, [(70, 10, 20, 235), (130, 20, 30, 235), (190, 40, 40, 235),
                                    (230, 90, 60, 235), (255, 170, 120, 240)], t * 2.0)
        obs, obs_l = (46, 36, 52), (86, 70, 96)
        shards = [(-38, 44, -30, -40, -14, 40), (36, 44, 30, -46, 14, 40), (-50, 44, -52, -6, -34, 44),
                  (50, 44, 54, -12, 34, 44), (-20, -36, 2, -64, 20, -38)]
        for (x0, y0, x1, y1, x2, y2) in shards:   # monólitos de obsidiana
            pts = [p + V(x0, y0), p + V(x1, y1), p + V(x2, y2)]
            pygame.draw.polygon(s, obs, pts)
            pygame.draw.line(s, obs_l, pts[0], pts[1], 2)
            pygame.draw.polygon(s, OUT, pts, 1)
        for (x, y) in ((-34, 0), (34, -6), (0, -50)):   # runas vermelhas
            pygame.draw.circle(s, (255, int(80 + 80 * pulse), 60), p + V(x, y), 2)
        for i in range(7):   # brasas subindo
            ph = (t * 0.5 + i / 7) % 1
            q = p + V(math.sin(t * 2 + i) * 22 + (i - 3) * 6, 30 - ph * 90)
            pygame.draw.circle(s, (255, int(140 + 80 * (1 - ph)), 60), q, 2 if ph < 0.7 else 1)

    def draw_chest(self, s):
        p = PLACES["chest"][0]
        _shadow(s, (p.x - 26, p.y + 10, 52, 14), 70)
        body = pygame.Rect(p.x - 24, p.y - 10, 48, 28)
        pygame.draw.rect(s, (130, 82, 40), body, border_radius=4)
        pygame.draw.rect(s, (150, 98, 50), (p.x - 24, p.y - 24, 48, 16), border_top_left_radius=12,
                         border_top_right_radius=12)
        pygame.draw.rect(s, OUT, (p.x - 24, p.y - 24, 48, 42), 2, border_radius=6)
        for x in (-14, 14):
            pygame.draw.line(s, GOLD, (p.x + x, p.y - 23), (p.x + x, p.y + 17), 4)
        pygame.draw.rect(s, GOLD, (p.x - 5, p.y - 12, 10, 10), border_radius=2)

    def draw_altar(self, s):
        """Altar de pedra com os troféus obtidos brilhando em cima."""
        import trophies as trophy
        p = PLACES["altar"][0]
        t = self.t
        _shadow(s, (p.x - 34, p.y + 12, 68, 16), 70)
        pygame.draw.rect(s, (110, 106, 118), (p.x - 30, p.y - 4, 60, 22), border_radius=3)   # base
        pygame.draw.rect(s, (135, 130, 145), (p.x - 24, p.y - 16, 48, 14), border_radius=3)  # tampo
        pygame.draw.rect(s, OUT, (p.x - 30, p.y - 4, 60, 22), 2, border_radius=3)
        pygame.draw.rect(s, OUT, (p.x - 24, p.y - 16, 48, 14), 2, border_radius=3)
        for x in (-20, 0, 20):   # runas
            pygame.draw.line(s, (90, 86, 100), (p.x + x - 3, p.y + 2), (p.x + x + 3, p.y + 12), 2)
        # uma bolinha por bioma: enchem de baixo para cima conforme os troféus do bioma ficam ativos
        from data import BIOMES
        roster = self.app.roster
        owned = set(getattr(roster, "trophies", []))
        active = set(getattr(roster, "trophies_on", []))
        glow = 0.5 + 0.5 * math.sin(t * 3)
        rad = 6 if len(BIOMES) <= 4 else 5
        for i, b in enumerate(BIOMES):
            tids = [tid for tid in trophy.ORDER if trophy.TROPHIES[tid][0] in b["stages"]]
            got = sum(1 for tid in tids if tid in owned)
            on = sum(1 for tid in tids if tid in active)
            c = (p.x - 24 + i * 48 / max(1, len(BIOMES) - 1), p.y - 23)
            col = b["color"]
            if on:   # brilho quando o bioma tem troféu ativo
                gl = pygame.Surface((22, 22), pygame.SRCALPHA)
                pygame.draw.circle(gl, (255, 220, 120, int(60 + 70 * glow * on / max(1, len(tids)))), (11, 11), 11)
                s.blit(gl, (c[0] - 11, c[1] - 11))
            pygame.draw.circle(s, (30, 30, 38), c, rad)
            if on:
                fill = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(fill, col, (rad, rad), rad)
                fill.fill((0, 0, 0, 0), (0, 0, rad * 2, int(rad * 2 * (1 - on / max(1, len(tids))))))
                s.blit(fill, (c[0] - rad, c[1] - rad))
            pygame.draw.circle(s, col if got else (75, 73, 84), c, rad, 1)

    def draw_greed(self, s):
        """Altar of Greed: gato da sorte dourado (maneki-neko) acenando sobre um pedestal, com moedas em volta."""
        import greed as grd
        p = PLACES["greed"][0]
        t = self.t
        _shadow(s, (p.x - 34, p.y + 14, 68, 16), 70)
        stone, stone_d = (118, 110, 104), (88, 82, 78)
        pygame.draw.polygon(s, stone_d, [p + V(-30, 22), p + V(30, 22), p + V(24, 6), p + V(-24, 6)])   # degrau
        pygame.draw.rect(s, stone, (p.x - 20, p.y - 10, 40, 18), border_radius=2)                      # pedestal
        pygame.draw.polygon(s, OUT, [p + V(-30, 22), p + V(30, 22), p + V(24, 6), p + V(-24, 6)], 2)
        pygame.draw.rect(s, OUT, (p.x - 20, p.y - 10, 40, 18), 2, border_radius=2)
        pygame.draw.rect(s, (200, 160, 60), (p.x - 14, p.y - 4, 28, 5))                                  # placa dourada
        # moedas empilhadas na base (crescem conforme o gold investido no altar)
        n = min(7, 1 + int(grd.spent() ** 0.3 / 2)) if grd.LEVELS else 1
        for k in range(n):
            cx = p.x + (-24 if k % 2 == 0 else 24) + (k // 2) * (3 if k % 2 == 0 else -3)
            cy = p.y + 12 - (k // 2) * 4
            pygame.draw.ellipse(s, (235, 195, 70), (cx - 6, cy - 3, 12, 6))
            pygame.draw.ellipse(s, (150, 110, 30), (cx - 6, cy - 3, 12, 6), 1)
        # o gato dourado
        gold, gold_d, gold_l = (240, 200, 80), (190, 145, 45), (255, 235, 150)
        c = p + V(0, -35)
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 215, 100, int(50 + 25 * math.sin(t * 2.5))), (40, 40), 40)
        s.blit(glow, (c.x - 40, c.y - 40))
        pygame.draw.ellipse(s, gold, (c.x - 18, c.y - 3, 36, 30))                          # corpo
        pygame.draw.ellipse(s, OUT, (c.x - 18, c.y - 3, 36, 30), 2)
        pygame.draw.circle(s, gold, c + V(0, -10.8), 16)                                       # cabeça
        pygame.draw.circle(s, OUT, c + V(0, -10.8), 16, 2)
        for sx in (-1, 1):                                                                  # orelhas
            pts = [c + V(sx * 5, -23), c + V(sx * 15, -33), c + V(sx * 15, -15)]
            pygame.draw.polygon(s, gold, pts)
            pygame.draw.polygon(s, OUT, pts, 2)
        wave = math.sin(t * 4) * 4                                                          # patinha acenando
        paw = c + V(18, -16 + wave)
        pygame.draw.line(s, gold_d, c + V(12.15, 0), paw, 8)
        pygame.draw.circle(s, gold, paw, 7)
        pygame.draw.circle(s, OUT, paw, 7, 2)
        pygame.draw.circle(s, (235, 195, 70), c + V(-8.1, 13.5), 8)                             # moeda no colo
        pygame.draw.circle(s, gold_d, c + V(-8.1, 13.5), 8, 2)
        for sx in (-4, 4):                                                                  # olhinhos fechados
            pygame.draw.arc(s, OUT, pygame.Rect(c.x + sx * 1.35 - 4, c.y - 15, 8, 6), 0, math.pi, 2)
        pygame.draw.line(s, (200, 60, 60), c + V(-10.8, -1.35), c + V(10.8, -1.35), 3)                   # coleira vermelha
        pygame.draw.circle(s, gold_l, c + V(0, 1.35), 2)
        pygame.draw.circle(s, gold_l, c + V(-5.4, -17.55), 2)                                     # brilho

    def draw_mastery(self, s):
        """Altar da Maestria: pedestal com um cristal que brilha mais conforme o nível do altar."""
        import progression as prog
        p = PLACES["mastery"][0]
        t = self.t
        lvl = prog.altar_level()
        _shadow(s, (p.x - 30, p.y + 12, 60, 16), 70)
        pygame.draw.polygon(s, (100, 104, 120), [p + V(-26, 18), p + V(26, 18), p + V(18, 2), p + V(-18, 2)])
        pygame.draw.rect(s, (125, 128, 145), (p.x - 12, p.y - 14, 24, 18))
        pygame.draw.polygon(s, OUT, [p + V(-26, 18), p + V(26, 18), p + V(18, 2), p + V(-18, 2)], 2)
        pygame.draw.rect(s, OUT, (p.x - 12, p.y - 14, 24, 18), 2)
        bob = math.sin(t * 2) * 3
        c = p + V(0, -32 + bob)
        glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        a = min(150, 50 + lvl * 6) * (0.75 + 0.25 * math.sin(t * 3))
        pygame.draw.circle(glow, (110, 220, 235, int(a)), (30, 30), 22 + min(8, lvl))
        s.blit(glow, (c.x - 30, c.y - 30))
        pts = [c + V(0, -14), c + V(9, 0), c + V(0, 14), c + V(-9, 0)]
        pygame.draw.polygon(s, (120, 225, 240), pts)
        pygame.draw.polygon(s, (230, 255, 255), [c + V(0, -14), c + V(9, 0), c + V(0, 0)])
        pygame.draw.polygon(s, OUT, pts, 2)

    def draw_tent(self, s):
        """Barraca da party: lona listrada com barrado, abas presas, lanterna lá dentro, cordas, tapete e caixotes."""
        p = PLACES["tent"][0]
        t = self.t
        _shadow(s, (p.x - 80, p.y + 24, 160, 34), 75)
        red, red_d, cream, cream_d = (170, 58, 52), (122, 40, 38), (226, 206, 160), (180, 160, 120)
        L, T, R = p + V(-70, 42), p + V(0, -60), p + V(70, 42)
        for sx in (-1, 1):   # cordas e estacas
            stake = p + V(sx * 92, 44)
            pygame.draw.line(s, (200, 185, 150), p + V(sx * 36, -12), stake, 1)
            pygame.draw.line(s, (110, 80, 50), stake, stake + V(0, 6), 3)
        n = 8
        for i in range(n):   # gomos listrados (mais escuros do lado esquerdo)
            a, b = L.lerp(R, i / n), L.lerp(R, (i + 1) / n)
            col = (red if i % 2 == 0 else cream)
            if i < n // 2:
                col = red_d if i % 2 == 0 else cream_d
            pygame.draw.polygon(s, col, [a, T, b])
        pygame.draw.line(s, (90, 30, 30), T, p + V(0, 42), 1)
        # entrada aberta com as abas presas para os lados e luz de lanterna lá dentro
        door = [p + V(-20, 42), p + V(0, -4), p + V(20, 42)]
        pygame.draw.polygon(s, (36, 24, 22), door)
        glow = 0.75 + 0.25 * math.sin(t * 4)
        lamp = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(lamp, (255, 190, 90, int(110 * glow)), (20, 20), 16)
        s.blit(lamp, (p.x - 20, p.y + 6))
        pygame.draw.rect(s, (255, 210, 120), (p.x - 3, p.y + 20, 6, 8))
        pygame.draw.polygon(s, red, [p + V(-20, 42), p + V(0, -4), p + V(-30, 30)])
        pygame.draw.polygon(s, red, [p + V(20, 42), p + V(0, -4), p + V(30, 30)])
        pygame.draw.line(s, GOLD, p + V(-28, 26), p + V(-24, 31), 2)   # amarras
        pygame.draw.line(s, GOLD, p + V(28, 26), p + V(24, 31), 2)
        for i in range(10):   # barrado com franjas douradas
            q = L.lerp(R, (i + 0.5) / 10)
            pygame.draw.polygon(s, GOLD, [q + V(-7, 0), q + V(7, 0), q + V(0, 7)])
        pygame.draw.polygon(s, OUT, [L, T, R], 2)
        pygame.draw.line(s, (120, 90, 60), T, T + V(0, -18), 3)   # mastro e bandeira tremulando
        wv = math.sin(t * 5) * 3
        pygame.draw.polygon(s, (240, 210, 90), [T + V(0, -18), T + V(20, -14 + wv), T + V(2, -8)])
        rug = pygame.Rect(p.x - 24, p.y + 46, 48, 12)   # tapete
        pygame.draw.rect(s, (120, 60, 110), rug)
        pygame.draw.rect(s, GOLD, rug, 1)
        pygame.draw.line(s, (220, 170, 90), (rug.x + 6, rug.centery), (rug.right - 6, rug.centery), 1)
        crate = pygame.Rect(p.x + 54, p.y + 18, 24, 22)   # caixote e saco de dormir
        pygame.draw.rect(s, (130, 92, 52), crate)
        pygame.draw.line(s, (90, 62, 36), crate.topleft, crate.bottomright, 2)
        pygame.draw.rect(s, OUT, crate, 1)
        pygame.draw.ellipse(s, (70, 100, 130), (p.x - 86, p.y + 26, 30, 16))
        pygame.draw.line(s, (40, 60, 80), (p.x - 72, p.y + 27), (p.x - 72, p.y + 41), 2)

    def draw_forge(self, s):
        """Forja do ferreiro: base de pedra, parede de enxaimel, telhado de tábuas, chaminé com faíscas,
        boca da forja em arco com brasa, foles, suporte de armas, barril e placa com martelo."""
        p = PLACES["forge"][0]
        t = self.t
        _shadow(s, (p.x - 84, p.y + 30, 168, 36), 75)
        stone, stone_d = (118, 112, 108), (88, 84, 80)
        base = pygame.Rect(p.x - 66, p.y + 4, 132, 38)   # base de pedra
        pygame.draw.rect(s, stone, base)
        for row in range(3):
            for col in range(7):
                bx = base.x + col * 20 + (10 if row % 2 else 0) - 4
                pygame.draw.rect(s, stone_d, (bx, base.y + row * 13 + 1, 18, 11), 1)
        wall = pygame.Rect(p.x - 62, p.y - 34, 124, 38)   # enxaimel
        pygame.draw.rect(s, (214, 196, 160), wall)
        beam = (86, 56, 36)
        pygame.draw.rect(s, beam, (wall.x, wall.y, wall.w, 4))
        pygame.draw.rect(s, beam, (wall.x, wall.bottom - 4, wall.w, 4))
        for x in (0, 30, 62, 94, 120):
            pygame.draw.rect(s, beam, (wall.x + x, wall.y, 4, wall.h))
        for x0 in (4, 66):
            pygame.draw.line(s, beam, (wall.x + x0, wall.bottom - 4), (wall.x + x0 + 26, wall.y + 4), 3)
        win = pygame.Rect(wall.x + 38, wall.y + 10, 18, 16)   # janelinha acesa
        flick = 0.8 + 0.2 * math.sin(t * 7)
        pygame.draw.rect(s, (int(255 * flick), int(170 * flick), 70), win)
        pygame.draw.line(s, beam, win.midtop, win.midbottom, 2)
        pygame.draw.rect(s, beam, win, 2)
        roof = [p + V(-80, -32), p + V(-60, -74), p + V(60, -74), p + V(80, -32)]   # telhado de tábuas
        pygame.draw.polygon(s, (112, 66, 42), roof)
        for i in range(1, 5):
            y = -74 + i * 8.4
            w = 60 + i * 4
            pygame.draw.line(s, (84, 48, 30), p + V(-w, y), p + V(w, y), 2)
            for x in range(-int(w) + 8, int(w), 16):
                pygame.draw.line(s, (84, 48, 30), p + V(x + (8 if i % 2 else 0), y - 8), p + V(x + (8 if i % 2 else 0), y), 1)
        pygame.draw.line(s, (150, 96, 60), p + V(-60, -74), p + V(60, -74), 3)
        pygame.draw.polygon(s, OUT, roof, 2)
        chim = pygame.Rect(p.x + 30, p.y - 98, 20, 40)   # chaminé
        pygame.draw.rect(s, stone, chim)
        for yy in range(chim.y + 6, chim.bottom, 8):
            pygame.draw.line(s, stone_d, (chim.x, yy), (chim.right, yy), 1)
        pygame.draw.rect(s, stone_d, (chim.x - 3, chim.y - 4, 26, 6))
        pygame.draw.rect(s, OUT, chim, 1)
        for i in range(4):   # fumaça e faíscas
            ph = (t * 0.35 + i * 0.25) % 1
            pygame.draw.circle(s, (150, 148, 152), (chim.centerx + math.sin(t + i) * 6, chim.y - 8 - ph * 56),
                               int(5 + ph * 9), 0 if ph < 0.55 else 2)
        for i in range(3):
            ph = (t * 0.9 + i / 3) % 1
            pygame.draw.circle(s, (255, 190, 80), (chim.centerx + math.sin(t * 3 + i * 2) * 10, chim.y - ph * 40), 1)
        mouth = pygame.Rect(p.x - 24, p.y + 2, 48, 40)   # boca da forja em arco de tijolos
        pygame.draw.rect(s, (150, 70, 50), mouth.inflate(10, 6), border_top_left_radius=28, border_top_right_radius=28)
        pygame.draw.rect(s, (36, 26, 24), mouth, border_top_left_radius=24, border_top_right_radius=24)
        glow = 150 + int(60 * (0.5 + 0.5 * math.sin(t * 5)))
        pygame.draw.rect(s, (glow, 90, 30), mouth.inflate(-12, -16).move(0, 6), border_top_left_radius=18,
                         border_top_right_radius=18)
        for i in range(5):   # brasas
            pygame.draw.circle(s, (255, 200 + 10 * (i % 3), 90), (mouth.x + 10 + i * 7, mouth.bottom - 6 - (i % 2) * 3), 2)
        bel = [p + V(-58, 34), p + V(-36, 26), p + V(-36, 40)]   # fole
        pygame.draw.polygon(s, (120, 80, 50), bel)
        pygame.draw.polygon(s, OUT, bel, 1)
        for k, (x, col) in enumerate(((-74, (200, 205, 215)), (-68, (170, 170, 180)), (-62, (200, 205, 215)))):
            pygame.draw.line(s, col, p + V(x, -10), p + V(x, 20), 3)   # armas no suporte
        pygame.draw.polygon(s, (170, 170, 180), [p + V(-68, -10), p + V(-60, -16), p + V(-60, -4)])
        pygame.draw.line(s, (100, 70, 45), p + V(-80, 6), p + V(-56, 6), 3)
        barrel = pygame.Rect(p.x + 60, p.y + 14, 20, 26)   # barril d'água
        pygame.draw.rect(s, (120, 80, 48), barrel, border_radius=4)
        pygame.draw.line(s, (60, 60, 66), (barrel.x, barrel.y + 7), (barrel.right, barrel.y + 7), 2)
        pygame.draw.line(s, (60, 60, 66), (barrel.x, barrel.bottom - 7), (barrel.right, barrel.bottom - 7), 2)
        pygame.draw.ellipse(s, (70, 110, 150), (barrel.x + 2, barrel.y - 3, 16, 6))
        pygame.draw.rect(s, OUT, barrel, 1, border_radius=4)
        sign = pygame.Rect(p.x - 52, p.y - 28, 22, 16)   # placa com martelo
        pygame.draw.line(s, beam, (sign.centerx - 6, sign.y - 6), (sign.centerx - 6, sign.y), 1)
        pygame.draw.line(s, beam, (sign.centerx + 6, sign.y - 6), (sign.centerx + 6, sign.y), 1)
        pygame.draw.rect(s, (150, 110, 70), sign)
        pygame.draw.rect(s, OUT, sign, 1)
        pygame.draw.line(s, (60, 60, 66), (sign.x + 6, sign.bottom - 4), (sign.right - 7, sign.y + 5), 2)
        pygame.draw.rect(s, (170, 170, 180), (sign.right - 11, sign.y + 2, 7, 5))
        pygame.draw.rect(s, OUT, wall, 1)

    def draw_smith(self, s):
        p = PLACES["smith"][0]
        t = self.t
        a = V(p.x - 34, p.y + 6)   # bigorna
        pygame.draw.polygon(s, (70, 72, 80), [a + V(-16, -6), a + V(18, -6), a + V(10, 2), a + V(-8, 2)])
        pygame.draw.rect(s, (60, 62, 70), (a.x - 5, a.y + 2, 10, 10))
        # ferreiro: gato de smoking com avental de couro (aparência fixa)
        cats.draw_cat(s, None, p, 16, (-1, 0.1), cats.NPC_LOOKS["smith"], tunic=(96, 64, 42), shadow=True)
        swing = math.sin(t * 6) * 0.6   # martelo batendo
        hand = p + V(-14, -2)
        tip = hand + V(-10, -14).rotate(math.degrees(swing))
        pygame.draw.line(s, (120, 80, 50), hand, tip, 4)
        pygame.draw.rect(s, STEEL, (tip.x - 7, tip.y - 5, 14, 10), border_radius=2)
        if math.sin(t * 6) > 0.95:
            for i in range(4):
                pygame.draw.circle(s, (255, 210, 90), a + V(random.uniform(-12, 12), random.uniform(-12, -2)), 2)

    def draw_jeweler(self, s):
        p = PLACES["jeweler"][0]
        t = self.t
        _shadow(s, (p.x - 44, p.y + 12, 88, 18), 60)
        table = pygame.Rect(p.x - 10, p.y - 2, 50, 24)   # bancada com joias
        pygame.draw.rect(s, (110, 70, 45), table, border_radius=4)
        pygame.draw.rect(s, OUT, table, 2, border_radius=4)
        for i, col in enumerate(((90, 200, 255), (240, 80, 120), (120, 230, 140), GOLD)):
            gx = table.x + 9 + i * 11
            sparkle = 1 + 0.3 * math.sin(t * 4 + i)
            pygame.draw.polygon(s, col, [(gx, table.y + 4), (gx + 4 * sparkle, table.y + 9), (gx, table.y + 14),
                                         (gx - 4 * sparkle, table.y + 9)])
        c = p + V(-26, 0)
        # joalheiro: gato siamês de capuz roxo e monóculo (aparência fixa)
        cats.draw_cat(s, None, c, 15, (1, 0.1), cats.NPC_LOOKS["jeweler"], tunic=(120, 70, 160), shadow=False)
        head = c + V(0, -15 * 0.95 * 0.45)
        hat_hood(_Pen(s, head, 14), (90, 50, 130), gem=(255, 230, 120))
        eye = head + V(0.62 * 14, 0)
        pygame.draw.circle(s, GOLD, eye, 4, 1)                              # monóculo
