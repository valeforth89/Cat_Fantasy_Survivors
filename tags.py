"""Tags das habilidades.

As tags são derivadas automaticamente da especificação de cada habilidade (arquétipo, alvo, elemento,
efeitos), então qualquer habilidade nova ou editada na planilha ganha as tags certas sozinha.
Passivas interagem com elas (ex.: +dano para "fire", chance crítica para "projectile", recarga para "melee").

Status de inimigos (usados por passivas condicionais): burning, poisoned, bleeding, chilled, stunned, slowed.
"""
from data import CLASSES, ELEMENT_STATUS, PHYS_STATUS

# ordem de exibição e nomes (inglês, português)
TAG_NAMES = {
    "melee": ("Melee", "Corpo a corpo"), "ranged": ("Ranged", "À distância"), "projectile": ("Projectile", "Projétil"),
    "aoe": ("AoE", "Área"), "single": ("Single target", "Alvo único"), "summon": ("Summon", "Invocação"),
    "heal": ("Heal", "Cura"), "buff": ("Buff", "Bônus"),
    "physical": ("Physical", "Físico"), "magical": ("Magical", "Mágico"),
    "fire": ("Fire", "Fogo"), "ice": ("Ice", "Gelo"), "lightning": ("Lightning", "Raio"), "water": ("Water", "Água"),
    "wind": ("Wind", "Vento"), "earth": ("Earth", "Terra"), "poison": ("Poison", "Veneno"), "holy": ("Holy", "Sagrado"),
    "arcane": ("Arcane", "Arcano"), "sound": ("Sound", "Som"), "gravity": ("Gravity", "Gravidade"),
    "time": ("Time", "Tempo"), "smoke": ("Smoke", "Fumaça"),
    "bleed": ("Bleed", "Sangramento"), "dot": ("Damage over time", "Dano contínuo"), "stun": ("Stun", "Atordoamento"),
    "slow": ("Slow", "Lentidão"), "knockback": ("Knockback", "Empurrão"), "pull": ("Pull", "Puxão"),
    "slash": ("Slash", "Corte"), "piercing": ("Piercing", "Perfurante"), "blunt": ("Blunt", "Impacto"),
    "homing": ("Homing", "Teleguiado"),
}
TAG_ORDER = list(TAG_NAMES)
ELEMENT_TAGS = ("fire", "ice", "lightning", "water", "wind", "earth", "poison", "holy", "arcane", "sound",
                "gravity", "time", "smoke")

# status que um inimigo pode ter (para passivas "contra alvos ...")
STATUS_NAMES = {
    "burning": ("Burning", "Queimando"), "poisoned": ("Poisoned", "Envenenado"), "bleeding": ("Bleeding", "Sangrando"),
    "chilled": ("Chilled", "Congelando"), "stunned": ("Stunned", "Atordoado"), "slowed": ("Slowed", "Lento"),
    "debuffed": ("any debuff", "qualquer debuff"), "elemental": ("an elemental status", "um status elemental"),
}

# classes cujos golpes FÍSICOS cortantes causam sangramento
BLEED_CLASSES = {"rogue", "assassin", "ninja", "marauder", "warrior", "berserker", "gladiator", "spellblade",
                 "dragoon", "lancer", "hunter", "archer", "freelancer", "freelancer_t2", "warfarer", "monk"}
BLUNT_WORDS = ("punch", "fist", "kick", "palm", "bash", "slam", "pound", "uppercut", "jab", "smoke", "stone",
               "shockwave", "chakra", "heaven", "pommel", "ground", "blow", "overpower", "quake", "earth",
               "ki wave", "aura", "chi ", "chi field", "smash", "crush")
SLASH_WORDS = ("axe", "sword", "shuriken", "blade", "cleave", "chop", "slash", "edge", "swing", "sweep", "spin")
PIERCE_WORDS = ("arrow", "javelin", "spear", "lance", "barrage", "caltrop", "kunai", "dagger", "knife", "knives",
                "stab", "thrust", "lunge", "fang", "impale", "skewer", "trap", "jump", "dive")
RANGED_WORDS = ("arrow", "rain", "barrage", "hail", "storm", "volley", "trap", "mark", "javelin", "blades")

# ajustes manuais onde o nome/tema pede algo diferente da regra automática
RANGE_OVERRIDE = {"Holy Strike": "melee", "Lullaby": "ranged", "Flash Powder": "melee", "Smoke Bomb": "melee"}
NATURE_OVERRIDE = {"Bear Trap": "piercing", "Snare Trap": "blunt", "Caltrops": "piercing", "Jump": "piercing",
                   "High Jump": "piercing", "Dragon Dive": "piercing", "Cataclysmic Leap": "blunt",
                   "Mug": "blunt", "Garrote": "slash", "Basic Attack (Claws)": "slash",
                   "Basic Attack (Arsenal)": "slash", "Basic Attack (Dagger)": "slash", "Warbringer": "slash", "Shadow Strike": "slash",
                   "Death Mark": "piercing", "Volley of Blades": "slash", "Snipe": "piercing"}
AREA_OVERRIDE = {"Snipe": "single", "Skull Splitter": "single", "Crushing Blow": "single",
                 "Earthsplitter": "aoe", "Radiant Palm": "aoe", "Godspear": "aoe"}
NO_PIERCE_TAG = {"Righteous Charge", "Earthsplitter"}


def skill_range(sp):
    """'melee' ou 'ranged' conforme o arquétipo, o tipo de dano e o tema do nome."""
    name = sp.get("name", "")
    if name in RANGE_OVERRIDE:
        return RANGE_OVERRIDE[name]
    k, tgt = sp.get("kind"), sp.get("target")
    low = name.lower()
    has_el = bool(sp.get("element") or sp.get("cycle"))
    if k in ("shot", "cloud", "summon"):
        return "ranged"
    if k in ("aura", "orbit"):
        return "melee"    # atinge só quem está colado no personagem
    if sp.get("dmgtype") != "phys":
        return "ranged"   # magias são conjuradas à distância
    if k == "strike" and tgt in ("nearest", "random"):
        # golpe físico que "salta" no alvo (Pommel Bash, Uppercut, Jump) é corpo a corpo;
        # chuva de flechas, armadilhas e golpes elementais vindos do céu são à distância
        return "ranged" if has_el or any(w in low for w in RANGED_WORDS) else "melee"
    if k == "cone" and has_el:
        return "ranged"   # sopros e jutsus (Katon, Fire Breath)
    return "melee"


def tag_name(tag, lang="en"):
    n = TAG_NAMES.get(tag)
    return (n[1] if lang == "pt" else n[0]) if n else tag


def status_name(st, lang="en"):
    n = STATUS_NAMES.get(st)
    return (n[1] if lang == "pt" else n[0]) if n else st


def derive_tags(sp, cid=None):
    """Lista ordenada de tags de uma habilidade."""
    k = sp.get("kind")
    t = set()
    tgt = sp.get("target")
    name = sp.get("name", "")
    low = name.lower()
    has_el = bool(sp.get("element") or sp.get("cycle"))
    if k == "heal":
        t.add("heal")
    elif k == "buff":
        t.add("buff")
    elif k == "summon":
        t |= {"summon", "ranged"}
    else:
        t.add(skill_range(sp))
    if k == "shot":
        t.add("projectile")
    # área x alvo único
    if name in AREA_OVERRIDE:
        t.add(AREA_OVERRIDE[name])
    elif k in ("slash", "cone", "aura", "cloud", "orbit") or sp.get("explode"):
        t.add("aoe")
    elif k == "strike":
        small = (sp.get("count", 1) or 1) <= 1 and (sp.get("radius", 0) or 0) <= 60 and tgt != "self"
        t.add("single" if small else "aoe")
    elif k == "thrust":   # estocada: alvo único, a não ser que seja larga (fenda, investida, lança gigante)
        wide = (sp.get("width", 26) or 26) >= 45 or any(w in low for w in ("splitter", "charge", "storm"))
        t.add("aoe" if wide else "single")
    elif k == "shot":     # vários projéteis, explosão ou atravessa tudo em linha = área
        many = (sp.get("count", 1) or 1) > 1 or (sp.get("pierce", 0) or 0) >= 99
        t.add("aoe" if many else "single")
    if k not in ("heal", "buff"):
        t.add("physical" if sp.get("dmgtype") == "phys" else "magical")
    els = list(sp.get("cycle") or []) + ([sp["element"]] if sp.get("element") else [])
    t |= {e for e in els if e in ELEMENT_TAGS}
    # tipo do golpe físico (corte / perfuração / impacto) e status que cada elemento pode causar
    nat = phys_nature(sp)
    if nat:
        t.add(nat)
    for st in [ELEMENT_STATUS[e] for e in els if e in ELEMENT_STATUS] + ([PHYS_STATUS[nat]] if nat else []):
        if st.get("stun"):
            t.add("stun")
        if st.get("slow"):
            t.add("slow")
        if st.get("dot"):
            t.add("dot")
            if st["dot"][0] == "bleed":
                t.add("bleed")
    if sp.get("stun"):
        t.add("stun")
    if sp.get("slow"):
        t.add("slow")
    if sp.get("pull"):
        t.add("pull")
    if (sp.get("knock", 0) or 0) >= 200 or any(e in ("water", "wind") for e in els):
        t.add("knockback")
    if ((sp.get("pierce", 0) or 0) >= 2 or k == "thrust") and nat not in ("blunt", "slash") and name not in NO_PIERCE_TAG \
            and not any(w in low for w in BLUNT_WORDS):
        t.add("piercing")
    if sp.get("homing"):
        t.add("homing")
    if sp.get("bleed"):
        t.add("bleed")
    if any(e in ("fire", "poison") for e in els) or sp.get("bleed") or k == "cloud":
        t.add("dot")
    return [x for x in TAG_ORDER if x in t]


def phys_nature(sp):
    """Tipo de um golpe físico sem elemento: "slash" (corte), "piercing" (perfuração) ou "blunt" (impacto)."""
    if sp.get("dmgtype") != "phys" or sp.get("kind") in ("heal", "buff", "summon"):
        return None
    if sp.get("element") in ELEMENT_STATUS or sp.get("cycle"):
        return None
    name = sp.get("name", "")
    if name in NATURE_OVERRIDE:
        return NATURE_OVERRIDE[name]
    low = name.lower()
    if any(w in low for w in BLUNT_WORDS):
        return "blunt"
    if any(w in low for w in SLASH_WORDS):
        return "slash"
    if any(w in low for w in PIERCE_WORDS):
        return "piercing"
    if sp.get("kind") in ("thrust", "shot") or (sp.get("pierce", 0) or 0) >= 2:
        return "piercing"
    return "slash"


def status_roll(sp):
    """Regra de status da habilidade (dict com chance e efeito) ou None."""
    els = list(sp.get("cycle") or []) + ([sp["element"]] if sp.get("element") else [])
    for e in els:
        if e in ELEMENT_STATUS:
            return ELEMENT_STATUS[e]
    nat = phys_nature(sp)
    return PHYS_STATUS[nat] if nat else None


def status_chances(sp, lang="en"):
    """Texto 'Burning 35%' / 'Queimando 35%' para cada elemento/tipo de golpe da habilidade."""
    els = list(sp.get("cycle") or []) + ([sp["element"]] if sp.get("element") else [])
    rules = [ELEMENT_STATUS[e] for e in dict.fromkeys(els) if e in ELEMENT_STATUS]
    nat = phys_nature(sp)
    if nat:
        rules.append(PHYS_STATUS[nat])
    out = []
    for r in rules:
        st = "chilled" if r is ELEMENT_STATUS.get("ice") else rule_status(r)
        txt = f"{status_name(st, lang)} {r['chance'] * 100:.0f}%"
        if txt not in out:
            out.append(txt)
    return out


def rule_status(r):
    if r.get("dot"):
        return {"burn": "burning", "poison": "poisoned", "bleed": "bleeding"}[r["dot"][0]]
    if r.get("stun"):
        return "stunned"
    return "slowed"


def add_bleed(sp, cid):
    """(Antigo) sangramento garantido. Agora o sangramento é uma chance por golpe (ver PHYS_STATUS)."""
    return


def class_tags(cid, content):
    """Tags presentes nas ativas da classe, da mais comum para a menos comum."""
    cnt = {}
    cc = content.get(cid, {})
    for sp in [cc.get("basic")] + list(cc.get("actives", [])):
        if not sp:
            continue
        for tg in sp.get("tags", []):
            cnt[tg] = cnt.get(tg, 0) + 1
    return sorted(cnt, key=lambda x: (-cnt[x], TAG_ORDER.index(x)))


def tag_list_text(tags, lang="en", limit=None):
    tags = list(tags)[:limit] if limit else list(tags)
    return " · ".join(tag_name(t, lang) for t in tags)


__all__ = ["derive_tags", "add_bleed", "phys_nature", "status_roll", "status_chances", "class_tags", "tag_name", "status_name", "tag_list_text", "TAG_NAMES",
           "STATUS_NAMES", "ELEMENT_TAGS", "CLASSES"]
