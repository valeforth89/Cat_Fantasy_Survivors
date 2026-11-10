"""Sala de Treino: um campo cercado para testar formações, builds e o DPS/HPS da party contra bonecos de palha.

- Os bonecos são invencíveis: quando a vida chega a zero ela volta cheia (o medidor conta todo o dano).
- Pode colocar bonecos comuns (com a quantidade), de elite, super elite, esquadrão de elite e chefão.
- "Os bonecos atacam": se ligado, eles andam até a party, batem e usam as habilidades da classe; se desligado,
  ficam parados no lugar (voltam para o lugar se forem empurrados).
- A força dos bonecos segue o monstro base (Morcego, Lobo...), a fase e o minuto da run escolhidos.
- Nada de recompensa: sem EXP, gold, fragmentos ou drops. O herói não cai (levanta na hora com a vida cheia).
- Painel (tecla T ou o botão no canto): bonecos, comportamento, medidor, level ups, party e saída.
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

from data import W, H, CLASSES, STAGES, ENEMY_TYPES, ENEMY_NAMES, WHITE, GREY, YELLOW, GREEN, RED, DARK
import elites as el
import i18n
from i18n import L, tr

HALF_W, HALF_H = 760, 470          # campo cercado (centro em 0, 0)
BASES = [k for k in ENEMY_TYPES if k != "chefe"]   # todos os monstros do jogo (de todos os biomas)
MINUTES = [0, 2, 4, 6, 8, 10]
DUMMY_COLOR = (196, 170, 120)
COUNT_STEPS = [1, 3, 5, 10, 20, 30, 50]
TIERS = ["normal", "super", "squad", "boss"]


def default_cfg():
    return dict(base="lobo", stage=0, minute=0, count=10, cls=None, aggro=False, spawned=[])


def cfg(app):
    """Configuração da sala (vale enquanto o jogo está aberto)."""
    c = getattr(app, "training_cfg", None)
    if c is None:
        c = app.training_cfg = default_cfg()
    return c


def class_list():
    return [None] + list(CLASSES)   # None = aleatória


def class_name(cid):
    return L("Random", "Aleatória") if cid is None else CLASSES[cid]["name"]


# ---------------------------------------------------------------------------
# Cenário: campo de terra cercado com cerca de madeira, fardos de feno e alvos
# ---------------------------------------------------------------------------
class TrainingScenery:
    def __init__(self, seed=7):
        rnd = random.Random(seed)
        import pixel   # chão em pixel art: terra batida da arena e grama em volta (ladrilhos sem emenda)
        lw = 256 // pixel.PX
        dirt = pixel.banded(pixel.tile_noise(lw, lw, rnd, (4, 8, 16)),
                            pixel.shades((150, 122, 84), (0.78, 0.88, 0.97, 1.06)), 0.1)
        for _ in range(90):   # palha e pedrinhas
            x, y = rnd.randrange(lw), rnd.randrange(lw)
            if rnd.random() < 0.5:
                for k in range(3):
                    dirt.set_at(((x + k) % lw, y), (214, 186, 104))
            else:
                dirt.set_at((x, y), (112, 88, 60))
                dirt.set_at((x, (y - 1) % lw), (176, 150, 112))
        self.tile = pygame.transform.scale(dirt, (lw * pixel.PX, lw * pixel.PX))
        grass = pixel.banded(pixel.tile_noise(lw, lw, rnd, (4, 8, 16)),
                             pixel.shades((70, 112, 58), (0.62, 0.76, 0.9, 1.02)), 0.1)
        for _ in range(160):   # tufos
            x, y = rnd.randrange(lw), rnd.randrange(lw)
            for k in range(3):
                grass.set_at((x % lw, (y - k) % lw), (104, 158, 80))
            grass.set_at(((x + 1) % lw, (y - 1) % lw), (96, 148, 74))
        self.grass = pygame.transform.scale(grass, (lw * pixel.PX, lw * pixel.PX))
        self.bales = [V(-HALF_W + 70, -HALF_H + 60), V(-HALF_W + 120, -HALF_H + 50), V(HALF_W - 80, HALF_H - 70),
                      V(HALF_W - 130, HALF_H - 60), V(HALF_W - 70, -HALF_H + 60), V(-HALF_W + 80, HALF_H - 65)]
        self.marks = [(V(rnd.uniform(-HALF_W + 40, HALF_W - 40), rnd.uniform(-HALF_H + 40, HALF_H - 40)),
                       rnd.randrange(3)) for _ in range(70)]

    # interface igual à dos outros cenários
    def collide(self, u):
        u.pos.x = max(-HALF_W + u.r, min(HALF_W - u.r, u.pos.x))
        u.pos.y = max(-HALF_H + u.r, min(HALF_H - u.r, u.pos.y))

    def clamp(self, e):
        e.pos.x = max(-HALF_W + e.r * 0.6, min(HALF_W - e.r * 0.6, e.pos.x))
        e.pos.y = max(-HALF_H + e.r * 0.6, min(HALF_H - e.r * 0.6, e.pos.y))

    def free_pos(self, pos, margin=30):
        return V(max(-HALF_W + margin, min(HALF_W - margin, pos.x)), max(-HALF_H + margin, min(HALF_H - margin, pos.y)))

    def draw_ground(self, s, cam, Wd, Hd):
        T = self.tile.get_width()
        ox, oy = int(-cam.x % T), int(-cam.y % T)
        for x in range(ox - T, Wd, T):
            for y in range(oy - T, Hd, T):
                s.blit(self.grass, (x, y))
        area = pygame.Rect(-HALF_W - cam.x, -HALF_H - cam.y, HALF_W * 2, HALF_H * 2)
        prev = s.get_clip()
        s.set_clip(area.clip(s.get_rect()))
        for x in range(ox - T, Wd, T):
            for y in range(oy - T, Hd, T):
                s.blit(self.tile, (x, y))
        s.set_clip(prev)
        for p, k in self.marks:   # pegadas / palha no chão
            sp = p - cam
            if -10 < sp.x < Wd + 10 and -10 < sp.y < Hd + 10:
                if k == 0:
                    pygame.draw.line(s, (214, 186, 104), sp, sp + V(7, -2), 2)
        # círculo de giz no meio
        c = V(0, 0) - cam
        pygame.draw.circle(s, (205, 190, 160), c, 120, 2)
        pygame.draw.circle(s, (205, 190, 160), c, 8)

    def draw_trees(self, s, cam, Wd, Hd):
        """Cerca de madeira em volta do campo e fardos de feno nos cantos."""
        wood, dark = (126, 88, 50), (82, 56, 30)
        top, bot = -HALF_H - cam.y, HALF_H - cam.y
        left, right = -HALF_W - cam.x, HALF_W - cam.x
        for y in (top, bot):
            for k in (0, 10):
                pygame.draw.line(s, wood, (left, y - 14 + k), (right, y - 14 + k), 4)
            x0 = left
            while x0 <= right + 1:
                if -20 < x0 < Wd + 20:
                    pygame.draw.rect(s, wood, (x0 - 4, y - 24, 8, 30))
                    pygame.draw.rect(s, dark, (x0 - 4, y - 24, 8, 30), 1)
                x0 += 60
        for x in (left, right):
            pygame.draw.line(s, wood, (x - 3, top), (x - 3, bot), 4)
            pygame.draw.line(s, wood, (x + 5, top), (x + 5, bot), 4)
            y0 = top
            while y0 <= bot + 1:
                if -30 < y0 < Hd + 30:
                    pygame.draw.rect(s, wood, (x - 6, y0 - 12, 12, 18))
                    pygame.draw.rect(s, dark, (x - 6, y0 - 12, 12, 18), 1)
                y0 += 60
        for b in self.bales:
            sp = b - cam
            if -40 < sp.x < Wd + 40 and -40 < sp.y < Hd + 40:
                r = pygame.Rect(sp.x - 24, sp.y - 16, 48, 32)
                pygame.draw.rect(s, (218, 184, 92), r, border_radius=6)
                pygame.draw.rect(s, (168, 134, 58), r, 2, border_radius=6)
                for dx in (-10, 10):
                    pygame.draw.line(s, (120, 88, 44), (sp.x + dx, r.top + 2), (sp.x + dx, r.bottom - 2), 2)


# ---------------------------------------------------------------------------
# Bonecos
# ---------------------------------------------------------------------------
def _finish(run, e, pos):
    e.kind = "dummy"
    e.sprite = "dummy"
    e.color = DUMMY_COLOR
    e.dummy = True
    e.home = V(pos)
    e.walk = e.speed
    e.xp = 0
    e.frags = {}
    run.enemies.append(e)
    return e


def _base_dummy(run, base, pos, tier=None, cid=None):
    from run import Enemy
    ts = 1 + run.scale_time() / 90
    e = Enemy(base, pos, ts * run.hp_mult, (0.5 + 0.5 * ts) * run.dmg_mult, run.res_mult)
    e.base_kind = base   # invocações dos elites usam o monstro base
    e.kind = "dummy"   # o nome do elite usa o tipo ("Novice Dummy")
    if tier:
        el.make_elite(e, cid, tier)
    return _finish(run, e, pos)


def _pick_cls(run, c):
    if c["cls"] is not None:
        return c["cls"]
    pool = run.elite_pool or list(CLASSES)
    return el.pick_class(pool, {u.member.cls for u in run.party})


def _anchor(run, spread):
    """Ponto livre à frente do herói para o novo grupo de bonecos."""
    hero = run.hero
    for _ in range(12):
        a = random.uniform(-0.9, 0.9) + (0 if hero.pos.x < HALF_W - 300 else math.pi)
        p = hero.pos + V(math.cos(a), math.sin(a)) * random.uniform(170, 240)
        p = run.scenery.free_pos(p, spread + 40)
        if all((p - e.pos).length() > spread + 50 for e in run.enemies):
            return p
    return run.scenery.free_pos(hero.pos + V(260, 0), spread + 40)


def spawn(run, entry, record=True):
    """entry: ("normal", base, n) · ("elite", base, cls, tier) · ("squad", base, cls) · ("boss", cls)."""
    c = cfg(run.app)
    kind = entry[0]
    if kind == "normal":
        _, base, n = entry
        cols = max(1, int(math.ceil(math.sqrt(n))))
        gap = ENEMY_TYPES[base]["r"] * 2 + 18
        spread = cols * gap / 2
        a = _anchor(run, spread)
        for i in range(n):
            p = a + V((i % cols - (cols - 1) / 2) * gap, (i // cols - (cols - 1) / 2) * gap)
            _base_dummy(run, base, run.scenery.free_pos(p, 20))
    elif kind == "elite":
        _, base, cls, tier = entry
        a = _anchor(run, 40)
        e = _base_dummy(run, base, a, tier, cls or _pick_cls(run, c))
        run.fx_ring(e.pos, e.r + 40, CLASSES[e.elite]["color"])
    elif kind == "squad":
        _, base, cls = entry
        a = _anchor(run, 90)
        for i in range(el.SQUAD_SIZE):
            ang = i * math.tau / el.SQUAD_SIZE
            _base_dummy(run, base, a + V(math.cos(ang), math.sin(ang)) * 70, "squad", cls or _pick_cls(run, c))
    elif kind == "boss":
        from run import Enemy
        _, cls = entry
        a = _anchor(run, 70)
        b = Enemy("chefe", a, run.hp_mult, run.dmg_mult, run.res_mult)
        b.base_kind = "lobo"
        b.name = "Great Dummy"
        b.stage_index = None
        first = cls or _pick_cls(run, c)
        pool = [x for x in (run.elite_pool or list(CLASSES)) if x != first] or [first]
        el.make_boss(b, [first, random.choice(pool)])
        _finish(run, b, a)
        run.boss = b
    if record:
        c["spawned"].append(entry)


def clear(run, forget=True):
    run.enemies = [e for e in run.enemies if not getattr(e, "dummy", False)]
    run.hostile_shots, run.hostile_zones = [], []
    run.boss = None
    if forget:
        cfg(run.app)["spawned"] = []


def respawn(run):
    """Recria os bonecos guardados (ao entrar na sala ou ao mudar a força)."""
    clear(run, forget=False)
    for entry in list(cfg(run.app)["spawned"]):
        spawn(run, entry, record=False)


def setup(run):
    """Chamado pelo Run ao criar a sala."""
    c = cfg(run.app)
    run.meter_t0 = 0.0
    respawn(run)   # vazio ao entrar pelo acampamento; ao voltar da party / recomeçar build, os mesmos bonecos


def set_stage(run, idx):
    """Muda a fase usada na força dos bonecos (ajusta os multiplicadores do Run)."""
    old = STAGES[run.stage["index"]]
    new = STAGES[idx]
    run.hp_mult *= new["hp"] / old["hp"]
    run.dmg_mult *= new["dmg"] / old["dmg"]
    run.res_mult *= new["res"] / old["res"]
    run.stage = dict(new, name="Training Room", training=True)
    cfg(run.app)["stage"] = idx


def reset_meter(run):
    run.dmg_log = {u: {} for u in run.party}
    run.taken_log = {u: {} for u in run.party}
    run.heal_log = {u: {} for u in run.party}
    run.cc_log = {u: {} for u in run.party}
    run.meter_t0 = run.time


def dummy_count(run):
    return sum(1 for e in run.enemies if getattr(e, "dummy", False))


def update_dummy(run, e, dt):
    """Bonecos parados: voltam devagar para o lugar se forem empurrados (sem tremer quando já estão lá)."""
    d = (e.home - e.pos).length()
    e.speed = min(e.walk, d * 3) if d > 2 else 0
    e.update(dt, e.home)
    e.speed = e.walk


# ---------------------------------------------------------------------------
# Painel
# ---------------------------------------------------------------------------
PANEL = pygame.Rect(W / 2 - 430, 40, 860, 640)


def toggle_rect():
    """Botão do painel na tela da run (para o mouse e o toque)."""
    return pygame.Rect(W - 258, 100, 170, 34)


def _btn(rect, label, action, style="normal"):
    return (pygame.Rect(rect), label, action, style)


def layout(run):
    """Lista de (rect, rótulo, ação, estilo). A mesma lista serve para desenhar e para os cliques."""
    c = cfg(run.app)
    x0, y = PANEL.x + 30, PANEL.y + 112
    out = []
    # força
    out += [_btn((x0 + 210, y, 34, 30), "<", ("base", -1)), _btn((x0 + 420, y, 34, 30), ">", ("base", 1))]
    y += 40
    out += [_btn((x0 + 210, y, 34, 30), "<", ("stage", -1)), _btn((x0 + 420, y, 34, 30), ">", ("stage", 1)),
            _btn((x0 + 620, y, 34, 30), "<", ("minute", -1)), _btn((x0 + 750, y, 34, 30), ">", ("minute", 1))]
    y += 78
    # bonecos comuns
    out += [_btn((x0 + 210, y, 34, 30), "-", ("count", -1)), _btn((x0 + 330, y, 34, 30), "+", ("count", 1)),
            _btn((x0 + 380, y, 220, 30), L("Add normal dummies", "Adicionar bonecos"), ("add", "normal"), "good")]
    y += 40
    out += [_btn((x0 + 210, y, 34, 30), "<", ("cls", -1)), _btn((x0 + 470, y, 34, 30), ">", ("cls", 1))]
    y += 40
    bw = 190
    for i, (t, lab) in enumerate((("elite", L("Elite", "Elite")), ("super", L("Super Elite", "Super Elite")),
                                  ("squad", L("Elite Squad", "Esquadrão de Elite")), ("boss", L("Boss", "Chefão")))):
        out.append(_btn((x0 + i * (bw + 10), y, bw, 32), "+ " + lab, ("add", t), "good"))
    y += 64
    out.append(_btn((x0, y, 540, 32), "", ("aggro",), "check"))
    out.append(_btn((x0 + 590, y, 210, 32), L("Remove all dummies", "Remover todos"), ("clear",), "bad"))
    y += 68
    bw = 190
    for i, (lab, act) in enumerate(((L("Reset meter", "Zerar medidor"), ("meter",)),
                                    (L("+1 level-up", "+1 level up"), ("level", 1)),
                                    (L("+10 level-ups", "+10 level ups"), ("level", 10)),
                                    (L("Restart build", "Recomeçar build"), ("restart",)))):
        out.append(_btn((x0 + i * (bw + 10), y, bw, 32), lab, act))
    yb = PANEL.bottom - 74
    out += [_btn((x0, yb, 250, 38), L("Manage party", "Gerenciar party"), ("party",)),
            _btn((x0 + 270, yb, 250, 38), L("Back to camp", "Voltar ao acampamento"), ("exit",), "bad"),
            _btn((x0 + 540, yb, 250, 38), L("Resume  [T]", "Continuar  [T]"), ("close",), "good")]
    return out


def _cycle(lst, cur, d):
    i = lst.index(cur) if cur in lst else 0
    return lst[(i + d) % len(lst)]


def do_action(run, act):
    """Executa uma ação do painel. Retorna 'menu' (sair), 'party' ou None."""
    c = cfg(run.app)
    k = act[0]
    if k == "base":
        c["base"] = _cycle(BASES, c["base"], act[1])
    elif k == "stage":
        set_stage(run, (c["stage"] + act[1]) % len(STAGES))
        respawn(run)
    elif k == "minute":
        c["minute"] = _cycle(MINUTES, c["minute"], act[1])
        respawn(run)
    elif k == "count":
        c["count"] = _cycle(COUNT_STEPS, c["count"], act[1]) if not (
            (act[1] < 0 and c["count"] == COUNT_STEPS[0]) or (act[1] > 0 and c["count"] == COUNT_STEPS[-1])) \
            else c["count"]
    elif k == "cls":
        c["cls"] = _cycle(class_list(), c["cls"], act[1])
    elif k == "add":
        t = act[1]
        if t == "normal":
            spawn(run, ("normal", c["base"], c["count"]))
        elif t in ("elite", "super"):
            spawn(run, ("elite", c["base"], c["cls"], "normal" if t == "elite" else "super"))
        elif t == "squad":
            spawn(run, ("squad", c["base"], c["cls"]))
        else:
            spawn(run, ("boss", c["cls"]))
    elif k == "aggro":
        c["aggro"] = not c["aggro"]
        if not c["aggro"]:
            run.hostile_shots, run.hostile_zones = [], []
            for e in run.enemies:
                if getattr(e, "dummy", False):
                    e.home = V(e.pos)
    elif k == "clear":
        clear(run)
    elif k == "meter":
        reset_meter(run)
    elif k == "level":
        run.pending_lv += act[1]
        run.state = "play"
    elif k == "restart":
        return "restart"
    elif k == "party":
        return "party"
    elif k == "exit":
        return "menu"
    elif k == "close":
        run.state = "play"
    return None


def handle_event(run, ev):
    if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_t):
        run.state = "play"
        return None
    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
        if not PANEL.collidepoint(ev.pos):
            run.state = "play"
            return None
        for r, _lab, act, _st in layout(run):
            if r.collidepoint(ev.pos):
                return do_action(run, act)
    return None


def draw_panel(run):
    s = run.screen
    c = cfg(run.app)
    s.blit(run.overlay, (0, 0))
    pygame.draw.rect(s, (24, 24, 34), PANEL, border_radius=14)
    pygame.draw.rect(s, (210, 170, 100), PANEL, 2, border_radius=14)
    x0 = PANEL.x + 30
    run.text(L("TRAINING ROOM", "SALA DE TREINO"), "big", (230, 200, 120), (PANEL.centerx, PANEL.y + 34), "center")
    run.text(L("Dummies never die: test formations and builds and check DPS / HPS in the meter (bottom right).",
               "Os bonecos nunca morrem: teste formações e builds e veja o DPS / HPS no medidor (canto inferior direito)."),
             "small", GREY, (PANEL.centerx, PANEL.y + 68), "center")
    y = PANEL.y + 112
    lab = (240, 240, 245)
    sec = (230, 200, 120)
    run.text(L("Dummy strength", "Força dos bonecos"), "small", sec, (x0, y - 22))
    t = ENEMY_TYPES[c["base"]]
    run.text(L("Base monster", "Monstro base"), "normal", lab, (x0, y + 4))
    run.text(tr(ENEMY_NAMES[c["base"]]), "normal", YELLOW, (x0 + 337, y + 15), "center")
    run.text(L(f"HP {t['hp']} · armor {t['armor']} · m.def {t['mres']} · dmg {t['dmg']}",
               f"Vida {t['hp']} · armadura {t['armor']} · def.mág {t['mres']} · dano {t['dmg']}"),
             "small", GREY, (x0 + 470, y + 8))
    y += 40
    run.text(L("Stage", "Fase"), "normal", lab, (x0, y + 4))
    run.text(tr(STAGES[c["stage"]]["name"]), "normal", YELLOW, (x0 + 337, y + 15), "center")
    run.text(L("Run time", "Tempo da run"), "normal", lab, (x0 + 470, y + 4))
    run.text(f"{c['minute']}:00", "normal", YELLOW, (x0 + 719, y + 15), "center")
    y += 36
    run.text(L("Applies to every dummy; the global level (trophies) and the party size also count, like in a run.",
               "Vale para todos os bonecos; o nível global (troféus) e o tamanho da party também contam, como numa run."),
             "small", GREY, (x0, y))
    y += 42
    run.text(L("Add dummies", "Adicionar bonecos"), "small", sec, (x0, y - 22))
    run.text(L("Normal dummies", "Bonecos comuns"), "normal", lab, (x0, y + 4))
    run.text(str(c["count"]), "normal", YELLOW, (x0 + 287, y + 15), "center")
    run.text(L(f"In the field: {dummy_count(run)}", f"No campo: {dummy_count(run)}"), "small", GREY,
             (x0 + 620, y + 8))
    y += 40
    run.text(L("Elite class", "Classe do elite"), "normal", lab, (x0, y + 4))
    cid = c["cls"]
    if cid is not None:
        import skill_icons as si
        ic = si.class_icon(cid, 24)
        nm = class_name(cid)
        wdt = run.fonts["normal"].size(nm)[0] + 30
        s.blit(ic, (x0 + 357 - wdt / 2, y + 3))
        run.text(nm, "normal", CLASSES[cid]["color"], (x0 + 357 - wdt / 2 + 30, y + 4))
    else:
        run.text(class_name(None), "normal", YELLOW, (x0 + 357, y + 15), "center")
    run.text(L("Boss: this class + 1 random", "Chefão: esta classe + 1 aleatória"), "small", GREY, (x0 + 520, y + 8))
    mouse = run.app.mouse_pos()
    lay = layout(run)
    for r, label, act, style in lay:
        hot = r.collidepoint(mouse)
        if style == "check":
            on = c["aggro"]
            box = pygame.Rect(r.x + 8, r.centery - 9, 18, 18)
            pygame.draw.rect(s, (55, 55, 75) if hot else DARK, r, border_radius=8)
            pygame.draw.rect(s, RED if on else GREY, r, 2 if on else 1, border_radius=8)
            pygame.draw.rect(s, WHITE, box, 2, border_radius=3)
            if on:
                pygame.draw.lines(s, RED, False, [(box.x + 3, box.centery), (box.x + 8, box.bottom - 4),
                                                  (box.right - 3, box.y + 3)], 3)
            run.text(L("Dummies attack (they chase, hit and use skills)",
                       "Os bonecos atacam (perseguem, batem e usam habilidades)"),
                     "small", WHITE if on else GREY, (box.right + 10, r.centery), "midleft")
            continue
        col = {"good": GREEN, "bad": (230, 110, 100)}.get(style, (200, 200, 215))
        pygame.draw.rect(s, (60, 60, 85) if hot else (36, 36, 50), r, border_radius=8)
        pygame.draw.rect(s, col, r, 2 if hot else 1, border_radius=8)
        run.text(label, "small" if r.h <= 32 else "normal", col if style != "normal" else WHITE, r.center, "center")
    row_y = {act[0]: r.y for r, _l, act, _s in lay}
    run.text(L("Behaviour", "Comportamento"), "small", sec, (x0, row_y["aggro"] - 22))
    run.text(L("Meter and build", "Medidor e build"), "small", sec, (x0, row_y["meter"] - 22))
    run.text(L("T or ESC closes the panel  ·  click outside it to resume",
               "T ou ESC fecha o painel  ·  clique fora dele para continuar"), "small", GREY,
             (PANEL.centerx, PANEL.bottom - 8), "midbottom")


def draw_toggle(run):
    """Botão no canto (abre o painel) e a contagem de bonecos."""
    s = run.screen
    r = toggle_rect()
    hot = r.collidepoint(run.app.mouse_pos())
    pygame.draw.rect(s, (60, 60, 85) if hot else (30, 30, 42), r, border_radius=8)
    pygame.draw.rect(s, (230, 200, 120), r, 2, border_radius=8)
    run.text(L("Training  [T]", "Treino  [T]"), "small", (230, 200, 120), r.center, "center")
    if not dummy_count(run):   # sala vazia: dica de como colocar bonecos
        box = pygame.Surface((720, 38), pygame.SRCALPHA)
        box.fill((15, 15, 22, 190))
        s.blit(box, (W / 2 - 360, H - 169))
        run.text(L("The field is empty: press T (or the Training button) to add dummies",
                   "O campo está vazio: aperte T (ou o botão Treino) para colocar bonecos"), "normal",
                 (230, 200, 120), (W / 2, H - 150), "center")
