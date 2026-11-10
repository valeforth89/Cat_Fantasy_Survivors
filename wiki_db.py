"""Wiki - aba "Database": tabelas com ícone geradas a partir dos dados do jogo (classes, habilidades, passivas,
acessórios, troféus, fases, inimigos, power-ups, itens da run, elementos, status e tags).

Tudo é montado na hora a partir de data.py / progression / accessories / trophies, então o que entrar no jogo
aparece aqui sozinho.

tables(lang) -> [dict(title, cols=[(cabeçalho, largura)], rows=[dict(icon=função(tamanho)->Surface, cells=[...])])]
"""
import unicodedata

from data import CLASS_ROLE_DEFS, ROLE_ORDER, ROLE_PT, role_name
from data import (CLASSES, STAGES, BIOMES, ENEMY_TYPES, ENEMY_NAMES, PASSIVES, ELEMENT_STATUS, PHYS_STATUS,
                  ROLE_FROM, ATTR_NAMES, element_color)
from i18n import tr

_CACHE = {}

TIER_NAME = {0: ("Starting", "Inicial"), 1: ("Basic", "Básica"), 2: ("Advanced", "Avançada"),
             3: ("Special", "Especial"), 4: ("Special", "Especial")}
ROLE_NAME = {"swarm": ("Weak swarm · from 0:00", "Enxame fraco · desde 0:00"),
             "mid": ("Intermediate · from 0:20", "Intermediário · a partir de 0:20"),
             "heavy": ("Heavy · from 1:20", "Forte · a partir de 1:20"),
             "new3": ("New from stage III · 0:30", "Novo a partir da fase III · 0:30"),
             "new5": ("New in stage V · 1:30", "Novo na fase V · 1:30")}
# ícones dos elementos, tipos de golpe, status e tags (símbolos de skill_icons)
SYM = {"fire": "flame", "ice": "snowflake", "lightning": "bolt", "water": "wave", "wind": "tornado",
       "earth": "rock", "poison": "poison", "holy": "holy", "arcane": "rune", "sound": "note", "gravity": "gravity",
       "time": "hourglass", "smoke": "tornado", "slash": "sword", "piercing": "spear", "blunt": "fist",
       "burning": "flame", "poisoned": "poison", "bleeding": "drop", "chilled": "snowflake", "stunned": "burst",
       "slowed": "clock", "debuffed": "skull", "elemental": "star", "melee": "sword", "ranged": "bow",
       "projectile": "arrow", "aoe": "burst", "single": "eye", "summon": "summon", "heal": "heal", "buff": "up",
       "physical": "fist", "magical": "orb", "bleed": "drop", "dot": "poison", "stun": "burst", "slow": "clock",
       "knockback": "wave", "pull": "gravity", "homing": "missile"}



def _cpt(n):
    import i18n_names
    return i18n_names.CLASS_PT.get(n, n)

def _L(lang, en, pt):
    return pt if lang == "pt" else en


def norm(s):
    """Minúsculas e sem acentos (para a busca)."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _fmt(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def _tags(sp, lang):
    from tags import tag_name
    return ", ".join(tag_name(t, lang) for t in sp.get("tags") or [])


# ------------------------------------------------------------------ ícones (criados só quando a linha aparece)
def _ic_class(cid):
    def f(size):
        import skill_icons as si
        return si.class_icon(cid, size)
    return f


def _ic_skill(sp, kind):
    def f(size):
        import skill_icons as si
        return si.icon_for(sp, kind, size)
    return f


def _ic_acc(aid):
    def f(size):
        import accessories as accm
        return accm.icon(aid, size)
    return f


def _ic_trophy(tid):
    def f(size):
        import trophies as trophy
        return trophy.icon(tid, size)
    return f


def _ic_enemy(sprite, color):
    def f(size):
        from enemy_sprites import sprite as spr
        import pygame
        surf = spr(sprite, max(4, int(size * 0.4)), color)   # o sprite é 5x o raio: recorta o centro
        out = pygame.Surface((size, size), pygame.SRCALPHA)
        out.blit(surf, ((size - surf.get_width()) // 2, (size - surf.get_height()) // 2))
        return out
    return f


def _ic_pw(kind):
    def f(size):
        import powerups as pw
        return pw.icon(kind, size)
    return f


def _ic_item(name):
    def f(size):
        import skill_icons as si
        return si.item_icon(name, size)
    return f


def _ic_sym(key, color=(110, 110, 130)):
    def f(size):
        import skill_icons as si
        return si._render(SYM.get(key, "star"), _dark(color), (240, 230, 200), size)
    return f


def _dark(c):
    return tuple(int(v * 0.55) for v in c)


# ------------------------------------------------------------------ tabelas
def _classes(lang):
    import progression as prog
    rows = []
    for cid, c in CLASSES.items():
        if c["tier"] == 0:
            unlock = _L(lang, "Starting class", "Classe inicial")
        elif c["tier"] == 1:
            unlock = _L(lang, "Novice Lv 10", "Novato Nv 10")
        elif c["tier"] == 2:
            unlock = _L(lang, f"{CLASSES[c['parent']]['name']} Lv 25 (1 of 2)",
                        f"{_cpt(CLASSES[c['parent']]['name'])} Nv 25 (1 de 2)")
        elif c["tier"] == 3:
            unlock = _L(lang, "All basic classes mastered", "Todas as básicas masterizadas")
        else:
            unlock = _L(lang, "All advanced classes mastered", "Todas as avançadas masterizadas")
        rows.append(dict(icon=_ic_class(cid), cells=[
            c["name"], _L(lang, *TIER_NAME.get(c["tier"], ("", ""))), role_name(cid, lang),
            f"{tr(c['weapon'])} · {tr(ATTR_NAMES.get(c['attr'], c['attr']))}", unlock,
            _L(lang, f"Lv {prog.mastery_level(cid)} / Lv {prog.base_max_level(cid)}",
               f"Nv {prog.mastery_level(cid)} / Nv {prog.base_max_level(cid)}"),
            tr(c.get("lore") or c.get("role", ""))]))
    return dict(title=_L(lang, "Classes", "Classes"),
                cols=[(_L(lang, "Class", "Classe"), 110), (_L(lang, "Tier", "Tipo"), 70), ("Role", 110),
                      (_L(lang, "Weapon · attr.", "Arma · atrib."), 120), (_L(lang, "How to unlock", "Como liberar"), 140),
                      (_L(lang, "Mastery / max", "Maestria / máx."), 90), (_L(lang, "Description", "Descrição"), 206)],
                rows=rows)


def _roles(lang):
    rows = []
    for rn in ROLE_ORDER:
        rd = CLASS_ROLE_DEFS[rn]
        classes = ", ".join(c["name"] for c in CLASSES.values() if c.get("class_role") == rn)
        rows.append(dict(icon=_ic_sym(rn, (200, 170, 90)), cells=[
            (ROLE_PT.get(rn, rn) if lang == "pt" else rn),
            _L(lang, f"HP x{rd['hp']:g} · Def x{rd['defense']:g} · Atk x{rd['attack']:g} · Spd x{rd['speed']:g}",
               f"Vida x{rd['hp']:g} · Def x{rd['defense']:g} · Atq x{rd['attack']:g} · Vel x{rd['speed']:g}"),
            rd.get("desc") if lang == "pt" else rd.get("desc_en", rd.get("desc", "")), classes]))
    return dict(title="Roles",
                cols=[("Role", 150), (_L(lang, "Base scaling", "Scaling base"), 200),
                      (_L(lang, "Behavior", "Comportamento"), 300), (_L(lang, "Classes", "Classes"), 196)],
                rows=rows)


def _skills(lang):
    import progression as prog
    rows = []
    for cid in CLASSES:
        cc = prog.CONTENT.get(cid, {})
        for sp in [cc.get("basic")] + list(cc.get("actives", [])):
            if not sp:
                continue
            kind = [_L(lang, "physical", "físico") if sp.get("dmgtype") == "phys" else _L(lang, "magical", "mágico")]
            if sp.get("dmg"):
                kind.append(_L(lang, f"dmg {_fmt(sp['dmg'])}%", f"dano {_fmt(sp['dmg'])}%"))
            if sp.get("cd"):
                kind.append(_L(lang, f"cd {_fmt(sp['cd'])} s", f"recarga {_fmt(sp['cd'])} s"))
            desc = tr(sp.get("desc", ""))
            tg = _tags(sp, lang)
            rows.append(dict(icon=_ic_skill(sp, "active"), cells=[
                sp["name"], CLASSES[cid]["name"], _L(lang, f"Lv {sp.get('unlock', 1)}", f"Nv {sp.get('unlock', 1)}"),
                " · ".join(kind), desc + (f"  [{tg}]" if tg else "")]))
    return dict(title=_L(lang, "Skills", "Habilidades"),
                cols=[(_L(lang, "Skill", "Habilidade"), 170), (_L(lang, "Class", "Classe"), 100),
                      (_L(lang, "Unlock", "Libera"), 56), (_L(lang, "Type", "Tipo"), 150),
                      (_L(lang, "Description and tags", "Descrição e tags"), 370)],
                rows=rows)


def _passives(lang):
    import progression as prog
    rows = []
    for cid in CLASSES:
        for p in prog.CONTENT.get(cid, {}).get("passives", []):
            eff = prog.describe_passive(p, lang)
            if p.get("capstone"):
                eff += _L(lang, "  (Capstone: 5th slot only)", "  (Capstone: só no 5º espaço)")
            rows.append(dict(icon=_ic_skill(p, "passive"), cells=[
                p["name"], CLASSES[cid]["name"], _L(lang, f"Lv {p.get('unlock', 1)}", f"Nv {p.get('unlock', 1)}"), eff]))
    return dict(title=_L(lang, "Passives", "Passivas"),
                cols=[(_L(lang, "Passive", "Passiva"), 230), (_L(lang, "Class", "Classe"), 100),
                      (_L(lang, "Unlock", "Libera"), 56), (_L(lang, "Effect", "Efeito"), 460)],
                rows=rows)


def acc_source(aid, lang):
    import accessories as accm
    import dungeons as dgm
    a = accm.ACC[aid]
    if a["cat"] == "neck":
        n = CLASSES[a["cls"]]["name"]
        import i18n_names
        return _L(lang, f"Take {n} to Lv 100 (any character)",
                  f"Levar {i18n_names.CLASS_PT.get(n, n)} ao Nv 100 (qualquer personagem)")
    stg = accm.stage_of(aid)
    if stg is not None:
        nm = tr(STAGES[stg]["name"])
        return _L(lang, f"Drops in {nm} (and its Endless)", f"Dropa em {nm} (e no Endless do bioma)")
    dg = accm.dungeon_of(aid)
    if dg is not None:
        nm = dgm.name(dg, lang)
        return _L(lang, f"Drops in the {nm} (red portal)", f"Dropa na {nm} (portal vermelho)")
    return _L(lang, "Future stage", "Fase futura")


def _accessories(lang):
    import accessories as accm
    rows = []
    for cat in accm.CATS:
        for aid in accm.ORDER[cat]:
            rows.append(dict(icon=_ic_acc(aid), cells=[
                accm.name(aid, lang), accm.cat_name(cat, lang), accm.desc(aid, 0, lang), acc_source(aid, lang)]))
    return dict(title=_L(lang, "Accessories", "Acessórios"),
                cols=[(_L(lang, "Accessory", "Acessório"), 180), (_L(lang, "Type", "Tipo"), 80),
                      (_L(lang, "Effect (at +0)", "Efeito (no +0)"), 360), (_L(lang, "How to get", "Como obter"), 226)],
                rows=rows)


def _trophies(lang):
    import trophies as trophy
    rows = []
    for tid in trophy.ORDER:
        st = STAGES[trophy.TROPHIES[tid][0]]
        rows.append(dict(icon=_ic_trophy(tid), cells=[
            trophy.name(tid, lang), f"{tr(st['boss'])} ({tr(st['name'])})", trophy.desc(tid, lang)]))
    return dict(title=_L(lang, "Trophies", "Troféus"),
                cols=[(_L(lang, "Trophy", "Troféu"), 200), (_L(lang, "Dropped by (1st kill)", "Dropado por (1º abate)"), 200),
                      (_L(lang, "Effect (+1 global difficulty)", "Efeito (+1 dificuldade global)"), 446)],
                rows=rows)


def _stages(lang):
    import accessories as accm
    import dungeons as dgm
    rows = []
    for st in STAGES:
        b = next((x for x in BIOMES if st["index"] in x["stages"]), BIOMES[0])
        pos = b["stages"].index(st["index"])
        enemies = [b["enemies"][r] for r in ("swarm", "mid", "heavy")]
        enemies += [b["enemies"][r] for r, (si, _t) in ROLE_FROM.items() if pos >= si]
        drops = ", ".join(accm.name(a, lang) for a in accm.STAGE_DROPS.get(st["index"], []))
        pct = round((st["hp"] - 1) * 100)
        rows.append(dict(icon=_ic_enemy(st["boss_sprite"], st["boss_color"]), cells=[
            tr(st["name"]), tr(st["boss"]), ", ".join(tr(ENEMY_NAMES[k]) for k in enemies),
            _L(lang, f"HP +{pct}% · rewards x{st['reward']:g}", f"Vida +{pct}% · recomp. x{st['reward']:g}"),
            drops or "-"]))
    for did in dgm.ORDER:
        d = dgm.DUNGEONS[did]
        rows.append(dict(icon=_ic_sym("burst", (170, 40, 50)), cells=[
            dgm.name(did, lang), _L(lang, "random (5 classes)", "aleatório (5 classes)"),
            _L(lang, "Super Elites and Elite Squads of unlocked stages",
               "Super Elites e Esquadrões das fases liberadas"),
            _L(lang, "infinite levels", "níveis infinitos"), ", ".join(accm.name(a, lang) for a in d["drops"])]))
    return dict(title=_L(lang, "Stages & dungeons", "Fases e masmorras"),
                cols=[(_L(lang, "Stage", "Fase"), 150), (_L(lang, "Boss", "Chefão"), 140),
                      (_L(lang, "Enemies", "Inimigos"), 200), (_L(lang, "Difficulty", "Dificuldade"), 130),
                      (_L(lang, "Accessory drops", "Drops de acessório"), 226)],
                rows=rows)


def _enemies(lang):
    import monster_ai as mai
    rows = []
    for b in BIOMES:
        for role, k in b["enemies"].items():
            t = ENEMY_TYPES[k]
            dt = _L(lang, "mag.", "mág.") if t.get("dmgtype") == "mag" else _L(lang, "phys.", "fís.")
            rows.append(dict(icon=_ic_enemy(k, t["color"]), cells=[
                tr(ENEMY_NAMES[k]), tr(b["name"]), _L(lang, *ROLE_NAME[role]), str(t["hp"]), f"{t['dmg']} {dt}",
                _fmt(t.get("armor", 0)), _fmt(t.get("mres", 0)), str(t["speed"]), mai.describe(k, lang)]))
    return dict(title=_L(lang, "Enemies", "Inimigos"),
                cols=[(_L(lang, "Enemy", "Inimigo"), 140), (_L(lang, "Biome", "Bioma"), 104),
                      (_L(lang, "Role", "Papel"), 120), (_L(lang, "HP", "Vida"), 46), (_L(lang, "Damage", "Dano"), 66),
                      (_L(lang, "Armor", "Arm."), 46), (_L(lang, "M.Def", "Def.M"), 50), (_L(lang, "Speed", "Vel."), 46),
                      (_L(lang, "Signature move", "Golpe exclusivo"), 280)],
                rows=rows)


def _items(lang):
    import powerups as pw
    rows = []
    for k, p in pw.POWERUPS.items():
        rows.append(dict(icon=_ic_pw(k), cells=[
            p[1] if lang == "pt" else p[0], _L(lang, "Power-up (drop)", "Power-up (drop)"), p[3] if lang == "pt" else p[2],
            _L(lang, "0.2% from normal enemies, 25% from elites", "0,2% de inimigos comuns, 25% de elites")]))
    for name, (desc, mx) in PASSIVES.items():
        rows.append(dict(icon=_ic_item(name), cells=[
            tr(name), _L(lang, "Run item", "Item da run"), tr(desc),
            _L(lang, f"Level-up cards (max Lv {mx}, only for the run)", f"Cartas de level up (máx. Nv {mx}, só na run)")]))
    return dict(title=_L(lang, "Power-ups & run items", "Power-ups e itens da run"),
                cols=[(_L(lang, "Name", "Nome"), 170), (_L(lang, "Type", "Tipo"), 110),
                      (_L(lang, "Effect", "Efeito"), 330), (_L(lang, "How to get", "Como obter"), 236)],
                rows=rows)


def _crafted(lang):
    """Armaduras, calças e botas de materiais (ferreiro) e os materiais de cada monstro."""
    import crafting as crf
    rows = []
    pt = lang == "pt"
    for iid in crf.ORDER:
        it = crf.ITEMS[iid]
        recipe = ", ".join(f"{q} {crf.mat_name(m, lang)}" for m, q in it["recipe"].items())
        rows.append(dict(icon=(lambda size, i=iid: crf.item_icon(i, size)), cells=[
            crf.name(iid, lang), crf.SLOT_NAME[it["slot"]][1 if pt else 0] + " · " + tr(BIOMES[it["biome"]]["name"]),
            "; ".join(crf.effects_lines(iid, 0, lang)) + _L(lang, f" (+{crf.MAX_LV}: x{crf.mult(crf.MAX_LV):g})",
                                                              f" (+{crf.MAX_LV}: x{crf.mult(crf.MAX_LV):g})"),
            recipe]))
    for kind, m in crf.MATERIALS.items():
        b = next((tr(bb["name"]) for bb in BIOMES if kind in bb["enemies"].values()), "")
        rows.append(dict(icon=(lambda size, i=m[0]: crf.material_icon(i, size)), cells=[
            crf.mat_name(m[0], lang), _L(lang, "Material", "Material") + " · " + b,
            _L(lang, f"Dropped by {ENEMY_NAMES.get(kind, kind)} (elites drop more; bosses drop every material of "
                     f"their biome)", f"Dropado por {tr(ENEMY_NAMES.get(kind, kind))} (elites dropam mais; os chefões "
                     f"dropam todos os materiais do bioma)"),
            _L(lang, "Used at the Blacksmith (Armor, Pants & Boots)", "Usado no Ferreiro (Armadura, Calça e Bota)")]))
    return dict(title=_L(lang, "Armor, pants, boots & materials", "Armaduras, calças, botas e materiais"),
                cols=[(_L(lang, "Name", "Nome"), 180), (_L(lang, "Type", "Tipo"), 170),
                      (_L(lang, "Bonuses (+0)", "Bônus (+0)"), 300), (_L(lang, "Recipe / use", "Receita / uso"), 196)],
                rows=rows)


def _greed(lang):
    import greed as grd
    rows = []
    for sid in grd.ORDER:
        st = grd.STATS[sid]
        mx = st[2]
        rows.append(dict(icon=(lambda size, sym=st[7], c=st[8]: __import__("skill_icons")._render(
            sym, c, (230, 230, 240), size)), cells=[
            grd.name(sid, lang), grd.bonus_text(sid, lang, 1) + _L(lang, " per level", " por nível"),
            _L(lang, f"max {mx} levels" if mx else "no limit", f"máx. {mx} níveis" if mx else "sem limite"),
            _L(lang, f"{grd.cost(sid, 0)} gold, x{grd.GROWTH:g} per level of that stat",
               f"{grd.cost(sid, 0)} gold, x{grd.GROWTH:g} a cada nível desse atributo")]))
    return dict(title=_L(lang, "Altar of Greed", "Altar da Ganância"),
                cols=[(_L(lang, "Stat", "Atributo"), 170), (_L(lang, "Bonus", "Bônus"), 260),
                      (_L(lang, "Limit", "Limite"), 140), (_L(lang, "Cost", "Custo"), 276)],
                rows=rows)


def _statuses(lang):
    from tags import TAG_NAMES, STATUS_NAMES
    rows = []
    el_st = {"fire": ("Burning (damage over time)", "Queimando (dano contínuo)"),
             "poison": ("Poisoned (damage over time)", "Envenenado (dano contínuo)"),
             "ice": ("Chilled (slow)", "Congelando (lentidão)"), "water": ("Soaked (light slow)", "Encharcado (lentidão leve)"),
             "lightning": ("Stunned", "Atordoado"), "earth": ("Knocked down (stun)", "Derrubado (atordoado)"),
             "holy": ("Dazzled (stun)", "Ofuscado (atordoado)"), "sound": ("Dizzy (stun)", "Zonzo (atordoado)"),
             "arcane": ("Slowed", "Lento"), "gravity": ("Slowed", "Lento"), "time": ("Slowed", "Lento"),
             "smoke": ("Slowed", "Lento")}
    for el, rule in ELEMENT_STATUS.items():
        rows.append(dict(icon=_ic_sym(el, element_color(el, (110, 110, 130))), cells=[
            TAG_NAMES[el][1] if lang == "pt" else TAG_NAMES[el][0], _L(lang, "Element", "Elemento"),
            _L(lang, f"{round(rule['chance'] * 100)}% chance per hit: ", f"{round(rule['chance'] * 100)}% de chance por golpe: ")
            + _L(lang, *el_st.get(el, ("-", "-")))]))
    phys = {"slash": ("Bleeding", "Sangrando"), "piercing": ("Bleeding", "Sangrando"), "blunt": ("Stunned", "Atordoado")}
    for k, rule in PHYS_STATUS.items():
        rows.append(dict(icon=_ic_sym(k, (140, 130, 120)), cells=[
            TAG_NAMES[k][1] if lang == "pt" else TAG_NAMES[k][0], _L(lang, "Physical hit", "Golpe físico"),
            _L(lang, f"{round(rule['chance'] * 100)}% chance per hit: ", f"{round(rule['chance'] * 100)}% de chance por golpe: ")
            + _L(lang, *phys[k])]))
    for nm, pt_nm, en_txt, pt_txt in (
            ("Taunted", "Provocado", "Attacks the character who taunted it (Taunt skills of tanks). Bosses: half the time.",
             "Ataca o personagem que o provocou (habilidades de Provocar dos tanks). Chefões: metade do tempo."),
            ("Weakened", "Enfraquecido", "Takes more damage from everyone for 4 s (Weaken skills).",
             "Recebe mais dano de todos por 4 s (habilidades de Enfraquecer).")):
        rows.append(dict(icon=_ic_sym(nm, (200, 120, 200)), cells=[
            pt_nm if lang == "pt" else nm, _L(lang, "Debuff", "Debuff"), _L(lang, en_txt, pt_txt)]))
    for k, (en, pt) in STATUS_NAMES.items():
        rows.append(dict(icon=_ic_sym(k, (150, 90, 90)), cells=[
            (pt if lang == "pt" else en).capitalize(), _L(lang, "Enemy status", "Status de inimigo"),
            _L(lang, "Bracers, passives and emblems can give bonuses against enemies with it.",
               "Braceletes, passivas e emblemas podem dar bônus contra inimigos com ele.")]))
    for k, (en, pt) in TAG_NAMES.items():
        if k in ELEMENT_STATUS or k in PHYS_STATUS:
            continue
        rows.append(dict(icon=_ic_sym(k, (90, 110, 150)), cells=[
            pt if lang == "pt" else en, _L(lang, "Skill tag", "Tag de habilidade"),
            _L(lang, "Used by the tag filters, passives and accessories (e.g. +damage with that tag).",
               "Usada nos filtros de tag, passivas e acessórios (ex.: +dano com aquela tag).")]))
    return dict(title=_L(lang, "Elements, statuses & tags", "Elementos, status e tags"),
                cols=[(_L(lang, "Name", "Nome"), 170), (_L(lang, "Kind", "Tipo"), 150), (_L(lang, "Effect", "Efeito"), 526)],
                rows=rows)


def tables(lang):
    """Tabelas da aba Database no idioma (cache)."""
    if lang in _CACHE:
        return _CACHE[lang]
    out = [_classes(lang), _roles(lang), _skills(lang), _passives(lang), _accessories(lang), _trophies(lang), _stages(lang),
           _enemies(lang), _items(lang), _crafted(lang), _greed(lang), _statuses(lang)]
    for t in out:
        for r in t["rows"]:
            r["key"] = norm(" ".join(r["cells"]))
    _CACHE[lang] = out
    return out


def search(query, lang, guide):
    """Busca nas duas abas: ([(tabela, [linhas])], [(título, texto) do guia])."""
    q = norm(query.strip())
    if not q:
        return [], []
    tabs = []
    for t in tables(lang):
        rows = [r for r in t["rows"] if q in r["key"]]
        if rows:
            tabs.append((t, rows))
    texts = []
    for sec_title, entries in guide:
        for title, txt in entries:
            if q in norm(title) or q in norm(txt):
                texts.append((f"{title}   ·   {sec_title}", txt))
    return tabs, texts
