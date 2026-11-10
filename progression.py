"""Conteúdo das classes: golpe básico, 10 ativas, 10 passivas e bônus de status por nível de classe.

O conteúdo vem da planilha `classes.xlsx` (mesma pasta do jogo). Se a planilha não existir, ou se o
openpyxl não estiver instalado, o jogo usa um conteúdo PROVISÓRIO gerado aqui mesmo.

Estrutura de CONTENT[classe]:
    basic    -> especificação do golpe básico (slot 1, fixo)
    actives  -> 10 ativas:   {"id": "A01", "unlock": nível, ...especificação}
    passives -> 10 passivas: {"id": "P01", "unlock": nível, "name", "desc", "effect", "value"}
    levels   -> {nível: {"str", "agi", "int", "vit", "hp"}}  (bônus PERMANENTES do personagem)
"""
import os
import sys

from data import CLASSES, ELEMENTS, BASIC_ORDER, ADVANCED, CLASS_ROLE_DEFS, ROLE_ORDER
from class_skills import class_actives
from class_passives import class_passives, cell_to_effects, effects_to_cell, effects_text
from tags import derive_tags, add_bleed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_FILE = os.path.join(BASE_DIR, "classes.xlsx")
if getattr(sys, "frozen", False):
    # executável: uma classes.xlsx ao lado do .exe tem prioridade sobre a que vai embutida
    _beside = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "classes.xlsx")
    XLSX_FILE = _beside if os.path.exists(_beside) else os.path.join(getattr(sys, "_MEIPASS", BASE_DIR),
                                                                      "classes.xlsx")

MAX_CLASS_LEVEL = 100   # nível máximo padrão das classes
MASTERY_LEVEL = 50      # no Nv 50 a classe está masterizada: todas as habilidades liberadas e usáveis por outras classes
# exceções: (nível máximo, nível de maestria)
CLASS_LIMITS = {"freelancer": (100, 25), "freelancer_t2": (100, 50), "warfarer": (100, 50)}


# Altar of Mastery: classe -> níveis extras comprados com fragmentos (vale para TODOS os personagens).
# O dicionário é o mesmo objeto guardado no Roster (roster.altar).
ALTAR = {}
ALTAR_FRAG_STEP = 0.025   # cada nível do altar: +2,5% de fragmentos por drop
ALTAR_HP = 5              # cada nível extra de classe: +5 de vida e +1 do atributo principal


def base_max_level(cid):
    return CLASS_LIMITS.get(cid, (MAX_CLASS_LEVEL, MASTERY_LEVEL))[0]


def max_level(cid):
    """Nível máximo da classe = padrão + níveis comprados no Altar of Mastery."""
    return base_max_level(cid) + int(ALTAR.get(cid, 0))


def altar_level():
    """Nível do Altar of Mastery = soma dos níveis colocados em todas as classes."""
    return sum(int(v) for v in ALTAR.values())


def altar_cost(cid):
    """Fragmentos da classe para o próximo nível no altar: 1, 2, 4, 8, 16..."""
    return 2 ** int(ALTAR.get(cid, 0))


def frag_gain():
    """Quanto vale cada fragmento dropado (1 + 2,5% por nível do altar)."""
    return 1 + ALTAR_FRAG_STEP * altar_level()


def fmt_frag(v):
    """Fragmentos agora têm decimais: 12, 12.5, 1.025..."""
    txt = f"{float(v):.3f}".rstrip("0").rstrip(".")
    return txt if txt not in ("", "-0") else "0"


def altar_attr(cid, lv):
    """Atributo dado por um nível extra (classes equilibradas alternam FOR, AGI, INT)."""
    attr = CLASSES[cid]["attr"]
    if attr == "bal":
        attr = ("str", "agi", "int")[(lv - base_max_level(cid) - 1) % 3]
    return attr


def level_bonus(cid, lv):
    """Bônus de status de um nível de classe (níveis acima do padrão vêm do Altar of Mastery)."""
    if lv > base_max_level(cid):
        return {altar_attr(cid, lv): 1, "hp": ALTAR_HP}
    return CONTENT.get(cid, {}).get("levels", {}).get(lv, {})


def levels_table(cid):
    """{nível: bônus} de todos os níveis da classe, inclusive os extras do altar."""
    out = {}
    for lv in range(1, max_level(cid) + 1):
        b = level_bonus(cid, lv)
        if b:
            out[lv] = b
    return out


def mastery_level(cid):
    return CLASS_LIMITS.get(cid, (MAX_CLASS_LEVEL, MASTERY_LEVEL))[1]
N_ACTIVES = 10
N_PASSIVES = 10
CLASS_ORDER = ["freelancer"] + [c for b in BASIC_ORDER for c in [b] + ADVANCED[b]] + ["freelancer_t2", "warfarer"]
STAT_KEYS = ("str", "agi", "int", "vit", "hp", "crit", "critdmg", "cdr", "armor", "mres", "dodge", "regen5")

# Bônus provisórios dos níveis de classe que NÃO liberam habilidade, focados no "core" da classe:
#   core  = atributo da classe + status ligados a ele (prioridade)
#   raros = armadura / chance crítica / dano crítico / esquiva que não sejam core (de vez em quando)
#   VIT   = vale para todas as classes
CORE_STATS = {
    "str": ["str", "armor", "str", "critdmg"],
    "agi": ["agi", "dodge", "agi", "crit"],
    "int": ["int", "cdr", "int", "mres"],
    "bal": ["str", "agi", "int"],
}
RARE_STATS = ["armor", "crit", "critdmg", "dodge"]
OTHER_ATTRS = {"str": ("agi", "int"), "agi": ("str", "int"), "int": ("str", "agi")}
SPLIT_BASE, SPLIT_OTHER = 28, 10   # a cada 28 pontos do atributo principal, 10 vão para os outros dois
BONUS_VALUE = {"str": 1, "agi": 1, "int": 1, "vit": 1, "armor": 0.3, "mres": 0.3, "dodge": 0.2, "crit": 0.2,
               "critdmg": 0.4, "cdr": 0.2, "regen5": 0.5}

# ---------------------------------------------------------------------------
# Vocabulário da planilha  <->  parâmetros do jogo
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "Projectile": "shot", "Arc strike": "slash", "Thrust": "thrust", "Area impact": "strike",
    "Cone": "cone", "Aura": "aura", "Orbit": "orbit", "Heal": "heal", "Buff": "buff",
    "Summon": "summon", "Lingering area": "cloud",
}
ARCH_NAME = {v: k for k, v in ARCHETYPES.items()}
TARGETS = {"Nearest": "nearest", "Random": "random", "Self": "self", "Party": "party"}
TARGET_NAME = {v: k for k, v in TARGETS.items()}
ELEM_BY_NAME = {v["name"]: k for k, v in ELEMENTS.items()}
DMG_TYPES = {"Physical": "phys", "Magical": "mag"}

# Efeitos especiais das ativas (até 2 por habilidade): nome na planilha -> parâmetro
SPECIAL_EFFECTS = {
    "Slow (%)": "slow", "Stun (s)": "stun", "Pull (force)": "pull", "Explosion (radius)": "explode",
    "Homing (strength)": "homing", "Knockback (force)": "knock", "Delay (s)": "delay",
    "Buff: damage (%)": "b_dmg", "Buff: speed (%)": "b_speed", "Buff: cooldown (%)": "b_haste",
    "Buff: defense (%)": "b_dr", "Taunt (s)": "taunt", "Weaken (%)": "weaken",
}
SPECIAL_NAME = {v: k for k, v in SPECIAL_EFFECTS.items()}

# Efeitos das passivas: nome na planilha -> chave interna
PASSIVE_EFFECTS = {
    "Physical damage (%)": "phys_dmg",
    "Magic damage (%)": "mag_dmg",
    "All damage (%)": "dmg",
    "Max HP (%)": "hp_pct",
    "Max HP (+)": "hp_flat",
    "Speed (%)": "speed",
    "Cooldown (%)": "cdr",
    "Critical chance (%)": "crit",
    "Critical damage (%)": "critdmg",
    "Defense (%)": "defense",
    "Area (%)": "area",
    "Range (%)": "range",
    "Healing (%)": "heal",
    "Duration (%)": "duration",
    "Regeneration (HP/5s)": "regen5",
    "Pickup range (%)": "magnet",
    "Armor (+)": "armor",
    "Magic defense (+)": "mres",
    "Dodge (%)": "dodge",
    "STR (+)": "str",
    "AGI (+)": "agi",
    "INT (+)": "int",
    "VIT (+)": "vit",
}
PASSIVE_NAME = {v: k for k, v in PASSIVE_EFFECTS.items()}
PASSIVE_SHORT = {  # nomes curtos (usados nos nomes provisórios das passivas)
    "phys_dmg": "Physical Damage", "mag_dmg": "Magic Damage", "dmg": "All Damage", "hp_pct": "Max HP",
    "hp_flat": "Max HP+", "speed": "Speed", "cdr": "Cooldown", "crit": "Critical Chance", "critdmg": "Critical Damage",
    "defense": "Defense", "area": "Area", "heal": "Healing", "duration": "Duration", "regen5": "Regeneration",
    "magnet": "Pickup Range", "armor": "Armor", "mres": "Magic Defense", "dodge": "Dodge", "str": "STR",
    "agi": "AGI", "int": "INT", "vit": "VIT",
}

ATTR_FROM_NAME = {"STR": "str", "AGI": "agi", "INT": "int", "Balanced": "bal"}
ATTR_TO_NAME = {v: k for k, v in ATTR_FROM_NAME.items()}
STYLES = {"Melee": False, "Ranged": True}

# ---------------------------------------------------------------------------
# Compatibilidade: planilhas antigas em português continuam sendo lidas
# ---------------------------------------------------------------------------
PT_ALIASES = {
    # arquétipos
    "Projétil": "Projectile", "Golpe em arco": "Arc strike", "Estocada": "Thrust", "Impacto em área": "Area impact",
    "Órbita": "Orbit", "Cura": "Heal", "Invocação": "Summon", "Área persistente": "Lingering area",
    # alvos
    "Mais próximo": "Nearest", "Aleatório": "Random", "Em si mesmo": "Self",
    # tipos de dano
    "Físico": "Physical", "Mágico": "Magical",
    # elementos
    "Fogo": "Fire", "Gelo": "Ice", "Raio": "Lightning", "Água": "Water", "Vento": "Wind", "Pedra": "Earth",
    "Veneno": "Poison", "Sagrado": "Holy", "Arcano": "Arcane", "Som": "Sound", "Gravidade": "Gravity",
    "Tempo": "Time", "Fumaça": "Smoke", "Nenhum": "None",
    # efeitos especiais
    "Lentidão (%)": "Slow (%)", "Atordoar (s)": "Stun (s)", "Puxar (força)": "Pull (force)",
    "Explosão (raio)": "Explosion (radius)", "Teleguiado (força)": "Homing (strength)",
    "Empurrão (força)": "Knockback (force)", "Atraso (s)": "Delay (s)", "Buff: dano (%)": "Buff: damage (%)",
    "Buff: velocidade (%)": "Buff: speed (%)", "Buff: recarga (%)": "Buff: cooldown (%)",
    "Buff: defesa (%)": "Buff: defense (%)",
    # passivas
    "Dano físico (%)": "Physical damage (%)", "Dano mágico (%)": "Magic damage (%)", "Dano geral (%)": "All damage (%)",
    "Vida máxima (%)": "Max HP (%)", "Vida máxima (+)": "Max HP (+)", "Velocidade (%)": "Speed (%)",
    "Recarga (-%)": "Cooldown (%)", "Chance crítica (%)": "Critical chance (%)", "Dano crítico (%)": "Critical damage (%)",
    "Defesa (%)": "Defense (%)", "Área (%)": "Area (%)", "Cura (%)": "Healing (%)", "Duração (%)": "Duration (%)",
    "Regeneração (hp/5s)": "Regeneration (HP/5s)", "Alcance de coleta (%)": "Pickup range (%)",
    "Armadura (+)": "Armor (+)", "Defesa mágica (+)": "Magic defense (+)", "Esquiva (%)": "Dodge (%)",
    "FOR (+)": "STR (+)",
    # atributos e estilo
    "FOR": "STR", "Equilibrado": "Balanced", "Corpo a corpo": "Melee", "À distância": "Ranged",
}


def en(v):
    """Normaliza um texto da planilha para o vocabulário em inglês (aceita o português antigo)."""
    v = str(v or "").strip()
    return PT_ALIASES.get(v, v)


DEFAULT_ACTIVE_UNLOCKS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45]
DEFAULT_PASSIVE_UNLOCKS = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
# Freelancer (classe inicial): tudo aprendido até a maestria no Nv 25
FREELANCER_ACTIVE_UNLOCKS = [1, 3, 5, 8, 10, 13, 15, 18, 20, 23]
FREELANCER_PASSIVE_UNLOCKS = [2, 4, 7, 9, 12, 14, 17, 19, 22, 25]

CONTENT = {}
LOAD_INFO = {"source": "placeholder", "warnings": []}


# ---------------------------------------------------------------------------
# Conteúdo provisório (até a planilha ser preenchida)
# ---------------------------------------------------------------------------
def _placeholder(cid):
    c = CLASSES[cid]
    if cid == "freelancer":
        a_unlocks, p_unlocks = FREELANCER_ACTIVE_UNLOCKS, FREELANCER_PASSIVE_UNLOCKS
    else:
        a_unlocks, p_unlocks = DEFAULT_ACTIVE_UNLOCKS, DEFAULT_PASSIVE_UNLOCKS
    seeds = c["skills"]
    attr = c["attr"]
    phys = attr in ("str", "agi")

    base = dict(seeds[0])
    base["name"] = f"Basic Attack ({c['weapon']})"
    base["desc"] = "Basic attack with the class weapon"
    import balance   # dano em % do dano do personagem (FOR+AGI+INT); golpe básico = 100% por segundo
    balance.tune_basic(base, c["weapon"])

    actives = []
    for i, sp in enumerate(class_actives(cid, N_ACTIVES)):   # 10 habilidades distintas (class_skills.py)
        sp["id"] = f"A{i + 1:02d}"
        sp["unlock"] = a_unlocks[i]
        balance.tune_active(sp)
        actives.append(sp)

    passives = []
    for i, p in enumerate(class_passives(cid)):   # 9 passivas + capstone (class_passives.py)
        p = dict(p)
        p["id"] = f"P{i + 1:02d}"
        p["unlock"] = p_unlocks[i]
        _legacy_fields(p)
        passives.append(p)

    levels = {}
    core = CORE_STATS[attr]
    # classe geral (Freelancer): FOR/AGI/INT no core e qualquer outro status como raro
    rare = RARE_STATS + ["mres", "cdr"] if attr == "bal" else [k for k in RARE_STATS if k not in core]
    j = ci = mi = oi = 0
    for lv in range(1, base_max_level(cid) + 1):
        b = {k: 0 for k in STAT_KEYS}
        if lv > 1 and lv not in a_unlocks and lv not in p_unlocks:
            j += 1   # só os níveis que não liberam habilidade dão status
            if j % 5 == 0:   # status de todas as classes: alterna VIT (+vida) e regeneração
                if (j // 5) % 2:
                    b["vit"] += BONUS_VALUE["vit"]
                    b["hp"] += 5
                else:
                    b["regen5"] += BONUS_VALUE["regen5"]
            elif j % 7 == 0:
                k = rare[(j // 7 - 1) % len(rare)]
                b[k] += BONUS_VALUE[k]
            else:
                k = core[ci % len(core)]
                ci += 1
                if k == attr and attr in OTHER_ATTRS:
                    # atributo principal: 18 de cada 28 pontos ficam nele, os outros 10 vão para os outros
                    # dois atributos (5 + 5), alternando — o total de atributos continua o mesmo
                    if (mi + 1) * SPLIT_OTHER // SPLIT_BASE > mi * SPLIT_OTHER // SPLIT_BASE:
                        k = OTHER_ATTRS[attr][oi % 2]
                        oi += 1
                    mi += 1
                b[k] += BONUS_VALUE[k]
        levels[lv] = b
    return dict(basic=base, actives=actives, passives=passives, levels=levels)


def _legacy_fields(p):
    """'effect'/'value' = primeiro efeito (usado pelo ícone e por planilhas antigas)."""
    eff = p.get("effects") or {}
    if eff:
        k0 = next(iter(eff))
        p["effect"], p["value"] = k0, eff[k0]
    p.setdefault("capstone", False)


def placeholder_content():
    return {cid: _placeholder(cid) for cid in CLASS_ORDER}


# ---------------------------------------------------------------------------
# Conversões especificação <-> linha da planilha
# ---------------------------------------------------------------------------
# (a ordem das colunas é a mesma da planilha antiga em português; a leitura é por posição)
ACTIVE_COLUMNS = ["ID", "Name", "Unlock Lv", "Archetype", "Target", "Element", "Damage type", "Damage / Heal",
                  "Cooldown (s)", "Count", "Radius / Range", "Arc / Width (°)", "Speed", "Pierce",
                  "Duration (s)", "Effect 1", "Value 1", "Effect 2", "Value 2", "Description"]
PASSIVE_COLUMNS = ["ID", "Name", "Unlock Lv", "Effect", "Value", "Description"]
LEVEL_COLUMNS = ["Level", "STR", "AGI", "INT", "VIT", "HP", "Critical chance (%)", "Critical damage (%)", "Cooldown (%)",
                 "Armor", "Magic defense", "Dodge (%)", "Regen. (HP/5s)", "Actives unlocked", "Passives unlocked",
                 "Notes"]
N_LEVEL_STATS = len(STAT_KEYS)  # colunas B..L


def spec_to_row(sp, sid, unlock):
    k = sp["kind"]
    el = "/".join(ELEMENTS[e]["name"] for e in sp["cycle"]) if sp.get("cycle") else \
        (ELEMENTS[sp["element"]]["name"] if sp.get("element") in ELEMENTS else "None")
    effects = []
    if sp.get("slow"):
        effects.append(("Slow (%)", round((1 - sp["slow"][0]) * 100)))
    for key in ("taunt", "weaken", "stun", "pull", "explode", "homing", "delay"):
        if sp.get(key):
            effects.append((SPECIAL_NAME[key], sp[key]))
    if sp.get("knock") and k != "buff":
        effects.append(("Knockback (force)", sp["knock"]))
    for key, v in sp.get("effects", {}).items():
        effects.append((SPECIAL_NAME["b_" + key], round(v * 100)))
    effects += [(None, None)] * 2
    target = sp.get("target")
    width = sp.get("arc") if k in ("slash", "cone") else sp.get("width") if k == "thrust" else \
        sp.get("spread") if k == "shot" else None
    radius = sp.get("length") if k == "thrust" else sp.get("radius")
    dur = sp.get("life") if k in ("summon", "shot") else sp.get("duration")
    return [sid, sp["name"], unlock, ARCH_NAME[k], TARGET_NAME.get(target) if target else None, el,
            None if k in ("heal", "buff") else ("Physical" if sp.get("dmgtype") == "phys" else "Magical"),
            sp.get("amount") if k == "heal" else sp.get("dmg"), sp.get("cd"), sp.get("count"), radius, width,
            sp.get("speed"), sp.get("pierce"), dur, effects[0][0], effects[0][1], effects[1][0], effects[1][1],
            sp["desc"]]


def _num(v, default=None, warn=None, label=""):
    if v is None or v == "":
        return default
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        if warn is not None:
            warn.append(f"{label}: value '{v}' is not a number")
        return default


def row_to_spec(row, warn, label, class_color):
    """Converte uma linha de ativa/golpe básico em especificação de habilidade (leitura por posição)."""
    g = dict(zip(ACTIVE_COLUMNS, row))
    arch = en(g["Archetype"])
    if arch not in ARCHETYPES:
        warn.append(f"{label}: unknown archetype '{arch}' (use the list)")
        return None
    k = ARCHETYPES[arch]
    sp = dict(kind=k, name=str(g["Name"] or "Unnamed").strip(), desc=str(g["Description"] or "").strip())
    sp["dmgtype"] = DMG_TYPES.get(en(g["Damage type"]), "mag")
    el_txt = str(g["Element"] or "").strip()
    if el_txt and en(el_txt) != "None":
        parts = [en(p) for p in el_txt.replace(",", "/").split("/") if p.strip()]
        els = [ELEM_BY_NAME[p] for p in parts if p in ELEM_BY_NAME]
        for p in parts:
            if p not in ELEM_BY_NAME:
                warn.append(f"{label}: unknown element '{p}'")
        if len(els) == 1:
            sp["element"] = els[0]
        elif len(els) > 1:
            sp["cycle"] = els
    val = _num(g["Damage / Heal"], 10, warn, label)
    if k == "heal":
        sp["amount"] = val
    elif k != "buff":
        sp["dmg"] = val
    sp["cd"] = _num(g["Cooldown (s)"], 1.0, warn, label)
    cnt = _num(g["Count"], None, warn, label)
    if cnt is not None:
        sp["count"] = int(cnt)
    rad = _num(g["Radius / Range"], None, warn, label)
    if rad is not None:
        sp["length" if k == "thrust" else "radius"] = rad
    wid = _num(g["Arc / Width (°)"], None, warn, label)
    if wid is not None:
        sp[{"slash": "arc", "cone": "arc", "thrust": "width", "shot": "spread"}.get(k, "arc")] = wid
    spd = _num(g["Speed"], None, warn, label)
    if spd is not None:
        sp["speed"] = spd
    prc = _num(g["Pierce"], None, warn, label)
    if prc is not None:
        sp["pierce"] = int(prc)
    dur = _num(g["Duration (s)"], None, warn, label)
    if dur is not None:
        sp["life" if k in ("summon", "shot") else "duration"] = dur
    tgt = en(g["Target"])
    if tgt:
        if tgt not in TARGETS:
            warn.append(f"{label}: unknown target '{tgt}'")
        else:
            sp["target"] = TARGETS[tgt]
    if k == "summon":
        sp["color"] = ELEMENTS[sp["element"]]["color"] if sp.get("element") in ELEMENTS else class_color
    effects = {}
    for en_col, vn in (("Effect 1", "Value 1"), ("Effect 2", "Value 2")):
        name = en(g[en_col])
        if not name:
            continue
        v = _num(g[vn], 0, warn, label)
        key = SPECIAL_EFFECTS.get(name)
        if key is None:
            warn.append(f"{label}: unknown effect '{name}'")
        elif key == "slow":
            sp["slow"] = (max(0.05, 1 - v / 100), 1.5)
        elif key.startswith("b_"):
            effects[key[2:]] = v / 100
        else:
            sp[key] = v
    if k == "buff":
        sp["effects"] = effects
        sp.setdefault("target", "party")
    return sp


# ---------------------------------------------------------------------------
# Leitura da planilha
# ---------------------------------------------------------------------------
SEC_BASIC = "BASIC ATTACK (slot 1)"
SEC_ACTIVE = "ACTIVE SKILLS"
SEC_PASSIVE = "PASSIVE SKILLS"
SEC_LEVELS = "LEVEL PROGRESSION"
# títulos aceitos (inglês e o português antigo)
SECTION_PREFIXES = {
    SEC_BASIC: ("BASIC ATTACK", "GOLPE BÁSICO"),
    SEC_ACTIVE: ("ACTIVE SKILLS", "HABILIDADES ATIVAS"),
    SEC_PASSIVE: ("PASSIVE SKILLS", "HABILIDADES PASSIVAS"),
    SEC_LEVELS: ("LEVEL PROGRESSION", "PROGRESSÃO DE NÍVEL"),
}
ALL_PREFIXES = tuple(p for ps in SECTION_PREFIXES.values() for p in ps) + ("TOTAL",)

INFO_LABELS = {
    "Main attribute": "attr", "Weapon": "weapon", "Role": "role", "Summary": "role",
    "Style": "ranged", "Description": "lore",
}
INFO_PT = {"Atributo principal": "Main attribute", "Arma": "Weapon", "Papel": "Role",
           "Vida (multiplicador)": "HP (multiplier)", "Defesa (%)": "Defense (%)",
           "Velocidade (multiplicador)": "Speed (multiplier)", "Estilo": "Style", "Descrição": "Description"}


def _sections(ws):
    """Encontra as seções pelo título na coluna A. Retorna {título: linha do cabeçalho}."""
    found = {}
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if isinstance(v, str):
            for sec, prefixes in SECTION_PREFIXES.items():
                if v.strip().upper().startswith(prefixes):
                    found[sec] = r + 1
    return found


def _rows(ws, header_row, ncols):
    r = header_row + 1
    while r <= ws.max_row:
        first = ws.cell(r, 1).value
        if first is None or (isinstance(first, str) and first.strip().upper().startswith(ALL_PREFIXES)):
            break
        yield r, [ws.cell(r, c).value for c in range(1, ncols + 1)]
        r += 1


def load_from_xlsx(path):
    from openpyxl import load_workbook  # import aqui: o jogo funciona sem openpyxl
    wb = load_workbook(path, data_only=True, read_only=False)
    warn = []
    content = placeholder_content()
    if "Index" in wb.sheetnames:
        load_roles(wb["Index"], warn)
    for cid in CLASS_ORDER:
        name = CLASSES[cid]["name"]
        if name not in wb.sheetnames:
            warn.append(f"Sheet '{name}' not found; using placeholder content")
            continue
        ws = wb[name]
        cc = content[cid]
        info = {}
        for r in range(1, 18):
            lab = ws.cell(r, 1).value
            if isinstance(lab, str):
                lab = INFO_PT.get(lab.strip(), lab.strip())
                if lab in INFO_LABELS:
                    info[INFO_LABELS[lab]] = ws.cell(r, 3).value
        upd = {}
        attr = en(info.get("attr"))
        if attr in ATTR_FROM_NAME:
            upd["attr"] = ATTR_FROM_NAME[attr]
        for key in ("weapon", "role", "lore"):
            if info.get(key):
                upd[key] = str(info[key])
        if upd.get("role") in CLASS_ROLE_DEFS:   # planilha que traz a role (Tank, Caster...) na linha "Role"
            upd["class_role"] = upd.pop("role")
        style = en(info.get("ranged"))
        if style in STYLES:
            upd["ranged"] = STYLES[style]
        CLASSES[cid].update(upd)

        secs = _sections(ws)
        color = CLASSES[cid]["color"]
        if SEC_BASIC in secs:
            for r, row in _rows(ws, secs[SEC_BASIC], len(ACTIVE_COLUMNS)):
                sp = row_to_spec(row, warn, f"{name} / basic attack", color)
                if sp:
                    cc["basic"] = sp
                break
        if SEC_ACTIVE in secs:
            acts = []
            for r, row in _rows(ws, secs[SEC_ACTIVE], len(ACTIVE_COLUMNS)):
                sid = str(row[0]).strip()
                if not row[1] and not row[3]:
                    continue
                sp = row_to_spec(row, warn, f"{name} / {sid}", color)
                if sp:
                    sp["id"] = sid
                    sp["unlock"] = int(_num(row[2], 1, warn, f"{name} / {sid}") or 1)
                    acts.append(sp)
            if acts:
                cc["actives"] = acts[:N_ACTIVES]
        if SEC_PASSIVE in secs:
            pas = []
            for r, row in _rows(ws, secs[SEC_PASSIVE], len(PASSIVE_COLUMNS)):
                g = dict(zip(PASSIVE_COLUMNS, row))
                sid = str(g["ID"]).strip()
                if not g["Name"] and not g["Effect"]:
                    continue
                eff = en(g["Effect"])
                if eff in PASSIVE_EFFECTS:       # planilha antiga: um efeito + valor
                    effects = {PASSIVE_EFFECTS[eff]: _num(g["Value"], 0, warn, f"{name} / {sid}") or 0}
                else:
                    effects, errs = cell_to_effects(g["Effect"])
                    for e in errs:
                        warn.append(f"{name} / {sid}: {e}")
                    if not effects:
                        continue
                p = dict(id=sid, name=fix_passive_name(str(g["Name"] or sid), cid), desc=str(g["Description"] or ""),
                         unlock=int(_num(g["Unlock Lv"], 1, warn, f"{name} / {sid}") or 1), effects=effects,
                         capstone=any(k.startswith("cap:") for k in effects) or str(g["Value"]).strip().lower() == "capstone")
                if not p["desc"]:
                    p["desc"] = effects_text(effects)
                _legacy_fields(p)
                pas.append(p)
            if pas:
                pas = pas[:N_PASSIVES]
                if not any(p["capstone"] for p in pas):   # a última é sempre a capstone
                    pas[-1]["capstone"] = True
                cc["passives"] = pas
        if SEC_LEVELS in secs:
            levels = {}
            for r, row in _rows(ws, secs[SEC_LEVELS], len(LEVEL_COLUMNS)):
                lv = _num(row[0], None)
                if lv is None:
                    continue
                vals = [_num(x, 0, warn, f"{name} / Lv {int(lv)}") or 0 for x in row[1:1 + N_LEVEL_STATS]]
                levels[int(lv)] = dict(zip(STAT_KEYS, vals))
            if levels:
                for lv, b in cc.get("levels", {}).items():   # níveis que faltam na planilha: padrão provisório
                    levels.setdefault(lv, b)
                cc["levels"] = levels
    return content, warn


ROLE_HEADERS = {"role": "name", "behavior": "desc_en", "behavior (en)": "desc_en", "comportamento": "desc",
                "behavior (pt)": "desc", "hp": "hp", "defense/magic defense": "defense",
                "defense / magic def.": "defense", "defense": "defense", "attack": "attack", "speed": "speed"}


def load_roles(ws, warn):
    """Aba Index: coluna "Role" ao lado de cada classe e a tabela de roles (Role, Behavior, HP, Defense, Attack,
    Speed). Uma role nova na tabela passa a valer para as classes que a usarem."""
    head_row, cols, class_col, role_col = None, {}, None, None
    for r in range(1, 12):
        for c in range(1, ws.max_column + 1):
            v = ws.cell(r, c).value
            if not isinstance(v, str):
                continue
            low = v.strip().lower()
            if low == "class" and class_col is None:
                class_col, head_row = c, r
            elif low == "role" and class_col is not None and role_col is None and c == class_col + 1:
                role_col = c
            elif low in ROLE_HEADERS and c > (class_col or 0) + 2:
                key = ROLE_HEADERS[low]
                if key == "name" and "name" in cols:
                    continue
                cols.setdefault(key, c)
    if head_row is None:
        return
    if "name" in cols:   # tabela de roles
        for r in range(head_row + 1, ws.max_row + 1):
            nm = ws.cell(r, cols["name"]).value
            if not isinstance(nm, str) or not nm.strip():
                break   # a tabela termina na primeira linha vazia (embaixo vem a nota explicativa)
            nm = nm.strip()
            if len(nm) > 32:
                break
            base = dict(CLASS_ROLE_DEFS.get(nm) or CLASS_ROLE_DEFS["All-Rounder"])
            for key in ("hp", "defense", "attack", "speed"):
                if key in cols:
                    v = _num(ws.cell(r, cols[key]).value, None, warn, f"Index / role {nm} / {key}")
                    if v is not None and v > 0:
                        base[key] = v
            for key in ("desc", "desc_en"):
                if key in cols and ws.cell(r, cols[key]).value:
                    base[key] = str(ws.cell(r, cols[key]).value).strip()
            if nm not in CLASS_ROLE_DEFS:
                ROLE_ORDER.append(nm)
            CLASS_ROLE_DEFS[nm] = base
    if role_col:   # role de cada classe
        by_name = {c["name"]: cid for cid, c in CLASSES.items()}
        for r in range(head_row + 1, ws.max_row + 1):
            cname, rname = ws.cell(r, class_col).value, ws.cell(r, role_col).value
            if cname in by_name and isinstance(rname, str) and rname.strip():
                if rname.strip() in CLASS_ROLE_DEFS:
                    CLASSES[by_name[cname]]["class_role"] = rname.strip()
                else:
                    warn.append(f"Index / {cname}: unknown role '{rname}' (add it to the role table)")


def fix_passive_name(name, cid):
    """Nome provisório antigo "Gladiator Physical Damage" -> "Physical Damage [Gladiator]"."""
    cname = CLASSES[cid]["name"]
    if name.startswith(cname + " ") and name[len(cname) + 1:] in PASSIVE_SHORT.values():
        return f"{name[len(cname) + 1:]} [{cname}]"
    return name


def clamp_unlocks():
    """Habilidades precisam estar liberadas até a maestria (Nv 50; Freelancer 25)."""
    for cid, cc in CONTENT.items():
        for sp in cc["actives"] + cc["passives"]:
            ml = mastery_level(cid)
            if sp["unlock"] > ml:
                LOAD_INFO["warnings"].append(f"{CLASSES[cid]['name']} / {sp['id']}: unlock Lv {sp['unlock']} "
                                             f"is above mastery ({ml}); using {ml}")
                sp["unlock"] = ml


def tag_attrs():
    """Marca em cada ativa/golpe básico o atributo da classe de origem (define o bônus de dano),
    o sangramento das classes de lâmina e as tags (derivadas da especificação)."""
    for cid, cc in CONTENT.items():
        attr = CLASSES[cid]["attr"]
        for sp in [cc["basic"]] + cc["actives"]:
            sp["attr"] = attr
            sp["cid"] = cid
            add_bleed(sp, cid)
            sp["tags"] = derive_tags(sp, cid)
        for p in cc["passives"]:
            p["cid"] = cid
            _legacy_fields(p)
            p["tags"] = passive_tags(p)


# status -> tag usada no filtro de passivas ("contra alvos sangrando" -> Bleed)
STATUS_TAG = {"burning": "fire", "poisoned": "poison", "bleeding": "bleed", "chilled": "ice", "stunned": "stun",
              "slowed": "slow"}


def passive_tags(p):
    """Tags com que a passiva interage (tagdmg:projectile -> projectile; dmgvs:bleeding -> bleed)."""
    out = []
    for k in (p.get("effects") or {}):
        if ":" not in k:
            continue
        pre, arg = k.split(":", 1)
        t = arg if pre in ("tagdmg", "tagcrit", "taghaste") else STATUS_TAG.get(arg) if pre in ("dmgvs", "critvs") else None
        if t and t not in out:
            out.append(t)
    return out


CACHE_FILE = os.path.join(BASE_DIR, "classes_cache.pkl")


def _load_cache():
    """Versão web (sem openpyxl): o build_web.py salva o conteúdo da classes.xlsx em classes_cache.pkl."""
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        import pickle
        with open(CACHE_FILE, "rb") as f:
            data_ = pickle.load(f)
        cls = data_.pop("__classes__", {})
        roles = data_.pop("__roles__", None)
        if roles:   # roles e dados das classes vindos da planilha
            CLASS_ROLE_DEFS.clear()
            CLASS_ROLE_DEFS.update(roles[0])
            ROLE_ORDER[:] = roles[1]
        for cid, upd in cls.items():
            if cid in CLASSES:
                CLASSES[cid].update(upd)
        CONTENT.update(data_)
        LOAD_INFO["source"] = "classes.xlsx"
        return True
    except Exception as exc:
        LOAD_INFO["warnings"] = [f"Error reading classes_cache.pkl: {exc}"]
        return False


def load():
    """Carrega a planilha se possível; senão, conteúdo provisório."""
    _load()
    clamp_unlocks()
    tag_attrs()


def _load():
    global CONTENT
    CONTENT.clear()
    LOAD_INFO["warnings"] = []
    if os.path.exists(XLSX_FILE):
        try:
            content, warn = load_from_xlsx(XLSX_FILE)
            CONTENT.update(content)
            LOAD_INFO["source"] = "classes.xlsx"
            LOAD_INFO["warnings"] = warn
            return
        except ImportError:
            if _load_cache():   # versão web: conteúdo da planilha já convertido no build
                return
            LOAD_INFO["warnings"] = ["openpyxl is not installed (pip install openpyxl); using placeholder content"]
        except Exception as exc:  # planilha corrompida/aberta de forma inesperada
            LOAD_INFO["warnings"] = [f"Error reading classes.xlsx: {exc}; using placeholder content"]
    elif _load_cache():   # versão web: a planilha vai convertida em classes_cache.pkl
        return
    else:
        LOAD_INFO["warnings"] = ["classes.xlsx not found; using placeholder content"]
    LOAD_INFO["source"] = "placeholder"
    CONTENT.update(placeholder_content())


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------
def ref(cid, sid):
    return f"{cid}:{sid}"


def parse_ref(r):
    cid, _, sid = r.partition(":")
    return cid, sid


def get_active(r):
    cid, sid = parse_ref(r)
    for sp in CONTENT.get(cid, {}).get("actives", []):
        if sp["id"] == sid:
            return sp
    return None


def get_passive(r):
    cid, sid = parse_ref(r)
    for sp in CONTENT.get(cid, {}).get("passives", []):
        if sp["id"] == sid:
            return sp
    return None


def describe_passive(p, lang="en"):
    return effects_text(p.get("effects") or {p["effect"]: p["value"]}, lang)


def is_capstone(p):
    return bool(p and p.get("capstone"))
