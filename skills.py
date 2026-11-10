"""Habilidades (ataques automáticos) e entidades que elas criam: projéteis, invocações, nuvens e efeitos visuais."""
import math
import random

import pygame
from pygame.math import Vector2 as V

from data import SKILL_MAX, WHITE, element_color
import skill_fx as sfx


def unit(v, fallback=(1, 0)):
    return v.normalize() if v.length_squared() > 1e-9 else V(fallback)


def angle_between(a, b):
    """Diferença de ângulo (graus, -180..180) entre os vetores a e b."""
    return (a.angle_to(b) + 180) % 360 - 180


# --------------------------------------------------------------------------
# Entidades criadas pelas habilidades
# --------------------------------------------------------------------------
class Projectile:
    def __init__(self, pos, vel, dmg, pierce, size=6, color=WHITE, life=1.4, homing=0.0, explode=0.0,
                 element=None, slow=None, stun=None, knock=140, dmgtype="phys", src=None, sk=None):
        self.pos = V(pos)
        self.vel = V(vel)
        self.dmg = dmg
        self.pierce = pierce
        self.r = size
        self.color = color
        self.life = life
        self.homing = homing
        self.explode = explode
        self.element = element
        self.slow = slow
        self.stun = stun
        self.knock = knock
        self.dmgtype = dmgtype
        self.src = src
        self.sk = sk          # nome da habilidade (para o medidor de dano)
        self.hit = set()


class Minion:
    """Invocação: persegue inimigos e causa dano por contato."""

    def __init__(self, pos, dmg, life, speed, size, color, element):
        self.pos = V(pos)
        self.dmg = dmg
        self.life = life
        self.speed = speed
        self.r = size
        self.color = color
        self.element = element
        self.dmgtype = "phys"
        self.cool = {}


class Cloud:
    """Área persistente que causa dano por segundo."""

    def __init__(self, pos, radius, dps, duration, element):
        self.pos = V(pos)
        self.r = radius
        self.dps = dps
        self.life = duration
        self.max_life = duration
        self.element = element
        self.dmgtype = "mag"
        self.tick = 0.0


class Fx:
    """Efeito visual de curta duração."""

    def __init__(self, kind, pos, life=0.2, **kw):
        self.kind = kind
        self.pos = V(pos)
        self.life = life
        self.max_life = life
        self.kw = kw

    def draw(self, s, cam):
        k = self.kw
        p = self.pos - cam
        t = max(0.0, self.life / self.max_life)
        col = k.get("color", WHITE)
        if self.kind == "anim":   # animação em pixel art (skill_fx): quadros já no tamanho da área do golpe
            sfx.blit_anim(s, k["frames"], 1 - t, p)
        elif self.kind == "ring":
            r = k["radius"] * (1.15 - 0.15 * t) if k.get("grow") else k["radius"]
            pygame.draw.circle(s, col, p, max(2, int(r)), max(1, int(4 * t) + 1))
        elif self.kind == "arc":
            r, arc, d = k["radius"], k["arc"], k["dir"]
            if arc >= 360:
                pygame.draw.circle(s, col, p, int(r), 3)
            else:
                pts = [p]
                steps = 10
                for i in range(steps + 1):
                    a = -arc / 2 + arc * i / steps
                    pts.append(p + d.rotate(a) * r)
                pygame.draw.polygon(s, col, pts, 2)
                pygame.draw.lines(s, WHITE, False, pts[1:], 2)
        elif self.kind == "line":
            end = k["end"] - cam
            pygame.draw.line(s, col, p, end, max(2, int(k["width"] * t)))
        elif self.kind == "cone":
            r, arc, d = k["radius"], k["arc"], k["dir"]
            size = int(r * 2 + 4)
            c = V(size / 2, size / 2)
            pts = [c] + [c + d.rotate(-arc / 2 + arc * i / 8) * r for i in range(9)]
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (*col, int(130 * t)), pts)
            pygame.draw.polygon(surf, (*col, 220), pts, 2)
            s.blit(surf, p - c)
        elif self.kind == "bolt":
            pts, y = [], -10.0
            while y < p.y:
                pts.append((p.x + random.uniform(-14, 14), y))
                y += max(20.0, (p.y + 10) / 8)
            pts.append(tuple(p))
            if len(pts) >= 2:
                pygame.draw.lines(s, col, False, pts, 3)
        elif self.kind == "telegraph":
            r = k["radius"]
            pygame.draw.circle(s, col, p, int(r), 2)
            pygame.draw.circle(s, col, p, max(2, int(r * (1 - t))), 0)
        elif self.kind == "text":
            pass


# --------------------------------------------------------------------------
# Habilidade
# --------------------------------------------------------------------------
class Skill:
    def __init__(self, spec):
        self.spec = spec
        self.kind = spec["kind"]
        self.name = spec["name"]
        self.look = sfx.look_for(spec)   # visual da habilidade (projétil, impacto, golpe...)
        self.level = 1
        self.t = random.uniform(0.1, 0.6)
        self.cycle_i = 0
        self.cd_total = 0.0     # duração da última recarga (para a barra de habilidades)
        self.waiting = True     # pronta, esperando um alvo
        self.angle = 0.0
        self.cool = {}

    def p(self, key, default=None):
        return self.spec.get(key, default)

    # ---------- escalonamento por nível (dentro da partida) ----------
    @property
    def lv_mult(self):
        return 1 + 0.25 * (self.level - 1)

    @property
    def bonus(self):
        return (self.level >= 3) + (self.level >= 5)

    def cooldown(self, u):
        return self.p("cd", 1.0) * (1 - 0.06 * (self.level - 1)) * u.haste_mult(self.p("tags", ()))

    def radius(self, key="radius", u=None):
        """Tamanho de uma área (raio de impacto, aura, explosão...): escala com Área."""
        return self.p(key, 0) * (1 + 0.08 * (self.level - 1)) * (u.area if u is not None else 1.0)

    def reach(self, key="radius", u=None):
        """Alcance de um golpe corpo a corpo (raio do arco/cone, comprimento da estocada): escala com Alcance."""
        return self.p(key, 0) * (1 + 0.08 * (self.level - 1)) * (getattr(u, "range", 1.0) if u is not None else 1.0)

    def widen(self, val, u):
        """Largura/ângulo de um golpe: escala com Área (ângulo máximo 360°)."""
        return min(360.0, val * (u.area if u is not None else 1.0)) if val < 360 else val

    def damage(self, u):
        """% do dano do personagem (FOR+AGI+INT) x nível na partida x bônus %."""
        cd_ = getattr(u, "char_damage", None)
        base = self.p("dmg", 0) / 100 * (cd_() if cd_ else 15)
        return base * self.lv_mult * u.power(self.p("dmgtype", "mag"))

    def element(self):
        cyc = self.p("cycle")
        if cyc:
            return cyc[self.cycle_i % len(cyc)]
        return self.p("element")

    def color(self):
        return element_color(self.element(), self.p("color", WHITE))

    def hit_kw(self, u=None):
        return dict(slow=self.p("slow"), stun=self.p("stun"), knock=self.p("knock", 100),
                    dmgtype=self.p("dmgtype", "mag"), src=u, sk=self.name)

    # ---------- loop ----------
    def update(self, dt, run, u):
        if self.kind == "orbit":
            self.update_orbit(dt, run, u)
            return
        self.t -= dt
        if self.t > 0:
            return
        fired = getattr(self, "do_" + self.kind)(run, u)
        if fired:
            self.t = self.cd_total = self.cooldown(u)
            self.waiting = False
            echo = getattr(u, "cap", lambda n: 0)("echo")
            if echo and random.random() * 100 < echo:   # capstone Echo: recarrega na hora
                self.t = min(self.t, 0.15)
            if self.p("cycle"):
                self.cycle_i += 1
        else:
            self.t = 0.15
            self.waiting = True

    def cooldown_frac(self):
        """0 = pronta, 1 = acabou de ser usada (aura/órbita são contínuas)."""
        if self.kind in ("orbit", "aura") or self.waiting or self.cd_total <= 0:
            return 0.0
        return max(0.0, min(1.0, self.t / self.cd_total))

    def draw(self, s, run, u, cam):
        if self.kind == "orbit":   # lâminas girando / orbes (o sprite tem o tamanho da área de toque)
            for k, bp in enumerate(self.orbit_positions(u)):
                p = bp - cam
                spr = sfx.orbit_sprite(self.look, run.time, k)
                s.blit(spr, (p.x - spr.get_width() / 2, p.y - spr.get_height() / 2))
        elif self.kind == "aura":   # anel do raio exato da aura, com partículas girando
            sfx.draw_aura(s, u.pos - cam, self.radius(u=u), self.element(), run.time)

    # ---------- arquétipos ----------
    def do_shot(self, run, u):
        rng = getattr(u, "range", 1.0)
        target = run.nearest_enemy(u.pos, 700 * rng)
        if not target:
            return False
        base = unit(target.pos - u.pos)
        u.facing = base
        n = self.p("count", 1) + self.bonus
        spread = self.p("spread", 10)
        el = self.element()
        for i in range(n):
            d = base.rotate((i - (n - 1) / 2) * spread)
            run.projectiles.append(Projectile(
                u.pos, d * self.p("speed", 520), self.damage(u), self.p("pierce", 1) + (self.level >= 4),
                size=self.p("size", 6) * u.area, color=self.color(), life=self.p("life", 1.4) * rng,
                homing=self.p("homing", 0),
                explode=self.radius("explode", u), element=el, **self.hit_kw(u)))
            run.projectiles[-1].look = self.look
        return True

    def do_slash(self, run, u):
        r = self.reach(u=u)
        target = run.nearest_enemy(u.pos, r + 40)
        if not target:
            return False
        d = unit(target.pos - u.pos)
        u.facing = d
        arc = self.widen(self.p("arc", 120), u)
        dmg, el = self.damage(u), self.element()
        for e in run.enemies_near(u.pos, r):
            to = e.pos - u.pos
            if arc >= 360 or to.length_squared() < 1 or abs(angle_between(d, to)) <= arc / 2 + 10:
                run.damage(e, dmg, to, el, **self.hit_kw(u))
        ang = math.degrees(math.atan2(d.y, d.x))
        run.fx.append(Fx("anim", u.pos, 0.24, frames=sfx.swoosh(self.look, r, arc, ang, el)))
        return True

    def do_thrust(self, run, u):
        length = self.reach("length", u)
        target = run.nearest_enemy(u.pos, length + 30)
        if not target:
            return False
        d = unit(target.pos - u.pos)
        u.facing = d
        half_w = self.p("width", 26) * u.area / 2
        dmg, el = self.damage(u), self.element()
        for e in run.enemies_near(u.pos, length + 30):
            rel = e.pos - u.pos
            along = rel.dot(d)
            if -e.r < along < length + e.r and abs(rel.cross(d)) < half_w + e.r:
                run.damage(e, dmg, d, el, **self.hit_kw(u))
        ang = math.degrees(math.atan2(d.y, d.x))
        run.fx.append(Fx("anim", u.pos, 0.24, frames=sfx.thrust(self.look, length, half_w * 2, ang, el)))
        return True

    def do_strike(self, run, u):
        mode = self.p("target", "random")
        r = self.radius(u=u)
        if mode == "self":
            if not run.enemies_near(u.pos, r):
                return False
            positions = [V(u.pos)]
        elif mode == "nearest":
            n = self.p("count", 1) + self.bonus
            positions = [V(e.pos) for e in run.nearest_enemies(u.pos, n, 520 * getattr(u, "range", 1.0))]
        else:
            n = self.p("count", 1) + self.bonus
            positions = [V(e.pos) for e in run.random_visible_enemies(n)]
        if not positions:
            return False
        dmg, el = self.damage(u), self.element()
        delay = self.p("delay", 0)
        for pos in positions:
            kw = dict(self.hit_kw(u), pull=self.p("pull", 0), look=self.look)
            if delay:
                run.pending.append([delay, pos, r, dmg, el, kw])
                run.fx.append(Fx("telegraph", pos, delay, radius=r, color=self.color()))
                if self.look.get("impact") == "meteor":   # a rocha cai durante o aviso e chega junto com o dano
                    run.fx.append(Fx("anim", pos, delay, frames=sfx.falling(self.look, r, el)))
            else:
                run.explode(pos, r, dmg, el, **kw)
        return True

    def do_cone(self, run, u):
        r = self.reach(u=u)
        target = run.nearest_enemy(u.pos, r)
        if not target:
            return False
        d = unit(target.pos - u.pos)
        u.facing = d
        arc = self.widen(self.p("arc", 60), u)
        dmg, el = self.damage(u), self.element()
        for e in run.enemies_near(u.pos, r):
            to = e.pos - u.pos
            if to.length_squared() < 1 or abs(angle_between(d, to)) <= arc / 2 + 5:
                run.damage(e, dmg, to, el, **self.hit_kw(u))
        ang = math.degrees(math.atan2(d.y, d.x))
        run.fx.append(Fx("anim", u.pos, 0.32, frames=sfx.cone(self.look, r, arc, ang, el)))
        return True

    def do_aura(self, run, u):
        r = self.radius(u=u)
        dmg, el = self.damage(u), self.element()
        hit = run.enemies_near(u.pos, r)
        for e in hit:
            run.damage(e, dmg, e.pos - u.pos, el, knock=60, show=False, dmgtype=self.p("dmgtype", "mag"), src=u,
                       sk=self.name)
        if hit:   # pulso visível a cada acerto da aura (o dano não aparece "do nada")
            run.fx.append(Fx("ring", u.pos, 0.18, radius=r, color=self.color(), grow=True))
        return True

    def do_heal(self, run, u):
        r = self.radius(u=u)
        targets = [m for m in run.party if not m.downed and (m.pos - u.pos).length_squared() < r * r
                   and m.hp < m.max_hp * 0.97]
        if not targets:
            return False
        amount = (self.p("amount", 8) + u.attr_damage(self.p("attr", "int"))) * self.lv_mult * u.heal_mult
        for m in targets:
            run.heal(m, amount, src=u, sk=self.name)
        run.fx.append(Fx("ring", u.pos, 0.4, radius=r, color=(120, 240, 140), grow=True))   # alcance da cura
        return True

    def do_buff(self, run, u):
        if not run.nearest_enemy(u.pos, 600):
            return False
        if self.p("target") == "self":
            targets = [u]
        else:
            targets = [m for m in run.party if not m.downed and (m.pos - u.pos).length_squared() < 350 ** 2]
        mult = 1 + 0.1 * (self.level - 1)
        effects = {k: v * mult for k, v in self.p("effects", {}).items()}
        dur = self.p("duration", 5) * mult * u.dur_mult * (1 + u.eff.get("buffdur", 0) / 100)   # passivas de duração de buff
        for m in targets:
            m.buffs[self.name] = [effects, dur]
            run.fx.append(Fx("anim", m.pos, 0.6, frames=sfx.buff_anim(self.p("effects", {}))))
        return True

    def do_summon(self, run, u):
        if not run.nearest_enemy(u.pos, 600):
            return False
        n = self.p("count", 1) + (self.level >= 4)
        legion = 1 + getattr(u, "cap", lambda k: 0)("legion") / 100   # capstone Legion
        for _ in range(n):
            off = V(random.uniform(-20, 20), random.uniform(-20, 20))
            run.minions.append(Minion(u.pos + off, self.damage(u) * legion,
                                      self.p("life", 7) * (1 + 0.1 * (self.level - 1)) * u.dur_mult * legion,
                                      self.p("speed", 260), self.p("size", 10), self.p("color", WHITE),
                                      self.element()))
            run.minions[-1].dmgtype = self.p("dmgtype", "mag")
            run.minions[-1].src = u
            run.minions[-1].sk = self.name
        return True

    def do_cloud(self, run, u):
        target = run.nearest_enemy(u.pos, 500)
        if not target:
            return False
        run.clouds.append(Cloud(target.pos, self.radius(u=u), self.damage(u), self.p("duration", 4) * u.dur_mult,
                                self.element()))
        run.clouds[-1].dmgtype = self.p("dmgtype", "mag")
        run.clouds[-1].src = u
        run.clouds[-1].sk = self.name
        return True

    # ---------- órbita ----------
    def orbit_stats(self, u):
        return (self.p("count", 2) + self.bonus, self.radius(u=u),
                self.p("speed", 3.0) * (1 + 0.1 * (self.level - 1)))

    def orbit_positions(self, u):
        n, rad, _ = self.orbit_stats(u)
        return [u.pos + V(math.cos(self.angle + k * math.tau / n), math.sin(self.angle + k * math.tau / n)) * rad
                for k in range(n)]

    def update_orbit(self, dt, run, u):
        n, rad, spd = self.orbit_stats(u)
        self.angle += spd * dt
        dmg = self.damage(u)
        now = run.time
        for bp in self.orbit_positions(u):
            for e in run.enemies_near(bp, 20):
                if self.cool.get(e, 0) <= now and (e.pos - bp).length_squared() < (e.r + 10) ** 2:
                    self.cool[e] = now + 0.45
                    run.damage(e, dmg, e.pos - u.pos, None, knock=220, dmgtype=self.p("dmgtype", "mag"), src=u,
                               sk=self.name)
        if len(self.cool) > 600:
            self.cool = {k: v for k, v in self.cool.items() if v > now}


def describe(spec):
    """Descrição curta de uma habilidade para menus."""
    return spec["desc"]


__all__ = ["Skill", "Projectile", "Minion", "Cloud", "Fx", "SKILL_MAX", "unit", "describe"]
