"""Meta progression: membros da party, níveis persistentes, classes e configurações (salvos em JSON)."""
import i18n as _i18n
import json
import os
import sys
import random

import progression as prog
import equipment as eq
import storage
import accessories as accm
import greed as grd
import crafting as crf
from data import CLASSES, ATTRS, DIFFICULTIES, STAGES, GENERAL_LEVEL_STAT, BIOMES, ENDLESS_BASE, is_endless, endless_biome

# no executável (PyInstaller) os saves ficam ao lado do .exe; no código-fonte, ao lado dos .py
BASE_DIR = (os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__)))
SAVE_FILE = os.path.join(BASE_DIR, "save.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
SAVE_SLOTS = 3   # save 1 = save.json (o save de sempre); saves 2 e 3 = save2.json e save3.json


def slot_file(slot):
    return SAVE_FILE if slot <= 1 else os.path.join(BASE_DIR, f"save{slot}.json")


def slot_exists(slot):
    return bool(storage.read_text(slot_file(slot)))


def slot_summary(slot):
    """Resumo de um save para o card do Load Save (lido direto do arquivo, sem carregar o save), ou None."""
    try:
        txt = storage.read_text(slot_file(slot))
        if not txt:
            return None
        d = json.loads(txt)
    except (ValueError, TypeError):
        return None
    import trophies as tr_mod
    import rift
    members = [m for m in d.get("members", []) if isinstance(m, dict)]
    hero = next((m for m in members if m.get("hero")), members[0] if members else {})
    lv100 = set()
    for m in members:
        for cid, val in dict(m.get("class_levels", {})).items():
            try:
                if cid in CLASSES and int(val[0]) >= 100:
                    lv100.add(cid)
            except (TypeError, ValueError, IndexError):
                pass
    cleared = max(0, min(len(STAGES), int(d.get("stages_cleared", 0) or 0)))
    trophies = {t for t in d.get("trophies", []) if t in tr_mod.TROPHIES}
    for i in range(cleared):   # troféus retroativos (fase concluída = troféu do chefão)
        tid = tr_mod.by_stage(i)
        if tid:
            trophies.add(tid)
    accs = [a for a in dict(d.get("acc_owned", {})) if a in accm.ACC]
    rift_lv = int(d.get("rift_lv", 1) or 1) if cleared >= 1 else 0
    parts = dict(stages=(cleared, len(STAGES)), accs=(len(accs), len(accm.ACC)),
                 trophies=(len(trophies), len(tr_mod.TROPHIES)), classes=(len(lv100), len(CLASSES)))
    pct = sum(a / b for a, b in parts.values()) / len(parts) * 100
    cls = hero.get("cls", "freelancer")
    import cats
    look = cats.clean_look(hero["look"]) if isinstance(hero.get("look"), dict) else \
        cats.look_from_name(str(hero.get("name", "Hero"))[:14])
    return dict(slot=slot, name=str(hero.get("name", "Hero"))[:14], cls=cls if cls in CLASSES else "freelancer", look=look,
                level=int(hero.get("level", 1) or 1), gold=int(d.get("gold", 0) or 0), members=len(members),
                rift=rift_lv, pct=pct, **parts)

MAX_LEVEL = None       # nível geral do personagem: sem limite (o nível de classe continua com limite)
MAX_CLASS_LEVEL = prog.MAX_CLASS_LEVEL  # nível máximo padrão das classes (100; Freelancer 50)
MASTERY_LEVEL = prog.MASTERY_LEVEL      # maestria padrão no Nv 50 (Freelancer 25)
MAX_ACTIVE = 5         # membros ativos na party
MAX_MEMBERS = 20       # total de membros recrutáveis (só 5 ficam ativos)
# Slots de habilidade de cada personagem
ACTIVE_CLASS_SLOTS = 4    # slots 2-5: ativas da classe atual (slot 1 = golpe básico, fixo)
ACTIVE_EXTRA_SLOTS = 2    # slots 6-7: ativas de qualquer classe no nível máximo
PASSIVE_CLASS_SLOTS = 5   # passivas 1-5: da classe atual
PASSIVE_EXTRA_SLOTS = 5   # passivas 6-10: de qualquer classe no nível máximo
BASIC_REQ = 10         # Freelancer Nv 10 libera as classes básicas
ADV_REQ = 25           # classe básica Nv 25 libera suas duas avançadas
RECRUIT_BASE_COST = 5  # 1º recrutamento custa 5; cada um seguinte custa o dobro (5, 10, 20, 40, 80...)


def exp_to_next(lv):
    """EXP necessária para ir do nível lv ao lv+1 (nível geral)."""
    return int(100 + lv * 50 + lv * lv * 2)


def class_exp_to_next(lv):
    """EXP necessária para ir do nível de classe lv ao lv+1."""
    return int(100 + lv * 40)


NAMES = ["Aria", "Bram", "Cael", "Dara", "Elio", "Fen", "Gaia", "Hugo", "Iris", "Joran", "Kael", "Lira",
         "Milo", "Nadia", "Orin", "Pia", "Quinn", "Rhea", "Soren", "Tala", "Ugo", "Vera", "Wren", "Yara", "Zeno"]


# --------------------------------------------------------------------------
# Configurações
# --------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "fullscreen": False,
    "difficulty": "Normal",
    "damage_numbers": True,
    "show_fps": False,
    "fps_limit": "Unlimited",   # limite de quadros por segundo: "60", "120", "144" ou "Unlimited"
    "language": "English",
    "slot": 1,            # último save usado (Continue)
}


FPS_LIMITS = ("60", "120", "144", "Unlimited")


def fps_cap(settings):
    """Valor para o clock.tick(): 0 = sem limite."""
    v = str(settings.get("fps_limit", "Unlimited"))
    return int(v) if v.isdigit() else 0


def load_settings():
    s = dict(DEFAULT_SETTINGS)
    try:
        txt = storage.read_text(SETTINGS_FILE)
        if txt:
            s.update({k: v for k, v in json.loads(txt).items() if k in DEFAULT_SETTINGS})
    except (ValueError, AttributeError):
        pass
    s["difficulty"] = {"Fácil": "Easy", "Difícil": "Hard"}.get(s["difficulty"], s["difficulty"])  # saves antigos
    if s["difficulty"] not in DIFFICULTIES:
        s["difficulty"] = "Normal"
    if str(s.get("fps_limit")) not in FPS_LIMITS:
        s["fps_limit"] = DEFAULT_SETTINGS["fps_limit"]
    s["fps_limit"] = str(s["fps_limit"])
    if s["language"] not in ("English", "Português"):
        s["language"] = "English"
    return s


def save_settings(s):
    storage.write_text(SETTINGS_FILE, json.dumps(s, ensure_ascii=False, indent=2))


# --------------------------------------------------------------------------
# Membros
# --------------------------------------------------------------------------
class Member:
    def __init__(self, name, hero=False):
        self.name = name
        self.hero = hero
        self.level = 1
        self.exp = 0
        self.cls = "freelancer"
        self.class_levels = {"freelancer": [1, 0]}  # classe -> [nível, exp]
        self.active = hero
        # loadout por classe (slots da classe atual) e slots de maestria (qualquer classe no Nv máximo)
        # classe -> {"active": [4], "passive": [5], "extra_active": [2], "extra_passive": [5]}  (refs "classe:ID")
        self.loadouts = {}
        # equipamentos: são da CLASSE, compartilhados por todos os personagens (ver equipment.GEAR)
        self.legacy_gear = {}   # saves antigos (antes da 0.0.14): melhorias por personagem, só para migrar
        self.acc = {}           # acessórios equipados: espaço (ring1, ring2, bracer, trinket1, trinket2) -> id
        self.craft = {}         # equipamentos de materiais: espaço (body, legs, feet) -> id (crafting.py)
        import cats
        self.look = cats.random_look()   # aparência do gato: sorteada ao recrutar, editável na tela da party
        self.refresh_loadout()

    @property
    def gear(self):
        return eq.GEAR

    def gear_level(self, cid, slot):
        return eq.gear_level(cid, slot)

    # ---------- persistência ----------
    def to_dict(self):
        return dict(name=self.name, hero=self.hero, level=self.level, exp=self.exp, cls=self.cls,
                    class_levels=self.class_levels, active=self.active, loadouts=self.loadouts,
                    acc=self.acc, craft=self.craft, look=self.look, loadout_version=2)

    @classmethod
    def from_dict(cls, d):
        m = cls(str(d.get("name", "???"))[:14], bool(d.get("hero", False)))
        m.level = max(1, int(d.get("level", 1)))
        m.exp = max(0, int(d.get("exp", 0)))
        m.active = bool(d.get("active", False))
        import cats   # saves antigos (sem aparência): a mesma pelagem de antes, fixa pelo nome
        m.look = cats.clean_look(d["look"]) if isinstance(d.get("look"), dict) else cats.look_from_name(m.name)
        for cid, val in dict(d.get("class_levels", {})).items():
            if cid in CLASSES:
                try:
                    m.class_levels[cid] = [max(1, min(prog.max_level(cid), int(val[0]))), max(0, int(val[1]))]
                except (TypeError, ValueError, IndexError):
                    pass
        for cid, lo in dict(d.get("loadouts", {})).items():
            if cid in CLASSES and isinstance(lo, dict):
                m.loadouts[cid] = {k: list(v) for k, v in lo.items() if isinstance(v, list)}
        for cid, g in dict(d.get("gear", {})).items():
            if cid in CLASSES and isinstance(g, dict):
                m.legacy_gear[cid] = {k: max(0, min(10, int(v))) for k, v in g.items()
                               if k in ("weapon", "helmet") and isinstance(v, (int, float))}
        for slot, aid in dict(d.get("acc", {}) or {}).items():
            if slot in accm.SLOT_CAT and aid in accm.ACC and accm.ACC[aid]["cat"] == accm.SLOT_CAT[slot]:
                m.acc[slot] = aid
        for slot, iid in dict(d.get("craft", {}) or {}).items():
            if slot in crf.SLOTS and iid in crf.ITEMS and crf.ITEMS[iid]["slot"] == slot:
                m.craft[slot] = iid
        cid = d.get("cls", "freelancer")
        if cid in CLASSES and m.is_unlocked(cid):
            m.cls = cid
            m.class_levels.setdefault(cid, [1, 0])
        m.refresh_loadout()
        if d.get("loadout_version", 1) < 2:   # passivas novas (capstones): reorganiza uma vez os saves antigos
            for c in list(m.loadouts):
                m.fill_slots(c)
        return m

    # ---------- classes ----------
    def class_level(self, cid):
        return self.class_levels.get(cid, [0, 0])[0]

    def class_exp(self, cid):
        return self.class_levels.get(cid, [0, 0])[1]

    def all_mastered(self, tier):
        return all(self.class_level(c) >= prog.mastery_level(c) for c, d in CLASSES.items() if d["tier"] == tier)

    def is_unlocked(self, cid):
        c = CLASSES[cid]
        if c["tier"] == 0:
            return True
        if c["tier"] == 3:   # Freelancer: todas as básicas masterizadas
            return self.all_mastered(1)
        if c["tier"] == 4:   # Warfarer: todas as avançadas masterizadas (e o Freelancer liberado)
            return self.all_mastered(1) and self.all_mastered(2)
        if c["tier"] == 1:
            return self.class_level("freelancer") >= BASIC_REQ
        return self.class_level(c["parent"]) >= ADV_REQ

    def unlock_requirement(self, cid):
        c = CLASSES[cid]
        if c["tier"] == 0:
            return ""
        if c["tier"] in (3, 4):
            tier = 1 if c["tier"] == 3 else 2
            total = [k for k, d in CLASSES.items() if d["tier"] == tier]
            done = sum(1 for k in total if self.class_level(k) >= prog.mastery_level(k))
            what = "basic" if tier == 1 else "advanced"
            return f"Requires all {what} classes mastered ({done}/{len(total)})"
        parent = "freelancer" if c["tier"] == 1 else c["parent"]
        need = BASIC_REQ if c["tier"] == 1 else ADV_REQ
        return f"Requires {_i18n.tr(CLASSES[parent]['name'])} Lv {need} (current: {self.class_level(parent)})"

    def unlocked_classes(self):
        return [cid for cid in CLASSES if self.is_unlocked(cid)]

    def mastered_classes(self):
        """Classes masterizadas (Nv 50+): liberam suas habilidades para os slots de maestria."""
        return [cid for cid in CLASSES if self.class_level(cid) >= prog.mastery_level(cid)]

    def set_class(self, cid):
        if not self.is_unlocked(cid):
            return False
        self.cls = cid
        self.class_levels.setdefault(cid, [1, 0])
        self.refresh_loadout()
        return True

    # ---------- status ----------
    def permanent_bonus(self):
        """Soma dos bônus de status de TODOS os níveis de classe já alcançados (vale em qualquer classe)."""
        tot = {k: 0.0 for k in prog.STAT_KEYS}
        for cid, (lv, _) in self.class_levels.items():
            if cid not in CLASSES:
                continue
            for L in range(1, lv + 1):   # inclui os níveis extras do Altar of Mastery (+1 atributo, +5 vida)
                for k, v in prog.level_bonus(cid, L).items():
                    tot[k] = tot.get(k, 0) + v
        for k, v in eq.mastery_bonus(self).items():   # itens +10: bônus permanente de meta progression
            tot[k] = tot.get(k, 0) + v
        return tot

    def stats(self):
        """FOR/AGI/INT/VIT e vida extra: base + nível geral + bônus permanentes dos níveis de classe."""
        bonus = self.permanent_bonus()
        st = {k: 5 + (self.level - 1) * GENERAL_LEVEL_STAT + bonus[k] for k in ATTRS}
        out = {k: int(v) for k, v in st.items()}
        out["hp"] = int(bonus["hp"])
        for k in ("crit", "critdmg", "cdr", "armor", "mres", "dodge", "regen5"):   # demais bônus dos níveis de classe
            out[k] = round(bonus[k], 2)
        return out

    # ---------- habilidades disponíveis ----------
    def effective_class_level(self, cid):
        """Nível da classe; uma classe liberada mas nunca usada conta como Nv 1."""
        return self.class_level(cid) or (1 if self.is_unlocked(cid) else 0)

    def class_actives(self, cid=None):
        """[(ref, especificação, liberada?)] das ativas da classe (padrão: atual)."""
        cid = cid or self.cls
        lv = self.effective_class_level(cid)
        return [(prog.ref(cid, sp["id"]), sp, lv >= sp["unlock"]) for sp in prog.CONTENT[cid]["actives"]]

    def class_passives(self, cid=None):
        cid = cid or self.cls
        lv = self.effective_class_level(cid)
        return [(prog.ref(cid, p["id"]), p, lv >= p["unlock"]) for p in prog.CONTENT[cid]["passives"]]

    def mastery_options(self, kind, cid=None, tiers=None):
        """Habilidades de classes masterizadas (exceto a própria classe do loadout); tiers filtra o nível da classe."""
        cid = cid or self.cls
        getter = self.class_actives if kind == "active" else self.class_passives
        return [(r, sp, True) for mc in self.mastered_classes() if mc != cid
                and (tiers is None or CLASSES[mc]["tier"] in tiers) for r, sp, _ in getter(mc)]

    def open_tiers(self, cid):
        """Freelancer: espaços da classe aceitam habilidades das básicas masterizadas; Warfarer: de qualquer classe."""
        t = CLASSES[cid]["tier"]
        return (1,) if t == 3 else (0, 1, 2, 3) if t == 4 else None

    def slot_options(self, kind, group, cid=None, index=None):
        """Opções para um slot. kind: 'active'/'passive'; group: 'class'/'extra'.
        Passivas: o 5º espaço da classe só aceita a capstone da classe; o 5º espaço de maestria só aceita a
        capstone de outra classe masterizada; os demais espaços não aceitam capstones."""
        cid = cid or self.cls
        if group == "class":
            opts = self.class_actives(cid) if kind == "active" else self.class_passives(cid)
            open_t = self.open_tiers(cid)
            if open_t is not None:
                opts = opts + self.mastery_options(kind, cid, open_t)
        else:
            opts = self.mastery_options(kind, cid)
        if kind == "passive" and index is not None:
            last = PASSIVE_CLASS_SLOTS - 1 if group == "class" else PASSIVE_EXTRA_SLOTS - 1
            want_cap = index == last
            opts = [o for o in opts if prog.is_capstone(o[1]) == want_cap]
            if group == "class" and want_cap:   # o capstone do 5º espaço é sempre o da própria classe
                opts = [o for o in opts if prog.parse_ref(o[0])[0] == cid]
        return opts

    # ---------- loadout (salvo por classe) ----------
    def class_loadout(self, cid=None):
        cid = cid or self.cls
        new = cid not in self.loadouts
        lo = self.loadouts.setdefault(cid, {})
        for key, n in (("active", ACTIVE_CLASS_SLOTS), ("passive", PASSIVE_CLASS_SLOTS),
                       ("extra_active", ACTIVE_EXTRA_SLOTS), ("extra_passive", PASSIVE_EXTRA_SLOTS)):
            lst = lo.get(key)
            if not isinstance(lst, list):
                lst = lo[key] = []
            del lst[n:]                     # ajusta no lugar (referências continuam válidas)
            lst.extend([None] * (n - len(lst)))
        if new:  # primeira vez nesta classe: já equipa o que estiver liberado
            self.fill_slots(cid)
        return lo

    def fill_slots(self, cid=None, only=None):
        """Coloca habilidades liberadas nos slots VAZIOS da classe (only = só estas refs)."""
        cid = cid or self.cls
        for kind in ("active", "passive"):
            slots = self.slots(kind, "class", cid)
            used = set(self.equipped(kind, cid))
            for i in range(len(slots)):
                if slots[i] is not None:
                    continue
                for r, _, unlocked in self.slot_options(kind, "class", cid, i):
                    if prog.parse_ref(r)[0] != cid:   # só preenche com habilidades da própria classe
                        continue
                    if unlocked and r not in used and (only is None or r in only):
                        slots[i] = r
                        used.add(r)
                        break

    def slots(self, kind, group, cid=None):
        lo = self.class_loadout(cid)
        return lo[kind] if group == "class" else lo["extra_" + kind]

    def equipped(self, kind, cid=None):
        return [r for r in self.slots(kind, "class", cid) + self.slots(kind, "extra", cid) if r]

    def equip(self, kind, group, index, ref, cid=None):
        """Equipa (ou limpa, com ref=None) um slot do loadout da classe cid. Retorna erro ou None."""
        slots = self.slots(kind, group, cid)
        if ref is None:
            slots[index] = None
            return None
        valid = {r: ok for r, _, ok in self.slot_options(kind, group, cid, index)}
        if ref not in valid:
            return "This skill can't go in this slot."
        if not valid[ref]:
            return "Skill not unlocked yet at this class level."
        if ref in slots:  # já está em outro slot do mesmo grupo: troca de lugar (se couber lá)
            j = slots.index(ref)
            other = slots[index]
            ok_there = other is None or other in {r for r, _, _ in self.slot_options(kind, group, cid, j)}
            slots[j] = other if ok_there else None
        slots[index] = ref
        return None

    def has_mastery_slots(self, cid=None):
        """A classe tem algo equipado nos slots de maestria?"""
        cid = cid or self.cls
        return cid in self.loadouts and any(self.slots(k, "extra", cid)[i]
                                            for k in ("active", "passive")
                                            for i in range(len(self.slots(k, "extra", cid))))

    def copy_mastery(self, src, dst):
        """Copia os slots de maestria da classe src para a classe dst (pula o que não couber). Retorna quantos."""
        n = 0
        for kind in ("active", "passive"):
            for i, ref in enumerate(list(self.slots(kind, "extra", src))):
                if ref and self.equip(kind, "extra", i, ref, dst) is None:
                    n += 1
        return n

    def refresh_loadout(self):
        """Em todas as classes: remove do loadout o que ficou inválido (ex.: planilha mudou).
        Slots que o jogador deixou vazios continuam vazios."""
        if not prog.CONTENT:
            prog.load()
        for cid in set(self.loadouts) | {self.cls}:
            if cid not in CLASSES:
                continue
            for kind in ("active", "passive"):
                for group in ("class", "extra"):
                    slots = self.slots(kind, group, cid)
                    seen = set()
                    for i, r in enumerate(slots):
                        ok = {x for x, _, unlocked in self.slot_options(kind, group, cid, i) if unlocked}
                        if r not in ok or r in seen:
                            slots[i] = None
                        else:
                            seen.add(r)

    def active_specs(self):
        """Golpe básico + ativas equipadas, na ordem dos slots."""
        out = [prog.CONTENT[self.cls]["basic"]]
        out += [sp for sp in (prog.get_active(r) for r in self.equipped("active")) if sp]
        return out

    def passive_specs(self):
        return [p for p in (prog.get_passive(r) for r in self.equipped("passive")) if p]

    # ---------- meta progression ----------
    def gain_exp(self, amount):
        """Aplica a EXP do fim de partida ao nível geral e ao nível da classe atual."""
        rep = dict(name=self.name, look=self.look, exp=amount, lv0=self.level, cls=self.cls, clv0=self.class_level(self.cls))
        before = set(self.unlocked_classes())

        self.exp += amount
        while self.exp >= exp_to_next(self.level):   # nível geral sem limite
            self.exp -= exp_to_next(self.level)
            self.level += 1

        entry = self.class_levels.setdefault(self.cls, [1, 0])
        entry[1] += amount
        cap = prog.max_level(self.cls)
        while entry[0] < cap and entry[1] >= class_exp_to_next(entry[0]):
            entry[1] -= class_exp_to_next(entry[0])
            entry[0] += 1
        if entry[0] >= cap:
            entry[1] = 0

        lv0, lv1 = rep["clv0"], entry[0]
        new_refs = {prog.ref(self.cls, sp["id"]) for sp in
                    prog.CONTENT[self.cls]["actives"] + prog.CONTENT[self.cls]["passives"] if lv0 < sp["unlock"] <= lv1}
        new_skills = [sp["name"] for sp in prog.CONTENT[self.cls]["actives"] + prog.CONTENT[self.cls]["passives"]
                      if lv0 < sp["unlock"] <= lv1]
        self.fill_slots(self.cls, only=new_refs)  # habilidades recém-liberadas entram nos slots vazios
        rep.update(lv1=self.level, clv1=lv1, new_skills=new_skills, mastered=lv1 >= prog.mastery_level(self.cls) > lv0,
                   unlocks=[CLASSES[c]["name"] for c in self.unlocked_classes() if c not in before])
        return rep


# --------------------------------------------------------------------------
# Roster (todos os membros recrutados)
# --------------------------------------------------------------------------
def _clean_altar(d):
    out = {}
    for k, v in (d or {}).items():
        try:
            if k in CLASSES and int(v) > 0:
                out[k] = int(v)
        except (TypeError, ValueError):
            pass
    return out


def _clean_gear(d):
    out = {}
    for cid, g in (d or {}).items():
        if cid in CLASSES and isinstance(g, dict):
            out[cid] = {k: max(0, min(10, int(v))) for k, v in g.items()
                        if k in ("weapon", "helmet") and isinstance(v, (int, float))}
    return out


class Roster:
    def __init__(self, members=None, gold=0, recruits=None, stages_cleared=0, stage=0, fragments=None,
                 endless_best=None, trophies=None, trophies_on=None, altar=None, gear=None, acc_owned=None,
                 acc_frags=None, dungeon_lv=None, rift_lv=1, unlocks=None, tips_seen=None, greed=None,
                 materials=None, craft_owned=None):
        # Altar of Mastery (níveis extras por classe) e equipamentos por classe: valem para todos os personagens
        prog.ALTAR.clear()
        prog.ALTAR.update(_clean_altar(altar))
        self.altar = prog.ALTAR
        eq.GEAR.clear()
        eq.GEAR.update(_clean_gear(gear))
        self.gear = eq.GEAR
        # Altar of Greed (níveis comprados com gold, valem para todos os personagens)
        grd.LEVELS.clear()
        grd.LEVELS.update(grd.clean(greed))
        self.greed = grd.LEVELS
        # materiais dos monstros e equipamentos criados no ferreiro (roupa, calça, bota)
        self.materials = {k: max(0, int(v)) for k, v in (materials or {}).items()
                          if k in crf.MAT and isinstance(v, (int, float))}
        crf.OWNED.clear()
        crf.OWNED.update({k: max(0, min(crf.MAX_LV, int(v))) for k, v in (craft_owned or {}).items()
                          if k in crf.ITEMS and isinstance(v, (int, float))})
        self.craft_owned = crf.OWNED
        self.members = members or []
        # acessórios: únicos, desbloqueio da conta (id -> nível) e fragmentos por categoria
        accm.OWNED.clear()
        for k, v in (acc_owned or {}).items():
            try:
                if k in accm.ACC:
                    accm.OWNED[k] = max(0, min(accm.MAX_LV, int(v)))
            except (TypeError, ValueError):
                pass
        self.acc_owned = accm.OWNED
        import dungeons as dgm
        self.rift_lv = max(1, int(rift_lv)) if isinstance(rift_lv, (int, float)) else 1   # Endless Rift
        # new player experience: lugares do acampamento liberados e dicas já vistas (saves antigos: tudo liberado)
        import tips as tips_mod
        self.unlocks = set(tips_mod.UNLOCKS) if unlocks is None and members else set(unlocks or [])
        self.tips_seen = set(tips_mod.TIPS) if tips_seen is None and members else set(tips_seen or [])
        self.dungeon_lv = {d: 1 for d in dgm.ORDER}   # masmorras: maior nível liberado de cada uma
        for k, v in (dungeon_lv or {}).items():
            if k in self.dungeon_lv and isinstance(v, (int, float)):
                self.dungeon_lv[k] = max(1, int(v))
        self.acc_frags = {c: 0 for c in accm.CATS}
        for k, v in (acc_frags or {}).items():
            if k in self.acc_frags and isinstance(v, (int, float)):
                self.acc_frags[k] = max(0, int(v))
        self.check_necklaces()   # retroativo: classes que já estão no nível máximo
        worn = set()
        for m in self.members:   # cada acessório só com um personagem (e só se foi obtido)
            for slot, aid in list(m.acc.items()):
                if aid not in self.acc_owned or aid in worn:
                    del m.acc[slot]
                else:
                    worn.add(aid)
        for m in self.members:   # saves antigos: junta as melhorias de cada personagem (fica a maior)
            for cid, g in m.legacy_gear.items():
                cur = eq.GEAR.setdefault(cid, {})
                for slot, lv in g.items():
                    cur[slot] = max(cur.get(slot, 0), lv)
            m.legacy_gear = {}
        self.fragments = {}   # inventário (fragmentos agora têm decimais)
        for k, v in (fragments or {}).items():
            try:
                if k in CLASSES:
                    self.fragments[k] = round(max(0.0, float(v)), 3)
            except (TypeError, ValueError):
                pass
        self.gold = gold
        self.stages_cleared = stages_cleared   # quantas fases já foram concluídas (libera a seguinte)
        self.endless_best = {k: float(v) for k, v in (endless_best or {}).items()}   # melhor tempo no Endless
        import trophies as tr_mod
        self.trophies = [t for t in (trophies or []) if t in tr_mod.TROPHIES]          # troféus obtidos (conta)
        for i in range(min(stages_cleared, len(STAGES))):   # retroativo: fase já concluída = troféu do chefão
            tid = tr_mod.by_stage(i)
            if tid and tid not in self.trophies:
                self.trophies.append(tid)
        self.trophies_on = [t for t in (trophies_on or []) if t in self.trophies]     # troféus ativos no altar
        self.stage = stage if self.stage_unlocked(stage) else min(stage, stages_cleared, len(STAGES) - 1)
        self.fix()
        # quantos recrutamentos já foram feitos (dispensar alguém não barateia o próximo)
        self.recruits = recruits if recruits is not None else len(self.members) - 1

    # ---------- new player experience ----------
    def check_unlocks(self):
        """Libera os lugares do acampamento conforme o progresso. Retorna os que acabaram de liberar."""
        cond = {
            "chest": any(v > 0 for v in self.fragments.values()) or any(v > 0 for v in self.acc_frags.values()),
            "smith": self.stages_cleared >= 3,
            "jeweler": bool(self.acc_owned),
            "altar": bool(self.trophies),
            "mastery": any(m.class_level(cid) >= prog.mastery_level(cid) for m in self.members for cid in CLASSES),
            "dungeons": self.stages_cleared >= 5,
            "greed": self.stages_cleared >= 4 or self.gold >= 150,      # Altar of Greed: o gold começa a sobrar
            "craft": self.stages_cleared >= 3 and any(v > 0 for v in self.materials.values()),
        }
        new = [k for k, ok in cond.items() if ok and k not in self.unlocks]
        if new:
            self.unlocks.update(new)
            self.save()
        return new

    def unlocked(self, key):
        return key is None or key in self.unlocks

    # ---------- acessórios ----------
    def acc_gain(self, aid):
        """Drop de acessório: novo (desbloqueia) ou repetido (vira fragmento da categoria). Retorna True se novo."""
        if aid in self.acc_owned:
            cat = accm.ACC[aid]["cat"]
            if cat == "neck":   # colar repetido: vira fragmentos da classe dele (que melhoram o colar)
                cid = accm.neck_class(aid)
                self.fragments[cid] = round(self.fragments.get(cid, 0) + accm.NECK_DUP_FRAGS, 3)
            else:
                self.acc_frags[cat] = self.acc_frags.get(cat, 0) + 1
            self.save()
            return False
        self.acc_owned[aid] = 0
        self.save()
        return True

    def check_necklaces(self):
        """Colar de cada classe: liberado quando algum personagem chega ao nível máximo padrão da classe.
        Retorna os ids recém-liberados."""
        new = []
        for aid in accm.ORDER["neck"]:
            if aid in self.acc_owned:
                continue
            cid = accm.neck_class(aid)
            if any(m.class_levels.get(cid, [0])[0] >= prog.base_max_level(cid) for m in self.members):
                self.acc_owned[aid] = 0
                new.append(aid)
        return new

    def acc_wearer(self, aid):
        for m in self.members:
            for slot, a in m.acc.items():
                if a == aid:
                    return m, slot
        return None, None

    def equip_acc(self, member, slot, aid):
        """Equipa (aid=None tira). Se outro personagem usa o acessório, ele sai de lá. Retorna erro ou None."""
        if aid is None:
            member.acc.pop(slot, None)
            self.save()
            return None
        if aid not in self.acc_owned:
            return ("You don't have this accessory yet.", "Você ainda não tem este acessório.")
        if accm.ACC[aid]["cat"] != accm.SLOT_CAT.get(slot):
            return ("This accessory doesn't fit this slot.", "Este acessório não serve neste espaço.")
        other, oslot = self.acc_wearer(aid)
        if other is not None:
            del other.acc[oslot]
        member.acc[slot] = aid
        self.save()
        return None

    def upgrade_acc(self, aid):
        lv = self.acc_owned.get(aid)
        if lv is None:
            return ("You don't have this accessory yet.", "Você ainda não tem este acessório.")
        if lv >= accm.MAX_LV:
            return (f"Already at the maximum (+{accm.MAX_LV}).", f"Já está no máximo (+{accm.MAX_LV}).")
        cat = accm.ACC[aid]["cat"]
        cost = accm.upgrade_cost(lv, aid)
        if cat == "neck":   # colares: fragmentos da classe do colar
            cid = accm.neck_class(aid)
            have = self.fragments.get(cid, 0)
            if have + 1e-9 < cost:
                n = CLASSES[cid]["name"]
                return (f"Not enough {n} Fragments: need {cost}, you have {prog.fmt_frag(have)}.",
                        f"Fragmentos de {_i18n.tr(n) if _i18n.LANG == 'pt' else n} insuficientes: precisa de {cost}, você "
                        f"tem {prog.fmt_frag(have)}.")
            self.fragments[cid] = round(have - cost, 3)
            self.acc_owned[aid] = lv + 1
            self.save()
            return None
        have = self.acc_frags.get(cat, 0)
        if have < cost:
            return (f"Not enough {accm.cat_name(cat)} Fragments: need {cost}, you have {have}.",
                    f"Fragmentos de {accm.cat_name(cat, 'pt')} insuficientes: precisa de {cost}, você tem {have}.")
        self.acc_frags[cat] = have - cost
        self.acc_owned[aid] = lv + 1
        self.save()
        return None

    def add_fragments(self, cid, n):
        self.fragments[cid] = round(self.fragments.get(cid, 0) + n, 3)

    def offer_altar(self, cid):
        """Coloca +1 nível da classe no Altar of Mastery. Retorna None se deu certo, ou a mensagem de erro."""
        cost = prog.altar_cost(cid)
        have = self.fragments.get(cid, 0)
        if have + 1e-9 < cost:
            return (f"Not enough {_i18n.tr(CLASSES[cid]['name'])} Fragments: need {cost}, you have {prog.fmt_frag(have)}.",
                    f"Fragmentos de {_i18n.tr(CLASSES[cid]['name'])} insuficientes: precisa de {cost}, você tem "
                    f"{prog.fmt_frag(have)}.")
        self.fragments[cid] = round(have - cost, 3)
        self.altar[cid] = int(self.altar.get(cid, 0)) + 1
        self.save()
        return None

    def toggle_trophy(self, tid):
        """Ativa/desativa um troféu obtido. Retorna True se ficou ativo."""
        if tid not in self.trophies:
            return False
        if tid in self.trophies_on:
            self.trophies_on.remove(tid)
            on = False
        else:
            self.trophies_on.append(tid)
            on = True
        self.save()
        return on

    def stage_unlocked(self, sid):
        """Fases normais: em sequência. Endless: libera ao concluir a fase V do bioma. Endless Rift: Floresta I."""
        import rift
        if sid == rift.RIFT_ID:
            return rift.unlocked(self)
        if is_endless(sid):
            if sid - ENDLESS_BASE >= len(BIOMES):
                return False
            b = endless_biome(sid)
            return bool(b["stages"]) and self.stages_cleared > max(b["stages"])
        return 0 <= sid < len(STAGES) and sid <= self.stages_cleared

    def fix(self):
        heroes = [m for m in self.members if m.hero]
        if not heroes:
            hero = Member("Hero", hero=True)
            self.members.insert(0, hero)
            heroes = [hero]
        for extra in heroes[1:]:
            extra.hero = False
        hero = heroes[0]
        self.members.remove(hero)
        self.members.insert(0, hero)
        hero.active = True
        count = 0
        for m in self.members:
            if m.active:
                count += 1
                if count > MAX_ACTIVE:
                    m.active = False

    @classmethod
    def load(cls, slot=1):
        r = cls._load(slot)
        r.slot = slot
        return r

    @classmethod
    def new(cls, slot):
        """Save novo (vazio) no espaço slot."""
        r = cls()
        r.slot = slot
        return r

    @classmethod
    def _load(cls, slot):
        try:
            txt = storage.read_text(slot_file(slot))
            if not txt:
                return cls()
            data = json.loads(txt)
            recruits = data.get("recruits")
            altar = data.get("altar") if isinstance(data.get("altar"), dict) else None
            prog.ALTAR.clear()
            prog.ALTAR.update(_clean_altar(altar))   # antes dos membros: o nível máximo das classes depende dele
            return cls([Member.from_dict(d) for d in data.get("members", [])], altar=altar,
                       acc_owned=data.get("acc_owned") if isinstance(data.get("acc_owned"), dict) else None,
                       acc_frags=data.get("acc_frags") if isinstance(data.get("acc_frags"), dict) else None,
                       dungeon_lv=data.get("dungeon_lv") if isinstance(data.get("dungeon_lv"), dict) else None,
                       rift_lv=data.get("rift_lv", 1),
                       unlocks=data.get("unlocks") if isinstance(data.get("unlocks"), list) else None,
                       tips_seen=data.get("tips_seen") if isinstance(data.get("tips_seen"), list) else None,
                       gear=data.get("gear") if isinstance(data.get("gear"), dict) else None,
                       greed=data.get("greed") if isinstance(data.get("greed"), dict) else None,
                       materials=data.get("materials") if isinstance(data.get("materials"), dict) else None,
                       craft_owned=data.get("craft_owned") if isinstance(data.get("craft_owned"), dict) else None,
                       gold=max(0, int(data.get("gold", 0))),
                       recruits=max(0, int(recruits)) if recruits is not None else None,
                       stages_cleared=max(0, int(data.get("stages_cleared", 0))),
                       stage=max(0, int(data.get("stage", 0))),
                       endless_best=data.get("endless_best") if isinstance(data.get("endless_best"), dict) else None,
                       trophies=data.get("trophies") if isinstance(data.get("trophies"), list) else None,
                       trophies_on=data.get("trophies_on") if isinstance(data.get("trophies_on"), list) else None,
                       fragments=data.get("fragments") if isinstance(data.get("fragments"), dict) else None)
        except (OSError, ValueError, AttributeError, TypeError):
            return cls()

    def save(self):
        storage.write_text(slot_file(getattr(self, "slot", 1)), json.dumps(
            {"gold": self.gold, "recruits": self.recruits, "stages_cleared": self.stages_cleared,
             "stage": self.stage, "fragments": self.fragments, "endless_best": self.endless_best,
             "trophies": self.trophies, "trophies_on": self.trophies_on, "altar": self.altar, "gear": self.gear,
             "acc_owned": self.acc_owned, "acc_frags": self.acc_frags, "dungeon_lv": self.dungeon_lv,
             "rift_lv": self.rift_lv, "unlocks": sorted(self.unlocks), "tips_seen": sorted(self.tips_seen),
             "greed": self.greed, "materials": self.materials, "craft_owned": self.craft_owned,
             "members": [m.to_dict() for m in self.members]}, ensure_ascii=False, indent=2))

    def recruit_cost(self):
        return RECRUIT_BASE_COST * 2 ** self.recruits

    def add_gold(self, amount):
        self.gold += amount
        self.save()

    @property
    def hero(self):
        return self.members[0]

    def active(self):
        return [m for m in self.members if m.active]

    def recruit(self):
        """Gasta gold e recruta um Novice. Retorna (membro, None) ou (None, mensagem de erro)."""
        if len(self.members) >= MAX_MEMBERS:
            return None, f"The party is full ({MAX_MEMBERS} members)."
        cost = self.recruit_cost()
        if self.gold < cost:
            return None, f"Not enough gold: recruiting costs {cost} (you have {self.gold})."
        self.gold -= cost
        self.recruits += 1
        used = {m.name for m in self.members}
        free = [n for n in NAMES if n not in used]
        name = random.choice(free) if free else f"Recruit {len(self.members) + 1}"
        m = Member(name)
        m.active = len(self.active()) < MAX_ACTIVE
        self.members.append(m)
        self.save()
        return m, None

    def toggle_active(self, m):
        """Retorna uma mensagem de erro, ou None se deu certo."""
        if m.hero:
            return "The hero is always in the party."
        if m.active:
            m.active = False
        elif len(self.active()) >= MAX_ACTIVE:
            return f"The party already has {MAX_ACTIVE} active members."
        else:
            m.active = True
        self.save()
        return None

    def dismiss(self, m):
        if m.hero:
            return "The hero can't be dismissed."
        self.members.remove(m)
        self.save()
        return None
