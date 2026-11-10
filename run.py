"""A partida: party em campo, inimigos, níveis da partida, tela de resultados e EXP meta."""
import heapq
import math
import random

import pygame

import pixel
from pygame.math import Vector2 as V

from data import REGEN5_PER_VIT
from data import role_of, TANK_THREAT, DEF_TO_DR
from data import (BASE_CHAR_DAMAGE, DMG_PER_ATTR, ARMOR_PER_STR, DODGE_PER_AGI, MRES_PER_INT, HP_PER_VIT, MAX_DODGE, CRIT_PER_AGI,
                  CRITDMG_PER_STR, CDR_PER_INT, BASE_CRIT_DMG, MAX_CRIT, MAX_CDR, soft_pct)
from data import (W, H, BG, GRID, WHITE, GREY, DARK, PANEL, RED, GREEN, BLUE, YELLOW, MAX_ENEMIES, STAGE_TIME, REVIVE_TIME, PARTY_SCALING,
                  ENEMY_TYPES, DIFFICULTIES, CLASSES, ELEMENTS, SKILL_UNLOCK, SKILL_MAX, MAX_RELICS, RELICS,
                  PASSIVES, element_color)
from icons import draw_class_icon, draw_class_hat, draw_dual_weapons
import elites as el
import monster_ai as mai
import powerups as pw
from scenery import Scenery
from dodge import DodgeState
from i18n import tr, L
import i18n
from tags import tag_list_text, phys_nature
from data import ELEMENT_STATUS, PHYS_STATUS
from class_passives import effects_text
from equipment import gear_totals
import skill_icons as si
import skill_fx as sfx
import greed as grd
import crafting as crf
import cats
from progression import ARCH_NAME, SPECIAL_NAME, TARGET_NAME
import progression as prog
import storage
from enemy_sprites import draw_enemy, flash_sprite, sprite as enemy_sprite
from data import STAGES, GOLD_STAGE_BASE, ENEMY_NAMES, ENEMY_FROM_STAGE, BIOMES, ROLE_FROM, stage_pos, roles_at
from data import is_endless, endless_biome, biome_of, ENDLESS_TIER_TIME, ENDLESS_BOSS_TIME
from skills import Skill, Fx, unit, Minion
import trophies as trophy
import accessories as accm
import dungeons as dgm
import training as trn
import rift

CELL = 64


# --------------------------------------------------------------------------
# Membro da party em campo
# --------------------------------------------------------------------------
def member_role(member):
    """Nome da role da classe atual do personagem (Tank, Caster...)."""
    return CLASSES[member.cls].get("class_role", "All-Rounder")


class Unit:
    def __init__(self, member, slot):
        self.member = member
        self.cls = CLASSES[member.cls]
        self.slot = slot
        self.is_hero = slot == 0
        self.color = self.cls["color"]
        self.r = 14 if self.is_hero else 12
        ang = slot * 2.1
        self.pos = V(0, 0) if self.is_hero else V(math.cos(ang), math.sin(ang)) * 60

        self.pas_specs = member.passive_specs()
        self.pas_lv = [1] * len(self.pas_specs)   # nível de cada passiva equipada na run (1..5)
        self.run_items = {}                         # itens da run (só o herói) para reaplicar após recalcular
        # acessórios equipados (anéis, bracelete, berloques): efeitos fixos + efeitos com chance (procs)
        self.accs = [(aid, accm.OWNED.get(aid, 0)) for aid in member.acc.values() if aid in accm.OWNED]
        self.acc_procs = [(aid, accm.ACC[aid]["proc"], accm.mult(lv)) for aid, lv in self.accs
                          if accm.ACC[aid]["proc"] and accm.ACC[aid]["cat"] != "emblem"]
        # emblemas: efeitos da party inteira (montados pela Run para todos os membros)
        self.emblem_procs = [(aid, accm.ACC[aid]["proc"], accm.mult(lv)) for aid, lv in self.accs
                             if accm.ACC[aid]["proc"] and accm.ACC[aid]["cat"] == "emblem"]
        self.party_eff = {}
        self.acc_icd = {}
        self.phoenix = any(p["act"] == "revive" for _a, p, _m in self.acc_procs)
        flags = {accm.ACC[aid]["flag"][0]: accm.ACC[aid]["flag"][1] * accm.mult(lv) for aid, lv in self.accs
                 if accm.ACC[aid].get("flag")}
        self.ricochet = flags.get("ricochet", 0) / 100   # colar do Archer
        self.imbue_bonus = flags.get("imbue", 0)         # colar do Spellblade
        self.imbue = None                                # (elemento, até quando)
        self._compute()
        # slot 1 = golpe básico; depois as ativas equipadas no loadout
        self.skills = [Skill(sp) for sp in member.active_specs()]
        self.skill_tags = {sk.name: tuple(sk.spec.get("tags", ())) for sk in self.skills}
        self.skill_bleed = {sk.name: sk.spec.get("bleed", 0) for sk in self.skills}
        self.skill_nature = {sk.name: phys_nature(sk.spec) for sk in self.skills}   # corte / perfuração / impacto
        # efeitos ao acertar que valem por qualquer caminho (projétil, área, nuvem...): Provocar e Enfraquecer
        self.skill_fx = {sk.name: (sk.spec.get("taunt", 0), sk.spec.get("weaken", 0)) for sk in self.skills
                         if sk.spec.get("taunt") or sk.spec.get("weaken")}
        self.frenzy = []      # instantes dos abates recentes (capstone Frenzy)
        self.run = None
        self.buffs = {}
        self.iframes = 0.0
        self.downed = False
        self.revive_t = 0.0   # contagem para ressuscitar (aliados)
        self.facing = V(1, 0)

    def _compute(self):
        """(Re)calcula todos os status a partir de passivas (com nível), equipamentos e atributos."""
        member = self.member
        # efeitos somados das passivas equipadas
        pas = {}
        for p, lv in zip(self.pas_specs, self.pas_lv):   # passivas: cada nível na run +50% do valor original
            mult = 1 + PASSIVE_LV_STEP * (lv - 1)
            for k, v in (p.get("effects") or {p["effect"]: p["value"]}).items():
                pas[k] = pas.get(k, 0) + v * mult
        self.passive_totals = dict(pas)            # só passivas (para os detalhes de status)
        self.gear_totals = gear_totals(member)     # arma e capacete da classe atual (melhorias)
        for k, v in crf.member_totals(member).items():   # roupa, calça e bota de materiais (ferreiro)
            self.gear_totals[k] = self.gear_totals.get(k, 0) + v
        for aid, lv in getattr(self, "accs", []):   # acessórios: somam junto com os equipamentos
            if accm.ACC[aid]["cat"] == "emblem":     # (os emblemas entram pela party_eff, para todos)
                continue
            for k, v in accm.effects(aid, lv).items():
                self.gear_totals[k] = self.gear_totals.get(k, 0) + v
        for k, v in getattr(self, "party_eff", {}).items():   # emblemas da party
            self.gear_totals[k] = self.gear_totals.get(k, 0) + v
        for k, v in self.gear_totals.items():
            pas[k] = pas.get(k, 0) + v
        self.greed_totals = grd.totals()           # Altar of Greed: bônus comprados com gold (toda a party)
        for k, v in self.greed_totals.items():
            pas[k] = pas.get(k, 0) + v
        g = lambda k: pas.get(k, 0)
        self.eff = pas   # todos os efeitos (passivas + equipamentos), inclusive os de tag/status/capstone

        st = member.stats()  # base + nível geral + bônus permanentes dos níveis de classe
        for k in ("str", "agi", "int", "vit"):
            st[k] += g(k)
            st[k] = int(round(st[k] * (1 + g(k + "_pct") / 100)))
        self.stats = st
        role = self.role = role_of(member.cls)   # scaling base da role (Vida, Defesa, Ataque, Velocidade)
        self.threat = TANK_THREAT if member_role(member) == "Tank" else 1.0
        self.max_hp = (60 + st["vit"] * HP_PER_VIT + st["hp"] + g("hp_flat")) * role["hp"] * (1 + g("hp_pct") / 100)
        self.hp = self.max_hp
        # redução % de todo dano: role (Defesa 1,3 = +15%; 0,7 = -15%, recebe mais dano) + passivas
        self.defense = (role["defense"] - 1) * DEF_TO_DR + g("defense") / 100
        self.armor = (st["str"] * ARMOR_PER_STR + st["armor"] + g("armor")) * (1 + g("armor_pct") / 100) * \
            role["defense"]  # físico
        self.mres = (st["int"] * MRES_PER_INT + st["mres"] + g("mres")) * (1 + g("mres_pct") / 100) * \
            role["defense"]  # mágico
        # chance crítica, esquiva e recarga: soma bruta com retorno decrescente (softcaps em 1/3 e 2/3 do máximo)
        self.dodge_raw = st["agi"] * DODGE_PER_AGI + st["dodge"] + g("dodge")
        self.dodge = soft_pct(self.dodge_raw, MAX_DODGE)  # % de anular dano físico
        self.base_speed = 200 * role["speed"] * (1 + g("speed") / 100)
        self.phys = 1 + (g("phys_dmg") + g("dmg")) / 100
        self.mag = 1 + (g("mag_dmg") + g("dmg")) / 100
        # crítico e cooldown: atributo + bônus dos níveis de classe + passivas
        self.crit_raw = st["agi"] * CRIT_PER_AGI + st["crit"] + g("crit")
        self.crit_chance = soft_pct(self.crit_raw, MAX_CRIT)
        self.crit_dmg = BASE_CRIT_DMG + st["str"] * CRITDMG_PER_STR + st["critdmg"] + g("critdmg")
        self.cdr_raw = st["int"] * CDR_PER_INT + st["cdr"] + g("cdr")
        self.cooldown = soft_pct(self.cdr_raw, MAX_CDR)
        self.haste = 1 - self.cooldown / 100
        self.area = 1 + g("area") / 100     # largura / tamanho / ângulo das habilidades
        self.range = 1 + g("range") / 100   # alcance corpo a corpo e distância dos projéteis
        self.heal_mult = 1 + g("heal") / 100
        self.dur_mult = 1 + g("duration") / 100
        # bônus de itens da partida (só o herói recebe)
        self.dmg_mult = 1.0
        self.cd_mult = 1.0
        self.speed_mult = 1.0
        # regeneração: hp a cada 5 s (VIT + níveis de classe + passivas); self.regen guarda o valor por segundo
        self.regen5 = st["vit"] * REGEN5_PER_VIT + st["regen5"] + g("regen5")
        self.regen = self.regen5 / 5
        self.magnet = 90 * (1 + g("magnet") / 100)
        self.dot_mult = 1 + g("dot_dmg") / 100

    def recompute(self):
        """Depois de melhorar uma passiva na run: recalcula mantendo a % de vida e os itens da run."""
        frac = self.hp / self.max_hp if self.max_hp else 1.0
        self._compute()
        for name, n in self.run_items.items():
            for _ in range(n):
                apply_passive(name, self)
        self.hp = self.max_hp * frac

    def buff(self, key):
        return sum(eff.get(key, 0) for eff, _ in self.buffs.values())

    def char_damage(self):
        """Dano do personagem: 10 + o atributo principal da classe atual (FOR, AGI ou INT; as classes
        equilibradas usam a média dos três). Todas as habilidades causam uma % disso."""
        st = self.stats
        attr = CLASSES[self.member.cls]["attr"]
        v = (st["str"] + st["agi"] + st["int"]) / 3 if attr == "bal" else st.get(attr, 0)
        return (BASE_CHAR_DAMAGE + v + self.buff("allattr")) * DMG_PER_ATTR * self.role["attack"]   # x Ataque da role

    def attr_damage(self, attr):
        """Dano extra de uma habilidade: +1 por ponto do atributo da classe dela (Equilibrado = média)."""
        if attr == "bal":
            v = (self.stats["str"] + self.stats["agi"] + self.stats["int"]) / 3
        else:
            v = self.stats.get(attr, 0)
        v += self.buff("allattr")   # emblema: +X em todos os atributos por alguns segundos
        return v * DMG_PER_ATTR

    def cap(self, name):
        """Valor de uma mecânica de capstone equipada (0 = não tem)."""
        return self.eff.get("cap:" + name, 0)

    def tag_bonus(self, prefix, tags):
        return sum(self.eff.get(f"{prefix}:{t}", 0) for t in tags)

    def power(self, dmgtype):
        base = self.phys if dmgtype == "phys" else self.mag
        anthem = self.run.anthem if self.run is not None else 0
        return base * self.dmg_mult * (1 + self.buff("dmg")) * (1 + anthem / 100)

    def haste_mult(self, tags=()):
        tag = min(50.0, self.tag_bonus("taghaste", tags)) / 100
        return self.haste * self.cd_mult * (1 - tag) / (1 + self.buff("haste"))

    def speed(self):
        slow = 0.7 if getattr(self, "slow_t", 0) > 0 else 1.0   # troféu Spider Queen Silk: lentidão de contato
        return self.base_speed * self.speed_mult * (1 + self.buff("speed")) * slow

    def hit(self, dmg, dmgtype="phys"):
        """Recebe dano. Retorna 'dodge', o dano sofrido, ou None (invulnerável)."""
        if self.iframes > 0 or self.downed:
            return None
        self.iframes = 0.5 if self.is_hero else 0.35
        if dmgtype == "phys" and random.random() * 100 < self.dodge:
            return "dodge"
        if self.buff("invuln"):
            return None
        aa = self.buff("allattr")   # atributos temporários (emblema): FOR -> armadura, INT -> defesa mágica
        dmg = max(1.0, dmg - (self.armor + aa * ARMOR_PER_STR if dmgtype == "phys" else self.mres + aa * MRES_PER_INT))
        bulwark = self.cap("bulwark") / 100 if self.hp < self.max_hp * 0.4 else 0
        dr = min(0.75, self.defense + self.buff("dr") + bulwark)
        dmg *= (1 - dr)
        self.hp -= dmg
        if self.hp <= 0 and self.phoenix:   # berloque Phoenix Feather: levanta uma vez por run
            self.phoenix = False
            self.hp = self.max_hp * 0.5
            self.iframes = 2.0
            if self.run is not None:
                self.run.fx_ring(self.pos, 90, (255, 150, 60))
                self.run.texts.append([self.pos + V(0, -self.r - 20), "Phoenix!", 1.5, (255, 170, 80)])
            return dmg
        if self.hp <= 0:
            self.hp = 0
            self.downed = True
            self.revive_t = REVIVE_TIME
        return dmg


def enemy_stats(kind, hp_scale, dmg_scale, res_mult):
    """Vida, dano, armadura e defesa mágica de um inimigo com os multiplicadores aplicados."""
    t = ENEMY_TYPES[kind]
    return (t["hp"] * hp_scale, t["dmg"] * dmg_scale, t.get("armor", 0) * res_mult, t.get("mres", 0) * res_mult)


class Enemy:
    def __init__(self, kind, pos, hp_scale, dmg_scale=1.0, res_mult=1.0):
        t = ENEMY_TYPES[kind]
        self.kind = kind
        self.boss = kind == "chefe"
        self.pos = V(pos)
        self.hp, self.dmg, self.armor, self.mres = enemy_stats(kind, hp_scale, dmg_scale, res_mult)
        self.max_hp = self.hp
        self.speed = t["speed"]
        self.r = t["r"]
        self.color = t["color"]
        self.xp = t["xp"]
        self.dmgtype = t.get("dmgtype", "phys")
        self.knock = V(0, 0)
        self.flash = 0.0
        self.slow_f = 1.0
        self.slow_t = 0.0
        self.stun_t = 0.0
        self.dots = []  # [dano por segundo, tempo restante, cor]
        self.elite = None   # id da classe quando é um inimigo de elite (ver elites.py)
        self.chill_t = 0.0  # gelo (status "chilled")
        self.last_src = None
        self.sprite = kind
        self.dummy = False   # boneco da Sala de Treino (não morre)
        self.taunt_t = 0.0   # provocado: ataca self.taunter até acabar
        self.taunter = None
        self.weak_t = 0.0    # Enfraquecido: recebe +weak_pct de dano
        self.weak_pct = 0.0
        self.anim = random.random() * 10   # defasagem da animação (bater de asas etc.)

    def update(self, dt, target):
        self.flash = max(0.0, self.flash - dt)
        self.stun_t = max(0.0, self.stun_t - dt)
        self.slow_t = max(0.0, self.slow_t - dt)
        self.taunt_t = max(0.0, self.taunt_t - dt)
        self.weak_t = max(0.0, self.weak_t - dt)
        if self.stun_t <= 0 and not getattr(self, "ai_hold", False):   # ai_hold: preparando um golpe
            spd = self.speed * (self.slow_f if self.slow_t > 0 else 1.0) * getattr(self, "ai_spd", 1.0)
            to = target - self.pos
            if to.length_squared() > 4:
                self.pos += unit(to) * spd * dt
        self.pos += self.knock * dt
        self.knock *= max(0.0, 1 - 8 * dt)
        self.chill_t = max(0.0, self.chill_t - dt)
        if self.dots:
            for d in self.dots:   # [dps, tempo, registro de dano da unidade (ou None), habilidade, tipo]
                if self.hp > 0 and d[2] is not None:
                    d[2][d[3]] = d[2].get(d[3], 0.0) + min(d[0] * dt, self.hp)
                self.hp -= d[0] * dt
                d[1] -= dt
            self.dots = [d for d in self.dots if d[1] > 0]

    def statuses(self):
        st = {d[4] for d in self.dots}
        out = set()
        if "burn" in st:
            out.add("burning")
        if "poison" in st:
            out.add("poisoned")
        if "bleed" in st:
            out.add("bleeding")
        if self.chill_t > 0:
            out.add("chilled")
        if self.stun_t > 0:
            out.add("stunned")
        if self.slow_t > 0:
            out.add("slowed")
        if self.weak_t > 0:
            out.add("weakened")
        if out:
            out.add("debuffed")
        if out & {"burning", "chilled", "poisoned", "stunned"}:
            out.add("elemental")
        return out


class Gem:
    def __init__(self, pos, value):
        self.pos = V(pos)
        self.value = value
        self.pulled = False

    @property
    def color(self):
        return RED if self.value >= 8 else GREEN if self.value >= 2 else BLUE


PASSIVE_LV_STEP = 0.5   # cada nível de passiva na run: +50% do valor original (Lv 5 = 300%)


def apply_passive(name, u):
    if name == "Feather Paws":
        u.speed_mult += 0.10
    elif name == "Ninth Life":
        u.max_hp += 20
        u.hp += 20
    elif name == "Long Whiskers":
        u.magnet *= 1.3
    elif name == "Catnip":
        u.dmg_mult += 0.12
    elif name == "Cat Nap":
        u.cd_mult *= 0.92
    elif name == "Warm Milk":
        u.regen += 0.5
    elif name == "Sharp Claws":
        u.range += 0.10
    elif name == "Ball of Yarn":
        u.area += 0.10


# --------------------------------------------------------------------------
# Partida
# --------------------------------------------------------------------------
class Run:
    def __init__(self, app, members, stage_index=0, dungeon=None, training=False):
        self.app = app
        self.dungeon = dungeon                    # (id, nível) nas masmorras do portal vermelho, senão None
        self.training = training                  # Sala de Treino (bonecos invencíveis, sem recompensas)
        self.meter_t0 = 0.0                       # início da contagem do medidor (Sala de Treino: zerar medidor)
        if dungeon:
            stage_index = 0
        if training:
            stage_index = trn.cfg(app)["stage"]
        self.stage_id = stage_index
        self.rift = stage_index == rift.RIFT_ID and not dungeon and not training   # Endless Rift
        self.endless = is_endless(stage_index) or self.rift
        if dungeon:   # masmorra: base da Floresta I, escalada pelo nível da masmorra
            did, dlv = dungeon
            self.biome = biome_of(0)
            self.stage = dict(STAGES[0], name=L(f"{dgm.name(did)} Lv {dlv}", f"{dgm.name(did, 'pt')} Nv {dlv}"),
                              dungeon=True)
        elif training:
            self.biome = biome_of(0)
            self.stage = dict(STAGES[stage_index], name="Training Room", training=True)
        elif self.rift:   # Endless Rift: dificuldade da fase mais alta concluída; cenário e chefões sorteados
            base = rift.base_stage(app.roster)
            self.biome = biome_of(base["index"])
            self.stage = dict(base, name="Endless Rift", endless=True, rift=True)
        elif self.endless:   # Endless: começa na dificuldade da fase I do bioma e não tem limite de tempo
            biome = endless_biome(stage_index)
            self.biome = biome
            self.stage = dict(STAGES[biome["stages"][0]], name=f"{biome['name']} Endless", endless=True)
        else:
            self.biome = biome_of(stage_index)
            self.stage = STAGES[stage_index]
        self.settings = app.settings
        self.fonts = app.fonts
        self.screen = app.screen
        self.party = [Unit(m, i) for i, m in enumerate(members)]
        self.dmg_log = {u: {} for u in self.party}    # medidor: unidade -> {habilidade: dano causado}
        self.taken_log = {u: {} for u in self.party}  # unidade -> {inimigo: dano recebido}
        self.heal_log = {u: {} for u in self.party}   # unidade (quem curou) -> {habilidade: cura efetiva}
        self.cc_log = {u: {} for u in self.party}     # unidade -> {tipo de controle: {habilidade: segundos}}
        for u in self.party:
            u.run = self
        self.anthem = 0.0                              # capstone Anthem: bônus de dano da party
        self.taken_kind = {}                          # nome do inimigo -> (tipo, cor) para o ícone
        self.rc_mode = 0
        self.rc_tabs = []
        self.hero = self.party[0]
        # emblemas: os bônus fixos valem para a party inteira; os efeitos com chance disparam com qualquer membro
        party_eff = {}
        self.party_procs = []
        for u in self.party:
            for aid, lv in u.accs:
                if accm.ACC[aid]["cat"] == "emblem":
                    for k, v in accm.effects(aid, lv).items():
                        party_eff[k] = party_eff.get(k, 0) + v
            self.party_procs += [(aid, p, m, u) for aid, p, m in u.emblem_procs]
        if party_eff:
            for u in self.party:
                u.party_eff = party_eff
                u.recompute()
        self.dodge = DodgeState(self.hero)   # esquiva manual (ESPAÇO), só do herói
        n = len(self.party)
        hp_mult, rate_mult = DIFFICULTIES[self.settings["difficulty"]]
        count_mult, party_hp = PARTY_SCALING.get(n, PARTY_SCALING[4])
        st = self.stage
        self.hp_mult = hp_mult * party_hp * st["hp"]       # dificuldade x party maior x fase
        self.dmg_mult = st["dmg"]                          # força dos inimigos na fase
        self.res_mult = st["res"]                          # resistência (armadura e defesa mágica)
        self.reward = st["reward"]                         # multiplicador de EXP e gold
        self.rate_mult = rate_mult * count_mult            # party maior => mais inimigos
        self.count_mult = count_mult
        # troféus ativos no altar: cada um = +1 nível de dificuldade global
        roster = app.roster
        self.trophies = [t for t in getattr(roster, "trophies_on", []) if t in trophy.TROPHIES]
        self.glevel = len(self.trophies)
        gm = trophy.global_mults(self.glevel)
        self.hp_mult *= gm["hp"]
        self.dmg_mult *= gm["dmg"]
        self.rate_mult *= gm["density"]
        self.exp_mult = gm["exp"]                          # nível global: +10% de EXP
        self.gold_mult = gm["gold"]                        # nível global: +10% de gold (fase e gold dropado)
        self.frag_mult = gm["frag"]                        # nível global: +10% de fragmentos
        if "tusk" in self.trophies:
            self.res_mult *= 1.10
        # troféu Corrupted Guardian Heart: a fase dura 5 minutos (a progressão anda 2x) e nascem 2x mais inimigos
        self.heart = "heart" in self.trophies and not (self.endless or self.dungeon or self.training)
        self.pace = 2.0 if self.heart else 1.0
        self.run_len = STAGE_TIME / self.pace              # duração real da fase (chefão aparece aqui)
        self.spawn_mult = 2 if self.heart else 1
        # troféus dos biomas novos: modificadores simples (bônus da party, inimigos, gold/EXP)
        self.enemy_speed = 1.0
        self.elite_mult = 1.0
        t_party = {}
        for tid in self.trophies:
            md = trophy.MODS.get(tid)
            if not md:
                continue
            for k, v in md.get("party", {}).items():
                t_party[k] = t_party.get(k, 0) + v
            em = md.get("enemy", {})
            self.hp_mult *= em.get("hp", 1.0)
            self.dmg_mult *= em.get("dmg", 1.0)
            self.rate_mult *= em.get("density", 1.0)
            self.enemy_speed *= em.get("speed", 1.0)
            self.elite_mult *= em.get("elite", 1.0)
            rm = md.get("run", {})
            self.gold_mult *= rm.get("gold", 1.0)
            self.exp_mult *= rm.get("exp", 1.0)
        if t_party:
            for u in self.party:
                merged = dict(u.party_eff)
                for k, v in t_party.items():
                    merged[k] = merged.get(k, 0) + v
                u.party_eff = merged
                u.recompute()
        self.trophies_got = []                             # troféus obtidos nesta run
        self.acc_got = []                                  # acessórios dropados nesta run [(id, novo?)]
        self.acc_pool = accm.pool_for(self.biome["stages"] if self.endless else [self.stage["index"]])
        if self.rift:   # Endless Rift: sem acessórios (por enquanto); fragmentos de acessório direto
            self.acc_pool = []
            self.rift_pool = rift.stage_pool(roster)
            self.rift_lv = max(1, min(roster.rift_lv, getattr(app, "rift_pick", None) or roster.rift_lv))
            rm = rift.mults(self.rift_lv)
            self.hp_mult *= rm["hp"]
            self.dmg_mult *= rm["dmg"]
            self.res_mult *= rm["res"]
            self.reward *= rm["reward"]
            self.rift_lv0 = self.rift_lv                   # nível em que a run começou
            self.rift_next = rift.LEVEL_TIME               # próxima pergunta (a cada 10 min)
            self.rift_shifted = True                       # cenário já trocou desde o último chefão
            self.dg_accfrags = {}
        if dungeon:   # nível da masmorra: inimigos mais fortes e recompensa maior; acessórios próprios
            dm = dgm.mults(dungeon[1])
            self.hp_mult *= dm["hp"]
            self.dmg_mult *= dm["dmg"]
            self.res_mult *= dm["res"]
            self.reward *= dm["reward"]
            self.acc_pool = list(dgm.DUNGEONS[dungeon[0]]["drops"])
            if dgm.DUNGEONS[dungeon[0]]["reward"] == "frag":   # Catacumba: fragmentos de classe em dobro
                self.frag_mult *= 2
            self.dg_encounters = dgm.encounters()          # posições x dos encontros que faltam
            self.dg_total = len(self.dg_encounters)
            self.dg_boss_spawned = False
            self.dg_accfrags = {}                          # fragmentos de acessório ganhos (Dungeon)
        self.base_mults = (self.hp_mult, self.dmg_mult, self.res_mult, self.reward)
        self.tier = 0                                      # Endless: degrau de dificuldade (sobe a cada 2 min)
        self.next_boss = ENDLESS_BOSS_TIME                 # Endless: próximo chefão
        self.boss_count = 0
        self.boss = None                                   # chefão (aparece aos 10:00)
        self.boss_summon_t = 12.0
        self.max_enemies = int(MAX_ENEMIES * (0.45 + 0.55 * (count_mult - 1) / 1.8))  # 1 membro ~200, 4 = 450
        self.max_enemies = min(int(MAX_ENEMIES * 1.3), int(self.max_enemies * gm["density"]))
        if storage.IS_WEB:   # navegador/celular: Python mais lento, menos inimigos ao mesmo tempo na tela
            self.max_enemies = int(self.max_enemies * 0.6)
        if self.heart:       # mais espaço para o dobro de inimigos
            self.max_enemies = int(self.max_enemies * 1.5)
        self.enemies, self.projectiles, self.gems, self.texts = [], [], [], []
        self.fx, self.pending, self.clouds, self.minions = [], [], [], []
        self.grid = {}
        self.passives = {}
        self.relics = 0
        self.auto_pick = None      # escolha automática quando não há mais melhorias (vale só nesta run)
        self.auto_arm = False      # caixa "escolher automaticamente" marcada na tela de level up
        self.rand_arm = False      # caixa "próximos level ups aleatórios" marcada na tela de level up
        self.auto_random = False   # level ups escolhidos ao acaso até o fim da run (não vale para cura/gold/power-up)
        self.time = 0.0
        self.kills = 0
        self.elite_kills = 0
        self.hostile_shots, self.hostile_zones, self.frag_drops = [], [], []
        self.hostile_lines = []   # avisos de investida dos monstros: [início, fim, largura, tempo, total]
        self.frags_run = {}                                # fragmentos de classe obtidos nesta run
        self.gold_run = 0                                  # gold de moedas dropadas nesta run (já somado à conta)
        self.mats_run = {}                                 # materiais dos monstros obtidos nesta run (crafting.py)
        self.announces = []                                # avisos "An elite ... has appeared!" [cid, inimigo, tempo]
        self.powerups = []                                 # power-ups no chão
        self.W, self.H, self.Fx = W, H, Fx
        self.elite_pool = el.class_pool(app.roster)        # classes já liberadas por qualquer personagem
        self.next_event = el.EVENT_INTERVAL                # próximo Super Elite / Esquadrão de Elite
        self.scenery = (dgm.DungeonScenery(dungeon[0]) if dungeon      # corredor da masmorra
                        else trn.TrainingScenery() if training           # campo cercado da Sala de Treino
                        else Scenery(self.stage["index"]))   # chão de grama, mato e árvores (obstáculos)
        if self.rift:
            self.rift_scen = random.choice(self.rift_pool)
            self.scenery = Scenery(self.rift_scen)
        self.level = 1
        self.xp = 0
        self.xp_total = 0           # EXP coletada na partida => vira EXP meta no final
        self.xp_next = 5
        self.spawn_t = 0.0
        self.next_horde = 60.0
        self.pending_lv = 0
        self.options = []
        self.state = "play"         # play, pause, levelup, over
        self.result = None
        self.num_cache = {}
        self.overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 175))
        if training:
            self.hero.pos = V(-200, 0)
            for i, u in enumerate(self.party[1:]):
                u.pos = self.hero.pos + V(-40 - 30 * (i % 2), (i - 1.5) * 40)
            trn.setup(self)

    # ---------- consultas espaciais ----------
    def build_grid(self):
        g = {}
        for e in self.enemies:
            g.setdefault((int(e.pos.x // CELL), int(e.pos.y // CELL)), []).append(e)
        self.grid = g

    def enemies_near(self, pos, r):
        out = []
        x0, x1 = int((pos.x - r - 24) // CELL), int((pos.x + r + 24) // CELL)
        y0, y1 = int((pos.y - r - 24) // CELL), int((pos.y + r + 24) // CELL)
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                for e in self.grid.get((cx, cy), ()):
                    if e.hp > 0 and (e.pos - pos).length_squared() < (r + e.r) ** 2:
                        out.append(e)
        return out

    def nearest_enemy(self, pos, max_dist=None):
        best, bd = None, (max_dist * max_dist) if max_dist else float("inf")
        if max_dist and max_dist < 400:
            pool = self.enemies_near(pos, max_dist)
        else:
            pool = self.enemies
        for e in pool:
            if e.hp <= 0:
                continue
            d = (e.pos - pos).length_squared()
            if d < bd:
                best, bd = e, d
        return best

    def nearest_enemies(self, pos, n, max_dist):
        pool = [e for e in self.enemies if e.hp > 0 and (e.pos - pos).length_squared() < max_dist ** 2]
        return heapq.nsmallest(n, pool, key=lambda e: (e.pos - pos).length_squared())

    def random_visible_enemies(self, n):
        hp = self.hero.pos
        vis = [e for e in self.enemies if e.hp > 0 and abs(e.pos.x - hp.x) < W / 2 and abs(e.pos.y - hp.y) < H / 2]
        return random.sample(vis, min(n, len(vis)))

    # ---------- combate ----------
    def damage(self, e, dmg, direction, element=None, slow=None, stun=None, knock=100, show=True, pull=0,
               dmgtype="phys", src=None, sk=None):
        if e.hp <= 0:
            return
        tags = src.skill_tags.get(sk, ()) if src is not None else ()
        sts = e.statuses() if src is not None else set()
        crit = False
        imbued = None
        if src is not None:
            e.last_src = src
            bonus = src.tag_bonus("tagdmg", tags) + src.tag_bonus("dmgvs", sts)
            if e.hp < e.max_hp * 0.3:
                bonus += src.cap("execute")
            if e.hp >= e.max_hp:
                bonus += src.cap("ambush")
            if src.hp < src.max_hp * 0.4:
                bonus += src.cap("lowhp")
            if src.cap("rage"):   # colar do Marauder: mais dano quanto menos vida
                bonus += src.cap("rage") * (1 - src.hp / max(1.0, src.max_hp))
            imb = src.imbue
            if src.imbue_bonus and element in ELEMENTS:
                src.imbue = (element, self.time + 4.0)   # colar do Spellblade: guarda o último elemento
            elif imb and imb[1] > self.time and element not in ELEMENTS and dmgtype == "phys":
                bonus += src.imbue_bonus
                imbued = imb[0]
            if "elemental" in sts:
                bonus += src.cap("elemental")
            if src.frenzy:
                src.frenzy = [t for t in src.frenzy if self.time - t < 4.0][-10:]
                bonus += src.cap("frenzy") * len(src.frenzy)
            dmg *= 1 + bonus / 100
            aa = src.buff("allattr")   # atributos temporários (emblema): AGI -> crítico, FOR -> dano crítico
            cc = soft_pct(getattr(src, "crit_raw", src.crit_chance) + src.buff("crit") + src.tag_bonus("tagcrit", tags)
                          + src.tag_bonus("critvs", sts) + aa * CRIT_PER_AGI, MAX_CRIT)
            crit = random.random() * 100 < cc
            if crit:
                dmg *= 1 + (src.crit_dmg + src.buff("critdmg") + aa * CRITDMG_PER_STR) / 100
        if e.weak_t > 0:   # Enfraquecido: recebe mais dano
            dmg *= 1 + e.weak_pct / 100
        if src is not None and sk in src.skill_fx:
            taunt, weaken = src.skill_fx[sk]
            if taunt and not e.dummy:
                t = taunt * (0.5 if (e.boss or getattr(e, "boss_classes", None)) else 1.0)   # chefões: metade
                if e.taunter is not src or e.taunt_t < t:
                    self.log_cc(src, "Taunt", sk, max(0.0, t - (e.taunt_t if e.taunter is src else 0.0)))
                e.taunt_t, e.taunter = t, src
            if weaken:
                if e.weak_t <= 0 or weaken >= e.weak_pct:
                    e.weak_pct = weaken
                    if e.weak_t <= 0:
                        self.log_cc(src, "Weaken", sk, 4.0)
                    e.weak_t = 4.0
        # armadura reduz dano físico; defesa mágica reduz dano mágico ou elemental (mínimo 1)
        magical = dmgtype == "mag" or element in ELEMENTS
        dmg = max(1.0, dmg - (e.mres if magical else e.armor))
        log = self.dmg_log.setdefault(src, {}) if src is not None else None
        if log is not None:   # medidor de dano: só o dano efetivo (sem o excedente da morte)
            key = sk or "Other"
            log[key] = log.get(key, 0.0) + (dmg if e.dummy else min(dmg, e.hp))
        e.hp -= dmg
        if e.dummy and e.hp <= 0:   # boneco de treino: nunca morre (o medidor conta o dano inteiro)
            e.hp = e.max_hp
        e.flash = 0.1
        if crit and src is not None and src.cap("vampiric") and not src.downed:
            self.heal(src, dmg * src.cap("vampiric") / 100, src=src, sk="Vampiric", fx=False)
        el = ELEMENTS.get(element, {})
        knock += el.get("knock", 0)
        if knock and direction.length_squared() > 0:
            e.knock += direction.normalize() * knock * (12 / e.r)
            if knock >= 150:
                self.log_cc(src, "Knockback", sk, 0.3)
        # chance de status: pelo elemento do golpe ou, em golpes físicos, pelo tipo (corte/perfuração/impacto)
        rule = ELEMENT_STATUS.get(element)
        if rule is None and imbued:   # golpe físico imbuído: chance do status do elemento
            rule = ELEMENT_STATUS.get(imbued)
        if rule is None and not magical and src is not None and src.skill_nature.get(sk):
            rule = PHYS_STATUS[src.skill_nature[sk]]
        dot = None
        if rule and random.random() < rule["chance"]:
            if rule.get("stun"):
                stun = max(stun or 0, rule["stun"])
            if rule.get("slow") and not slow:
                slow = rule["slow"]
            dot = rule.get("dot")
        stun = stun or 0
        if stun:
            old = e.stun_t
            e.stun_t = max(e.stun_t, stun * (12 / e.r if e.r > 15 else 1))
            kind = "Freeze" if element == "ice" else "Knockdown" if element == "earth" else "Stun"
            self.log_cc(src, kind, sk, e.stun_t - old)
        slow = slow or None
        if slow:
            old = e.slow_t
            e.slow_f = min(e.slow_f if e.slow_t > 0 else 1.0, slow[0])
            e.slow_t = max(e.slow_t, slow[1])
            if element == "ice":
                e.chill_t = max(e.chill_t, slow[1])
            self.log_cc(src, "Chill" if element == "ice" else "Slow", sk, e.slow_t - old)
        dm = src.dot_mult if src is not None else 1.0
        tag = [log, sk or "Other"] if log is not None else [None, None]
        if dot:
            e.dots.append([dmg * dot[1] * dm, dot[2]] + tag + [dot[0]])
        bleed = src.skill_bleed.get(sk, 0) if src is not None else 0
        if bleed and not magical:
            e.dots.append([dmg * bleed * dm, 3.0] + tag + ["bleed"])
        if src is not None and (src.acc_procs or self.party_procs) and not self._in_proc:   # acessórios com efeito ao acertar
            applied = set()
            if dot:
                applied.add({"burn": "burning", "poison": "poisoned", "bleed": "bleeding"}.get(dot[0], dot[0]))
            if bleed and not magical:
                applied.add("bleeding")
            if stun:
                applied.add("stunned")
            if slow:
                applied.add("chilled" if element == "ice" else "slowed")
            kinds = set(tags) | {element, src.skill_nature.get(sk), "magical" if magical else "physical"}
            self._last_el = element if element in ELEMENTS else None
            self.acc_hit(src, e, dmg, crit, element, kinds, applied)
        if show and self.settings["damage_numbers"] and len(self.texts) < 100:
            if crit:
                self.texts.append([e.pos + V(random.uniform(-6, 6), -e.r - 6), f"{int(round(dmg))}!", 0.75,
                                   (255, 200, 60)])
            else:
                self.texts.append([e.pos + V(random.uniform(-6, 6), -e.r), str(int(round(dmg))), 0.6,
                                   element_color(element)])

    # ---------- acessórios: efeitos com chance ----------
    _in_proc = False
    _last_el = None

    def acc_ready(self, u, aid, p):
        icd = p.get("icd", 0)
        if icd and self.time < u.acc_icd.get(aid, -99):
            return False
        if random.random() >= p["chance"]:
            return False
        if icd:
            u.acc_icd[aid] = self.time + icd
        return True

    def acc_hit(self, u, e, dmg, crit, element, kinds, applied):
        procs = [(aid, p, m, u) for aid, p, m in u.acc_procs]
        if u in self.party:   # emblemas: os golpes de qualquer membro contam
            procs += self.party_procs
        for aid, p, m, owner in procs:
            on = p["on"]
            if on == "status":
                if not applied.intersection(p["st"]):
                    continue
            elif on == "crit":
                if not crit:
                    continue
            elif on == "hit":
                if p.get("tags") and not kinds.intersection(p["tags"]):
                    continue
                if not p.get("tags") and not p.get("any_hit", True):
                    continue
            else:
                continue
            if self.acc_ready(owner, aid, p):
                self.acc_act(owner, aid, p, m, e, dmg)

    def acc_kill(self, u, e):
        sts = e.statuses()
        procs = [(aid, p, m, u) for aid, p, m in u.acc_procs]
        if u in self.party:
            procs += self.party_procs
        for aid, p, m, owner in procs:
            if p["on"] != "kill":
                continue
            if p.get("st") and not sts.intersection(p["st"]):
                continue
            if p.get("elite") and not (e.elite or e.boss):
                continue
            if self.acc_ready(owner, aid, p):
                self.acc_act(owner, aid, p, m, e, e.max_hp)

    def acc_hurt(self, u, dmg):
        for aid, p, m in u.acc_procs:
            if p["on"] == "hurt" and self.acc_ready(u, aid, p):
                self.acc_act(u, aid, p, m, None, dmg)

    def acc_dodge(self, u):
        for aid, p, m in u.acc_procs:
            if p["on"] == "dodge" and self.acc_ready(u, aid, p):
                self.acc_act(u, aid, p, m, None, 0)

    def acc_act(self, u, aid, p, m, e, dmg):
        act = p["act"]
        sk = accm.name(aid)
        el = p.get("el")
        dtype = "mag" if el else "phys"
        self._in_proc = True
        try:
            if act == "nova":
                self.explode(e.pos, p["r"], dmg * p["v"] * m / 100, el, stun=p.get("stun"), knock=p.get("knock", 100),
                             dmgtype=dtype, src=u, sk=sk)
                if el == "fire":
                    self.fx.append(Fx("bolt", e.pos, 0.2, color=(255, 140, 60)))
            elif act == "nova_rand":   # colar do Thaumaturge: feitiço extra de elemento aleatório
                el = random.choice(("fire", "ice", "lightning"))
                self.explode(e.pos, p["r"], dmg * p["v"] * m / 100, el, dmgtype="mag", src=u, sk=sk)
            elif act == "nova_same":   # mesmo elemento do golpe (ou físico)
                el = self._last_el
                self.explode(e.pos, p["r"], dmg * p["v"] * m / 100, el, dmgtype="mag" if el else "phys", src=u,
                             sk=sk)
            elif act == "retaliate":   # colar do Gladiator: revida nos inimigos próximos
                self.explode(u.pos, p["r"], dmg * p["v"] * m / 100, None, knock=200, dmgtype="phys", src=u, sk=sk)
            elif act == "summon":   # invocação temporária (tipo do golpe, se el == "hit")
                el = self._last_el if p.get("el") == "hit" else p.get("el")
                base = dmg if not p.get("fixed") else u.power("phys") * 12
                mn = Minion(u.pos + V(random.uniform(-30, 30), random.uniform(-30, 30)), base * p["v"] * m / 100,
                            p["t"], 300, 9, element_color(el) if el else (200, 200, 210), el)
                mn.dmgtype = "mag" if el else "phys"
                mn.src, mn.sk = u, sk
                self.minions.append(mn)
                self.fx_ring(mn.pos, 26, element_color(el) if el else (200, 200, 210))
            elif act == "party_stack":   # emblemas: bônus da party que acumula
                step, top = p["step"] * m, p["max"] * m
                if p["key"] in accm.BUFF_FRAC:
                    step, top = step / 100, top / 100
                for v in self.party:
                    if not v.downed:
                        cur = v.buffs.get(sk, [{}, 0])[0].get(p["key"], 0)
                        v.buffs[sk] = [{p["key"]: min(top, cur + step)}, p["t"]]
            elif act == "stack":   # colar do Pugilist: combo que acumula
                cur = u.buffs.get(sk, [{}, 0])[0].get(p["key"], 0)
                step, top = p["step"] * m / 100, p["max"] * m / 100
                u.buffs[sk] = [{p["key"]: min(top, cur + step)}, p["t"]]
            elif act == "poison":
                log = self.dmg_log.setdefault(u, {})
                e.dots.append([dmg * p["v"] * m / 100 * u.dot_mult, 4.0, log, sk, "poison"])
            elif act == "party_heal":
                for v in self.party:
                    if not v.downed:
                        self.heal(v, v.max_hp * p["v"] * m / 100, src=u, sk=sk, fx=False)
                self.fx_ring(u.pos, 120, (120, 255, 160))
            elif act == "leech":
                self.heal(u, dmg * p["v"] * m / 100, src=u, sk=sk, fx=False)
            elif act == "nova_kill":
                self.explode(e.pos, p["r"], e.max_hp * p["v"] * m / 100, el, knock=150, dmgtype=dtype, src=u, sk=sk)
            elif act == "chain":
                hit = {id(e)}
                cur = e.pos
                for _ in range(p.get("n", 1)):
                    near = [x for x in self.enemies_near(cur, 240) if id(x) not in hit and x.hp > 0]
                    if not near:
                        break
                    t = min(near, key=lambda x: (x.pos - cur).length_squared())
                    hit.add(id(t))
                    self.fx.append(Fx("line", cur, 0.18, end=V(t.pos), width=4, color=element_color(el)))
                    self.damage(t, dmg * p["v"] * m / 100, t.pos - cur, el, knock=0, dmgtype=dtype, src=u, sk=sk)
                    cur = t.pos
            elif act == "buff":
                self.acc_buff(u, sk, p, m)
            elif act == "party_buff":
                for v in self.party:
                    if not v.downed:
                        self.acc_buff(v, sk, p, m)
            elif act == "heal":
                self.heal(u, u.max_hp * p["v"] * m / 100, src=u, sk=sk, fx=False)
            elif act == "cdr":
                for s_ in u.skills:
                    s_.t = max(0.0, s_.t - p["v"] * m)
        finally:
            self._in_proc = False

    def acc_buff(self, u, sk, p, m):
        eff = {k: (v * m / 100 if k in accm.BUFF_FRAC else v * m) for k, v in p["buff"].items()}
        u.buffs[sk] = [eff, p["t"]]

    def acc_drop(self, e):
        """Chance de um inimigo forte soltar um acessório da fase (o Endless usa os do bioma todo)."""
        if not self.acc_pool:
            return
        kind = "boss" if e.boss else getattr(e, "tier", "normal") if e.elite else None
        chance = accm.DROP_CHANCE.get(kind, 0) if kind else 0
        if kind == "normal":   # party maior tem mais elites comuns: mantém a média por run
            chance /= self.count_mult
        if kind is None or random.random() >= chance:
            return
        aid = random.choice(self.acc_pool)
        new = self.app.roster.acc_gain(aid)
        self.acc_got.append((aid, new))
        self.announces.append([aid, accm.name(aid, i18n.LANG), self.ANNOUNCE_TIME + 2.0, "acc" if new else "accdup"])
        self.fx.append(Fx("ring", e.pos, 1.0, radius=160, color=(120, 220, 230), grow=True))

    def explode(self, pos, r, dmg, element, slow=None, stun=None, knock=100, pull=0, dmgtype="mag", src=None,
                sk=None, look=None):
        for e in self.enemies_near(pos, r):
            if pull:
                e.knock += unit(pos - e.pos) * pull * 0.5
                self.log_cc(src, "Pull", sk, 0.5)
                self.damage(e, dmg, V(0, 0), element, slow, stun, 0, dmgtype=dmgtype, src=src, sk=sk)
            else:
                self.damage(e, dmg, e.pos - pos, element, slow, stun, knock, dmgtype=dmgtype, src=src, sk=sk)
        # animação do impacto no tamanho exato da área (visual da habilidade ou do elemento)
        lk = look if look is not None else dict(impact=sfx._EL_IMPACT.get(element, "hit"), el=element)
        self.fx.append(Fx("anim", pos, 0.42 if lk.get("impact") == "meteor" else 0.34,
                          frames=sfx.impact(lk, r, element if element else lk.get("el"))))

    def log_cc(self, src, kind, sk, secs):
        """Medidor: controle de grupo causado (segundos efetivamente adicionados), por tipo e habilidade."""
        if src is None or secs <= 0:
            return
        log = self.cc_log.setdefault(src, {}).setdefault(kind, {})
        key = sk or "Other"
        log[key] = log.get(key, 0.0) + secs

    def heal(self, u, amount, src=None, sk=None, fx=True):
        before = u.hp
        u.hp = min(u.max_hp, u.hp + amount)
        if src is not None and src.cap("sanctuary") and sk not in ("Vampiric", "Regeneration"):
            u.buffs["Sanctuary"] = [{"dr": src.cap("sanctuary") / 100}, 4.0]
        if not fx:
            if src is not None and u.hp > before:
                log = self.heal_log.setdefault(src, {})
                log[sk or "Other"] = log.get(sk or "Other", 0.0) + (u.hp - before)
            return
        if src is not None and u.hp > before:   # medidor: só a cura efetiva (sem o excedente)
            log = self.heal_log.setdefault(src, {})
            log[sk or "Other"] = log.get(sk or "Other", 0.0) + (u.hp - before)
        self.fx.append(Fx("anim", u.pos, 0.6, frames=sfx.heal_anim()))
        if self.settings["damage_numbers"] and u.hp > before:
            self.texts.append([u.pos + V(0, -u.r - 6), f"+{int(u.hp - before)}", 0.8, GREEN])

    # ---------- geração de inimigos ----------
    def ring_point(self):
        a = random.uniform(0, math.tau)
        d = math.hypot(W, H) / 2 + random.uniform(30, 120)
        return self.hero.pos + V(math.cos(a), math.sin(a)) * d

    def clock(self):
        """Tempo mostrado na tela: trava em 10:00 quando o chefão aparece (no Endless e nas masmorras não trava)."""
        return self.time if self.endless or self.dungeon or self.training else min(self.time, self.run_len)

    def prog_time(self):
        """Tempo de progressão da fase (spawns, hordas, eventos): com o troféu Heart anda 2x (5 min = 10:00)."""
        return self.clock() * self.pace

    def scale_time(self):
        """Tempo usado no crescimento dos inimigos ao longo da run (até 10:00; no Endless o resto vem dos degraus)."""
        if self.dungeon:
            return dgm.SCALE_TIME
        if self.training:   # Sala de Treino: o minuto escolhido no painel
            return trn.cfg(self.app)["minute"] * 60
        return min(self.time * self.pace, STAGE_TIME)

    def stage_level(self):
        """Posição equivalente da fase no bioma (0 = fase I ... 4 = fase V; Endless: fase I + degraus) — define
        quais inimigos aparecem (o bioma define quem faz cada papel)."""
        if self.rift:   # mesma ordem do Endless, a partir da posição da fase mais alta concluída
            return min(4, stage_pos(self.stage["index"]) + self.tier)
        if self.endless:
            return min(4, self.tier)
        return stage_pos(self.stage["index"])

    def role_kind(self, role):
        """Inimigo que faz o papel (swarm, mid, heavy, new3, new5). Endless Rift: de qualquer bioma liberado."""
        if self.rift:
            opts = [b["enemies"][role] for b in BIOMES if b["stages"] and any(
                i in self.rift_pool and b["stages"].index(i) >= ROLE_FROM.get(role, (0, 0))[0] for i in b["stages"])]
            if opts:
                return random.choice(opts)
        return self.biome["enemies"][role]

    def update_endless(self):
        """Endless: a cada 2 minutos a dificuldade sobe (vida, força, resistência) e a EXP/gold também."""
        tier = int(self.time // ENDLESS_TIER_TIME)
        if tier == self.tier:
            return
        self.tier = tier
        hp0, dmg0, res0, rew0 = self.base_mults
        st = self.stage
        self.hp_mult = hp0 * (st["hp"] + 0.5 * tier) / st["hp"]
        self.dmg_mult = dmg0 * (st["dmg"] + 0.3 * tier) / st["dmg"]
        self.res_mult = res0 * (st["res"] + 0.5 * tier) / st["res"]
        self.reward = rew0 * (st["reward"] + 0.25 * tier) / st["reward"]
        self.texts.append([self.hero.pos + V(0, -60), L(f"Difficulty up! Tier {tier + 1}",
                                                         f"A dificuldade subiu! Dificuldade {tier + 1}"), 2.5, RED])
        self.fx.append(Fx("ring", self.hero.pos, 1.0, radius=300, color=RED, grow=True))

    # ---------- Endless Rift ----------
    def rift_shift(self):
        """Troca o cenário por outro sorteado entre as fases liberadas."""
        self.rift_shifted = True
        opts = [i for i in self.rift_pool if i != self.rift_scen] or self.rift_pool
        self.rift_scen = random.choice(opts)
        self.scenery = Scenery(self.rift_scen)
        for u in self.party:
            self.scenery.collide(u)
        self.fx.append(Fx("ring", self.hero.pos, 1.2, radius=420, color=rift.COLOR, grow=True))
        nm = tr(STAGES[self.rift_scen]["name"])
        self.texts.append([self.hero.pos + V(0, -70), L(f"The rift shifts: {nm}", f"A fenda muda: {nm}"), 2.5,
                           rift.COLOR])

    def rift_frag(self, e):
        """Elites e chefões da fenda: fragmentos de acessório direto (no lugar dos acessórios)."""
        kind = "boss" if e.boss else getattr(e, "tier", "normal")
        chance = rift.FRAG_CHANCE.get(kind, 0)
        if kind == "normal":
            chance /= self.count_mult
        if random.random() < chance:
            self.gain_accfrag(e.pos)

    def rift_check(self):
        """A cada 10 minutos: o nível conta como concluído (libera o próximo) e o jogo pergunta se sobe."""
        if self.time < self.rift_next:
            return
        self.rift_next += rift.LEVEL_TIME
        roster = self.app.roster
        if self.rift_lv + 1 > roster.rift_lv:
            roster.rift_lv = self.rift_lv + 1
            roster.save()
        self.rift_ask = True   # a pergunta abre no fim do quadro (antes de um level up pendente)

    def rift_set_level(self, lv):
        """Muda o nível da fenda no meio da run (o tempo e o degrau continuam)."""
        old, new = rift.mults(self.rift_lv), rift.mults(lv)
        hp0, dmg0, res0, rew0 = self.base_mults
        self.base_mults = (hp0 * new["hp"] / old["hp"], dmg0 * new["dmg"] / old["dmg"],
                           res0 * new["res"] / old["res"], rew0 * new["reward"] / old["reward"])
        self.rift_lv = lv
        self.app.rift_pick = lv
        tier, self.tier = self.tier, -1
        self.update_endless()
        self.texts = [t for t in self.texts if "Tier" not in t[1] and "Dificuldade" not in t[1]]
        self.texts.append([self.hero.pos + V(0, -60), L(f"Rift Lv {lv}!", f"Fenda Nv {lv}!"), 2.5, rift.COLOR])

    def riftq_rects(self):
        return (pygame.Rect(W / 2 - 330, H / 2 + 40, 310, 56), pygame.Rect(W / 2 + 20, H / 2 + 40, 310, 56))

    def riftq_answer(self, up):
        if up:
            self.rift_set_level(self.rift_lv + 1)
        self.state = "play"

    def draw_riftq(self):
        s = self.screen
        s.blit(self.overlay, (0, 0))
        mins = int(self.time // 60)
        self.text(L(f"{mins} MINUTES SURVIVED!", f"{mins} MINUTOS SOBREVIVIDOS!"), "big", rift.COLOR,
                  (W / 2, H / 2 - 110), "center")
        self.text(L(f"Rift Lv {self.rift_lv} cleared: Lv {self.rift_lv + 1} is unlocked.",
                    f"Fenda Nv {self.rift_lv} concluída: o Nv {self.rift_lv + 1} está liberado."), "normal", GREEN,
                  (W / 2, H / 2 - 50), "center")
        nm = rift.mults(self.rift_lv + 1)
        self.text(L(f"Next level: enemy HP x{nm['hp']:.2f} · strength x{nm['dmg']:.2f} · rewards x{nm['reward']:.2f}"
                    "  (the timer and the tier keep going)",
                    f"Próximo nível: vida x{nm['hp']:.2f} · força x{nm['dmg']:.2f} · recompensas x{nm['reward']:.2f}"
                    "  (o tempo e o degrau continuam)"), "small", GREY, (W / 2, H / 2 - 16), "center")
        mouse = self.app.mouse_pos()
        labels = (L(f"[1] Stay at Lv {self.rift_lv}", f"[1] Ficar no Nv {self.rift_lv}"),
                  L(f"[2] Go to Lv {self.rift_lv + 1}", f"[2] Ir para o Nv {self.rift_lv + 1}"))
        for r, lab, col in zip(self.riftq_rects(), labels, (WHITE, rift.COLOR)):
            hot = r.collidepoint(mouse)
            pygame.draw.rect(s, (60, 60, 85) if hot else DARK, r, border_radius=12)
            pygame.draw.rect(s, col, r, 3 if hot else 2, border_radius=12)
            self.text(lab, "normal", col, r.center, "center")

    def new_enemy(self, kind, pos, allow_elite=True):
        ts = 1 + self.scale_time() / 90  # inimigos ficam mais fortes com o tempo (até os 10:00)
        e = Enemy(kind, pos, ts * self.hp_mult, (0.5 + 0.5 * ts) * self.dmg_mult, self.res_mult)
        e.speed *= self.enemy_speed
        if (allow_elite and kind != "chefe" and self.elite_pool
                and random.random() < el.ELITE_CHANCE * self.elite_mult
                and sum(1 for x in self.enemies if x.elite) < el.MAX_ELITES):
            el.make_elite(e, el.pick_class(self.elite_pool, {u.member.cls for u in self.party}))
            self.fx_ring(e.pos, e.r + 30, CLASSES[e.elite]["color"])
            self.announces.append([e.elite, ENEMY_NAMES.get(kind, kind), self.ANNOUNCE_TIME, None])
        return e

    def has(self, tid):
        return tid in self.trophies

    def drop_frag(self, pos, cid, spread):
        """Solta um fragmento (o valor dele é calculado ao coletar)."""
        off = V(random.uniform(-1, 1), random.uniform(-1, 1)) * spread
        self.frag_drops.append(el.FragmentDrop(pos + off, cid))

    def scale_gold(self, amount):
        """Gold dropado x bônus do nível global (a fração vira +1 com a chance correspondente)."""
        v = amount * self.gold_mult
        n = int(v)
        return n + (1 if random.random() < v - n else 0)

    def drop_materials(self, e):
        """Material do monstro derrotado (vai direto para a conta, fica mesmo se a run acabar em morte)."""
        got = crf.drop_for(e, self)
        if not got:
            return
        roster = self.app.roster
        for mid, q in got:
            roster.materials[mid] = roster.materials.get(mid, 0) + q
            self.mats_run[mid] = self.mats_run.get(mid, 0) + q
            if self.settings["damage_numbers"]:
                col = crf.MAT[mid]["color"]
                col = tuple(min(255, int(c * 0.6 + 110)) for c in col)
                self.texts.append([e.pos + V(0, -e.r - 22), f"+{q} {crf.mat_name(mid, i18n.LANG)}", 1.1, col])

    def collect_frag(self, cid):
        """Um fragmento chegou ao herói: vale 1 x (1 + 2,5% por nível do Altar of Mastery)
        x (1 + 10% por nível de dificuldade global dos troféus)."""
        n = prog.frag_gain() * self.frag_mult
        self.frags_run[cid] = round(self.frags_run.get(cid, 0) + n, 3)
        self.app.roster.add_fragments(cid, n)
        return n

    def trophy_kill(self, e):
        """Efeitos de troféus quando um inimigo morre + troféu do chefão (só na primeira vez)."""
        if self.has("tusk") and self.elite_pool and random.random() < 0.003:
            self.drop_frag(e.pos, random.choice(sorted(self.elite_pool)), 6)
        if self.has("sap") and random.random() < 0.01 and len(self.powerups) < pw.MAX_ON_FIELD + 4:
            self.powerups.append(pw.PowerUp(self.scenery.free_pos(e.pos), "gold"))
        if e.boss:
            tid = trophy.by_stage(getattr(e, "stage_index", None))
            roster = self.app.roster
            if tid and tid not in roster.trophies:
                roster.trophies.append(tid)
                roster.save()
                self.trophies_got.append(tid)
                self.announces.append([tid, trophy.name(tid, i18n.LANG), self.ANNOUNCE_TIME + 2.0, "trophy"])
                self.fx.append(Fx("ring", e.pos, 1.2, radius=220, color=(255, 215, 120), grow=True))

    def contact_trophies(self, u):
        """Golpe de contato de inimigo que acertou: lentidão (Silk) e sangramento (Fang)."""
        if self.has("silk") and random.random() < 0.25:
            u.slow_t = 1.5
        if self.has("fang") and random.random() < 0.25:
            u.bleed_t = 3.0

    def roll_powerup(self, e):
        """Chance de um inimigo morto soltar um power-up (elites: bem maior)."""
        if e.boss or len(self.powerups) >= pw.MAX_ON_FIELD:
            return
        chance = pw.ELITE_DROP_CHANCE if e.elite else pw.DROP_CHANCE
        if random.random() < chance:
            self.powerups.append(pw.PowerUp(self.scenery.free_pos(e.pos), pw.pick_kind()))

    def thorns_fx(self, e):
        """Espinhos (capstone Thorns): faísca no inimigo que levou o dano de volta."""
        self.fx.append(Fx("anim", e.pos, 0.2, frames=sfx.impact(dict(impact="cut", el=None), e.r + 6)))

    def minion_surface(self, m):
        """Sprite da invocação (os clones de sombra são o próprio gato, escurecido)."""
        name = getattr(m, "sk", "") or ""
        src = getattr(m, "src", None)
        tgt = self.nearest_enemy(m.pos, 500)
        right = tgt is None or tgt.pos.x >= m.pos.x
        if "clone" in name.lower() and src is not None:
            walk = int(self.time * 10 + id(m) % 4) % 4   # os clones estão sempre correndo
            key = ("clone", src.member.cls, cats.look_key(cats.clean_look(src.member.look)), right, walk)
            cache = self.__dict__.setdefault("_clone_cache", {})
            surf = cache.get(key)
            if surf is None:
                base = cats.cat_sprite(src.member.cls, m.r + 4, (1 if right else -1, 0), src.member.look,
                                       walk=walk)
                surf = base.copy()
                surf.fill((70, 70, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
                surf.set_alpha(210)
                cache[key] = surf
            return surf
        return sfx.minion_sprite(name, m.r, tuple(m.color), m.element, right, self.time + (id(m) % 13) * 0.1)

    def fx_ring(self, pos, r, col):
        self.fx.append(Fx("ring", pos, 0.35, radius=r, color=col, grow=True))

    def hostile_hit(self, u, dmg, src, name, fx=None, push=None):
        """Dano de uma habilidade de elite ou golpe de monstro em um membro da party (fx: stun, slow, bleed, knock)."""
        caster = el.caster_class(src) if src is not None and (src.elite or getattr(src, "boss_classes", None)) else None
        dmgtype = "mag" if caster and CLASSES[caster]["attr"] == "int" else "phys"
        res = u.hit(dmg, dmgtype)
        if isinstance(res, (int, float)) and u.cap("thorns") and src is not None and src.hp > 0:
            self.damage(src, res * u.cap("thorns") / 100, src.pos - u.pos, None, knock=0, show=False,
                        dmgtype="phys", src=u, sk="Thorns")
            self.thorns_fx(src)
        if isinstance(res, (int, float)):
            if fx:
                self.apply_hostile_fx(u, fx, src, push)
            if u.acc_procs:
                self.acc_hurt(u, res)
            log = self.taken_log.setdefault(u, {})
            log[name] = log.get(name, 0.0) + res
            if src is not None:
                self.taken_kind.setdefault(name, (src.kind, src.color))
        elif res == "dodge":
            if u.acc_procs:
                self.acc_dodge(u)
            if self.settings["damage_numbers"]:
                self.texts.append([u.pos + V(0, -u.r - 8), "Dodge!", 0.6, (170, 250, 190)])

    CORPSE_TIME = 1.1    # quanto tempo o corpo fica no chão (some rápido)
    PUFF_TIME = 0.45     # nuvenzinha que esconde a troca do sprite vivo pelo morto
    MAX_CORPSES = 70

    def add_corpse(self, e):
        """Inimigo morreu: nuvenzinha de poeira + corpo caído (olhos em X) que some logo depois."""
        corpses = self.__dict__.setdefault("corpses", [])
        if len(corpses) >= self.MAX_CORPSES:
            corpses.pop(0)
        right = self.hero.pos.x >= e.pos.x
        corpses.append([V(e.pos), e.sprite, e.r, tuple(e.color), right, self.CORPSE_TIME])
        puffs = self.__dict__.setdefault("puffs", [])
        n = 5 if e.r < 16 else 8
        puffs.append([V(e.pos), self.PUFF_TIME, e.r,
                      [(V(random.uniform(-1, 1), random.uniform(-1, 1)) * e.r * 0.6, random.uniform(0.6, 1.0))
                       for _ in range(n)]])

    def update_corpses(self, dt):
        if getattr(self, "corpses", None):
            for c in self.corpses:
                c[5] -= dt
            self.corpses = [c for c in self.corpses if c[5] > 0]
        if getattr(self, "puffs", None):
            for p in self.puffs:
                p[1] -= dt
            self.puffs = [p for p in self.puffs if p[1] > 0]

    def draw_corpses(self, s, cam):
        for pos, spr, r, col, right, t in getattr(self, "corpses", []):
            sp = pos - cam
            if not self.on_screen(sp):
                continue
            img = enemy_sprite(spr, r, col, right, 0, dead=True)
            if t < 0.3:   # some depressa no fim
                img = img.copy()
                img.set_alpha(int(255 * t / 0.3))
            s.blit(img, (sp.x - img.get_width() / 2, sp.y - img.get_height() / 2 + r * 0.3))

    def draw_puffs(self, s, cam):
        for pos, t, r, blobs in getattr(self, "puffs", []):
            sp = pos - cam
            if not self.on_screen(sp):
                continue
            k = 1 - t / self.PUFF_TIME   # 0 -> 1
            a = int(230 * (1 - k) ** 0.7)
            for off, sz in blobs:
                rr = max(2, int(r * sz * (0.6 + 0.9 * k)))
                c = sp + off * (1 + 1.4 * k) + V(0, -10 * k)
                pygame.draw.circle(s, (150, 146, 150), c + V(1, 2), rr)
                pygame.draw.circle(s, (226, 222, 226) if a > 120 else (190, 186, 192), c, rr)
                pygame.draw.circle(s, (250, 250, 252), c - V(rr * 0.3, rr * 0.35), max(1, rr // 3))

    STUN_IMMUNE = 2.5   # depois de um atordoamento, a party fica um tempo imune (sem atordoamento em cadeia)

    def apply_hostile_fx(self, u, fx, src=None, push=None):
        """Efeitos dos golpes de monstro na party: atordoar, lentidão, sangramento e empurrão."""
        now = self.time
        if fx.get("stun") and now >= getattr(u, "stun_immune", 0):
            u.stun_t = max(getattr(u, "stun_t", 0), fx["stun"])
            u.stun_immune = now + fx["stun"] + self.STUN_IMMUNE
            if self.settings["damage_numbers"]:
                self.texts.append([u.pos + V(0, -u.r - 14), "Stunned!", 0.8, (255, 230, 90)])
        if fx.get("slow"):
            u.slow_t = max(getattr(u, "slow_t", 0), fx["slow"])
        if fx.get("bleed"):
            u.bleed_t = max(getattr(u, "bleed_t", 0), fx["bleed"])
        if fx.get("knock"):
            d = V(push) if push is not None else (u.pos - src.pos if src is not None else V(0, 0))
            if d.length_squared() > 1e-6:
                u.pos += d.normalize() * fx["knock"] * 0.18
                self.scenery.collide(u)

    def spawn_boss(self, st=None, pos=None):
        st = st or self.stage
        b = Enemy("chefe", pos if pos is not None else self.ring_point(), self.hp_mult, self.dmg_mult, self.res_mult)
        b.color = st["boss_color"]
        b.speed *= self.enemy_speed
        b.name = st["boss"]
        b.sprite = st["boss_sprite"]
        b.stage_index = st["index"]   # para o troféu do chefão
        n_cls = dgm.BOSS_CLASSES if self.dungeon else 2
        if self.elite_pool:   # o chefão vem com 2 classes aleatórias (5 nas masmorras)
            el.make_boss(b, el.pick_classes(self.elite_pool, {u.member.cls for u in self.party}, n_cls))
        if self.dungeon:   # chefão das masmorras: mais forte e sem troféu
            b.hp *= dgm.BOSS_HP
            b.max_hp = b.hp
            b.stage_index = None
            self.announces.append([b.boss_classes, st["boss"], self.ANNOUNCE_TIME + 1.5, "boss"])
        self.boss = b
        self.enemies.append(b)

    def spawn_elite_event(self):
        """A cada minuto: um Super Elite OU um Esquadrão de Elite (com aviso na tela)."""
        if not self.elite_pool:
            return
        t = self.clock()
        roles = ["heavy", "mid"] if t >= 80 else ["mid"] if t >= 20 else ["swarm"]
        for r_new, (si, t0) in ROLE_FROM.items():   # os inimigos novos (fases III e V) também viram elites
            if self.stage_level() >= si and t >= t0:
                roles.append(r_new)
        kinds = [self.role_kind(r) for r in roles]
        party_cls = {u.member.cls for u in self.party}
        if random.random() < 0.5:
            kind = kinds[0]
            e = self.new_enemy(kind, self.ring_point(), allow_elite=False)
            el.make_elite(e, el.pick_class(self.elite_pool, party_cls), "super")
            self.enemies.append(e)
            self.fx_ring(e.pos, e.r + 40, CLASSES[e.elite]["color"])
            self.announces.append([e.elite, ENEMY_NAMES.get(kind, kind), self.ANNOUNCE_TIME + 1.0, "super"])
        else:
            base = self.ring_point()
            cids = []
            for i in range(el.SQUAD_SIZE):
                kind = random.choice(kinds)
                a = i * math.tau / el.SQUAD_SIZE
                e = self.new_enemy(kind, base + V(math.cos(a), math.sin(a)) * 70, allow_elite=False)
                cid = el.pick_class(self.elite_pool, party_cls)
                el.make_elite(e, cid, "squad")
                cids.append(cid)
                self.enemies.append(e)
            self.announces.append([cids, "", self.ANNOUNCE_TIME + 1.0, "squad"])

    # ---------- masmorras ----------
    def dungeon_update(self):
        """Encontros (Super Elite ou Esquadrão) aparecem à frente conforme o herói avança; chefão no fim."""
        hero = self.hero
        while self.dg_encounters and hero.pos.x >= self.dg_encounters[0] - dgm.TRIGGER_AHEAD:
            x = self.dg_encounters.pop(0)
            self.dungeon_encounter(V(x + 120, random.uniform(-dgm.HALF_H + 80, dgm.HALF_H - 80)))
        if not self.dg_boss_spawned and hero.pos.x >= dgm.LENGTH - dgm.BOSS_TRIGGER:
            self.dg_boss_spawned = True
            st = random.choice(STAGES)   # aparência de um dos chefões das fases
            self.spawn_boss(st, pos=V(dgm.LENGTH - 120, 0))

    def dungeon_encounter(self, pos):
        pool = dgm.monster_pool(self.app.roster)
        party_cls = {u.member.cls for u in self.party}
        if not self.elite_pool:
            return
        if random.random() < 0.5:
            kind = random.choice(pool)
            e = self.new_enemy(kind, pos, allow_elite=False)
            el.make_elite(e, el.pick_class(self.elite_pool, party_cls), "super")
            self.enemies.append(e)
            self.fx_ring(e.pos, e.r + 40, CLASSES[e.elite]["color"])
            self.announces.append([e.elite, ENEMY_NAMES.get(kind, kind), self.ANNOUNCE_TIME + 1.0, "super"])
        else:
            cids = []
            for i in range(el.SQUAD_SIZE):
                kind = random.choice(pool)
                a = i * math.tau / el.SQUAD_SIZE
                e = self.new_enemy(kind, pos + V(math.cos(a), math.sin(a)) * 70, allow_elite=False)
                cid = el.pick_class(self.elite_pool, party_cls)
                el.make_elite(e, cid, "squad")
                cids.append(cid)
                self.enemies.append(e)
            self.announces.append([cids, "", self.ANNOUNCE_TIME + 1.0, "squad"])

    def dungeon_kill(self, e):
        """Recompensa principal de cada masmorra ao abater elites e o chefão."""
        did = self.dungeon[0]
        kind = dgm.DUNGEONS[did]["reward"]
        tier = "boss" if e.boss else getattr(e, "tier", "normal")
        if kind == "gold":   # Caverna: moedas de gold
            n = {"boss": 6, "super": 2, "squad": 1}.get(tier, 0)
            for _ in range(n):
                pu = pw.PowerUp(self.scenery.free_pos(e.pos + V(random.uniform(-40, 40), random.uniform(-40, 40))),
                                "gold")
                pu.amount = max(1, int(round(pu.amount * self.reward)))
                self.powerups.append(pu)
        elif kind == "accfrag":   # Masmorra: fragmentos de acessório sortidos
            n = 3 if tier == "boss" else 1 if random.random() < {"super": 0.35, "squad": 0.07}.get(tier, 0) else 0
            for _ in range(n):
                self.gain_accfrag(e.pos)

    def gain_accfrag(self, pos):
        cat = random.choice(accm.FRAG_CATS)
        roster = self.app.roster
        roster.acc_frags[cat] = roster.acc_frags.get(cat, 0) + 1
        self.dg_accfrags[cat] = self.dg_accfrags.get(cat, 0) + 1
        self.texts.append([pos + V(0, -30), L(f"+1 {accm.cat_name(cat)} Fragment",
                                              f"+1 Fragmento de {accm.cat_name(cat, 'pt')}"), 1.6, (120, 220, 230)])

    def dungeon_clear(self):
        """Recompensa fixa por concluir a masmorra + libera o próximo nível."""
        did, lv = self.dungeon
        roster = self.app.roster
        cr = dgm.clear_reward(did, lv)
        out = {}
        if "gold" in cr:
            g = self.scale_gold(cr["gold"])
            roster.gold += g
            out["gold"] = g
        if "frags" in cr and self.elite_pool:
            pool = sorted(self.elite_pool)
            for _ in range(cr["frags"]):
                self.collect_frag(random.choice(pool))
            out["frags"] = cr["frags"]
        if "accfrags" in cr:
            for _ in range(cr["accfrags"]):
                self.gain_accfrag(self.hero.pos)
            out["accfrags"] = cr["accfrags"]
        new_lv = lv + 1 > roster.dungeon_lv.get(did, 1)
        roster.dungeon_lv[did] = max(roster.dungeon_lv.get(did, 1), lv + 1)
        out["next"] = lv + 1 if new_lv else None
        return out

    def spawn(self, dt):
        if self.training:   # Sala de Treino: só os bonecos colocados pelo painel
            return
        if self.dungeon:
            self.dungeon_update()
            return
        if self.endless:
            self.update_endless()
            if self.rift:
                self.rift_check()
            if self.time >= self.next_boss:   # chefões revezando entre as fases I..V do bioma
                self.next_boss += ENDLESS_BOSS_TIME
                if self.rift:   # chefão de qualquer fase liberada; se o anterior não morreu, o cenário troca agora
                    if not self.rift_shifted and self.boss_count:
                        self.rift_shift()
                    self.rift_shifted = False
                    self.spawn_boss(STAGES[random.choice(self.rift_pool)])
                else:
                    stages = self.biome["stages"]
                    self.spawn_boss(STAGES[stages[self.boss_count % len(stages)]])
                self.boss_count += 1
        elif self.time >= self.run_len and self.boss is None:
            self.spawn_boss()
        if self.time * self.pace >= self.next_event and (self.time < self.run_len or self.endless):
            self.next_event += el.EVENT_INTERVAL
            self.spawn_elite_event()
        if self.boss is not None and self.boss.hp > 0:
            self.boss_summon_t -= dt
            if self.boss_summon_t <= 0:  # o chefão invoca um anel de morcegos de tempos em tempos
                self.boss_summon_t = 12.0
                for k in range(12):
                    a = k * math.tau / 12
                    self.enemies.append(self.new_enemy(self.role_kind("swarm"),
                                                       self.boss.pos + V(math.cos(a), math.sin(a)) * 90))
        t = self.prog_time()
        self.spawn_t -= dt
        if self.spawn_t <= 0 and len(self.enemies) < self.max_enemies:
            self.spawn_t = max(0.05, 0.8 - t * 0.005) / self.rate_mult
            roles = ["swarm", "mid", "heavy"]
            weights = [1.0, min(1.2, max(0.0, (t - 20) / 40)), min(0.4, max(0.0, (t - 80) / 60))]
            si = self.stage_level()
            if si >= ROLE_FROM["new3"][0]:   # fase III+ do bioma: o inimigo novo da fase III
                roles.append("new3")
                weights.append(min(0.9, max(0.0, (t - ROLE_FROM["new3"][1]) / 60)))
            if si >= ROLE_FROM["new5"][0]:   # fase V: o inimigo novo da fase V
                roles.append("new5")
                weights.append(min(0.5, max(0.0, (t - ROLE_FROM["new5"][1]) / 90)))
            for _ in range((1 + int(min(t, STAGE_TIME) // 45)) * self.spawn_mult):
                self.enemies.append(self.new_enemy(self.role_kind(random.choices(roles, weights)[0]),
                                                   self.ring_point()))
        if t >= self.next_horde and (t < STAGE_TIME or self.endless):
            count_scale = PARTY_SCALING.get(len(self.party), PARTY_SCALING[4])[0]
            self.next_horde += 60
            n = int((30 + min(int(t // 60), 15) * 6) * count_scale * self.spawn_mult)
            d = math.hypot(W, H) / 2 + 20
            for k in range(n):
                a = k * math.tau / n
                self.enemies.append(self.new_enemy(self.role_kind("swarm"),
                                                   self.hero.pos + V(math.cos(a), math.sin(a)) * d))

    def separate(self):
        for e in self.enemies:
            cx, cy = int(e.pos.x // CELL), int(e.pos.y // CELL)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for o in self.grid.get((cx + dx, cy + dy), ()):
                        if o is e:
                            continue
                        d = e.pos - o.pos
                        d2 = d.length_squared()
                        m = e.r + o.r
                        if 0 < d2 < m * m:
                            dist = math.sqrt(d2)
                            e.pos += d * ((m - dist) / dist * 0.25)

    # ---------- IA dos aliados ----------
    def ally_goal(self, u):
        """Para onde o aliado quer ir, conforme a role da classe (ver data.ROLES)."""
        hero = self.hero
        role = member_role(u.member)
        ang = {1: 140, 2: 220, 3: 0}.get(u.slot, 180) + self.time * 8

        def engage(t):
            return t.pos - unit(t.pos - u.pos) * (t.r + u.r + 4)

        def ring(rad):
            return hero.pos + V(rad, 0).rotate(ang)

        if role == "Tank":
            # protege o grupo: vai atrás do inimigo mais perto de qualquer outro membro
            best, bd = None, 170 ** 2
            for m in self.party:
                if m is u or m.downed or (m.pos - hero.pos).length_squared() > 420 ** 2:
                    continue
                for e in self.enemies_near(m.pos, 170):
                    d = (e.pos - m.pos).length_squared()
                    if e.hp > 0 and d < bd:
                        best, bd = e, d
            if best is None:
                t = self.nearest_enemy(u.pos, 200)
                if t and (t.pos - hero.pos).length_squared() < 300 ** 2:
                    best = t
            return engage(best) if best else ring(60)
        if role == "Melee Assassin":   # agressivo: persegue mais longe e chega antes
            t = self.nearest_enemy(u.pos, 420)
            if t and (t.pos - hero.pos).length_squared() < 560 ** 2:
                return engage(t)
            return ring(90)
        if role in ("Ranged Assassin", "Caster"):   # mantém distância dos alvos
            goal = ring(115)
            t = self.nearest_enemy(u.pos, 170)
            if t:
                away = unit(u.pos - t.pos)
                goal = u.pos + away * 140
                if (goal - hero.pos).length_squared() > 300 ** 2:   # sem se perder do grupo
                    goal = hero.pos + unit(goal - hero.pos) * 300
            return goal
        if role == "Healer":   # perto do grupo, um pouco atrás (do lado oposto aos inimigos)
            t = self.nearest_enemy(hero.pos, 400)
            goal = hero.pos + (unit(hero.pos - t.pos).rotate((u.slot or 0) * 25 - 40) * 75 if t else
                               V(70, 0).rotate(ang))
            near = self.nearest_enemy(u.pos, 110)
            if near:
                goal = u.pos + unit(u.pos - near.pos) * 120
            return goal
        if role == "Support":   # perto do grupo; os de corpo a corpo brigam só com quem chega perto
            if not u.cls["ranged"]:
                t = self.nearest_enemy(u.pos, 160)
                if t and (t.pos - hero.pos).length_squared() < 220 ** 2:
                    return engage(t)
            return ring(60)
        # All-Rounder: o comportamento padrão
        if not u.cls["ranged"]:
            t = self.nearest_enemy(u.pos, 260)
            if t and (t.pos - hero.pos).length_squared() < 380 ** 2:
                return engage(t)
        return ring(80)

    def ally_move(self, u, dt):
        hero = self.hero
        goal = self.ally_goal(u)
        to = goal - u.pos
        dist = to.length()
        if dist > 900:
            u.pos = hero.pos + V(random.uniform(-40, 40), random.uniform(-40, 40))
            return
        if dist > 6:
            step = to / dist * u.speed() * min(1.0, dist / 40) * dt
            before = V(u.pos)
            u.pos += step
            self.scenery.collide(u)
            if (u.pos - before).length_squared() < step.length_squared() * 0.15:
                # travou numa árvore: contorna pelo lado
                u.pos += step.rotate(80 if (u.slot or 0) % 2 else -80)
                self.scenery.collide(u)
        # não ficar em cima dos colegas
        for o in self.party:
            if o is u:
                continue
            d = u.pos - o.pos
            m = u.r + o.r + 4
            if 0 < d.length_squared() < m * m:
                u.pos += unit(d) * (m - d.length()) * 0.5

    # ---------- níveis da partida ----------
    def gain_xp(self, value):
        self.xp += value
        self.xp_total += value
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(5 + self.level * 4 + self.level ** 1.5)
            self.pending_lv += 1
            self.ally_level_up()

    def ally_level_up(self):
        """Aliados melhoram sozinhos a cada nível da partida."""
        for u in self.party[1:]:
            opts = self.unit_options(u)
            if opts:
                self.apply_option(u, random.choice(opts))

    def unit_options(self, u):
        opts = [("up", s) for s in u.skills if s.level < SKILL_MAX]
        opts += [("pup", i) for i in range(len(u.pas_specs)) if u.pas_lv[i] < SKILL_MAX]
        return opts

    def roll_options(self):
        opts = self.unit_options(self.hero)
        opts += [("pas", n) for n, (_, mx) in PASSIVES.items() if self.passives.get(n, 0) < mx]
        random.shuffle(opts)
        return opts[:3] or list(self.EXHAUSTED)

    # quando o herói já melhorou tudo: cura, 1 gold ou um power-up aleatório
    EXHAUSTED = (("heal", None), ("gold", None), ("power", None))

    def exhausted(self):
        return [o[0] for o in self.options] == [o[0] for o in self.EXHAUSTED]

    def apply_option(self, u, opt):
        kind, obj = opt
        if kind == "up":
            obj.level += 1
        elif kind in ("new", "relic"):
            u.skills.append(Skill(obj))
            if kind == "relic":
                self.relics += 1
        elif kind == "pas":
            self.passives[obj] = self.passives.get(obj, 0) + 1
            u.run_items[obj] = u.run_items.get(obj, 0) + 1
            apply_passive(obj, u)
        elif kind == "pup":
            u.pas_lv[obj] += 1
            u.recompute()
        elif kind == "gold":
            g = self.scale_gold(1)
            self.gold_run += g
            self.app.roster.add_gold(g)
            self.texts.append([u.pos + V(0, -u.r - 26), f"+{g} gold", 1.4, (255, 230, 120)])
        elif kind == "power":
            pk = pw.pick_kind()
            pu = pw.PowerUp(u.pos, pk)
            pw.apply(self, pk, pu.amount)
            label = f"+{pu.amount} gold" if pk == "gold" else pw.name(pk, L("en", "pt"))
            self.texts.append([u.pos + V(0, -u.r - 26), label, 1.6, (255, 230, 120)])
            self.fx_ring(u.pos, 60, (255, 230, 120))
        else:
            self.heal(u, 30, src=u, sk="Fish Feast")

    def option_text(self, opt):
        kind, obj = opt
        if kind == "up":
            return f"{obj.name}  Lv {obj.level + 1}", obj.spec["desc"], self.hero.color
        if kind == "new":
            return f"{obj['name']}  (NEW)", obj["desc"], YELLOW
        if kind == "relic":
            return f"{obj['name']}  (RELIC)", obj["desc"], (200, 140, 255)
        if kind == "pas":
            return f"{tr(obj)}  Lv {self.passives.get(obj, 0) + 1}", PASSIVES[obj][0], GREEN
        if kind == "pup":
            p = self.hero.pas_specs[obj]
            nxt = self.hero.pas_lv[obj] + 1
            mult = 1 + PASSIVE_LV_STEP * (nxt - 1)
            eff = {k: v * mult for k, v in (p.get("effects") or {p["effect"]: p["value"]}).items()}
            return f"{p['name']}  Lv {nxt}", effects_text(eff, i18n.LANG), (250, 210, 70) if p.get("capstone") else (110, 200, 255)
        if kind == "gold":
            return "+1 Gold", "Adds 1 gold to your account right away", (250, 205, 60)
        if kind == "power":
            return "Mystery Box", "Activates a random power-up right away", (255, 230, 120)
        return "Fish Feast", "Restores 30 HP", RED

    def choose(self, i):
        if self.state != "levelup" or i >= len(self.options):
            return
        if self.exhausted() and self.auto_arm:   # a partir de agora, escolhe isso sozinho até o fim da run
            self.auto_pick = self.options[i][0]
        if not self.exhausted() and self.rand_arm:   # a partir de agora, os level ups são sorteados
            self.auto_random = True
        self.apply_option(self.hero, self.options[i])
        self.pending_lv -= 1
        if self.pending_lv > 0:
            self.options = self.roll_options()
        else:
            self.state = "play"

    def next_dungeon(self):
        """Masmorra concluída: (id, próximo nível) para já iniciar o próximo nível; senão None."""
        res = getattr(self, "result", None)
        if not self.dungeon or not res or not res.get("victory"):
            return None
        did, lv = self.dungeon
        if lv + 1 > self.app.roster.dungeon_lv.get(did, 1):
            return None
        return did, lv + 1

    def next_rect(self):
        return pygame.Rect(W / 2 - 170, H - 76, 340, 40)

    def auto_rect(self):
        return pygame.Rect(W / 2 - 290, H / 2 + 172, 580, 34)

    def card_rects(self):
        cw, ch, gap = 340, 170, 30
        n = len(self.options)
        x0 = (W - (n * cw + (n - 1) * gap)) // 2
        return [pygame.Rect(x0 + i * (cw + gap), H // 2 - ch // 2 + 30, cw, ch) for i in range(n)]

    # ---------- fim da partida / meta progression ----------
    def end_run(self, victory):
        """victory = chefão derrotado (fase concluída). Morte ou saída também guardam EXP e fragmentos."""
        roster = self.app.roster
        for fd in self.frag_drops:   # fragmentos que ainda estavam voando até o herói
            self.collect_frag(fd.cid)
        self.frag_drops = []
        exp = int(self.xp_total)
        reports = [u.member.gain_exp(exp) for u in self.party]
        self.new_necks = roster.check_necklaces()   # colares liberados por classes no nível máximo
        # gold: base da fase x multiplicador da fase, proporcional ao tempo se não concluir
        frac = 1.0 if victory else min(1.0, self.clock() / self.run_len)
        if self.endless:   # Endless: gold pelo tempo sobrevivido (sem limite), com a recompensa do degrau atual
            frac = self.time / STAGE_TIME
            bid = "rift" if self.rift else self.biome["id"]
            self.new_best = self.time > roster.endless_best.get(bid, 0)
            roster.endless_best[bid] = max(roster.endless_best.get(bid, 0), self.time)
        gold = int(round(GOLD_STAGE_BASE * self.reward * self.gold_mult * frac))
        unlocked = None
        dres = None
        if self.dungeon:   # masmorra: sem gold da fase; recompensa própria ao concluir
            gold = 0
            for pu in self.powerups:   # moedas que ainda estavam no chão
                if pu.kind == "gold":
                    amt = self.scale_gold(pu.amount)
                    self.gold_run += amt
                    roster.gold += amt
            self.powerups = [pu for pu in self.powerups if pu.kind != "gold"]
            if victory:
                dres = self.dungeon_clear()
        elif victory and not self.endless and self.stage["index"] == roster.stages_cleared:
            roster.stages_cleared += 1
            if roster.stages_cleared < len(STAGES):
                unlocked = STAGES[roster.stages_cleared]["name"]
                roster.stage = roster.stages_cleared
        roster.add_gold(gold)  # também salva o progresso
        self.result = dict(victory=victory, time=self.clock(), kills=self.kills, level=self.level, exp=exp,
                           gold=gold, gold_frac=frac, total_gold=roster.gold, reports=reports,
                           stage=self.stage["name"], unlocked=unlocked, elite_kills=self.elite_kills,
                           fragments=dict(self.frags_run), gold_drops=self.gold_run, endless=self.endless,
                           tier=self.tier, best=roster.endless_best.get("rift" if self.rift else self.biome["id"], 0),
                           rift=(self.rift_lv, roster.rift_lv) if self.rift else None,
                           new_best=getattr(self, "new_best", False), trophies=list(self.trophies_got),
                           accs=list(self.acc_got) + [(a, True) for a in self.new_necks],
                           glevel=self.glevel, dungeon=self.dungeon, dres=dres,
                           accfrags=dict(getattr(self, "dg_accfrags", {})), mats=dict(self.mats_run))
        self.state = "over"

    # ---------- eventos ----------
    def handle_event(self, ev):
        """Retorna 'menu', 'restart' ou None."""
        if self.state == "train":   # painel da Sala de Treino
            return trn.handle_event(self, ev)
        if self.state == "riftq":   # Endless Rift: ficar no nível ou subir
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_1, pygame.K_2, pygame.K_KP1, pygame.K_KP2):
                self.riftq_answer(ev.key in (pygame.K_2, pygame.K_KP2))
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(self.riftq_rects()):
                    if r.collidepoint(ev.pos):
                        self.riftq_answer(i == 1)
            return None
        if self.training and self.state in ("play", "pause"):
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_t:
                self.state = "train"
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.state == "play" and \
                    trn.toggle_rect().collidepoint(ev.pos):
                self.state = "train"
                return None
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_q and self.state == "pause":
                return "menu"   # sair da sala: sem resultado nem recompensas
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if self.state == "play" and k == pygame.K_SPACE:
                self.dodge.start(self)
            elif self.state == "levelup" and k in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.choose(k - pygame.K_1)
            elif self.state == "levelup" and k == pygame.K_a and self.exhausted():
                self.auto_arm = not self.auto_arm
            elif self.state == "levelup" and k == pygame.K_a:
                self.rand_arm = not self.rand_arm
            elif self.state == "pause" and k == pygame.K_a and (self.auto_pick or self.auto_random):
                self.auto_pick = None
                self.auto_arm = False
                self.auto_random = False
                self.rand_arm = False
            elif self.state == "over":
                if k == pygame.K_r:
                    return "restart"
                if k == pygame.K_n and self.next_dungeon():
                    return "next"
                if k in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return "menu"
            elif k == pygame.K_TAB and self.state in ("play", "levelup"):
                self.rc_mode = (self.rc_mode + 1) % len(self.RC_MODES)
            elif k == pygame.K_ESCAPE:
                if self.state == "play":
                    self.state = "pause"
                elif self.state == "pause":
                    self.state = "play"
            elif self.state == "pause" and k in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.pause_scroll_by(-self.PAUSE_ROW if k in (pygame.K_UP, pygame.K_w) else self.PAUSE_ROW)
            elif self.state == "pause" and k in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                self.bonus_scroll_by(-220 if k == pygame.K_PAGEUP else 220)
            elif self.state == "pause" and k == pygame.K_q:
                self.end_run(False)
        elif ev.type == pygame.MOUSEWHEEL and self.state == "pause":
            bv = getattr(self, "bonus_view", None)
            if bv is not None and bv.collidepoint(pygame.mouse.get_pos()):
                self.bonus_scroll_by(-ev.y * 22)
            else:
                self.pause_scroll_by(-ev.y * self.PAUSE_ROW)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.state == "over":
            if self.next_dungeon() and self.next_rect().collidepoint(ev.pos):
                return "next"
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.state in ("play", "levelup"):
            for i, r in enumerate(self.rc_tabs):   # abas do medidor
                if r.collidepoint(ev.pos):
                    self.rc_mode = i
                    return None
            if self.state == "levelup":
                if self.auto_rect().collidepoint(ev.pos):
                    if self.exhausted():
                        self.auto_arm = not self.auto_arm
                    else:
                        self.rand_arm = not self.rand_arm
                    return None
                for i, r in enumerate(self.card_rects()):
                    if r.collidepoint(ev.pos):
                        self.choose(i)
                        break
        return None

    # ---------- atualização ----------
    def update(self, dt, keys):
        if self.state != "play":
            return
        self.time += dt
        hero = self.hero

        d = V(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            d.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            d.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            d.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            d.x += 1
        dashing = self.dodge.update(self, dt)   # durante a esquiva o herói segue o movimento dela
        if d.length_squared() > 0:
            d = d.normalize()
            hero.facing = d
            if not dashing and getattr(hero, "stun_t", 0) <= 0:
                hero.pos += d * hero.speed() * dt
        self.scenery.collide(hero)

        self.build_grid()
        for u in self.party:
            u.iframes = max(0.0, u.iframes - dt)
            for name in list(u.buffs):
                u.buffs[name][1] -= dt
                if u.buffs[name][1] <= 0:
                    del u.buffs[name]
            if u.downed:
                if not u.is_hero:
                    u.revive_t -= dt
                    if u.revive_t <= 0:   # ressuscita com metade da vida e alguns instantes de invulnerabilidade
                        u.downed = False
                        u.hp = u.max_hp * 0.5
                        u.iframes = 1.5
                        self.fx.append(Fx("ring", u.pos, 0.6, radius=34, color=GREEN, grow=True))
                        if self.settings["damage_numbers"]:
                            self.texts.append([u.pos + V(0, -u.r - 8), "Back!", 0.9, GREEN])
                continue
            if getattr(u, "slow_t", 0) > 0:
                u.slow_t -= dt
            if getattr(u, "bleed_t", 0) > 0:   # troféu Shadow Wolf Fang: 2% da vida máxima por segundo
                u.bleed_t -= dt
                bd = u.max_hp * 0.02 * dt
                u.hp -= bd
                log = self.taken_log.setdefault(u, {})
                log["Bleeding"] = log.get("Bleeding", 0.0) + bd
                if u.hp <= 0:
                    u.hp = 0
                    u.downed = True
                    u.revive_t = REVIVE_TIME
                    u.bleed_t = 0
                    continue
            if getattr(u, "stun_t", 0) > 0:   # atordoado por um golpe de monstro: não anda nem ataca
                u.stun_t -= dt
                continue
            if not u.is_hero:
                self.ally_move(u, dt)
            before = u.hp
            u.hp = min(u.max_hp, u.hp + u.regen * dt)
            if u.hp > before:
                log = self.heal_log.setdefault(u, {})
                log["Regeneration"] = log.get("Regeneration", 0.0) + (u.hp - before)
            for s in u.skills:
                s.update(dt, self, u)

        self.spawn(dt)
        alive_units = [u for u in self.party if not u.downed]
        self.anthem = sum(u.cap("anthem") for u in alive_units)
        passive = self.training and not trn.cfg(self.app)["aggro"]   # bonecos parados que não atacam
        for e in self.enemies:
            if passive and e.dummy:
                trn.update_dummy(self, e, dt)
                self.scenery.clamp(e)
                continue
            if e.taunt_t > 0 and e.taunter is not None and not e.taunter.downed and e.taunter in alive_units:
                tgt = e.taunter   # provocado por um tank
            else:   # o mais perto, mas os tanks "parecem" mais perto (chamam mais atenção)
                tgt = min(alive_units, key=lambda u: (u.pos - e.pos).length_squared() / (u.threat * u.threat)) \
                    if len(alive_units) > 1 else hero
            e.update(dt, mai.goal(self, e, tgt, dt))   # cada monstro anda do seu jeito (monster_ai.py)
            mai.act(self, e, tgt, alive_units, dt)       # e usa o golpe exclusivo dele
            if self.has("sap") and 0 < e.hp < e.max_hp:   # troféu Ancient Ent Sap: inimigos regeneram 1%/s
                e.hp = min(e.max_hp, e.hp + e.max_hp * 0.01 * dt)
            if e.elite or getattr(e, "boss_classes", None):
                el.update_elite(self, e, dt, alive_units)
            if self.dungeon or self.training:
                self.scenery.clamp(e)
            elif (e.pos - hero.pos).length_squared() > 1400 ** 2:
                e.pos = self.ring_point()
        el.update_hostiles(self, dt, alive_units)
        self.build_grid()
        self.separate()

        self.update_projectiles(dt)
        self.update_minions(dt)
        self.update_clouds(dt)
        self.update_corpses(dt)
        for p in self.pending:
            p[0] -= dt
            if p[0] <= 0:
                self.explode(p[1], p[2], p[3], p[4], **p[5])
        self.pending = [p for p in self.pending if p[0] > 0]

        for u in ([] if passive else alive_units):
            for e in self.enemies_near(u.pos, u.r):
                res = u.hit(e.dmg, e.dmgtype)
                if isinstance(res, (int, float)) and u.cap("thorns"):   # capstone Thorns
                    self.damage(e, res * u.cap("thorns") / 100, e.pos - u.pos, None, knock=0, show=False,
                                dmgtype="phys", src=u, sk="Thorns")
                    self.thorns_fx(e)
                if isinstance(res, (int, float)):   # medidor: dano recebido por tipo de inimigo
                    if self.trophies:
                        self.contact_trophies(u)
                    if u.acc_procs:
                        self.acc_hurt(u, res)
                    nm = e.name if e.elite else ENEMY_NAMES.get(e.kind, e.kind)
                    log = self.taken_log.setdefault(u, {})
                    log[nm] = log.get(nm, 0.0) + res
                    self.taken_kind.setdefault(nm, (e.kind, e.color))
                if res == "dodge":
                    if u.acc_procs:
                        self.acc_dodge(u)
                    if self.settings["damage_numbers"]:
                        self.texts.append([u.pos + V(0, -u.r - 8), "Dodge!", 0.6, (170, 250, 190)])
                if u.downed or res is not None:
                    break

        alive = []
        for e in self.enemies:
            if e.hp <= 0 and e.dummy:   # boneco de treino: invencível, a vida volta cheia
                e.hp = e.max_hp
                alive.append(e)
            elif e.hp <= 0 and self.training:   # invocações dos bonecos: morrem sem recompensa
                self.add_corpse(e)
                self.kills += 1
            elif e.hp <= 0:
                self.add_corpse(e)
                self.gems.append(Gem(e.pos, e.xp))
                self.kills += 1
                ks = e.last_src
                if ks is not None:
                    if ks.cap("frenzy"):
                        ks.frenzy.append(self.time)
                    if ks.cap("detonate") and e.statuses() & {"burning", "poisoned", "bleeding"}:
                        self.explode(e.pos, e.r + 60, e.max_hp * ks.cap("detonate") / 100, None, knock=120,
                                     dmgtype="mag", src=ks, sk="Detonate")
                self.roll_powerup(e)
                self.drop_materials(e)
                if self.trophies or e.boss:
                    self.trophy_kill(e)
                if e.elite or e.boss:
                    self.acc_drop(e)
                    if self.dungeon:
                        self.dungeon_kill(e)
                    if self.rift:
                        self.rift_frag(e)
                        if e.boss and not self.rift_shifted:   # chefão derrotado: o cenário muda
                            self.rift_shift()
                if ks is not None and (ks.acc_procs or self.party_procs):
                    self.acc_kill(ks, e)
                if e.elite:
                    self.elite_kills += 1
                    self.fx_ring(e.pos, e.r + 40, CLASSES[e.elite]["color"])
                # elites, super elites, esquadrões e o chefão: fragmentos das suas classes
                for fcid, n in getattr(e, "frags", {}).items():
                    for _ in range(n):
                        self.drop_frag(e.pos, fcid, e.r + 10)
                if e.boss and not self.endless:   # no Endless os chefões não encerram a run
                    self.boss_dead = True
            else:
                alive.append(e)
        self.enemies = alive

        mag = hero.magnet
        if self.has("silk"):   # Spider Queen Silk: bônus de coleta igual ao bônus de velocidade
            mag *= max(1.0, hero.speed() / 200)
        mag2 = mag * mag
        keep = []
        for gm in self.gems:
            to = hero.pos - gm.pos
            d2 = to.length_squared()
            if d2 < mag2:
                gm.pulled = True
            if gm.pulled:
                gm.pos += unit(to) * 480 * dt
            if d2 < (hero.r + 8) ** 2:
                self.gain_xp(gm.value * self.reward * self.exp_mult)  # fases avançadas e nível global: mais EXP
            else:
                keep.append(gm)
        self.gems = keep

        keep = []
        for pu in self.powerups:   # power-ups: o herói pega ao encostar
            pu.life -= dt
            if pu.kind == "gold":   # moedas: voam sozinhas até o herói, como os fragmentos
                pu.age = getattr(pu, "age", 0.0) + dt
                if pu.age > 0.7:
                    to = hero.pos - pu.pos
                    pu.pos += unit(to) * min(900, 250 + pu.age * 500) * dt
            if (pu.pos - hero.pos).length_squared() < (hero.r + 20) ** 2:
                if pu.kind == "gold":
                    pu.amount = self.scale_gold(pu.amount)
                pw.apply(self, pu.kind, pu.amount)
                label = f"+{pu.amount} gold" if pu.kind == "gold" else pw.name(pu.kind, L("en", "pt"))
                self.texts.append([hero.pos + V(0, -hero.r - 26), label, 1.6, (255, 230, 120)])
                self.fx_ring(hero.pos, 60, (255, 230, 120))
            elif pu.life > 0:
                keep.append(pu)
        self.powerups = keep

        keep = []
        for fd in self.frag_drops:   # fragmentos voam até o herói depois de um instante
            fd.age += dt
            to = hero.pos - fd.pos
            if fd.age > 0.7:
                fd.pos += unit(to) * min(900, 250 + fd.age * 500) * dt
            if fd.age > 0.7 and to.length_squared() < (hero.r + 12) ** 2:
                n = self.collect_frag(fd.cid)
                self.texts.append([hero.pos + V(0, -hero.r - 14),
                                   L(f"+{prog.fmt_frag(n)} {tr(CLASSES[fd.cid]['name'])} Fragment",
                                     f"+{prog.fmt_frag(n)} Fragmento de {tr(CLASSES[fd.cid]['name'])}"), 1.4,
                                   CLASSES[fd.cid]["color"]])
            else:
                keep.append(fd)
        self.frag_drops = keep

        for a in self.announces:
            a[2] -= dt
        live = [a for a in self.announces if a[2] > 0]   # avisos especiais (super, esquadrão, chefão) têm prioridade
        self.announces = ([a for a in live if a[3]] + [a for a in live if not a[3]][-3:])[:3]

        for t in self.texts:
            t[0].y -= 30 * dt
            t[2] -= dt
        self.texts = [t for t in self.texts if t[2] > 0]
        for f in self.fx:
            f.life -= dt
        self.fx = [f for f in self.fx if f.life > 0]

        if hero.downed and self.training:   # Sala de Treino: o herói levanta na hora com a vida cheia
            hero.downed = False
            hero.hp = hero.max_hp
            hero.iframes = 2.0
            self.texts.append([hero.pos + V(0, -hero.r - 26), L("Knocked out! (training)", "Nocauteado! (treino)"),
                               1.6, RED])
            self.fx.append(Fx("ring", hero.pos, 0.6, radius=40, color=GREEN, grow=True))
        elif hero.downed:
            self.end_run(False)
        elif getattr(self, "boss_dead", False):
            self.end_run(True)
        elif getattr(self, "rift_ask", False):   # Endless Rift: 10 minutos sobrevividos
            self.rift_ask = False
            self.state = "riftq"
        elif self.pending_lv > 0:
            self.options = self.roll_options()
            while self.auto_random and self.pending_lv > 0 and not self.exhausted():   # seleção aleatória ligada
                opt = random.choice(self.options)
                self.apply_option(self.hero, opt)
                self.pending_lv -= 1
                self.texts.append([self.hero.pos + V(0, -self.hero.r - 22),
                                   L("Level up: ", "Subiu: ") + self.option_text(opt)[0], 1.6, YELLOW])
                self.options = self.roll_options()
            if self.pending_lv <= 0:
                pass
            elif self.auto_pick and self.exhausted():   # escolha automática ligada nesta run
                while self.pending_lv > 0:
                    self.apply_option(self.hero, (self.auto_pick, None))
                    self.pending_lv -= 1
            else:
                self.state = "levelup"

    def update_projectiles(self, dt):
        for pr in self.projectiles:
            if pr.homing:
                tgt = self.nearest_enemy(pr.pos, 300)
                if tgt:
                    want = unit(tgt.pos - pr.pos) * pr.vel.length()
                    pr.vel += (want - pr.vel) * min(1.0, pr.homing * dt)
            pr.pos += pr.vel * dt
            pr.life -= dt
            for e in self.enemies_near(pr.pos, pr.r):
                if e in pr.hit:
                    continue
                pr.hit.add(e)
                if pr.explode:
                    lk = getattr(pr, "look", None)
                    if lk and lk.get("impact") in ("hit", "fist", "cut", "rain", "trap"):
                        lk = dict(lk, impact=sfx._EL_IMPACT.get(pr.element, "fire"))
                    self.explode(pr.pos, pr.explode, pr.dmg, pr.element, pr.slow, pr.stun, pr.knock,
                                 dmgtype=pr.dmgtype, src=pr.src, sk=pr.sk, look=lk)
                    pr.life = 0
                    break
                self.damage(e, pr.dmg, pr.vel, pr.element, pr.slow, pr.stun, pr.knock, dmgtype=pr.dmgtype,
                            src=pr.src, sk=pr.sk)
                pr.pierce -= 1
                if pr.pierce <= 0:
                    src = pr.src
                    bounces = getattr(pr, "bounces", 0)
                    if src is not None and getattr(src, "ricochet", 0) and bounces < 2 and \
                            random.random() < src.ricochet:   # colar do Archer: ricochete
                        near = [x for x in self.enemies_near(pr.pos, 280) if x not in pr.hit and x.hp > 0]
                        if near:
                            t = min(near, key=lambda x: (x.pos - pr.pos).length_squared())
                            pr.vel = unit(t.pos - pr.pos) * max(300.0, pr.vel.length())
                            pr.pierce = 1
                            pr.life = max(pr.life, 0.8)
                            pr.bounces = bounces + 1
                            break
                    pr.life = 0
                    break
        self.projectiles = [pr for pr in self.projectiles if pr.life > 0]

    def update_minions(self, dt):
        now = self.time
        for m in self.minions:
            m.life -= dt
            tgt = self.nearest_enemy(m.pos, 500)
            if tgt:
                m.pos += unit(tgt.pos - m.pos) * m.speed * dt
            else:
                m.pos += unit(self.hero.pos - m.pos) * m.speed * 0.5 * dt
            for e in self.enemies_near(m.pos, m.r):
                if m.cool.get(e, 0) <= now:
                    m.cool[e] = now + 0.4
                    self.damage(e, m.dmg, e.pos - m.pos, m.element, knock=150, dmgtype=m.dmgtype,
                                src=getattr(m, "src", None), sk=getattr(m, "sk", None))
        self.minions = [m for m in self.minions if m.life > 0]

    def update_clouds(self, dt):
        for c in self.clouds:
            c.life -= dt
            c.tick -= dt
            if c.tick <= 0:
                c.tick = 0.5
                for e in self.enemies_near(c.pos, c.r):
                    self.damage(e, c.dps * 0.5, V(0, 0), None, knock=0, show=False,
                                dmgtype="mag" if c.element else c.dmgtype, src=getattr(c, "src", None),
                                sk=getattr(c, "sk", None))
                    if c.element == "wind":
                        e.knock += unit(c.pos - e.pos).rotate(80) * 120
                    elif c.element == "poison":
                        e.slow_f, e.slow_t = min(e.slow_f, 0.8), max(e.slow_t, 0.6)
        self.clouds = [c for c in self.clouds if c.life > 0]

    # ---------- desenho ----------
    def text(self, txt, font, color, pos, anchor="topleft"):
        surf = self.fonts[font].render(tr(txt), True, color)
        self.screen.blit(surf, surf.get_rect(**{anchor: pos}))

    def on_screen(self, sp, m=40):
        return -m < sp.x < W + m and -m < sp.y < H + m

    def draw(self):
        s = self.screen
        s.fill(BG)
        hero = self.hero
        cam = hero.pos - V(W / 2, H / 2)

        self.scenery.draw_ground(s, cam, W, H)
        self.scenery.draw_trees(s, cam, W, H)

        for c in self.clouds:   # áreas persistentes animadas (raio = área de dano)
            sfx.draw_cloud(s, c.pos - cam, c.r, c.element, self.time, c.life / 1.5,   # some no último meio segundo
                           seed=id(c) % 9973, name=getattr(c, "sk", "") or "")

        for gm in self.gems:
            sp = gm.pos - cam
            if self.on_screen(sp):
                pygame.draw.polygon(s, gm.color, [(sp.x, sp.y - 6), (sp.x + 4, sp.y), (sp.x, sp.y + 6),
                                                  (sp.x - 4, sp.y)])

        for u in self.party:
            if not u.downed:
                for sk in u.skills:
                    if sk.kind == "aura":
                        sk.draw(s, self, u, cam)

        el.draw_hostiles(self, s, cam, under=True)   # áreas dos chefões ficam por baixo deles
        self.draw_corpses(s, cam)                      # inimigos mortos no chão (somem logo)
        for e in self.enemies:
            sp = e.pos - cam
            if self.on_screen(sp):
                frame = int((self.time + e.anim) * (10 if e.stun_t <= 0 else 0))
                if e.elite and not e.boss:   # aura da classe por baixo (chefões: sem círculos, atrapalhavam a visão)
                    pygame.draw.circle(s, CLASSES[e.elite]["color"], sp, e.r + 7, 3)
                if getattr(e, "tier", None) == "super" and not e.boss:
                    pygame.draw.circle(s, (255, 215, 80), sp, e.r + 12, 3)
                draw_enemy(s, e.sprite, sp, e.r, e.color, hero.pos.x >= e.pos.x, frame)
                if e.elite:
                    draw_class_hat(s, e.elite, sp, e.r)
                if getattr(e, "boss_classes", None):
                    draw_dual_weapons(s, e.boss_classes, sp, e.r, hero.pos - e.pos)
                if e.flash > 0:   # pisca: silhueta branca do próprio sprite (pixel art)
                    fl = flash_sprite(e.sprite, e.r, e.color, hero.pos.x >= e.pos.x, frame)
                    s.blit(fl, (sp.x - fl.get_width() / 2, sp.y - fl.get_height() / 2))
                # debuffs animados: sangrando, envenenado, queimando, congelando, atordoado, lento
                sfx.draw_status(s, sp, e.r, e.statuses(), self.time, id(e))
                mk = [k for k, on in (("taunt", e.taunt_t > 0), ("weaken", e.weak_t > 0)) if on]
                for k, kind in enumerate(mk):   # Provocado (!) e Enfraquecido (seta) em cima do inimigo
                    img = sfx.marker(kind)
                    s.blit(img, (sp.x - img.get_width() / 2 + (k - (len(mk) - 1) / 2) * 12,
                                 sp.y - e.r - img.get_height() - 4 + math.sin(self.time * 6) * 1.5))

        self.draw_puffs(s, cam)   # nuvenzinha de poeira escondendo a troca vivo -> morto
        el.draw_hostiles(self, s, cam)
        for fd in self.frag_drops:
            el.draw_fragment(s, fd.pos - cam, fd.cid, self.time + fd.age)

        for m in self.minions:   # invocações: lobo, falcão, espíritos, clones de sombra
            sp = m.pos - cam
            spr = self.minion_surface(m)
            s.blit(spr, (sp.x - spr.get_width() / 2, sp.y - spr.get_height() / 2))

        self.dodge.draw_trail(self, s, cam)
        for u in sorted(self.party, key=lambda u: u.is_hero):
            self.draw_unit(u, cam)

        for pr in self.projectiles:   # flechas, kunai, machados, bolas de fogo... (tamanho = raio de acerto)
            sp = pr.pos - cam
            lk = getattr(pr, "look", None) or sfx.look_for(None)
            spr = sfx.projectile_sprite(lk, pr.r, pr.vel, self.time + (id(pr) % 97) * 0.013, el=pr.element)
            s.blit(spr, (sp.x - spr.get_width() / 2, sp.y - spr.get_height() / 2))

        for u in self.party:
            if not u.downed:
                for sk in u.skills:
                    if sk.kind == "orbit":
                        sk.draw(s, self, u, cam)

        for f in self.fx:
            f.draw(s, cam)

        pw.draw(self, s, cam, self.fonts["small"])
        pixel.pixelate_world(s)   # pixel art: o mundo vira blocos de 2x2 e ganha o acabamento de cor
        self.draw_elite_names(cam)
        for pos, txt, life, col in self.texts:
            key = (txt, col)
            surf = self.num_cache.get(key)
            if surf is None:
                if len(self.num_cache) > 2000:
                    self.num_cache.clear()
                surf = self.num_cache[key] = self.fonts["small"].render(tr(txt), True, col)
            s.blit(surf, pos - cam - V(surf.get_width() / 2, 0))

        self.draw_hud()

        if self.state == "levelup":
            self.draw_levelup()
        elif self.state == "pause":
            self.draw_pause()
        elif self.state == "over":
            self.draw_results()
        elif self.state == "train":
            trn.draw_panel(self)
        elif self.state == "riftq":
            self.draw_riftq()
        if self.state in ("play", "levelup", "pause"):   # mouseover nos ícones de habilidade
            mp = pygame.mouse.get_pos()
            for r, sk, u in getattr(self, "hover_slots", []):
                if r.collidepoint(mp):
                    self.draw_tooltip(self.skill_tooltip(sk, u), mp)
                    break
            else:
                if self.state != "pause":   # mouseover no medidor de dano
                    for r, u in getattr(self, "recount_rows", []):
                        if r.collidepoint(mp):
                            self.draw_recount_breakdown(u, mp)
                            break

    def draw_elite_names(self, cam):
        """Nome e vida dos elites: por cima do mundo pixelado (texto nítido)."""
        s = self.screen
        for e in self.enemies:
            if e.elite:
                sp = e.pos - cam
                if self.on_screen(sp):
                    col = CLASSES[e.elite]["color"]
                    big = getattr(e, "tier", None) == "super"
                    bw = 110 if big else 60
                    self.text(e.name, "normal" if big else "small", (255, 215, 80) if big else col,
                              (sp.x, sp.y - e.r - (40 if big else 34)), "center")
                    bx, by = sp.x - bw / 2, sp.y - e.r - 24
                    pygame.draw.rect(s, DARK, (bx, by, bw, 7))
                    pygame.draw.rect(s, RED, (bx, by, bw * max(0.0, e.hp) / e.max_hp, 7))
                    pygame.draw.rect(s, col, (bx, by, bw, 7), 1)

    def draw_unit(self, u, cam):
        s = self.screen
        sp = u.pos - cam
        if u.downed:   # gato caído: deitado e sem cor
            ds = pygame.transform.rotate(cats.cat_sprite(u.member.cls, u.r, (1, 0), u.member.look,
                                                     gear=crf.gear_colors(u.member)), 90).copy()
            ds.fill((120, 115, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
            s.blit(ds, ds.get_rect(center=(sp.x, sp.y + 4)))
            if not u.is_hero:  # barrinha de contagem para ressuscitar
                frac = 1 - max(0.0, u.revive_t) / REVIVE_TIME
                bx, by = sp.x - 18, sp.y + u.r + 5
                pygame.draw.rect(s, DARK, (bx, by, 36, 5))
                pygame.draw.rect(s, (90, 170, 255), (bx, by, 36 * frac, 5))
            return
        if u.iframes > 0 and int(u.iframes * 20) % 2 == 0 and not (u.is_hero and self.dodge.active > 0):
            return
        stunned = getattr(u, "stun_t", 0) > 0
        wf = cats.walk_frame(("unit", id(u)), u.pos, u.r) if not stunned else None   # andando: ciclo de passos
        draw_class_icon(s, u.member.cls, sp, u.r, facing=u.facing, outline=YELLOW if u.is_hero else None,
                        who=u.member.name, look=u.member.look, member=u.member, walk=wf)
        sts = set()   # debuffs dos golpes dos monstros na party
        if getattr(u, "stun_t", 0) > 0:
            sts.add("stunned")
        if getattr(u, "slow_t", 0) > 0:
            sts.add("slowed")
        if getattr(u, "bleed_t", 0) > 0:
            sts.add("bleeding")
        sfx.draw_status(s, sp, u.r, sts, self.time, id(u))
        if not u.is_hero:
            bx, by = sp.x - 16, sp.y + u.r + 5
            pygame.draw.rect(s, DARK, (bx, by, 32, 4))
            pygame.draw.rect(s, GREEN, (bx, by, 32 * u.hp / u.max_hp, 4))
        else:
            bx, by = sp.x - 22, sp.y + u.r + 8
            pygame.draw.rect(s, DARK, (bx, by, 44, 6))
            pygame.draw.rect(s, RED, (bx, by, 44 * u.hp / u.max_hp, 6))

    def draw_hud(self):
        s = self.screen
        pygame.draw.rect(s, DARK, (0, 0, W, 14))
        pygame.draw.rect(s, BLUE, (0, 0, int(W * self.xp / self.xp_next), 14))
        self.text(f"Lv {self.level}", "small", WHITE, (W - 50, 1))
        m, sec = divmod(int(self.clock()), 60)
        locked = self.time >= self.run_len and not self.endless and not self.dungeon and not self.training
        self.text(f"{m:02d}:{sec:02d}", "normal", RED if locked else WHITE, (W / 2, 32), "center")
        name = tr(self.stage["name"]) + (L(f"  ·  Tier {self.tier + 1}", f"  ·  Dificuldade {self.tier + 1}")
                                         if self.endless else "")
        if self.dungeon:   # progresso no corredor
            prog_pct = max(0, min(100, int(self.hero.pos.x / dgm.LENGTH * 100)))
            name = L(f"{dgm.name(self.dungeon[0])} Lv {self.dungeon[1]}  ·  {prog_pct}%",
                     f"{dgm.name(self.dungeon[0], 'pt')} Nv {self.dungeon[1]}  ·  {prog_pct}%")
        if self.rift:   # Endless Rift: nível da fenda e cenário atual
            name = (tr("Endless Rift") + L(f"  ·  Lv {self.rift_lv}  ·  Tier {self.tier + 1}",
                                           f"  ·  Nv {self.rift_lv}  ·  Dificuldade {self.tier + 1}")
                    + "  ·  " + tr(STAGES[self.rift_scen]["name"]))
        if self.glevel:
            name += L(f"  ·  Global Lv {self.glevel}", f"  ·  Nível Global {self.glevel}")
        if self.heart:
            name += L("  ·  5 min · 2x monsters", "  ·  5 min · 2x monstros")
        self.text(name, "small", rift.COLOR if self.rift else (255, 150, 120) if self.endless else GREY, (W / 2, 50),
                  "center")
        b = self.boss
        if b is not None and b.hp > 0:
            bw = 520
            bx = W / 2 - bw / 2
            pygame.draw.rect(s, DARK, (bx, 68, bw, 14), border_radius=4)
            pygame.draw.rect(s, RED, (bx, 68, bw * b.hp / b.max_hp, 14), border_radius=4)
            pygame.draw.rect(s, WHITE, (bx, 68, bw, 14), 1, border_radius=4)
            bc = getattr(b, "boss_classes", None)
            cls_txt = f"  ({' / '.join(tr(CLASSES[c]['name']) for c in bc)})" if bc else ""
            hp_txt = L("invincible", "invencível") if b.dummy else f"{int(b.hp)} / {int(b.max_hp)}"
            self.text(f"{tr(b.name)}{cls_txt}  —  {hp_txt}", "small", WHITE, (W / 2, 92), "center")
        if self.training:
            self.text(L(f"Dummies: {trn.dummy_count(self)}", f"Bonecos: {trn.dummy_count(self)}"), "normal", WHITE,
                      (W - 150, 22))
            self.text(L("Attacking" if trn.cfg(self.app)["aggro"] else "Standing still",
                        "Atacando" if trn.cfg(self.app)["aggro"] else "Parados"), "small",
                      RED if trn.cfg(self.app)["aggro"] else GREY, (W - 150, 46))
            if self.state == "play":
                trn.draw_toggle(self)
        else:
            self.text(f"Kills: {self.kills}", "normal", WHITE, (W - 150, 22))
            self.text(f"Elite kills: {self.elite_kills}", "small", (230, 170, 255), (W - 150, 46))
            self.text(f"Run EXP: {int(self.xp_total)}", "small", GREY, (W - 150, 64))
        if self.settings["show_fps"]:
            self.text(f"FPS {self.app.fps:.0f}", "small", GREEN, (W - 150, 82))

        # party: cada membro com barra de vida e mini barra de habilidades
        self.hover_slots = []
        y = 24
        for u in self.party:
            pygame.draw.rect(s, PANEL, (8, y, 290, self.PARTY_ROW), border_radius=6)
            if u.downed:
                pygame.draw.circle(s, (70, 70, 80), (26, y + 22), 10)
            else:
                draw_class_icon(s, u.member.cls, (26, y + 22), 10, who=u.member.name, look=u.member.look, member=u.member, shadow=False)
            name_surf = self.fonts["small"].render(u.member.name, True, YELLOW if u.is_hero else WHITE)
            s.blit(name_surf, (44, y + 4))
            self.text(f"Lv {u.member.level}", "small", (150, 190, 255), (44 + name_surf.get_width() + 8, y + 4))
            ctxt = f"{tr(u.cls['name'])} Lv {u.member.class_level(u.member.cls)}"
            self.text(ctxt, "small", GREY, (290, y + 4), "topright")
            cw = self.fonts["small"].size(ctxt)[0]
            s.blit(si.class_icon(u.member.cls, 18), (290 - cw - 22, y + 1))
            if u.downed and not u.is_hero:
                frac = 1 - max(0.0, u.revive_t) / REVIVE_TIME
                pygame.draw.rect(s, DARK, (44, y + 25, 176, 6), border_radius=2)
                pygame.draw.rect(s, (90, 170, 255), (44, y + 25, 176 * frac, 6), border_radius=2)
                self.text(f"revive {max(0.0, u.revive_t):.0f}s", "small", (150, 200, 255), (290, y + 21), "topright")
            else:
                pygame.draw.rect(s, DARK, (44, y + 24, 246, 6))
                pygame.draw.rect(s, GREEN if not u.downed else RED, (44, y + 24, 246 * u.hp / u.max_hp, 6))
            sz, gap = self.MINI_SIZE, 4
            for i in range(self.HOT_SLOTS):
                r = pygame.Rect(44 + i * (sz + gap), y + 38, sz, sz)
                if i < len(u.skills):
                    self.draw_skill_slot(r, u.skills[i], u, small=True)
                else:
                    pygame.draw.rect(s, (40, 40, 52), r, border_radius=5)
            y += self.PARTY_ROW + 6

        # power-ups ativos (canto inferior esquerdo): ícone + barra com o tempo restante; e barra de habilidades
        self.draw_powerup_timers()
        self.draw_hotbar()
        self.draw_recount()
        self.draw_announces()
        self.draw_buff_tip()

    POWERUP_BUFFS = {"Cardboard Box": "barrier", "Zoomies": "fury", "Laser Pointer": "precision",
                     "Feather Wand": "haste"}

    def buff_icon(self, name, size):
        """Ícone de um buff do herói: habilidade (de qualquer membro), acessório/emblema ou passiva."""
        cache = self.__dict__.setdefault("_buff_icons", {})
        key = (name, size)
        if key in cache:
            return cache[key]
        ic, kind = None, "other"
        if name in accm.ACC:
            ic, kind = accm.icon(name, size), "item"
        else:
            for u in self.party:
                for sk in u.skills:
                    if sk.name == name:
                        ic, kind = si.active_icon(sk.spec, size), "skill"
                        break
                if ic:
                    break
        if ic is None:   # habilidade de quem não está na party (ex.: buff de outra fonte): procura pelo nome
            for cc in prog.CONTENT.values():
                for sp in [cc.get("basic")] + list(cc.get("actives", [])):
                    if sp and sp.get("name") == name:
                        ic, kind = si.active_icon(sp, size), "skill"
                        break
                if ic:
                    break
        if ic is None:
            ic = si._render("holy" if name == "Sanctuary" else "up", (60, 90, 70), (240, 230, 200), size)
        cache[key] = (ic, kind)
        return ic, kind

    def draw_powerup_timers(self):
        """Canto inferior esquerdo: power-ups ativos (quadrados com moldura dourada) e buffs de habilidades e
        acessórios (redondos, com anel de tempo: azul = habilidade, roxo = acessório/emblema)."""
        s = self.screen
        self._buff_tip = None
        lang = L("en", "pt")
        hero = self.hero
        mx = self.__dict__.setdefault("_buff_max", {})   # duração total de cada buff (para a barra)
        for name, b in hero.buffs.items():
            if b[1] > mx.get(name, 0) - 0.05 or name not in mx:
                mx[name] = max(b[1], 0.01) if b[1] > mx.get(name, 0) else mx[name]
        for name in list(mx):
            if name not in hero.buffs:
                del mx[name]
        x0, y0 = 12, H - 64
        x, y = x0, y0
        mouse = pygame.mouse.get_pos()
        tip = None

        def advance():
            nonlocal x, y
            x += 56
            if x > 300:   # não invade a esquiva / barra de habilidades: sobe uma linha
                x, y = x0, y - 62

        pu_names = set(self.POWERUP_BUFFS)
        for name, kind in self.POWERUP_BUFFS.items():   # power-ups: quadrados dourados
            b = hero.buffs.get(name)
            if not b:
                continue
            left = max(0.0, b[1])
            frac = min(1.0, left / pw.BUFF_TIME)
            box = pygame.Rect(x - 4, y - 4, 52, 58)
            pygame.draw.rect(s, (20, 20, 28), box, border_radius=6)
            pygame.draw.rect(s, (255, 220, 90), box, 2, border_radius=6)
            ic = pw.icon(kind, 40)
            if left < 2.5 and int(self.time * 6) % 2:   # pisca perto de acabar
                ic = ic.copy()
                ic.set_alpha(110)
            s.blit(ic, (x + 2, y))
            sh = pygame.Surface((40, int(40 * (1 - frac))), pygame.SRCALPHA)   # sombra que desce com o tempo
            sh.fill((0, 0, 0, 120))
            s.blit(sh, (x + 2, y))
            pygame.draw.rect(s, (40, 40, 52), (x, y + 44, 44, 6), border_radius=3)
            pygame.draw.rect(s, (255, 220, 90), (x, y + 44, int(44 * frac), 6), border_radius=3)
            self.text(f"{left:.0f}", "small", WHITE, (x + 38, y + 2), "center")
            if box.collidepoint(mouse):
                tip = (L("Power-up · ", "Power-up · ") + f"{pw.name(kind, lang)}: {pw.desc(kind, lang)}", (255, 220, 90))
            advance()
        for name, b in hero.buffs.items():   # buffs de habilidades / acessórios: redondos
            if name in pu_names:
                continue
            left = max(0.0, b[1])
            frac = min(1.0, left / max(0.01, mx.get(name, left)))
            ic, kind = self.buff_icon(name, 34)
            col = (110, 200, 255) if kind == "skill" else (190, 140, 255) if kind == "item" else (140, 220, 160)
            c = (x + 22, y + 22)
            pygame.draw.circle(s, (20, 20, 28), c, 26)
            pygame.draw.circle(s, (45, 45, 58), c, 24, 4)
            if frac > 0:   # anel que esvazia com o tempo
                import math as _m
                rect = pygame.Rect(0, 0, 48, 48)
                rect.center = c
                pygame.draw.arc(s, col, rect, _m.pi / 2, _m.pi / 2 + frac * _m.tau, 4)
            mask = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (17, 17), 17)
            icc = ic.copy()
            icc.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            if left < 1.5 and int(self.time * 6) % 2:
                icc.set_alpha(110)
            s.blit(icc, (c[0] - 17, c[1] - 17))
            self.text(f"{left:.0f}", "small", WHITE, (c[0], y + 50), "center")
            if (pygame.Vector2(mouse) - c).length() <= 26:
                nm = accm.name(name, lang) if kind == "item" else tr(name)
                lab = L("Skill buff", "Buff de habilidade") if kind == "skill" else \
                    L("Accessory buff", "Buff de acessório") if kind == "item" else L("Passive buff", "Buff de passiva")
                parts = []
                for k, v in b[0].items():   # efeitos do buff (frações viram %)
                    if k in accm.BUFF_NAME:
                        parts.append(accm.buff_text({k: v * 100 if k in accm.BUFF_FRAC else v}, 1, lang))
                    else:
                        parts.append(f"{k} {v:+g}")
                tip = (f"{lab} · {nm}: " + ", ".join(parts), col)
            advance()
        # descrição do item sob o mouse: desenhada depois da hotbar (draw_buff_tip) para não ficar por baixo
        self._buff_tip = (tip, x0, min(y, y0)) if tip else None

    def draw_buff_tip(self):
        bt = getattr(self, "_buff_tip", None)
        if not bt:
            return
        tip, x0, ytop = bt
        s = self.screen
        surf = self.fonts["small"].render(tr(tip[0]), True, tip[1])
        box = surf.get_rect(bottomleft=(x0, ytop - 12)).inflate(12, 8)
        if box.right > W - 4:
            box.right = W - 4
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill((12, 12, 18, 235))
        s.blit(bg, box)
        pygame.draw.rect(s, tip[1], box, 1)
        s.blit(surf, surf.get_rect(center=box.center))

    # ---------- pause: síntese do herói e bônus da run ----------
    RUN_ITEM_TOTAL = {
        "Feather Paws": lambda n: f"+{10 * n}% movement speed",
        "Ninth Life": lambda n: f"+{20 * n} max HP",
        "Long Whiskers": lambda n: f"+{(1.3 ** n - 1) * 100:.0f}% pickup range",
        "Catnip": lambda n: f"+{12 * n}% damage",
        "Cat Nap": lambda n: f"-{(1 - 0.92 ** n) * 100:.0f}% cooldown time",
        "Warm Milk": lambda n: f"+{2.5 * n:g} HP/5s regeneration",
        "Sharp Claws": lambda n: f"+{10 * n}% range",
        "Ball of Yarn": lambda n: f"+{10 * n}% area",
    }

    def hero_summary(self):
        """[(rótulo, valor)] com os status efetivos do herói agora (meta + passivas + itens da run)."""
        u = self.hero
        st = u.stats
        cd = (1 - u.haste * u.cd_mult) * 100
        return [
            ("HP", f"{int(u.hp)} / {int(u.max_hp)}"),
            ("STR", f"{st['str']}"),
            ("AGI", f"{st['agi']}"),
            ("INT", f"{st['int']}"),
            ("VIT", f"{st['vit']}"),
            ("Physical damage", f"+{(u.phys * u.dmg_mult - 1) * 100:.0f}%"),
            ("Magic damage", f"+{(u.mag * u.dmg_mult - 1) * 100:.0f}%"),
            ("Critical chance", f"{u.crit_chance:.1f}%"),
            ("Critical damage", f"+{u.crit_dmg:.0f}%"),
            ("Cooldown", f"{cd:.1f}%"),
            ("Armor", f"{u.armor:.1f}"),
            ("Magic defense", f"{u.mres:.1f}"),
            ("Dodge", f"{u.dodge:.1f}%"),
            ("Defense", f"{min(0.75, u.defense) * 100:.0f}%"),
            ("Regeneration", f"{u.regen * 5:.1f} HP/5s"),
            ("Speed", f"{u.speed():.0f}"),
            ("Pickup range", f"{u.magnet:.0f}"),
            ("Area", f"+{(u.area - 1) * 100:.0f}%"),
            ("Range", f"+{(u.range - 1) * 100:.0f}%"),
            ("Healing", f"+{(u.heal_mult - 1) * 100:.0f}%"),
            ("Duration", f"+{(u.dur_mult - 1) * 100:.0f}%"),
        ]

    def skill_bonus_text(self, sk):
        L = sk.level
        if L <= 1:
            return "no bonus yet"
        parts = [f"+{25 * (L - 1)}% damage" if sk.kind not in ("heal", "buff") else
                 (f"+{25 * (L - 1)}% healing" if sk.kind == "heal" else f"+{10 * (L - 1)}% effect/duration"),
                 f"-{6 * (L - 1)}% cooldown"]
        if sk.kind in ("slash", "strike", "cone", "aura", "heal", "cloud", "orbit") or sk.p("explode"):
            parts.append(f"+{8 * (L - 1)}% area")
        extra = sk.bonus
        if extra and sk.kind in ("shot", "strike", "orbit"):
            parts.append(f"+{extra} {'projectile' if sk.kind == 'shot' else 'impact' if sk.kind == 'strike' else 'blade'}"
                         + ("s" if extra > 1 else ""))
        if sk.kind == "shot" and L >= 4:
            parts.append("+1 pierce")
        return " · ".join(parts)

    def wrap_lines(self, txt, width):
        f = self.fonts["small"]
        words, lines, cur = tr(txt).split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if f.size(t)[0] <= width:
                cur = t
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def fit_text(self, txt, width):
        """Corta o texto (já traduzido) com '...' para caber na largura."""
        f = self.fonts["small"]
        txt = tr(txt)
        if f.size(txt)[0] <= width:
            return txt
        while len(txt) > 3 and f.size(txt + "...")[0] > width:
            txt = txt[:-1]
        return txt.rstrip() + "..."

    def wrap_fit(self, txt, width):
        """Corta o texto (por partes ' · ') para caber na largura."""
        f = self.fonts["small"]
        if f.size(txt)[0] <= width:
            return txt
        sep = " · " if " · " in txt else "; "
        parts = txt.split(sep)
        while len(parts) > 1 and f.size(sep.join(parts) + " ...")[0] > width:
            parts.pop()
        out = sep.join(parts)
        while len(out) > 4 and f.size(out + "...")[0] > width:
            out = out[:-1]
        return out.rstrip(" ;·") + " ..."

    PAUSE_ROW = 26
    ANNOUNCE_TIME = 4.0

    def draw_announces(self):
        """Faixas no topo: elite comum, Super Elite, Esquadrão de Elite e o chefão de 2 classes."""
        if self.state == "pause":
            return
        s = self.screen
        y = 120 if self.boss is None or self.boss.hp <= 0 else 132
        fn = self.fonts["normal"]
        for cid, enemy, t, kind in self.announces:
            total = self.ANNOUNCE_TIME + {"boss": 1.5, "trophy": 2.0, "acc": 2.0, "accdup": 2.0}.get(kind, 1.0 if kind else 0.0)
            alpha = int(255 * min(1.0, t / 0.6, (total - t) / 0.25 + 0.2))
            white = WHITE
            if kind == "super":
                col = (255, 215, 80)
                parts = [(fn.render(L("WARNING! A SUPER ELITE ", "ALERTA! Um SUPER ELITE "), True, (255, 120, 90)), None),
                         (si.class_icon(cid, 28), "icon"),
                         (fn.render(f" Super {tr(CLASSES[cid]['name'])} {tr(enemy)}", True, col), None),
                         (fn.render(L(" has appeared!", " apareceu!"), True, white), None)]
            elif kind == "squad":
                col = (255, 120, 90)
                parts = [(fn.render(L("WARNING! An ELITE SQUAD has appeared: ", "ALERTA! Um ESQUADRÃO DE ELITE apareceu: "),
                                    True, col), None)]
                for c in cid:
                    parts.append((si.class_icon(c, 28), "icon"))
                    parts.append((fn.render(" ", True, white), None))
            elif kind in ("acc", "accdup"):
                col = (120, 220, 230)
                cat = accm.ACC[cid]["cat"]
                parts = [(fn.render(L("ACCESSORY FOUND: ", "ACESSÓRIO ENCONTRADO: ") if kind == "acc" else
                                    L("Duplicate: ", "Repetido: "), True, white), None),
                         (accm.icon(cid, 30), "icon"), (fn.render(f" {enemy}", True, col), None),
                         (fn.render(L("  (Jeweler)", "  (Joalheiro)") if kind == "acc" else
                                    L(f"  -> +{accm.NECK_DUP_FRAGS} {tr(CLASSES[accm.neck_class(cid)]['name'])} Fragments",
                                      f"  -> +{accm.NECK_DUP_FRAGS} Fragmentos de "
                                      f"{tr(CLASSES[accm.neck_class(cid)]['name'])}") if cat == "neck" else
                                    L(f"  -> +1 {accm.cat_name(cat)} Fragment",
                                      f"  -> +1 Fragmento de {accm.cat_name(cat, 'pt')}"), True, GREY), None)]
            elif kind == "trophy":
                col = (255, 215, 120)
                parts = [(fn.render(L("TROPHY OBTAINED: ", "TROFÉU OBTIDO: "), True, white), None),
                         (trophy.icon(cid, 30), "icon"),
                         (fn.render(f" {enemy}", True, col), None),
                         (fn.render(L("  (Altar of Trophies)", "  (Altar dos Troféus)"), True, GREY), None)]
            elif kind == "boss":
                col = RED
                parts = [(fn.render(f"{tr(enemy)} ", True, RED), None)]
                for k, c in enumerate(cid):
                    parts.append((si.class_icon(c, 28), "icon"))
                    parts.append((fn.render(f" {tr(CLASSES[c]['name'])}" + (" + " if k == 0 else ""), True,
                                            CLASSES[c]["color"]), None))
                parts.append((fn.render(L(" has arrived!", " chegou!"), True, white), None))
            else:
                col = CLASSES[cid]["color"]
                parts = [(fn.render(L("An elite ", "Um elite "), True, white), None),
                         (si.class_icon(cid, 28), "icon"),
                         (fn.render(f" {tr(CLASSES[cid]['name'])} {tr(enemy)}", True, col), None),
                         (fn.render(L(" has appeared!", " apareceu!"), True, white), None)]
            w = sum(p.get_width() for p, _ in parts) + 36
            hgt = 44 if kind else 40
            box = pygame.Surface((w, hgt), pygame.SRCALPHA)
            pygame.draw.rect(box, (40, 10, 14, 230) if kind else (20, 14, 26, 215), box.get_rect(), border_radius=10)
            pygame.draw.rect(box, (*col, 255), box.get_rect(), 3 if kind else 2, border_radius=10)
            x = 18
            for p, _k in parts:
                box.blit(p, (x, (hgt - p.get_height()) // 2))
                x += p.get_width()
            box.set_alpha(max(0, min(255, alpha)))
            s.blit(box, (W / 2 - w / 2, y))
            y += hgt + 6

    def bonus_scroll_by(self, dy):
        self.bonus_scroll = max(0, min(getattr(self, "bonus_max_scroll", 0), getattr(self, "bonus_scroll", 0) + dy))

    def pause_scroll_by(self, dy):
        self.pause_scroll = max(0, min(getattr(self, "pause_max_scroll", 0), getattr(self, "pause_scroll", 0) + dy))

    def draw_pause(self):
        s = self.screen
        s.blit(self.overlay, (0, 0))
        self.hover_slots = []   # no pause só valem as linhas da lista de habilidades
        u = self.hero
        self.text("PAUSED", "big", WHITE, (W / 2, 46), "center")
        m, sec = divmod(int(self.clock()), 60)
        self.text(f"{self.stage['name']}  ·  {m:02d}:{sec:02d}  ·  Run level {self.level}  ·  Kills {self.kills}  ·  "
                  f"EXP {int(self.xp_total)}  ·  Gold +{self.gold_run}", "normal", GREY, (W / 2, 88), "center")

        # ---- síntese do herói ----
        left = pygame.Rect(40, 120, 520, 520)
        pygame.draw.rect(s, PANEL, left, border_radius=12)
        draw_class_icon(s, u.member.cls, (left.x + 34, left.y + 40), 18, outline=YELLOW, who=u.member.name, look=u.member.look, member=u.member)
        self.text(u.member.name, "normal", YELLOW, (left.x + 66, left.y + 18))
        self.text(f"Lv {u.member.level}  ·  {tr(u.cls['name'])} Lv {u.member.class_level(u.member.cls)}", "small", GREY,
                  (left.x + 66, left.y + 44))
        # lista de status com rolagem (roda do mouse sobre o painel ou setas cima/baixo)
        rows = self.hero_summary()
        view = pygame.Rect(left.x + 8, left.y + 74, left.w - 16, left.h - 98)
        self.pause_view = view
        self.pause_max_scroll = max(0, len(rows) * self.PAUSE_ROW - view.h)
        self.pause_scroll = max(0, min(self.pause_max_scroll, getattr(self, "pause_scroll", 0)))
        clip = s.get_clip()
        s.set_clip(view)
        for i, (lab, val) in enumerate(rows):
            y = view.y + 8 + i * self.PAUSE_ROW - self.pause_scroll
            if y < view.y - 30 or y > view.bottom:
                continue
            if i % 2:
                pygame.draw.rect(s, (34, 34, 46), (left.x + 12, y - 4, left.w - 24, 24), border_radius=4)
            self.text(lab, "small", GREY, (left.x + 24, y))
            self.text(val, "small", WHITE, (left.right - 30, y), "topright")
        s.set_clip(clip)
        if self.pause_max_scroll > 0:   # barra de rolagem
            total = len(rows) * self.PAUSE_ROW
            bar_h = max(30, view.h * view.h / total)
            by = view.y + (view.h - bar_h) * self.pause_scroll / self.pause_max_scroll
            pygame.draw.rect(s, GREY, (left.right - 14, by, 4, bar_h), border_radius=2)
            if self.pause_scroll < self.pause_max_scroll:
                self.text("mouse wheel / Up-Down: more stats", "small", (110, 110, 125), (left.centerx, left.bottom - 6),
                          "midbottom")

        # ---- bônus da run ----
        right = pygame.Rect(580, 120, W - 620, 520)
        pygame.draw.rect(s, PANEL, right, border_radius=12)
        x = right.x + 24
        self.text("Bonuses gained this run", "normal", YELLOW, (x, right.y + 18))
        # conteúdo com rolagem (roda do mouse sobre o painel ou PgUp/PgDn)
        view = pygame.Rect(right.x + 4, right.y + 50, right.w - 8, right.h - 70)
        self.bonus_view = view
        self.bonus_scroll = max(0, min(getattr(self, "bonus_scroll", 0), getattr(self, "bonus_max_scroll", 0)))
        clip = s.get_clip()
        s.set_clip(view)
        y0 = view.y + 4
        y = y0 - self.bonus_scroll
        self.text("Skills", "small", YELLOW, (x, y))
        y += 22
        for sk in u.skills:
            self.hover_slots.append((pygame.Rect(x, y - 3, 260, 20), sk, u))
            s.blit(si.active_icon(sk.spec, 18), (x, y - 2))
            self.text(self.fit_text(sk.name, 170), "small", WHITE, (x + 24, y))
            self.text(f"Lv {sk.level}/{SKILL_MAX}", "small", GREEN if sk.level > 1 else GREY, (x + 200, y))
            for ln in self.wrap_lines(self.skill_bonus_text(sk), right.right - (x + 262) - 14):
                self.text(ln, "small", GREEN if sk.level > 1 else (110, 110, 120), (x + 262, y))
                y += 18
            y += 4
        y += 14
        self.text("Passives", "small", YELLOW, (x, y))
        y += 22
        if not u.pas_specs:
            self.text("no passives equipped", "small", (110, 110, 120), (x, y))
            y += 22
        for p, lv in zip(u.pas_specs, u.pas_lv):
            mult = 1 + PASSIVE_LV_STEP * (lv - 1)
            eff = {k: v * mult for k, v in (p.get("effects") or {p["effect"]: p["value"]}).items()}
            s.blit(si.passive_icon(p, 18), (x, y - 2))
            self.text(p["name"], "small", (250, 210, 70) if p.get("capstone") else WHITE, (x + 24, y))
            self.text(f"Lv {lv}/{SKILL_MAX}", "small", GREEN if lv > 1 else GREY, (right.right - 24, y), "topright")
            y += 18
            for ln in self.wrap_lines(effects_text(eff, i18n.LANG), right.right - (x + 24) - 24):
                self.text(ln, "small", GREEN if lv > 1 else (150, 150, 165), (x + 24, y))
                y += 17
            y += 6
        y += 14
        self.text("Run items", "small", YELLOW, (x, y))
        y += 22
        if not self.passives:
            self.text("no items yet", "small", (110, 110, 120), (x, y))
            y += 22
        for name, lv in self.passives.items():
            mx = PASSIVES[name][1]
            s.blit(si.item_icon(name, 18), (x, y - 2))
            self.text(name, "small", WHITE, (x + 24, y))
            self.text(f"Lv {lv}/{mx}", "small", GREEN, (x + 200, y))
            self.text(self.RUN_ITEM_TOTAL.get(name, lambda n: PASSIVES[name][0])(lv), "small", GREEN, (x + 262, y))
            y += 22
        # fragmentos de classe: obtidos nesta run (total no inventário)
        y += 14
        self.text("Fragments this run  (inventory total)", "small", YELLOW, (x, y))
        y += 22
        if not self.frags_run:
            self.text("no fragments yet", "small", (110, 110, 120), (x, y))
            y += 22
        inv = self.app.roster.fragments
        col_w = 300
        for i, (cid, n) in enumerate(sorted(self.frags_run.items(), key=lambda kv: -kv[1])):
            fx = x + (i % 2) * col_w
            s.blit(si.class_icon(cid, 18), (fx, y - 2))
            self.text(f"{tr(CLASSES[cid]['name'])} Fragment", "small", CLASSES[cid]["color"], (fx + 24, y))
            self.text(f"{prog.fmt_frag(n)} ({prog.fmt_frag(inv.get(cid, 0))})", "small", WHITE,
                      (fx + col_w - 30, y), "topright")
            if i % 2 == 1:
                y += 22
        if len(self.frags_run) % 2 == 1:
            y += 22
        if u.buffs:
            y += 14
            self.text("Active buffs", "small", YELLOW, (x, y))
            y += 22
            for name, (eff, t) in u.buffs.items():
                txt = ", ".join(f"{ {'dmg': 'damage', 'speed': 'speed', 'haste': 'cooldown', 'dr': 'defense', 'crit': 'crit chance', 'critdmg': 'crit damage', 'invuln': 'invulnerable'}.get(k, k)} "
                                + (f"+{v:.0f}%" if k in ('crit', 'critdmg') else "" if k == "invuln" else f"+{v * 100:.0f}%")
                                for k, v in eff.items())
                self.text(f"{name}  ({t:.0f}s): {txt}", "small", (150, 200, 255), (x, y))
                y += 22
        s.set_clip(clip)
        total = y + self.bonus_scroll - y0
        self.bonus_max_scroll = max(0, total - view.h + 8)
        if self.bonus_max_scroll > 0:   # barra de rolagem
            bar_h = max(30, view.h * view.h / max(1, total))
            by = view.y + (view.h - bar_h) * self.bonus_scroll / self.bonus_max_scroll
            pygame.draw.rect(s, GREY, (right.right - 10, by, 4, bar_h), border_radius=2)
            if self.bonus_scroll < self.bonus_max_scroll:
                self.text("mouse wheel / PgUp-PgDn: more", "small", (110, 110, 125), (right.centerx, right.bottom - 6),
                          "midbottom")

        if self.training:
            self.text(L("ESC resume  ·  T training panel  ·  Q back to camp",
                        "ESC continua  ·  T painel de treino  ·  Q volta ao acampamento"), "normal", GREY,
                      (W / 2, H - 40), "center")
        else:
            self.text("ESC resume  ·  Q end the run (the party keeps EXP and fragments)", "normal", GREY, (W / 2, H - 40), "center")
        auto = []
        if self.auto_random:
            auto.append(L("Random level-ups", "Seleção aleatória"))
        if self.auto_pick:
            auto.append(L("Auto: ", "Automático: ") + self.option_text((self.auto_pick, None))[0])
        if auto:
            self.text("  ·  ".join(auto) + L("  ·  A turn off", "  ·  A desliga"), "small", YELLOW,
                      (W / 2, H - 16), "center")

    HOT_SLOTS = 7
    HOT_SIZE = 50
    HOT_GAP = 8

    # ---------- medidor (estilo Recount): dano causado, dano recebido e cura ----------
    RC_W, RC_ROW, RC_HEAD = 330, 24, 26
    RC_MODES = [("Damage Done", "Damage", "DPS"), ("Damage Taken", "Taken", "DTPS"), ("Healing Done", "Healing", "HPS"),
                ("Crowd Control", "CC", "s")]
    CC_COLORS = {"Taunt": (240, 120, 90), "Weaken": (200, 120, 230), "Stun": (255, 230, 90), "Freeze": (140, 210, 255), "Knockdown": (200, 150, 90), "Slow": (170, 170, 220),
                 "Chill": (120, 190, 255), "Knockback": (150, 230, 180), "Pull": (190, 140, 255)}

    def rc_log(self, mode=None):
        mode = self.rc_mode if mode is None else mode
        return (self.dmg_log, self.taken_log, self.heal_log, self.cc_log)[mode]

    def unit_total(self, u, mode=None):
        mode = self.rc_mode if mode is None else mode
        log = self.rc_log(mode).get(u, {})
        if mode == 3:
            return sum(sum(d.values()) for d in log.values())
        return sum(log.values())

    def rc_value_text(self, val, rate):
        if self.rc_mode == 3:
            return f"{val:,.1f} s"
        return f"{val:,.0f} - {val / self.fight_time():,.1f} {rate}"

    def unit_damage(self, u):
        return self.unit_total(u, 0)

    def fight_time(self):
        return max(1.0, self.time - self.meter_t0)

    def draw_recount(self):
        s = self.screen
        self.recount_rows, self.rc_tabs = [], []
        if self.state == "pause":
            return
        title, _, rate = self.RC_MODES[self.rc_mode]
        rows = sorted(self.party, key=self.unit_total, reverse=True)
        w, rh, hh = self.RC_W, self.RC_ROW, self.RC_HEAD
        h = hh + 20 + len(rows) * rh + 6
        box = pygame.Rect(W - w - 10, H - h - 10, w, h)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (10, 10, 16, 200), bg.get_rect(), border_radius=6)
        pygame.draw.rect(bg, (60, 40, 30, 235), (0, 0, w, hh), border_top_left_radius=6, border_top_right_radius=6)
        s.blit(bg, box)
        pygame.draw.rect(s, (110, 90, 70), box, 1, border_radius=6)
        # abas (clicáveis; TAB também alterna)
        mp = pygame.mouse.get_pos()
        tx = box.x + 4
        for i, (_, short, _) in enumerate(self.RC_MODES):
            tw = self.fonts["small"].size(short)[0] + 16
            tr = pygame.Rect(tx, box.y + 3, tw, hh - 6)
            act, hov = i == self.rc_mode, tr.collidepoint(mp)
            pygame.draw.rect(s, (150, 110, 60) if act else (85, 65, 50) if hov else (45, 32, 26), tr, border_radius=4)
            pygame.draw.rect(s, (230, 190, 120) if act else (110, 90, 70), tr, 1, border_radius=4)
            self.text(short, "small", WHITE if act else (210, 195, 170), tr.center, "center")
            self.rc_tabs.append(tr)
            tx += tw + 4
        total = sum(self.unit_total(u) for u in self.party)
        self.text(f"{title}:  {total:,.1f} s" if self.rc_mode == 3 else
                  f"{title}:  {total:,.0f}  ·  {total / self.fight_time():,.1f} {rate}", "small", (200, 190, 170),
                  (box.x + 8, box.y + hh + 3))
        top = max(1.0, self.unit_total(rows[0])) if rows else 1.0
        bar_col = {0: None, 1: (170, 60, 60), 2: (60, 170, 90), 3: (150, 110, 210)}[self.rc_mode]
        f = self.fonts["small"]
        for i, u in enumerate(rows):
            r = pygame.Rect(box.x + 3, box.y + hh + 21 + i * rh, w - 6, rh - 2)
            val = self.unit_total(u)
            col = bar_col or u.cls["color"]
            pygame.draw.rect(s, (30, 30, 38), r)
            if val > 0:
                bw = max(2, int((r.w - 22) * val / top))
                bar = pygame.Surface((bw, r.h), pygame.SRCALPHA)
                bar.fill((*[int(c * 0.75) for c in col], 220))
                s.blit(bar, (r.x + 22, r.y))
            s.blit(si.class_icon(u.member.cls, r.h), (r.x, r.y))
            if r.collidepoint(mp):
                pygame.draw.rect(s, WHITE, r, 1)
            txt = f"{u.member.name} - {self.rc_value_text(val, rate)}"
            if u.downed:
                txt += L("  (down)", "  (caído)")
            s.blit(f.render(txt, True, (0, 0, 0)), (r.x + 28, r.y + 5))
            s.blit(f.render(txt, True, WHITE if not u.downed else (190, 190, 190)), (r.x + 27, r.y + 4))
            self.recount_rows.append((r, u))

    def rc_entry_icon(self, u, name, size):
        """Ícone de uma linha do detalhamento: habilidade, fonte de cura ou inimigo."""
        if self.rc_mode == 1:
            kind, color = self.taken_kind.get(name, ("javali", (150, 150, 150)))
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (40, 30, 34), surf.get_rect(), border_radius=4)
            spr = enemy_sprite(kind, max(4, size // 3), color)
            surf.blit(spr, spr.get_rect(center=(size / 2, size / 2)))
            return surf
        if name == "Regeneration":
            return si.item_icon("Warm Milk", size)
        if name == "Fish Feast":
            return si.item_icon("Fish Feast", size)
        sp = {sk.name: sk.spec for sk in u.skills}.get(name)
        return si.active_icon(sp, size) if sp else si.item_icon("?", size)

    def draw_recount_breakdown(self, u, mp):
        """Detalhamento do membro na categoria atual (habilidades, ou inimigos no dano recebido)."""
        s = self.screen
        title, _, rate = self.RC_MODES[self.rc_mode]
        log = self.rc_log().get(u, {})
        if self.rc_mode == 3:
            return self.draw_cc_breakdown(u, log, mp)
        total = sum(log.values())
        items = sorted(log.items(), key=lambda kv: kv[1], reverse=True)
        w, rh = 380, 24
        h = 62 + max(1, len(items)) * rh + 8
        x = max(8, min(mp[0] - w - 14, W - w - 8))
        y = max(8, min(mp[1] - h // 2, H - h - 8))
        box = pygame.Rect(x, y, w, h)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (16, 16, 24, 245), bg.get_rect(), border_radius=8)
        s.blit(bg, box)
        pygame.draw.rect(s, YELLOW, box, 1, border_radius=8)
        s.blit(si.class_icon(u.member.cls, 34), (x + 10, y + 10))
        self.text(f"{u.member.name}  ({tr(u.cls['name'])})", "normal", YELLOW, (x + 52, y + 10))
        self.text(f"{title} {total:,.0f}  ·  {total / self.fight_time():,.1f} {rate}", "small", GREY,
                  (x + 52, y + 34))
        yy = y + 58
        if not items:
            self.text({0: "No damage dealt yet", 1: "No damage taken yet", 2: "No healing done yet"}[self.rc_mode],
                      "small", GREY, (x + 14, yy + 4))
        bar_col = {0: u.cls["color"], 1: (200, 70, 70), 2: (70, 200, 100)}[self.rc_mode]
        for name, val in items:
            pct = val / total * 100 if total else 0
            bar_w = int((w - 64) * pct / 100)
            pygame.draw.rect(s, (34, 34, 44), (x + 40, yy, w - 52, rh - 4), border_radius=3)
            if bar_w > 0:
                pygame.draw.rect(s, tuple(int(c * 0.6) for c in bar_col), (x + 40, yy, bar_w, rh - 4),
                                 border_radius=3)
            s.blit(self.rc_entry_icon(u, name, rh - 4), (x + 12, yy))
            self.text(name, "small", WHITE, (x + 46, yy + 3))
            self.text(f"{val:,.0f}  ({pct:.1f}%)", "small", WHITE, (x + w - 16, yy + 3), "topright")
            yy += rh

    def draw_cc_breakdown(self, u, log, mp):
        """Controle de grupo: tempo por tipo (atordoar, congelar, lentidão...) e quais habilidades causaram."""
        s = self.screen
        total = sum(sum(d.values()) for d in log.values())
        rows = []
        for kind, d in sorted(log.items(), key=lambda kv: -sum(kv[1].values())):
            rows.append(("kind", kind, sum(d.values())))
            for name, secs in sorted(d.items(), key=lambda kv: -kv[1]):
                rows.append(("skill", name, secs))
        w = 400
        h = 62 + max(1, len(rows)) * 22 + 8
        x = max(8, min(mp[0] - w - 14, W - w - 8))
        y = max(8, min(mp[1] - h // 2, H - h - 8))
        box = pygame.Rect(x, y, w, h)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (16, 16, 24, 245), bg.get_rect(), border_radius=8)
        s.blit(bg, box)
        pygame.draw.rect(s, YELLOW, box, 1, border_radius=8)
        s.blit(si.class_icon(u.member.cls, 34), (x + 10, y + 10))
        self.text(f"{u.member.name}  ({tr(u.cls['name'])})", "normal", YELLOW, (x + 52, y + 10))
        self.text(f"Crowd Control: {total:,.1f} s", "small", GREY, (x + 52, y + 34))
        yy = y + 58
        if not rows:
            self.text("No crowd control yet", "small", GREY, (x + 14, yy + 4))
        for kind, name, secs in rows:
            if kind == "kind":
                col = self.CC_COLORS.get(name, WHITE)
                pygame.draw.circle(s, col, (x + 20, yy + 9), 6)
                self.text(name, "small", col, (x + 34, yy + 2))
                self.text(f"{secs:,.1f} s", "small", col, (x + w - 16, yy + 2), "topright")
            else:
                s.blit(self.rc_entry_icon(u, name, 16), (x + 40, yy + 1))
                self.text(name, "small", WHITE, (x + 62, yy + 2))
                self.text(f"{secs:,.1f} s", "small", GREY, (x + w - 16, yy + 2), "topright")
            yy += 22

    PARTY_ROW = 70
    MINI_SIZE = 26

    def draw_skill_slot(self, r, sk, u, small=False):
        """Ícone da habilidade com a varredura de recarga; registra o retângulo para o mouseover."""
        s = self.screen
        ic = si.active_icon(sk.spec, r.w)
        if u.downed:
            ic = ic.copy()
            ic.set_alpha(80)
        s.blit(ic, r)
        frac = 1.0 if u.downed else sk.cooldown_frac()
        if frac > 0:   # varredura escura de cima para baixo, como recarga de hotkey
            shade = pygame.Surface((r.w, max(1, int(r.h * frac))), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 165))
            s.blit(shade, r.topleft)
            if not u.downed and sk.t >= 1.0:
                self.text(f"{sk.t:.0f}", "small" if small else "normal", WHITE, r.center, "center")
        hov = r.collidepoint(pygame.mouse.get_pos())
        col = WHITE if hov else (YELLOW if frac == 0 else GREY)
        pygame.draw.rect(s, col, r, 1 if small and not hov else 2, border_radius=5 if small else 8)
        if not small:   # no painel da party o nível aparece no mouseover
            for k in range(SKILL_MAX):   # nível da habilidade na run
                pygame.draw.circle(s, YELLOW if k < sk.level else DARK, (r.x + 7 + k * 9, r.bottom + 7), 3)
        self.hover_slots.append((r, sk, u))

    def skill_tooltip(self, sk, u):
        """Linhas [(texto, cor)] com os indicadores atuais da habilidade para esse membro."""
        k = sk.kind
        cyc = sk.p("cycle")
        el = " / ".join(ELEMENTS[e]["name"] for e in cyc) if cyc else \
            ELEMENTS[sk.p("element")]["name"] if sk.p("element") in ELEMENTS else None
        head = [ARCH_NAME.get(k, k)]
        if k not in ("heal", "buff"):
            head.append("Physical" if sk.p("dmgtype") == "phys" else "Magical")
        if el:
            head.append(el)
        if sk.p("target") in TARGET_NAME:
            head.append("Target: " + TARGET_NAME[sk.p("target")])
        lines = [(f"{sk.name}   Lv {sk.level}/{SKILL_MAX}", YELLOW), (" · ".join(head), (150, 190, 255))]
        if sk.p("tags"):
            lines.append((f"Tags: {tag_list_text(sk.p('tags'), i18n.LANG)}", (120, 220, 200)))
        if sk.p("desc"):
            lines.append((sk.p("desc"), GREY))
        st = []
        if k == "heal":
            amt = (sk.p("amount", 8) + u.attr_damage(sk.p("attr", "int"))) * sk.lv_mult * u.heal_mult
            st.append(("Healing", f"{amt:.0f}"))
        elif k != "buff":
            lbl = {"cloud": "Damage per second", "aura": "Damage per tick", "orbit": "Damage per hit"}.get(k, "Damage")
            st.append((lbl, f"{sk.p('dmg', 0) * sk.lv_mult:.0f}% ({sk.damage(u):.0f})"))
            st.append(("Critical", f"{u.crit_chance:.1f}% chance · +{u.crit_dmg:.0f}% damage"))
        if k == "aura":
            st.append(("Tick interval", f"{sk.cooldown(u):.2f}s"))
        elif k != "orbit":
            st.append(("Cooldown", f"{sk.cooldown(u):.2f}s"))
        if k in ("shot", "strike", "orbit"):
            st.append(("Count", str(sk.p("count", 2 if k == "orbit" else 1) + sk.bonus)))
        elif k == "summon":
            st.append(("Count", str(sk.p("count", 1) + (sk.level >= 4))))
        if k == "thrust":
            st.append(("Range", f"{sk.radius('length', u):.0f}"))
        elif sk.p("radius"):
            st.append(("Area (radius)", f"{sk.radius(u=u):.0f}"))
        if k in ("slash", "cone") and sk.p("arc"):
            st.append(("Arc", f"{sk.p('arc'):.0f}°"))
        elif k == "thrust":
            st.append(("Width", f"{sk.p('width', 26):.0f}"))
        elif k == "shot":
            st.append(("Pierce", str(sk.p("pierce", 1) + (sk.level >= 4))))
        if k in ("shot", "summon", "orbit") and sk.p("speed"):
            st.append(("Speed", f"{sk.p('speed'):g}"))
        if k == "summon":
            st.append(("Duration", f"{sk.p('life', 7) * (1 + 0.1 * (sk.level - 1)) * u.dur_mult:.1f}s"))
        elif k == "cloud":
            st.append(("Duration", f"{sk.p('duration', 4) * u.dur_mult:.1f}s"))
        elif k == "buff":
            mult = 1 + 0.1 * (sk.level - 1)
            st.append(("Duration", f"{sk.p('duration', 5) * mult * u.dur_mult * (1 + u.eff.get('buffdur', 0) / 100):.1f}s"))
            for key, v in sk.p("effects", {}).items():
                st.append((SPECIAL_NAME.get("b_" + key, key).replace("Buff: ", "Buff ").replace(" (%)", ""),
                           f"+{v * mult * 100:.0f}%"))
        if sk.p("slow"):
            st.append(("Slow", f"{(1 - sk.p('slow')[0]) * 100:.0f}% for {sk.p('slow')[1]:g}s"))
        if sk.p("taunt"):
            st.append((L("Taunt", "Provocar"), L(f"{sk.p('taunt'):g}s - enemies hit attack {u.member.name}",
                                                 f"{sk.p('taunt'):g}s - os inimigos atingidos atacam {u.member.name}")))
        if sk.p("weaken"):
            st.append((L("Weaken", "Enfraquecer"), L(f"+{sk.p('weaken'):g}% damage taken for 4s",
                                                     f"+{sk.p('weaken'):g}% de dano recebido por 4s")))
        for key, unit_txt in (("stun", "s"), ("pull", ""), ("explode", " radius"), ("homing", "")):
            if sk.p(key):
                st.append((SPECIAL_NAME[key].split(" (")[0], f"{sk.p(key):g}{unit_txt}"))
        lines += [(f"{a}:  {b}", WHITE) for a, b in st]
        if u.downed:
            lines.append(("Unavailable - member is down", RED))
        elif k in ("orbit", "aura"):
            lines.append(("Always active", GREEN))
        elif sk.cooldown_frac() > 0:
            lines.append((f"Recharging - {max(0.0, sk.t):.1f}s left", (255, 170, 80)))
        else:
            lines.append(("Ready", GREEN))
        lines.append((f"Used by {u.member.name} ({tr(u.cls['name'])})", GREY))
        return lines

    def draw_tooltip(self, lines, pos):
        """Caixa de dica perto do mouse; a 1ª linha é o título."""
        f_small, max_w = self.fonts["small"], 340
        rendered = []
        for i, (txt, col) in enumerate(lines):
            f = self.fonts["normal"] if i == 0 else f_small
            words, cur = tr(txt).split(" "), ""
            for wd in words:
                test = (cur + " " + wd).strip()
                if f.size(test)[0] > max_w and cur:
                    rendered.append(f.render(cur, True, col))
                    cur = wd
                else:
                    cur = test
            rendered.append(f.render(cur, True, col))
        w = max(r.get_width() for r in rendered) + 24
        h = sum(r.get_height() + 4 for r in rendered) + 16
        x = min(pos[0] + 18, W - w - 8)
        y = pos[1] + 18 if pos[1] + 18 + h < H - 8 else pos[1] - h - 10
        box = pygame.Rect(x, max(8, y), w, h)
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (18, 18, 26, 240), bg.get_rect(), border_radius=8)
        self.screen.blit(bg, box)
        pygame.draw.rect(self.screen, YELLOW, box, 1, border_radius=8)
        yy = box.y + 8
        for r in rendered:
            self.screen.blit(r, (box.x + 12, yy))
            yy += r.get_height() + 4

    def draw_hotbar(self):
        """Barra estilo atalhos: ícones das habilidades do herói com a recarga em tempo real."""
        if self.state == "pause":   # o pause já lista as habilidades e usa o rodapé
            return
        s = self.screen
        n, sz, gap = self.HOT_SLOTS, self.HOT_SIZE, self.HOT_GAP
        total = n * sz + (n - 1) * gap
        x0, y0 = W / 2 - total / 2, H - sz - 22
        back = pygame.Rect(x0 - 10, y0 - 10, total + 20, sz + 28)
        surf = pygame.Surface(back.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (12, 12, 18, 190), surf.get_rect(), border_radius=10)
        s.blit(surf, back)
        # esquiva: ícone separado à esquerda das hotkeys
        dr = pygame.Rect(x0 - 10 - 26 - sz, y0, sz, sz)
        bg = pygame.Surface((sz + 20, sz + 46), pygame.SRCALPHA)
        pygame.draw.rect(bg, (12, 12, 18, 190), bg.get_rect(), border_radius=10)
        s.blit(bg, (dr.x - 10, dr.y - 22))
        self.dodge.draw_slot(self, dr)
        for i in range(n):
            r = pygame.Rect(x0 + i * (sz + gap), y0, sz, sz)
            if i < len(self.hero.skills):
                self.draw_skill_slot(r, self.hero.skills[i], self.hero)
            else:
                pygame.draw.rect(s, (40, 40, 52), r, border_radius=8)
                pygame.draw.rect(s, (70, 70, 85), r, 1, border_radius=8)
            self.text(str(i + 1), "small", GREY, (r.x + 4, r.y + 2))

    def draw_levelup(self):
        s = self.screen
        s.blit(self.overlay, (0, 0))
        self.text("LEVEL UP!", "big", YELLOW, (W / 2, H / 2 - 120), "center")
        mouse = self.app.mouse_pos()
        for i, (r, opt) in enumerate(zip(self.card_rects(), self.options)):
            title, desc, color = self.option_text(opt)
            hover = r.collidepoint(mouse)
            pygame.draw.rect(s, (55, 55, 75) if hover else DARK, r, border_radius=12)
            pygame.draw.rect(s, color, r, 3, border_radius=12)
            self.text(f"[{i + 1}]", "normal", GREY, (r.x + 14, r.y + 12))
            kind, obj = opt
            if kind == "up":
                ic = si.active_icon(obj.spec, 48)
            elif kind in ("new", "relic"):
                ic = si.active_icon(obj, 48)
            elif kind == "pas":
                ic = si.item_icon(obj, 48)
            elif kind == "pup":
                ic = si.passive_icon(self.hero.pas_specs[obj], 48)
            elif kind == "gold":
                ic = pw.icon("gold", 48)
            elif kind == "power":
                ic = si.item_icon("Mystery Box", 48)
            else:
                ic = si.item_icon("Fish Feast", 48)
            ir = ic.get_rect(center=(r.centerx, r.y + 46))
            s.blit(ic, ir)
            if kind == "up":
                self.hover_slots.append((ir.inflate(8, 8), obj, self.hero))
            elif kind in ("new", "relic"):
                self.hover_slots.append((ir.inflate(8, 8), Skill(obj), self.hero))
            self.text(title, "normal", color, (r.centerx, r.y + 96), "center")
            for li, ln in enumerate(self.wrap_lines(desc, r.w - 24)[:3]):
                self.text(ln, "small", WHITE, (r.centerx, r.y + 122 + li * 17), "center")
        self.text("Allies improve on their own every level.", "small", GREY, (W / 2, H / 2 + 150), "center")
        # caixa para automatizar a escolha até o fim da run: com tudo melhorado, repete a minha escolha
        # (cura/gold/power-up); antes disso, sorteia os próximos level ups
        ex = self.exhausted()
        armed = self.auto_arm if ex else self.rand_arm
        r = self.auto_rect()
        hot = r.collidepoint(mouse)
        box = pygame.Rect(r.x + 10, r.centery - 9, 18, 18)
        pygame.draw.rect(s, (55, 55, 75) if hot else DARK, r, border_radius=8)
        pygame.draw.rect(s, YELLOW if armed else GREY, r, 2 if armed else 1, border_radius=8)
        pygame.draw.rect(s, WHITE, box, 2, border_radius=3)
        if armed:
            pygame.draw.lines(s, YELLOW, False, [(box.x + 3, box.centery), (box.x + 8, box.bottom - 4),
                                                 (box.right - 3, box.y + 3)], 3)
        lab = ("[A] Pick my choice automatically on every next level-up of this run" if ex else
               L("[A] Pick the next level-ups of this run at random", "[A] Escolher ao acaso os próximos level ups desta run"))
        self.text(lab, "small", WHITE if armed else GREY, (box.right + 10, r.centery), "midleft")

    def draw_results(self):
        s = self.screen
        s.blit(self.overlay, (0, 0))
        s.blit(self.overlay, (0, 0))   # mais escuro que o pause: o resumo fica legível sobre o mapa
        res = self.result
        title, col = ("STAGE CLEAR!", GREEN) if res["victory"] else ("RUN OVER", RED)
        if res.get("dungeon") and res["victory"]:
            title = L("DUNGEON CLEAR!", "MASMORRA CONCLUÍDA!")
        self.text(f"{title}  —  {tr(res['stage'])}", "big", col, (W / 2, 70), "center")
        dr = res.get("dres")
        if dr:   # recompensa da masmorra e próximo nível
            parts = []
            if dr.get("gold"):
                parts.append(L(f"+{dr['gold']} gold", f"+{dr['gold']} de gold"))
            if dr.get("frags"):
                parts.append(L(f"+{dr['frags']} class fragments", f"+{dr['frags']} fragmentos de classe"))
            af = res.get("accfrags") or {}
            if af:
                parts.append(L("accessory fragments: ", "fragmentos de acessório: ") + ", ".join(
                    f"{accm.cat_name(c, i18n.LANG)} x{n}" for c, n in af.items()))
            did, lv = res["dungeon"]
            nxt = (L(f"  ·  {dgm.name(did)} Lv {dr['next']} unlocked!", f"  ·  {dgm.name(did, 'pt')} Nv {dr['next']} "
                     "liberado!") if dr.get("next") else "")
            self.text(L("Clear reward: ", "Recompensa: ") + "  ·  ".join(parts) + nxt, "normal", GREEN, (W / 2, 114),
                      "center")
        if res.get("unlocked"):
            self.text(f"New stage unlocked: {res['unlocked']}", "normal", GREEN, (W / 2, 114), "center")
        if res.get("endless"):
            bm, bs = divmod(int(res.get("best", 0)), 60)
            txt = L(f"Tier reached: {res['tier'] + 1}   ·   Best time: {bm:02d}:{bs:02d}",
                    f"Dificuldade alcançada: {res['tier'] + 1}   ·   Melhor tempo: {bm:02d}:{bs:02d}")
            if res.get("new_best"):
                txt += L("   ·   NEW RECORD!", "   ·   NOVO RECORDE!")
            self.text(txt, "normal", (255, 150, 120), (W / 2, 114), "center")
        if res.get("rift"):   # Endless Rift: nível e fragmentos de acessório
            lv, top = res["rift"]
            rt = L(f"Rift Lv {lv}  ·  highest unlocked: Lv {top}", f"Fenda Nv {lv}  ·  maior liberado: Nv {top}")
            af = res.get("accfrags") or {}
            if af:
                rt += L("  ·  accessory fragments: ", "  ·  fragmentos de acessório: ") + ", ".join(
                    f"{accm.cat_name(c, i18n.LANG)} x{n}" for c, n in af.items())
            self.text(rt, "small", rift.COLOR, (W / 2, 132), "center")
        if res.get("trophies"):
            busy = res.get("unlocked") or res.get("endless")
            ttxt = L("Trophy obtained: ", "Troféu obtido: ") + ", ".join(
                trophy.name(t, i18n.LANG) for t in res["trophies"]) + L("  —  equip it at the Altar of Trophies",
                                                                        "  —  equipe no Altar dos Troféus")
            ty = 168 if res.get("rift") else 132 if busy else 114
            self.text(ttxt, "small" if busy else "normal", (255, 215, 120), (W / 2, ty), "center")
        m, sec = divmod(int(res["time"]), 60)
        self.text(f"Time {m:02d}:{sec:02d}   ·   Run level {res['level']}   ·   Kills {res['kills']}   ·   "
                  f"Elite kills {res.get('elite_kills', 0)}", "normal", WHITE, (W / 2, 150), "center")
        y = 240
        if res.get("fragments"):
            ftxt = "Fragments: " + ", ".join(f"{tr(CLASSES[c]['name'])} x{prog.fmt_frag(n)}"
                                             for c, n in res["fragments"].items())
            lines = self.wrap_lines(ftxt, W - 80)
            if len(lines) > 3:
                lines = lines[:3]
                lines[2] += " ..."
            for li, ln in enumerate(lines):
                self.text(ln, "small", (230, 170, 255), (W / 2, 214 + li * 16), "center")
            y = 236 + 16 * len(lines)
        if res.get("accs"):   # acessórios dropados nesta run
            lang = i18n.LANG
            cnt = {}
            for a, new in res["accs"]:
                k = (a, new)
                cnt[k] = cnt.get(k, 0) + 1
            items = [accm.name(a, lang) + (f" x{n}" if n > 1 else "") + ("" if new else L(" (duplicate)", " (repetido)"))
                     for (a, new), n in cnt.items()]
            lines = self.wrap_lines(L("Accessories: ", "Acessórios: ") + ", ".join(items), W - 80)
            if len(lines) > 2:
                lines = lines[:2]
                lines[1] += " ..."
            for ln in lines:
                self.text(ln, "small", (120, 220, 230), (W / 2, y - 6), "center")
                y += 16
        if res.get("mats"):   # materiais dos monstros (para a roupa, calça e bota do ferreiro)
            lang = i18n.LANG
            items = [f"{crf.mat_name(m, lang)} x{n}" for m, n in sorted(res["mats"].items(), key=lambda kv: -kv[1])]
            lines = self.wrap_lines(L("Materials: ", "Materiais: ") + ", ".join(items), W - 80)
            if len(lines) > 2:
                lines = lines[:2]
                lines[1] += " ..."
            for ln in lines:
                self.text(ln, "small", (225, 190, 140), (W / 2, y - 6), "center")
                y += 16
        gtxt = f"+{res['gold']} gold" + ("" if res["victory"] or res.get("dungeon") else
                                         f" ({int(res['gold_frac'] * 100)}% of the stage time)")
        if res.get("gold_drops"):
            gtxt += f"  ·  +{res['gold_drops']} gold from drops"
        if res.get("dungeon"):   # masmorras: sem gold de fase (a recompensa aparece na linha de cima)
            gtxt = f"+{res['gold_drops']} gold from drops"
        self.text(f"Each party member gained {res['exp']} EXP   ·   {gtxt}   ·   total: {res['total_gold']}",
                  "normal", YELLOW, (W / 2, 190), "center")

        for rep in res["reports"]:
            box = pygame.Rect(W / 2 - 420, y, 840, 72)
            pygame.draw.rect(s, PANEL, box, border_radius=10)
            c = CLASSES[rep["cls"]]
            draw_class_icon(s, rep["cls"], (box.x + 34, box.centery + 2), 17, who=rep["name"], look=rep.get("look"))
            self.text(rep["name"], "normal", WHITE, (box.x + 70, box.y + 12))
            lv = f"Lv {rep['lv0']}" + (f" > {rep['lv1']}" if rep["lv1"] > rep["lv0"] else "")
            self.text(lv, "normal", GREEN if rep["lv1"] > rep["lv0"] else GREY, (box.x + 70, box.y + 40))
            clv = f"{tr(c['name'])} Lv {rep['clv0']}" + (f" > {rep['clv1']}" if rep["clv1"] > rep["clv0"] else "")
            self.text(clv, "normal", GREEN if rep["clv1"] > rep["clv0"] else GREY, (box.x + 300, box.y + 12))
            extra = []
            if rep.get("mastered"):
                extra.append(f"{tr(c['name'])} MASTERED! Its skills are now available to other classes")
            if rep["unlocks"]:
                extra.append("New classes: " + ", ".join(rep["unlocks"]))
            if rep.get("new_skills"):
                extra.append("New skills: " + ", ".join(rep["new_skills"]))
            if extra:
                for li, ln in enumerate(self.wrap_lines("  ·  ".join(extra), box.right - (box.x + 300) - 12)[:2]):
                    self.text(ln, "small", YELLOW, (box.x + 300, box.y + 38 + li * 16))
            y += 78
        self.text("ENTER back to menu  ·  R new run with the same party", "normal", GREY, (W / 2, H - 22),
                  "center")
        nd = self.next_dungeon()
        if nd and not self.app.touch.enabled:   # masmorra concluída: botão para já entrar no próximo nível
            r = self.next_rect()
            hot = r.collidepoint(self.app.mouse_pos())
            pygame.draw.rect(s, (60, 60, 85) if hot else DARK, r, border_radius=10)
            pygame.draw.rect(s, GREEN, r, 2, border_radius=10)
            self.text(L(f"[N] Run next level (Lv {nd[1]})", f"[N] Ir para o próximo nível (Nv {nd[1]})"), "normal",
                      GREEN, r.center, "center")
