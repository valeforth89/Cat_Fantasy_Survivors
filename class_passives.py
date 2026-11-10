"""Passivas das classes (9 passivas + 1 capstone por classe).

Cada passiva tem um ou mais efeitos {chave: valor}. Chaves:
  str_pct, agi_pct, int_pct, vit_pct ...... +% do atributo
  armor_pct, mres_pct ...................... +% de armadura / defesa mágica
  dodge, crit, critdmg, cdr, hp_pct, ...... status diretos (mesmas chaves antigas)
  dot_dmg .................................. +% de dano contínuo (queimadura, veneno, sangramento)
  buffdur .................................. +% de duração das habilidades de buff
  tagdmg:<tag> ............................. +% de dano das habilidades com a tag
  tagcrit:<tag> ............................ +% de chance crítica das habilidades com a tag
  taghaste:<tag> ........................... -% de recarga das habilidades com a tag
  dmgvs:<status> / critvs:<status> ......... +% de dano / chance crítica contra alvos com o status
  cap:<mecânica> ........................... efeito especial de capstone (ver CAPSTONE_MECHANICS)

A 10ª passiva de cada classe é a CAPSTONE: só pode ir no 5º espaço de passiva da classe (a da própria
classe) ou no 5º espaço de maestria (a capstone de outra classe masterizada).
"""
from data import CLASSES
from tags import tag_name, status_name

CAPSTONE_MECHANICS = {
    # chave: (inglês, português) — {v} = valor
    "execute": ("+{v}% damage to enemies below 30% HP", "+{v}% de dano em inimigos abaixo de 30% de vida"),
    "detonate": ("Enemies that die burning, poisoned or bleeding explode for {v}% of their max HP",
                 "Inimigos que morrem queimando, envenenados ou sangrando explodem causando {v}% da vida máxima deles"),
    "vampiric": ("Critical hits heal you for {v}% of the damage dealt", "Críticos curam você em {v}% do dano causado"),
    "frenzy": ("Each kill grants +{v}% damage for 4 s (stacks up to 10 times)",
               "Cada abate dá +{v}% de dano por 4 s (acumula até 10 vezes)"),
    "ambush": ("+{v}% damage to enemies at full HP", "+{v}% de dano em inimigos com a vida cheia"),
    "echo": ("{v}% chance for a skill to recharge instantly after use",
             "{v}% de chance de uma habilidade recarregar na hora após o uso"),
    "sanctuary": ("Your heals also grant the target +{v}% defense for 4 s",
                  "Suas curas também dão +{v}% de defesa ao alvo por 4 s"),
    "legion": ("Summons deal +{v}% damage and last {v}% longer", "Invocações causam +{v}% de dano e duram {v}% a mais"),
    "elemental": ("+{v}% damage to enemies with an elemental status (burning, chilled, poisoned, stunned)",
                  "+{v}% de dano em inimigos com status elemental (queimando, congelando, envenenado, atordoado)"),
    "thorns": ("Reflects {v}% of the damage you take to the attacker", "Reflete {v}% do dano recebido em quem atacou"),
    "anthem": ("The whole party deals +{v}% damage while you are standing",
               "A party inteira causa +{v}% de dano enquanto você estiver de pé"),
    "bulwark": ("Below 40% HP you gain +{v}% defense", "Abaixo de 40% de vida você ganha +{v}% de defesa"),
    "lowhp": ("Below 40% HP you deal +{v}% damage", "Abaixo de 40% de vida você causa +{v}% de dano"),
    "rage": ("Up to +{v}% damage the lower your HP is (full bonus near 0 HP)",
             "Até +{v}% de dano quanto menor a sua vida (bônus total perto de 0)"),
}

SIMPLE_EFFECTS = {
    # chave: (inglês, português, unidade)
    "str_pct": ("STR", "FOR", "%"), "agi_pct": ("AGI", "AGI", "%"), "int_pct": ("INT", "INT", "%"),
    "vit_pct": ("VIT", "VIT", "%"), "armor_pct": ("armor", "armadura", "%"), "mres_pct": ("magic defense", "defesa mágica", "%"),
    "dodge": ("dodge", "esquiva", "%"), "crit": ("critical chance", "chance crítica", "%"),
    "critdmg": ("critical damage", "dano crítico", "%"), "cdr": ("cooldown reduction", "redução de recarga", "%"),
    "hp_pct": ("max HP", "vida máxima", "%"), "hp_flat": ("max HP", "vida máxima", ""), "dmg": ("all damage", "todo dano", "%"),
    "phys_dmg": ("physical damage", "dano físico", "%"), "mag_dmg": ("magic damage", "dano mágico", "%"),
    "speed": ("movement speed", "velocidade de movimento", "%"), "defense": ("defense", "defesa", "%"),
    "area": ("area (width, size and angle)", "área (largura, tamanho e ângulo)", "%"),
    "range": ("range (melee reach and projectile distance)", "alcance (corpo a corpo e distância dos projéteis)", "%"), "heal": ("healing", "cura", "%"), "duration": ("duration", "duração", "%"),
    "regen5": ("HP regeneration every 5 s", "regeneração de vida a cada 5 s", ""), "magnet": ("pickup range", "alcance de coleta", "%"),
    "armor": ("armor", "armadura", ""), "mres": ("magic defense", "defesa mágica", ""), "str": ("STR", "FOR", ""),
    "agi": ("AGI", "AGI", ""), "int": ("INT", "INT", ""), "vit": ("VIT", "VIT", ""),
    "dot_dmg": ("damage over time (burn, poison, bleed)", "dano contínuo (queimadura, veneno, sangramento)", "%"),
    "buffdur": ("duration of buff skills", "duração das habilidades de buff", "%"),
}


def _fmt(v):
    return f"{v:g}"


def effect_text(key, v, lang="en"):
    """Texto de um efeito de passiva."""
    pt = lang == "pt"
    if key in SIMPLE_EFFECTS:
        e, p, unit = SIMPLE_EFFECTS[key]
        sign = "-" if key == "cdr" and False else "+"
        return f"{sign}{_fmt(v)}{unit} {'de ' + p if pt else e}"
    kind, _, arg = key.partition(":")
    if kind == "tagdmg":
        return (f"+{_fmt(v)}% de dano das habilidades de {tag_name(arg, 'pt')}" if pt
                else f"+{_fmt(v)}% damage with {tag_name(arg)} skills")
    if kind == "tagcrit":
        return (f"+{_fmt(v)}% de chance crítica das habilidades de {tag_name(arg, 'pt')}" if pt
                else f"+{_fmt(v)}% critical chance with {tag_name(arg)} skills")
    if kind == "taghaste":
        return (f"-{_fmt(v)}% de recarga das habilidades de {tag_name(arg, 'pt')}" if pt
                else f"-{_fmt(v)}% cooldown of {tag_name(arg)} skills")
    if kind == "dmgvs":
        return (f"+{_fmt(v)}% de dano em inimigos com {status_name(arg, 'pt')}" if pt and arg in ("debuffed", "elemental")
                else f"+{_fmt(v)}% de dano em inimigos {status_name(arg, 'pt')}" if pt
                else f"+{_fmt(v)}% damage to {status_name(arg)} enemies" if arg not in ("debuffed", "elemental")
                else f"+{_fmt(v)}% damage to enemies with {status_name(arg)}")
    if kind == "critvs":
        return (f"+{_fmt(v)}% de chance crítica em inimigos com {status_name(arg, 'pt')}" if pt and arg in ("debuffed", "elemental")
                else f"+{_fmt(v)}% de chance crítica em inimigos {status_name(arg, 'pt')}" if pt
                else f"+{_fmt(v)}% critical chance against {status_name(arg)} enemies" if arg not in ("debuffed", "elemental")
                else f"+{_fmt(v)}% critical chance against enemies with {status_name(arg)}")
    if kind == "cap" and arg in CAPSTONE_MECHANICS:
        return CAPSTONE_MECHANICS[arg][1 if pt else 0].format(v=_fmt(v))
    return f"{key}: {_fmt(v)}"


def effects_text(effects, lang="en"):
    return "; ".join(effect_text(k, v, lang) for k, v in effects.items())


def effects_to_cell(effects):
    """Formato da planilha: 'chave=valor; chave=valor'."""
    return "; ".join(f"{k}={_fmt(v)}" for k, v in effects.items())


def valid_key(key):
    if key in SIMPLE_EFFECTS:
        return True
    kind, _, arg = key.partition(":")
    if kind in ("tagdmg", "tagcrit", "taghaste"):
        from tags import TAG_NAMES
        return arg in TAG_NAMES
    if kind in ("dmgvs", "critvs"):
        from tags import STATUS_NAMES
        return arg in STATUS_NAMES
    return kind == "cap" and arg in CAPSTONE_MECHANICS


def cell_to_effects(text):
    """Lê 'chave=valor; ...'. Retorna (efeitos, erros)."""
    out, errs = {}, []
    for part in str(text or "").replace(",", ";").split(";"):
        part = part.strip()
        if not part:
            continue
        key, _, val = part.partition("=")
        key = key.strip()
        try:
            v = float(val.strip().replace("%", ""))
        except ValueError:
            errs.append(f"bad value in '{part}'")
            continue
        if not valid_key(key):
            errs.append(f"unknown effect '{key}'")
            continue
        out[key] = out.get(key, 0) + v
    return out, errs


# ---------------------------------------------------------------------------
# Desenho das passivas por classe
# ---------------------------------------------------------------------------
# (dano principal, crítico, recarga, status explorado, dano secundário, (efeito geral, valor),
#  capstone: (nome, {efeitos}))
DESIGN = {
    "freelancer": ("melee", "single", "melee", "slowed", "projectile", ("dmg", 5),
                   ("Jack of All Trades", {"dmg": 8, "cap:echo": 10})),
    "archer": ("projectile", "piercing", "projectile", "bleeding", "aoe", ("range", 15),
               ("Deadeye", {"cap:ambush": 40, "tagcrit:projectile": 8})),
    "thaumaturge": ("fire", "lightning", "magical", "burning", "ice", ("area", 8),
                    ("Elemental Convergence", {"cap:elemental": 20, "cap:detonate": 15})),
    "arcanist": ("arcane", "projectile", "buff", "debuffed", "homing", ("duration", 10),
                 ("Arcane Overflow", {"cap:echo": 15, "tagdmg:arcane": 10})),
    "pugilist": ("melee", "blunt", "melee", "stunned", "knockback", ("speed", 6),
                 ("Iron Fists", {"cap:frenzy": 3, "tagcrit:melee": 6})),
    "lancer": ("piercing", "melee", "piercing", "bleeding", "single", ("range", 12),
               ("Impaler", {"cap:execute": 30, "tagdmg:piercing": 10})),
    "rogue": ("melee", "bleed", "melee", "slowed", "slash", ("speed", 6),
              ("Shadow Opportunist", {"cap:ambush": 30, "critvs:debuffed": 10})),
    "conjurer": ("earth", "wind", "heal", "stunned", "water", ("heal", 10),
                 ("Nature's Embrace", {"cap:sanctuary": 15, "heal": 15})),
    "gladiator": ("melee", "aoe", "buff", "stunned", "physical", ("defense", 4),
                  ("Champion of the Arena", {"cap:thorns": 25, "cap:bulwark": 20})),
    "marauder": ("aoe", "melee", "melee", "bleeding", "knockback", ("area", 12),
                 ("Bloodthirst", {"cap:vampiric": 8, "tagdmg:bleed": 15})),
    "bard": ("sound", "projectile", "buff", "slowed", "piercing", ("heal", 8),
             ("Grand Anthem", {"cap:anthem": 10, "duration": 15})),
    "hunter": ("projectile", "piercing", "summon", "bleeding", "summon", ("magnet", 15),
               ("Apex Predator", {"cap:legion": 30, "cap:ambush": 25})),
    "black_mage": ("magical", "fire", "aoe", "burning", "ice", ("area", 10),
                   ("Cataclysm", {"cap:detonate": 20, "tagdmg:aoe": 12})),
    "time_mage": ("gravity", "time", "buff", "slowed", "stun", ("cdr", 4),
                  ("Chronomancer", {"cap:echo": 20, "dmgvs:slowed": 15})),
    "summoner": ("summon", "magical", "summon", "burning", "fire", ("duration", 15),
                 ("Pact of Legions", {"cap:legion": 50, "tagdmg:summon": 10})),
    "scholar": ("arcane", "single", "heal", "poisoned", "dot", ("heal", 12),
                ("Grand Treatise", {"cap:sanctuary": 20, "heal": 15})),
    "monk": ("melee", "aoe", "melee", "stunned", "knockback", ("critdmg", 15),
             ("Hundred Fists Doctrine", {"cap:frenzy": 4, "cap:echo": 8})),
    "white_monk": ("holy", "melee", "heal", "stunned", "aoe", ("heal", 10),
                   ("Serenity", {"cap:sanctuary": 15, "cap:vampiric": 5})),
    "dragoon": ("piercing", "fire", "aoe", "burning", "lightning", ("area", 10),
                ("Dragon Heart", {"cap:execute": 25, "tagcrit:aoe": 8})),
    "templar": ("holy", "piercing", "buff", "stunned", "melee", ("defense", 4),
                ("Holy Crusade", {"cap:anthem": 8, "cap:bulwark": 15})),
    "ninja": ("projectile", "fire", "projectile", "burning", "water", ("dodge", 3),
              ("Thousand Shadows", {"cap:echo": 15, "cap:ambush": 20})),
    "assassin": ("poison", "melee", "single", "poisoned", "bleed", ("critdmg", 15),
                 ("Death Sentence", {"cap:execute": 40, "cap:detonate": 10})),
    "white_mage": ("holy", "aoe", "heal", "debuffed", "single", ("heal", 15),
                   ("Divine Grace", {"cap:sanctuary": 25, "heal": 20})),
    "bishop": ("earth", "water", "aoe", "stunned", "wind", ("area", 10),
               ("Wrath of Nature", {"cap:elemental": 20, "duration": 20})),
    "paladin": ("holy", "melee", "heal", "stunned", "aoe", ("defense", 5),
                ("Aegis of Light", {"cap:bulwark": 25, "cap:thorns": 20})),
    "spellblade": ("melee", "fire", "melee", "chilled", "lightning", ("crit", 3),
                   ("Elemental Edge", {"cap:elemental": 25, "tagcrit:melee": 8})),
    "warrior": ("aoe", "knockback", "buff", "stunned", "melee", ("hp_pct", 10),
                ("Warlord", {"cap:anthem": 10, "cap:thorns": 15})),
    "berserker": ("melee", "aoe", "melee", "bleeding", "bleed", ("critdmg", 20),
                  ("Unending Rage", {"cap:frenzy": 5, "cap:vampiric": 6})),
    "freelancer_t2": ("physical", "single", "melee", "debuffed", "magical", ("dmg", 8),
                      ("Versatility", {"dmg": 10, "cap:echo": 12})),
    "warfarer": ("aoe", "projectile", "melee", "debuffed", "magical", ("dmg", 10),
                 ("Master of War", {"cap:frenzy": 3, "cap:execute": 25, "dmg": 10})),
}

# Passivas de % de atributo (FOR/AGI/INT/VIT) eram fortes demais para existirem em quase toda classe (dava para
# equipar várias de classes masterizadas). Agora só há UMA de cada: STR Training (Lancer), AGI Training (Archer),
# INT Training (Thaumaturge) e, no Novice, Versatile Training e Vitality. As outras classes ganharam passivas novas.
KEEP_TRAINING = {"freelancer", "lancer", "archer", "thaumaturge"}
# mesma lógica para as defensivas: Fortitude (Lancer), Evasion (Archer), Warding (Thaumaturge), Endurance (Novice)
KEEP_DEFENSE = {"freelancer", "lancer", "archer", "thaumaturge"}
# classe: substituta da passiva defensiva (3ª passiva)
NEW_DEFENSE = {
    "freelancer_t2": ("Adaptable", {"armor": 2, "mres": 2, "dodge": 1}),
    "warfarer": ("Commander's Resolve", {"defense": 3, "regen5": 2}),
    "bard": ("Soothing Melody", {"regen5": 3, "mres": 2}),
    "hunter": ("Camouflage", {"dodge": 2, "dmgvs:slowed": 6}),
    "pugilist": ("Rolling with Punches", {"armor": 3, "speed": 3}),
    "monk": ("Iron Shirt", {"armor_pct": 10, "regen5": 2}),
    "white_monk": ("Serene Guard", {"mres_pct": 10, "heal": 5}),
    "rogue": ("Opportunist", {"critvs:slowed": 6, "critdmg": 8}),
    "ninja": ("Vanishing Act", {"speed": 6, "magnet": 10}),
    "assassin": ("Toxic Mastery", {"dot_dmg": 10, "critvs:poisoned": 5}),
    "black_mage": ("Overcharge", {"mag_dmg": 6, "critdmg": 6}),
    "time_mage": ("Haste Field", {"speed": 6, "buffdur": 10}),
    "arcanist": ("Arcane Barrier", {"defense": 2, "cdr": 2}),
    "summoner": ("Ritual Circle", {"area": 6, "duration": 6}),
    "scholar": ("Erudition", {"cdr": 2, "crit": 2}),
    "conjurer": ("Verdant Growth", {"hp_pct": 5, "regen5": 2}),
    "white_mage": ("Purity", {"mres": 3, "heal": 6}),
    "bishop": ("Consecration", {"tagdmg:aoe": 8, "area": 4}),
    "dragoon": ("Dragon Scales", {"armor_pct": 10, "defense": 2}),
    "templar": ("Zealot", {"phys_dmg": 5, "mag_dmg": 5}),
    "gladiator": ("Showmanship", {"critdmg": 10, "magnet": 10}),
    "paladin": ("Divine Bulwark", {"armor_pct": 8, "mres_pct": 8}),
    "spellblade": ("Blade Dance", {"speed": 4, "crit": 2}),
    "marauder": ("Pillager", {"magnet": 20, "phys_dmg": 4}),
    "warrior": ("Shield Training", {"defense": 3, "armor": 2}),
    "berserker": ("Pain Tolerance", {"hp_flat": 30, "regen5": 2}),
}
# "Buff Haste" (-recarga de buffs) aparecia em 6 classes: algumas viraram +% de duração dos buffs
KEEP_BUFF_HASTE = {"bard", "time_mage"}
BUFF_DURATION = {"arcanist": "Lingering Enchantment", "templar": "Steadfast Faith", "gladiator": "Crowd's Roar",   # Gladiator: duração de buff + dano crítico (ver class_passives)
                 "warrior": "Rallying Presence"}
KEEP_VITALITY = {"freelancer"}
# classe: (substituta da "Training" (1ª passiva), substituta da "Vitality" (5ª passiva))
NEW_PASSIVES = {
    "freelancer_t2": (("Wanderer's Kit", {"phys_dmg": 6, "mag_dmg": 6}),
                      ("Seasoned Traveler", {"speed": 5, "magnet": 15})),
    "warfarer": (("Battle Hardened", {"hp_pct": 5, "defense": 3}), ("War Veteran", {"critdmg": 12, "crit": 2})),
    "archer": (None, ("Steady Aim", {"crit": 3, "range": 8})),
    "bard": (("Stage Presence", {"duration": 10, "heal": 6}), ("Traveling Minstrel", {"speed": 6, "magnet": 20})),
    "hunter": (("Tracker", {"dmgvs:slowed": 10, "magnet": 15}), ("Wilderness Survival", {"regen5": 3, "hp_flat": 30})),
    "thaumaturge": (None, ("Elemental Attunement", {"dot_dmg": 10, "critvs:chilled": 5})),
    "black_mage": (("Arcane Fuel", {"mag_dmg": 8}), ("Pyromania", {"dot_dmg": 15})),
    "time_mage": (("Borrowed Time", {"duration": 12, "cdr": 2}), ("Temporal Shift", {"defense": 4, "dodge": 2})),
    "arcanist": (("Spell Weaving", {"mag_dmg": 6, "area": 5}), ("Mana Shield", {"mres": 4, "hp_flat": 25})),
    "summoner": (("Binding Circle", {"duration": 10, "tagcrit:summon": 5}), ("Life Link", {"heal": 10, "regen5": 2})),
    "scholar": (("Studious Mind", {"cdr": 3, "duration": 6}), ("Field Medicine", {"heal": 8, "hp_pct": 4})),
    "pugilist": (("Iron Body", {"armor": 3, "hp_flat": 25}), ("Footwork", {"speed": 5, "dodge": 2})),
    "monk": (("Inner Focus", {"crit": 3, "critdmg": 8}), ("Ki Flow", {"regen5": 3, "cdr": 2})),
    "white_monk": (("Healing Palm", {"heal": 10, "phys_dmg": 4}), ("Tranquility", {"defense": 3, "regen5": 2})),
    "lancer": (None, ("Phalanx Drill", {"armor": 3, "defense": 2})),
    "dragoon": (("Dragon Blood", {"hp_pct": 5, "mres": 3}), ("Sky Dive", {"critdmg": 8, "range": 6})),
    "templar": (("Oath of Light", {"mres_pct": 12, "heal": 5}), ("Sacred Vow", {"defense": 3, "hp_flat": 30})),
    "rogue": (("Quick Hands", {"cdr": 2, "crit": 2}), ("Shadowstep", {"speed": 6, "dodge": 2})),
    "ninja": (("Shuriken Drills", {"tagcrit:projectile": 5, "range": 6}), ("Smoke Bomb", {"dodge": 2, "duration": 8})),
    "assassin": (("Poisoned Blades", {"dot_dmg": 12}), ("Mark for Death", {"dmgvs:debuffed": 8, "critdmg": 8})),
    "conjurer": (("Earth's Bounty", {"heal": 8, "magnet": 15}), ("Stone Skin", {"armor": 3, "mres": 3})),
    "white_mage": (("Blessed Aura", {"heal": 8, "duration": 6}), ("Divine Protection", {"defense": 3, "hp_pct": 4})),
    "bishop": (("Sermon", {"mag_dmg": 6, "area": 4}), ("Faith", {"regen5": 2, "defense": 3})),
    "gladiator": (("Crowd Pleaser", {"dmg": 4, "speed": 3}), ("Arena Veteran", {"hp_pct": 6, "armor": 2})),
    "paladin": (("Holy Shield", {"defense": 3, "mres": 3}), ("Lay on Hands", {"heal": 12, "regen5": 2})),
    "spellblade": (("Arcane Edge", {"mag_dmg": 5, "phys_dmg": 5}), ("Runic Ward", {"mres_pct": 12, "armor_pct": 8})),
    "marauder": (("Savage Strength", {"phys_dmg": 8}), ("Blood Frenzy", {"dot_dmg": 12, "speed": 3})),
    "warrior": (("Battle Cry", {"dmg": 4, "critdmg": 8}), ("Second Wind", {"regen5": 4})),
    "berserker": (("Reckless Swing", {"critdmg": 12, "area": 4}), ("Thick Skin", {"hp_flat": 40})),
}

# ---------------------------------------------------------------------------
# Passivas iguais em muitas classes: no máximo 3 cópias de cada. classe: {posição: (nome, efeitos)}
# posições: 1 Mastery, 3 Precision, 5 Haste, 6 Exploit, 7 Power, 8 geral
# ---------------------------------------------------------------------------
REDUNDANT_SWAP = {
    "freelancer": {1: ("Physical Mastery", {"tagdmg:physical": 10}), 5: ("Bleed Haste", {"taghaste:bleed": 8}),
                   7: ("Slash Power", {"tagdmg:slash": 12})},
    "freelancer_t2": {5: ("Physical Haste", {"taghaste:physical": 8})},
    "warfarer": {5: ("Damage over time Haste", {"taghaste:dot": 8}), 7: ("Fire Power", {"tagdmg:fire": 12})},
    "archer": {6: ("Wounding Shots", {"dot_dmg": 8, "critvs:bleeding": 6}), 7: ("Damage over time Power", {"tagdmg:dot": 12})},
    "hunter": {6: ("Blood Trail", {"dmgvs:bleeding": 10, "magnet": 10})},
    "dragoon": {3: ("Bleed Precision", {"tagcrit:bleed": 6}), 6: ("Dragon Fire", {"dmgvs:burning": 10, "critdmg": 8}),
                8: ("Far Reach", {"range": 12})},
    "ninja": {6: ("Exploit Chilled", {"dmgvs:chilled": 10, "critvs:chilled": 6})},
    "rogue": {1: ("Bleed Mastery", {"tagdmg:bleed": 12}), 5: ("Slash Haste", {"taghaste:slash": 8}),
              6: ("Hamstring", {"dmgvs:slowed": 10, "tagdmg:bleed": 6})},
    "monk": {1: ("Blunt Mastery", {"tagdmg:blunt": 12})},
    "white_monk": {3: ("Stun Precision", {"tagcrit:stun": 6}), 5: ("Holy Haste", {"taghaste:holy": 8}),
                   6: ("Pressure Points", {"dmgvs:stunned": 10, "critdmg": 8}), 8: ("Calm Mind", {"cdr": 2, "heal": 6}),
                   7: ("Stun Power", {"tagdmg:stun": 12})},
    "templar": {6: ("Smite the Stunned", {"dmgvs:stunned": 10, "tagdmg:holy": 6}),
                7: ("Ranged Power", {"tagdmg:ranged": 10})},
    "conjurer": {5: ("Knockback Haste", {"taghaste:knockback": 8}),
                 6: ("Exploit Elemental", {"dmgvs:elemental": 10, "critvs:elemental": 6})},
    "bishop": {6: ("Exploit Elemental", {"dmgvs:elemental": 10, "critvs:elemental": 6})},
    "white_mage": {1: ("Magical Mastery", {"tagdmg:magical": 10}), 3: ("Holy Precision", {"tagcrit:holy": 6}),
                   6: ("Holy Judgment", {"dmgvs:debuffed": 10, "heal": 6})},
    "gladiator": {6: ("Crowd Control", {"critvs:stunned": 6, "critdmg": 8})},
    "warrior": {6: ("Shield Bash", {"dmgvs:stunned": 10, "armor": 2}), 7: ("Slash Power", {"tagdmg:slash": 12})},
    "paladin": {7: ("Stun Power", {"tagdmg:stun": 12})},
    "spellblade": {1: ("Spellsword Training", {"tagdmg:melee": 6, "mag_dmg": 6}),
                   5: ("Single target Haste", {"taghaste:single": 8})},
    "marauder": {3: ("Slash Precision", {"tagcrit:slash": 6}), 5: ("Slash Haste", {"taghaste:slash": 8}),
                 8: ("Ravager", {"area": 5, "dmg": 4})},
    "bard": {8: ("Lingering Notes", {"duration": 6, "heal": 6})},
}

# ---------------------------------------------------------------------------
# Balanceamento: quanto de cada efeito vale UMA passiva inteira. Uma passiva com 2+ efeitos divide esse
# orçamento (ex.: armadura + vida dá menos armadura do que a passiva só de armadura).
# ---------------------------------------------------------------------------
UNITS = {
    "str_pct": 8, "agi_pct": 8, "int_pct": 8, "vit_pct": 10, "hp_pct": 8, "hp_flat": 40,
    "armor_pct": 15, "mres_pct": 15, "armor": 4, "mres": 4, "dodge": 4, "crit": 4, "critdmg": 15, "cdr": 4,
    "defense": 4, "dmg": 8, "phys_dmg": 10, "mag_dmg": 10, "dot_dmg": 15, "speed": 6, "area": 10, "range": 12,
    "heal": 12, "duration": 12, "buffdur": 15, "magnet": 20, "regen5": 4,
    "tagcrit": 6, "taghaste": 8, "dmgvs": 20, "critvs": 12,
}
BROAD_TAGS = {"melee", "ranged", "projectile", "aoe", "single", "physical", "magical"}   # tags amplas: bônus menor


def unit(key):
    kind, _, arg = key.partition(":")
    if kind == "tagdmg":
        return 10 if arg in BROAD_TAGS else 12
    return UNITS.get(kind if arg else key)


def _step(v):
    return 1.0 if v >= 5 else 0.5


def balance(effects):
    """Ajusta os valores para que a passiva valha uma 'passiva inteira' (soma das frações = 1)."""
    keys = list(effects)
    if any(unit(k) is None for k in keys):
        return dict(effects)
    if len(keys) == 1:
        return {keys[0]: float(unit(keys[0]))}
    w = {k: effects[k] / unit(k) for k in keys}   # proporção pedida entre os efeitos
    tot = sum(w.values())
    out = {}
    for k in keys:
        raw = unit(k) * w[k] / tot
        st = _step(raw)
        out[k] = max(st, round(raw / st) * st)
    for _ in range(6):   # arredondamento: aproxima a soma de 1,0 sem passar do valor da passiva simples
        frac = sum(out[k] / unit(k) for k in keys)
        if abs(frac - 1) <= 0.07:
            break
        k = max(keys, key=lambda k: out[k] / unit(k))
        if frac > 1:
            k = max(keys, key=lambda k: out[k] / unit(k))
            if out[k] - _step(out[k]) > 0:
                out[k] -= _step(out[k])
        else:
            k = min(keys, key=lambda k: out[k] / unit(k))
            out[k] += _step(out[k])
    return {k: (int(v) if v == int(v) else v) for k, v in out.items()}


ATTR_PCT = {"str": "str_pct", "agi": "agi_pct", "int": "int_pct"}
DEF_STAT = {"str": ("armor_pct", 15), "agi": ("dodge", 4), "int": ("mres_pct", 15), "bal": ("hp_pct", 6)}


def _title(tag):
    return tag_name(tag)


def class_passives(cid):
    """Lista de 10 passivas (dicts com name, desc, effects, capstone) — sem id/unlock."""
    c = CLASSES[cid]
    cname = c["name"]
    attr = c["attr"]
    dtag, ctag, htag, status, stag, gen, cap = DESIGN[cid]
    out = []

    def add(name, effects):
        out.append(dict(name=f"{name} [{cname}]", effects=dict(effects), capstone=False))

    new_train, new_vit = NEW_PASSIVES.get(cid, (None, None))
    if cid not in KEEP_TRAINING:
        add(*new_train)
    elif attr in ATTR_PCT:
        add(f"{attr.upper()} Training", {ATTR_PCT[attr]: 8})
    else:
        add("Versatile Training", {"str_pct": 4, "agi_pct": 4, "int_pct": 4})
    add(f"{_title(dtag)} Mastery", {f"tagdmg:{dtag}": 10})
    k, v = DEF_STAT.get(attr, DEF_STAT["bal"])
    if cid in KEEP_DEFENSE:
        add({"armor_pct": "Fortitude", "dodge": "Evasion", "mres_pct": "Warding", "hp_pct": "Endurance"}[k], {k: v})
    else:
        add(*NEW_DEFENSE[cid])
    add(f"{_title(ctag)} Precision", {f"tagcrit:{ctag}": 6})
    if cid in KEEP_VITALITY:
        add("Vitality", {"vit_pct": 10})
    else:
        add(*new_vit)
    if htag == "buff" and cid not in KEEP_BUFF_HASTE:
        add(BUFF_DURATION[cid], {"buffdur": 8, "critdmg": 7} if cid == "gladiator" else {"buffdur": 15})
    else:
        add(f"{_title(htag)} Haste", {f"taghaste:{htag}": 8})
    add(f"Exploit {status_name(status).title()}", {f"dmgvs:{status}": 10, f"critvs:{status}": 6})
    add(f"{_title(stag)} Power", {f"tagdmg:{stag}": 12})
    gk, gv = gen
    add({"dmg": "Ferocity", "speed": "Swiftness", "area": "Expansion", "range": "Far Reach", "duration": "Persistence",
         "hp_pct": "Toughness", "armor_pct": "Iron Skin", "heal": "Benevolence", "defense": "Guard",
         "magnet": "Scavenger", "cdr": "Quick Mind", "dodge": "Light Feet", "critdmg": "Brutality",
         "crit": "Keen Eye"}.get(gk, "Discipline"), {gk: gv})
    for slot, (name, eff) in REDUNDANT_SWAP.get(cid, {}).items():   # passivas que se repetiam demais
        out[slot] = dict(name=f"{name} [{cname}]", effects=dict(eff), capstone=False)
    for p in out:
        p["effects"] = balance(p["effects"])
    cap_name, cap_eff = cap
    out.append(dict(name=cap_name, effects=dict(cap_eff), capstone=True))
    for p in out:
        p["desc"] = effects_text(p["effects"])
    return out
