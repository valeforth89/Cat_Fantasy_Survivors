"""Power-ups: itens raros dropados pelos inimigos (elites dropam com muito mais frequência).

Fora da tela, cada power-up mostra um "pin" na borda com o ícone e a direção para achá-lo.
"""
import math
import random

import pygame
from pygame.math import Vector2 as V

DROP_CHANCE = 0.002       # inimigo comum (0,2%)
ELITE_DROP_CHANCE = 0.25  # elite (25%)
MAX_ON_FIELD = 6
LIFETIME = 40.0
BUFF_TIME = 10.0

# tipo: (nome EN, nome PT, descrição EN, descrição PT, símbolo do ícone, cor de fundo, peso do sorteio)
POWERUPS = {
    "potion": ("Tuna Can", "Lata de Atum", "Heals the party for 20% of max HP",
               "Cura a party em 20% da vida máxima", "tuna", (150, 40, 60), 3),
    "barrier": ("Cardboard Box", "Caixa de Papelão", "The party is invulnerable for 10 s", "A party fica invulnerável por 10 s",
                "box", (60, 90, 150), 1),
    "fury": ("Zoomies", "Surto Felino", "+30% damage for 10 s", "+30% de dano por 10 s",
             "zoomies", (150, 60, 40), 2),
    "precision": ("Laser Pointer", "Ponteiro Laser", "+20% critical chance and +50% critical damage for 10 s",
                  "+20% de chance crítica e +50% de dano crítico por 10 s", "laser", (140, 110, 30), 2),
    "haste": ("Feather Wand", "Varinha de Penas", "Skills recharge 40% faster for 10 s",
              "As habilidades recarregam 40% mais rápido por 10 s", "feather_wand", (40, 110, 110), 2),
    "shock": ("Big Hiss", "Chiado Feroz", "Stuns every enemy on screen for 3 s",
              "Atordoa todos os inimigos da tela por 3 s", "hiss", (110, 100, 30), 2),
    "magnet": ("Treat Bag", "Saco de Petiscos", "Pulls every EXP gem on the map", "Puxa todas as gemas de EXP do mapa",
               "treats", (120, 50, 50), 3),
    "gold": ("Gold", "Gold", "Gold coins: usually 1, sometimes 5, rarely 10",
             "Moedas de gold: geralmente 1, às vezes 5, raramente 10", "coins", (110, 85, 25), 6),
}
# quantidade de gold de um drop de moedas: (quantidade, peso)
GOLD_AMOUNTS = ((1, 70), (5, 25), (10, 5))


class PowerUp:
    def __init__(self, pos, kind):
        self.pos, self.kind, self.life = V(pos), kind, LIFETIME
        self.amount = 0
        if kind == "gold":
            self.amount = random.choices([a for a, _ in GOLD_AMOUNTS], [w for _, w in GOLD_AMOUNTS])[0]


def pick_kind():
    kinds = list(POWERUPS)
    return random.choices(kinds, [POWERUPS[k][6] for k in kinds])[0]


def name(kind, lang="en"):
    p = POWERUPS[kind]
    return p[1] if lang == "pt" else p[0]


def desc(kind, lang="en"):
    p = POWERUPS[kind]
    return p[3] if lang == "pt" else p[2]


def icon(kind, size=32):
    import skill_icons as si
    p = POWERUPS[kind]
    return si._render(p[4], p[5], (230, 230, 240), size)


def apply(run, kind, amount=0):
    """Efeito ao pegar o power-up."""
    party = [u for u in run.party if not u.downed]
    if kind == "gold":   # vai direto para o gold da conta (fica salvo mesmo se a run acabar em morte)
        run.gold_run += amount
        run.app.roster.add_gold(amount)
    elif kind == "potion":
        for u in party:
            run.heal(u, u.max_hp * 0.2)
    elif kind == "barrier":
        for u in party:
            u.buffs["Cardboard Box"] = [{"invuln": 1}, BUFF_TIME]
    elif kind == "fury":
        for u in party:
            u.buffs["Zoomies"] = [{"dmg": 0.3}, BUFF_TIME]
    elif kind == "precision":
        for u in party:
            u.buffs["Laser Pointer"] = [{"crit": 20, "critdmg": 50}, BUFF_TIME]
    elif kind == "haste":
        for u in party:
            u.buffs["Feather Wand"] = [{"haste": 0.4}, BUFF_TIME]
    elif kind == "shock":
        cam = run.hero.pos - V(run.W / 2, run.H / 2)
        for e in run.enemies:
            sp = e.pos - cam
            if run.on_screen(sp, 0):
                e.stun_t = max(e.stun_t, 3.0)
                run.fx.append(run.Fx("bolt", e.pos, 0.2, color=(255, 250, 130)))
    elif kind == "magnet":
        for gm in run.gems:
            gm.pulled = True
            gm.magnet_all = True


def draw(run, s, cam, font):
    """Power-ups no campo e pins na borda da tela para os que estão fora dela."""
    W, H = run.W, run.H
    t = run.time
    for pu in run.powerups:
        sp = pu.pos - cam
        blink = pu.life < 5 and int(pu.life * 6) % 2 == 0
        if run.on_screen(sp, -10):
            if blink:
                continue
            bob = math.sin(t * 4 + pu.pos.x) * 3
            glow = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 240, 160, 70), (32, 32), 30)
            s.blit(glow, (sp.x - 32, sp.y - 32 + bob))
            ic = icon(pu.kind, 30)
            s.blit(ic, ic.get_rect(center=(sp.x, sp.y + bob)))
            if pu.kind == "gold":
                lab = font.render(str(pu.amount), True, (255, 230, 120))
                s.blit(lab, lab.get_rect(midtop=(sp.x, sp.y + bob + 16)))
            continue
        # pin na borda apontando para o item
        c = V(W / 2, H / 2)
        d = sp - c
        if d.length_squared() < 1:
            continue
        m = 44
        k = min((W / 2 - m) / max(1e-6, abs(d.x)), (H / 2 - m) / max(1e-6, abs(d.y)))
        p = c + d * k
        n = d.normalize()
        tip = p + n * 30
        side = n.rotate(90) * 9
        pygame.draw.polygon(s, (255, 230, 120), [tip, p + n * 16 + side, p + n * 16 - side])
        pygame.draw.circle(s, (20, 20, 28), p, 22)
        pygame.draw.circle(s, (255, 230, 120) if not blink else (120, 110, 70), p, 22, 2)
        ic = icon(pu.kind, 28)
        s.blit(ic, ic.get_rect(center=p))
        dist = int(d.length() / 10)
        lab = font.render(f"{dist}m", True, (230, 230, 230))
        s.blit(lab, lab.get_rect(center=(p.x, p.y + 32)))
