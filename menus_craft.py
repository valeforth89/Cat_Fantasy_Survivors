"""Telas do Altar of Greed (gold -> bônus permanentes) e do ferreiro: Armadura, Calça e Bota (materiais)."""
import pygame

from data import W, H, WHITE, GREY, DARK, PANEL, RED, GREEN, YELLOW, BIOMES, CLASSES
import i18n
import greed as grd
import crafting as crf
import skill_icons as si


def _L(en, pt):
    return i18n.L(en, pt)


class CraftMixin:
    # ================================================================== Baú: abas Fragmentos | Materiais
    chest_tab = 0

    def chest_tab_rects(self):
        return [pygame.Rect(470, 84, 200, 32), pygame.Rect(680, 84, 250, 32)]

    def draw_chest_tabs(self, mouse):
        labels = [_L("Fragments", "Fragmentos"), _L("Monster materials", "Materiais de monstros")]
        for i, (r, lab) in enumerate(zip(self.chest_tab_rects(), labels)):
            on = i == self.chest_tab
            hot = r.collidepoint(mouse)
            pygame.draw.rect(self.screen, (70, 64, 48) if on else (40, 40, 52), r, border_radius=8)
            pygame.draw.rect(self.screen, YELLOW if on or hot else GREY, r, 2 if on else 1, border_radius=8)
            self.text(lab, "small", YELLOW if on else WHITE, r.center, "center")

    def chest_tab_click(self, pos):
        for i, r in enumerate(self.chest_tab_rects()):
            if r.collidepoint(pos):
                self.chest_tab = i
                return True
        return False

    def chest_mat_cells(self):
        """Materiais em colunas (uma por bioma) x 5 linhas."""
        nb = len(BIOMES)
        gx, gy, ch = 10, 9, 92
        cw = (W - 64 - (nb - 1) * gx) // nb
        x0 = (W - (nb * cw + (nb - 1) * gx)) // 2
        out = []
        for i, mid in enumerate(crf.MAT_ORDER):
            col, row = divmod(i, 5)
            out.append((mid, pygame.Rect(x0 + col * (cw + gx), 162 + row * (ch + gy), cw, ch)))
        return out

    def draw_chest_materials(self, mouse):
        from data import ENEMY_NAMES
        s = self.screen
        lang = i18n.LANG
        mats = self.roster.materials
        cells = self.chest_mat_cells()
        for b in range(len(BIOMES)):
            r0 = cells[b * 5][1]
            bio = BIOMES[b]
            self.text(i18n.tr(bio["name"]), "small", bio["color"], (r0.x + 4, r0.y - 22))
        hover = None
        for mid, r in cells:
            m = crf.MAT[mid]
            n = mats.get(mid, 0)
            hot = r.collidepoint(mouse)
            pygame.draw.rect(s, (55, 55, 75) if hot else PANEL, r, border_radius=10)
            pygame.draw.rect(s, m["color"] if n else (60, 60, 72), r, 2 if n else 1, border_radius=10)
            ic = crf.material_icon(mid, 44)
            if not n:
                ic = ic.copy()
                ic.set_alpha(80)
            s.blit(ic, ic.get_rect(center=(r.x + 30, r.centery)))
            tw = r.w - 66
            self.text(self.fit(crf.mat_name(mid, lang), "small", tw), "small", WHITE if n else (110, 110, 120),
                      (r.x + 58, r.y + 14))
            self.text(f"x{n}", "normal", m["color"] if n else (90, 90, 100), (r.x + 58, r.y + 36))
            self.text(self.fit(_L("From: ", "De: ") + i18n.tr(ENEMY_NAMES.get(m["kind"], m["kind"])), "small", tw),
                      "small", GREY, (r.x + 58, r.y + 66))
            if hot:
                hover = mid
        tot = sum(mats.get(k, 0) for k in crf.MAT_ORDER)
        self.text(_L(f"Total: {tot} materials  ·  used at the Blacksmith to craft and upgrade armor, pants and boots",
                     f"Total: {tot} materiais  ·  usados no Ferreiro para criar e melhorar armaduras, calças e botas"),
                  "small", GREY, (W / 2, 676), "center")
        if hover:
            m = crf.MAT[hover]
            uses = [crf.name(iid, lang) + f" ({q})" for iid, it in crf.ITEMS.items()
                    for mm, q in it["recipe"].items() if mm == hover]
            lines = [(crf.mat_name(hover, lang), YELLOW),
                     (_L(f"Owned: {mats.get(hover, 0)}", f"Você tem: {mats.get(hover, 0)}"), WHITE),
                     (_L(f"Common enemies drop it rarely ({crf.DROP_NORMAL * 100:g}%), elites often and in larger "
                         f"amounts; the biome's bosses drop {crf.BOSS_QTY} of every material of the biome.",
                         f"Inimigos comuns dropam raramente ({crf.DROP_NORMAL * 100:g}%), elites com frequência e em "
                         f"maior quantidade; os chefões do bioma dropam {crf.BOSS_QTY} de cada material do bioma."),
                      GREY)]
            if uses:
                lines.append((_L("Recipes: ", "Receitas: ") + ", ".join(uses), (150, 190, 255)))
            lines.append((_L("Upgrades of these items also use it.", "As melhorias desses itens também usam."),
                          (150, 190, 255)))
            self.draw_tooltip(lines, mouse)

    # ================================================================== Altar of Greed
    GR_COLS = 3
    greed_sel = "atk"

    def greed_cells(self):
        cw, ch, gap = 376, 150, 14
        x0 = (W - (self.GR_COLS * cw + (self.GR_COLS - 1) * gap)) // 2
        out = []
        for i, sid in enumerate(grd.ORDER):
            row, col = divmod(i, self.GR_COLS)
            out.append((sid, pygame.Rect(x0 + col * (cw + gap), 150 + row * (ch + gap), cw, ch)))
        return out

    def greed_buy(self, sid):
        self.greed_sel = sid
        err = grd.buy(self.roster, sid)
        if err:
            self.toast(_L(*err))
        else:
            lang = i18n.LANG
            self.toast(_L(f"{grd.name(sid)} Lv {grd.level(sid)}: {grd.bonus_text(sid, 'en')} for the whole party!",
                          f"{grd.name(sid, 'pt')} Nv {grd.level(sid)}: {grd.bonus_text(sid, 'pt')} para toda a party!"))

    def greed_event(self, ev):
        order = grd.ORDER
        if self.greed_sel not in order:
            self.greed_sel = order[0]
        i = order.index(self.greed_sel)
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.greed_buy(self.greed_sel)
            elif k in (pygame.K_LEFT, pygame.K_a):
                self.greed_sel = order[(i - 1) % len(order)]
            elif k in (pygame.K_RIGHT, pygame.K_d):
                self.greed_sel = order[(i + 1) % len(order)]
            elif k in (pygame.K_UP, pygame.K_w):
                self.greed_sel = order[(i - self.GR_COLS) % len(order)]
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.greed_sel = order[(i + self.GR_COLS) % len(order)]
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            for sid, r in self.greed_cells():
                if r.collidepoint(ev.pos):
                    self.greed_buy(sid)
                    return True
        elif ev.type == pygame.MOUSEMOTION:
            for sid, r in self.greed_cells():
                if r.collidepoint(ev.pos):
                    self.greed_sel = sid
        return True

    def draw_greed(self):
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        lang = i18n.LANG
        self.text(_L("ALTAR OF GREED", "ALTAR DA GANÂNCIA"), "big", YELLOW, (40, 20))
        self.text(_L("Spend gold on permanent bonuses for the WHOLE party. Each stat costs 40% more per level: "
                     "spreading the gold is cheaper.",
                     "Gaste gold em bônus permanentes para a party INTEIRA. Cada atributo custa 40% a mais por nível: "
                     "espalhar o gold sai mais barato."), "small", GREY, (42, 84))
        self.text(_L(f"Gold spent on the altar: {grd.spent()}", f"Gold gasto no altar: {grd.spent()}"), "small",
                  (230, 200, 120), (42, 106))
        self.draw_gold((W - 240, 36))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        for sid, r in self.greed_cells():
            st = grd.STATS[sid]
            sel = sid == self.greed_sel
            lv, mx = grd.level(sid), grd.max_level(sid)
            maxed = grd.is_maxed(sid)
            cost = grd.cost(sid)
            can = not maxed and self.roster.gold >= cost
            pygame.draw.rect(s, (52, 48, 40) if sel else PANEL, r, border_radius=12)
            pygame.draw.rect(s, YELLOW if sel else (90, 84, 70), r, 3 if sel else 1, border_radius=12)
            s.blit(si._render(st[7], st[8], (230, 230, 240), 56), (r.x + 16, r.y + 16))
            self.text(grd.name(sid, lang), "normal", WHITE, (r.x + 86, r.y + 14))
            lvtxt = _L(f"Lv {lv}", f"Nv {lv}") + (f" / {mx}" if mx else "")
            self.text(lvtxt, "normal", GREEN if maxed else (230, 200, 120), (r.right - 16, r.y + 14), "topright")
            self.text(_L("Now: ", "Agora: ") + (grd.bonus_text(sid, lang) if lv else "-"), "small", GREY,
                      (r.x + 86, r.y + 48))
            if not maxed:
                self.text(_L("Next: ", "Próximo: ") + grd.bonus_text(sid, lang, lv + 1), "small", (150, 230, 160),
                          (r.x + 86, r.y + 68))
            if mx:   # barrinha dos níveis (stats com limite)
                self.bar(r.x + 86, r.y + 92, r.w - 102, 8, lv / mx, GREEN if maxed else (230, 190, 70))
            br = pygame.Rect(r.x + 16, r.bottom - 44, r.w - 32, 34)
            if maxed:
                self.text(_L("MAX", "MÁXIMO"), "normal", GREEN, br.center, "center")
            else:
                hot = br.collidepoint(mouse)
                pygame.draw.rect(s, (70, 60, 30) if hot and can else DARK, br, border_radius=8)
                pygame.draw.rect(s, YELLOW if can else (90, 90, 100), br, 2 if can else 1, border_radius=8)
                self.text(_L(f"Buy  -  {cost} gold", f"Comprar  -  {cost} gold"), "normal",
                          YELLOW if can else (120, 110, 100), br.center, "center")
        self.text(_L("Click a stat (or arrows + ENTER) to buy · ESC back",
                     "Clique num atributo (ou setas + ENTER) para comprar · ESC volta"), "small", GREY,
                  (W / 2, H - 22), "center")
        self.draw_toast()

    # ================================================================== Ferreiro: Armadura, Calça e Bota
    craft_sel = "wolf_vest"

    def smith_tab_rects(self):
        return [pygame.Rect(40, 108, 250, 28), pygame.Rect(300, 108, 290, 28)]

    def draw_smith_tabs(self, active, mouse):
        labels = [_L("Weapons & Helmets", "Armas e Capacetes"), _L("Armor, Pants & Boots", "Armadura, Calça e Bota")]
        for i, (r, lab) in enumerate(zip(self.smith_tab_rects(), labels)):
            on = i == active
            hot = r.collidepoint(mouse)
            pygame.draw.rect(self.screen, (70, 64, 48) if on else (40, 40, 52), r, border_radius=8)
            pygame.draw.rect(self.screen, YELLOW if on or hot else GREY, r, 2 if on else 1, border_radius=8)
            self.text(lab, "small", YELLOW if on else WHITE, r.center, "center")

    def smith_tab_click(self, pos):
        """Clique nas abas do ferreiro. Retorna True se trocou de aba."""
        r0, r1 = self.smith_tab_rects()
        if r1.collidepoint(pos) and self.state != "craft":
            self.go("craft")
            return True
        if r0.collidepoint(pos) and self.state == "craft":
            self.inv_mode = "smith"
            self.go("inventory")
            return True
        return False

    CR_LIST = pygame.Rect(32, 152, 420, 540)
    CR_PANEL = pygame.Rect(468, 152, W - 500, 540)

    def craft_rows(self):
        out = []
        y = self.CR_LIST.y + 4
        for b in range(len(BIOMES)):   # 5 biomas x 3 itens: linhas de uma linha só para caber
            y += 18
            for iid in crf.ORDER:
                if crf.ITEMS[iid]["biome"] == b:
                    out.append((iid, pygame.Rect(self.CR_LIST.x + 8, y, self.CR_LIST.w - 16, 26)))
                    y += 28
            y += 2
        return out

    def craft_member_rects(self):
        p = self.CR_PANEL
        members = self.roster.active()
        w = (p.w - 48 - 8 * (len(members) - 1)) // max(1, len(members))
        return [(m, pygame.Rect(p.x + 24 + i * (w + 8), p.y + 410, w, 56)) for i, m in enumerate(members)]

    def craft_button_rect(self):
        p = self.CR_PANEL
        return pygame.Rect(p.right - 300, p.y + 318, 276, 44)

    def craft_event(self, ev):
        order = crf.ORDER
        if self.craft_sel not in order:
            self.craft_sel = order[0]
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            i = order.index(self.craft_sel)
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.go("hub")
            elif k in (pygame.K_UP, pygame.K_w):
                self.craft_sel = order[(i - 1) % len(order)]
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.craft_sel = order[(i + 1) % len(order)]
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.craft_do()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.inventory_back_rect().collidepoint(ev.pos):
                self.go("hub")
                return True
            if self.smith_tab_click(ev.pos):
                return True
            for iid, r in self.craft_rows():
                if r.collidepoint(ev.pos):
                    self.craft_sel = iid
                    return True
            if self.craft_button_rect().collidepoint(ev.pos):
                self.craft_do()
                return True
            iid = self.craft_sel
            for m, r in self.craft_member_rects():
                if r.collidepoint(ev.pos):
                    if iid not in crf.OWNED:
                        self.toast(_L("Craft this item first.", "Crie este item primeiro."))
                    elif m.craft.get(crf.ITEMS[iid]["slot"]) == iid:
                        crf.equip(self.roster, m, None, crf.ITEMS[iid]["slot"])
                        self.toast(_L(f"{m.name} took off {crf.name(iid)}.", f"{m.name} tirou {crf.name(iid, 'pt')}."))
                    else:
                        crf.equip(self.roster, m, iid)
                        self.toast(_L(f"{m.name} is wearing {crf.name(iid)}.",
                                      f"{m.name} está usando {crf.name(iid, 'pt')}."))
                    return True
        return True

    def craft_do(self):
        iid = self.craft_sel
        new = iid not in crf.OWNED
        err = crf.craft(self.roster, iid)
        if err:
            self.toast(_L(*err))
        elif new:
            self.toast(_L(f"Crafted {crf.name(iid)}!", f"{crf.name(iid, 'pt')} criado!"))
        else:
            self.toast(_L(f"{crf.name(iid)} upgraded to +{crf.OWNED[iid]}!",
                          f"{crf.name(iid, 'pt')} melhorado para +{crf.OWNED[iid]}!"))

    def draw_craft(self):
        s = self.screen
        self.menu_bg()
        mouse = self.mouse_pos()
        lang = i18n.LANG
        self.text("BLACKSMITH", "big", YELLOW, (40, 20))
        self.text(_L("Craft armor, pants and boots with the materials monsters drop (each item is unique: one "
                     "character at a time)",
                     "Crie armaduras, calças e botas com os materiais que os monstros dropam (cada item é único: um "
                     "personagem por vez)"), "small", GREY, (42, 84))
        self.draw_gold((W - 240, 36))
        back = self.inventory_back_rect()
        self.button(back, "Back", back.collidepoint(mouse))
        self.draw_smith_tabs(1, mouse)
        if self.craft_sel not in crf.ITEMS:
            self.craft_sel = crf.ORDER[0]
        # ---- lista ----
        lst = self.CR_LIST
        pygame.draw.rect(s, PANEL, lst, border_radius=12)
        rows = self.craft_rows()
        shown = set()
        for iid, r in rows:
            it = crf.ITEMS[iid]
            if it["biome"] not in shown:
                shown.add(it["biome"])
                b = BIOMES[it["biome"]]
                self.text(i18n.tr(b["name"]), "small", b["color"], (r.x + 4, r.y - 18))
            sel, hov = iid == self.craft_sel, r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 56, 46) if sel else (44, 44, 56) if hov else (34, 34, 44), r, border_radius=8)
            if sel:
                pygame.draw.rect(s, YELLOW, r, 2, border_radius=8)
            owned = iid in crf.OWNED
            ic = crf.item_icon(iid, 24)
            if not owned:
                ic = ic.copy()
                ic.set_alpha(110)
            s.blit(ic, (r.x + 5, r.y + 1))
            w = crf.wearer(self.roster, iid) if owned else None
            right = (f"{w.name}  " if w is not None else "") + (f"+{crf.OWNED[iid]}" if owned else _L("new", "novo"))
            rw = self.fonts["small"].size(right)[0]
            self.text(self.fit(crf.name(iid, lang), "small", r.w - 50 - rw), "small",
                      WHITE if owned else (150, 150, 160), (r.x + 36, r.centery), "midleft")
            self.text(right, "small", (230, 200, 120) if owned else (150, 230, 160), (r.right - 10, r.centery),
                      "midright")
        # ---- detalhes ----
        p = self.CR_PANEL
        pygame.draw.rect(s, PANEL, p, border_radius=12)
        iid = self.craft_sel
        it = crf.ITEMS[iid]
        owned = iid in crf.OWNED
        lv = crf.OWNED.get(iid, 0)
        s.blit(crf.item_icon(iid, 72), (p.x + 24, p.y + 20))
        self.text(crf.name(iid, lang) + (f"  +{lv}" if owned else ""), "big", WHITE, (p.x + 112, p.y + 18))
        b = BIOMES[it["biome"]]
        self.text(crf.SLOT_NAME[it["slot"]][1 if lang == "pt" else 0] + "  ·  " + i18n.tr(b["name"]), "small",
                  b["color"], (p.x + 114, p.y + 74))
        self.text(it["desc"][1 if lang == "pt" else 0], "small", GREY, (p.x + 114, p.y + 94))
        # status agora -> próximo
        y = p.y + 128
        self.text(_L("Bonuses", "Bônus"), "normal", YELLOW, (p.x + 24, y))
        cur = crf.effects_lines(iid, lv, lang)
        nxt = crf.effects_lines(iid, lv + 1, lang) if owned and lv < crf.MAX_LV else None
        for k, ln in enumerate(cur):
            self.text(ln, "small", WHITE if owned else (170, 170, 180), (p.x + 30, y + 30 + k * 20))
            if nxt:
                self.text("->  " + nxt[k], "small", (150, 230, 160), (p.x + 300, y + 30 + k * 20))
        # receita
        y = p.y + 210
        if owned and lv >= crf.MAX_LV:
            self.text(_L("Fully upgraded (+10)!", "Melhorado ao máximo (+10)!"), "normal", GREEN, (p.x + 24, y))
        else:
            mats, gold = crf.cost(iid)
            self.text(_L("Upgrade cost" if owned else "Recipe", "Custo da melhoria" if owned else "Receita"), "normal",
                      YELLOW, (p.x + 24, y))
            for k, (mid, q) in enumerate(mats.items()):
                have = self.roster.materials.get(mid, 0)
                x = p.x + 30 + k * 230
                s.blit(crf.material_icon(mid, 36), (x, y + 32))
                self.text(crf.mat_name(mid, lang), "small", WHITE, (x + 44, y + 32))
                self.text(f"{have} / {q}", "small", GREEN if have >= q else RED, (x + 44, y + 50))
            self.text(f"+ {gold} gold", "small", YELLOW if self.roster.gold >= gold else RED, (p.x + 30, y + 80))
            br = self.craft_button_rect()
            self.button(br, _L("Upgrade (+1)", "Melhorar (+1)") if owned else _L("Craft", "Criar"),
                        br.collidepoint(mouse), YELLOW)
        # quem usa
        y = p.y + 382
        self.text(_L("Wear it (click a party member; click again to take it off)",
                     "Usar (clique num membro da party; clique de novo para tirar)"), "small", YELLOW, (p.x + 24, y))
        for m, r in self.craft_member_rects():
            on = m.craft.get(it["slot"]) == iid
            hot = r.collidepoint(mouse)
            pygame.draw.rect(s, (50, 70, 50) if on else (44, 44, 56) if hot else (34, 34, 44), r, border_radius=8)
            pygame.draw.rect(s, GREEN if on else YELLOW if hot else (80, 80, 92), r, 2 if on or hot else 1,
                             border_radius=8)
            from icons import draw_class_icon
            draw_class_icon(s, m.cls, (r.x + 22, r.centery + 2), 12, who=m.name, look=m.look, member=m, shadow=False)
            self.text(m.name, "small", WHITE, (r.x + 42, r.y + 8))
            cur_i = m.craft.get(it["slot"])
            txt = crf.name(cur_i, lang) if cur_i in crf.ITEMS else "-"
            while len(txt) > 4 and self.fonts["small"].size(txt)[0] > r.w - 48:   # cabe no cartão
                txt = txt[:-2].rstrip() + "…" if not txt.endswith("…") else txt[:-2].rstrip() + "…"
            self.text(txt, "small", GREEN if on else GREY, (r.x + 42, r.y + 28))
        # materiais do bioma
        y = p.bottom - 52
        self.text(_L("Materials of this biome:", "Materiais deste bioma:"), "small", GREY, (p.x + 24, y + 12))
        kinds = [k for k in b["enemies"].values() if k in crf.MATERIALS]
        for k, kind in enumerate(kinds):
            mid = crf.MATERIALS[kind][0]
            x = p.x + 210 + k * 100
            s.blit(crf.material_icon(mid, 28), (x, y + 4))
            self.text(str(self.roster.materials.get(mid, 0)), "small", WHITE, (x + 34, y + 10))
            if pygame.Rect(x, y + 4, 28, 28).collidepoint(mouse):
                self.draw_tooltip([(crf.mat_name(mid, lang), YELLOW),
                                   (_L("From: ", "De: ") + i18n.tr(self.enemy_label(kind)), GREY)],
                                  mouse)
        self.text(_L("Arrows choose · ENTER craft/upgrade · ESC back", "Setas escolhem · ENTER cria/melhora · ESC volta"),
                  "small", GREY, (W / 2, H - 14), "center")
        self.draw_toast()

    def enemy_label(self, kind):
        from data import ENEMY_NAMES
        return ENEMY_NAMES.get(kind, kind)
