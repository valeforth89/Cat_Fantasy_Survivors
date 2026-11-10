"""Tuning do dano das habilidades.

Métrica: o DANO DO PERSONAGEM é 10 + o atributo principal da classe atual (FOR, AGI ou INT; Novice, Freelancer e
Warfarer usam a média dos três). O "dmg" de cada habilidade é uma PORCENTAGEM desse dano (100 = 100% por golpe).

- Golpe básico: 100% por segundo de recarga. Armas leves batem mais rápido (e mais fraco por golpe); armas
  pesadas / de duas mãos são mais lentas e batem mais forte, com o mesmo dano por segundo.
- Ativas: o dano por uso cresce com a recarga (um pouco mais que linear: recarga longa = golpe mais forte).
  Área, vários alvos, perfurar, explosão, teleguiado, atordoar, lentidão, empurrão e efeitos elementais
  deixam a habilidade um pouco mais fraca do que uma de dano puro em um alvo. Provocar (Taunt) e Enfraquecer
  (Weaken) também.
- Contínuas: nuvem (dano por segundo), aura (dano por pulso), órbita e invocação (dano por toque).
- Cura e bônus não mudam aqui.
"""
import math

# recarga do golpe básico por arma (s): dano = 100% x recarga
WEAPON_CD = {
    "Dagger": 0.75, "Daggers": 0.75, "Claws": 0.75, "Fist weapons": 0.75, "Holy fists": 0.8,
    "Kunai and shuriken": 0.8, "Short sword": 0.9,
    "Bow": 1.0, "Bow and harp": 1.0, "Staff": 1.0, "White staff": 1.0, "Staff and hourglass": 1.0,
    "Scepter": 1.0, "Grimoire": 1.0, "Enchanted sword": 1.0, "Black staff": 1.1, "Arsenal": 1.1,
    "Spear": 1.15, "Sword and shield": 1.15, "Spear and banner": 1.2, "Holy sword and shield": 1.2,
    "Longbow": 1.25, "Longsword": 1.25, "Long spear": 1.3, "Twin axes": 1.3, "War axe": 1.4,
    "Two-handed axe": 1.6,
}
STATUS_ELEMENTS = {"fire", "ice", "lightning", "poison", "water", "earth", "wind", "holy", "gravity", "time", "sound",
                   "smoke", "arcane"}


def per_cast(cd):
    """Dano total por uso (% do dano do personagem) de uma ativa de dano puro em um alvo."""
    cd = max(0.4, cd)
    return 110 * cd * (1 + 0.05 * (cd - 1))


def modifiers(sp):
    """Multiplicador (<= 1) por área, alvos múltiplos e controle."""
    k = sp["kind"]
    m = 1.0
    r = sp.get("radius", 0) or 0
    if k == "slash":
        m *= 1 - 0.3 * min(1.0, (sp.get("arc", 120) or 120) / 300)
    elif k == "cone":
        m *= 0.72
    elif k == "thrust":
        m *= 0.82
    elif k == "strike":
        m *= 0.7 if r >= 90 else 0.82 if r >= 60 else 0.95
    elif k == "shot":
        p = sp.get("pierce", 1) or 1
        if p >= 99:
            m *= 0.78
        elif p > 1:
            m *= 0.85
        if sp.get("explode"):
            m *= 0.8
        if sp.get("homing"):
            m *= 0.95
    if sp.get("stun"):
        m *= max(0.7, 0.9 - 0.06 * float(sp["stun"]))
    if sp.get("slow"):
        m *= 0.9
    if (sp.get("knock") or 0) >= 250:
        m *= 0.95
    if sp.get("cycle") or sp.get("element") in STATUS_ELEMENTS:
        m *= 0.92
    if sp.get("bleed"):
        m *= 0.9
    if sp.get("taunt"):    # provocação em área: o foco é segurar os inimigos, não o dano
        m *= 0.6
    if sp.get("weaken"):   # Enfraquecer: o grupo todo bate mais forte no alvo
        m *= 0.85
    return m


def active_pct(sp):
    """Dano (%) por golpe de uma ativa."""
    k = sp["kind"]
    cd = sp.get("cd", 1.0) or 1.0
    n = max(1, int(sp.get("count", 1) or 1))
    if k == "aura":       # pulso contínuo em volta: 40% do dano por segundo, por pulso
        return 100 * cd * 0.4
    if k == "orbit":      # lâminas girando: dano por toque
        return 40 / math.sqrt(n)
    if k == "summon":     # invocações batem a cada 0,4 s enquanto vivem
        return 25 / math.sqrt(n)
    if k == "cloud":      # área persistente: dano por segundo durante a duração
        dur = sp.get("duration", 4) or 4
        return per_cast(cd) * 0.55 / dur
    # habilidades de utilidade (provocar, enfraquecer, controle forte): a recarga longa vem do efeito, não do dano
    if sp.get("taunt"):
        cd = min(cd, 2.5)
    elif sp.get("weaken") or (sp.get("stun") or 0) >= 1.2 or (sp.get("slow") and sp.get("target") == "self"):
        cd = min(cd, 4.0)
    total = per_cast(cd) * modifiers(sp)
    if n > 1:
        if k == "strike" and sp.get("target") == "random":   # alvos diferentes
            return total * 0.85 / math.sqrt(n)
        return total * 1.1 / n                                # vários projéteis/impactos no mesmo alvo
    return total


def basic_cd(weapon):
    return WEAPON_CD.get(weapon, 1.0)


def tune_basic(sp, weapon):
    if sp["kind"] in ("heal", "buff"):
        return sp
    cd = basic_cd(weapon)
    sp["cd"] = cd
    n = max(1, int(sp.get("count", 1) or 1))
    sp["dmg"] = round(100 * cd / n)
    return sp


def tune_active(sp):
    if sp["kind"] in ("heal", "buff"):
        return sp
    sp["dmg"] = max(5, int(round(active_pct(sp))))
    return sp
