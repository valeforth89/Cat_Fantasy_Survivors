"""Comportamento e golpe exclusivo de cada monstro (também vale para os elites, que somam as habilidades de classe).

Cada tipo tem:
- um jeito de se mover (perseguir, pairar em volta, manter distância, ziguezague...);
- um golpe característico com aviso no chão (cone, área, linha, projétil ou investida) e efeitos na party
  (sangramento, atordoamento, lentidão, empurrão).

O dano dos golpes é o dano de contato do monstro x um multiplicador. O aviso fica no chão um instante antes do
golpe acontecer, para dar tempo de desviar. O estado de cada monstro fica em e.ai (dict).
"""
import math
import random

from pygame.math import Vector2 as V

import elites as el
import skill_fx as sfx

CONE_COLOR = (230, 70, 70)


def _u(v):
    return v.normalize() if v.length_squared() > 1e-9 else V(1, 0)


# ---------------------------------------------------------------------------
# Tabela de comportamento: move = modo de andar; move_args; atk = golpe; cd = recarga (s)
# ---------------------------------------------------------------------------
SPECS = {
    # Floresta
    "morcego": dict(move="hover", dist=(90, 130), atk="cone", cd=4.0, limit=3, rng=150, radius=140, arc=55, mult=0.9,
                    delay=0.55, fx=dict(slow=0.8), name=("Sonar", "Sonar")),
    "lobo": dict(move="pounce", boost=1.25, atk="bite", cd=1.6, rng=46, mult=1.2, fx=dict(bleed=3.0),
                 name=("Bite", "Mordida")),
    "javali": dict(move="chase", atk="charge", cd=5.5, rng=(150, 360), mult=1.5, delay=0.75, dash=(4.2, 0.6),
                   fx=dict(stun=0.8, knock=260), name=("Charge", "Investida")),
    "esqueleto": dict(move="chase", atk="shot", cd=3.2, rng=(110, 320), mult=0.9, speed=360, size=7,
                      color=(230, 225, 205), fx={}, name=("Bone Throw", "Arremesso de Osso")),
    "zumbi": dict(move="chase", atk="puddle", cd=6.0, rng=(0, 260), radius=70, mult=0.35, delay=0.8, linger=3.5,
                  color=(120, 170, 80), fx=dict(slow=1.0), name=("Rotten Bile", "Bile Podre")),
    # Cidade
    "rato": dict(move="zigzag", atk="bite", cd=2.0, limit=4, rng=34, mult=1.0, fx=dict(bleed=1.5),
                 name=("Plague Bite", "Mordida da Peste")),
    "cao": dict(move="chase", atk="leap", cd=4.0, rng=(90, 230), mult=1.25, delay=0.45, dash=(3.6, 0.35),
                fx=dict(bleed=2.0), name=("Pounce", "Bote")),
    "bruto": dict(move="chase", atk="smash", cd=4.5, rng=80, radius=75, mult=1.6, delay=0.85,
                  fx=dict(stun=0.7, knock=200), name=("Club Smash", "Porretada")),
    "carnical": dict(move="frenzy", boost=1.45, atk="bite", cd=1.3, rng=44, mult=1.1, fx=dict(bleed=2.5),
                     name=("Claws", "Garras")),
    "espectro": dict(move="hover", dist=(95, 135), atk="nova", cd=4.5, rng=140, radius=130, mult=1.2, delay=0.8,
                     blink=7.0, fx=dict(slow=1.5), name=("Wail", "Lamento")),
    # Catedral
    "fatuo": dict(move="chase", boost=1.1, atk="explode", rng=34, radius=60, mult=1.6, delay=0.3,
                  fx={}, name=("Burst", "Explosão")),
    "cultista": dict(move="kite", dist=(190, 240), atk="shot", cd=2.6, rng=(0, 380), mult=1.1, speed=300, size=8,
                     color=(200, 60, 90), fx=dict(slow=0.6), name=("Dark Bolt", "Raio Sombrio")),
    "gargula": dict(move="chase", atk="dive", cd=6.0, rng=(120, 380), radius=75, mult=1.6, delay=1.0,
                    fx=dict(knock=280), name=("Dive", "Mergulho")),
    "armadura": dict(move="chase", atk="lance", cd=4.0, rng=150, length=170, width=26, mult=1.5, delay=0.6,
                     fx=dict(knock=180), name=("Lance Thrust", "Estocada")),
    "serafim": dict(move="kite", dist=(170, 220), atk="smite", cd=5.0, rng=(0, 420), radius=60, mult=1.4,
                    delay=0.95, targets=2, fx=dict(stun=0.5), name=("Fallen Light", "Luz Caída")),
    # Subterrâneo
    "besouro": dict(move="chase", atk="roll", cd=4.5, rng=(80, 240), mult=1.2, delay=0.4, dash=(3.4, 0.5),
                    fx=dict(knock=220), name=("Roll", "Rolamento")),
    "goblin": dict(move="kite", dist=(140, 190), atk="bomb", cd=4.0, rng=(0, 330), radius=58, mult=1.4, delay=1.0,
                   fx=dict(knock=200), name=("Bomb", "Bomba")),
    "golem": dict(move="chase", atk="nova", cd=6.0, rng=110, radius=115, mult=1.5, delay=1.0,
                  fx=dict(stun=0.6), name=("Ground Slam", "Pancada no Chão")),
    "gosma": dict(move="chase", atk="trail", cd=1.2, radius=28, mult=0.25, linger=4.0, color=(110, 200, 120),
                  fx=dict(slow=0.8), name=("Slime Trail", "Rastro de Gosma")),
    "verme": dict(move="chase", atk="erupt", cd=6.5, rng=(140, 500), radius=72, mult=1.7, delay=1.0,
                  fx=dict(knock=300, stun=0.4), name=("Eruption", "Erupção")),
    # Inferno
    "diabrete": dict(move="hover", dist=(110, 160), atk="shot", cd=3.0, limit=4, rng=(0, 300), mult=0.9, speed=320,
                     size=6, color=(255, 120, 40), fx={}, name=("Fireball", "Bola de Fogo")),
    "cao_inferno": dict(move="pounce", boost=1.3, atk="leap", cd=4.0, rng=(90, 240), mult=1.3, delay=0.4,
                        dash=(3.8, 0.35), fx=dict(bleed=2.0), name=("Burning Pounce", "Bote Flamejante")),
    "demonio": dict(move="chase", atk="smash", cd=5.0, rng=85, radius=85, mult=1.7, delay=0.9,
                    fx=dict(stun=0.8, knock=240), name=("Hellish Cleave", "Machadada Infernal")),
    "salamandra": dict(move="chase", boost=1.15, atk="trail", cd=1.0, radius=30, mult=0.35, linger=3.0,
                       color=(255, 120, 40), fx=dict(slow=0.5), name=("Fire Trail", "Rastro de Fogo")),
    "bruxo": dict(move="kite", dist=(180, 230), atk="smite", cd=5.0, rng=(0, 430), radius=62, mult=1.5,
                  delay=1.0, targets=2, fx=dict(knock=150), name=("Hellfire Pillar", "Coluna do Inferno")),
}


def spec(e):
    if getattr(e, "dummy", False) or e.kind == "chefe":
        return None
    return SPECS.get(e.kind)


def move_name(kind, lang="en"):
    sp = SPECS.get(kind)
    if not sp:
        return ""
    return sp["name"][1 if lang == "pt" else 0]


def _state(e, sp):
    ai = getattr(e, "ai", None)
    if ai is None:
        ai = e.ai = dict(cd=random.uniform(0.6, 1.0) * sp.get("cd", 3.0), wind=0.0, act=None, dash=0.0,
                         dvel=V(0, 0), hit=set(), orbit=random.choice((-1, 1)), zig=random.uniform(0, 6.28),
                         blink=sp.get("blink", 0) * random.uniform(0.5, 1.0))
    return ai


# ---------------------------------------------------------------------------
# Movimento: devolve o ponto para onde o monstro anda neste quadro (o Enemy.update anda até ele)
# ---------------------------------------------------------------------------
def goal(run, e, tgt, dt):
    sp = spec(e)
    if sp is None:
        return tgt.pos
    ai = _state(e, sp)
    e.ai_hold = ai["wind"] > 0 and ai["act"] in ("charge", "leap", "roll", "smash", "nova", "lance", "cone",
                                                    "explode")
    e.ai_spd = 1.0
    to = tgt.pos - e.pos
    d = to.length()
    mv = sp["move"]
    rng = sp.get("rng")
    if isinstance(rng, tuple) and rng[0] > 0 and ai["cd"] < 1.3 and d < rng[0] + 25:
        return e.pos - _u(to) * 80   # golpe quase pronto e perto demais: recua para ganhar distância
    if mv == "hover":       # fica por perto, girando em volta, sem encostar
        lo, hi = sp["dist"]
        side = to.rotate(90 * ai["orbit"])
        if d < lo:
            return e.pos - _u(to) * 60 + _u(side) * 40
        if d > hi:
            return tgt.pos
        return e.pos + _u(side) * 60
    if mv == "kite":        # mantém distância (atira de longe)
        lo, hi = sp["dist"]
        if d < lo:
            return e.pos - _u(to) * 80
        if d > hi:
            return tgt.pos
        return e.pos + _u(to.rotate(90 * ai["orbit"])) * 40
    if mv == "zigzag":      # enxame em ziguezague
        ai["zig"] += dt * 7
        return tgt.pos + _u(to).rotate(90) * math.sin(ai["zig"]) * min(80, d * 0.5)
    if mv == "pounce" and d < 260:   # lobo: acelera quando está perto da presa
        e.ai_spd = sp["boost"]
    if mv == "frenzy" and e.hp < e.max_hp * 0.5:   # carniçal: frenesi com pouca vida
        e.ai_spd = sp["boost"]
    if sp.get("boost") and mv == "chase":
        e.ai_spd = sp["boost"]
    return tgt.pos


# ---------------------------------------------------------------------------
# Golpe
# ---------------------------------------------------------------------------
def _in_range(sp, d):
    r = sp.get("rng", 60)
    if isinstance(r, tuple):
        return r[0] <= d <= r[1]
    return d <= r


def _zone(run, e, sp, pos, radius, delay, cone=None, linger=0.0, color=None, mult=None):
    z = el.HostileZone(pos, radius, e.dmg * (mult if mult is not None else sp["mult"]), delay, e,
                       _label(e, sp), color or CONE_COLOR, linger=linger)
    z.fx = dict(sp.get("fx", {}))
    z.cone = cone
    z.monster = True
    z.look = MONSTER_LOOK.get(e.kind) or MONSTER_LOOK.get(sp["atk"])   # animação do golpe (skill_fx)
    run.hostile_zones.append(z)
    return z


def _label(e, sp):
    from data import ENEMY_NAMES
    base = e.name if getattr(e, "elite", None) else ENEMY_NAMES.get(e.kind, e.kind)
    return f"{base} - {sp['name'][0]}"


def act(run, e, tgt, targets, dt):
    sp = spec(e)
    if sp is None or e.stun_t > 0:
        return
    ai = _state(e, sp)
    to = tgt.pos - e.pos
    d = to.length()
    # investida em andamento: anda em linha reta e acerta quem estiver no caminho
    if ai["dash"] > 0:
        ai["dash"] -= dt
        e.pos += ai["dvel"] * dt
        ai["dust"] = ai.get("dust", 0.0) - dt
        if ai["dust"] <= 0:   # poeira levantando atrás da investida
            ai["dust"] = 0.07
            from skills import Fx
            run.fx.append(Fx("anim", e.pos - _u(ai["dvel"]) * e.r, 0.3,
                             frames=sfx.impact(dict(impact="smoke", el="earth"), max(10, e.r * 0.8))))
        for u in targets:
            if u not in ai["hit"] and (u.pos - e.pos).length_squared() < (u.r + e.r + 4) ** 2:
                ai["hit"].add(u)
                run.hostile_hit(u, e.dmg * sp["mult"], e, _label(e, sp), fx=sp.get("fx"), push=ai["dvel"])
        if ai["dash"] <= 0:
            ai["hit"] = set()
        return
    if sp.get("blink"):     # espectro: some e reaparece perto do alvo de vez em quando
        ai["blink"] -= dt
        if ai["blink"] <= 0 and d > 220:
            ai["blink"] = sp["blink"]
            run.fx_ring(e.pos, e.r + 14, (150, 170, 220))
            e.pos = tgt.pos - _u(to) * random.uniform(140, 170)
            run.fx_ring(e.pos, e.r + 14, (150, 170, 220))
    # golpe preparando (o monstro para e mostra o aviso)
    if ai["wind"] > 0:
        ai["wind"] -= dt
        if ai["wind"] <= 0:
            _release(run, e, sp, ai, tgt, targets)
        return
    ai["cd"] -= dt
    a = sp["atk"]
    if a == "trail":        # gosma: deixa poças por onde passa
        if ai["cd"] <= 0:
            ai["cd"] = sp["cd"]
            _zone(run, e, sp, e.pos, sp["radius"], 0.05, linger=sp["linger"], color=sp["color"])
        return
    if ai["cd"] > 0 or not _in_range(sp, d):
        return
    if sp.get("limit"):   # enxames: só alguns usam o golpe ao mesmo tempo (a tela não vira um mar de avisos)
        busy = run.__dict__.setdefault("ai_busy", {})
        now = run.time
        recent = [t for t in busy.get(e.kind, []) if now - t < sp.get("delay", 0.6) + 0.4]
        if len(recent) >= sp["limit"]:
            ai["cd"] = 0.5
            return
        busy[e.kind] = recent + [now]
    ai["cd"] = sp.get("cd", 3.0) * random.uniform(0.85, 1.15)
    ai["act"] = a
    ai["aim"] = V(tgt.pos)
    ai["dir"] = _u(to)
    if a == "bite":         # mordida imediata (sem aviso)
        run.hostile_hit(tgt, e.dmg * sp["mult"], e, _label(e, sp), fx=sp.get("fx"), push=_u(to) * 120)
        from skills import Fx
        run.fx.append(Fx("anim", tgt.pos, 0.26, frames=sfx.impact(dict(impact="cut", el=None), tgt.r + 8)))
        return
    if a == "shot":         # projétil
        sh = el.HostileShot(e.pos, _u(to) * sp["speed"], e.dmg * sp["mult"], sp["size"], 2.4, e, _label(e, sp),
                            sp["color"])
        sh.fx = dict(sp.get("fx", {}))
        sh.look = MONSTER_LOOK.get(e.kind) or dict(proj="dark", el="dark")
        run.hostile_shots.append(sh)
        return
    if a == "explode":      # fogo-fátuo: incha e explode (morre na explosão)
        _zone(run, e, sp, e.pos, sp["radius"], sp["delay"], color=(140, 200, 255))
        ai["wind"] = sp["delay"]
        e.ai_boom = True
        return
    ai["wind"] = sp.get("delay", 0.6)
    if a == "cone":
        _zone(run, e, sp, e.pos, sp["radius"], ai["wind"], cone=(ai["dir"], sp["arc"]))
    elif a in ("smash",):
        _zone(run, e, sp, e.pos + ai["dir"] * (e.r + sp["radius"] * 0.5), sp["radius"], ai["wind"])
    elif a == "nova":
        _zone(run, e, sp, e.pos, sp["radius"] + e.r, ai["wind"])
    elif a in ("puddle", "bomb", "dive", "erupt"):
        _zone(run, e, sp, tgt.pos, sp["radius"], ai["wind"], linger=sp.get("linger", 0.0), color=sp.get("color"))
    elif a == "smite":
        pool = sorted(targets, key=lambda u: (u.pos - e.pos).length_squared())[:sp.get("targets", 1)]
        for u in pool:
            _zone(run, e, sp, u.pos, sp["radius"], ai["wind"], color=(255, 220, 140))
    elif a == "lance":      # linha à frente: várias áreas pequenas em fila
        n = 5
        for k in range(n):
            _zone(run, e, sp, e.pos + ai["dir"] * (e.r + sp["length"] * (k + 0.5) / n), sp["width"], ai["wind"])
    elif a in ("charge", "leap", "roll"):
        end = e.pos + ai["dir"] * sp["dash"][0] * e.speed * sp["dash"][1] * 1.0
        run.hostile_lines.append([V(e.pos), V(end), e.r * 2, ai["wind"], ai["wind"]])


def _release(run, e, sp, ai, tgt, targets):
    a = ai["act"]
    if a in ("charge", "leap", "roll"):
        ai["dash"] = sp["dash"][1]
        ai["dvel"] = ai["dir"] * e.speed * sp["dash"][0]
        ai["hit"] = set()
    elif a == "dive":       # gárgula pousa onde marcou
        e.pos = V(ai["aim"])
        run.fx_ring(e.pos, sp["radius"], (160, 160, 170))
    elif a == "erupt":      # verme surge de baixo da terra onde marcou
        e.pos = V(ai["aim"])
        run.fx_ring(e.pos, sp["radius"], (200, 150, 90))
    elif a == "explode":
        e.hp = 0            # o fogo-fátuo se desfaz na explosão
        e.ai_boom = False


# visual dos golpes (skill_fx): por monstro e, na falta, pelo tipo de golpe
MONSTER_LOOK = {
    "morcego": dict(impact="sound", el="sound"),              # sonar em cone
    "esqueleto": dict(proj="bone", el=None),
    "zumbi": dict(impact="poison", el="poison", name="bile"),  # poça de bile
    "bruto": dict(impact="quake", el="earth"),
    "espectro": dict(impact="sound", el="time"),              # lamento fantasmagórico
    "fatuo": dict(impact="fire", el="ice"),
    "cultista": dict(proj="dark", el="dark"),
    "gargula": dict(impact="quake", el="smoke"),
    "armadura": dict(impact="cut", el=None),
    "serafim": dict(impact="pillar", el="holy"),
    "goblin": dict(impact="fire", el="fire"),
    "golem": dict(impact="quake", el="earth"),
    "gosma": dict(impact="poison", el="poison", name="slime"),
    "verme": dict(impact="quake", el="earth"),
    "diabrete": dict(proj="fireball", el="fire"), "cao_inferno": dict(impact="fire", el="fire"),
    "demonio": dict(impact="quake", el="fire"), "salamandra": dict(impact="fire", el="fire", name="fire"),
    "bruxo": dict(impact="pillar", el="fire"),
    "smash": dict(impact="quake", el="earth"), "nova": dict(impact="sound", el="time"),
    "puddle": dict(impact="poison", el="poison"), "bomb": dict(impact="fire", el="fire"),
    "dive": dict(impact="quake", el="smoke"), "erupt": dict(impact="quake", el="earth"),
    "smite": dict(impact="pillar", el="holy"), "lance": dict(impact="cut", el=None),
    "explode": dict(impact="fire", el="fire"), "cone": dict(impact="sound", el="sound"),
    "trail": dict(impact="poison", el="poison"),
}


# descrição curta do golpe de cada monstro (Wiki)
DESC = {
    "morcego": ("Hovers nearby without touching you; sonar cone that slows", "Fica perto sem encostar; sonar em cone que deixa lento"),
    "lobo": ("Speeds up near prey; bite that causes bleeding", "Acelera perto da presa; mordida que causa sangramento"),
    "javali": ("Backs off and charges in a line; stuns and knocks back", "Recua e investe em linha; atordoa e empurra"),
    "esqueleto": ("Keeps a short distance and throws bones", "Mantém uma distância curta e arremessa ossos"),
    "zumbi": ("Spits rotten bile that leaves a slowing puddle", "Cospe bile podre que deixa uma poça que deixa lento"),
    "rato": ("Zigzags in swarms; plague bite that causes bleeding", "Anda em ziguezague em bando; mordida da peste que causa sangramento"),
    "cao": ("Pounces from a distance; causes bleeding", "Dá o bote de longe; causa sangramento"),
    "bruto": ("Club smash in front of him; stuns", "Porretada à frente; atordoa"),
    "carnical": ("Frenzy when hurt; claws that cause bleeding", "Frenesi quando ferido; garras que causam sangramento"),
    "espectro": ("Floats around, blinks close and wails around itself; slows", "Flutua em volta, some e reaparece perto e solta um lamento em volta; deixa lento"),
    "fatuo": ("Flies at you and explodes", "Voa até você e explode"),
    "cultista": ("Keeps distance and casts dark bolts; slows", "Mantém distância e lança raios sombrios; deixa lento"),
    "gargula": ("Dives from above where it marked the ground; knocks back", "Mergulha do alto onde marcou o chão; empurra"),
    "armadura": ("Lance thrust in a straight line; knocks back", "Estocada de lança em linha reta; empurra"),
    "serafim": ("Keeps distance; fallen light on up to 2 heroes; stuns", "Mantém distância; luz caída em até 2 heróis; atordoa"),
    "besouro": ("Backs off and rolls into you; knocks back", "Recua e rola em cima de você; empurra"),
    "goblin": ("Keeps distance and throws bombs; knocks back", "Mantém distância e joga bombas; empurra"),
    "golem": ("Ground slam around itself; stuns", "Pancada no chão em volta; atordoa"),
    "gosma": ("Leaves a slime trail that slows", "Deixa um rastro de gosma que deixa lento"),
    "verme": ("Burrows and erupts under you; stuns and knocks back", "Se enterra e surge embaixo de você; atordoa e empurra"),
    "diabrete": ("Flies around you and spits fireballs", "Voa em volta de você e cospe bolas de fogo"),
    "cao_inferno": ("Speeds up near prey and pounces from a distance; causes bleeding",
                    "Acelera perto da presa e dá o bote de longe; causa sangramento"),
    "demonio": ("Axe cleave in front of him; stuns and knocks back", "Machadada à frente; atordoa e empurra"),
    "salamandra": ("Leaves a trail of fire that hurts and slows", "Deixa um rastro de fogo que fere e deixa lento"),
    "bruxo": ("Keeps distance; hellfire pillars on up to 2 heroes; knocks back",
              "Mantém distância; colunas do inferno em até 2 heróis; empurra"),
}


def describe(kind, lang="en"):
    sp = SPECS.get(kind)
    if not sp:
        return ""
    d = DESC.get(kind, ("", ""))
    return f"{sp['name'][1 if lang == 'pt' else 0]}: {d[1 if lang == 'pt' else 0]}"
