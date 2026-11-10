"""Telas de menu: principal, Party Setup, árvore de classes, renomear e configurações."""
import math

import pygame

import pixel
from pygame.math import Vector2 as V

from data import role_of, role_name
from data import STAGES, STAGE_TIME, GOLD_STAGE_BASE, ENEMY_NAMES, PARTY_SCALING, ENEMY_FROM_STAGE
from data import BIOMES, ENDLESS_BASE, is_endless, endless_biome, biome_of
from data import (DMG_PER_ATTR, ARMOR_PER_STR, DODGE_PER_AGI, MRES_PER_INT, HP_PER_VIT, MAX_DODGE, CRIT_PER_AGI,
                  CRITDMG_PER_STR, CDR_PER_INT, BASE_CRIT_DMG, MAX_CDR, GENERAL_LEVEL_STAT, REGEN5_PER_VIT,
                  MAX_CRIT, soft_marks)
from data import (W, H, BG, GRID, WHITE, GREY, DARK, PANEL, RED, GREEN, YELLOW, CLASSES, ENEMY_TYPES,
                  DIFFICULTIES, ATTR_NAMES, BASIC_ORDER, ADVANCED, ELEMENTS, element_color)
import progression as prog
from icons import draw_class_icon
import skill_icons as si
from faq import FAQ, faq_for
import i18n
from i18n import tr
L = i18n.L
from version import VERSION, STAGE as VERSION_STAGE
import equipment as eq
import accessories as accm
import dungeons as dgm
import rift
import elites as el
from tags import class_tags, tag_list_text, tag_name, TAG_ORDER, status_chances
from class_passives import effect_text, effects_text
from enemy_sprites import draw_enemy
from roster import slot_summary as roster_slot_summary
from roster import (MAX_ACTIVE, MAX_MEMBERS, MAX_LEVEL, MAX_CLASS_LEVEL, MASTERY_LEVEL, exp_to_next, class_exp_to_next, save_settings)
from run import Unit

STAT_LABELS = (("str", "STR", ""), ("agi", "AGI", ""), ("int", "INT", ""), ("vit", "VIT", ""), ("hp", "HP", ""),
               ("crit", "Crit", "%"), ("critdmg", "CDmg", "%"), ("cdr", "CD", "%"), ("armor", "Arm", ""),
               ("mres", "MDef", ""), ("dodge", "Ddg", "%"), ("regen5", "Reg", ""))


def fmt_num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if not float(v).is_integer() else f"{int(v)}"


def bonus_text(d, sep="  "):
    """Texto compacto dos bônus de status (ex.: FOR+3  Crit+0.6%)."""
    return sep.join(f"{lab}+{fmt_num(d[k])}{suf}" for k, lab, suf in STAT_LABELS if d.get(k))


TIER_NAMES = {0: "Starting class", 1: "Basic class", 2: "Advanced class", 3: "Evolved class", 4: "Ultimate class"}


def draw_infinity(s, center, w, col, thick=3):
    """Símbolo de infinito desenhado (a fonte padrão não tem o caractere)."""
    cx, cy = center
    pts = []
    for i in range(41):
        t = i / 40 * math.tau
        d = 1 + math.sin(t) ** 2
        pts.append((cx + w / 2 * math.cos(t) / d, cy + w / 2 * math.sin(t) * math.cos(t) / d))
    pygame.draw.lines(s, col, True, pts, thick)


def draw_star(s, center, r, col):
    """Estrelinha desenhada (indica classe masterizada)."""
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 36 - 90)
        pts.append((center[0] + math.cos(a) * rr, center[1] + math.sin(a) * rr))
    pygame.draw.polygon(s, col, pts)
ROW_H = 58
LIST_ROWS = 8



def softcap_line(raw, cap):
    """Linha dos detalhes de status: total bruto e os dois softcaps (retorno decrescente)."""
    a, b = soft_marks(cap)
    col = (150, 220, 150) if raw <= a else (240, 200, 90) if raw <= cap else (240, 120, 90)
    return (f"Raw total {raw:.1f}%  ·  softcaps at {a:.0f}% (bonus worth 1/2) and {b:.0f}% (worth 1/5)  ·  "
            f"max {cap:.0f}%", col)

class MenusMixin:
    MAIN_ITEMS = ["Continue", "New Save", "Load Save", "Configurations", "Quit"]
    CONFIG_ITEMS = ["fullscreen", "difficulty", "damage_numbers", "show_fps", "fps_limit", "language", "back"]

    # ================================================================
    # utilitários de desenho
    # ================================================================
    def text(self, txt, font, color, pos, anchor="topleft"):
        surf = self.fonts[font].render(tr(str(txt)), True, color)
        self.screen.blit(surf, surf.get_rect(**{anchor: pos}))

    def button(self, rect, label, hot, color=WHITE, value="", enabled=True):
        s = self.screen
        pygame.draw.rect(s, (60, 60, 85) if hot and enabled else DARK, rect, border_radius=10)
        pygame.draw.rect(s, YELLOW if hot and enabled else GREY, rect, 3 if hot and enabled else 1, border_radius=10)
        col = color if enabled else (80, 80, 92)
        if value:
            self.text(label, "normal", col, (rect.x + 22, rect.centery), "midleft")
            self.text(value, "normal", YELLOW if hot else WHITE, (rect.right - 22, rect.centery), "midright")
        else:
            self.text(label, "normal", col, rect.center, "center")

    def bar(self, x, y, w, h, frac, color):
        pygame.draw.rect(self.screen, DARK, (x, y, w, h), border_radius=3)
        pygame.draw.rect(self.screen, color, (x, y, int(w * max(0.0, min(1.0, frac))), h), border_radius=3)

    def menu_bg(self, monsters=False):
        """Fundo das telas: grade simples (os submenus do acampamento não têm monstros)."""
        s = self.screen
        s.fill(BG)
        t = self.clock_time
        off = V(t * 25, t * 12) if monsters else V(0, 0)
        for x in range(int(-off.x % 64), W, 64):
            pygame.draw.line(s, GRID, (x, 0), (x, H))
        for y in range(int(-off.y % 64), H, 64):
            pygame.draw.line(s, GRID, (0, y), (W, y))
        s.blit(pixel.vignette((W, H), 120), (0, 0))   # bordas escurecidas (clima gótico)
        if not monsters:
            return
        for i, kind in enumerate(["morcego", "lobo", "javali"] * 6):
            et = ENEMY_TYPES[kind]
            a = t * (0.15 + 0.03 * (i % 4)) + i * 1.7
            rad = 260 + (i * 37) % 200
            pos = V(W / 2 + math.cos(a) * rad * 1.5, H / 2 + math.sin(a) * rad * 0.8)
            draw_enemy(s, kind, pos, et["r"], tuple(c // 2 for c in et["color"]), math.cos(a) < 0,
                       int(t * 6 + i))

    def draw_gold(self, topright):
        """Moeda + quantidade de gold, alinhado pelo canto superior direito."""
        surf = self.fonts["normal"].render(f"{self.roster.gold} gold", True, YELLOW)
        r = surf.get_rect(topright=topright)
        self.screen.blit(surf, r)
        c = (r.x - 14, r.centery)
        pygame.draw.circle(self.screen, (230, 180, 40), c, 9)
        pygame.draw.circle(self.screen, (255, 230, 120), c, 9, 2)

    def fit(self, txt, font, width):
        """Texto já traduzido e cortado com "…" para caber na largura."""
        t = tr(str(txt))
        f = self.fonts[font]
        if f.size(t)[0] <= width:
            return t
        while len(t) > 2 and f.size(t + "…")[0] > width:
            t = t[:-1]
        return t.rstrip() + "…"

    def wrap(self, txt, font, width):
        """Quebra o texto na largura. '\n' força nova linha; itens '• ' continuam recuados na linha seguinte."""
        f = self.fonts[font]
        lines = []
        for para in tr(txt).split("\n"):
            indent = "    " if para.startswith(("• ", "1. ", "2. ", "3. ", "4. ", "5. ")) else ""
            cur = ""
            for w in para.split():
                test = (cur + " " + w).strip() if not cur.startswith(" ") else cur + " " + w
                if not cur or f.size(test)[0] <= width:
                    cur = test
                else:
                    lines.append(cur)
                    cur = indent + w
            lines.append(cur)
        return lines

    def skill_icon(self, sp, kind, size, center, dim=False, hover=None):
        """Desenha o ícone e registra a área de mouseover (hover = retângulo da linha; padrão = o próprio ícone)."""
        ic = si.icon_for(sp, kind, size)
        if dim:
            ic = ic.copy()
            ic.set_alpha(90)
        rect = ic.get_rect(center=center)
        self.screen.blit(ic, rect)
        self.add_skill_hover(hover or rect, sp, kind)

    def add_skill_hover(self, rect, sp, kind):
        if not hasattr(self, "skill_hovers"):
            self.skill_hovers = []
        self.skill_hovers.append((pygame.Rect(rect), sp, kind, getattr(self, "tip_member", None)))

    def draw_skill_hover(self):
        """Tooltip da habilidade sob o mouse (qualquer tela de menu); a última registrada fica por cima."""
        hovers, self.skill_hovers = getattr(self, "skill_hovers", []), []
        self.tip_member = None   # cada tela informa de novo, a cada quadro, de quem são as habilidades
        mp = self.mouse_pos()
        for rect, sp, kind, m in reversed(hovers):
            if rect.collidepoint(mp):
                self.tip_member_now = m
                self.draw_tooltip(self.skill_tip_lines(sp, kind), mp)
                self.tip_member_now = None
                return

    def skill_real_damage(self, sp):
        """Dano calculado da habilidade com os status do personagem dono do tooltip (None se não houver)."""
        m = getattr(self, "tip_member_now", None) or getattr(self, "tip_member", None)
        if m is None:
            return None
        try:
            u = Unit(m, 0)
            return sp.get("dmg", 0) / 100 * u.char_damage() * u.power(sp.get("dmgtype", "mag"))
        except Exception:
            return None

    @staticmethod
    def _fmt(v):
        return f"{v:g}" if isinstance(v, (int, float)) else str(v)

    def skill_tip_lines(self, sp, kind):
        """Linhas [(texto, cor)] com os valores base da habilidade/passiva (sem bônus do personagem)."""
        f = self._fmt
        if kind == "passive":
            effects = sp.get("effects") or {sp.get("effect"): sp.get("value", 0)}
            cap = sp.get("capstone")
            lines = [(sp["name"], YELLOW),
                     ("Capstone · only in the 5th class slot (own class) or the 5th mastery slot (another class)"
                      if cap else "Passive · always active while equipped", (250, 210, 70) if cap else (150, 190, 255))]
            auto = effects_text(effects)
            if sp.get("desc") and sp["desc"] != auto:
                lines.append((sp["desc"], GREY))
            for k, v in effects.items():
                lines.append((effect_text(k, v, i18n.LANG), WHITE))
            if sp.get("unlock"):
                lines.append((f"Unlocks at class Lv {sp['unlock']}", GREEN))
            return lines
        k = sp["kind"]
        head = [prog.ARCH_NAME.get(k, k)]
        if k not in ("heal", "buff"):
            head.append("Physical" if sp.get("dmgtype") == "phys" else "Magical")
        if sp.get("cycle"):
            head.append(" / ".join(ELEMENTS[e]["name"] for e in sp["cycle"]))
        elif sp.get("element") in ELEMENTS:
            head.append(ELEMENTS[sp["element"]]["name"])
        if sp.get("target") in prog.TARGET_NAME:
            head.append("Target: " + prog.TARGET_NAME[sp["target"]])
        lines = [(sp["name"], YELLOW), (" · ".join(head), (150, 190, 255))]
        if sp.get("tags"):
            lines.append((f"Tags: {tag_list_text(sp['tags'], i18n.LANG)}", (120, 220, 200)))
        if sp.get("desc"):
            lines.append((sp["desc"], GREY))
        st = []
        if sp.get("bleed"):
            st.append(("Bleed", f"{sp['bleed'] * 100:.0f}% of the hit per second for 3s"))
        chances = status_chances(sp, i18n.LANG)
        if chances:
            st.append((i18n.L("Status chance per hit", "Chance de status por golpe"), ", ".join(chances)))
        if k == "heal":
            st.append(("Healing", f(sp.get("amount", 8))))
        elif k != "buff":
            lbl = {"cloud": "Damage per second", "aura": "Damage per tick", "orbit": "Damage per hit"}.get(k, "Damage")
            real = self.skill_real_damage(sp)
            st.append((lbl, f"{f(sp.get('dmg', 0))}%" + (f" ({real:.0f})" if real is not None else "")))
            st.append(("Scales with", i18n.L("Character damage (10 + main attribute of the current class)",
                                             "Dano do personagem (10 + atributo principal da classe atual)")))
        if k == "aura":
            st.append(("Tick interval", f"{f(sp.get('cd', 1.0))}s"))
        elif k != "orbit":
            st.append(("Cooldown", f"{f(sp.get('cd', 1.0))}s"))
        if k in ("shot", "strike", "orbit", "summon") or sp.get("count"):
            st.append(("Count", f(sp.get("count", 2 if k == "orbit" else 1))))
        if k == "thrust" and sp.get("length"):
            st.append(("Range", f(sp["length"])))
        elif sp.get("radius"):
            st.append(("Area (radius)", f(sp["radius"])))
        if k in ("slash", "cone") and sp.get("arc"):
            st.append(("Arc", f"{f(sp['arc'])}°"))
        elif k == "thrust" and sp.get("width"):
            st.append(("Width", f(sp["width"])))
        elif k == "shot":
            if sp.get("spread"):
                st.append(("Spread", f"{f(sp['spread'])}°"))
            st.append(("Pierce", f(sp.get("pierce", 1))))
        if sp.get("speed") and k in ("shot", "summon", "orbit"):
            st.append(("Speed", f(sp["speed"])))
        if k in ("summon", "shot") and sp.get("life"):
            st.append(("Duration" if k == "summon" else "Lifetime", f"{f(sp['life'])}s"))
        elif sp.get("duration"):
            st.append(("Duration", f"{f(sp['duration'])}s"))
        if sp.get("slow"):
            st.append(("Slow", f"{(1 - sp['slow'][0]) * 100:.0f}% for {f(sp['slow'][1])}s"))
        if sp.get("taunt"):
            st.append((i18n.L("Taunt", "Provocar"), i18n.L(f"{f(sp['taunt'])}s - enemies hit attack this character",
                                                          f"{f(sp['taunt'])}s - os inimigos atingidos atacam este personagem")))
        if sp.get("weaken"):
            st.append((i18n.L("Weaken", "Enfraquecer"), i18n.L(f"+{f(sp['weaken'])}% damage taken for 4s",
                                                              f"+{f(sp['weaken'])}% de dano recebido por 4s")))
        for key in ("stun", "pull", "explode", "homing", "delay"):
            if sp.get(key):
                st.append((prog.SPECIAL_NAME[key].split(" (")[0], f(sp[key]) + ("s" if key in ("stun", "delay") else "")))
        for key, v in sp.get("effects", {}).items():
            nm = prog.SPECIAL_NAME.get("b_" + key, key).replace("Buff: ", "Buff ").replace(" (%)", "")
            st.append((nm, f"+{v * 100:.0f}%"))
        lines += [(f"{a}:  {b}", WHITE) for a, b in st]
        if sp.get("unlock"):
            lines.append((f"Unlocks at class Lv {sp['unlock']}", GREEN))
        if k not in ("heal", "buff") and self.skill_real_damage(sp) is not None:
            lines.append((i18n.L("(n) = damage with this character's current stats; run level raises it",
                                 "(n) = dano com os status atuais do personagem; o nível na partida aumenta"),
                          (110, 110, 125)))
        else:
            lines.append(("Base values - attributes, items and run level raise them", (110, 110, 125)))
        return lines

    def draw_tooltip(self, lines, pos):
        """Caixa de dica perto do mouse. lines = [(texto, cor)]; a 1ª linha é o título."""
        font_w = 380
        rendered = []
        for i, (txt, col) in enumerate(lines):
            f = "normal" if i == 0 else "small"
            for ln in (self.wrap(txt, f, font_w) or [""]):
                rendered.append(self.fonts[f].render(ln, True, col))
        w = max(s.get_width() for s in rendered) + 24
        h = sum(s.get_height() + 4 for s in rendered) + 18
        x = min(pos[0] + 16, W - w - 8)
        y = min(pos[1] + 16, H - h - 8)
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (22, 22, 30), box, border_radius=8)
        pygame.draw.rect(self.screen, YELLOW, box, 1, border_radius=8)
        yy = y + 9
        for s in rendered:
            self.screen.blit(s, (x + 12, yy))
            yy += s.get_height() + 4

    def toast(self, msg):
        self.toast_msg = msg
        self.toast_t = 2.5

    def draw_toast(self):
        if self.toast_t > 0 and self.toast_msg:
            surf = self.fonts["normal"].render(tr(self.toast_msg), True, WHITE)
            r = surf.get_rect(center=(W / 2, H - 70)).inflate(30, 16)
            pygame.draw.rect(self.screen, (90, 40, 40), r, border_radius=8)
            self.screen.blit(surf, surf.get_rect(center=r.center))

    # ================================================================
    # menu principal
    # ================================================================
    def main_rects(self):
        return [pygame.Rect(W // 2 - 170, 300 + i * 62, 340, 50) for i in range(len(self.MAIN_ITEMS))]

    # ---- fundo da tela principal: fases em ordem aleatória e gatinhos de todas as classes passeando ----
    MAIN_BG_TIME = 9.0

    def main_bg_init(self):
        import random as _r
        from scenery import Scenery
        self._mbg_scen = {}
        self._mbg_order = []
        self._mbg_t = 0.0
        self._mbg_stage = None
        self._mbg_scenery_cls = Scenery
        import cats
        rnd = _r.Random()
        mobs = []
        for cid in CLASSES:   # 1 ou 2 gatos de cada classe, cada um com aparência aleatória
            for _ in range(rnd.randint(1, 2)):
                mobs.append(dict(cid=cid, look=cats.random_look(rnd), r=rnd.choice((15, 16, 17, 18)),
                                 speed=rnd.uniform(0.08, 0.2) * rnd.choice((1, -1)),
                                 phase=rnd.uniform(0, math.tau), rad=rnd.uniform(200, 540),
                                 hop=rnd.uniform(0, math.tau)))
        self._mbg_mobs = mobs

    def main_bg_next(self):
        import random as _r
        if not self._mbg_order:
            self._mbg_order = list(range(len(STAGES)))
            _r.shuffle(self._mbg_order)
            if len(self._mbg_order) > 1 and self._mbg_order[0] == self._mbg_stage:
                self._mbg_order.append(self._mbg_order.pop(0))
        self._mbg_stage = self._mbg_order.pop(0)
        if self._mbg_stage not in self._mbg_scen:
            self._mbg_scen[self._mbg_stage] = self._mbg_scenery_cls(self._mbg_stage)
        self._mbg_t = 0.0

    def draw_main_bg(self):
        s = self.screen
        if not hasattr(self, "_mbg_mobs"):
            self.main_bg_init()
        if self._mbg_stage is None or self._mbg_t >= self.MAIN_BG_TIME:
            self.main_bg_next()
        dt = min(0.05, max(0.0, self.clock_time - getattr(self, "_mbg_last", self.clock_time)))
        self._mbg_last = self.clock_time
        self._mbg_t += dt
        scen = self._mbg_scen[self._mbg_stage]
        t = self.clock_time
        cam = V(1500 + t * 22, 900 + t * 10)   # câmera passeando devagar pela floresta
        scen.draw_ground(s, cam, W, H)
        scen.draw_trees(s, cam, W, H)
        import cats
        mobs = []
        for mb in self._mbg_mobs:
            a = t * mb["speed"] + mb["phase"]
            pos = V(W / 2 + math.cos(a) * mb["rad"] * 1.35, H / 2 + math.sin(a) * mb["rad"] * 0.75)
            vel = V(-math.sin(a) * mb["rad"] * 1.35, math.cos(a) * mb["rad"] * 0.75) * mb["speed"]   # direção do passo
            mobs.append((pos, vel, mb))
        for pos, vel, mb in sorted(mobs, key=lambda x: x[0].y):   # os de baixo na frente
            wf = int(t * (4 + vel.length() / 12) + mb["hop"]) % cats.WALK_FRAMES   # passos no ritmo da velocidade
            cats.draw_cat(s, mb["cid"], (pos.x, pos.y), mb["r"], (vel.x, vel.y * 0.3), mb["look"], walk=wf)
        pixel.pixelate_world(s)
        shade = pygame.Surface((W, H), pygame.SRCALPHA)   # escurece para o texto ficar legível
        fade = min(1.0, self._mbg_t / 0.8, (self.MAIN_BG_TIME - self._mbg_t) / 0.8)
        shade.fill((8, 8, 14, int(85 + 170 * (1 - max(0.0, fade)))))
        s.blit(shade, (0, 0))
        self.text(STAGES[self._mbg_stage]["name"], "small", (190, 190, 200), (14, H - 12), "bottomleft")

    def draw_main(self):
        self.draw_main_bg()
        bob = math.sin(self.clock_time * 2) * 6
        title = self.fonts["title"].render("CAT FANTASY SURVIVORS", True, YELLOW)
        trect = title.get_rect(center=(W / 2, 170 + bob))
        self.screen.blit(title, trect)
        # tag da fase (Alpha) presa ao canto do título
        tag = self.fonts["small"].render(tr(VERSION_STAGE.upper()), True, (30, 20, 10))
        box = tag.get_rect().inflate(16, 8)
        box.bottomleft = (trect.right - 34, trect.top + 8)
        pygame.draw.rect(self.screen, (230, 110, 60), box, border_radius=6)
        pygame.draw.rect(self.screen, (255, 200, 150), box, 1, border_radius=6)
        self.screen.blit(tag, tag.get_rect(center=box.center))
        self.text("survive the horde", "normal", GREY, (W / 2, 240), "center")
        for i, (r, label) in enumerate(zip(self.main_rects(), self.MAIN_ITEMS)):
            self.button(r, label, i == self.sel, RED if label == "Quit" else WHITE)
            if label == "Continue":   # qual save vai continuar
                m = self.roster.members[0]
                self.text(i18n.L(f"Save {getattr(self.roster, 'slot', 1)}: {m.name} · {tr(CLASSES[m.cls]['name'])} Lv {m.level}",
                                 f"Save {getattr(self.roster, 'slot', 1)}: {m.name} · {tr(CLASSES[m.cls]['name'])} Nv {m.level}"),
                          "small", GREY, (r.right + 14, r.centery), "midleft")
        self.text(f"ver. {VERSION} ({VERSION_STAGE})", "small", (140, 140, 160), (W - 14, H - 12), "bottomright")
        fb = self.faq_button_rect()   # botão da Wiki, isolado no canto
        self.button(fb, "Wiki", fb.collidepoint(self.mouse_pos()), (150, 200, 255))

    def main_activate(self, i):
        choice = self.MAIN_ITEMS[i]
        if choice == "Continue":   # entra no acampamento (HUB) com o último save usado
            self.hub.reset()
            self.go("hub")
        elif choice in ("New Save", "Load Save"):
            self.saves_mode = "new" if choice == "New Save" else "load"
            self.saves_sel = getattr(self.roster, 'slot', 1) - 1
            self.saves_confirm = None
            self.go("saves")
        elif choice == "Configurations":
            self.go("config")
        else:
            return False
        return True

    def main_event(self, ev):
        rects = self.main_rects()
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(rects)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(rects)
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.main_activate(self.sel)
            elif ev.key == pygame.K_ESCAPE:
                return False
        elif ev.type == pygame.MOUSEMOTION:
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos):
                    self.sel = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.faq_button_rect().collidepoint(ev.pos):
                self.open_faq()
                return True
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos):
                    return self.main_activate(i)
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_F1, pygame.K_h):
            self.open_faq()
        return True

    # ================================================================
    # New player experience: pop-ups de explicação (tips.py) e o botão "?" de cada tela
    # ================================================================
    STATE_TIPS = {"stages": "stages", "party": "party", "classes": "classes", "loadout": "loadout",
                  "jeweler": "jeweler", "altar": "altar", "mastery": "mastery", "dungeons": "dungeons",
                  "greed": "greed", "craft": "craft",
                  "levels": "classes"}

    def state_tip(self, help_btn=False):
        """Dica da tela atual (None se não houver). help_btn: a do botão "?" (na run, só no pause)."""
        st = self.state
        if st == "run":
            run = self.run
            if help_btn and run is not None and run.state == "pause":
                return "training" if run.training else "run"
            return None
        if st == "hub":
            return "welcome"
        if st == "inventory":
            return "smith" if self.inv_mode == "smith" else "chest"
        if st == "levels" and not help_btn:
            return None
        return self.STATE_TIPS.get(st)

    def help_rect(self):
        if self.state == "run":
            return pygame.Rect(W - 56, 14, 40, 40)
        if self.state == "party":   # a party não tem o Voltar no topo
            return pygame.Rect(W - 222, 42, 40, 40)
        return pygame.Rect(W - 218, 26, 40, 40)

    def draw_help_button(self, rect, mouse):
        """Bolinha com "?" que abre a explicação da tela."""
        s = self.screen
        hot = rect.collidepoint(mouse)
        c = rect.center
        rad = rect.w // 2
        pygame.draw.circle(s, (70, 90, 140) if hot else (40, 50, 80), c, rad)
        pygame.draw.circle(s, (150, 200, 255) if hot else (110, 150, 210), c, rad, 2)
        self.text("?", "normal", WHITE, c, "center")

    def show_tip(self, tid, force=False):
        """Abre a pop-up de explicação (só na primeira vez, a não ser com force)."""
        import tips as tips_mod
        if tid not in tips_mod.TIPS:
            return
        seen = self.roster.tips_seen
        if tid in seen and not force:
            return
        if self.tip is not None and not force:   # já tem uma aberta: esta fica para a próxima vez
            return
        self.tip = [tid, 0]
        if tid not in seen:
            seen.add(tid)
            self.roster.save()

    def tip_rects(self):
        import tips as tips_mod
        tid, page = self.tip
        txt = tips_mod.pages(tid, i18n.LANG)[page]
        lines = self.wrap(txt, "normal", 700)
        h = 150 + len(lines) * 27
        panel = pygame.Rect(W / 2 - 390, max(20, H / 2 - h / 2), 780, h)
        nxt = pygame.Rect(panel.right - 190, panel.bottom - 62, 166, 44)
        prev = pygame.Rect(panel.x + 24, panel.bottom - 62, 140, 44)
        return panel, lines, nxt, prev

    def tip_next(self, step=1):
        import tips as tips_mod
        tid, page = self.tip
        n = len(tips_mod.pages(tid, i18n.LANG))
        page += step
        if page >= n:
            self.tip = None
        else:
            self.tip[1] = max(0, page)

    def tip_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_d):
                self.tip_next()
            elif ev.key in (pygame.K_LEFT, pygame.K_a):
                self.tip_next(-1)
            elif ev.key == pygame.K_ESCAPE:
                self.tip = None
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            panel, _lines, nxt, prev = self.tip_rects()
            if nxt.collidepoint(ev.pos):
                self.tip_next()
            elif prev.collidepoint(ev.pos) and self.tip[1] > 0:
                self.tip_next(-1)

    def draw_tip(self):
        import tips as tips_mod
        L = i18n.L
        s = self.screen
        tid, page = self.tip
        n = len(tips_mod.pages(tid, i18n.LANG))
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 165))
        s.blit(shade, (0, 0))
        panel, lines, nxt, prev = self.tip_rects()
        pygame.draw.rect(s, (26, 28, 40), panel, border_radius=16)
        pygame.draw.rect(s, (150, 200, 255), panel, 2, border_radius=16)
        self.draw_help_button(pygame.Rect(panel.x + 22, panel.y + 18, 40, 40), (-1, -1))
        self.text(tips_mod.title(tid, i18n.LANG), "big", YELLOW, (panel.x + 76, panel.y + 14))
        y = panel.y + 76
        for ln in lines:
            self.text(ln, "normal", WHITE, (panel.x + 40, y))
            y += 27
        mouse = self.mouse_pos()
        last = page == n - 1
        self.button(nxt, L("Got it!", "Entendi!") if last else L("Next", "Próximo"), nxt.collidepoint(mouse),
                    GREEN if last else WHITE)
        if page > 0:
            self.button(prev, L("Back", "Voltar"), prev.collidepoint(mouse))
        if n > 1:
            for k in range(n):
                pygame.draw.circle(s, YELLOW if k == page else (90, 90, 105),
                                   (panel.centerx - (n - 1) * 9 + k * 18, nxt.centery), 5)

    # ================================================================
    # Saves (New Save / Load Save): 3 espaços com um card de resumo cada
    # ================================================================
    def saves_rects(self):
        w, h, gap = 370, 470, 25
        x0 = (W - (3 * w + 2 * gap)) / 2
        return [pygame.Rect(x0 + i * (w + gap), 140, w, h) for i in range(3)]

    def saves_pick(self, i):
        L = i18n.L
        slot = i + 1
        info = roster_slot_summary(slot)
        if self.saves_mode == "load":
            if info is None:
                self.toast(L("This slot is empty: use New Save to create a save here.",
                             "Este espaço está vazio: use New Save para criar um save aqui."))
                return
            self.use_slot(slot)
            self.toast(L(f"Save {slot} loaded.", f"Save {slot} carregado."))
            self.go("hub")
            return
        if info is not None and self.saves_confirm != slot:   # sobrescrever pede confirmação
            self.saves_confirm = slot
            self.toast(L(f"Save {slot} already has progress: click it again to ERASE it and start over.",
                         f"O Save {slot} já tem progresso: clique de novo nele para APAGAR e começar do zero."))
            return
        self.use_slot(slot, new=True)
        self.toast(L(f"New save created in slot {slot}.", f"Save novo criado no espaço {slot}."))
        self.go("hub")

    def saves_event(self, ev):
        rects = self.saves_rects()
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                self.saves_sel = (self.saves_sel - 1) % 3
                self.saves_confirm = None
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.saves_sel = (self.saves_sel + 1) % 3
                self.saves_confirm = None
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.saves_pick(self.saves_sel)
            elif ev.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("menu")
        elif ev.type == pygame.MOUSEMOTION:
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos) and self.saves_sel != i:
                    self.saves_sel = i
                    self.saves_confirm = None
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.lo_back_rect().collidepoint(ev.pos):
                self.go("menu")
                return True
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos):
                    self.saves_sel = i
                    self.saves_pick(i)
        return True

    def draw_saves(self):
        L = i18n.L
        s = self.screen
        self.draw_main_bg()
        mouse = self.mouse_pos()
        new = self.saves_mode == "new"
        self.text(L("NEW SAVE", "NOVO SAVE") if new else L("LOAD SAVE", "CARREGAR SAVE"), "big", YELLOW, (40, 22))
        self.text(L("Pick a slot for the new save (a slot with progress asks for confirmation before erasing it)",
                    "Escolha um espaço para o save novo (um espaço com progresso pede confirmação antes de apagar)")
                  if new else L("Pick the save to continue", "Escolha o save para continuar"),
                  "normal", GREY, (42, 84))
        back = self.lo_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        rows = [("stages", L("Stages cleared", "Fases concluídas")), ("accs", L("Accessories", "Acessórios")),
                ("trophies", L("Trophies", "Troféus")), ("classes", L("Classes at Lv 100", "Classes no Nv 100"))]
        for i, r in enumerate(self.saves_rects()):
            slot = i + 1
            info = roster_slot_summary(slot)
            sel = i == self.saves_sel
            cur = slot == getattr(self.roster, 'slot', 1)
            danger = new and info is not None and self.saves_confirm == slot
            panel = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(panel, (24, 24, 34, 235), panel.get_rect(), border_radius=14)
            s.blit(panel, r)
            bc = RED if danger else YELLOW if sel else (120, 220, 230) if cur else (90, 90, 105)
            pygame.draw.rect(s, bc, r, 3 if sel or danger else 1, border_radius=14)
            self.text(f"Save {slot}", "normal", WHITE, (r.x + 20, r.y + 16))
            if cur:
                self.text(L("in use", "em uso"), "small", (120, 220, 230), (r.right - 20, r.y + 20), "topright")
            if info is None:
                self.text(L("Empty", "Vazio"), "big", (110, 110, 125), (r.centerx, r.centery - 20), "center")
                self.text(L("Create a new save here" if new else "No save in this slot",
                            "Criar um save novo aqui" if new else "Nenhum save neste espaço"), "small",
                          GREEN if new else GREY, (r.centerx, r.centery + 24), "center")
                continue
            # herói: bonequinho com a classe atual, nome e nível
            draw_class_icon(s, info["cls"], (r.x + 62, r.y + 104), 26, facing=V(1, 0.2), outline=YELLOW, outline_w=3,
                            who=info["name"], look=info.get("look"))
            self.text(info["name"], "normal", YELLOW, (r.x + 108, r.y + 66))
            self.text(f"{tr(CLASSES[info['cls']]['name'])}  ·  " + L(f"Lv {info['level']}", f"Nv {info['level']}"),
                      "small", CLASSES[info["cls"]]["color"], (r.x + 108, r.y + 94))
            self.text(L(f"{info['members']} in the group  ·  {info['gold']} gold",
                        f"{info['members']} no grupo  ·  {info['gold']} de gold"), "small", GREY, (r.x + 108, r.y + 114))
            # completude
            y = r.y + 150
            self.text(L("Completion", "Completude"), "small", GREY, (r.x + 20, y))
            self.text(f"{info['pct']:.0f}%", "big", GREEN if info["pct"] >= 100 else WHITE, (r.right - 20, y - 8),
                      "topright")
            self.bar(r.x + 20, y + 30, r.w - 40, 10, info["pct"] / 100, GREEN)
            y += 58
            for key, label in rows:
                a, b = info[key]
                self.text(label, "small", WHITE, (r.x + 20, y))
                self.text(f"{a} / {b}", "small", WHITE, (r.right - 20, y), "topright")
                self.bar(r.x + 20, y + 20, r.w - 40, 6, a / b if b else 0, (120, 220, 230))
                y += 40
            self.text(L("Endless Rift: highest level", "Endless Rift: maior nível"), "small", WHITE, (r.x + 20, y))
            self.text(L(f"Lv {info['rift']}", f"Nv {info['rift']}") if info["rift"] else L("locked", "bloqueada"),
                      "small", (190, 140, 255) if info["rift"] else GREY, (r.right - 20, y), "topright")
            if danger:
                self.text(L("Click again to ERASE and start over", "Clique de novo para APAGAR e recomeçar"),
                          "small", RED, (r.centerx, r.bottom - 24), "center")
        self.text(L("Arrows choose  ·  ENTER / click pick  ·  ESC back", "Setas escolhem  ·  ENTER / clique escolhe  ·  ESC volta"),
                  "small", GREY, (W / 2, H - 14), "center")
        self.draw_toast()

    # ================================================================
    # FAQ (botão isolado na tela principal)
    # ================================================================
    def faq_button_rect(self):
        return pygame.Rect(24, 20, 96, 40)

    # Wiki (antigo FAQ): aba "Guide" (o texto do FAQ), aba "Database" (wiki_db.py, gerada dos dados do jogo)
    # e barra de busca (procura nas duas abas)
    def open_faq(self, back="menu"):
        self.faq_back = back
        self.faq_sec = getattr(self, "faq_sec", 0)
        self.faq_scroll = 0
        self.wiki_tab = getattr(self, "wiki_tab", "guide")
        self.wiki_query = getattr(self, "wiki_query", "")
        self.wiki_typing = False
        self.go("faq")

    def faq_data(self):
        """Seções da aba atual; com busca, uma seção só com os resultados."""
        import wiki_db
        lang = i18n.LANG
        q = getattr(self, "wiki_query", "")
        key = (lang, getattr(self, "wiki_tab", "guide"), q)
        memo = getattr(self, "_wiki_memo", None)
        if memo and memo[0] == key:
            return memo[1]
        self._wiki_memo = (key, self._faq_data(wiki_db, lang, q))
        return self._wiki_memo[1]

    def _faq_data(self, wiki_db, lang, q):
        if q.strip():
            tabs, texts = wiki_db.search(q, lang, faq_for(lang))
            n = sum(len(r) for _t, r in tabs) + len(texts)
            return [(i18n.L(f"Results for \"{q.strip()}\" ({n})", f"Resultados para \"{q.strip()}\" ({n})"),
                     ("search", tabs, texts))]
        if getattr(self, "wiki_tab", "guide") == "db":
            return [(t["title"], t) for t in wiki_db.tables(lang)]
        return faq_for(lang)

    def wiki_tab_rects(self):
        return [pygame.Rect(32, 92, 121, 34), pygame.Rect(161, 92, 121, 34)]

    def wiki_search_rect(self):
        return pygame.Rect(300, 28, 560, 40)

    def faq_section_rects(self):
        n = len(self.faq_data())
        top = 136
        step = min(44, (self.FAQ_PANEL.bottom - top) // max(1, n))   # encolhe se houver muitos tópicos
        return [pygame.Rect(32, top + i * step, 250, step - 5) for i in range(n)]

    FAQ_PANEL = pygame.Rect(300, 92, W - 332, H - 140)

    WIKI_ICON = 30          # ícone das linhas da Database
    WIKI_LINE = 18          # altura de uma linha de texto pequeno

    def faq_layout(self):
        """Blocos da seção atual (em cache): ("gap", h) · ("text", linha, fonte, cor, h) · ("title", texto, h) ·
        ("thead", tabela, h) · ("row", tabela, linha, células quebradas, h)."""
        key = (i18n.LANG, getattr(self, "wiki_tab", "guide"), getattr(self, "wiki_query", ""), self.faq_sec)
        cache = self.__dict__.setdefault("_faq_cache", {})
        if key in cache:
            return cache[key]
        out = []
        data = self.faq_data()
        self.faq_sec = min(self.faq_sec, len(data) - 1)
        payload = data[self.faq_sec][1]
        tw = self.FAQ_PANEL.w - 56

        def texts(entries):
            for q, a in entries:
                out.append(("gap", 14))
                for ln in self.wrap(q, "normal", tw):
                    out.append(("text", ln, "normal", YELLOW, 28))
                for ln in self.wrap(a, "small", tw):
                    out.append(("text", ln, "small", WHITE, 21))

        def table(t, rows):
            out.append(("thead", t, 30))
            for r in rows:
                cells = [self.wrap(c, "small", w - 10) or [""] for c, (_h, w) in zip(r["cells"], t["cols"])]
                h = max(self.WIKI_ICON + 8, max(len(c) for c in cells) * self.WIKI_LINE + 10)
                out.append(("row", t, r, cells, h))

        if isinstance(payload, dict):            # tabela da Database
            table(payload, payload["rows"])
        elif isinstance(payload, tuple):         # resultados da busca
            _k, tabs, txts = payload
            for t, rows in tabs:
                out.append(("gap", 10))
                out.append(("title", t["title"], 34))
                table(t, rows)
            if txts:
                out.append(("gap", 10))
                out.append(("title", i18n.L("Guide", "Guia"), 34))
                texts(txts)
            if not tabs and not txts:
                texts([(i18n.L("Nothing found", "Nada encontrado"), i18n.L("Try another word.", "Tente outra palavra."))])
        else:                                    # texto do guia
            texts(payload)
        if len(cache) > 40:
            cache.clear()
        cache[key] = out
        return out

    def faq_content_height(self):
        return sum(b[-1] for b in self.faq_layout())

    def draw_wiki_block(self, b, x, y, mouse):
        """Desenha um bloco da Wiki na posição y."""
        s = self.screen
        kind = b[0]
        if kind == "text":
            self.text(b[1], b[2], b[3], (x, y))
        elif kind == "title":
            self.text(b[1], "normal", (150, 200, 255), (x, y + 6))
        elif kind == "thead":
            t = b[1]
            pygame.draw.rect(s, (40, 42, 58), (x - 8, y, self.FAQ_PANEL.w - 40, 26), border_radius=6)
            cx = x + self.WIKI_ICON + 8
            for head, w in t["cols"]:
                self.text(head, "small", (230, 200, 120), (cx, y + 13), "midleft")
                cx += w
        elif kind == "row":
            _k, t, r, cells, h = b
            rr = pygame.Rect(x - 8, y + 2, self.FAQ_PANEL.w - 40, h - 4)
            if rr.collidepoint(mouse):
                pygame.draw.rect(s, (44, 46, 64), rr, border_radius=6)
            pygame.draw.line(s, (40, 40, 52), (rr.x, rr.bottom + 1), (rr.right, rr.bottom + 1), 1)
            ic = r.get("_ic")
            if ic is None and r.get("icon"):
                try:
                    ic = r["_ic"] = r["icon"](self.WIKI_ICON)
                except Exception:   # um ícone que falhe não derruba a Wiki
                    ic = r["_ic"] = False
            if ic:
                s.blit(ic, ic.get_rect(center=(x + self.WIKI_ICON // 2, y + h // 2)))
            cx = x + self.WIKI_ICON + 8
            for k, ((_hd, w), lines) in enumerate(zip(t["cols"], cells)):
                ly = y + 6
                for ln in lines:
                    self.text(ln, "small", YELLOW if k == 0 else WHITE, (cx, ly))
                    ly += self.WIKI_LINE
                cx += w

    def wiki_set(self, tab=None, query=None):
        if tab is not None:
            self.wiki_tab = tab
            self.faq_sec = 0
        if query is not None:
            self.wiki_query = query
            self.faq_sec = 0
        self.faq_scroll = 0

    def faq_scroll_by(self, dy):
        max_scroll = max(0, self.faq_content_height() - (self.FAQ_PANEL.h - 70))
        self.faq_scroll = max(0, min(max_scroll, self.faq_scroll + dy))

    def faq_back_rect(self):
        return pygame.Rect(W - 170, 24, 140, 44)

    def faq_event(self, ev):
        n = len(self.faq_data())
        if ev.type == pygame.KEYDOWN and getattr(self, "wiki_typing", False):   # digitando na busca
            k = ev.key
            if k == pygame.K_ESCAPE:
                if self.wiki_query:
                    self.wiki_set(query="")
                else:
                    self.wiki_typing = False
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self.wiki_typing = False
            elif k == pygame.K_BACKSPACE:
                self.wiki_set(query=self.wiki_query[:-1])
            elif ev.unicode and ev.unicode.isprintable() and len(self.wiki_query) < 40:
                self.wiki_set(query=self.wiki_query + ev.unicode)
            return True
        if ev.type == pygame.KEYDOWN and (ev.key == pygame.K_SLASH or ev.unicode == "/"):
            self.wiki_typing = True
            return True
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k == pygame.K_ESCAPE and self.wiki_query:
                self.wiki_set(query="")
            elif k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go(getattr(self, "faq_back", "menu"))
            elif k in (pygame.K_UP, pygame.K_w):
                self.faq_sec, self.faq_scroll = (self.faq_sec - 1) % n, 0
            elif k in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                self.faq_sec, self.faq_scroll = (self.faq_sec + 1) % n, 0
            elif k == pygame.K_PAGEDOWN:
                self.faq_scroll_by(300)
            elif k == pygame.K_PAGEUP:
                self.faq_scroll_by(-300)
        elif ev.type == pygame.MOUSEWHEEL:
            self.faq_scroll_by(-ev.y * 40)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.faq_back_rect().collidepoint(ev.pos):
                self.go(getattr(self, "faq_back", "menu"))
                return True
            self.wiki_typing = self.wiki_search_rect().collidepoint(ev.pos)
            if self.wiki_typing:
                return True
            for tab, r in zip(("guide", "db"), self.wiki_tab_rects()):
                if r.collidepoint(ev.pos):
                    self.wiki_set(tab=tab, query="")
                    return True
            for i, r in enumerate(self.faq_section_rects()):
                if r.collidepoint(ev.pos):
                    self.faq_sec, self.faq_scroll = i, 0
        return True

    def draw_faq(self):
        s = self.screen
        self.menu_bg()   # mesmo fundo simples, aberto do menu principal ou do acampamento
        mouse = self.mouse_pos()
        self.text("WIKI", "big", YELLOW, (32, 24))
        back = self.faq_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        L = i18n.L
        # abas e busca
        tab = getattr(self, "wiki_tab", "guide")
        searching = bool(getattr(self, "wiki_query", "").strip())
        for name, r, lab in zip(("guide", "db"), self.wiki_tab_rects(), (L("Guide", "Guia"), "Database")):
            sel = name == tab and not searching
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if r.collidepoint(mouse) else PANEL, r,
                             border_radius=8)
            pygame.draw.rect(s, YELLOW if sel else (90, 90, 105), r, 2 if sel else 1, border_radius=8)
            self.text(lab, "normal", YELLOW if sel else WHITE, r.center, "center")
        sr = self.wiki_search_rect()
        typing = getattr(self, "wiki_typing", False)
        pygame.draw.rect(s, (36, 36, 50), sr, border_radius=10)
        pygame.draw.rect(s, YELLOW if typing else (110, 110, 130), sr, 2 if typing else 1, border_radius=10)
        pygame.draw.circle(s, GREY, (sr.x + 20, sr.centery - 2), 7, 2)   # lupa
        pygame.draw.line(s, GREY, (sr.x + 25, sr.centery + 3), (sr.x + 31, sr.centery + 9), 2)
        q = getattr(self, "wiki_query", "")
        if q or typing:
            caret = "|" if typing and int(self.clock_time * 2) % 2 == 0 else ""
            self.text(q + caret, "normal", WHITE, (sr.x + 42, sr.centery), "midleft")
        else:
            self.text(L("Search (items, skills, statuses, classes...)  ·  click or press /",
                        "Pesquisar (itens, habilidades, status, classes...)  ·  clique ou aperte /"), "small", GREY,
                      (sr.x + 42, sr.centery), "midleft")
        for i, (r, (title, _)) in enumerate(zip(self.faq_section_rects(), self.faq_data())):
            sel, hov = i == self.faq_sec, r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hov else PANEL, r, border_radius=8)
            if sel:
                pygame.draw.rect(s, YELLOW, r, 2, border_radius=8)
            lab = tr(title)
            while len(lab) > 4 and self.fonts["normal"].size(lab)[0] > r.w - 24:
                lab = lab[:-2].rstrip() + "…"
            self.text(lab, "normal", YELLOW if sel else WHITE, (r.x + 14, r.centery), "midleft")
        panel = self.FAQ_PANEL
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        self.text(self.faq_data()[self.faq_sec][0], "big", WHITE, (panel.x + 28, panel.y + 14))
        view = pygame.Rect(panel.x + 2, panel.y + 66, panel.w - 4, panel.h - 72)
        prev_clip = s.get_clip()
        s.set_clip(view)
        y = view.y - self.faq_scroll
        for b in self.faq_layout():
            if y + b[-1] > view.y and y < view.bottom:
                self.draw_wiki_block(b, panel.x + 28, y, mouse)
            y += b[-1]
        s.set_clip(prev_clip)
        total = self.faq_content_height()
        if total > view.h:   # barra de rolagem
            bar_h = max(30, view.h * view.h / total)
            by = view.y + (view.h - bar_h) * self.faq_scroll / max(1, total - view.h)
            pygame.draw.rect(s, GREY, (panel.right - 10, by, 4, bar_h), border_radius=2)
        self.text(i18n.L("Click a topic or use Up/Down  ·  mouse wheel / PgUp PgDn to scroll  ·  / search  ·  ESC back",
                         "Clique num tópico ou use Cima/Baixo  ·  roda do mouse / PgUp PgDn rola  ·  / pesquisa  ·  ESC volta"),
                  "small", GREY, (W / 2, H - 30), "center")

    # ================================================================
    # Party Setup
    # ================================================================
    PARTY_BUTTONS = ["toggle", "class", "loadout", "look", "rename", "dismiss", "back"]

    def party_layout(self):
        rows = []
        for vis in range(LIST_ROWS):
            i = self.party_scroll + vis
            if i < len(self.roster.members):
                rows.append((i, pygame.Rect(40, 100 + vis * ROW_H, 430, ROW_H - 6)))
        recruit = pygame.Rect(40, 580, 430, 52)
        bw, gap = 98, 9
        buttons = {name: pygame.Rect(500 + k * (bw + gap), 580, bw, 52) for k, name in enumerate(self.PARTY_BUTTONS)}
        return rows, recruit, buttons

    @property
    def party_member(self):
        self.party_sel = max(0, min(self.party_sel, len(self.roster.members) - 1))
        return self.roster.members[self.party_sel]

    def party_scroll_to_sel(self):
        if self.party_sel < self.party_scroll:
            self.party_scroll = self.party_sel
        elif self.party_sel >= self.party_scroll + LIST_ROWS:
            self.party_scroll = self.party_sel - LIST_ROWS + 1
        self.party_scroll = max(0, min(self.party_scroll, max(0, len(self.roster.members) - LIST_ROWS)))

    def stat_lines(self, key, u):
        """Texto da dica de cada atributo, com o quanto ele está contribuindo agora."""
        m = u.member
        b = m.permanent_bonus()
        pas = u.passive_totals
        gt = getattr(u, "gear_totals", {})   # arma e capacete
        c = CLASSES[m.cls]
        GOLD = (250, 210, 70)

        def gear(k, pct=False):
            return f"  +  equipment {gt[k]:.1f}{'%' if pct else ''}" if gt.get(k) else ""

        def origem(k):
            parts = [f"base 5", f"character level {(m.level - 1) * GENERAL_LEVEL_STAT:.0f}", f"class levels {b[k]:.0f}"]
            if pas.get(k):
                parts.append(f"passives {pas[k]:.0f}")
            return "Source: " + " + ".join(parts)

        def dmg_line(attr, label):
            v = u.stats[attr]
            uses = c["attr"] == attr
            if c["attr"] == "bal":
                avg = (u.stats["str"] + u.stats["agi"] + u.stats["int"]) / 3
                cur = f"{tr(c['name'])} (Balanced) uses the average of STR/AGI/INT: +{avg:.1f} damage."
            elif uses:
                cur = f"Your current class ({tr(c['name'])}) uses {label}: its skills gain +{v * DMG_PER_ATTR:.0f} damage."
            else:
                cur = f"Your current class ({tr(c['name'])}) doesn't use {label}; applies to mastery skills from {label} classes."
            return [(f"+{v * DMG_PER_ATTR:.0f} damage on skills from {label} classes", WHITE), (cur, GREY)]

        if key == "str":
            v = u.stats["str"]
            return [(f"STR (Strength): {v}", GOLD)] + dmg_line("str", "STR") + [
                (f"+{v * ARMOR_PER_STR:.1f} armor ({ARMOR_PER_STR} per point)", WHITE),
                (f"+{v * CRITDMG_PER_STR:.1f}% critical damage ({CRITDMG_PER_STR}% per point)", WHITE), (origem("str"), GREY)]
        if key == "agi":
            v = u.stats["agi"]
            return [(f"AGI (Agility): {v}", GOLD)] + dmg_line("agi", "AGI") + [
                (f"+{v * DODGE_PER_AGI:.1f}% dodge ({DODGE_PER_AGI}% per point)", WHITE),
                (f"+{v * CRIT_PER_AGI:.1f}% critical chance ({CRIT_PER_AGI}% per point)", WHITE), (origem("agi"), GREY)]
        if key == "int":
            v = u.stats["int"]
            return [(f"INT (Intelligence): {v}", GOLD)] + dmg_line("int", "INT") + [
                (f"+{v * DMG_PER_ATTR:.0f} healing on heals from INT classes", WHITE),
                (f"+{v * MRES_PER_INT:.1f} magic defense ({MRES_PER_INT} per point)", WHITE),
                (f"+{v * CDR_PER_INT:.1f}% cooldown ({CDR_PER_INT}% per point)", WHITE), (origem("int"), GREY)]
        if key == "vit":
            v = u.stats["vit"]
            return [(f"VIT (Vitality): {v}", GOLD),
                    (f"+{v * HP_PER_VIT} base HP ({HP_PER_VIT} per point), before the class multiplier", WHITE),
                    (f"+{v * REGEN5_PER_VIT:.1f} HP/5s regeneration ({REGEN5_PER_VIT} per point)", WHITE),
                    (origem("vit"), GREY)]
        if key == "hp":
            base = 60 + u.stats["vit"] * HP_PER_VIT + u.stats["hp"] + pas.get("hp_flat", 0)
            return [(f"Max HP: {int(u.max_hp)}", GOLD),
                    (f"60 base + {u.stats['vit'] * HP_PER_VIT} from VIT + {int(u.stats['hp'])} from class levels"
                     + (f" + {pas['hp_flat']:.0f} from passives" if pas.get("hp_flat") else "") + f" = {int(base)}", WHITE),
                    (f"x{u.role['hp']:g} from the {role_name(m.cls)} role" +
                     (f"  ·  +{pas['hp_pct']:.0f}% from passives" if pas.get("hp_pct") else "") +
                     (f"  ·  +{gt['hp_pct']:.0f}% from equipment" if gt.get("hp_pct") else ""), GREY)]
        if key == "armor":
            return [(f"Armor: {u.armor:.1f}", GOLD),
                    ("Subtracted from every PHYSICAL hit taken (a hit always deals at least 1).", WHITE),
                    (f"STR {u.stats['str']} x {ARMOR_PER_STR} = {u.stats['str'] * ARMOR_PER_STR:.1f}  +  class levels "
                     f"{u.stats['armor']:.1f}" + (f"  +  passives {pas['armor']:.1f}" if pas.get("armor") else "")
                     + gear("armor"), GREY)]
        if key == "mres":
            return [(f"Magic defense: {u.mres:.1f}", GOLD),
                    ("Subtracted from every MAGICAL or ELEMENTAL hit taken (minimum 1).", WHITE),
                    (f"INT {u.stats['int']} x {MRES_PER_INT} = {u.stats['int'] * MRES_PER_INT:.1f}  +  class levels "
                     f"{u.stats['mres']:.1f}" + (f"  +  passives {pas['mres']:.1f}" if pas.get("mres") else "")
                     + gear("mres"), GREY)]
        if key == "dodge":
            return [(f"Dodge: {u.dodge:.1f}%", GOLD),
                    ("Chance to fully negate a PHYSICAL hit taken.", WHITE),
                    (f"AGI {u.stats['agi']} x {DODGE_PER_AGI}% = {u.stats['agi'] * DODGE_PER_AGI:.1f}%  +  class levels "
                     f"{u.stats['dodge']:.1f}%" +
                     (f"  +  passives {pas['dodge']:.1f}%" if pas.get("dodge") else ""), GREY),
                    softcap_line(getattr(u, "dodge_raw", u.dodge), MAX_DODGE)]
        lvb = u.stats
        if key == "regen5":
            return [(f"Regeneration: {u.regen5:.1f} HP every 5 s", GOLD),
                    ("HP recovered continuously during the run.", WHITE),
                    (f"VIT {lvb['vit']} x {REGEN5_PER_VIT} = {lvb['vit'] * REGEN5_PER_VIT:.1f}  +  class levels "
                     f"{lvb['regen5']:.1f}" + (f"  +  passives {pas['regen5']:.1f}" if pas.get("regen5") else ""), GREY)]
        if key == "crit":
            return [(f"Critical chance: {u.crit_chance:.1f}%", GOLD),
                    ("Chance for each hit to be critical and deal the extra critical damage.", WHITE),
                    (f"AGI {lvb['agi']} x {CRIT_PER_AGI}% = {lvb['agi'] * CRIT_PER_AGI:.1f}%  +  class levels "
                     f"{lvb['crit']:.1f}%" + (f"  +  passives {pas['crit']:.1f}%" if pas.get("crit") else "")
                     + gear("crit", True), GREY),
                    softcap_line(getattr(u, "crit_raw", u.crit_chance), MAX_CRIT)]
        if key == "critdmg":
            return [(f"Critical damage: +{u.crit_dmg:.1f}%", GOLD),
                    ("Extra damage of a critical hit (applied before the target's armor/magic defense).", WHITE),
                    (f"base {BASE_CRIT_DMG:.0f}%  +  STR {lvb['str']} x {CRITDMG_PER_STR}% = "
                     f"{lvb['str'] * CRITDMG_PER_STR:.1f}%  +  class levels {lvb['critdmg']:.1f}%" +
                     (f"  +  passives {pas['critdmg']:.1f}%" if pas.get("critdmg") else ""), GREY)]
        if key == "cdr":
            return [(f"Cooldown: {u.cooldown:.1f}%", GOLD),
                    (f"Reduces the cooldown of all skills (max {MAX_CDR:.0f}%).", WHITE),
                    (f"INT {lvb['int']} x {CDR_PER_INT}% = {lvb['int'] * CDR_PER_INT:.1f}%  +  class levels "
                     f"{lvb['cdr']:.1f}%" + (f"  +  passives {pas['cdr']:.1f}%" if pas.get("cdr") else ""), GREY),
                    softcap_line(getattr(u, "cdr_raw", u.cooldown), MAX_CDR)]
        return [(f"Defense: {int(min(0.75, u.defense) * 100)}%", GOLD),
                ("Reduces all damage taken by %, after armor/magic defense. Max 75% (with buffs).", WHITE),
                (f"{role_name(m.cls)} role (Defense x{u.role['defense']:g}): {(u.role['defense'] - 1) * 50:+.0f}%" +
                 (f"  ·  passivas: {pas['defense']:.0f}%" if pas.get("defense") else ""), GREY)]

    def party_action(self, name):
        m = self.party_member
        if name != "dismiss":
            self.confirm_dismiss = False
        if name == "toggle":
            err = self.roster.toggle_active(m)
            if err:
                self.toast(err)
        elif name == "loadout":
            self.open_loadout(m.cls, "party")
        elif name == "class":
            self.class_cursor = m.cls
            self.go("classes")
        elif name == "look":
            self.open_look(m)
        elif name == "rename":
            self.rename_buf = m.name
            pygame.key.start_text_input()
            self.go("rename")
        elif name == "dismiss":
            if m.hero:
                self.toast("The hero can't be dismissed.")
            elif not self.confirm_dismiss:
                self.confirm_dismiss = True
                self.toast(f"Click Dismiss again to remove {m.name}.")
            else:
                self.roster.dismiss(m)
                self.confirm_dismiss = False
                self.party_sel -= 1
                self.party_scroll_to_sel()
        elif name == "recruit":
            cost = self.roster.recruit_cost()
            new, err = self.roster.recruit()
            if err:
                self.toast(err)
                return
            self.party_sel = len(self.roster.members) - 1
            self.party_scroll_to_sel()
            self.toast(f"{new.name} joined the group for {cost} gold" +
                       (" (active)." if new.active else " (reserve)."))
        elif name == "back":
            self.go("hub")
            self.sel = 2

    def party_event(self, ev):
        rows, recruit, buttons = self.party_layout()
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_UP, pygame.K_w):
                self.party_sel = (self.party_sel - 1) % len(self.roster.members)
                self.confirm_dismiss = False
                self.party_scroll_to_sel()
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.party_sel = (self.party_sel + 1) % len(self.roster.members)
                self.confirm_dismiss = False
                self.party_scroll_to_sel()
            elif k == pygame.K_SPACE:
                self.party_action("toggle")
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_c):
                self.party_action("class")
            elif k == pygame.K_r:
                self.party_action("rename")
            elif k == pygame.K_a:
                self.party_action("look")
            elif k == pygame.K_l:
                self.party_action("loadout")
            elif k == pygame.K_n:
                self.party_action("recruit")
            elif k == pygame.K_DELETE:
                self.party_action("dismiss")
            elif k == pygame.K_ESCAPE:
                self.party_action("back")
        elif ev.type == pygame.MOUSEWHEEL:
            self.party_scroll = max(0, min(self.party_scroll - ev.y, max(0, len(self.roster.members) - LIST_ROWS)))
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, r in rows:
                if r.collidepoint(ev.pos):
                    if i != self.party_sel:
                        self.confirm_dismiss = False
                    self.party_sel = i
                    return True
            if recruit.collidepoint(ev.pos):
                self.party_action("recruit")
            for name, r in buttons.items():
                if r.collidepoint(ev.pos):
                    self.party_action(name)
        return True

    def draw_party(self):
        s = self.screen
        self.menu_bg()
        self.text("PARTY SETUP", "big", YELLOW, (40, 30))
        n_active = len(self.roster.active())
        self.text(f"Active: {n_active}/{MAX_ACTIVE}   ·   Members: {len(self.roster.members)}", "normal", WHITE,
                  (W - 240, 50), "topright")
        self.draw_gold((W - 40, 50))
        rows, recruit, buttons = self.party_layout()
        mouse = self.mouse_pos()

        # ---- lista ----
        pygame.draw.rect(s, PANEL, (32, 92, 446, LIST_ROWS * ROW_H + 10), border_radius=12)
        for i, r in rows:
            m = self.roster.members[i]
            self.tip_member = m
            sel = i == self.party_sel
            hover = r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hover else DARK, r, border_radius=8)
            if sel:
                pygame.draw.rect(s, YELLOW, r, 2, border_radius=8)
            c = CLASSES[m.cls]
            draw_class_icon(s, m.cls, (r.x + 26, r.centery + 2), 13, outline=None, who=m.name, look=m.look, member=m, shadow=False)
            ci = si.class_icon(m.cls, 26)
            s.blit(ci, ci.get_rect(midleft=(r.x + 46, r.centery)))
            self.text(m.name, "normal", WHITE, (r.x + 80, r.y + 6))
            self.text(f"Lv {m.level}  ·  {tr(c['name'])} {m.class_level(m.cls)}", "small", GREY, (r.x + 80, r.y + 30))
            tag, col = ("HERO", YELLOW) if m.hero else ("ACTIVE", GREEN) if m.active else ("RESERVE", GREY)
            self.text(tag, "small", col, (r.right - 14, r.centery), "midright")
        if len(self.roster.members) > LIST_ROWS:
            total = len(self.roster.members)
            h = LIST_ROWS * ROW_H
            bar_h = max(30, h * LIST_ROWS / total)
            y = 100 + (h - bar_h) * self.party_scroll / max(1, total - LIST_ROWS)
            pygame.draw.rect(s, GREY, (474, y, 4, bar_h), border_radius=2)
        cost = self.roster.recruit_cost()
        afford = self.roster.gold >= cost
        if len(self.roster.members) >= MAX_MEMBERS:
            self.button(recruit, f"Party full ({MAX_MEMBERS}/{MAX_MEMBERS})", False, GREY, enabled=False)
        else:
            self.button(recruit, f"+ Recruit new member  ({cost} gold)", recruit.collidepoint(mouse),
                        GREEN if afford else RED)

        # ---- detalhes ----
        m = self.party_member
        c = CLASSES[m.cls]
        panel = pygame.Rect(500, 92, 740, LIST_ROWS * ROW_H + 10)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        draw_class_icon(s, m.cls, (556, 158), 28, outline=YELLOW if m.hero else WHITE, who=m.name, look=m.look, member=m)
        self.text(m.name, "big", WHITE, (650, 118))
        tag = "Hero (always in the party)" if m.hero else "Active in the party" if m.active else "In reserve"
        self.text(tag, "small", YELLOW if m.hero else GREEN if m.active else GREY, (653, 170))

        y = 215
        lvl_txt = f"Level {m.level}"
        self.text(lvl_txt, "normal", WHITE, (530, y))
        if True:   # nível geral sem limite: sempre mostra a barra de EXP
            self.bar(780, y + 4, 230, 12, m.exp / exp_to_next(m.level), (90, 160, 255))
            self.text(f"{m.exp}/{exp_to_next(m.level)}", "small", GREY, (1020, y + 2))
        y += 34
        clv = m.class_level(m.cls)
        s.blit(si.class_icon(m.cls, 26), (530, y - 4))
        self.text(f"{tr(c['name'])}  Lv {clv} / {prog.max_level(m.cls)}", "normal", c["color"], (564, y))
        if clv < prog.max_level(m.cls):
            self.bar(780, y + 4, 230, 12, m.class_exp(m.cls) / class_exp_to_next(clv), c["color"])
            self.text(f"{m.class_exp(m.cls)}/{class_exp_to_next(clv)}", "small", GREY, (1020, y + 2))
        y += 30
        self.text(f"{TIER_NAMES[c['tier']]}  ·  {c['weapon']}  ·  Attribute: {ATTR_NAMES[c['attr']]}", "small",
                  GREY, (530, y))
        self.text(self.fit(f"{i18n.L('Role', 'Role')}: {role_name(m.cls, i18n.LANG)}  ·  " + tr(c['role']), "small", 700),
                  "small", GREY, (530, y + 20))

        # atributos (já com bônus permanentes de classe e passivas equipadas) — passe o mouse para detalhes
        u = Unit(m, 0)
        st = u.stats
        y = 345
        self.text("Attributes  (hover for details)", "normal", YELLOW, (530, y))
        attrs = [("STR", st["str"], "str"), ("AGI", st["agi"], "agi"), ("INT", st["int"], "int"),
                 ("VIT", st["vit"], "vit"), ("HP", int(u.max_hp), "hp"), ("Armor", f"{u.armor:.1f}", "armor"),
                 ("Magic def.", f"{u.mres:.1f}", "mres"), ("Dodge", f"{u.dodge:.1f}%", "dodge"),
                 ("Defense", f"{int(min(0.75, u.defense) * 100)}%", "defense"),
                 ("Crit chance", f"{u.crit_chance:.1f}%", "crit"), ("Crit damage", f"+{u.crit_dmg:.0f}%", "critdmg"),
                 ("Cooldown", f"{u.cooldown:.1f}%", "cdr"), ("Regen. HP/5s", f"{u.regen5:.1f}", "regen5")]
        hover = None
        for k, (name, val, key) in enumerate(attrs):
            col_x = 530 + (k % 2) * 160
            row_y = y + 30 + (k // 2) * 22
            rect = pygame.Rect(col_x - 4, row_y - 3, 148, 22)
            if rect.collidepoint(mouse):
                pygame.draw.rect(s, (55, 55, 75), rect, border_radius=4)
                hover = key
            self.text(name, "small", GREY, (col_x, row_y))
            self.text(val, "small", WHITE, (col_x + 136, row_y), "topright")
        # (a origem de cada valor, incluindo os bônus permanentes de classe, aparece na dica de cada atributo)
        self.stat_tooltip = (hover, u) if hover else None

        # resumo do loadout
        x0 = 880
        self.text("Loadout  (L to edit)", "normal", YELLOW, (x0, y))
        specs = [prog.CONTENT[m.cls]["basic"]]
        specs += [prog.get_active(r) if r else None for r in m.slots("active", "class") + m.slots("active", "extra")]
        for k, sp in enumerate(specs):
            ry = y + 30 + k * 20
            self.text(f"{k + 1}", "small", GREY, (x0, ry))
            if sp:
                self.skill_icon(sp, "active", 17, (x0 + 26, ry + 7), hover=(x0 + 16, ry - 2, 330, 19))
                self.text(self.fit(sp["name"], "small", 300), "small", WHITE, (x0 + 40, ry))
            else:
                self.text("-", "small", (90, 90, 100), (x0 + 40, ry))
        n_pas = len(m.equipped("passive"))
        self.text(f"Passives equipped: {n_pas}/10", "small", GREEN if n_pas else GREY, (x0, y + 176))

        # botões
        labels = {
            "toggle": "Remove" if (m.active and not m.hero) else "Activate",
            "class": "Class",
            "loadout": "Loadout",
            "rename": "Rename",
            "look": L("Look", "Aparência"),
            "dismiss": "Confirm?" if self.confirm_dismiss else "Dismiss",
            "back": "Back",
        }
        for name, r in buttons.items():
            enabled = not (m.hero and name in ("toggle", "dismiss"))
            col = RED if name == "dismiss" else WHITE
            self.button(r, labels[name], r.collidepoint(mouse), col, enabled=enabled)
        self.text(L("Arrows select  ·  SPACE activate/remove  ·  ENTER class  ·  L loadout  ·  A look  ·  R rename  ·  "
                    "N recruit  ·  DEL dismiss  ·  ESC back",
                    "Setas selecionam  ·  ESPAÇO ativa/remove  ·  ENTER classe  ·  L loadout  ·  A aparência  ·  "
                    "R renomeia  ·  N recruta  ·  DEL dispensa  ·  ESC volta"), "small", GREY, (W / 2, H - 30), "center")
        self.draw_toast()
        if getattr(self, "stat_tooltip", None) and self.state == "party":
            key, u = self.stat_tooltip
            self.draw_tooltip(self.stat_lines(key, u), mouse)

    # ================================================================
    # árvore de classes
    # ================================================================
    # Layout horizontal: Freelancer -> 9 básicas -> cada básica se bifurca em 2 avançadas (uma OU outra)
    TREE_TOP = 100
    TREE_ROW = 62
    BASIC_X, BASIC_W, BASIC_H = 210, 150, 46
    FORK_X = 392
    ADV_X, ADV_W, ADV_H = 430, 190, 26

    def class_layout(self):
        """Retorna {classe: Rect} e a ordem de navegação."""
        rects = {}
        n = len(BASIC_ORDER)
        mid = self.TREE_TOP + (n - 1) * self.TREE_ROW / 2 + self.BASIC_H / 2
        rects["freelancer"] = pygame.Rect(24, int(mid - 30), 140, 60)
        rects["freelancer_t2"] = pygame.Rect(24, int(mid + 70), 140, 50)
        rects["warfarer"] = pygame.Rect(24, int(mid + 160), 140, 50)
        for i, b in enumerate(BASIC_ORDER):
            y = self.TREE_TOP + i * self.TREE_ROW
            rects[b] = pygame.Rect(self.BASIC_X, y, self.BASIC_W, self.BASIC_H)
            cy = y + self.BASIC_H // 2
            a1, a2 = ADVANCED[b]
            rects[a1] = pygame.Rect(self.ADV_X, cy - self.ADV_H - 3, self.ADV_W, self.ADV_H)
            rects[a2] = pygame.Rect(self.ADV_X, cy + 3, self.ADV_W, self.ADV_H)
        return rects

    def class_select_rect(self):
        return pygame.Rect(1050, H - 104, 176, 50)

    def class_loadout_rect(self):
        return pygame.Rect(862, H - 104, 176, 50)

    def class_levels_rect(self):
        return pygame.Rect(674, H - 104, 176, 50)

    def open_levels(self):
        self.lv_cid = self.class_cursor
        self.lv_scroll = 0
        self.go("levels")

    def class_open_loadout(self):
        m = self.party_member
        if not m.is_unlocked(self.class_cursor):
            self.toast(m.unlock_requirement(self.class_cursor))
        else:
            self.open_loadout(self.class_cursor, "classes")

    def class_move(self, key):
        cur = self.class_cursor
        c = CLASSES[cur]
        adv_seq = [a for b in BASIC_ORDER for a in ADVANCED[b]]
        if c["tier"] in (0, 3, 4):
            chain = ["freelancer", "freelancer_t2", "warfarer"]
            i = chain.index(cur)
            if key == "right":
                self.class_cursor = BASIC_ORDER[len(BASIC_ORDER) // 2]
            elif key == "down":
                self.class_cursor = chain[min(len(chain) - 1, i + 1)]
            elif key == "up":
                self.class_cursor = chain[max(0, i - 1)]
        elif c["tier"] == 1:
            i = BASIC_ORDER.index(cur)
            if key == "up":
                self.class_cursor = BASIC_ORDER[(i - 1) % len(BASIC_ORDER)]
            elif key == "down":
                self.class_cursor = BASIC_ORDER[(i + 1) % len(BASIC_ORDER)]
            elif key == "left":
                self.class_cursor = "freelancer"
            elif key == "right":
                self.class_cursor = ADVANCED[cur][0]
        else:
            i = adv_seq.index(cur)
            if key == "up":
                self.class_cursor = adv_seq[(i - 1) % len(adv_seq)]
            elif key == "down":
                self.class_cursor = adv_seq[(i + 1) % len(adv_seq)]
            elif key == "left":
                self.class_cursor = c["parent"]

    def class_choose(self):
        m = self.party_member
        cid = self.class_cursor
        if cid == m.cls:
            self.toast("That is already the current class.")
        elif not m.is_unlocked(cid):
            self.toast(m.unlock_requirement(cid))
        elif cid not in m.loadouts and m.has_mastery_slots(m.cls):
            self.mastery_prompt = (m, m.cls, cid)   # primeira vez nesta classe: pergunta se copia a maestria
        else:
            m.set_class(cid)
            self.roster.save()
            self.toast(f"{m.name} is now a {tr(CLASSES[cid]['name'])}!")

    # ---- primeira troca para uma classe: copiar os slots de maestria da classe atual? ----
    mastery_prompt = None

    def mastery_prompt_rects(self):
        box = pygame.Rect(0, 0, 620, 210)
        box.center = (W / 2, H / 2)
        yes = pygame.Rect(box.centerx - 170, box.bottom - 64, 150, 44)
        no = pygame.Rect(box.centerx + 20, box.bottom - 64, 150, 44)
        return box, yes, no

    def mastery_answer(self, copy):
        m, old, cid = self.mastery_prompt
        self.mastery_prompt = None
        m.set_class(cid)
        n = m.copy_mastery(old, cid) if copy else 0
        m.refresh_loadout()
        self.roster.save()
        L = i18n.L
        if copy:
            self.toast(L(f"{m.name} is now a {tr(CLASSES[cid]['name'])}! Mastery slots copied ({n}).",
                         f"{m.name} agora é {tr(CLASSES[cid]['name'])}! Slots de maestria copiados ({n})."))
        else:
            self.toast(f"{m.name} is now a {tr(CLASSES[cid]['name'])}!")

    def mastery_prompt_event(self, ev):
        box, yes, no = self.mastery_prompt_rects()
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_y, pygame.K_s, pygame.K_RETURN):
                self.mastery_answer(True)
            elif ev.key in (pygame.K_n, pygame.K_ESCAPE):
                self.mastery_answer(False)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if yes.collidepoint(ev.pos):
                self.mastery_answer(True)
            elif no.collidepoint(ev.pos):
                self.mastery_answer(False)
        return True

    def draw_mastery_prompt(self):
        m, old, cid = self.mastery_prompt
        L = i18n.L
        s = self.screen
        shade = pygame.Surface((W, H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 150))
        s.blit(shade, (0, 0))
        box, yes, no = self.mastery_prompt_rects()
        pygame.draw.rect(s, PANEL, box, border_radius=14)
        pygame.draw.rect(s, YELLOW, box, 2, border_radius=14)
        on, nn = CLASSES[old]["name"], CLASSES[cid]["name"]
        self.text(L("First time as this class", "Primeira vez nesta classe"), "normal", YELLOW,
                  (box.centerx, box.y + 18), "midtop")
        msg = L(f"Copy the mastery slots of {on} to {nn}?", f"Copiar os slots de maestria de {on} para {nn}?")
        self.text(msg, "normal", WHITE, (box.centerx, box.y + 56), "midtop")
        self.text(L("Skills that don't fit the new class are skipped.",
                    "Habilidades que não couberem na nova classe são ignoradas."), "small", GREY,
                  (box.centerx, box.y + 90), "midtop")
        mouse = self.mouse_pos()
        self.button(yes, L("Yes (Y)", "Sim (S)"), yes.collidepoint(mouse))
        self.button(no, L("No (N)", "Não (N)"), no.collidepoint(mouse))

    # ---- filtro por tag na tela de classes (destaca classes e habilidades com a tag) ----
    cls_ftag = None
    cls_dd = False
    cls_dd_sel = 0

    def cls_filter_rect(self):
        return pygame.Rect(650, 40, 290, 32)

    def cls_tag_values(self):
        seen = set()
        for cc in prog.CONTENT.values():
            for sp in [cc.get("basic")] + list(cc.get("actives", [])) + list(cc.get("passives", [])):
                if sp:
                    seen.update(sp.get("tags") or [])
        return [None] + [t for t in TAG_ORDER if t in seen]

    def skill_has_tag(self, sp):
        return bool(self.cls_ftag) and self.cls_ftag in (sp.get("tags") or [])

    def class_has_tag(self, cid):
        cc = prog.CONTENT.get(cid, {})
        return any(self.skill_has_tag(sp) for sp in list(cc.get("actives", [])) + list(cc.get("passives", [])) if sp)

    def cls_dd_rects(self):
        vals = self.cls_tag_values()
        rows = -(-len(vals) // self.DD_COLS)
        out = []
        for i, v in enumerate(vals):
            col, row = i // rows, i % rows
            out.append((i, v, pygame.Rect(656 + col * self.DD_COL_W, 82 + row * self.DD_ROW_H, self.DD_COL_W - 8,
                                          self.DD_ROW_H - 3)))
        return out

    def cls_dd_pick(self, i):
        vals = self.cls_tag_values()
        if 0 <= i < len(vals):
            self.cls_ftag = vals[i]
        self.cls_dd = False

    def cls_dd_event(self, ev):
        vals = self.cls_tag_values()
        n = len(vals)
        rows = max(1, -(-n // self.DD_COLS))
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_t):
                self.cls_dd = False
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.cls_dd_pick(self.cls_dd_sel)
            elif k in (pygame.K_UP, pygame.K_DOWN):
                self.cls_dd_sel = (self.cls_dd_sel + (1 if k == pygame.K_DOWN else -1)) % n
            elif k in (pygame.K_LEFT, pygame.K_RIGHT):
                j = self.cls_dd_sel + (rows if k == pygame.K_RIGHT else -rows)
                if 0 <= j < n:
                    self.cls_dd_sel = j
            elif ev.unicode and ev.unicode.isalpha():
                ch = ev.unicode.lower()
                for step in range(1, n + 1):
                    j = (self.cls_dd_sel + step) % n
                    if vals[j] and tag_name(vals[j], i18n.LANG).lower().startswith(ch):
                        self.cls_dd_sel = j
                        break
        elif ev.type == pygame.MOUSEMOTION:
            for i, v, r in self.cls_dd_rects():
                if r.collidepoint(ev.pos):
                    self.cls_dd_sel = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            for i, v, r in self.cls_dd_rects():
                if r.collidepoint(ev.pos):
                    self.cls_dd_pick(i)
                    return True
            self.cls_dd = False
        return True

    def tag_mark(self, r):
        """Fundo destacado de uma habilidade que tem a tag selecionada no filtro."""
        hl = pygame.Surface(r.size, pygame.SRCALPHA)
        hl.fill((90, 230, 255, 45))
        self.screen.blit(hl, r.topleft)
        pygame.draw.rect(self.screen, (90, 230, 255), r, 1, border_radius=4)

    def draw_cls_filter(self, mouse):
        s = self.screen
        r = self.cls_filter_rect()
        active = self.cls_ftag is not None
        pygame.draw.rect(s, (60, 60, 85) if r.collidepoint(mouse) else DARK, r, border_radius=6)
        pygame.draw.rect(s, YELLOW if active else (80, 80, 100), r, 2 if active else 1, border_radius=6)
        val = tag_name(self.cls_ftag, i18n.LANG) if active else i18n.L("All tags", "Todas as tags")
        self.text(f"{i18n.L('Highlight tag', 'Destacar tag')}: {val}", "small", WHITE if active else GREY,
                  (r.x + 12, r.centery), "midleft")
        cy = r.centery
        col = YELLOW if (active or self.cls_dd) else GREY
        if self.cls_dd:
            pygame.draw.polygon(s, col, [(r.right - 22, cy + 4), (r.right - 10, cy + 4), (r.right - 16, cy - 4)])
        else:
            pygame.draw.polygon(s, col, [(r.right - 22, cy - 4), (r.right - 10, cy - 4), (r.right - 16, cy + 4)])

    def draw_cls_dropdown(self):
        s = self.screen
        rects = self.cls_dd_rects()
        panel = pygame.Rect(648, 76, 604, max(r.bottom for _, _, r in rects) - 76 + 8)
        shadow = pygame.Surface(panel.inflate(12, 12).size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        s.blit(shadow, panel.inflate(12, 12).move(4, 4))
        pygame.draw.rect(s, (34, 34, 46), panel, border_radius=8)
        pygame.draw.rect(s, YELLOW, panel, 2, border_radius=8)
        for i, v, r in rects:
            if i == self.cls_dd_sel:
                pygame.draw.rect(s, (70, 70, 100), r, border_radius=5)
            if v == self.cls_ftag:
                pygame.draw.rect(s, GREEN, r, 1, border_radius=5)
            label = tag_name(v, i18n.LANG) if v else i18n.L("All tags (no highlight)", "Todas (sem destaque)")
            self.text(label, "small", YELLOW if v is None else WHITE, (r.x + 10, r.centery), "midleft")

    def classes_event(self, ev):
        if self.mastery_prompt:
            return self.mastery_prompt_event(ev)
        rects = self.class_layout()
        if self.cls_dd:
            return self.cls_dd_event(ev)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_t:
            vals = self.cls_tag_values()
            self.cls_dd = True
            self.cls_dd_sel = vals.index(self.cls_ftag) if self.cls_ftag in vals else 0
            return True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3) and self.cls_filter_rect().collidepoint(ev.pos):
            if ev.button == 3:
                self.cls_ftag = None
            else:
                vals = self.cls_tag_values()
                self.cls_dd = True
                self.cls_dd_sel = vals.index(self.cls_ftag) if self.cls_ftag in vals else 0
            return True
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            moves = {pygame.K_UP: "up", pygame.K_w: "up", pygame.K_DOWN: "down", pygame.K_s: "down",
                     pygame.K_LEFT: "left", pygame.K_a: "left", pygame.K_RIGHT: "right", pygame.K_d: "right"}
            if k in moves:
                self.class_move(moves[k])
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.class_choose()
            elif k == pygame.K_l:
                self.class_open_loadout()
            elif k == pygame.K_p:
                self.open_levels()
            elif k == pygame.K_ESCAPE:
                self.go("party")
        elif ev.type == pygame.MOUSEMOTION:
            for cid, r in rects.items():
                if r.collidepoint(ev.pos):
                    self.class_cursor = cid
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.lo_back_rect().collidepoint(ev.pos):   # voltar para a party (igual ao ESC)
                self.go("party")
                return True
            if self.class_select_rect().collidepoint(ev.pos):
                self.class_choose()
                return True
            if self.class_loadout_rect().collidepoint(ev.pos):
                self.class_open_loadout()
                return True
            if self.class_levels_rect().collidepoint(ev.pos):
                self.open_levels()
                return True
            for cid, r in rects.items():
                if r.collidepoint(ev.pos):
                    if self.class_cursor == cid:
                        self.class_choose()
                    self.class_cursor = cid
        return True

    def class_box(self, cid, r, m, compact=False):
        s = self.screen
        c = CLASSES[cid]
        unlocked = m.is_unlocked(cid)
        current = cid == m.cls
        cursor = cid == self.class_cursor
        pygame.draw.rect(s, (60, 60, 85) if cursor else DARK if unlocked else (26, 26, 32), r, border_radius=7)
        border = YELLOW if cursor else c["color"] if current else (GREY if unlocked else (55, 55, 65))
        pygame.draw.rect(s, border, r, 3 if (cursor or current) else 1, border_radius=7)
        name_col = c["color"] if unlocked else (90, 90, 100)
        lv = m.class_level(cid)
        if unlocked:
            sub = (f"CURRENT Lv {lv}" if current else f"Lv {lv}" if lv else "new")
            mastered = lv >= prog.mastery_level(cid)
            sub_col = GREEN if current else GREY
        else:
            sub, sub_col = "locked", (85, 85, 95)
        isz = r.h - 8 if compact else min(34, r.h - 12)
        ic = si.class_icon(cid, isz)
        if not unlocked:
            ic = ic.copy()
            ic.set_alpha(80)
        s.blit(ic, ic.get_rect(midleft=(r.x + 5, r.centery)))
        sw = self.fonts["small"].size(tr(sub))[0]
        star = unlocked and mastered
        if compact:
            nx = r.x + isz + 11
            right = r.right - (22 if star else 9)
            full = self.fonts["small"].size(tr(c["name"]))[0]
            show_sub = unlocked or full <= right - sw - 6 - nx   # bloqueada e sem espaço: só o nome (já apagado)
            self.text(self.fit(c["name"], "small", (right - sw - 6 if show_sub else right) - nx), "small", name_col,
                      (nx, r.centery), "midleft")
            if show_sub:
                self.text(sub, "small", sub_col, (right, r.centery), "midright")
            if star:
                draw_star(s, (r.right - 13, r.centery), 7, YELLOW)
        else:
            cx = r.centerx + (isz + 4) / 2
            self.text(c["name"], "small", name_col, (cx, r.y + r.h * 0.33), "center")
            self.text(sub, "small", sub_col, (cx - (7 if star else 0), r.y + r.h * 0.72), "center")
            if star:
                draw_star(s, (cx - 7 + sw / 2 + 10, r.y + r.h * 0.72), 7, YELLOW)
        if self.cls_ftag:   # filtro por tag: destaca quem tem a tag e apaga o resto
            if self.class_has_tag(cid):
                pygame.draw.rect(s, (90, 230, 255), r.inflate(6, 6), 3, border_radius=9)
            else:
                shade = pygame.Surface(r.size, pygame.SRCALPHA)
                shade.fill((10, 10, 16, 150))
                s.blit(shade, r.topleft)

    def draw_classes(self):
        s = self.screen
        self.menu_bg()
        m = self.party_member
        self.tip_member = m
        rects = self.class_layout()
        self.text(f"CLASSES - {m.name}", "big", YELLOW, (24, 24))
        back = self.lo_back_rect()
        self.button(back, "Back", back.collidepoint(self.mouse_pos()))
        self.draw_cls_filter(self.mouse_pos())

        # cabeçalhos das colunas
        hy = self.TREE_TOP - 22
        self.text("Starting", "small", GREY, (rects["freelancer"].centerx, hy), "center")
        self.text(i18n.L("Basic (Novice Lv 10)", "Básicas (Novato Nv 10)"), "small", GREY, (self.BASIC_X + self.BASIC_W / 2, hy), "center")
        self.text("Advanced (pick 1 of 2, Lv 25)", "small", GREY, (self.ADV_X + self.ADV_W / 2 - 20, hy),
                  "center")

        cur = CLASSES[self.class_cursor]
        if cur["tier"] == 2:       # destaca o caminho: básica -> esta avançada
            focus = {self.class_cursor, cur["parent"]}
        elif cur["tier"] == 1:     # destaca as duas opções de evolução
            focus = {self.class_cursor, *ADVANCED[self.class_cursor]}
        else:
            focus = {self.class_cursor}
        dim = (62, 62, 80)

        # linhas Freelancer -> básicas
        fr = rects["freelancer"]
        trunk_x = fr.right + 18
        pygame.draw.line(s, dim, fr.midright, (trunk_x, fr.centery), 2)
        tops = [rects[b].centery for b in BASIC_ORDER]
        pygame.draw.line(s, dim, (trunk_x, min(tops)), (trunk_x, max(tops)), 2)
        for b in BASIC_ORDER:
            br = rects[b]
            col = CLASSES[b]["color"] if b in focus else dim
            pygame.draw.line(s, col, (trunk_x, br.centery), br.midleft, 2)

        # bifurcações básica -> (avançada A  OU  avançada B)
        for b in BASIC_ORDER:
            br = rects[b]
            a1, a2 = ADVANCED[b]
            r1, r2 = rects[a1], rects[a2]
            fx = self.FORK_X
            pygame.draw.line(s, dim, br.midright, (fx, br.centery), 2)
            for a, r in ((a1, r1), (a2, r2)):
                col = CLASSES[a]["color"] if a in focus else dim
                w = 3 if a in focus else 2
                pygame.draw.line(s, col, (fx, br.centery), (fx, r.centery), w)
                pygame.draw.line(s, col, (fx, r.centery), r.midleft, w)
            pill = pygame.Rect(0, 0, 26, 16)
            pill.center = (fx, br.centery)
            pygame.draw.rect(s, PANEL, pill, border_radius=8)
            pygame.draw.rect(s, (90, 90, 110), pill, 1, border_radius=8)
            self.text("or", "small", WHITE, pill.center, "center")

        # Novice -> Freelancer -> Warfarer
        for a, b in (("freelancer", "freelancer_t2"), ("freelancer_t2", "warfarer")):
            col = CLASSES[b]["color"] if b in focus or a in focus else dim
            pygame.draw.line(s, col, rects[a].midbottom, rects[b].midtop, 2)
        for cid, r in rects.items():
            self.class_box(cid, r, m, compact=CLASSES[cid]["tier"] == 2)

        # painel de descrição
        cid = self.class_cursor
        c = CLASSES[cid]
        panel = pygame.Rect(650, 84, W - 680, H - 124)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        x = panel.x + 24
        draw_class_icon(s, cid, (x + 22, panel.y + 52), 20)
        self.text(c["name"], "big", c["color"], (x + 62, panel.y + 18))
        name_w = self.fonts["big"].size(c["name"])[0]
        s.blit(si.class_icon(cid, 44), (x + 74 + name_w, panel.y + 12))
        self.text(f"{TIER_NAMES[c['tier']]}  ·  {c['weapon']}  ·  Attribute: {ATTR_NAMES[c['attr']]}", "small",
                  GREY, (x, panel.y + 80))
        # textos com altura variável: história, tags e caminho de evolução quebram em quantas linhas precisarem
        y = panel.y + 100
        for ln in self.wrap(c.get("lore") or c["role"], "small", panel.w - 48):
            self.text(ln, "small", WHITE, (x, y))
            y += 18
        y += 4
        ctags = class_tags(cid, prog.CONTENT)
        tag_txt = tr("Skill tags:") + " " + tag_list_text(ctags, i18n.LANG)
        for ln in self.wrap(tag_txt, "small", panel.w - 48):
            self.text(ln, "small", (150, 190, 255), (x, y))
            y += 18
        # role: nome + scaling numa linha; o comportamento aparece ao passar o mouse
        rl = role_of(cid)
        mods = [f"{i18n.L('HP', 'Vida')} x{rl['hp']:g}",
                f"{i18n.L('Def', 'Def')} x{rl['defense']:g}",
                f"{i18n.L('Atk', 'Atq')} x{rl['attack']:g}",
                f"{i18n.L('Spd', 'Vel')} x{rl['speed']:g}",
                tr("Melee") if not c["ranged"] else tr("Ranged")]
        role_txt = f"Role: {role_name(cid, i18n.LANG)}"
        self.text(role_txt, "small", YELLOW, (x, y + 2))
        rw = self.fonts["small"].size(role_txt)[0]
        self.text("  ·  " + "  ·  ".join(mods), "small", GREY, (x + rw, y + 2))
        role_rect = pygame.Rect(x, y, panel.w - 48, 20)
        y += 26

        # caminho de evolução
        if c["tier"] == 0:
            path = "Evolves into any basic class at Lv 10  ·  into Freelancer when all basic classes are mastered"
        elif c["tier"] == 3:
            path = "Evolved Novice  ·  into Warfarer when all advanced classes are mastered"
        elif c["tier"] == 4:
            path = "Ultimate evolution of the Novice"
        elif c["tier"] == 1:
            a1, a2 = ADVANCED[cid]
            path = f"Evolves at Lv 25 into:  {tr(CLASSES[a1]['name'])}  OR  {tr(CLASSES[a2]['name'])}"
        else:
            sib = [a for a in ADVANCED[c["parent"]] if a != cid][0]
            path = f"Evolution of {tr(CLASSES[c['parent']]['name'])}  ·  alternative: {tr(CLASSES[sib]['name'])}"
        for ln in self.wrap(path, "small", panel.w - 48):
            self.text(ln, "small", YELLOW, (x, y))
            y += 18

        unlocked = m.is_unlocked(cid)
        y += 6
        if not unlocked:
            self.text(m.unlock_requirement(cid), "normal", RED, (x, y))
        else:
            lv = m.class_level(cid)
            ml = prog.mastery_level(cid)
            self.text(f"Class level: {max(1, lv)} / {prog.max_level(cid)}" +
                      ("   ·   MASTERED" if lv >= ml else f"   ·   mastery at Lv {ml}"),
                      "normal", GREEN, (x, y))

        cc = prog.CONTENT[cid]
        lv_have = m.effective_class_level(cid)

        y += 36
        col2 = x + 300
        self.text("Actives (10)", "normal", YELLOW, (x, y))
        self.text("Passives (10)", "normal", YELLOW, (col2, y))
        row_h = max(18, min(22, (self.class_select_rect().y - 8 - (y + 26)) // 10))
        for k, sp in enumerate(cc["actives"][:10]):
            ok = lv_have >= sp["unlock"]
            ry = y + 26 + k * row_h
            el_col = element_color(sp.get("element") or (sp.get("cycle") or [None])[0], WHITE)
            if self.skill_has_tag(sp):
                self.tag_mark(pygame.Rect(x - 6, ry - 3, col2 - x - 6, row_h))
            self.text(f"Lv {sp['unlock']:>2}", "small", GREEN if ok else (90, 90, 100), (x, ry))
            self.skill_icon(sp, "active", 18, (x + 56, ry + 7), dim=not ok, hover=(x + 46, ry - 2, col2 - x - 56, 21))
            self.text(self.fit(sp["name"], "small", col2 - x - 80), "small", el_col if ok else (110, 110, 120),
                      (x + 70, ry))
        for k, p in enumerate(cc["passives"][:10]):
            ok = lv_have >= p["unlock"]
            ry = y + 26 + k * row_h
            if self.skill_has_tag(p):
                self.tag_mark(pygame.Rect(col2 - 6, ry - 3, panel.right - col2 - 12, row_h))
            self.text(f"Lv {p['unlock']:>2}", "small", GREEN if ok else (90, 90, 100), (col2, ry))
            self.skill_icon(p, "passive", 18, (col2 + 56, ry + 7), dim=not ok, hover=(col2 + 46, ry - 2, 240, 21))
            capc = (250, 210, 70) if p.get("capstone") else WHITE
            pname = tr(p["name"])
            if pname.endswith("]") and " [" in pname:   # a lista já é da classe: sem o "[Classe]" no fim
                pname = pname[:pname.rindex(" [")]
            self.text(self.fit(pname + ("  (Capstone)" if p.get("capstone") else ""), "small",
                               panel.right - col2 - 82), "small", capc if ok else (110, 110, 120), (col2 + 70, ry))

        sel_r = self.class_select_rect()
        can = unlocked and cid != m.cls
        self.button(sel_r, "Select class" if cid != m.cls else "Current class",
                    sel_r.collidepoint(self.mouse_pos()), GREEN, enabled=can)
        lo_r = self.class_loadout_rect()
        self.button(lo_r, "Build loadout", lo_r.collidepoint(self.mouse_pos()), YELLOW, enabled=unlocked)
        pv_r = self.class_levels_rect()
        self.button(pv_r, "Progression", pv_r.collidepoint(self.mouse_pos()), WHITE)
        if self.cls_dd:
            self.draw_cls_dropdown()
        if self.mastery_prompt:
            self.draw_mastery_prompt()
        self.text("Arrows navigate  ·  ENTER / double-click select  ·  L loadout  ·  P level progression  ·  "
                  "T tag highlight  ·  ESC back", "small", GREY, (W / 2, H - 12), "midbottom")
        if role_rect.collidepoint(self.mouse_pos()) and not self.cls_dd:
            tip = [(f"Role: {role_name(cid, i18n.LANG)}", YELLOW),
                   (rl.get("desc") if i18n.LANG == "pt" else rl.get("desc_en", rl.get("desc", "")), WHITE),
                   (i18n.L(f"HP x{rl['hp']:g} · Defense x{rl['defense']:g} (armor, magic defense and "
                           f"{(rl['defense'] - 1) * 50:+.0f}% damage reduction) · Attack x{rl['attack']:g} "
                           f"(character damage) · Speed x{rl['speed']:g}",
                           f"Vida x{rl['hp']:g} · Defesa x{rl['defense']:g} (armadura, defesa mágica e "
                           f"{(rl['defense'] - 1) * 50:+.0f}% de redução de dano) · Ataque x{rl['attack']:g} "
                           f"(dano do personagem) · Velocidade x{rl['speed']:g}"), GREY)]
            self.draw_tooltip(tip, self.mouse_pos())
        self.draw_toast()

    # ================================================================
    # loadout (por classe)
    # ================================================================
    LO_ROWS = ([("basic", None, 0)] + [("active", "class", i) for i in range(4)] +
               [("active", "extra", i) for i in range(2)] + [("passive", "class", i) for i in range(5)] +
               [("passive", "extra", i) for i in range(5)])
    LO_VISIBLE = 13
    lo_fclass = None   # filtro por classe masterizada (slots de maestria)
    lo_ftag = None     # filtro por tag
    lo_dd = None       # dropdown aberto: None, "class" ou "tag"
    lo_dd_sel = 0
    DD_COLS, DD_COL_W, DD_ROW_H = 3, 198, 28

    def open_loadout(self, cid, back):
        self.lo_cid = cid
        self.lo_back = back
        self.lo_sel, self.lo_focus, self.lo_list_sel, self.lo_scroll = 1, "slots", 0, 0
        self.lo_fclass, self.lo_ftag = None, None   # filtros (classe masterizada / tag) dos slots de maestria
        self.lo_dd = None
        self.go("loadout")

    def lo_slot_rects(self):
        rects = []
        for i, (kind, group, idx) in enumerate(self.LO_ROWS):
            if kind in ("basic", "active"):
                rects.append(pygame.Rect(24, 122 + i * 34, 596, 30))
            else:
                rects.append(pygame.Rect(24, 400 + (i - 7) * 29, 596, 26))
        return rects

    def lo_filtered(self):
        """Ativas e passivas têm filtro por tag; os slots de maestria também têm o filtro por classe masterizada."""
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        return kind != "basic"

    def lo_class_filter(self):
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        return kind != "basic" and group == "extra"

    def lo_raw_options(self):
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        if kind == "basic":
            return []
        return self.party_member.slot_options(kind, group, self.lo_cid, idx)

    def lo_filter_classes(self):
        out = []
        for ref, sp, ok in self.lo_raw_options():
            c = prog.parse_ref(ref)[0]
            if c not in out:
                out.append(c)
        return [None] + out

    def lo_filter_tags(self):
        seen = set()
        for ref, sp, ok in self.lo_raw_options():
            if self.lo_fclass and prog.parse_ref(ref)[0] != self.lo_fclass:
                continue
            seen.update(sp.get("tags") or [])
        return [None] + [t for t in TAG_ORDER if t in seen]

    def lo_fix_filters(self):
        if self.lo_fclass not in self.lo_filter_classes():
            self.lo_fclass = None
        if self.lo_ftag not in self.lo_filter_tags():
            self.lo_ftag = None

    def lo_options(self):
        """Opções do slot selecionado: [(ref ou None, spec, liberada?)]."""
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        if kind == "basic":
            return []
        opts = self.lo_raw_options()
        if self.lo_filtered():
            self.lo_fix_filters()
            opts = [o for o in opts if (not self.lo_fclass or prog.parse_ref(o[0])[0] == self.lo_fclass)
                    and (not self.lo_ftag or self.lo_ftag in (o[1].get("tags") or []))]
        return [(None, None, True)] + opts

    def lo_list_top(self):
        return 160 if self.lo_filtered() else 122

    def lo_visible(self):
        return 12 if self.lo_filtered() else self.LO_VISIBLE

    def lo_filter_rects(self):
        if not self.lo_class_filter():   # slots da própria classe: só o filtro de tag (o de classe fica fora da tela)
            return pygame.Rect(-1000, -1000, 1, 1), pygame.Rect(650, 122, 600, 28)
        return pygame.Rect(650, 122, 296, 28), pygame.Rect(954, 122, 296, 28)

    def lo_cycle_filter(self, which, step):
        if which == "class":
            vals = self.lo_filter_classes()
            cur = self.lo_fclass if self.lo_fclass in vals else None
            self.lo_fclass = vals[(vals.index(cur) + step) % len(vals)]
        else:
            vals = self.lo_filter_tags()
            cur = self.lo_ftag if self.lo_ftag in vals else None
            self.lo_ftag = vals[(vals.index(cur) + step) % len(vals)]
        self.lo_fix_filters()
        self.lo_list_sel, self.lo_scroll = 0, 0

    # ---- dropdown dos filtros ----
    def lo_dd_values(self, which=None):
        which = which or self.lo_dd
        return self.lo_filter_classes() if which == "class" else self.lo_filter_tags()

    def lo_dd_label(self, which, v):
        if v is None:
            return i18n.L("All classes", "Todas as classes") if which == "class" else i18n.L("All tags", "Todas as tags")
        return CLASSES[v]["name"] if which == "class" else tag_name(v, i18n.LANG)

    def lo_dd_rects(self):
        vals = self.lo_dd_values()
        rows = -(-len(vals) // self.DD_COLS)
        out = []
        for i, v in enumerate(vals):
            col, row = i // rows, i % rows   # preenche por coluna (ordem de leitura de cima para baixo)
            out.append((i, v, pygame.Rect(656 + col * self.DD_COL_W, 162 + row * self.DD_ROW_H, self.DD_COL_W - 8,
                                          self.DD_ROW_H - 3)))
        return out

    def lo_dd_panel(self):
        rects = [r for _, _, r in self.lo_dd_rects()]
        if not rects:
            return pygame.Rect(650, 156, 600, 40)
        return pygame.Rect(648, 154, 604, max(r.bottom for r in rects) - 154 + 8)

    def lo_open_dd(self, which):
        if self.lo_dd == which:
            self.lo_dd = None
            return
        self.lo_dd = which
        vals = self.lo_dd_values()
        cur = self.lo_fclass if which == "class" else self.lo_ftag
        self.lo_dd_sel = vals.index(cur) if cur in vals else 0

    def lo_dd_pick(self, i):
        vals = self.lo_dd_values()
        if 0 <= i < len(vals):
            if self.lo_dd == "class":
                self.lo_fclass = vals[i]
            else:
                self.lo_ftag = vals[i]
            self.lo_fix_filters()
            self.lo_list_sel, self.lo_scroll = 0, 0
            self.lo_focus = "list"
        self.lo_dd = None

    def lo_dd_event(self, ev):
        """Eventos com o dropdown aberto (ele captura tudo até fechar)."""
        vals = self.lo_dd_values()
        n = len(vals)
        rows = max(1, -(-n // self.DD_COLS))
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.lo_dd = None
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.lo_dd_pick(self.lo_dd_sel)
            elif k in (pygame.K_UP, pygame.K_DOWN):
                self.lo_dd_sel = (self.lo_dd_sel + (1 if k == pygame.K_DOWN else -1)) % n
            elif k in (pygame.K_LEFT, pygame.K_RIGHT):
                j = self.lo_dd_sel + (rows if k == pygame.K_RIGHT else -rows)
                if 0 <= j < n:
                    self.lo_dd_sel = j
            elif k == pygame.K_TAB:
                self.lo_open_dd("tag" if self.lo_dd == "class" else "class")
            elif ev.unicode and ev.unicode.isalpha():
                # digitar uma letra pula para o próximo item que começa com ela
                ch = ev.unicode.lower()
                for step in range(1, n + 1):
                    j = (self.lo_dd_sel + step) % n
                    if vals[j] is not None and self.lo_dd_label(self.lo_dd, vals[j]).lower().startswith(ch):
                        self.lo_dd_sel = j
                        break
        elif ev.type == pygame.MOUSEMOTION:
            for i, v, r in self.lo_dd_rects():
                if r.collidepoint(ev.pos):
                    self.lo_dd_sel = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            for i, v, r in self.lo_dd_rects():
                if r.collidepoint(ev.pos):
                    self.lo_dd_pick(i)
                    return True
            for which, r in zip(("class", "tag"), self.lo_filter_rects()):
                if r.collidepoint(ev.pos):
                    self.lo_open_dd(which)
                    return True
            self.lo_dd = None
        return True

    def draw_lo_dropdown(self, mouse):
        s = self.screen
        which = self.lo_dd
        panel = self.lo_dd_panel()
        shadow = pygame.Surface(panel.inflate(12, 12).size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        s.blit(shadow, panel.inflate(12, 12).move(4, 4))
        pygame.draw.rect(s, (34, 34, 46), panel, border_radius=8)
        pygame.draw.rect(s, YELLOW, panel, 2, border_radius=8)
        cur = self.lo_fclass if which == "class" else self.lo_ftag
        for i, v, r in self.lo_dd_rects():
            hot = i == self.lo_dd_sel
            if hot:
                pygame.draw.rect(s, (70, 70, 100), r, border_radius=5)
            if v == cur:
                pygame.draw.rect(s, GREEN, r, 1, border_radius=5)
            label = self.lo_dd_label(which, v)
            if which == "class" and v:
                draw_class_icon(s, v, (r.x + 13, r.centery + 2), 8)
                col = CLASSES[v]["color"]
            else:
                col = YELLOW if v is None else WHITE
            self.text(label, "small", col, (r.x + 32, r.centery), "midleft")

    def lo_option_rects(self):
        opts = self.lo_options()
        rects = []
        top = self.lo_list_top()
        for vis in range(self.lo_visible()):
            i = self.lo_scroll + vis
            if i < len(opts):
                rects.append((i, pygame.Rect(650, top + vis * 31, 600, 28)))
        return rects

    def lo_keep_visible(self):
        n = len(self.lo_options())
        self.lo_list_sel = max(0, min(self.lo_list_sel, n - 1))
        if self.lo_list_sel < self.lo_scroll:
            self.lo_scroll = self.lo_list_sel
        elif self.lo_list_sel >= self.lo_scroll + self.lo_visible():
            self.lo_scroll = self.lo_list_sel - self.lo_visible() + 1

    def lo_select_slot(self, i):
        self.lo_sel = i
        self.lo_list_sel, self.lo_scroll = 0, 0
        kind, group, idx = self.LO_ROWS[i]
        if kind != "basic":
            cur = self.party_member.slots(kind, group, self.lo_cid)[idx]
            for j, (r, _, _) in enumerate(self.lo_options()):
                if r == cur:
                    self.lo_list_sel = j
            self.lo_keep_visible()

    def lo_equip(self, j):
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        if kind == "basic":
            self.toast("Slot 1 is always the class weapon's basic attack.")
            return
        opts = self.lo_options()
        if not (0 <= j < len(opts)):
            return
        m = self.party_member
        err = m.equip(kind, group, idx, opts[j][0], self.lo_cid)
        if err:
            self.toast(err)
        else:
            self.roster.save()
            self.lo_focus = "slots"

    def lo_clear(self):
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        if kind != "basic":
            self.party_member.equip(kind, group, idx, None, self.lo_cid)
            self.roster.save()

    def loadout_event(self, ev):
        if self.lo_dd and self.lo_filtered():
            return self.lo_dd_event(ev)
        self.lo_dd = None
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_c, pygame.K_t) and self.lo_filtered():
            if ev.key == pygame.K_t or self.lo_class_filter():
                self.lo_open_dd("class" if ev.key == pygame.K_c else "tag")
                return True
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if self.lo_focus == "slots":
                if k in (pygame.K_UP, pygame.K_w):
                    self.lo_select_slot((self.lo_sel - 1) % len(self.LO_ROWS))
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.lo_select_slot((self.lo_sel + 1) % len(self.LO_ROWS))
                elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_d):
                    if self.LO_ROWS[self.lo_sel][0] != "basic":
                        self.lo_focus = "list"
                elif k in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    self.lo_clear()
                elif k == pygame.K_ESCAPE:
                    self.go(self.lo_back)
            else:
                n = len(self.lo_options())
                if k in (pygame.K_UP, pygame.K_w):
                    self.lo_list_sel = (self.lo_list_sel - 1) % n
                    self.lo_keep_visible()
                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.lo_list_sel = (self.lo_list_sel + 1) % n
                    self.lo_keep_visible()
                elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.lo_equip(self.lo_list_sel)
                elif k in (pygame.K_ESCAPE, pygame.K_LEFT, pygame.K_a):
                    self.lo_focus = "slots"
        elif ev.type == pygame.MOUSEWHEEL:
            if self.lo_filtered():
                for which, r in zip(("class", "tag"), self.lo_filter_rects()):
                    if r.collidepoint(self.mouse_pos()):
                        self.lo_cycle_filter(which, -1 if ev.y > 0 else 1)
                        return True
            n = len(self.lo_options())
            self.lo_scroll = max(0, min(self.lo_scroll - ev.y, max(0, n - self.lo_visible())))
        elif ev.type == pygame.MOUSEMOTION:
            for j, r in self.lo_option_rects():
                if r.collidepoint(ev.pos):
                    self.lo_list_sel = j
                    self.lo_focus = "list"
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            if self.lo_back_rect().collidepoint(ev.pos):
                self.go(self.lo_back)
                return True
            for i, r in enumerate(self.lo_slot_rects()):
                if r.collidepoint(ev.pos):
                    self.lo_select_slot(i)
                    if ev.button == 3:
                        self.lo_clear()
                    return True
            if self.lo_filtered():
                for which, r in zip(("class", "tag"), self.lo_filter_rects()):
                    if r.collidepoint(ev.pos):
                        if ev.button == 3:   # botão direito limpa o filtro
                            if which == "class":
                                self.lo_fclass = None
                            else:
                                self.lo_ftag = None
                            self.lo_fix_filters()
                            self.lo_list_sel, self.lo_scroll = 0, 0
                        else:
                            self.lo_open_dd(which)
                        return True
            if ev.button == 1:
                for j, r in self.lo_option_rects():
                    if r.collidepoint(ev.pos):
                        self.lo_equip(j)
        return True

    def draw_lo_filters(self, mouse):
        """Dois seletores: classe masterizada e tag (clique: esquerda volta, direita avança; roda do mouse)."""
        s = self.screen
        lang = i18n.LANG
        vals = (CLASSES[self.lo_fclass]["name"] if self.lo_fclass else i18n.L("All classes", "Todas as classes"),
                tag_name(self.lo_ftag, lang) if self.lo_ftag else i18n.L("All tags", "Todas as tags"))
        labels = (i18n.L("Class", "Classe"), "Tag")
        for r, lab, val, active in zip(self.lo_filter_rects(), labels, vals, (self.lo_fclass, self.lo_ftag)):
            if r.x < 0:   # filtro de classe só nos slots de maestria
                continue
            hot = r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if hot else DARK, r, border_radius=6)
            pygame.draw.rect(s, YELLOW if active else (80, 80, 100), r, 2 if active else 1, border_radius=6)
            col = YELLOW if active else GREY
            cy = r.centery
            opened = self.lo_dd == ("class" if lab != "Tag" else "tag")
            if opened:
                pygame.draw.polygon(s, YELLOW, [(r.right - 22, cy + 4), (r.right - 10, cy + 4), (r.right - 16, cy - 4)])
            else:
                pygame.draw.polygon(s, col, [(r.right - 22, cy - 4), (r.right - 10, cy - 4), (r.right - 16, cy + 4)])
            self.text(f"{lab}: {val}", "small", WHITE if active else GREY, (r.x + 12, cy), "midleft")

    def lo_back_rect(self):
        return pygame.Rect(W - 170, 24, 140, 44)

    def skill_line(self, sp, kind):
        """Resumo técnico de uma habilidade para o painel de detalhes."""
        if kind == "passive":
            txt = effects_text(sp.get("effects") or {sp["effect"]: sp["value"]}, i18n.LANG)
            return ("CAPSTONE  ·  " if sp.get("capstone") else "") + txt
        parts = [prog.ARCH_NAME.get(sp["kind"], sp["kind"])]
        if sp.get("cycle"):
            parts.append("/".join(ELEMENTS[e]["name"] for e in sp["cycle"]))
        elif sp.get("element") in ELEMENTS:
            parts.append(ELEMENTS[sp["element"]]["name"])
        if sp["kind"] == "heal":
            parts.append(f"heal {sp.get('amount')}")
        elif sp["kind"] != "buff":
            parts.append(f"{'physical' if sp.get('dmgtype') == 'phys' else 'magical'} {sp.get('dmg')}")
        parts.append(f"cooldown {sp.get('cd')}s")
        return "  ·  ".join(str(p) for p in parts)

    def draw_loadout(self):
        s = self.screen
        self.menu_bg()
        m = self.party_member
        self.tip_member = m
        cid = self.lo_cid
        c = CLASSES[cid]
        mouse = self.mouse_pos()
        self.text(f"LOADOUT - {m.name}", "big", YELLOW, (24, 22))
        cur = " (current class)" if cid == m.cls else ""
        self.text(f"{tr(c['name'])} Lv {max(1, m.class_level(cid))}{cur}  ·  saved for this class", "normal", c["color"],
                  (26, 72))
        self.button(self.lo_back_rect(), "Back", self.lo_back_rect().collidepoint(mouse))

        # ---- slots ----
        self.text("ACTIVES", "small", YELLOW, (24, 104))
        self.text("PASSIVES", "small", YELLOW, (24, 382))
        mastered = [CLASSES[x]["name"] for x in m.mastered_classes() if x != cid]
        for i, ((kind, group, idx), r) in enumerate(zip(self.LO_ROWS, self.lo_slot_rects())):
            sel = i == self.lo_sel
            pygame.draw.rect(s, (60, 60, 85) if sel else DARK, r, border_radius=6)
            if sel:
                pygame.draw.rect(s, YELLOW if self.lo_focus == "slots" else GREY, r, 2, border_radius=6)
            num = i + 1 if kind in ("basic", "active") else i - 6
            if kind == "basic":
                tag, tcol = "Basic attack", GREY
                sp = prog.CONTENT[cid]["basic"]
                name, ncol = f"{sp['name']}  (fixed)", WHITE
            else:
                tag, tcol = ("Class", c["color"]) if group == "class" else ("Mastery", (200, 140, 255))
                if kind == "passive" and idx == 4:
                    tag, tcol = ("Capstone", (250, 210, 70)) if group == "class" else ("Capstone (M)", (250, 210, 70))
                ref = m.slots(kind, group, cid)[idx]
                sp = (prog.get_active(ref) if kind == "active" else prog.get_passive(ref)) if ref else None
                if sp:
                    src_cls = CLASSES[prog.parse_ref(ref)[0]]["name"]
                    name = sp["name"] + (f"   [{src_cls}]" if group == "extra" and not sp["name"].endswith("]") else "")
                    ncol = WHITE
                else:
                    name, ncol = "(empty)", (100, 100, 112)
            self.text(f"{num:>2}", "small", GREY, (r.x + 10, r.centery), "midleft")
            self.text(tag, "small", tcol, (r.x + 40, r.centery), "midleft")
            if sp:
                self.skill_icon(sp, "passive" if kind == "passive" else "active", r.h - 6, (r.x + 152, r.centery),
                                hover=r)
            self.text(name[:50], "small", ncol, (r.x + 172, r.centery), "midleft")

        # ---- opções do slot selecionado ----
        kind, group, idx = self.LO_ROWS[self.lo_sel]
        panel = pygame.Rect(640, 84, 620, 600)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        x = panel.x + 10
        if kind == "basic":
            sp = prog.CONTENT[cid]["basic"]
            self.text("Slot 1 - weapon basic attack (fixed)", "normal", YELLOW, (x + 10, panel.y + 14))
            self.skill_icon(sp, "active", 56, (x + 38, panel.y + 86))
            self.text(sp["name"], "normal", WHITE, (x + 78, panel.y + 60))
            self.text(self.skill_line(sp, "active"), "small", GREY, (x + 78, panel.y + 88))
            self.text(sp["desc"], "small", GREY, (x + 78, panel.y + 110))
        else:
            what = "active" if kind == "active" else "passive"
            if group == "class":
                head = f"Choose a {what} from {tr(c['name'])}"
            else:
                head = f"Choose a {what} from a mastered class"
            self.text(head, "normal", YELLOW, (x + 10, panel.y + 12))
            opts = self.lo_options()
            if self.lo_filtered() and self.lo_raw_options():
                self.draw_lo_filters(mouse)
                if len(opts) == 1:
                    self.text("No skill matches these filters.", "small", GREY, (x + 10, self.lo_list_top() + 40))
            elif group == "extra" and len(opts) == 1:
                self.text("No other mastered class yet.", "small", GREY, (x + 10, panel.y + 80))
                self.text(f"Bring a class to mastery (Lv {MASTERY_LEVEL}; Novice Lv "
                          f"{prog.mastery_level('freelancer')}) to unlock these slots.", "small", GREY,
                          (x + 10, panel.y + 100))
            equipped = m.slots(kind, group, cid)
            for j, r in self.lo_option_rects():
                ref, sp, ok = opts[j]
                hot = j == self.lo_list_sel
                pygame.draw.rect(s, (60, 60, 85) if hot else DARK, r, border_radius=6)
                if hot and self.lo_focus == "list":
                    pygame.draw.rect(s, YELLOW, r, 2, border_radius=6)
                if ref is None:
                    self.text("(leave empty)", "small", GREY, (r.x + 12, r.centery), "midleft")
                    continue
                col = WHITE if ok else (95, 95, 105)
                label = sp["name"]
                if group == "extra" and not label.endswith("]"):
                    label += f"   [{tr(CLASSES[prog.parse_ref(ref)[0]]['name'])}]"
                self.skill_icon(sp, kind, 22, (r.x + 18, r.centery), dim=not ok, hover=r)
                self.text(label[:46], "small", col, (r.x + 36, r.centery), "midleft")
                if ref in equipped:
                    tag, tcol = f"slot {equipped.index(ref) + 1}", GREEN
                elif not ok:
                    tag, tcol = f"Lv {sp['unlock']}", RED
                else:
                    tag, tcol = (f"Lv {sp['unlock']}" if group == "class" else ""), GREY
                self.text(tag, "small", tcol, (r.right - 12, r.centery), "midright")
            n = len(opts)
            vis_n = self.lo_visible()
            if n > vis_n:
                h = vis_n * 31
                bar_h = max(30, h * vis_n / n)
                yb = self.lo_list_top() + (h - bar_h) * self.lo_scroll / max(1, n - vis_n)
                pygame.draw.rect(s, GREY, (panel.right - 6, yb, 4, bar_h), border_radius=2)
            # detalhes da opção destacada
            if 0 <= self.lo_list_sel < n and opts[self.lo_list_sel][0]:
                ref, sp, ok = opts[self.lo_list_sel]
                dy = panel.bottom - 140
                pygame.draw.line(s, DARK, (panel.x + 14, dy - 10), (panel.right - 14, dy - 10), 2)
                self.skill_icon(sp, kind, 64, (x + 42, dy + 44))
                self.text(sp["name"], "normal", WHITE, (x + 86, dy))
                tw = panel.right - (x + 86) - 14
                ly = dy + 28
                lines = self.wrap(self.skill_line(sp, kind), "small", tw)[:3]
                if sp.get("desc") and kind == "active":   # nas passivas a linha de efeitos já descreve tudo
                    lines += self.wrap(sp["desc"], "small", tw)[:max(1, 5 - len(lines))]
                for ln in lines[:5]:
                    self.text(ln, "small", GREY, (x + 86, ly))
                    ly += 17
                req = f"Unlocks at {tr(CLASSES[prog.parse_ref(ref)[0]]['name'])} Lv {sp['unlock']}"
                self.text(req, "small", GREEN if ok else RED, (x + 86, ly))

        if self.lo_dd and kind != "basic" and self.lo_filtered():
            self.draw_lo_dropdown(mouse)
        hint = ("Arrows select slot  ·  ENTER open options  ·  DEL / right-click clear  ·  ESC back"
                if self.lo_focus == "slots" else
                ("Arrows select  ·  ENTER equip  ·  C / T open filters  ·  ESC back to slots"
                 if self.lo_class_filter() else "Arrows select  ·  ENTER equip  ·  T tag filter  ·  ESC back to slots"))
        if self.lo_dd and self.lo_filtered():
            hint = "Arrows / letter keys choose  ·  ENTER apply  ·  TAB other filter  ·  ESC close"
        self.text(hint, "small", GREY, (W / 2, H - 10), "midbottom")
        self.draw_toast()

    # ================================================================
    # progressão por nível da classe (o que cada nível libera)
    # ================================================================
    LV_ROW_H = 25
    LV_VISIBLE = 20

    def level_rows(self):
        """[(nível, [(texto, cor)])] com bônus de status e habilidades liberadas em cada nível."""
        cc = prog.CONTENT[self.lv_cid]
        rows = []
        for lv in range(1, prog.max_level(self.lv_cid) + 1):
            parts = []
            for sp in cc["actives"]:
                if sp["unlock"] == lv:
                    parts.append((f"Active: {sp['name']}", element_color(sp.get("element") or
                                                                       (sp.get("cycle") or [None])[0], WHITE),
                                  sp, "active"))
            for p in cc["passives"]:
                if p["unlock"] == lv:
                    parts.append((f"Passive: {p['name']}", (200, 140, 255), p, "passive"))
            if lv == prog.mastery_level(self.lv_cid):
                parts.append(("MASTERY: skills available to other classes", (250, 210, 70), None, None))
            if lv > prog.base_max_level(self.lv_cid):
                parts.append((i18n.L("Altar of Mastery level", "Nível do Altar da Maestria"), (120, 220, 230),
                              None, None))
            rows.append((lv, prog.level_bonus(self.lv_cid, lv), parts))
        # última linha: total de cada status somando todos os níveis da classe
        tot = {}
        for b in prog.levels_table(self.lv_cid).values():
            for k, v in b.items():
                tot[k] = tot.get(k, 0) + v
        rows.append(("total", tot, []))
        return rows

    def levels_event(self, ev):
        max_scroll = max(0, prog.max_level(self.lv_cid) + 1 - self.LV_VISIBLE)   # +1 = linha de total
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.lv_scroll = max(0, self.lv_scroll - 1)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.lv_scroll = min(max_scroll, self.lv_scroll + 1)
            elif ev.key == pygame.K_PAGEUP:
                self.lv_scroll = max(0, self.lv_scroll - self.LV_VISIBLE)
            elif ev.key == pygame.K_PAGEDOWN:
                self.lv_scroll = min(max_scroll, self.lv_scroll + self.LV_VISIBLE)
            elif ev.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN, pygame.K_BACKSPACE):
                self.go("classes")
        elif ev.type == pygame.MOUSEWHEEL:
            self.lv_scroll = max(0, min(max_scroll, self.lv_scroll - ev.y * 2))
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.lo_back_rect().collidepoint(ev.pos):
                self.go("classes")
        return True

    def draw_levels(self):
        s = self.screen
        self.menu_bg()
        m = self.party_member
        self.tip_member = m
        cid = self.lv_cid
        c = CLASSES[cid]
        cur_lv = m.effective_class_level(cid)
        mouse = self.mouse_pos()
        self.text(f"PROGRESSION - {tr(c['name'])}", "big", c["color"], (24, 22))
        status = f"{m.name}: Lv {cur_lv} / {prog.max_level(cid)}" if m.is_unlocked(cid) else \
            f"{m.name}: class locked ({m.unlock_requirement(cid)})"
        self.text(status, "normal", WHITE, (26, 72))
        self.button(self.lo_back_rect(), "Back", self.lo_back_rect().collidepoint(mouse))

        panel = pygame.Rect(24, 104, W - 48, self.LV_ROW_H * self.LV_VISIBLE + 44)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        cols = [("Level", 22)] + [(lab + ("%" if suf else ""), 70 + i * 55) for i, (_, lab, suf) in
                                  enumerate(STAT_LABELS)] + [("Unlocks", 735)]
        for name, x in cols:
            self.text(name, "small", YELLOW, (panel.x + x, panel.y + 12))
        rows = self.level_rows()
        y0 = panel.y + 38
        for vis in range(self.LV_VISIBLE):
            i = self.lv_scroll + vis
            if i >= len(rows):
                break
            lv, bonus, parts = rows[i]
            y = y0 + vis * self.LV_ROW_H
            if lv == "total":
                pygame.draw.rect(s, (70, 60, 35), (panel.x + 8, y - 3, panel.w - 16, self.LV_ROW_H - 2),
                                 border_radius=5)
                self.text("Total", "small", YELLOW, (panel.x + 22, y))
                for (key, _, _), (_, x) in zip(STAT_LABELS, cols[1:-1]):
                    v = bonus.get(key, 0)
                    self.text(f"+{fmt_num(v)}" if v else "·", "small", YELLOW if v else (70, 70, 82), (panel.x + x, y))
                self.text("Sum of every level of the class", "small", YELLOW, (panel.x + 735, y))
                continue
            reached = m.is_unlocked(cid) and lv <= cur_lv
            if lv == cur_lv and m.is_unlocked(cid):
                pygame.draw.rect(s, (60, 60, 85), (panel.x + 8, y - 3, panel.w - 16, self.LV_ROW_H - 2),
                                 border_radius=5)
            elif vis % 2:
                pygame.draw.rect(s, (34, 34, 46), (panel.x + 8, y - 3, panel.w - 16, self.LV_ROW_H - 2),
                                 border_radius=5)
            base_col = GREEN if reached else GREY
            self.text(f"{lv}", "small", base_col, (panel.x + 22, y))
            for (key, _, _), (_, x) in zip(STAT_LABELS, cols[1:-1]):
                v = bonus.get(key, 0)
                txt = f"+{fmt_num(v)}" if v else "·"
                self.text(txt, "small", (WHITE if reached else (150, 150, 160)) if v else (70, 70, 82),
                          (panel.x + x, y))
            x = panel.x + 735
            if not parts:
                self.text("—", "small", (70, 70, 82), (x, y))
            for txt, col, sp, kind in parts:
                surf = self.fonts["small"].render(tr(txt), True, col if reached else tuple(v // 2 + 40 for v in col))
                if sp is not None:
                    self.skill_icon(sp, kind, 18, (x + 9, y + 7), dim=not reached,
                                    hover=(x, y - 2, 24 + surf.get_width(), 20))
                    x += 22
                s.blit(surf, (x, y))
                x += surf.get_width() + 24
        # barra de rolagem
        h = self.LV_ROW_H * self.LV_VISIBLE
        n_lv = prog.max_level(cid) + 1
        bar_h = h * self.LV_VISIBLE / n_lv
        yb = y0 + (h - bar_h) * self.lv_scroll / max(1, n_lv - self.LV_VISIBLE)
        pygame.draw.rect(s, GREY, (panel.right - 10, yb, 4, bar_h), border_radius=2)

        # totais
        cc = prog.CONTENT[cid]
        tot = {k: 0 for k in prog.STAT_KEYS}
        got = {k: 0 for k in prog.STAT_KEYS}
        for lv, b in prog.levels_table(cid).items():
            for k in tot:
                tot[k] += b.get(k, 0)
                if m.is_unlocked(cid) and lv <= cur_lv:
                    got[k] += b.get(k, 0)
        txt = "   ".join(f"{lab} {fmt_num(got[k])}/{fmt_num(tot[k])}{suf}" for k, lab, suf in STAT_LABELS if tot[k])
        self.text(f"Permanent bonuses earned / class total:   {txt}", "small", WHITE,
                  (26, panel.bottom + 10))
        self.text("Green = level reached  ·  Arrows / mouse wheel scroll  ·  PgUp/PgDn page  ·  ESC back",
                  "small", GREY, (W / 2, H - 8), "midbottom")

    # ================================================================
    # seleção de fase
    # ================================================================
    # ================================================================
    # Seleção de fase: biomas (5 fases + Endless cada)
    # ================================================================
    TILE_W, TILE_H, TILE_GAP = 94, 68, 8
    BIOME_X, BIOME_Y, BIOME_H = 32, 88, 102   # 5 biomas + a Endless Rift embaixo

    def biome_tiles(self):
        """[(stage_id ou None, índice do bioma, posição 0..5, retângulo)] — posição 5 = Endless."""
        out = []
        for bi, b in enumerate(BIOMES):
            y = self.BIOME_Y + bi * self.BIOME_H + 24
            for k in range(6):
                r = pygame.Rect(self.BIOME_X + k * (self.TILE_W + self.TILE_GAP), y, self.TILE_W, self.TILE_H)
                if k < 5:
                    sid = b["stages"][k] if k < len(b["stages"]) else None
                else:
                    sid = ENDLESS_BASE + bi if b["stages"] else None
                out.append((sid, bi, k, r))
        return out

    def selectable_stages(self):
        return [sid for sid, _, _, _ in self.biome_tiles() if sid is not None] + [rift.RIFT_ID]

    def rift_tile_rect(self):
        return pygame.Rect(self.BIOME_X, self.BIOME_Y + len(BIOMES) * self.BIOME_H + 22,
                           6 * self.TILE_W + 5 * self.TILE_GAP, 54)

    def rift_level(self):
        """Nível escolhido da Endless Rift (padrão: o mais alto liberado)."""
        top = self.roster.rift_lv
        pick = getattr(self, "rift_pick", None)
        return max(1, min(top, pick)) if pick else top

    def rift_lv_rects(self, x, y):
        return pygame.Rect(x, y, 34, 30), pygame.Rect(x + 190, y, 34, 30)

    def rift_step(self, d):
        top = self.roster.rift_lv
        self.rift_pick = max(1, min(top, self.rift_level() + d))

    def stage_start_rect(self):
        return pygame.Rect(W - 300, H - 98, 250, 52)

    def stage_unlocked(self, i):
        return self.roster.stage_unlocked(i)

    def stage_name(self, sid):
        if sid == rift.RIFT_ID:
            return "Endless Rift"
        if is_endless(sid):
            return f"{endless_biome(sid)['name']} Endless"
        return STAGES[sid]["name"]

    def stage_lock_text(self, sid):
        if sid == rift.RIFT_ID:
            return i18n.L(f"Clear {STAGES[0]['name']} to unlock.", f"Conclua a {tr(STAGES[0]['name'])} para liberar.")
        if is_endless(sid):
            b = endless_biome(sid)
            return f"Clear {STAGES[b['stages'][-1]]['name']} to unlock."
        return f"Clear {STAGES[sid - 1]['name']} to unlock."

    def stage_pick(self, i):
        if not self.stage_unlocked(i):
            self.toast(self.stage_lock_text(i))
            return False
        self.roster.stage = i
        self.roster.save()
        if i == rift.RIFT_ID:   # explicação na primeira vez que escolhe a Endless Rift / um Endless
            self.show_tip("rift")
        elif is_endless(i):
            self.show_tip("endless")
        return True

    def stage_preview(self, sid, w, h):
        """Miniatura do cenário da fase (cache)."""
        cache = self.__dict__.setdefault("_stage_prev", {})
        key = (sid, w, h)
        if key not in cache:
            from scenery import Scenery
            idx = (0 if sid == rift.RIFT_ID else biome_of(sid)["stages"][0] if is_endless(sid) else sid)
            sc = Scenery(idx, seed=777 + idx)
            surf = pygame.Surface((w, h))
            sc.draw_ground(surf, V(1100, 700), w, h)
            sc.draw_trees(surf, V(1100, 700), w, h)
            cache[key] = surf
        return cache[key]

    def draw_rift_tile(self, mouse):
        """Faixa da Endless Rift embaixo dos biomas."""
        s = self.screen
        r = self.rift_tile_rect()
        sid = rift.RIFT_ID
        unlocked = self.stage_unlocked(sid)
        cur = self.stage_cursor == sid
        chosen = self.roster.stage == sid
        t = pygame.time.get_ticks() / 1000
        tile = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(tile, (34, 18, 52) if unlocked else (26, 24, 32), tile.get_rect(), border_radius=8)
        if unlocked:   # rasgo roxo no meio, com faíscas girando
            for k in range(5):
                rr = 1 - k * 0.17
                pygame.draw.ellipse(tile, (120 + k * 25, 50 + k * 22, 190 + k * 12, 150),
                                    (r.w / 2 - 170 * rr, r.h / 2 - 22 * rr, 340 * rr, 44 * rr))
            for i in range(10):
                a = t * 1.8 + i * math.tau / 10
                pygame.draw.circle(tile, (235, 210, 255), (r.w / 2 + math.cos(a) * 150, r.h / 2 + math.sin(a) * 19), 2)
        s.blit(tile, r)
        col = WHITE if unlocked else (110, 110, 120)
        draw_infinity(s, (r.x + 35, r.centery + 1), 40, (0, 0, 0), 5)
        draw_infinity(s, (r.x + 34, r.centery), 40, rift.COLOR if unlocked else (90, 90, 100), 4)
        self.text("ENDLESS RIFT", "normal", col, (r.centerx, r.centery - 10), "center")
        self.text(i18n.L("Monsters, bosses and scenery from every unlocked stage",
                         "Monstros, chefões e cenários de todas as fases liberadas"), "small",
                  (230, 215, 245) if unlocked else (100, 100, 110), (r.centerx, r.centery + 13), "center")
        if not unlocked:
            lk = pygame.Rect(0, 0, 16, 12)
            lk.center = (r.right - 22, r.centery + 2)
            pygame.draw.rect(s, (150, 150, 160), lk, border_radius=3)
            pygame.draw.arc(s, (150, 150, 160), (lk.x + 2, lk.y - 8, 12, 14), 0, math.pi, 2)
        else:
            self.text(i18n.L(f"Lv {self.rift_level()}", f"Nv {self.rift_level()}"), "normal", rift.COLOR,
                      (r.right - 12, r.centery), "midright")
        pygame.draw.rect(s, YELLOW if cur else GREEN if chosen else (110, 80, 150), r, 3 if (cur or chosen) else 1,
                         border_radius=8)

    def draw_rift_details(self, x, y, tw, para, mouse):
        """Painel da Endless Rift na seleção de fase."""
        s = self.screen
        L = i18n.L
        lang = i18n.LANG
        base = rift.base_stage(self.roster)

        def para(txt, col=GREY, gap=4):   # parágrafo com quebra de linha (y local deste painel)
            nonlocal y
            for ln in self.wrap(txt, "small", tw):
                self.text(ln, "small", col, (x, y))
                y += 17
            y += gap

        para(L(f"Like the Endless: no time limit, the difficulty goes up one tier every 2 minutes and a boss "
               f"appears every 2 minutes. It starts at the difficulty of the highest stage you have cleared "
               f"({base['name']}).",
               f"Como o Endless: sem limite de tempo, a dificuldade sobe um degrau a cada 2 minutos e um chefão "
               f"aparece a cada 2 minutos. Começa na dificuldade da fase mais alta que você já concluiu "
               f"({tr(base['name'])})."), WHITE, 2)
        para(L("• Monsters and bosses come from every stage you have unlocked (new biomes join the pool).",
               "• Monstros e chefões vêm de todas as fases que você já liberou (biomas novos entram na lista)."),
             WHITE, 0)
        para(L("• The scenery changes after each boss: a random unlocked stage.",
               "• O cenário muda depois de cada chefão: uma fase liberada sorteada."), WHITE, 0)
        para(L("• Surviving 10 minutes clears the level and unlocks the next one; every 10 minutes you choose "
               "to stay or go up (the timer keeps going).",
               "• Sobreviver 10 minutos conclui o nível e libera o próximo; a cada 10 minutos você escolhe ficar "
               "ou subir (o tempo continua)."), WHITE, 0)
        para(L("• No accessories (for now): elites and bosses drop accessory fragments directly.",
               "• Sem acessórios (por enquanto): elites e chefões dropam fragmentos de acessório direto."), WHITE, 8)
        # nível
        self.text(L("Rift level", "Nível da fenda"), "normal", YELLOW, (x, y + 3))
        lx = x + 170
        rects = self.rift_lv_rects(lx, y)
        self._rift_lv_rects = rects
        lv, top = self.rift_level(), self.roster.rift_lv
        for r, lab, ok in zip(rects, ("<", ">"), (lv > 1, lv < top)):
            hot = ok and r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if hot else (36, 36, 50), r, border_radius=8)
            pygame.draw.rect(s, (200, 200, 215) if ok else (70, 70, 80), r, 1, border_radius=8)
            self.text(lab, "normal", WHITE if ok else (90, 90, 100), r.center, "center")
        self.text(L(f"Lv {lv}", f"Nv {lv}"), "normal", rift.COLOR, (lx + 112, y + 15), "center")
        self.text(L(f"highest unlocked: Lv {top}", f"maior liberado: Nv {top}"), "small", GREY, (lx + 240, y + 7))
        y += 38
        m = rift.mults(lv)
        para(L(f"Enemy HP x{m['hp']:.2f}  ·  Strength x{m['dmg']:.2f}  ·  Resistance x{m['res']:.2f}  ·  "
               f"Rewards x{m['reward']:.2f}  (on top of {base['name']})",
               f"Vida x{m['hp']:.2f}  ·  Força x{m['dmg']:.2f}  ·  Resistência x{m['res']:.2f}  ·  "
               f"Recompensas x{m['reward']:.2f}  (sobre a {tr(base['name'])})"), WHITE, 8)
        best = self.roster.endless_best.get("rift", 0)
        bm, bs = divmod(int(best), 60)
        self.text(L(f"Best time: {bm:02d}:{bs:02d}", f"Melhor tempo: {bm:02d}:{bs:02d}") if best else
                  L("Best time: -", "Melhor tempo: -"), "normal", (255, 170, 140), (x, y))
        y += 30
        frags = self.roster.acc_frags
        para(L("Accessory fragments you have: ", "Fragmentos de acessório que você tem: ") + ", ".join(
            f"{accm.cat_name(c, lang)} {frags.get(c, 0)}" for c in accm.FRAG_CATS), (120, 220, 230), 6)
        return y

    def stages_event(self, ev):
        ids = self.selectable_stages()
        if self.stage_cursor not in ids:
            self.stage_cursor = ids[0]
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w, pygame.K_RIGHT, pygame.K_d,
                     pygame.K_DOWN, pygame.K_s):
                step = -1 if k in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w) else 1
                self.stage_cursor = ids[(ids.index(self.stage_cursor) + step) % len(ids)]
                if self.stage_unlocked(self.stage_cursor):
                    self.stage_pick(self.stage_cursor)
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.stage_pick(self.stage_cursor):
                    self.start_run()
            elif k == pygame.K_ESCAPE:
                self.go("hub")
            elif k in (pygame.K_PAGEUP, pygame.K_PAGEDOWN) and self.stage_cursor == rift.RIFT_ID:
                self.rift_step(1 if k == pygame.K_PAGEUP else -1)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rift_tile_rect().collidepoint(ev.pos):
                self.stage_cursor = rift.RIFT_ID
                self.stage_pick(rift.RIFT_ID)
                return True
            if self.stage_cursor == rift.RIFT_ID:
                for d, r in zip((-1, 1), getattr(self, "_rift_lv_rects", ())):
                    if r.collidepoint(ev.pos):
                        self.rift_step(d)
                        return True
            if self.lo_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            if self.stage_start_rect().collidepoint(ev.pos):
                if self.stage_pick(self.stage_cursor):
                    self.start_run()
                return True
            for sid, bi, k, r in self.biome_tiles():
                if r.collidepoint(ev.pos):
                    if sid is None:
                        self.toast(f"{tr(BIOMES[bi]['name'])}: " + tr("coming soon"))
                    else:
                        self.stage_cursor = sid
                        self.stage_pick(sid)
        return True

    def draw_stages(self):
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        self.text("STAGE SELECT", "big", YELLOW, (40, 22))
        self.button(self.lo_back_rect(), "Back", self.lo_back_rect().collidepoint(mouse))
        ids = self.selectable_stages()
        if self.stage_cursor not in ids:
            self.stage_cursor = ids[0]

        # ---- biomas e fases ----
        for bi, b in enumerate(BIOMES):
            y = self.BIOME_Y + bi * self.BIOME_H
            ready = bool(b["stages"])
            self.text(b["name"], "normal", b["color"] if ready else (90, 90, 100), (self.BIOME_X, y))
            if not ready:
                self.text("Coming soon", "small", (120, 120, 135), (self.BIOME_X + 6 + self.fonts["normal"].size(
                    tr(b["name"]))[0] + 10, y + 5))
        romans = ["I", "II", "III", "IV", "V", "∞"]
        for sid, bi, k, r in self.biome_tiles():
            b = BIOMES[bi]
            if sid is None:   # bioma ainda não implementado: apagadinho
                pygame.draw.rect(s, (24, 24, 30), r, border_radius=8)
                pygame.draw.rect(s, (48, 48, 58), r, 1, border_radius=8)
                if k == 5:
                    draw_infinity(s, r.center, 34, (70, 70, 80), 2)
                else:
                    self.text(romans[k], "normal", (70, 70, 80), r.center, "center")
                continue
            unlocked = self.stage_unlocked(sid)
            cur = sid == self.stage_cursor
            chosen = sid == self.roster.stage
            prev = self.stage_preview(sid, r.w, r.h).copy()
            if not unlocked:
                prev.fill((70, 70, 80), special_flags=pygame.BLEND_RGB_MULT)
                prev.fill((10, 10, 14), special_flags=pygame.BLEND_RGB_ADD)
            mask = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=8)
            tile = pygame.Surface(r.size, pygame.SRCALPHA)
            tile.blit(prev, (0, 0))
            tile.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            s.blit(tile, r)
            if is_endless(sid):   # Endless: faixa avermelhada
                band = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                band.fill((120, 20, 30, 70))
                s.blit(band, r)
            else:   # chefão da fase no canto
                st = STAGES[sid]
                draw_enemy(s, st["boss_sprite"], (r.right - 20, r.bottom - 20), 11,
                           st["boss_color"] if unlocked else (60, 60, 70))
            if k < 5:
                lab = self.fonts["normal"].render(romans[k], True, WHITE if unlocked else (110, 110, 120))
                shadow = self.fonts["normal"].render(romans[k], True, (0, 0, 0))
                s.blit(shadow, (r.x + 11, r.y + 6))
                s.blit(lab, (r.x + 9, r.y + 4))
            else:
                draw_infinity(s, (r.centerx + 1, r.y + 29), 46, (0, 0, 0), 5)
                draw_infinity(s, (r.centerx, r.y + 28), 46, WHITE if unlocked else (110, 110, 120), 4)
            if k == 5:
                self.text("ENDLESS", "small", (255, 170, 140) if unlocked else (110, 110, 120),
                          (r.centerx, r.bottom - 6), "midbottom")
            if not unlocked:   # cadeado
                lk = pygame.Rect(0, 0, 16, 12)
                lk.center = (r.right - 16, r.y + 18)
                pygame.draw.rect(s, (150, 150, 160), lk, border_radius=3)
                pygame.draw.arc(s, (150, 150, 160), (lk.x + 2, lk.y - 8, 12, 14), 0, math.pi, 2)
            elif not is_endless(sid) and sid < self.roster.stages_cleared:
                draw_star(s, (r.right - 14, r.y + 14), 7, YELLOW)   # fase concluída
            pygame.draw.rect(s, YELLOW if cur else GREEN if chosen else (90, 90, 105), r, 3 if (cur or chosen) else 1,
                             border_radius=8)

        self.draw_rift_tile(mouse)

        # ---- detalhes da fase ----
        sid = self.stage_cursor
        panel = pygame.Rect(660, 92, W - 690, H - 200)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        x, tw = panel.x + 22, panel.w - 44
        y = panel.y + 12
        self.text(self.stage_name(sid), "big", WHITE, (x, y))
        y += 52
        if not self.stage_unlocked(sid):
            self.text(self.stage_lock_text(sid), "small", RED, (x, y))
            y += 22

        def para(txt, col=GREY, gap=4):
            nonlocal y
            for ln in self.wrap(txt, "small", tw):
                self.text(ln, "small", col, (x, y))
                y += 17
            y += gap

        n = len(self.roster.active())
        diff_hp, diff_rate = DIFFICULTIES[self.settings["difficulty"]]
        count_mult, party_hp = PARTY_SCALING.get(n, PARTY_SCALING[4])
        pct = lambda v: f"+{round((v - 1) * 100)}%" if v > 1 else "base"
        if sid == rift.RIFT_ID:
            y = self.draw_rift_details(x, y, tw, para, mouse)
            para(f"Party of {n}: {count_mult:.1f}x enemies, HP {pct(party_hp)}   ·   {self.settings['difficulty']} "
                 f"difficulty: HP x{diff_hp:.2f}, amount x{diff_rate:.2f}")
        elif is_endless(sid):
            b = endless_biome(sid)
            st1 = STAGES[b["stages"][0]]
            best = self.roster.endless_best.get(b["id"], 0)
            bm, bs = divmod(int(best), 60)
            para(f"No time limit: the run goes on until the hero falls or you quit. It starts at "
                 f"{st1['name']} difficulty.", WHITE)
            para("• Every 2 minutes the difficulty goes up one tier: +50% enemy HP, +30% strength, +50% resistance "
                 "and +25% EXP and gold.", WHITE, 0)
            para("• Every minute a Super Elite or an Elite Squad appears.", WHITE, 0)
            para(f"• Every 2 minutes a boss appears (with 2 random classes), taking turns among the bosses of "
                 f"{b['name']} I to V and following the scaling.", WHITE, 0)
            para("• Gold is proportional to the time survived, with the reward of the current tier.", WHITE, 10)
            self.text("Bosses in rotation", "normal", YELLOW, (x, y))
            y += 30
            for k, stx in enumerate(b["stages"]):
                stg = STAGES[stx]
                cx = x + 14 + k * 108
                draw_enemy(s, stg["boss_sprite"], (cx, y + 16), 14, stg["boss_color"])
                for j, ln in enumerate(self.wrap(stg["boss"], "small", 100)[:2]):
                    self.text(ln, "small", WHITE, (cx - 14, y + 36 + j * 16))
                self.text(f"{(k + 1) * 2}:00 · {(k + 6) * 2}:00", "small", GREY, (cx - 14, y + 70))
            y += 96
            self.text(f"Best time: {bm:02d}:{bs:02d}" if best else "Best time: -", "normal", (255, 170, 140), (x, y))
            y += 30
            y = self.draw_stage_drops(b["stages"], x, y, mouse, tw) + 4
            para(f"Party of {n}: {count_mult:.1f}x enemies, HP {pct(party_hp)}   ·   {self.settings['difficulty']} "
                 f"difficulty: HP x{diff_hp:.2f}, amount x{diff_rate:.2f}")
        else:
            st = STAGES[sid]
            mins = STAGE_TIME // 60
            if "heart" in getattr(self.roster, "trophies_on", []):   # troféu Heart: fase de 5 minutos
                mins //= 2
            para(st["desc"])
            para(f"Duration: {mins}:00  ·  at {mins}:00 the boss {st['boss']} appears and the timer stops. "
                 "Defeat it to clear the stage.", WHITE, 8)
            self.text("Stage difficulty", "normal", YELLOW, (x, y))
            y += 26
            para(f"Enemy HP {pct(st['hp'])}   ·   Strength {pct(st['dmg'])}   ·   Resistance {pct(st['res'])}", WHITE, 0)
            para(f"Party of {n}: {count_mult:.1f}x enemies, HP {pct(party_hp)}   ·   "
                 f"{self.settings['difficulty']} difficulty: HP x{diff_hp:.2f}, amount x{diff_rate:.2f}", GREY, 8)
            self.text("Rewards", "normal", YELLOW, (x, y))
            y += 26
            gold = GOLD_STAGE_BASE * st["reward"]
            para(f"EXP {pct(st['reward'])}   ·   Gold {pct(st['reward'])}   ·   Stage clear: {gold:g} gold "
                 f"(not cleared: proportional to time played)", WHITE, 2)
            y = self.draw_stage_drops([sid], x, y, mouse, tw) + 6
            # tabela de inimigos (compacta)
            self.text("Enemies", "normal", YELLOW, (x, y))
            y += 26
            cols = [("", 0), ("HP", 112), ("Damage", 232), ("Arm.", 322), ("M.Def", 380), ("Spd.", 440),
                    ("Appears", 490)]
            for name, cx in cols:
                self.text(name, "small", GREY, (x + cx, y))
            y += 20
            hp_mult = diff_hp * party_hp * st["hp"]
            from data import ROLE_FROM, stage_pos
            bio = biome_of(sid)["enemies"]
            rows = [(bio["swarm"], "0:00"), (bio["mid"], "~0:20"), (bio["heavy"], "~1:20")]
            for r_new, (si, t0) in ROLE_FROM.items():   # inimigos novos das fases III e V do bioma
                if stage_pos(sid) >= si:
                    rows.append((bio[r_new], f"~{t0 // 60}:{t0 % 60:02d}"))
            rows.append(("chefe", f"{mins}:00"))
            ts_end = 1 + STAGE_TIME / 90
            for kind, when in rows:
                t = ENEMY_TYPES[kind]
                boss = kind == "chefe"
                col = st["boss_color"] if boss else t["color"]
                draw_enemy(s, st["boss_sprite"] if boss else kind, (x + 8, y + 8), 8, col)
                label = tr(st["boss"] if boss else ENEMY_NAMES[kind])
                while len(label) > 4 and self.fonts["small"].size(label)[0] > 86:
                    label = label[:-2].rstrip() + "…"
                self.text(label, "small", RED if boss else WHITE, (x + 22, y))
                if boss:
                    hp0 = hp1 = t["hp"] * hp_mult * el.BOSS_HP
                    dmg0 = dmg1 = t["dmg"] * st["dmg"] * el.BOSS_DMG
                else:
                    hp0, hp1 = t["hp"] * hp_mult, t["hp"] * hp_mult * ts_end
                    dmg0, dmg1 = t["dmg"] * st["dmg"], t["dmg"] * st["dmg"] * (0.5 + 0.5 * ts_end)
                vals = [f"{hp0:,.0f}" + ("" if boss else f" > {hp1:,.0f}"),
                        f"{dmg0:.0f}" + ("" if boss else f" > {dmg1:.0f}"),
                        f"{t.get('armor', 0) * st['res']:.1f}", f"{t.get('mres', 0) * st['res']:.1f}",
                        f"{t['speed']}", when]
                for (name, cx), v in zip(cols[1:], vals):
                    self.text(v, "small", WHITE, (x + cx, y))
                y += 21
            y += 4
            sw_en = ENEMY_NAMES[bio["swarm"]]
            sw_pt = tr(sw_en)
            para(i18n.L(f"Every minute: a horde of {sw_en} plus a Super Elite or an Elite Squad. The boss comes with 2 "
                        f"random classes (their weapons and skills) and summons {sw_en}.",
                        f"A cada minuto: uma horda de {sw_pt} e um Super Elite ou Esquadrão de Elite. O chefão vem "
                        f"com 2 classes aleatórias (armas e habilidades delas) e invoca {sw_pt}."))

        st_r = self.stage_start_rect()
        ok = self.stage_unlocked(sid)
        self.button(st_r, "Start run", st_r.collidepoint(mouse), GREEN, enabled=ok)
        self.text("Clear stage V of a biome to unlock its Endless and stage I of the next biome", "small",
                  (150, 150, 165), (self.BIOME_X, self.BIOME_Y + len(BIOMES) * self.BIOME_H + 2))
        self.text("Arrows choose stage  ·  ENTER start  ·  ESC back", "small", GREY, (W / 2, H - 12), "midbottom")
        if getattr(self, "_stage_tip", None):   # dica dos acessórios (por cima de tudo)
            self.draw_tooltip(self._stage_tip, mouse)
            self._stage_tip = None
        self.draw_toast()

    # ================================================================
    # renomear
    # ================================================================
    def draw_stage_drops(self, stage_ids, x, y, mouse, width=546):
        """Linha 'Accessory drops' com os ícones dos acessórios possíveis (✓ = já obtido); quebra em mais linhas
        quando não cabem (Endless: os do bioma todo)."""
        L = i18n.L
        pool = accm.pool_for(stage_ids)
        if not pool:
            return y
        s = self.screen
        n_own = sum(1 for a in pool if a in self.roster.acc_owned)
        lab = L(f"Accessory drops ({n_own}/{len(pool)}):", f"Drops de acessório ({n_own}/{len(pool)}):")
        self.text(lab, "small", (120, 220, 230), (x, y + 6))
        x0 = x + self.fonts["small"].size(tr(lab))[0] + 10
        cx = x0
        hover = None
        for aid in pool:
            own = aid in self.roster.acc_owned
            if cx + 26 > x + width:   # próxima linha
                cx = x0
                y += 30
            r = pygame.Rect(cx, y, 26, 26)
            s.blit(accm.icon(aid, 26, dim=not own), r)
            if own:   # marca de já obtido
                pygame.draw.circle(s, (40, 160, 70), (r.right - 2, r.y + 3), 7)
                pygame.draw.lines(s, WHITE, False, [(r.right - 6, r.y + 3), (r.right - 3, r.y + 6), (r.right + 2, r.y)],
                                  2)
            if r.collidepoint(mouse):
                hover = aid
            cx += 32
        if hover:
            lang = i18n.LANG
            own = hover in self.roster.acc_owned
            self._stage_tip = [(accm.name(hover, lang) + "  ·  " + accm.cat_name(accm.ACC[hover]["cat"], lang), YELLOW),
                               (L("Already found", "Já encontrado") if own else L("Not found yet", "Ainda não encontrado"),
                                GREEN if own else GREY),
                               (accm.desc(hover, self.roster.acc_owned.get(hover, 0), lang), WHITE)]
        return y + 30

    def rename_event(self, ev):
        if ev.type == pygame.TEXTINPUT:
            if len(self.rename_buf) < 14:
                self.rename_buf += ev.text
            self.rename_buf = self.rename_buf[:14]
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.rename_buf = self.rename_buf[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                name = self.rename_buf.strip()
                if name:
                    self.party_member.name = name
                    self.roster.save()
                pygame.key.stop_text_input()
                self.go("party")
            elif ev.key == pygame.K_ESCAPE:
                pygame.key.stop_text_input()
                self.go("party")
        return True

    def draw_rename(self):
        self.draw_party()
        s = self.screen
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        s.blit(overlay, (0, 0))
        box = pygame.Rect(W / 2 - 260, H / 2 - 90, 520, 180)
        pygame.draw.rect(s, PANEL, box, border_radius=12)
        pygame.draw.rect(s, YELLOW, box, 2, border_radius=12)
        self.text("New name", "normal", YELLOW, (box.centerx, box.y + 30), "center")
        field = pygame.Rect(box.x + 40, box.y + 60, box.w - 80, 50)
        pygame.draw.rect(s, DARK, field, border_radius=8)
        cursor = "_" if int(self.clock_time * 2) % 2 == 0 else " "
        self.text(self.rename_buf + cursor, "normal", WHITE, (field.x + 16, field.centery), "midleft")
        self.text("ENTER confirm  ·  ESC cancel", "small", GREY, (box.centerx, box.bottom - 30), "center")

    # ================================================================
    # aparência do gato (criação de personagem)
    # ================================================================
    def open_look(self, m):
        import cats
        self.look_member = m
        self.look_orig = dict(cats.clean_look(m.look))
        m.look = dict(self.look_orig)
        self.look_sel = 0
        self.go("look")

    def look_layout(self):
        import cats
        rows = [pygame.Rect(560, 150 + i * 62, 640, 50) for i in range(len(cats.FIELDS))]
        arrows = [(pygame.Rect(r.x + 250, r.y + 5, 40, 40), pygame.Rect(r.right - 50, r.y + 5, 40, 40)) for r in rows]
        bw = 196
        buttons = {name: pygame.Rect(560 + k * (bw + 26), 560, bw, 52)
                   for k, name in enumerate(("random", "reset", "done"))}
        return rows, arrows, buttons

    def look_change(self, row, d):
        import cats
        key, _e, _p, opts = cats.FIELDS[row]
        m = self.look_member
        m.look[key] = (m.look.get(key, 0) + d) % len(opts)

    def look_action(self, name):
        import cats
        m = self.look_member
        if name == "random":
            m.look = cats.random_look()
        elif name == "reset":
            m.look = dict(self.look_orig)
        elif name == "done":
            m.look = cats.clean_look(m.look)
            self.roster.save()
            self.go("party")

    def look_event(self, ev):
        import cats
        rows, arrows, buttons = self.look_layout()
        n = len(cats.FIELDS)
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_UP, pygame.K_w):
                self.look_sel = (self.look_sel - 1) % n
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.look_sel = (self.look_sel + 1) % n
            elif k in (pygame.K_LEFT, pygame.K_a):
                self.look_change(self.look_sel, -1)
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.look_change(self.look_sel, 1)
            elif k == pygame.K_r:
                self.look_action("random")
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.look_action("done")
        elif ev.type == pygame.MOUSEWHEEL:
            self.look_change(self.look_sel, -ev.y)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, (a, b) in enumerate(arrows):
                if a.collidepoint(ev.pos):
                    self.look_sel = i
                    self.look_change(i, -1)
                    return True
                if b.collidepoint(ev.pos):
                    self.look_sel = i
                    self.look_change(i, 1)
                    return True
            for i, r in enumerate(rows):
                if r.collidepoint(ev.pos):
                    self.look_sel = i
                    return True
            for name, r in buttons.items():
                if r.collidepoint(ev.pos):
                    self.look_action(name)
        return True

    def _arrow(self, rect, left, hot):
        s = self.screen
        pygame.draw.rect(s, (60, 60, 85) if hot else DARK, rect, border_radius=4)
        pygame.draw.rect(s, YELLOW if hot else GREY, rect, 2 if hot else 1, border_radius=4)
        cx, cy = rect.center
        pts = [(cx + 7, cy - 9), (cx - 7, cy), (cx + 7, cy + 9)] if left else [(cx - 7, cy - 9), (cx + 7, cy), (cx - 7, cy + 9)]
        pygame.draw.polygon(s, YELLOW if hot else WHITE, pts)

    def draw_look(self):
        import cats
        s = self.screen
        self.menu_bg()
        m = self.look_member
        lang = i18n.LANG
        mouse = self.mouse_pos()
        self.text(L(f"APPEARANCE - {m.name}", f"APARÊNCIA - {m.name}"), "big", YELLOW, (40, 30))
        # prévia: grande, e no tamanho da run olhando para os dois lados
        prev = pygame.Rect(40, 110, 480, 420)
        pygame.draw.rect(s, PANEL, prev, border_radius=10)
        pygame.draw.rect(s, GREY, prev, 1, border_radius=10)
        glow = pygame.Surface((300, 90), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (250, 210, 120, 40), glow.get_rect())
        s.blit(glow, (prev.centerx - 150, prev.y + 268))
        face = V(1, 0.15) if int(self.clock_time / 2.5) % 2 == 0 else V(-1, 0.15)
        cats.draw_cat(s, m.cls, (prev.centerx, prev.y + 200), 70, face, m.look)
        for k, f in enumerate((V(1, 0), V(-1, 0), V(0.2, 1))):
            cats.draw_cat(s, m.cls, (prev.centerx - 90 + k * 90, prev.bottom - 50), 16, f, m.look)
        self.text(L("Helmet, weapon and tunic come from the class", "Capacete, arma e túnica são da classe"),
                  "small", GREY, (prev.centerx, prev.bottom + 22), "center")
        # opções
        rows, arrows, buttons = self.look_layout()
        for i, (key, en, pt, opts) in enumerate(cats.FIELDS):
            r = rows[i]
            sel = i == self.look_sel
            pygame.draw.rect(s, (50, 50, 72) if sel else PANEL, r, border_radius=6)
            pygame.draw.rect(s, YELLOW if sel else (70, 70, 90), r, 2 if sel else 1, border_radius=6)
            self.text(pt if lang == "pt" else en, "normal", YELLOW if sel else WHITE, (r.x + 18, r.centery), "midleft")
            a, b = arrows[i]
            self._arrow(a, True, a.collidepoint(mouse))
            self._arrow(b, False, b.collidepoint(mouse))
            v = m.look.get(key, 0) % len(opts)
            name = cats.option_name(key, v, lang)
            mid = (a.right + b.left) // 2
            color = opts[v][2] if len(opts[v]) > 2 else None
            if color:   # amostra da cor
                sw = pygame.Rect(a.right + 14, r.y + 13, 24, 24)
                pygame.draw.rect(s, color, sw)
                if len(opts[v]) > 3 and opts[v][3]:
                    pygame.draw.rect(s, opts[v][3], (sw.centerx, sw.y, sw.w // 2, sw.h))
                pygame.draw.rect(s, (14, 10, 16), sw, 2)
                mid += 18
            self.text(name, "normal", WHITE, (mid, r.centery), "center")
            self.text(f"{v + 1}/{len(opts)}", "small", GREY, (b.x - 10, r.centery), "midright")
        labels = {"random": L("Randomize", "Aleatório"), "reset": L("Undo changes", "Desfazer"),
                  "done": L("Done", "Pronto")}
        for name, r in buttons.items():
            self.button(r, labels[name], r.collidepoint(mouse), GREEN if name == "done" else WHITE)
        self.text(L("Up/Down choose  ·  Left/Right change  ·  R randomize  ·  ENTER/ESC done",
                    "Cima/Baixo escolhe  ·  Esquerda/Direita muda  ·  R aleatório  ·  ENTER/ESC pronto"),
                  "small", GREY, (W / 2, H - 30), "center")

    # ================================================================
    # configurações
    # ================================================================
    def config_rects(self):
        return [pygame.Rect(W // 2 - 260, 170 + i * 66, 520, 54) for i in range(len(self.CONFIG_ITEMS))]

    def config_label(self, key):
        s = self.settings
        on_off = lambda v: "On" if v else "Off"
        return {
            "fullscreen": ("Fullscreen", on_off(s["fullscreen"])),
            "difficulty": ("Difficulty", f"<  {s['difficulty']}  >"),
            "damage_numbers": ("Damage numbers", on_off(s["damage_numbers"])),
            "show_fps": ("Show FPS", on_off(s["show_fps"])),
            "fps_limit": ("FPS limit", f"<  {tr(s['fps_limit'])}  >"),
            "language": ("Language", f"<  {s['language']}  >"),
            "back": ("Back", ""),
        }[key]

    def change_config(self, key, step=1):
        s = self.settings
        if key == "back":
            self.go("menu")
            self.sel = self.MAIN_ITEMS.index("Configurations")
            return
        if key == "difficulty":
            names = list(DIFFICULTIES)
            s["difficulty"] = names[(names.index(s["difficulty"]) + step) % len(names)]
        elif key == "fps_limit":
            from roster import FPS_LIMITS
            cur = s["fps_limit"] if s["fps_limit"] in FPS_LIMITS else FPS_LIMITS[-1]
            s["fps_limit"] = FPS_LIMITS[(FPS_LIMITS.index(cur) + step) % len(FPS_LIMITS)]
        elif key == "language":
            names = list(i18n.LANGUAGES)
            s["language"] = names[(names.index(s["language"]) + step) % len(names)]
            i18n.set_language(s["language"])
        else:
            s[key] = not s[key]
            if key == "fullscreen":
                self.apply_display()
        save_settings(s)

    def config_event(self, ev):
        rects = self.config_rects()
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(rects)
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(rects)
            elif k in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                key = self.CONFIG_ITEMS[self.sel]
                if key != "back":
                    self.change_config(key, -1 if k in (pygame.K_LEFT, pygame.K_a) else 1)
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.change_config(self.CONFIG_ITEMS[self.sel])
            elif k == pygame.K_ESCAPE:
                self.change_config("back")
        elif ev.type == pygame.MOUSEMOTION:
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos):
                    self.sel = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            for i, r in enumerate(rects):
                if r.collidepoint(ev.pos):
                    self.sel = i
                    self.change_config(self.CONFIG_ITEMS[i], 1 if ev.button == 1 else -1)
        return True

    # ================================================================
    # Inventário: fragmentos de classe (dropados por inimigos de elite)
    # ================================================================
    INV_COLS = 8

    def inventory_cells(self):
        cw, ch, gap = 144, 118, 9
        x0 = (W - (self.INV_COLS * cw + (self.INV_COLS - 1) * gap)) // 2
        cells = []
        for i, cid in enumerate(prog.CLASS_ORDER):
            row, col = divmod(i, self.INV_COLS)
            cells.append((cid, pygame.Rect(x0 + col * (cw + gap), 140 + row * (ch + gap), cw, ch)))
        return cells

    def inventory_back_rect(self):
        return pygame.Rect(W - 170, 24, 140, 44)

    def inventory_tab_rects(self):
        return [pygame.Rect(40, 82, 230, 40), pygame.Rect(282, 82, 170, 40)]

    def inventory_member_rects(self):
        return [pygame.Rect(32, 140 + i * 112, 320, 100) for i in range(len(self.roster.active()))]

    INV_PANEL = pygame.Rect(372, 140, W - 404, 548)

    def inventory_item_rects(self):
        p = self.INV_PANEL
        w = (p.w - 72) // 2
        return {"weapon": pygame.Rect(p.x + 24, p.y + 76, w, 272),
                "helmet": pygame.Rect(p.x + 48 + w, p.y + 76, w, 272)}

    def inventory_upgrade_rect(self, slot):
        r = self.inventory_item_rects()[slot]
        return pygame.Rect(r.x + 16, r.bottom - 52, r.w - 32, 40)

    def inventory_event(self, ev):
        # baú = inventário (fragmentos); ferreiro = melhorias dos equipamentos
        tab = 0 if getattr(self, "inv_mode", "chest") == "smith" else 1
        members = self.roster.active()
        self.inv_member = max(0, min(getattr(self, "inv_member", 0), len(members) - 1))
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif tab == 0 and k in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                order = prog.CLASS_ORDER
                d = -1 if k in (pygame.K_UP, pygame.K_w) else 1
                self.smith_cid = order[(order.index(self.smith_sel()) + d) % len(order)]
                self.smith_show(self.smith_cid)
        elif ev.type == pygame.MOUSEWHEEL and tab == 0:
            n = len(prog.CLASS_ORDER)
            self.smith_scroll = max(0, min(n - self.SMITH_VISIBLE, self.smith_scroll - ev.y))
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            if tab == 0 and self.smith_tab_click(ev.pos):
                return True
            if tab == 1 and self.chest_tab_click(ev.pos):
                return True
            if tab == 0:
                for k, r in self.smith_rows():
                    if r.collidepoint(ev.pos):
                        self.smith_cid = k
                        return True
                cid = self.smith_sel()
                for slot in eq.FIXED_SLOTS:
                    if self.inventory_upgrade_rect(slot).collidepoint(ev.pos):
                        err = eq.try_upgrade(self.roster, cid, slot)
                        lv = eq.gear_level(cid, slot)
                        self.toast(err or i18n.L(
                            f"Upgraded to {eq.item_name(cid, slot, lv)}! (every {tr(CLASSES[cid]['name'])})",
                            f"Melhorado para {eq.item_name(cid, slot, lv, 'pt')}! (todo {tr(CLASSES[cid]['name'])})"))
        return True

    # ================================================================
    # Joalheiro: acessórios (anéis, bracelete, berloques; colar depois)
    # ================================================================
    JW_LIST = pygame.Rect(32, 130, 250, 558)
    JW_ROW = 34
    JW_VISIBLE = 15
    JW_SLOTS = pygame.Rect(292, 130, 300, 352)
    JW_GRID = pygame.Rect(604, 130, 644, 348)
    JW_DETAIL = pygame.Rect(604, 486, 644, 202)
    jw_member = 0
    jw_scroll = 0
    jw_slot = "ring1"
    jw_sel = None

    def jw_members(self):
        return self.roster.members

    def jw_member_rows(self):
        out = []
        for i, m in enumerate(self.jw_members()):
            vis = i - self.jw_scroll
            if 0 <= vis < self.JW_VISIBLE:
                out.append((i, pygame.Rect(self.JW_LIST.x + 6, self.JW_LIST.y + 30 + vis * self.JW_ROW,
                                           self.JW_LIST.w - 14, self.JW_ROW - 3)))
        return out

    def jw_slot_rects(self):
        p = self.JW_SLOTS
        return [(sl, pygame.Rect(p.x + 8, p.y + 30 + i * 45, p.w - 16, 41)) for i, sl in enumerate(accm.SLOTS)]

    jw_ftag = None    # filtro por tag da grade de acessórios
    jw_dd = False     # dropdown do filtro aberto

    def jw_cells(self):
        cat = accm.SLOT_CAT[self.jw_slot]
        g = self.JW_GRID
        cw, ch, gap = (g.w - 16 - 3 * 4) // 4, 36, 4
        aids = [a for a in accm.ORDER[cat] if not self.jw_ftag or self.jw_ftag in accm.tags(a)]
        return [(aid, pygame.Rect(g.x + 8 + (i % 4) * (cw + gap), g.y + 32 + (i // 4) * (ch + gap), cw, ch))
                for i, aid in enumerate(aids)]

    # ---- filtro por tag (igual ao das skills) ----
    def jw_filter_rect(self):
        g = self.JW_GRID
        return pygame.Rect(g.right - 238, g.y + 4, 230, 24)

    def jw_filter_tags(self):
        cat = accm.SLOT_CAT[self.jw_slot]
        seen = set()
        for a in accm.ORDER[cat]:
            seen.update(accm.tags(a))
        return [None] + [t for t in TAG_ORDER if t in seen]

    def jw_fix_filter(self):
        if self.jw_ftag not in self.jw_filter_tags():
            self.jw_ftag = None

    def jw_dd_rects(self):
        vals = self.jw_filter_tags()
        g = self.JW_GRID
        cols = 3
        rows = -(-len(vals) // cols)
        cw = (g.w - 24) // cols
        return [(i, v, pygame.Rect(g.x + 12 + (i // rows) * cw, g.y + 36 + (i % rows) * self.DD_ROW_H, cw - 8,
                                   self.DD_ROW_H - 3)) for i, v in enumerate(vals)]

    def draw_jw_filter(self, mouse):
        s = self.screen
        r = self.jw_filter_rect()
        hot = r.collidepoint(mouse) or self.jw_dd
        on = self.jw_ftag is not None
        pygame.draw.rect(s, (60, 60, 85) if hot else (36, 36, 50), r, border_radius=6)
        pygame.draw.rect(s, GREEN if on else YELLOW if hot else (90, 90, 105), r, 1, border_radius=6)
        lab = tag_name(self.jw_ftag, i18n.LANG) if on else i18n.L("All tags", "Todas as tags")
        self.text("Tag: " + lab, "small", WHITE if on else GREY, (r.x + 10, r.centery), "midleft")
        cx, cy = r.right - 14, r.centery
        pygame.draw.polygon(s, GREY, [(cx - 5, cy - 3), (cx + 5, cy - 3), (cx, cy + 3)])

    def draw_jw_dropdown(self, mouse):
        s = self.screen
        rects = self.jw_dd_rects()
        g = self.JW_GRID
        panel = pygame.Rect(g.x + 4, g.y + 30, g.w - 8, max(r.bottom for _, _, r in rects) - g.y - 30 + 8)
        sh = pygame.Surface(panel.inflate(12, 12).size, pygame.SRCALPHA)
        sh.fill((0, 0, 0, 110))
        s.blit(sh, panel.inflate(12, 12).move(4, 4))
        pygame.draw.rect(s, (34, 34, 46), panel, border_radius=8)
        pygame.draw.rect(s, YELLOW, panel, 2, border_radius=8)
        cat = accm.SLOT_CAT[self.jw_slot]
        for i, v, r in rects:
            if r.collidepoint(mouse):
                pygame.draw.rect(s, (70, 70, 100), r, border_radius=5)
            if v == self.jw_ftag:
                pygame.draw.rect(s, GREEN, r, 1, border_radius=5)
            if v is None:
                self.text(i18n.L("All tags", "Todas as tags"), "small", YELLOW, (r.x + 10, r.centery), "midleft")
            else:
                n = sum(1 for a in accm.ORDER[cat] if v in accm.tags(a))
                self.text(tag_name(v, i18n.LANG), "small", WHITE, (r.x + 10, r.centery), "midleft")
                self.text(str(n), "small", GREY, (r.right - 8, r.centery), "midright")

    def jw_filter_event(self, ev):
        """Clique no filtro / no dropdown. Retorna True se tratou o evento."""
        if ev.type != pygame.MOUSEBUTTONDOWN or ev.button not in (1, 3):
            return False
        if self.jw_dd:
            for i, v, r in self.jw_dd_rects():
                if r.collidepoint(ev.pos):
                    self.jw_ftag = v
                    break
            self.jw_dd = False
            return True
        if self.jw_filter_rect().collidepoint(ev.pos):
            self.jw_dd = True
            return True
        return False

    def jw_buttons(self):
        d = self.JW_DETAIL
        return (pygame.Rect(d.right - 400, d.bottom - 48, 190, 38), pygame.Rect(d.right - 202, d.bottom - 48, 190, 38))

    def jw_current(self):
        ms = self.jw_members()
        self.jw_member = max(0, min(self.jw_member, len(ms) - 1))
        return ms[self.jw_member]

    def jw_equip_action(self):
        L = i18n.L
        m = self.jw_current()
        aid = self.jw_sel
        if aid is None:
            return
        if m.acc.get(self.jw_slot) == aid:   # já está neste espaço: tira
            self.roster.equip_acc(m, self.jw_slot, None)
            self.toast(L(f"{accm.name(aid)} removed.", f"{accm.name(aid, 'pt')} removido."))
            return
        other, _sl = self.roster.acc_wearer(aid)
        err = self.roster.equip_acc(m, self.jw_slot, aid)
        if err:
            self.toast(L(*err))
        elif other is not None and other is not m:
            self.toast(L(f"{accm.name(aid)} moved from {other.name} to {m.name}.",
                         f"{accm.name(aid, 'pt')} passou de {other.name} para {m.name}."))
        else:
            self.toast(L(f"{m.name} equipped {accm.name(aid)}.", f"{m.name} equipou {accm.name(aid, 'pt')}."))

    def jw_upgrade_action(self):
        L = i18n.L
        aid = self.jw_sel
        if aid is None:
            return
        err = self.roster.upgrade_acc(aid)
        if err:
            self.toast(L(*err))
        else:
            lv = self.roster.acc_owned[aid]
            self.toast(L(f"{accm.name(aid)} is now +{lv}!", f"{accm.name(aid, 'pt')} agora é +{lv}!"))

    def acc_source(self, aid, short=False):
        """Onde o acessório é obtido (fase do drop ou nível da classe, para os colares)."""
        import dungeons as dgm
        L = i18n.L
        a = accm.ACC[aid]
        stg = accm.stage_of(aid)
        dg = accm.dungeon_of(aid)
        if a["cat"] == "neck":   # colar: dropa numa fase/masmorra e/ou libera com a classe no nível máximo
            cid = a["cls"]
            lv = prog.base_max_level(cid)
            n = CLASSES[cid]["name"]
            where = (tr(STAGES[stg]["name"]) if stg is not None else
                     dgm.name(dg, i18n.LANG) if dg is not None else None)
            if short:
                return where or L(f"{n} Lv {lv}", f"{n} Nv {lv}")
            unlock = L(f"taking {n} to Lv {lv} (any character)", f"levar {n} ao Nv {lv} (qualquer personagem)")
            short_unlock = L(f"taking {n} to Lv {lv}", f"levar {n} ao Nv {lv}")
            return (L(f"Drops in {where}, or unlocked by {short_unlock}", f"Dropa em {where}, ou libera ao {short_unlock}")
                    if where else L(f"Unlocked by {unlock}", f"Liberado ao {unlock}"))
        if stg is None and dg is not None:
            nm = dgm.name(dg, i18n.LANG)
            return nm if short else L(f"Drops in the {nm} (red portal)", f"Dropa na {nm} (portal vermelho)")
        if stg is None:
            return L("Future stage", "Fase futura") if short else L("Drops in a future stage", "Dropa numa fase futura")
        nm = tr(STAGES[stg]["name"])
        if short:   # nome curto para as células do Joalheiro
            return nm.replace("Abandoned Town", "Town").replace("Cidade Abandonada", "Cidade")
        return L(f"Drops in {nm} (and its Endless)", f"Dropa em {nm} (e no Endless do bioma)")

    def jeweler_event(self, ev):
        self.jw_fix_filter()
        if self.jw_filter_event(ev):
            return True
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if self.jw_dd and k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.jw_dd = False
            elif k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif k in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                n = len(self.jw_members())
                self.jw_member = (self.jw_member + (-1 if k in (pygame.K_UP, pygame.K_w) else 1)) % n
                if self.jw_member < self.jw_scroll:
                    self.jw_scroll = self.jw_member
                elif self.jw_member >= self.jw_scroll + self.JW_VISIBLE:
                    self.jw_scroll = self.jw_member - self.JW_VISIBLE + 1
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
                self.jw_equip_action()
            elif k == pygame.K_u:
                self.jw_upgrade_action()
        elif ev.type == pygame.MOUSEWHEEL:
            if self.JW_LIST.collidepoint(self.mouse_pos()):
                n = len(self.jw_members())
                self.jw_scroll = max(0, min(max(0, n - self.JW_VISIBLE), self.jw_scroll - ev.y))
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            for i, r in self.jw_member_rows():
                if r.collidepoint(ev.pos):
                    self.jw_member = i
                    return True
            m = self.jw_current()
            for sl, r in self.jw_slot_rects():
                if r.collidepoint(ev.pos):
                    self.jw_slot = sl
                    self.jw_sel = m.acc.get(sl)
                    return True
            for aid, r in self.jw_cells():
                if r.collidepoint(ev.pos):
                    self.jw_sel = aid
                    return True
            eqb, upb = self.jw_buttons()
            if eqb.collidepoint(ev.pos):
                self.jw_equip_action()
            elif upb.collidepoint(ev.pos):
                self.jw_upgrade_action()
        return True

    def draw_jeweler(self):
        L = i18n.L
        lang = i18n.LANG
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        R = self.roster
        self.text(L("JEWELER", "JOALHEIRO"), "big", YELLOW, (40, 20))
        self.text(L("Unique accessories: each one can be worn by one character at a time",
                    "Acessórios únicos: cada um só pode ser usado por um personagem por vez"), "normal", GREY, (42, 84))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        x = W - 240   # (deixa espaço para o botão "?")
        for cat in ("emblem", "trinket", "bracer", "ring"):   # fragmentos de cada categoria (cópias repetidas)
            txt = f"{R.acc_frags.get(cat, 0)}"
            w = self.fonts["normal"].size(txt)[0]
            x -= w + 40
            s.blit(accm.cat_icon(cat, 26), (x, 33))
            self.text(txt, "normal", WHITE, (x + 30, 36))
        m = self.jw_current()

        # personagens
        lst = self.JW_LIST
        pygame.draw.rect(s, PANEL, lst, border_radius=12)
        self.text(L("Characters", "Personagens"), "small", YELLOW, (lst.x + 12, lst.y + 8))
        for i, r in self.jw_member_rows():
            mm = self.jw_members()[i]
            sel, hov = i == self.jw_member, r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hov else (32, 32, 44), r, border_radius=8)
            if sel:
                pygame.draw.rect(s, YELLOW, r, 2, border_radius=8)
            draw_class_icon(s, mm.cls, (r.x + 16, r.centery + 1), 9, who=mm.name, look=mm.look, member=mm)
            self.text(mm.name, "small", WHITE if mm.active else GREY, (r.x + 32, r.y + 8))
            n = len(mm.acc)
            self.text(f"{n}/{len(accm.SLOTS)}", "small", (120, 220, 230) if n else (100, 100, 112), (r.right - 10, r.y + 8),
                      "topright")
        n = len(self.jw_members())
        if n > self.JW_VISIBLE:
            h = lst.h - 40
            bh = h * self.JW_VISIBLE / n
            yb = lst.y + 32 + (h - bh) * self.jw_scroll / max(1, n - self.JW_VISIBLE)
            pygame.draw.rect(s, GREY, (lst.right - 6, yb, 3, bh), border_radius=2)

        # espaços do personagem
        p = self.JW_SLOTS
        pygame.draw.rect(s, PANEL, p, border_radius=12)
        self.text(L(f"{m.name}'s accessories", f"Acessórios de {m.name}"), "small", YELLOW, (p.x + 12, p.y + 8))
        for sl, r in self.jw_slot_rects():
            sel = sl == self.jw_slot
            locked = False
            aid = m.acc.get(sl)
            pygame.draw.rect(s, (60, 60, 85) if sel else (36, 36, 50), r, border_radius=8)
            pygame.draw.rect(s, YELLOW if sel else (70, 70, 85), r, 2 if sel else 1, border_radius=8)
            self.text(accm.SLOT_LABEL[sl][1 if lang == "pt" else 0], "small", GREY, (r.x + 10, r.y + 3))
            if locked:
                self.text(L("Coming in a future version", "Chega numa versão futura"), "small", (110, 110, 125),
                          (r.x + 10, r.y + 24))
            elif aid:
                s.blit(accm.icon(aid, 30), (r.x + 110, r.y + 5))
                lv = R.acc_owned.get(aid, 0)
                nm = accm.name(aid, lang) + (f"  +{lv}" if lv else "")
                while len(nm) > 4 and self.fonts["small"].size(nm)[0] > r.w - 156:
                    nm = nm[:-2].rstrip() + "…"
                self.text(nm, "small", (120, 220, 230), (r.x + 146, r.y + 12))
            else:
                self.text(L("empty", "vazio"), "small", (100, 100, 112), (r.x + 110, r.y + 12))
        # resumo do personagem
        sp = pygame.Rect(p.x, p.bottom + 10, p.w, self.JW_DETAIL.bottom - p.bottom - 10)
        pygame.draw.rect(s, PANEL, sp, border_radius=12)
        self.text(L("Total from accessories", "Total dos acessórios"), "small", YELLOW, (sp.x + 12, sp.y + 8))
        y = sp.y + 30
        lines = []
        for sl in accm.SLOTS:
            aid = m.acc.get(sl)
            if aid:
                lines += self.wrap("• " + accm.desc(aid, R.acc_owned.get(aid, 0), lang), "small", sp.w - 24)
        if not lines:
            lines = [L("nothing equipped", "nada equipado")]
        for ln in lines[:11]:
            self.text(ln, "small", WHITE, (sp.x + 12, y))
            y += 16

        # grade da categoria do espaço selecionado
        cat = accm.SLOT_CAT[self.jw_slot]
        g = self.JW_GRID
        pygame.draw.rect(s, PANEL, g, border_radius=12)
        owned_n = sum(1 for a in accm.ORDER[cat] if a in R.acc_owned)
        self.text(L(f"{accm.cat_name(cat, 'en', True)}: {owned_n} / {len(accm.ORDER[cat])} found",
                    f"{accm.cat_name(cat, 'pt', True)}: {owned_n} / {len(accm.ORDER[cat])} encontrados"), "small",
                  YELLOW, (g.x + 12, g.y + 8))
        self.jw_fix_filter()
        self.draw_jw_filter(mouse)
        hover = None
        for aid, r in self.jw_cells():
            own = aid in R.acc_owned
            wearer, _sl = R.acc_wearer(aid)
            sel, hov = aid == self.jw_sel, r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hov else (30, 30, 40), r, border_radius=6)
            pygame.draw.rect(s, YELLOW if sel else (120, 220, 230) if wearer is m else (70, 70, 85), r,
                             2 if sel or wearer is m else 1, border_radius=6)
            s.blit(accm.icon(aid, 28, dim=not own), (r.x + 4, r.y + 4))
            nm = CLASSES[accm.neck_class(aid)]["name"] if cat == "neck" else accm.short_name(aid, lang)
            col = WHITE if own else (95, 95, 108)
            while len(nm) > 4 and self.fonts["small"].size(nm)[0] > r.w - 44:
                nm = nm[:-2].rstrip() + "…"
            self.text(nm, "small", col, (r.x + 36, r.y + 4))
            sub = (f"+{R.acc_owned[aid]}  " if own and R.acc_owned[aid] else "") + (wearer.name if wearer else "")
            if not own:   # onde consegue
                sub = self.acc_source(aid, short=True)
            self.text(sub, "small", (120, 220, 230) if wearer else (100, 100, 112), (r.x + 36, r.y + 19))
            if hov:
                hover = aid

        # detalhes do acessório selecionado
        d = self.JW_DETAIL
        pygame.draw.rect(s, PANEL, d, border_radius=12)
        aid = self.jw_sel if self.jw_sel in accm.ACC and accm.ACC[self.jw_sel]["cat"] == cat else None
        if aid is None:
            self.text(L("Click a slot on the left and then an accessory to see it here.",
                        "Clique num espaço à esquerda e depois num acessório para ver aqui."), "small", GREY,
                      (d.x + 16, d.y + 16))
        else:
            own = aid in R.acc_owned
            lv = R.acc_owned.get(aid, 0)
            s.blit(accm.icon(aid, 48, dim=not own), (d.x + 14, d.y + 14))
            self.text(accm.name(aid, lang) + (f"  +{lv}" if lv else ""), "normal", WHITE if own else GREY,
                      (d.x + 74, d.y + 14))
            self.text(accm.cat_name(cat, lang) + "  ·  " + self.acc_source(aid), "small", GREY, (d.x + 74, d.y + 42))
            y = d.y + 70
            for ln in self.wrap(accm.desc(aid, lv, lang), "small", d.w - 30)[:3]:
                self.text(ln, "small", WHITE if own else (130, 130, 140), (d.x + 16, y))
                y += 17
            if own and lv < accm.MAX_LV:
                room = max(1, (d.bottom - 54 - y) // 17)
                for ln in self.wrap(L(f"Next (+{lv + 1}): ", f"Próximo (+{lv + 1}): ") +
                                    accm.desc(aid, lv + 1, lang), "small", d.w - 30)[:room]:
                    self.text(ln, "small", (150, 190, 255), (d.x + 16, y + 2))
                    y += 17
            wearer, _sl = R.acc_wearer(aid)
            if not own:
                self.text(L("Not found yet.", "Ainda não encontrado."), "small", RED, (d.x + 16, d.bottom - 38))
            else:
                wtxt = (L(f"Worn by {wearer.name}", f"Usado por {wearer.name}") if wearer else
                        L("Not worn", "Ninguém está usando"))
                if cat == "neck":   # colares melhoram com os fragmentos da classe
                    cn = accm.neck_class(aid)
                    self.text(L(f"{tr(CLASSES[cn]['name'])} Fragments: ", f"Fragmentos de {tr(CLASSES[cn]['name'])}: ") +
                              prog.fmt_frag(R.fragments.get(cn, 0)), "small", (230, 170, 255), (d.right - 16, d.y + 16),
                              "topright")
                self.text(wtxt, "small", (120, 220, 230), (d.x + 16, d.bottom - 38))
                eqb, upb = self.jw_buttons()
                here = m.acc.get(self.jw_slot) == aid
                lab = (L("Unequip", "Tirar") if here else
                       L(f"Equip on {m.name}", f"Equipar em {m.name}"))
                self.button(eqb, lab, eqb.collidepoint(mouse), GREEN)
                if lv >= accm.MAX_LV:
                    self.button(upb, "MAX", False, GREEN, enabled=False)
                else:
                    cost = accm.upgrade_cost(lv, aid)
                    if cat == "neck":   # colares: fragmentos da classe
                        okc = R.fragments.get(accm.neck_class(aid), 0) + 1e-9 >= cost
                    else:
                        okc = R.acc_frags.get(cat, 0) >= cost
                    self.button(upb, L(f"Upgrade ({cost} frag.)", f"Melhorar ({cost} frag.)"),
                                upb.collidepoint(mouse) and okc, GREEN if okc else RED, enabled=okc)
        if self.jw_dd:   # dropdown do filtro por tag por cima da grade
            self.draw_jw_dropdown(mouse)
            hover = None
        if hover:
            own = hover in R.acc_owned
            tl = [(accm.name(hover, lang), YELLOW),
                  (accm.desc(hover, R.acc_owned.get(hover, 0), lang), WHITE if own else GREY)]
            if accm.tags(hover):
                tl.append((f"Tags: {tag_list_text(accm.tags(hover), lang)}", (120, 220, 200)))
            self.draw_tooltip(tl, mouse)
        self.text(L("Duplicates become category fragments (top right) to upgrade accessories (+1 to +5); necklaces "
                    "use their class fragments  ·  ESC back",
                    "Repetidos viram fragmentos da categoria (canto superior direito) para melhorar (+1 a +5); colares "
                    "usam os fragmentos da classe  ·  ESC volta"), "small", GREY, (W / 2, H - 16), "center")
        self.draw_toast()

    # ------------------------------------------------------------------ Masmorras (portal vermelho)
    dg_sel = 0
    dg_pick = None   # nível escolhido de cada masmorra

    def dg_cards(self):
        return [pygame.Rect(40 + i * 404, 112, 392, 572) for i in range(len(dgm.ORDER))]

    def dg_level(self, did):
        if self.dg_pick is None:
            self.dg_pick = {}
        top = self.roster.dungeon_lv.get(did, 1)
        lv = self.dg_pick.get(did, top)
        lv = max(1, min(top, lv))
        self.dg_pick[did] = lv
        return lv

    def dg_parts(self, card):
        """(seta -, seta +, botão iniciar) de um cartão."""
        minus = pygame.Rect(card.x + 20, card.y + 190, 44, 36)
        plus = pygame.Rect(card.right - 64, card.y + 190, 44, 36)
        start = pygame.Rect(card.x + 20, card.bottom - 58, card.w - 40, 44)
        return minus, plus, start

    def dg_change(self, did, d):
        self.dg_pick[did] = max(1, min(self.roster.dungeon_lv.get(did, 1), self.dg_level(did) + d))

    def dg_start(self, i):
        did = dgm.ORDER[i]
        self.start_run((did, self.dg_level(did)))

    def dungeons_event(self, ev):
        n = len(dgm.ORDER)
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            did = dgm.ORDER[self.dg_sel]
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif k in (pygame.K_LEFT, pygame.K_a):
                self.dg_sel = (self.dg_sel - 1) % n
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.dg_sel = (self.dg_sel + 1) % n
            elif k in (pygame.K_UP, pygame.K_w):
                self.dg_change(did, 1)
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.dg_change(did, -1)
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.dg_start(self.dg_sel)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            for i, card in enumerate(self.dg_cards()):
                if not card.collidepoint(ev.pos):
                    continue
                self.dg_sel = i
                did = dgm.ORDER[i]
                minus, plus, start = self.dg_parts(card)
                if minus.collidepoint(ev.pos):
                    self.dg_change(did, -1)
                elif plus.collidepoint(ev.pos):
                    self.dg_change(did, 1)
                elif start.collidepoint(ev.pos):
                    self.dg_start(i)
        return True

    def draw_dungeons(self):
        L = i18n.L
        lang = i18n.LANG
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        self.text(L("DUNGEONS", "MASMORRAS"), "big", (230, 80, 70), (40, 20))
        self.text(L("A long corridor with only Super Elites and Elite Squads, and a boss at the end (~1 to 1.5 min). "
                    "Clear a level to unlock the next one.",
                    "Um corredor longo só com Super Elites e Esquadrões de Elite, e um chefão no fim (~1 a 1,5 min). "
                    "Conclua um nível para liberar o próximo."), "small", GREY, (42, 84))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        if not hasattr(self, "_dg_prev"):
            self._dg_prev = {d: dgm.preview(d, 352, 80) for d in dgm.ORDER}
        tip = None
        for i, (did, card) in enumerate(zip(dgm.ORDER, self.dg_cards())):
            d = dgm.DUNGEONS[did]
            sel = i == self.dg_sel
            pygame.draw.rect(s, (40, 36, 48) if sel else PANEL, card, border_radius=12)
            pygame.draw.rect(s, d["color"] if sel else (70, 70, 85), card, 3 if sel else 1, border_radius=12)
            x, y = card.x + 20, card.y + 14
            self.text(dgm.name(did, lang), "normal", d["color"], (x, y))
            self.text(L("Main reward: ", "Recompensa principal: ") + d["reward_name"][1 if lang == "pt" else 0],
                      "small", WHITE, (x, y + 28))
            s.blit(self._dg_prev[did], (x, y + 50))
            pygame.draw.rect(s, (70, 70, 85), (x, y + 50, 352, 80), 1)
            yy = y + 136
            for ln in self.wrap(d["desc"][1 if lang == "pt" else 0], "small", card.w - 40)[:2]:
                self.text(ln, "small", GREY, (x, yy))
                yy += 16
            # nível
            lv = self.dg_level(did)
            top = self.roster.dungeon_lv.get(did, 1)
            minus, plus, start = self.dg_parts(card)
            self.button(minus, "<", minus.collidepoint(mouse), enabled=lv > 1)
            self.button(plus, ">", plus.collidepoint(mouse), enabled=lv < top)
            self.text(L(f"Level {lv}", f"Nível {lv}"), "normal", WHITE, ((minus.right + plus.x) / 2, minus.centery),
                      "center")
            self.text(L(f"Highest unlocked: Lv {top}", f"Maior liberado: Nv {top}"), "small", GREY,
                      ((minus.right + plus.x) / 2, minus.bottom + 2), "midtop")
            m = dgm.mults(lv)
            yy = minus.bottom + 22
            self.text(L("Difficulty", "Dificuldade"), "small", YELLOW, (x, yy))
            yy += 18
            self.text(L(f"Enemy HP x{m['hp']:.2f}  ·  Strength x{m['dmg']:.2f}  ·  Resist. x{m['res']:.2f}",
                        f"Vida x{m['hp']:.2f}  ·  Força x{m['dmg']:.2f}  ·  Resist. x{m['res']:.2f}"), "small",
                      WHITE, (x, yy))
            yy += 24
            self.text(L(f"Rewards (x{m['reward']:.2f})", f"Recompensas (x{m['reward']:.2f})"), "small", YELLOW, (x, yy))
            yy += 18
            for line in dgm.reward_lines(did, lv, lang):
                for ln in self.wrap("• " + line, "small", card.w - 40):
                    self.text(ln, "small", WHITE, (x, yy))
                    yy += 16
            yy += 8
            self.text(L("Accessory drops", "Drops de acessório"), "small", (120, 220, 230), (x, yy))
            yy += 20
            n_own = sum(1 for a in d["drops"] if a in self.roster.acc_owned)
            self.text(f"{n_own}/{len(d['drops'])}", "small", GREY, (card.right - 20, yy - 20), "topright")
            for k, aid in enumerate(d["drops"]):   # 1 de cada tipo: ícones lado a lado (passe o mouse para ver)
                own = aid in self.roster.acc_owned
                r = pygame.Rect(x + k * 70, yy, 40, 40)
                s.blit(accm.icon(aid, 40, dim=not own), r)
                if own:
                    pygame.draw.circle(s, (40, 160, 70), (r.right - 3, r.y + 4), 8)
                    pygame.draw.lines(s, WHITE, False, [(r.right - 8, r.y + 4), (r.right - 4, r.y + 8),
                                                        (r.right + 2, r.y)], 2)
                self.text(accm.cat_name(accm.ACC[aid]["cat"], lang), "small", WHITE if own else GREY,
                          (r.centerx, r.bottom + 2), "midtop")
                if r.inflate(20, 20).collidepoint(mouse):
                    tip = [(accm.name(aid, lang) + "  ·  " + accm.cat_name(accm.ACC[aid]["cat"], lang), YELLOW),
                           (L("Already found", "Já encontrado") if own else L("Not found yet", "Ainda não encontrado"),
                            GREEN if own else GREY), (accm.desc(aid, self.roster.acc_owned.get(aid, 0), lang), WHITE)]
            yy += 66
            self.button(start, L(f"Enter Lv {lv}", f"Entrar no Nv {lv}"), start.collidepoint(mouse) or sel, GREEN)
        if tip:
            self.draw_tooltip(tip, mouse)
        self.text(L("Left/right choose  ·  Up/down level  ·  ENTER enter  ·  ESC back",
                    "Esquerda/direita escolhe  ·  Cima/baixo nível  ·  ENTER entra  ·  ESC volta"), "small", GREY,
                  (W / 2, H - 16), "center")
        self.draw_toast()

    # ------------------------------------------------------------------ Altar of Mastery
    MA_COLS = 3
    mastery_cid = None

    def mastery_cells(self):
        cw, ch, gap = 252, 50, 4
        out = []
        for i, cid in enumerate(prog.CLASS_ORDER):
            row, col = divmod(i, self.MA_COLS)
            out.append((cid, pygame.Rect(470 + col * (cw + gap), 130 + row * (ch + gap), cw, ch)))
        return out

    def mastery_offer_rect(self):
        return pygame.Rect(60, 606, 370, 46)

    def mastery_sel(self):
        if self.mastery_cid not in CLASSES:
            self.mastery_cid = self.roster.hero.cls
        return self.mastery_cid

    def mastery_offer(self):
        cid = self.mastery_sel()
        err = self.roster.offer_altar(cid)
        L = i18n.L
        if err:
            self.toast(L(*err))
        else:
            self.toast(L(f"{tr(CLASSES[cid]['name'])} max level is now {prog.max_level(cid)} for every character!",
                         f"O nível máximo de {tr(CLASSES[cid]['name'])} agora é {prog.max_level(cid)} para todos!"))

    def mastery_event(self, ev):
        order = prog.CLASS_ORDER
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            i = order.index(self.mastery_sel())
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.mastery_offer()
            elif k in (pygame.K_LEFT, pygame.K_a):
                self.mastery_cid = order[(i - 1) % len(order)]
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.mastery_cid = order[(i + 1) % len(order)]
            elif k in (pygame.K_UP, pygame.K_w):
                self.mastery_cid = order[(i - self.MA_COLS) % len(order)]
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.mastery_cid = order[(i + self.MA_COLS) % len(order)]
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            if self.mastery_offer_rect().collidepoint(ev.pos):
                self.mastery_offer()
                return True
            for cid, r in self.mastery_cells():
                if r.collidepoint(ev.pos):
                    self.mastery_cid = cid
        return True

    def draw_mastery(self):
        L = i18n.L
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        self.text(L("ALTAR OF MASTERY", "ALTAR DA MAESTRIA"), "big", YELLOW, (40, 20))
        self.text(L("Offer class fragments to raise the max level of a class for every character",
                    "Ofereça fragmentos de classe para subir o nível máximo da classe para todos os personagens"),
                  "normal", GREY, (42, 84))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        cid = self.mastery_sel()
        frs = self.roster.fragments

        # painel esquerdo: nível do altar + classe selecionada
        panel = pygame.Rect(40, 130, 410, 536)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        lvl = prog.altar_level()
        self.text(L("Altar level", "Nível do altar"), "normal", GREY, (panel.centerx, panel.y + 16), "midtop")
        self.text(str(lvl), "big", (120, 220, 230), (panel.centerx, panel.y + 40), "midtop")
        self.text(L(f"Fragment drops +{lvl * prog.ALTAR_FRAG_STEP * 100:g}%  ·  each fragment is worth "
                    f"{prog.fmt_frag(prog.frag_gain())}",
                    f"Drop de fragmentos +{lvl * prog.ALTAR_FRAG_STEP * 100:g}%  ·  cada fragmento vale "
                    f"{prog.fmt_frag(prog.frag_gain())}"), "small", WHITE, (panel.centerx, panel.y + 94), "midtop")
        y = panel.y + 122
        note = L("Each level offered raises the class max level by 1 for every character. Those extra levels give "
                 "+1 of the class main attribute and +5 HP (balanced classes alternate STR, AGI and INT). Each "
                 "level offered also raises the altar level: +2.5% fragment drops. Costs double: 1, 2, 4, 8...",
                 "Cada nível oferecido sobe em 1 o nível máximo da classe para todos os personagens. Esses níveis "
                 "extras dão +1 do atributo principal da classe e +5 de vida (classes equilibradas alternam FOR, AGI "
                 "e INT). Cada nível oferecido também sobe o nível do altar: +2,5% de drop de fragmentos. O custo "
                 "dobra: 1, 2, 4, 8...")
        for ln in self.wrap(note, "small", panel.w - 40):
            self.text(ln, "small", (190, 190, 205), (panel.x + 20, y))
            y += 18
        c = CLASSES[cid]
        y += 14
        pygame.draw.line(s, (70, 70, 85), (panel.x + 20, y), (panel.right - 20, y))
        y += 14
        s.blit(si.class_icon(cid, 40), (panel.x + 20, y))
        self.text(c["name"], "normal", c["color"], (panel.x + 70, y + 2))
        n = int(prog.ALTAR.get(cid, 0))
        base = prog.base_max_level(cid)
        self.text(L(f"Offered: +{n}  ·  Max level {base} > {base + n}",
                    f"Oferecido: +{n}  ·  Nível máximo {base} > {base + n}"), "small", WHITE, (panel.x + 70, y + 26))
        y += 54
        attr = {"str": "STR", "agi": "AGI", "int": "INT"}
        nxt_attr = attr[prog.altar_attr(cid, base + n + 1)]
        if i18n.LANG == "pt":
            nxt_attr = nxt_attr.replace("STR", "FOR")
        self.text(L(f"Next level ({base + n + 1}): +1 {nxt_attr}, +5 HP",
                    f"Próximo nível ({base + n + 1}): +1 {nxt_attr}, +5 de vida"), "small", (150, 190, 255),
                  (panel.x + 20, y))
        y += 22
        have, cost = frs.get(cid, 0), prog.altar_cost(cid)
        self.text(L(f"You have {prog.fmt_frag(have)} {tr(c['name'])} Fragments",
                    f"Você tem {prog.fmt_frag(have)} Fragmentos de {tr(c['name'])}"), "small", (230, 170, 255),
                  (panel.x + 20, y))
        ok = have + 1e-9 >= cost
        ob = self.mastery_offer_rect()
        self.button(ob, L(f"Offer {cost} fragment{'s' if cost > 1 else ''}",
                          f"Oferecer {cost} fragmento{'s' if cost > 1 else ''}"),
                    ob.collidepoint(mouse) and ok, GREEN if ok else RED, enabled=ok)

        # grade de classes
        for k, r in self.mastery_cells():
            ck = CLASSES[k]
            sel, hov = k == cid, r.collidepoint(mouse)
            nk = int(prog.ALTAR.get(k, 0))
            hk = frs.get(k, 0)
            can = hk + 1e-9 >= prog.altar_cost(k)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hov else PANEL, r, border_radius=8)
            pygame.draw.rect(s, YELLOW if sel else (120, 220, 230) if nk else (70, 70, 85), r, 2 if sel or nk else 1,
                             border_radius=8)
            s.blit(si.class_icon(k, 30), (r.x + 8, r.y + 10))
            self.text(ck["name"], "small", ck["color"], (r.x + 46, r.y + 7))
            self.text(f"Lv {prog.max_level(k)}" + (f"  (+{nk})" if nk else ""), "small",
                      (120, 220, 230) if nk else GREY, (r.x + 46, r.y + 28))
            self.text(f"x{prog.fmt_frag(hk)}", "small", WHITE if hk else (90, 90, 100), (r.right - 10, r.y + 7),
                      "topright")
            self.text(L(f"cost {prog.altar_cost(k)}", f"custo {prog.altar_cost(k)}"), "small",
                      GREEN if can else (150, 110, 110), (r.right - 10, r.y + 28), "topright")
        self.text(L("Click a class, then Offer (or ENTER)  ·  Arrows navigate  ·  ESC back to the camp",
                    "Clique numa classe e depois em Oferecer (ou ENTER)  ·  Setas navegam  ·  ESC volta ao acampamento"),
                  "small", GREY, (W / 2, H - 22), "center")
        self.draw_toast()

    # ------------------------------------------------------------------ Altar of Trophies
    def altar_tab_rects(self):
        """Abas por bioma (5 troféus cada)."""
        n = len(BIOMES)
        w = (W - 510 - (n - 1) * 8) / n
        return [pygame.Rect(470 + i * (w + 8), 128, w, 34) for i in range(n)]

    def altar_tids(self, tab=None):
        import trophies as trophy
        tab = getattr(self, "altar_tab", 0) if tab is None else tab
        stages = BIOMES[tab]["stages"]
        return [tid for tid in trophy.ORDER if trophy.TROPHIES[tid][0] in stages]

    def altar_rows(self):
        return [(tid, pygame.Rect(470, 170 + i * 102, W - 510, 100)) for i, tid in enumerate(self.altar_tids())]

    def altar_toggle(self, tid):
        import trophies as trophy
        L = i18n.L
        if tid not in self.roster.trophies:
            st = STAGES[trophy.TROPHIES[tid][0]]
            self.toast(L(f"Defeat {st['boss']} to obtain this trophy.",
                         f"Derrote {tr(st['boss'])} para obter este troféu."))
            return
        on = self.roster.toggle_trophy(tid)
        self.toast(L(f"{trophy.name(tid)} {'activated' if on else 'deactivated'}  ·  Global Lv "
                     f"{len(self.roster.trophies_on)}",
                     f"{trophy.name(tid, 'pt')} {'ativado' if on else 'desativado'}  ·  Nível Global "
                     f"{len(self.roster.trophies_on)}"))

    def altar_event(self, ev):
        import trophies as trophy
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif pygame.K_1 <= ev.key <= pygame.K_5:
                tids = self.altar_tids()
                if ev.key - pygame.K_1 < len(tids):
                    self.altar_toggle(tids[ev.key - pygame.K_1])
            elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_TAB):
                d = -1 if ev.key in (pygame.K_LEFT, pygame.K_a) else 1
                self.altar_tab = (getattr(self, "altar_tab", 0) + d) % len(BIOMES)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            for i, r in enumerate(self.altar_tab_rects()):
                if r.collidepoint(ev.pos):
                    self.altar_tab = i
                    return True
            for tid, r in self.altar_rows():
                if r.collidepoint(ev.pos):
                    self.altar_toggle(tid)
        return True

    def draw_altar(self):
        import trophies as trophy
        L = i18n.L
        pt = i18n.LANG == "pt"
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        self.text(L("ALTAR OF TROPHIES", "ALTAR DOS TROFÉUS"), "big", YELLOW, (40, 20))
        self.text(L("Each active trophy adds its modifier to the run and +1 global difficulty level",
                    "Cada troféu ativo aplica o seu modificador na run e +1 nível de dificuldade global"),
                  "normal", GREY, (42, 84))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))

        # painel esquerdo: nível global e valores modificados
        lvl = len(self.roster.trophies_on)
        gm = trophy.global_mults(lvl)
        panel = pygame.Rect(40, 130, 410, 536)
        pygame.draw.rect(s, PANEL, panel, border_radius=12)
        self.text(L("Global difficulty", "Dificuldade global"), "normal", GREY, (panel.centerx, panel.y + 22), "midtop")
        self.text(L(f"Level {lvl}", f"Nível {lvl}"), "big", (255, 150, 120) if lvl else WHITE,
                  (panel.centerx, panel.y + 50), "midtop")
        self.text(L(f"{lvl} / {len(trophy.ORDER)} trophies active", f"{lvl} / {len(trophy.ORDER)} troféus ativos"),
                  "small", GREY, (panel.centerx, panel.y + 104), "midtop")
        rows = [(L("Enemy HP", "Vida dos inimigos"), gm["hp"], RED),
                (L("Enemy strength", "Força dos inimigos"), gm["dmg"], RED),
                (L("Enemy density", "Quantidade de inimigos"), gm["density"], RED),
                (L("EXP", "EXP"), gm["exp"], GREEN),
                (L("Gold", "Gold"), gm["gold"], GREEN),
                (L("Fragments", "Fragmentos"), gm["frag"], GREEN)]
        y = panel.y + 140
        for label, mult, col in rows:
            pygame.draw.rect(s, (30, 30, 40), (panel.x + 18, y, panel.w - 36, 34), border_radius=6)
            self.text(label, "normal", WHITE, (panel.x + 32, y + 17), "midleft")
            pct = (mult - 1) * 100
            self.text(f"+{pct:.0f}%" if pct else "—", "normal", col if pct else GREY, (panel.right - 32, y + 17),
                      "midright")
            y += 40
        y += 8
        note = L("Each level: enemies +15% HP, +10% strength and +10% density; +10% EXP and gold; "
                 "+10% fragments (each fragment picked up is worth 10% more).",
                 "Cada nível: inimigos com +15% de vida, +10% de força e +10% de quantidade; +10% de EXP e gold; "
                 "+10% de fragmentos (cada fragmento coletado vale 10% a mais).")
        for ln in self.wrap(note, "small", panel.w - 40):
            self.text(ln, "small", (190, 190, 205), (panel.x + 20, y))
            y += 18
        y += 10
        for ln in self.wrap(L("Bosses drop their trophy the first time they are defeated (Endless counts too).",
                              "Os chefões dropam o troféu na primeira vez que são derrotados (o Endless também vale)."),
                            "small", panel.w - 40):
            self.text(ln, "small", (200, 150, 255), (panel.x + 20, y))
            y += 18

        # abas por bioma
        tab = getattr(self, "altar_tab", 0)
        for i, r in enumerate(self.altar_tab_rects()):
            tids = self.altar_tids(i)
            got = sum(1 for t in tids if t in self.roster.trophies)
            on_n = sum(1 for t in tids if t in self.roster.trophies_on)
            hot = r.collidepoint(mouse)
            sel = i == tab
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hot else (32, 32, 42), r, border_radius=8)
            pygame.draw.rect(s, YELLOW if sel else (90, 90, 105), r, 2 if sel else 1, border_radius=8)
            # bolinha do bioma: enche de baixo para cima conforme os troféus dele ficam ativos (0 a 5)
            bc = (r.x + 18, r.centery)
            rad = 11
            col = BIOMES[i]["color"]
            pygame.draw.circle(s, (20, 20, 28), bc, rad)
            if on_n:
                frac = on_n / max(1, len(tids))
                fill = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(fill, col, (rad, rad), rad)
                cut = int(rad * 2 * (1 - frac))
                fill.fill((0, 0, 0, 0), (0, 0, rad * 2, cut))
                s.blit(fill, (bc[0] - rad, bc[1] - rad))
            pygame.draw.circle(s, col if got else (80, 80, 92), bc, rad, 1)
            name = tr(BIOMES[i]["name"]).replace("Abandoned Town", "Town").replace("Cidade Abandonada", "Cidade")
            tcol = YELLOW if sel else WHITE if got else GREY
            cnt = f"{got}/{len(tids)}"
            self.text(self.fit(name, "small", r.w - 54 - self.fonts["small"].size(cnt)[0]), "small", tcol,
                      (r.x + 36, r.centery), "midleft")
            self.text(cnt, "small", tcol, (r.right - 10, r.centery), "midright")
        # lista de troféus
        for i, (tid, r) in enumerate(self.altar_rows()):
            owned = tid in self.roster.trophies
            on = tid in self.roster.trophies_on
            hot = r.collidepoint(mouse)
            st = STAGES[trophy.TROPHIES[tid][0]]
            bg = (48, 44, 36) if on else (36, 36, 48) if owned else (26, 26, 32)
            pygame.draw.rect(s, bg, r, border_radius=10)
            bc = (255, 215, 120) if on else (YELLOW if hot and owned else (90, 90, 105) if owned else (55, 55, 65))
            pygame.draw.rect(s, bc, r, 3 if on or hot else 1, border_radius=10)
            ic = trophy.icon(tid, 60, dim=not owned)
            s.blit(ic, (r.x + 14, r.y + 14))
            self.text(str(i + 1), "small", GREY, (r.x + 8, r.y + 6))
            ncol = (255, 215, 120) if on else WHITE if owned else (110, 110, 125)
            self.text(trophy.name(tid, i18n.LANG), "normal", ncol, (r.x + 90, r.y + 8))
            src = L(f"Dropped by {st['boss']} ({st['name']})", f"Dropado por {tr(st['boss'])} ({tr(st['name'])})")
            self.text(src, "small", GREY if owned else (90, 90, 100), (r.x + 90, r.y + 32))
            dcol = (215, 215, 225) if owned else (100, 100, 112)
            for k, ln in enumerate(self.wrap(trophy.desc(tid, i18n.LANG), "small", r.w - 250)[:3]):
                self.text(ln, "small", dcol, (r.x + 90, r.y + 50 + k * 16))
            badge = pygame.Rect(r.right - 140, r.centery - 16, 124, 32)
            if owned:
                pygame.draw.rect(s, (70, 120, 60) if on else (50, 50, 62), badge, border_radius=8)
                self.text(L("ACTIVE", "ATIVO") if on else L("Inactive", "Inativo"), "normal",
                          WHITE if on else GREY, badge.center, "center")
            else:
                pygame.draw.rect(s, (40, 40, 48), badge, border_radius=8)
                self.text(L("Locked", "Bloqueado"), "normal", (110, 110, 125), badge.center, "center")
        self.text(L("Click a trophy (or press 1-5) to activate / deactivate  ·  Left/right: biome  ·  ESC back to the camp",
                    "Clique em um troféu (ou 1-5) para ativar / desativar  ·  Esquerda/direita: bioma  ·  ESC volta ao "
                    "acampamento"),
                  "small", GREY, (W / 2, H - 22), "center")
        self.draw_toast()

    def draw_inventory(self):
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        smith = getattr(self, "inv_mode", "chest") == "smith"
        self.text("BLACKSMITH" if smith else "INVENTORY", "big", YELLOW, (40, 20))
        self.text(i18n.L("Upgrade the weapon and helmet of each class (shared by every character)",
                         "Melhore a arma e o capacete de cada classe (vale para todos os personagens)")
                  if smith else "Fragments and gold stored in the chest", "normal", GREY, (42, 84))
        if smith:
            self.draw_gold((W - 240, 36))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        if smith:
            self.draw_smith_tabs(0, mouse)   # abas: armas e capacetes | armadura, calça e bota (materiais)
            self.draw_inventory_equipment(mouse)
        else:
            self.draw_gold((W - 240, 36))
            self.draw_chest_tabs(mouse)   # abas: fragmentos | materiais de monstros
            if self.chest_tab == 1:
                self.draw_chest_materials(mouse)
            else:
                self.draw_inventory_fragments(mouse)
        self.text("ESC back to the camp", "small", GREY, (W / 2, H - 22), "center")
        self.draw_toast()

    def draw_inventory_equipment(self, mouse):
        """Ferreiro: lista de classes à esquerda; à direita a arma e o capacete da classe selecionada.
        As melhorias são da CLASSE e valem para todos os personagens."""
        s = self.screen
        L = i18n.L
        cid = self.smith_sel()
        rows = self.smith_rows()
        lst = self.SMITH_LIST
        pygame.draw.rect(s, PANEL, lst, border_radius=12)
        self.text(L("Classes", "Classes"), "small", YELLOW, (lst.x + 14, lst.y + 8))
        self.text(L("Weapon / Helmet", "Arma / Capacete"), "small", GREY, (lst.right - 14, lst.y + 8), "topright")
        using = self.smith_users()
        prev = s.get_clip()
        s.set_clip(pygame.Rect(lst.x, lst.y + 30, lst.w, lst.h - 34))
        for k, r in rows:
            c = CLASSES[k]
            sel, hov = k == cid, r.collidepoint(mouse)
            known = any(m.is_unlocked(k) for m in self.roster.members)
            pygame.draw.rect(s, (60, 60, 85) if sel else (45, 45, 60) if hov else (32, 32, 44), r, border_radius=8)
            if sel:
                pygame.draw.rect(s, YELLOW, r, 2, border_radius=8)
            ic = si.class_icon(k, 24)
            if not known:
                ic = ic.copy()
                ic.set_alpha(80)
            s.blit(ic, (r.x + 8, r.y + 5))
            self.text(c["name"], "small", c["color"] if known else (100, 100, 112), (r.x + 40, r.y + 9))
            if using.get(k):   # alguém está nesta classe agora
                pygame.draw.circle(s, YELLOW, (r.x + 44 + self.fonts["small"].size(c["name"])[0] + 6, r.centery), 3)
            for j, slot in enumerate(eq.FIXED_SLOTS):
                lv = eq.gear_level(k, slot)
                x = r.right - 112 + j * 54
                s.blit(si.gear_icon(k, slot, 20), (x, r.y + 7))
                self.text(f"+{lv}", "small", (230, 170, 255) if lv >= eq.MAX_UPGRADE else GREEN if lv else GREY,
                          (x + 23, r.y + 9))
        s.set_clip(prev)
        n = len(prog.CLASS_ORDER)
        if n > self.SMITH_VISIBLE:   # barra de rolagem
            h = lst.h - 40
            bh = h * self.SMITH_VISIBLE / n
            yb = lst.y + 34 + (h - bh) * self.smith_scroll / max(1, n - self.SMITH_VISIBLE)
            pygame.draw.rect(s, GREY, (lst.right - 6, yb, 3, bh), border_radius=2)

        c = CLASSES[cid]
        lang = i18n.LANG
        p = self.INV_PANEL
        pygame.draw.rect(s, PANEL, p, border_radius=12)
        s.blit(si.class_icon(cid, 36), (p.x + 20, p.y + 16))
        self.text(L(f"{tr(c['name'])} equipment  ·  shared by every character", f"Equipamentos de {tr(c['name'])}  ·  "
                    f"compartilhados por todos os personagens"), "normal", YELLOW, (p.x + 66, p.y + 16))
        self.text(L(f"Upgrades belong to the class: every character who is a {tr(c['name'])} uses them, no matter "
                    f"who paid.", f"As melhorias são da classe: todo personagem que estiver como {tr(c['name'])} usa, "
                    f"não importa quem pagou."), "small", GREY, (p.x + 66, p.y + 44))
        frag = self.roster.fragments.get(cid, 0)
        for slot, r in self.inventory_item_rects().items():
            lv = eq.gear_level(cid, slot)
            pygame.draw.rect(s, (36, 36, 50), r, border_radius=10)
            pygame.draw.rect(s, c["color"] if lv else (80, 80, 95), r, 2, border_radius=10)
            s.blit(si.gear_icon(cid, slot, 64), (r.x + 16, r.y + 16))
            self.text("Weapon" if slot == "weapon" else "Helmet", "small", GREY, (r.x + 96, r.y + 16))
            self.text("Fixed to the class", "small", (110, 110, 125), (r.right - 14, r.y + 16), "topright")
            self.text(eq.item_name(cid, slot, lv, lang), "normal", c["color"], (r.x + 96, r.y + 38))
            self.text(f"+{lv} / +{eq.MAX_UPGRADE}", "small", GREEN if lv else GREY, (r.x + 96, r.y + 64))
            mb = eq.max_bonus_text(cid, slot, lang)
            y = r.y + 92
            for ln in self.wrap(L(f"At +10: {mb} (permanent, for every character)",
                                  f"No +10: {mb} (permanente, para todos os personagens)"), "small", r.w - 36):
                self.text(ln, "small", (230, 170, 255) if lv >= eq.MAX_UPGRADE else (150, 125, 185), (r.x + 18, y))
                y += 18
            y += 4
            if lv:
                cur = ", ".join(eq.bonus_lines(slot, lv, lang))
                for ln in self.wrap((f"Now: {cur}" if lang == "en" else f"Atual: {cur}"), "small", r.w - 36):
                    self.text(ln, "small", WHITE, (r.x + 18, y))
                    y += 18
            if lv < eq.MAX_UPGRADE:
                nxt = eq.bonus_lines(slot, lv + 1, lang)
                y += 4
                for ln in self.wrap(f"Next: {', '.join(nxt)}", "small", r.w - 36):
                    self.text(ln, "small", (150, 190, 255), (r.x + 18, y))
                    y += 18
            ub = self.inventory_upgrade_rect(slot)
            if lv >= eq.MAX_UPGRADE:
                self.button(ub, "MAX", False, GREEN, enabled=False)
            else:
                cost = eq.upgrade_cost(lv)
                gold = eq.gold_cost(lv)
                ok = frag + 1e-9 >= cost and self.roster.gold >= gold
                label = (f"Upgrade  ({cost} fragments + {gold} gold)" if lang == "en"
                         else f"Melhorar  ({cost} fragmentos + {gold} gold)")
                self.button(ub, label, ub.collidepoint(mouse) and ok, GREEN if ok else RED, enabled=ok)
        self.text(L(f"You have {prog.fmt_frag(frag)} {tr(c['name'])} Fragments",
                    f"Você tem {prog.fmt_frag(frag)} Fragmentos de {tr(c['name'])}"), "small", (230, 170, 255),
                  (p.x + 24, p.y + 356))
        # quem usa esta classe agora
        y = p.y + 388
        self.text(L("Characters using these items now", "Personagens usando estes itens agora"), "small", YELLOW,
                  (p.x + 24, y))
        y += 22
        x = p.x + 24
        users = using.get(cid, [])
        if not users:
            self.text(L(f"nobody is a {tr(c['name'])} right now - the upgrades wait for whoever becomes one",
                        f"ninguém está como {tr(c['name'])} agora - as melhorias esperam quem virar"), "small",
                      (110, 110, 125), (x, y))
        for m in users:
            w = 30 + self.fonts["small"].size(m.name)[0] + 22
            if x + w > p.right - 20:
                x, y = p.x + 24, y + 26
            draw_class_icon(s, m.cls, (x + 10, y + 7), 9, who=m.name, look=m.look, member=m)
            self.text(m.name, "small", WHITE if m.active else GREY, (x + 24, y))
            x += w
        self.text(L("Accessories (necklace, rings, bracer, trinkets): talk to the Jeweler at the camp.",
                    "Acessórios (colar, anéis, bracelete, berloques): fale com o Joalheiro do acampamento."),
                  "small", GREY, (p.x + 24, p.bottom - 30))

    # ---- ferreiro: lista de classes ----
    SMITH_LIST = pygame.Rect(32, 140, 320, 548)
    SMITH_ROW_H = 35
    SMITH_VISIBLE = 14
    smith_scroll = 0
    smith_cid = None

    def smith_sel(self):
        if self.smith_cid not in CLASSES:
            self.smith_cid = self.roster.hero.cls
            self.smith_show(self.smith_cid)
        return self.smith_cid

    def smith_show(self, cid):
        """Rola a lista para a classe aparecer."""
        i = prog.CLASS_ORDER.index(cid)
        if i < self.smith_scroll:
            self.smith_scroll = i
        elif i >= self.smith_scroll + self.SMITH_VISIBLE:
            self.smith_scroll = i - self.SMITH_VISIBLE + 1

    def smith_rows(self):
        lst = self.SMITH_LIST
        out = []
        for i, cid in enumerate(prog.CLASS_ORDER):
            vis = i - self.smith_scroll
            if 0 <= vis < self.SMITH_VISIBLE:
                out.append((cid, pygame.Rect(lst.x + 8, lst.y + 34 + vis * (self.SMITH_ROW_H + 1), lst.w - 18,
                                             self.SMITH_ROW_H)))
        return out

    def smith_users(self):
        out = {}
        for m in self.roster.members:
            out.setdefault(m.cls, []).append(m)
        return out

    def draw_inventory_fragments(self, mouse):
        s = self.screen
        frs = self.roster.fragments
        total = sum(frs.values())
        self.text(f"Class fragments: {prog.fmt_frag(total)}   ·   dropped by Elite enemies, used to upgrade each class's equipment",
                  "small", GREY, (W / 2, 662), "center")
        hover = None
        for cid, r in self.inventory_cells():
            n = frs.get(cid, 0)
            c = CLASSES[cid]
            hot = r.collidepoint(mouse)
            pygame.draw.rect(s, (55, 55, 75) if hot else PANEL, r, border_radius=10)
            pygame.draw.rect(s, c["color"] if n else (60, 60, 72), r, 2 if n else 1, border_radius=10)
            ic = si.class_icon(cid, 48)
            if not n:
                ic = ic.copy()
                ic.set_alpha(70)
            s.blit(ic, ic.get_rect(center=(r.centerx - 40, r.y + 40)))
            cx, cy = r.centerx - 2, r.y + 40
            col = c["color"] if n else (70, 70, 80)
            pts = [(cx, cy - 18), (cx + 12, cy), (cx, cy + 18), (cx - 12, cy)]
            pygame.draw.polygon(s, col, pts)
            pygame.draw.polygon(s, WHITE if n else (90, 90, 100), pts, 2)
            ntxt = f"x{prog.fmt_frag(n)}"
            self.text(ntxt, "normal" if len(ntxt) <= 4 else "small", WHITE if n else (90, 90, 100), (cx + 16, cy),
                      "midleft")
            self.text(c["name"], "small", c["color"] if n else (100, 100, 110),
                      (r.centerx, r.bottom - 26), "center")
            if hot:
                hover = (cid, n)
        # fragmentos de acessório (cópias repetidas), no espaço livre depois das classes
        L = i18n.L
        cells = self.inventory_cells()
        last = cells[-1][1]
        box = pygame.Rect(last.right + 9, last.y, W - 32 - last.right - 9, last.h)
        if box.w > 200:
            s = self.screen
            pygame.draw.rect(s, PANEL, box, border_radius=10)
            pygame.draw.rect(s, (120, 220, 230), box, 1, border_radius=10)
            self.text(L("Accessory fragments", "Fragmentos de acessório"), "small", (120, 220, 230),
                      (box.x + 12, box.y + 8))
            for i, cat in enumerate(accm.FRAG_CATS):
                y = box.y + 27 + i * 22
                s.blit(accm.cat_icon(cat, 20), (box.x + 12, y))
                self.text(accm.cat_name(cat, i18n.LANG, True), "small", WHITE, (box.x + 40, y + 3))
                self.text(f"x{self.roster.acc_frags.get(cat, 0)}", "small", WHITE, (box.right - 14, y + 3), "topright")
            if box.collidepoint(mouse) and not hover:
                self.draw_tooltip([(L("Accessory fragments", "Fragmentos de acessório"), YELLOW),
                                   (L("A duplicate accessory becomes a fragment of its category.",
                                      "Um acessório repetido vira um fragmento da categoria."), WHITE),
                                   (L("Used at the Jeweler to upgrade rings, bracers, trinkets and emblems (+1 to +5). "
                                      "Necklaces use class fragments.",
                                      "Usados no Joalheiro para melhorar anéis, braceletes, berloques e emblemas (+1 a "
                                      "+5). Os colares usam fragmentos de classe."), (150, 190, 255))], mouse)
        if hover:
            cid, n = hover
            name = CLASSES[cid]["name"]
            self.draw_tooltip([(f"{name} Fragment", YELLOW), (f"Owned: {prog.fmt_frag(n)}", WHITE),
                               (f"Dropped by Elite {name} enemies (any enemy can spawn as an elite of a class "
                                f"you have already unlocked).", GREY),
                               (f"Used to upgrade {name} weapon and helmet.", (150, 190, 255)),
                               (i18n.L(f"Also offered at the Altar of Mastery (+1 max level for every {name}) and "
                                       f"used to upgrade the {name}'s Necklace.",
                                       f"Também oferecido no Altar da Maestria (+1 nível máximo para todo {name}) e "
                                       f"usado para melhorar o Colar do {name}."),
                                (120, 220, 230))], mouse)

    def draw_config(self):
        self.draw_main_bg()   # mesmo fundo da tela inicial
        self.text("CONFIGURATIONS", "big", YELLOW, (W / 2, 110), "center")
        for i, (r, key) in enumerate(zip(self.config_rects(), self.CONFIG_ITEMS)):
            label, value = self.config_label(key)
            self.button(r, label, i == self.sel, value=value)
        self.text("Arrows navigate  ·  ENTER / left-right change  ·  ESC back", "small", GREY,
                  (W / 2, H - 30), "center")
