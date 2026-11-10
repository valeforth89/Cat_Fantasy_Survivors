"""Equipamentos de materiais (Ferreiro): roupa/armadura, calça e bota.

- Cada monstro comum dropa o SEU material (Wolf -> Wolf Fur, Skeleton -> Skeleton Bone...). Elites dropam mais;
  os chefões dropam um punhado dos materiais do bioma deles.
- Com os materiais de cada bioma dá para criar 1 roupa, 1 calça e 1 bota (15 itens no total) e melhorá-los até +10
  gastando mais materiais (cada nível: +12% nos valores; +10 = 2,2x).
- Cada item é ÚNICO na conta: só um personagem da party pode usar cada um (como os acessórios), e cada personagem
  usa no máximo 1 roupa, 1 calça e 1 bota.
- Identidade: roupa = defensiva; calça = metade defesa, metade utilidade; bota = só utilidade / qualidade de vida.
  Os itens têm o mesmo "orçamento" de status em todos os biomas (o do bioma 4 não é melhor que o do bioma 1, só
  diferente).
"""
import math
import random

import pygame

from class_passives import effect_text

MAX_LV = 10
LV_STEP = 0.12
SLOTS = ("body", "legs", "feet")
SLOT_NAME = {"body": ("Armor", "Armadura"), "legs": ("Pants", "Calça"), "feet": ("Boots", "Bota")}

# chance de dropar o material ao matar (por tipo de inimigo); elites e chefões dropam mais
DROP_NORMAL = 0.02
DROP_ELITE = 0.4
ELITE_QTY = 2
SUPER_QTY = 4
BOSS_QTY = 3          # o chefão dropa isso de CADA material do bioma

# inimigo -> (id do material, nome EN, nome PT, desenho do ícone, cor)
MATERIALS = {
    # Floresta
    "morcego": ("bat_wing", "Bat Wing", "Asa de Morcego", "wing", (130, 80, 160)),
    "lobo": ("wolf_fur", "Wolf Fur", "Pelo de Lobo", "fur", (150, 150, 165)),
    "javali": ("boar_hide", "Boar Hide", "Couro de Javali", "hide", (150, 95, 60)),
    "esqueleto": ("skel_bone", "Skeleton Bone", "Osso de Esqueleto", "bone", (230, 222, 205)),
    "zumbi": ("rot_cloth", "Rotten Cloth", "Pano Podre", "cloth", (110, 140, 80)),
    # Cidade Abandonada
    "rato": ("rat_tail", "Rat Tail", "Rabo de Rato", "tail", (215, 150, 155)),
    "cao": ("hound_fang", "Hound Fang", "Presa de Cão", "fang", (240, 235, 220)),
    "bruto": ("bandit_leather", "Bandit Leather", "Couro de Bandido", "hide", (110, 70, 45)),
    "carnical": ("ghoul_claw", "Ghoul Claw", "Garra de Carniçal", "claw", (170, 175, 150)),
    "espectro": ("ectoplasm", "Ectoplasm", "Ectoplasma", "goo", (150, 200, 230)),
    # Catedral
    "fatuo": ("wisp_spark", "Wisp Spark", "Centelha de Fogo-Fátuo", "spark", (140, 200, 255)),
    "cultista": ("cultist_silk", "Cultist Silk", "Seda de Cultista", "cloth", (150, 40, 50)),
    "gargula": ("gargoyle_stone", "Gargoyle Stone", "Pedra de Gárgula", "stone", (130, 130, 140)),
    "armadura": ("haunted_steel", "Haunted Steel", "Aço Assombrado", "ingot", (170, 180, 200)),
    "serafim": ("fallen_feather", "Fallen Feather", "Pena Caída", "feather", (90, 80, 110)),
    # Subterrâneo
    "besouro": ("beetle_shell", "Beetle Shell", "Carapaça de Besouro", "shell", (70, 100, 140)),
    "goblin": ("goblin_ore", "Goblin Ore", "Minério Goblin", "ore", (190, 150, 60)),
    "golem": ("golem_core", "Golem Core", "Núcleo de Golem", "core", (255, 150, 60)),
    "gosma": ("slime_gel", "Slime Gel", "Gel de Gosma", "goo", (110, 200, 120)),
    "verme": ("wyrm_crystal", "Wyrm Crystal", "Cristal de Wyrm", "crystal", (150, 220, 255)),
    # Inferno
    "diabrete": ("imp_horn", "Imp Horn", "Chifre de Diabrete", "horn", (200, 70, 55)),
    "cao_inferno": ("hell_ember", "Hellhound Ember", "Brasa de Cão Infernal", "spark", (255, 140, 40)),
    "demonio": ("demon_hide", "Demon Hide", "Couro de Demônio", "hide", (150, 45, 45)),
    "salamandra": ("salamander_scale", "Salamander Scale", "Escama de Salamandra", "scale", (240, 140, 50)),
    "bruxo": ("warlock_sigil", "Warlock Sigil", "Sigilo do Bruxo", "sigil", (170, 80, 200)),
}
MAT = {m[0]: dict(id=m[0], kind=k, name=(m[1], m[2]), icon=m[3], color=m[4]) for k, m in MATERIALS.items()}
MAT_ORDER = [m[0] for m in MATERIALS.values()]

# item: slot, bioma (índice em BIOMES), nomes, efeitos no +0, receita {material: quantidade}, cor
ITEMS = {}


def _item(iid, slot, biome, en, pt, eff, recipe, color, desc_en, desc_pt):
    ITEMS[iid] = dict(id=iid, slot=slot, biome=biome, name=(en, pt), eff=eff, recipe=recipe, color=color,
                      desc=(desc_en, desc_pt))


# ---- Floresta: sustento e mobilidade ----
_item("wolf_vest", "body", 0, "Wolfhide Vest", "Colete de Pele de Lobo", {"hp_pct": 6, "regen5": 3},
      {"wolf_fur": 10, "rot_cloth": 6, "skel_bone": 4}, (150, 150, 165),
      "Sustain: more max HP and regeneration.", "Sustento: mais vida máxima e regeneração.")
_item("boar_trousers", "legs", 0, "Boar-hide Trousers", "Calça de Couro de Javali", {"armor": 3, "speed": 6},
      {"boar_hide": 10, "wolf_fur": 5, "bat_wing": 4}, (150, 95, 60),
      "Sturdy and light: armor and movement speed.", "Resistente e leve: armadura e velocidade.")
_item("batwing_boots", "feet", 0, "Bat-wing Boots", "Botas de Asa de Morcego", {"speed": 9},
      {"bat_wing": 10, "boar_hide": 5, "skel_bone": 4}, (130, 80, 160),
      "Pure speed.", "Velocidade pura.")
# ---- Cidade Abandonada: esquiva e coleta ----
_item("bandit_coat", "body", 1, "Bandit Leather Coat", "Casaco de Couro de Bandido", {"armor": 4, "dodge": 4},
      {"bandit_leather": 10, "ghoul_claw": 5, "ectoplasm": 4}, (110, 70, 45),
      "Evasive: armor and dodge.", "Evasivo: armadura e esquiva.")
_item("ratcatcher_pants", "legs", 1, "Ratcatcher Pants", "Calça de Caçador de Ratos", {"dodge": 3, "magnet": 25},
      {"rat_tail": 10, "bandit_leather": 5, "hound_fang": 4}, (215, 150, 155),
      "Dodge and a bigger pickup range.", "Esquiva e alcance de coleta maior.")
_item("hound_runners", "feet", 1, "Hound Runners", "Corredoras do Cão", {"speed": 5, "magnet": 15},
      {"hound_fang": 10, "rat_tail": 5, "ectoplasm": 4}, (240, 235, 220),
      "Speed and pickup range.", "Velocidade e alcance de coleta.")
# ---- Catedral: redução de dano e duração ----
_item("haunted_plate", "body", 2, "Haunted Plate", "Placa Assombrada", {"defense": 4, "mres": 2.5},
      {"haunted_steel": 10, "gargoyle_stone": 5, "wisp_spark": 4}, (170, 180, 200),
      "Damage reduction and magic defense.", "Redução de dano e defesa mágica.")
_item("silk_leggings", "legs", 2, "Cultist Silk Leggings", "Calça de Seda de Cultista", {"mres": 3, "duration": 7},
      {"cultist_silk": 10, "haunted_steel": 4, "fallen_feather": 4}, (150, 40, 50),
      "Magic defense and longer skill / buff duration.", "Defesa mágica e mais duração de habilidades e bônus.")
_item("feather_sandals", "feet", 2, "Feather Sandals", "Sandálias de Pena", {"duration": 5, "heal": 6},
      {"fallen_feather": 10, "cultist_silk": 5, "wisp_spark": 4}, (90, 80, 110),
      "Longer durations and stronger healing.", "Durações maiores e curas mais fortes.")
# ---- Subterrâneo: armadura bruta e alcance ----
_item("beetle_carapace", "body", 3, "Beetle Carapace", "Carapaça de Besouro", {"armor": 5, "hp_flat": 45},
      {"beetle_shell": 10, "goblin_ore": 5, "golem_core": 4}, (70, 100, 140),
      "Heavy: lots of armor and flat HP.", "Pesada: muita armadura e vida fixa.")
_item("miner_overalls", "legs", 3, "Miner Overalls", "Macacão de Minerador", {"hp_pct": 4, "area": 5},
      {"goblin_ore": 10, "beetle_shell": 5, "wyrm_crystal": 3}, (190, 150, 60),
      "Max HP and a bigger area for skills.", "Vida máxima e área maior nas habilidades.")
_item("slime_boots", "feet", 3, "Slime-step Boots", "Botas de Gosma", {"range": 5, "magnet": 12},
      {"slime_gel": 10, "wyrm_crystal": 4, "goblin_ore": 4}, (110, 200, 120),
      "Range for skills and pickup range.", "Alcance das habilidades e alcance de coleta.")

# ---- Inferno: dano e crítico ----
_item("demon_cuirass", "body", 4, "Demonhide Cuirass", "Couraça de Couro de Demônio", {"armor": 3, "dmg": 4},
      {"demon_hide": 10, "imp_horn": 6, "hell_ember": 4}, (150, 45, 45),
      "Offensive armor: armor and damage.", "Armadura ofensiva: armadura e dano.")
_item("salamander_leggings", "legs", 4, "Salamander Leggings", "Calça de Escama de Salamandra",
      {"mres": 2, "dot_dmg": 8}, {"salamander_scale": 10, "demon_hide": 5, "warlock_sigil": 3}, (230, 120, 40),
      "Magic defense and stronger damage over time.", "Defesa mágica e dano contínuo mais forte.")
_item("hellhound_treads", "feet", 4, "Hellhound Treads", "Botas do Cão Infernal", {"speed": 5, "crit": 3},
      {"hell_ember": 10, "salamander_scale": 4, "imp_horn": 4}, (70, 50, 50),
      "Speed and critical chance.", "Velocidade e chance crítica.")

ORDER = list(ITEMS)

OWNED = {}   # item criado -> nível (o mesmo dicionário fica em roster.craft_owned)


# ---------------------------------------------------------------------------
# Regras
# ---------------------------------------------------------------------------
def name(iid, lang="en"):
    return ITEMS[iid]["name"][1 if lang == "pt" else 0]


def mat_name(mid, lang="en"):
    return MAT[mid]["name"][1 if lang == "pt" else 0]


def mult(lv):
    return 1 + LV_STEP * lv


def effects(iid, lv=None):
    lv = OWNED.get(iid, 0) if lv is None else lv
    return {k: round(v * mult(lv), 1) for k, v in ITEMS[iid]["eff"].items()}


def effects_lines(iid, lv=None, lang="en"):
    return [effect_text(k, v, lang) for k, v in effects(iid, lv).items()]


def cost(iid, lv=None):
    """Materiais para criar (lv None e não criado) ou para ir de +lv a +lv+1, e o gold."""
    owned = iid in OWNED
    lv = OWNED.get(iid, 0) if lv is None else lv
    k = 1.0 if not owned else 1 + 0.5 * (lv + 1)      # criar = receita; +1 = 1,5x ... +10 = 6x
    mats = {m: int(math.ceil(q * k)) for m, q in ITEMS[iid]["recipe"].items()}
    gold = 20 if not owned else 15 * (lv + 1)
    return mats, gold


def member_totals(member):
    """Efeitos somados da roupa, calça e bota que o personagem está usando."""
    tot = {}
    for slot in SLOTS:
        iid = getattr(member, "craft", {}).get(slot)
        if iid in OWNED:
            for k, v in effects(iid).items():
                tot[k] = tot.get(k, 0) + v
    return tot


def gear_colors(member):
    """Cores da roupa, calça e bota equipadas (para o sprite do gato), ou None se não usa nenhuma."""
    if member is None:
        return None
    cr = getattr(member, "craft", None) or {}
    cols = tuple(ITEMS[cr[sl]]["color"] if cr.get(sl) in ITEMS and cr.get(sl) in OWNED else None for sl in SLOTS)
    return cols if any(cols) else None


def craft(roster, iid):
    """Cria o item ou melhora +1. Retorna None ou (erro EN, erro PT)."""
    if iid not in ITEMS:
        return ("Unknown item.", "Item desconhecido.")
    owned = iid in OWNED
    if owned and OWNED[iid] >= MAX_LV:
        return (f"Already at the maximum (+{MAX_LV}).", f"Já está no máximo (+{MAX_LV}).")
    mats, gold = cost(iid)
    have = roster.materials
    miss = [(m, q - have.get(m, 0)) for m, q in mats.items() if have.get(m, 0) < q]
    if miss:
        en = ", ".join(f"{q} {mat_name(m)}" for m, q in miss)
        pt = ", ".join(f"{q} {mat_name(m, 'pt')}" for m, q in miss)
        return (f"Missing materials: {en}.", f"Faltam materiais: {pt}.")
    if roster.gold < gold:
        return (f"Not enough gold: {gold} needed (you have {roster.gold}).",
                f"Gold insuficiente: precisa de {gold} (você tem {roster.gold}).")
    for m, q in mats.items():
        have[m] = have.get(m, 0) - q
    roster.gold -= gold
    OWNED[iid] = OWNED[iid] + 1 if owned else 0
    roster.craft_owned = OWNED
    roster.save()
    return None


def wearer(roster, iid):
    for m in roster.members:
        if getattr(m, "craft", {}).get(ITEMS[iid]["slot"]) == iid:
            return m
    return None


def equip(roster, member, iid, slot=None):
    """Equipa o item no personagem (iid None = tira o do slot). Quem estava usando perde o item."""
    if iid is None:
        member.craft.pop(slot, None)
        roster.save()
        return None
    if iid not in OWNED:
        return ("Craft this item first.", "Crie este item primeiro.")
    slot = ITEMS[iid]["slot"]
    other = wearer(roster, iid)
    if other is not None:
        other.craft.pop(slot, None)
    member.craft[slot] = iid
    roster.save()
    return None


def drop_for(e, run):
    """Materiais que o inimigo derrotado deixa: [(material, quantidade)]."""
    if getattr(e, "dummy", False):
        return []
    kind = getattr(e, "base_kind", None) or e.kind
    if getattr(e, "boss", False) or getattr(e, "boss_classes", None) or kind == "chefe":
        b = getattr(run, "biome", None) or {}
        en = b.get("enemies", {}) if isinstance(b, dict) else {}
        return [(MATERIALS[k][0], BOSS_QTY) for k in en.values() if k in MATERIALS]
    if kind not in MATERIALS:
        return []
    mid = MATERIALS[kind][0]
    tier = getattr(e, "tier", None)
    if tier == "super":
        return [(mid, SUPER_QTY)]
    if getattr(e, "elite", None):
        return [(mid, ELITE_QTY)] if random.random() < DROP_ELITE else []
    return [(mid, 1)] if random.random() < DROP_NORMAL else []


# ---------------------------------------------------------------------------
# Ícones (pixel art)
# ---------------------------------------------------------------------------
_ICONS = {}


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _mat_symbol(s, kind, col):
    W = (240, 240, 245)
    d, l = _shade(col, 0.6), _shade(col, 1.35)
    P = lambda pts, c: pygame.draw.polygon(s, c, pts)
    if kind == "wing":
        P([(14, 60), (48, 22), (84, 30), (74, 46), (82, 58), (64, 60), (66, 74), (48, 64)], col)
        for x, y in ((48, 22), (84, 30), (82, 58)):
            pygame.draw.line(s, d, (24, 62), (x, y), 3)
    elif kind == "fur":
        for k in range(6):
            x = 22 + k * 10
            P([(x, 80), (x + 10, 80), (x + 14 + (k % 2) * 6, 22 + (k % 3) * 8)], col if k % 2 else l)
    elif kind == "hide":
        P([(18, 30), (40, 20), (60, 26), (80, 18), (84, 52), (76, 80), (50, 74), (22, 82), (14, 54)], col)
        for x, y in ((36, 40), (60, 50), (42, 62)):
            pygame.draw.circle(s, d, (x, y), 4)
    elif kind == "bone":
        pygame.draw.line(s, col, (26, 70), (70, 26), 12)
        for x, y in ((22, 66), (30, 76), (66, 22), (76, 30)):
            pygame.draw.circle(s, col, (x, y), 9)
    elif kind == "cloth":
        P([(20, 24), (78, 20), (74, 60), (80, 82), (56, 72), (40, 84), (24, 70), (16, 48)], col)
        pygame.draw.line(s, d, (24, 40), (72, 36), 3)
        pygame.draw.line(s, d, (22, 58), (70, 56), 3)
    elif kind == "tail":
        pygame.draw.lines(s, col, False, [(14, 70), (34, 56), (52, 64), (70, 40), (84, 22)], 8)
    elif kind == "fang":
        P([(36, 16), (62, 16), (54, 70), (48, 86), (42, 70)], col)
        pygame.draw.line(s, l, (44, 22), (46, 64), 3)
    elif kind == "claw":
        for k in range(3):
            x = 26 + k * 20
            P([(x, 74), (x + 12, 74), (x + 22, 22), (x + 8, 44)], col)
    elif kind == "goo":
        pygame.draw.ellipse(s, col, (16, 40, 64, 44))
        pygame.draw.circle(s, col, (40, 40), 16)
        pygame.draw.circle(s, l, (34, 50), 7)
    elif kind == "spark":
        P([(48, 10), (58, 38), (86, 48), (58, 58), (48, 86), (38, 58), (10, 48), (38, 38)], col)
        pygame.draw.circle(s, W, (48, 48), 9)
    elif kind == "stone":
        P([(20, 40), (40, 20), (70, 24), (84, 50), (70, 80), (32, 82), (14, 62)], col)
        pygame.draw.line(s, d, (36, 40), (54, 66), 3)
    elif kind == "ingot":
        P([(14, 66), (30, 40), (80, 40), (88, 66)], col)
        P([(30, 40), (40, 28), (72, 28), (80, 40)], l)
    elif kind == "feather":
        P([(70, 12), (82, 30), (44, 78), (24, 84), (30, 66)], col)
        pygame.draw.line(s, d, (76, 18), (20, 88), 3)
    elif kind == "shell":
        pygame.draw.ellipse(s, col, (14, 22, 70, 58))
        pygame.draw.line(s, d, (49, 22), (49, 80), 3)
        pygame.draw.ellipse(s, l, (26, 32, 18, 10))
    elif kind == "ore":
        P([(16, 60), (30, 30), (60, 20), (82, 44), (74, 76), (36, 82)], (110, 100, 95))
        for x, y in ((38, 46), (58, 38), (54, 62)):
            P([(x, y - 8), (x + 7, y), (x, y + 8), (x - 7, y)], col)
    elif kind == "core":
        pygame.draw.circle(s, (90, 85, 80), (48, 48), 34)
        pygame.draw.circle(s, col, (48, 48), 20)
        pygame.draw.circle(s, (255, 240, 200), (48, 48), 9)
    elif kind == "horn":
        P([(30, 84), (46, 84), (54, 60), (70, 34), (80, 12), (62, 28), (44, 50)], col)
        pygame.draw.line(s, l, (40, 78), (60, 44), 3)
        for y in (70, 58, 46):
            pygame.draw.line(s, d, (34 + (84 - y) // 3, y), (48 + (84 - y) // 3, y + 4), 2)
    elif kind == "scale":
        for k, (x, y) in enumerate(((30, 34), (60, 34), (45, 56), (24, 66), (68, 64))):
            P([(x - 14, y), (x, y - 14), (x + 14, y), (x, y + 16)], col if k % 2 else l)
            pygame.draw.line(s, d, (x, y - 10), (x, y + 12), 2)
    elif kind == "sigil":
        pygame.draw.circle(s, col, (48, 48), 34, 5)
        for k in range(5):
            a0, a1 = math.radians(-90 + k * 144), math.radians(-90 + (k + 1) * 144)
            pygame.draw.line(s, l, (48 + math.cos(a0) * 28, 48 + math.sin(a0) * 28),
                             (48 + math.cos(a1) * 28, 48 + math.sin(a1) * 28), 4)
    elif kind == "crystal":
        for x, h in ((30, 50), (48, 70), (66, 46)):
            P([(x - 10, 84), (x, 84 - h), (x + 10, 84)], col)
            pygame.draw.line(s, l, (x - 2, 80), (x - 1, 88 - h), 2)


def material_icon(mid, size=32):
    key = ("m", mid, size)
    if key not in _ICONS:
        import pixel
        base = pygame.Surface((96, 96), pygame.SRCALPHA)
        m = MAT[mid]
        _mat_symbol(base, m["icon"], m["color"])
        _ICONS[key] = pixel.pixel_icon(base, tuple(int(c * 0.35) + 18 for c in m["color"]), size)
    return _ICONS[key]


def _item_symbol(s, slot, col, biome):
    d, l = _shade(col, 0.6), _shade(col, 1.3)
    P = lambda pts, c: pygame.draw.polygon(s, c, pts)
    trim = [(235, 195, 70), (200, 200, 215), (250, 220, 120), (150, 220, 255), (255, 120, 40)][biome % 5]
    if slot == "body":
        P([(26, 22), (40, 16), (56, 16), (70, 22), (84, 42), (72, 50), (68, 40), (68, 84), (28, 84), (28, 40),
           (24, 50), (12, 42)], col)
        P([(40, 16), (48, 30), (56, 16)], d)
        pygame.draw.line(s, trim, (48, 30), (48, 84), 4)
        pygame.draw.line(s, d, (28, 66), (68, 66), 5)
    elif slot == "legs":
        P([(24, 16), (72, 16), (78, 86), (56, 86), (48, 40), (40, 86), (18, 86)], col)
        pygame.draw.line(s, trim, (24, 26), (72, 26), 6)
        P([(48, 30), (52, 40), (44, 40)], d)
    else:
        for x in (16, 52):
            P([(x + 4, 20), (x + 22, 20), (x + 22, 66), (x + 34, 72), (x + 34, 84), (x, 84)], col)
            pygame.draw.line(s, trim, (x + 4, 30), (x + 22, 30), 4)
            pygame.draw.line(s, d, (x, 80), (x + 34, 80), 4)


def item_icon(iid, size=40):
    key = ("i", iid, size)
    if key not in _ICONS:
        import pixel
        it = ITEMS[iid]
        base = pygame.Surface((96, 96), pygame.SRCALPHA)
        _item_symbol(base, it["slot"], it["color"], it["biome"])
        _ICONS[key] = pixel.pixel_icon(base, tuple(int(c * 0.3) + 20 for c in it["color"]), size)
    return _ICONS[key]

