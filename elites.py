"""Inimigos de elite: qualquer inimigo comum pode surgir como elite de uma classe já liberada.

O elite é ~10x mais forte, usa o sprite do inimigo com o chapéu da classe, lança TODAS as habilidades
da classe contra a party e, ao morrer, solta muito mais EXP e um fragmento da classe.
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

import progression as prog
import skill_fx as sfx
from data import CLASSES, ELEMENTS, ENEMY_NAMES

ELITE_CHANCE = 0.012     # chance de um inimigo comum surgir como elite
MAX_ELITES = 3           # elites vivos ao mesmo tempo
ELITE_HP = 10.0          # multiplicadores em relação à versão normal
ELITE_DMG = 2.5          # dano de contato
ELITE_XP = 10
ELITE_SIZE = 1.4
ELITE_SPEED = 0.85
PARTY_CLASS_WEIGHT = 3   # classes da party atual têm 3x mais chance (ajuda a focar o farm, sem tirar a variedade)
SKILL_RANGE = 460        # alcance para começar a lançar habilidades
CD_MULT = 1.8            # elites lançam as habilidades mais devagar que os heróis

# Eventos de minuto: a cada minuto da run surge um Super Elite OU um Esquadrão de Elite
EVENT_INTERVAL = 60.0
# tier: (vida x, dano de contato x, dano das habilidades x, tamanho x, EXP x, recarga x, fragmentos, defesas x)
TIERS = {
    "normal": (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1, 1.0),
    "super": (10.0, 2.0, 2.2, 1.35, 5.0, 0.75, 10, 1.5),   # 10x mais forte que um elite comum
    "squad": (2.0, 1.4, 1.4, 1.1, 1.5, 0.9, 2, 1.2),       # 5 elites, 2x mais fortes que um elite comum
}
SQUAD_SIZE = 5
# Chefão: carrega 2 classes aleatórias (armas e habilidades das duas) e é bem mais forte
BOSS_HP = 3.0
BOSS_DMG = 1.6
BOSS_SKILL = 2.0
BOSS_FRAGS = 5           # fragmentos de CADA uma das duas classes


def class_pool(roster):
    """Classes que já foram liberadas por qualquer personagem."""
    pool = set()
    for m in roster.members:
        pool.update(m.unlocked_classes())
    return sorted(pool)


def pick_class(pool, party_classes):
    """Sorteia a classe do elite entre as liberadas; as classes da party atual pesam mais."""
    weights = [PARTY_CLASS_WEIGHT if c in party_classes else 1 for c in pool]
    return random.choices(pool, weights)[0]


def make_elite(e, cid, tier="normal"):
    """Transforma um inimigo comum em elite da classe cid (tier: normal, super ou squad)."""
    hp_m, dmg_m, sk_m, size_m, xp_m, cd_m, frags, res_m = TIERS[tier]
    c = CLASSES[cid]
    e.elite = cid
    e.tier = tier
    prefix = "Super " if tier == "super" else ""
    e.name = f"{prefix}{c['name']} {ENEMY_NAMES.get(e.kind, e.kind)}"   # padrão [Classe] [Monstro]
    e.hp *= ELITE_HP * hp_m
    e.max_hp = e.hp
    e.base_dmg = e.dmg
    e.dmg *= ELITE_DMG * dmg_m
    e.armor *= 2 * res_m
    e.mres *= 2 * res_m
    e.r = int(e.r * ELITE_SIZE * size_m)
    e.speed *= ELITE_SPEED
    e.base_speed = e.speed
    e.xp *= ELITE_XP * xp_m
    e.buff_t = 0.0
    e.skill_mult = sk_m
    e.cd_mult = cd_m
    e.frags = {cid: frags}
    cc = prog.CONTENT.get(cid, {})
    specs = [cc.get("basic")] + list(cc.get("actives", []))
    e.casts = [[sp, random.uniform(1.0, 4.0)] for sp in specs if sp]


def make_boss(e, cids):
    """Chefão com 2 classes: usa as habilidades das duas, carrega as duas armas e solta fragmentos de ambas."""
    e.boss_classes = list(cids)
    e.hp *= BOSS_HP
    e.max_hp = e.hp
    e.base_dmg = e.dmg
    e.dmg *= BOSS_DMG
    e.base_speed = e.speed
    e.buff_t = 0.0
    e.skill_mult = BOSS_SKILL
    e.cd_mult = 1.0
    e.frags = {c: BOSS_FRAGS for c in cids}
    e.casts = []
    for cid in cids:   # golpe básico + 3 ativas sorteadas de cada classe
        cc = prog.CONTENT.get(cid, {})
        acts = [sp for sp in cc.get("actives", []) if sp]
        for sp in [cc.get("basic")] + random.sample(acts, min(3, len(acts))):
            if sp:
                e.casts.append([sp, random.uniform(2.0, 6.0)])


def caster_class(e, sp=None):
    """Classe usada para cor/tipo de dano de uma habilidade hostil (elite ou chefão)."""
    if sp is not None and sp.get("cid") in CLASSES:
        return sp["cid"]
    if getattr(e, "elite", None):
        return e.elite
    return (getattr(e, "boss_classes", None) or ["freelancer"])[0]


def pick_classes(pool, party_classes, n):
    """n classes diferentes (quando possível), com o mesmo peso das classes da party."""
    out = []
    for _ in range(n):
        rest = [c for c in pool if c not in out] or list(pool)
        out.append(pick_class(rest, party_classes))
    return out


# ---------------------------------------------------------------------------
# Efeitos hostis (atingem a party)
# ---------------------------------------------------------------------------
class HostileShot:
    def __init__(self, pos, vel, dmg, r, life, src, name, color):
        self.pos, self.vel, self.dmg, self.r, self.life = V(pos), V(vel), dmg, r, life
        self.src, self.name, self.color = src, name, color


class HostileZone:
    """Área marcada no chão: espera 'delay' e então causa dano (uma vez) ou vira nuvem (dps)."""

    def __init__(self, pos, radius, dmg, delay, src, name, color, linger=0.0):
        self.pos, self.r, self.dmg, self.t, self.delay = V(pos), radius, dmg, delay, delay
        self.src, self.name, self.color, self.linger = src, name, color, linger
        self.tick = 0.0


def _skill_dmg(e, sp):
    """Dano de uma habilidade do elite: escala com o dano base do inimigo e com a força da habilidade."""
    # o "dmg" das habilidades é % do dano do personagem: 100% ~ força 1 (o elite não usa os atributos)
    power = sp.get("dmg") / 100 if sp.get("dmg") else (sp.get("amount", 14) or 14) / 14
    mult = 1.3 if e.buff_t > 0 else 1.0
    return e.base_dmg * 1.6 * max(0.6, min(4.0, power)) * mult * getattr(e, "skill_mult", 1.0)


def _color(e, sp):
    el = sp.get("element") or (sp.get("cycle") or [None])[0]
    return ELEMENTS[el]["color"] if el in ELEMENTS else CLASSES[caster_class(e, sp)]["color"]


def cast(run, e, sp, targets):
    """Lança a habilidade sp do elite. Retorna True se foi usada."""
    k = sp["kind"]
    near = min(targets, key=lambda u: (u.pos - e.pos).length_squared())
    dist = (near.pos - e.pos).length()
    name = e.name
    col = _color(e, sp)
    if k == "heal":
        if e.hp >= e.max_hp * 0.9:
            return False
        e.hp = min(e.max_hp, e.hp + e.max_hp * 0.08)
        run.fx_ring(e.pos, e.r + 12, (110, 230, 120))
        return True
    if k == "buff":
        e.buff_t = max(e.buff_t, sp.get("duration", 5))
        e.speed = e.base_speed * 1.25
        run.fx_ring(e.pos, e.r + 14, (250, 210, 70))
        return True
    if k == "summon":
        if len(run.enemies) >= run.max_enemies:
            return False
        for i in range(min(3, sp.get("count", 1) + 1)):
            a = random.uniform(0, math.tau)
            run.enemies.append(run.new_enemy(getattr(e, "base_kind", e.kind), e.pos + V(math.cos(a), math.sin(a)) * (e.r + 30), allow_elite=False))
        run.fx_ring(e.pos, e.r + 20, col)
        return True
    dmg = _skill_dmg(e, sp)
    if k == "shot":
        if dist > SKILL_RANGE:
            return False
        base = (near.pos - e.pos)
        base = base.normalize() if base.length_squared() > 1e-6 else V(1, 0)
        n = min(5, sp.get("count", 1))
        spread = sp.get("spread", 12)
        speed = max(220, sp.get("speed", 450) * 0.55)
        for i in range(n):
            d = base.rotate((i - (n - 1) / 2) * spread)
            run.hostile_shots.append(HostileShot(e.pos, d * speed, dmg, max(6, sp.get("size", 6) + 2), 2.6,
                                                 e, name, col))
            run.hostile_shots[-1].look = sfx.look_for(sp)   # mesmo visual da habilidade da classe
        return True
    if k == "cloud":
        if dist > SKILL_RANGE:
            return False
        r = sp.get("radius", 90)
        run.hostile_zones.append(HostileZone(near.pos, r, dmg * 0.5, 0.8, e, name, col,
                                             linger=sp.get("duration", 4)))
        run.hostile_zones[-1].look = sfx.look_for(sp)
        return True
    if k == "strike" and sp.get("target") in ("nearest", "random"):
        if dist > SKILL_RANGE:
            return False
        pool = [u for u in targets if (u.pos - e.pos).length() <= SKILL_RANGE] or [near]
        n = min(3, sp.get("count", 1))
        r = max(50, sp.get("radius", 60))
        delay = 0.8 + sp.get("delay", 0)
        for u in random.sample(pool, min(n, len(pool))):
            run.hostile_zones.append(HostileZone(u.pos, r, dmg, delay, e, name, col))
            run.hostile_zones[-1].look = sfx.look_for(sp)
        return True
    # golpes, cones, estocadas, auras, órbitas e impactos em si mesmo: área ao redor do elite
    r = sp.get("length") or sp.get("radius") or 90
    r = max(70, min(220, r)) + e.r
    if dist > r + near.r:
        return False
    z = HostileZone(e.pos, r, dmg, 0.55, e, name, col)
    z.around = bool(getattr(e, "boss", False))   # área ao redor do chefão: sem anel vermelho, desenhada por baixo
    lk = sfx.look_for(sp)
    if k in ("slash", "thrust", "aura", "orbit") or lk.get("impact") in ("hit",):
        lk = dict(lk, impact="cut" if (lk.get("cut") or k in ("slash", "thrust")) and not lk.get("el") else
                  ("fist" if not lk.get("el") else sfx._EL_IMPACT.get(lk.get("el"), "hit")))
    z.look = lk
    run.hostile_zones.append(z)
    return True


def update_elite(run, e, dt, targets):
    if e.buff_t > 0:
        e.buff_t -= dt
        if e.buff_t <= 0:
            e.speed = e.base_speed
    if not targets or e.stun_t > 0:
        return
    for c in e.casts:
        c[1] -= dt
        if c[1] <= 0:
            sp = c[0]
            if cast(run, e, sp, targets):
                c[1] = max(1.2, sp.get("cd", 2.0) * CD_MULT * getattr(e, "cd_mult", 1.0))
            else:
                c[1] = 0.6


def update_hostiles(run, dt, targets):
    keep = []
    for sh in run.hostile_shots:
        sh.pos += sh.vel * dt
        sh.life -= dt
        for u in targets:
            if (u.pos - sh.pos).length_squared() < (u.r + sh.r) ** 2:
                run.hostile_hit(u, sh.dmg, sh.src, sh.name, fx=getattr(sh, "fx", None), push=sh.vel)
                sh.life = 0
                break
        if sh.life > 0:
            keep.append(sh)
    run.hostile_shots = keep
    keep = []
    for z in run.hostile_zones:
        if z.t > 0:
            z.t -= dt
            if z.t <= 0:
                for u in targets:
                    if zone_hits(z, u):
                        run.hostile_hit(u, z.dmg, z.src, z.name, fx=getattr(z, "fx", None))
                release_fx(run, z)
                if z.linger <= 0:
                    continue
            keep.append(z)
        else:
            z.linger -= dt
            z.tick -= dt
            if z.tick <= 0:
                z.tick = 0.5
                for u in targets:
                    if zone_hits(z, u):
                        run.hostile_hit(u, z.dmg, z.src, z.name, fx=getattr(z, "fx", None))
            if z.linger > 0:
                keep.append(z)
    run.hostile_zones = keep
    for ln in getattr(run, "hostile_lines", []):   # avisos de investida somem sozinhos
        ln[3] -= dt
    if getattr(run, "hostile_lines", None):
        run.hostile_lines = [ln for ln in run.hostile_lines if ln[3] > 0]


def release_fx(run, z):
    """Animação do golpe quando a área marcada dispara (mesmo raio/cone da área de dano)."""
    from skills import Fx
    lk = getattr(z, "look", None)
    cone = getattr(z, "cone", None)
    if lk is None:
        if cone is None:
            run.fx_ring(z.pos, z.r, z.color)
        return
    if cone is not None:
        fwd, arc = cone
        run.fx.append(Fx("anim", z.pos, 0.32, frames=sfx.cone(lk, z.r, arc, math.degrees(math.atan2(fwd.y, fwd.x)))))
        return
    if z.linger > 0 and lk.get("impact") in ("poison", "smoke", "hit"):
        return   # poças: a própria poça animada já aparece
    run.fx.append(Fx("anim", z.pos, 0.36, frames=sfx.impact(lk, z.r)))


def zone_hits(z, u):
    """A unidade está dentro da área (círculo ou cone)?"""
    d = u.pos - z.pos
    if d.length_squared() >= (z.r + u.r) ** 2:
        return False
    cone = getattr(z, "cone", None)
    if cone is None or d.length_squared() < 1:
        return True
    fwd, arc = cone
    diff = (fwd.angle_to(d) + 180) % 360 - 180
    return abs(diff) <= arc / 2 + 8


def _cone_pts(c, fwd, r, arc, frac=1.0):
    pts = [c]
    for k in range(13):
        a = -arc / 2 + arc * k / 12
        pts.append(c + fwd.rotate(a) * r * frac)
    return pts


def draw_hostiles(run, s, cam, under=False):
    """under=True: só as áreas ao redor dos chefões (por baixo dos inimigos, sem vermelho)."""
    for z in run.hostile_zones:
        if getattr(z, "around", False) != under:
            continue
        p = z.pos - cam
        cone = getattr(z, "cone", None)
        if cone is not None and not under:   # golpe em cone (sonar do morcego): leque que vai se enchendo
            size = int(z.r * 2 + 4)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            c = V(size / 2, size / 2)
            frac = 1 - max(0.0, z.t) / z.delay if z.delay else 1.0
            pygame.draw.polygon(surf, (230, 50, 50, 55), _cone_pts(c, cone[0], z.r, cone[1]))
            pygame.draw.polygon(surf, (*z.color, 120), _cone_pts(c, cone[0], z.r, cone[1], max(0.1, frac)))
            pygame.draw.polygon(surf, (240, 60, 60, 220), _cone_pts(c, cone[0], z.r, cone[1]), 2)
            s.blit(surf, (p.x - c.x, p.y - c.y))
            continue
        if under:   # aviso discreto na cor da habilidade, sem círculo vermelho por cima do chefão
            size = int(z.r * 2 + 4)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            c = (size / 2, size / 2)
            if z.t > 0:
                frac = 1 - z.t / z.delay
                pygame.draw.circle(surf, (*z.color, 45), c, max(2, z.r * frac))
                pygame.draw.circle(surf, (*z.color, 110), c, z.r, 1)
            s.blit(surf, (p.x - c[0], p.y - c[1]))
            continue
        size = int(z.r * 2 + 4)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (size / 2, size / 2)
        if z.t > 0:   # aviso: anel vermelho que vai se preenchendo
            frac = 1 - z.t / z.delay
            pygame.draw.circle(surf, (230, 50, 50, 60), c, z.r)
            pygame.draw.circle(surf, (*z.color, 120), c, max(2, z.r * frac))
            pygame.draw.circle(surf, (240, 60, 60, 230), c, z.r, 2)
        else:         # nuvem / poça persistente: animada, com a borda vermelha de perigo (mesmo raio do dano)
            lk = getattr(z, "look", None) or {}
            sfx.draw_cloud(s, p, z.r, lk.get("el") or getattr(z, "pool_el", "poison"), run.time, z.linger / 1.5,
                           seed=id(z) % 9973, name=lk.get("name", ""))
            pygame.draw.circle(surf, (230, 60, 60, 160), c, z.r, 2)
        s.blit(surf, (p.x - c[0], p.y - c[1]))
    if under:
        return
    for p0, p1, w, t, tot in getattr(run, "hostile_lines", []):   # aviso de investida: faixa que vai se enchendo
        a, b = p0 - cam, p1 - cam
        frac = 1 - t / tot if tot else 1.0
        pygame.draw.line(s, (120, 30, 30), a, b, int(w))
        pygame.draw.line(s, (240, 70, 60), a, a + (b - a) * frac, max(2, int(w * 0.5)))
        pygame.draw.circle(s, (240, 70, 60), b, int(w * 0.5), 2)
    for sh in run.hostile_shots:   # projéteis inimigos: sprite do golpe com brilho vermelho embaixo
        p = sh.pos - cam
        lk = getattr(sh, "look", None) or dict(proj="dark", el="dark")
        spr = sfx.projectile_sprite(lk, sh.r, sh.vel, run.time + (id(sh) % 97) * 0.013, hostile=True)
        s.blit(spr, (p.x - spr.get_width() / 2, p.y - spr.get_height() / 2))


# ---------------------------------------------------------------------------
# Fragmento de classe (drop)
# ---------------------------------------------------------------------------
class FragmentDrop:
    def __init__(self, pos, cid):
        self.pos, self.cid, self.age = V(pos), cid, 0.0


def draw_fragment(s, pos, cid, t, size=9):
    col = CLASSES[cid]["color"]
    bob = math.sin(t * 5) * 3
    p = V(pos) + V(0, bob)
    pts = [p + V(0, -size * 1.4), p + V(size, 0), p + V(0, size * 1.4), p + V(-size, 0)]
    glow = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*col, 70), (size * 3, size * 3), size * 3)
    s.blit(glow, (p.x - size * 3, p.y - size * 3))
    pygame.draw.polygon(s, col, pts)
    pygame.draw.polygon(s, (255, 255, 255), pts, 2)
