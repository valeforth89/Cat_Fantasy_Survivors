"""Altar of Greed (Altar da Ganância): o "gold sink" do jogo.

Gasta gold em bônus PERMANENTES para a party inteira (todos os personagens). Cada stat tem o próprio nível e o
custo do próximo nível sobe exponencialmente (x1,4 por nível daquele stat): subir um stat só fica caro rápido, então
compensa distribuir. Os stats com retorno decrescente (chance crítica, recarga, esquiva) e a Defesa (limitada a
75%) têm um limite de níveis baixo e fácil de alcançar, para não bagunçar os caps.
"""
BASE_COST = 20       # gold do 1º nível de qualquer stat
GROWTH = 1.4         # cada nível do stat multiplica o custo do próximo

# id: (chave do efeito, valor por nível, nível máximo (None = sem limite), nome EN, nome PT,
#      texto do bônus EN, texto PT, símbolo do ícone, cor do ícone)
STATS = {
    "atk": ("dmg", 2.0, None, "Attack", "Ataque", "+{v:g}% damage", "+{v:g}% de dano", "sword_up", (150, 60, 40)),
    "def": ("defense", 1.0, 10, "Defense", "Defesa", "+{v:g}% damage reduction", "+{v:g}% de redução de dano",
            "shield", (60, 90, 150)),
    "hp": ("hp_pct", 3.0, None, "Max HP", "Vida máxima", "+{v:g}% max HP", "+{v:g}% de vida máxima", "heart",
           (150, 50, 70)),
    "range": ("range", 2.0, None, "Range", "Alcance", "+{v:g}% range", "+{v:g}% de alcance", "spear",
              (70, 110, 150)),
    "area": ("area", 2.0, None, "Area", "Área", "+{v:g}% area", "+{v:g}% de área", "rings", (110, 70, 150)),
    "crit": ("crit", 0.5, 10, "Critical chance", "Chance crítica", "+{v:g}% critical chance",
             "+{v:g}% de chance crítica", "star", (140, 110, 30)),
    "critdmg": ("critdmg", 4.0, None, "Critical damage", "Dano crítico", "+{v:g}% critical damage",
                "+{v:g}% de dano crítico", "burst_up", (150, 90, 40)),
    "cdr": ("cdr", 0.5, 10, "Cooldown", "Recarga", "-{v:g}% cooldown", "-{v:g}% de recarga", "hourglass",
            (70, 90, 150)),
    "dodge": ("dodge", 0.5, 10, "Dodge", "Esquiva", "+{v:g}% dodge", "+{v:g}% de esquiva", "boot", (60, 120, 90)),
}
ORDER = list(STATS)

LEVELS = {}   # nível atual de cada stat (o roster carrega/salva; valem para todos os personagens)


def clean(d):
    out = {}
    for k, v in (d or {}).items():
        if k in STATS:
            try:
                lv = max(0, int(v))
            except (TypeError, ValueError):
                continue
            mx = STATS[k][2]
            out[k] = min(lv, mx) if mx else lv
    return out


def level(sid):
    return int(LEVELS.get(sid, 0))


def max_level(sid):
    return STATS[sid][2]


def is_maxed(sid):
    mx = STATS[sid][2]
    return mx is not None and level(sid) >= mx


def cost(sid, lv=None):
    """Gold do próximo nível do stat (20, 28, 39, 55, 77... x1,4 a cada nível daquele stat)."""
    lv = level(sid) if lv is None else lv
    return int(round(BASE_COST * GROWTH ** lv))


def bonus(sid, lv=None):
    lv = level(sid) if lv is None else lv
    return STATS[sid][1] * lv


def totals():
    """Efeitos somados (mesmas chaves das passivas: dmg, defense, hp_pct, range, area, crit, critdmg, cdr, dodge)."""
    out = {}
    for sid, lv in LEVELS.items():
        if sid in STATS and lv:
            key = STATS[sid][0]
            out[key] = out.get(key, 0) + STATS[sid][1] * lv
    return out


def name(sid, lang="en"):
    st = STATS[sid]
    return st[4] if lang == "pt" else st[3]


def bonus_text(sid, lang="en", lv=None):
    st = STATS[sid]
    return (st[6] if lang == "pt" else st[5]).format(v=round(bonus(sid, lv), 2))


def spent():
    """Gold total já gasto no altar."""
    return sum(sum(cost(sid, k) for k in range(level(sid))) for sid in STATS)


def buy(roster, sid):
    """Compra 1 nível do stat. Retorna None se deu certo, ou (mensagem EN, mensagem PT)."""
    if sid not in STATS:
        return ("Unknown stat.", "Atributo desconhecido.")
    if is_maxed(sid):
        return (f"{name(sid)} is already at the maximum ({max_level(sid)} levels).",
                f"{name(sid, 'pt')} já está no máximo ({max_level(sid)} níveis).")
    c = cost(sid)
    if roster.gold < c:
        return (f"Not enough gold: {c} needed (you have {roster.gold}).",
                f"Gold insuficiente: precisa de {c} (você tem {roster.gold}).")
    roster.gold -= c
    LEVELS[sid] = level(sid) + 1
    roster.greed = LEVELS
    roster.save()
    return None
