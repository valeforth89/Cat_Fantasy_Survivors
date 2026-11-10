"""Equipamentos das classes.

Regras:
- Cada personagem usa a ARMA e o CAPACETE fixos da sua classe ATUAL. Eles não podem ser trocados.
- Ambos podem ser melhorados (+1 ... +10) no ferreiro gastando fragmentos DAQUELA classe e gold.
- A melhoria é da CLASSE, não do personagem: o capacete do Warrior +2 vale para todo personagem que estiver
  como Warrior, não importa quem pagou a melhoria (desde a 0.0.14).
- Outros espaços (colar, 2 anéis, bracelete, 2 berloques) existem na tela, mas ainda não têm itens.
"""
from i18n import tr
from data import CLASSES

MAX_UPGRADE = 10
# melhorias por CLASSE, compartilhadas por todos os personagens: classe -> {"weapon": nível, "helmet": nível}
# (o mesmo dicionário fica em roster.gear e é salvo no save.json)
GEAR = {}


def gear_level(cid, slot):
    return int(GEAR.get(cid, {}).get(slot, 0))
FIXED_SLOTS = ("weapon", "helmet")
FUTURE_SLOTS = [("necklace", "Necklace"), ("ring1", "Ring"), ("ring2", "Ring"), ("bracer", "Bracer"),
                ("trinket1", "Trinket"), ("trinket2", "Trinket")]

# bônus por nível de melhoria
WEAPON_BONUS = {"dmg": 3.0, "crit": 0.5}                 # +3% de todo dano, +0,5% de chance crítica
HELMET_BONUS = {"hp_pct": 3.0, "armor": 1.0, "mres": 1.0}  # +3% de vida máx., +1 armadura, +1 defesa mágica

# nome genérico da arma de cada classe (inglês, português)
WEAPON_NAMES = {
    "freelancer": ("Short Sword", "Espada Curta"), "archer": ("Bow", "Arco"), "thaumaturge": ("Staff", "Cajado"),
    "arcanist": ("Grimoire", "Grimório"), "pugilist": ("Knuckles", "Soqueiras"), "lancer": ("Spear", "Lança"),
    "rogue": ("Dagger", "Adaga"), "conjurer": ("Staff", "Cajado"), "gladiator": ("Sword and Shield", "Espada e Escudo"),
    "marauder": ("Two-Handed Axe", "Machado de Duas Mãos"), "bard": ("Harp Bow", "Arco-Harpa"),
    "hunter": ("Longbow", "Arco Longo"), "black_mage": ("Black Staff", "Cajado Negro"),
    "time_mage": ("Hourglass Staff", "Cajado da Ampulheta"), "summoner": ("Grimoire", "Grimório"),
    "scholar": ("Codex", "Códice"), "monk": ("Claws", "Garras"), "white_monk": ("Holy Knuckles", "Soqueiras Sagradas"),
    "dragoon": ("Long Spear", "Lança Longa"), "templar": ("Banner Spear", "Lança-Estandarte"),
    "ninja": ("Kunai", "Kunai"), "assassin": ("Twin Daggers", "Adagas Gêmeas"), "white_mage": ("White Staff", "Cajado Branco"),
    "bishop": ("Scepter", "Cetro"), "paladin": ("Holy Sword and Shield", "Espada e Escudo Sagrados"),
    "spellblade": ("Enchanted Sword", "Espada Encantada"), "warrior": ("War Axe", "Machado de Guerra"),
    "berserker": ("Twin Axes", "Machados Gêmeos"), "freelancer_t2": ("Longsword", "Espada Longa"),
    "warfarer": ("War Arsenal", "Arsenal de Guerra"),
}


def upgrade_cost(level):
    """Fragmentos necessários para ir de +level a +level+1 (1, 2, 3 ... 10; 55 no total por item)."""
    return level + 1


def gold_cost(level):
    """Gold necessário para ir de +level a +level+1 (2, 4, 6 ... 20; 110 no total por item)."""
    return 2 * (level + 1)


# Bônus PERMANENTE do personagem (vale em qualquer classe) quando um item da classe chega a +10
MAX_WEAPON_BONUS = {"str": {"str": 5}, "agi": {"agi": 5}, "int": {"int": 5}, "bal": {"str": 2, "agi": 2, "int": 2}}
MAX_HELMET_BONUS = {"str": {"armor": 2, "critdmg": 4, "vit": 3}, "agi": {"dodge": 1.5, "crit": 1.5, "vit": 3},
                    "int": {"mres": 2, "cdr": 1.5, "vit": 3}, "bal": {"armor": 1, "mres": 1, "vit": 3}}
STAT_LABELS = {"str": ("STR", "FOR"), "agi": ("AGI", "AGI"), "int": ("INT", "INT"), "vit": ("VIT", "VIT"),
               "armor": ("armor", "armadura"), "mres": ("magic defense", "defesa mágica"),
               "dodge": ("% dodge", "% de esquiva"), "crit": ("% critical chance", "% de chance crítica"),
               "critdmg": ("% critical damage", "% de dano crítico"), "cdr": ("% cooldown", "% de recarga")}


def max_bonus(cid, slot):
    attr = CLASSES[cid]["attr"]
    return dict((MAX_WEAPON_BONUS if slot == "weapon" else MAX_HELMET_BONUS)[attr])


def max_bonus_text(cid, slot, lang="en"):
    parts = []
    for k, v in max_bonus(cid, slot).items():
        lab = STAT_LABELS[k][1 if lang == "pt" else 0]
        parts.append(f"+{v:g}{lab}" if lab.startswith("%") else f"+{v:g} {lab}")
    return ", ".join(parts)


def mastery_bonus(member=None):
    """Soma dos bônus permanentes dos itens +10 de todas as classes (valem para todos os personagens)."""
    tot = {}
    for cid, g in GEAR.items():
        if cid not in CLASSES:
            continue
        for slot in FIXED_SLOTS:
            if g.get(slot, 0) >= MAX_UPGRADE:
                for k, v in max_bonus(cid, slot).items():
                    tot[k] = tot.get(k, 0) + v
    return tot


def item_name(cid, slot, level, lang="en"):
    cname = CLASSES[cid]["name"]
    if lang == "pt":
        base = WEAPON_NAMES[cid][1] if slot == "weapon" else "Elmo"
        import i18n_names
        name = f"{base} do {i18n_names.CLASS_PT.get(cname, cname)}"
    else:
        base = WEAPON_NAMES[cid][0] if slot == "weapon" else "Helmet"
        name = f"{cname}'s {base}"
    return f"+{level} {name}" if level > 0 else name


def item_bonus(slot, level):
    """{efeito: valor} do item nesse nível (mesmas chaves das passivas)."""
    table = WEAPON_BONUS if slot == "weapon" else HELMET_BONUS
    return {k: v * level for k, v in table.items()}


def bonus_lines(slot, level, lang="en"):
    b = item_bonus(slot, level)
    if lang == "pt":
        if slot == "weapon":
            return [f"+{b['dmg']:g}% de todo dano", f"+{b['crit']:g}% de chance crítica"]
        return [f"+{b['hp_pct']:g}% de vida máxima", f"+{b['armor']:g} de armadura", f"+{b['mres']:g} de defesa mágica"]
    if slot == "weapon":
        return [f"+{b['dmg']:g}% all damage", f"+{b['crit']:g}% critical chance"]
    return [f"+{b['hp_pct']:g}% max HP", f"+{b['armor']:g} armor", f"+{b['mres']:g} magic defense"]


def gear_totals(member):
    """Bônus somados dos equipamentos da classe atual do personagem."""
    tot = {}
    for slot in FIXED_SLOTS:
        for k, v in item_bonus(slot, gear_level(member.cls, slot)).items():
            tot[k] = tot.get(k, 0) + v
    return tot


def try_upgrade(roster, cid, slot):
    """Melhora o item (cid, slot) da classe (vale para todos os personagens).
    Retorna None se deu certo, ou a mensagem de erro (em inglês)."""
    lv = gear_level(cid, slot)
    if lv >= MAX_UPGRADE:
        return "Already at the maximum upgrade (+10)."
    cost = upgrade_cost(lv)
    gold = gold_cost(lv)
    have = roster.fragments.get(cid, 0)
    if have < cost:
        return f"Not enough {tr(CLASSES[cid]['name'])} Fragments: need {cost}, you have {_fmt(have)}."
    if roster.gold < gold:
        return f"Not enough gold: need {gold}, you have {roster.gold}."
    roster.fragments[cid] = round(have - cost, 3)
    roster.gold -= gold
    GEAR.setdefault(cid, {})[slot] = lv + 1
    roster.save()
    return None


def _fmt(v):
    from progression import fmt_frag
    return fmt_frag(v)
