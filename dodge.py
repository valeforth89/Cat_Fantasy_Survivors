"""Esquiva manual do herói (tecla ESPAÇO), na direção para onde ele está virado.

O tipo depende do atributo principal da classe atual do herói:
- FOR  -> Charge: investida de distância média que empurra (e fere um pouco) quem encostar; recarga média, 2 usos.
- AGI  -> Dodge: movimento rápido e longo que atravessa os inimigos (invulnerável); recarga curta, 1 uso.
- INT  -> Blink: teleporte longo; ao aparecer, causa um impacto em 360° que empurra os inimigos; recarga longa, 1 uso.
- Equilibrado (Novice, Freelancer, Warfarer) -> Dodge.
Só o herói tem esquiva.
"""
import math

import pygame
from pygame.math import Vector2 as V

import skill_icons as si

# nome EN, nome PT, símbolo do ícone, cor do ícone, distância, duração do movimento, recarga, usos
DODGES = {
    "charge": dict(name=("Charge", "Investida"), icon="shield+up", bg=(150, 60, 45), dist=240, dur=0.26, cd=6.0,
                   uses=2, knock=650, stun=0.4,
                   desc=("Rush forward a medium distance, pushing away every enemy you touch.",
                         "Avança uma distância média, empurrando todo inimigo em que encostar.")),
    "dodge": dict(name=("Dodge", "Esquiva"), icon="feather+up", bg=(50, 120, 80), dist=330, dur=0.17, cd=2.2,
                  uses=1, desc=("A quick, long dash that passes through enemies untouched.",
                                "Um deslocamento rápido e longo que atravessa os inimigos sem sofrer dano.")),
    "blink": dict(name=("Blink", "Blink"), icon="vortex+bolt", bg=(90, 60, 160), dist=380, dur=0.0, cd=9.0,
                  uses=1, radius=150, knock=380,
                  desc=("Teleport far ahead; an impact around you pushes nearby enemies away (360°).",
                        "Teleporta para longe; um impacto ao seu redor empurra os inimigos próximos (360°).")),
}
ATTR_DODGE = {"str": "charge", "agi": "dodge", "int": "blink", "bal": "dodge"}


def kind_for(cls):
    from data import CLASSES
    return ATTR_DODGE.get(CLASSES[cls]["attr"], "dodge")


class DodgeState:
    def __init__(self, hero):
        self.kind = kind_for(hero.member.cls)
        self.spec = DODGES[self.kind]
        self.charges = self.spec["uses"]
        self.timer = 0.0        # recarga do próximo uso
        self.active = 0.0       # tempo restante do movimento
        self.vel = V(0, 0)
        self.hit = set()        # inimigos já empurrados nesta investida
        self.trail = []         # posições recentes (rastro visual)
        self.cd = self.spec["cd"]   # recarga atual (com a redução de recarga do herói)

    def name(self, lang):
        return self.spec["name"][1 if lang == "pt" else 0]

    def update(self, run, dt):
        sp = self.spec
        # redução de recarga (INT, passivas, itens, buffs de velocidade de ataque) vale para a esquiva também
        self.cd = sp["cd"] * run.hero.haste_mult(())
        if self.charges < sp["uses"]:
            self.timer += dt
            if self.timer >= self.cd:
                self.timer -= self.cd
                self.charges += 1
                if self.charges >= sp["uses"]:
                    self.timer = 0.0
        self.trail = [(p, t - dt) for p, t in self.trail if t - dt > 0]
        if self.active <= 0:
            return False
        hero = run.hero
        self.active -= dt
        self.trail.append((V(hero.pos), 0.25))
        hero.pos += self.vel * dt
        run.scenery.collide(hero)
        if self.kind == "charge":   # empurra quem encostar durante a investida
            dmg = 8 + hero.stats["str"] * 0.6
            for e in run.enemies_near(hero.pos, hero.r + 8):
                if id(e) in self.hit:
                    continue
                self.hit.add(id(e))
                side = e.pos - hero.pos
                push = (self.vel.normalize() * 0.7 + (side.normalize() if side.length_squared() > 1 else V(0, 0)))
                run.damage(e, dmg, push, None, knock=sp["knock"], stun=sp["stun"], dmgtype="phys", src=hero,
                           sk=self.name("en"))
        return True

    def start(self, run):
        """Usa a esquiva. Retorna True se usou."""
        hero = run.hero
        sp = self.spec
        if hero.downed or self.charges <= 0 or self.active > 0:
            return False
        d = V(hero.facing)
        if d.length_squared() < 1e-6:
            d = V(1, 0)
        d = d.normalize()
        self.charges -= 1
        self.hit = set()
        if self.kind == "blink":
            start = V(hero.pos)
            dest = run.scenery.free_pos(hero.pos + d * sp["dist"], hero.r + 4)
            run.fx_ring(start, 40, (190, 150, 255))
            hero.pos = dest
            hero.iframes = max(hero.iframes, 0.4)
            dmg = 10 + hero.stats["int"] * 0.8
            run.explode(dest, sp["radius"], dmg, None, knock=sp["knock"], dmgtype="mag", src=hero,
                        sk=self.name("en"))
            run.fx_ring(dest, sp["radius"], (190, 150, 255))
            for k in range(10):
                self.trail.append((start + (dest - start) * (k / 10), 0.25))
            return True
        self.vel = d * (sp["dist"] / sp["dur"])
        self.active = sp["dur"]
        hero.iframes = max(hero.iframes, sp["dur"] + 0.12)   # sem dano durante o movimento
        return True

    # ------------------------------------------------------------------ desenho
    def draw_trail(self, run, s, cam):
        col = {"charge": (255, 170, 110), "dodge": (170, 255, 200), "blink": (200, 170, 255)}[self.kind]
        r = run.hero.r
        for p, t in self.trail:
            a = max(0, min(255, int(255 * t / 0.25 * 0.5)))
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*col, a), (r + 2, r + 2), r)
            s.blit(surf, (p.x - cam.x - r - 2, p.y - cam.y - r - 2))

    def draw_slot(self, run, r):
        """Ícone da esquiva perto das hotkeys: recarga, usos e a tecla."""
        s = run.screen
        sp = self.spec
        ready = self.charges > 0
        ic = si._render(sp["icon"], sp["bg"], (230, 230, 240), r.w)
        if not ready:
            ic = ic.copy()
            ic.set_alpha(110)
        s.blit(ic, r)
        if self.charges < sp["uses"]:   # recarga do próximo uso (sombra que vai baixando)
            frac = max(0.0, 1 - self.timer / self.cd)
            sh = pygame.Surface((r.w, int(r.h * frac)), pygame.SRCALPHA)
            sh.fill((0, 0, 0, 140))
            s.blit(sh, (r.x, r.bottom - sh.get_height()))
            left = max(0.0, self.cd - self.timer)
            run.text(f"{left:.1f}" if left < 10 else f"{left:.0f}", "small", WHITE_TXT, r.center, "center")
        pygame.draw.rect(s, (255, 230, 120) if ready else (90, 90, 105), r, 2, border_radius=8)
        if sp["uses"] > 1:   # contador de usos
            badge = pygame.Rect(r.right - 16, r.y - 6, 20, 18)
            pygame.draw.rect(s, (30, 30, 40), badge, border_radius=6)
            pygame.draw.rect(s, (255, 230, 120), badge, 1, border_radius=6)
            run.text(str(self.charges), "small", WHITE_TXT, badge.center, "center")
        run.text("SPACE", "small", (170, 170, 185), (r.centerx, r.bottom + 2), "midtop")
        run.text(self.name(_lang()), "small", (255, 230, 120), (r.centerx, r.y - 4), "midbottom")


WHITE_TXT = (240, 240, 245)


def _lang():
    import i18n
    return i18n.LANG
