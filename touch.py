"""Controles de toque (versão web no celular).

Ligados automaticamente no navegador (pygbag). No PC dá para testar com a variável de ambiente FS_TOUCH=1.

- Joystick virtual: encoste o dedo na metade esquerda da tela e arraste (na run e no acampamento).
- Botão de esquiva (canto inferior direito) e botão de pause (canto superior direito) durante a run.
- Pause e tela de resultado ganham botões grandes (Continuar / Encerrar run, Acampamento / Jogar de novo).
- Arrastar o dedo para cima/baixo nas telas com lista rola o conteúdo (como a roda do mouse).
Os toques simples nos menus chegam ao jogo como cliques do mouse (o navegador já faz isso).
"""
import math
import os

import pygame
from pygame.math import Vector2 as V

import storage
from data import W, H
from i18n import L

JOY_RADIUS = 80        # quanto o dedo precisa arrastar para velocidade máxima
JOY_DEAD = 14          # zona morta (px)
DODGE_C, DODGE_R = V(W - 118, H - 210), 62
PAUSE_RECT = pygame.Rect(W - 76, 100, 60, 56)
DRAG_STEP = 34         # px arrastados por "clique" de roda


def enabled_by_default():
    return storage.IS_WEB or os.environ.get("FS_TOUCH") == "1"


class TouchControls:
    def __init__(self, app):
        self.app = app
        self.enabled = enabled_by_default()
        self.joy_id = None
        self.joy_c = V(0, 0)
        self.joy_p = V(0, 0)
        self.drag_acc = 0.0
        self.used = False      # já houve algum toque (mostra a dica do joystick até o primeiro uso)

    # ------------------------------------------------------------------ cenas
    def scene(self):
        app = self.app
        if app.state == "run" and app.run is not None:
            return "run-" + app.run.state
        return app.state

    def bottom_buttons(self):
        """Botões grandes do pause / resultado: [(rect, rótulo, ação)]."""
        sc = self.scene()
        y = H - 64
        if sc == "run-pause":
            return [(pygame.Rect(W / 2 - 250, y, 240, 48), L("Resume", "Continuar"), "resume"),
                    (pygame.Rect(W / 2 + 10, y, 240, 48), L("End run", "Encerrar run"), "end")]
        if sc == "run-over":
            nd = self.app.run.next_dungeon()
            if nd:   # masmorra concluída: 3 botões
                return [(pygame.Rect(W / 2 - 400, y, 250, 48), L("Back to camp", "Voltar ao acampamento"), "menu"),
                        (pygame.Rect(W / 2 - 125, y, 250, 48), L("Play again", "Jogar de novo"), "restart"),
                        (pygame.Rect(W / 2 + 150, y, 250, 48), L(f"Next level (Lv {nd[1]})", f"Próximo nível (Nv {nd[1]})"),
                         "next")]
            return [(pygame.Rect(W / 2 - 250, y, 240, 48), L("Back to camp", "Voltar ao acampamento"), "menu"),
                    (pygame.Rect(W / 2 + 10, y, 240, 48), L("Play again", "Jogar de novo"), "restart")]
        return []

    # ------------------------------------------------------------------ joystick
    def direction(self):
        """Vetor do joystick (comprimento 0..1) ou None."""
        if self.joy_id is None:
            return None
        d = self.joy_p - self.joy_c
        if d.length() < JOY_DEAD:
            return V(0, 0)
        return d / max(d.length(), JOY_RADIUS)

    def keys(self, base):
        """Teclado + joystick: o joystick 'aperta' WASD (8 direções)."""
        d = self.direction() if self.enabled else None
        if not d or d.length_squared() == 0:
            return base
        n = d.normalize()
        extra = {pygame.K_w: n.y < -0.38, pygame.K_s: n.y > 0.38, pygame.K_a: n.x < -0.38, pygame.K_d: n.x > 0.38}
        return _Keys(base, extra)

    # ------------------------------------------------------------------ eventos
    def handle(self, ev):
        """Retorna (consumido, ação). ação: None ou 'menu'/'restart' (resultado da run)."""
        if not self.enabled:
            return False, None
        sc = self.scene()
        t = ev.type
        if t == pygame.FINGERDOWN:
            self.used = True
            p = V(ev.x * W, ev.y * H)
            if sc == "run-play":
                if (p - DODGE_C).length() <= DODGE_R + 14:
                    self.app.run.dodge.start(self.app.run)
                    return True, None
                if PAUSE_RECT.inflate(16, 16).collidepoint(p):
                    self.app.run.state = "pause"
                    return True, None
            if sc in ("run-play", "hub") and p.x < W * 0.55 and self.joy_id is None:
                self.joy_id = ev.finger_id
                self.joy_c, self.joy_p = V(p), V(p)
            return False, None
        if t == pygame.FINGERMOTION and ev.finger_id == self.joy_id:
            self.joy_p = V(ev.x * W, ev.y * H)
            d = self.joy_p - self.joy_c
            if d.length() > JOY_RADIUS * 1.6:   # a base acompanha o dedo se ele for longe demais
                self.joy_c = self.joy_p - d.normalize() * JOY_RADIUS * 1.6
            return False, None
        if t == pygame.FINGERUP and ev.finger_id == self.joy_id:
            self.joy_id = None
            return False, None
        if sc not in ("run-play", "run-pause", "run-over") and self.joy_id is not None:
            self.joy_id = None   # saiu da run / do acampamento com o dedo na tela
        # botões grandes do pause / resultado
        if t == pygame.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 1:
            self.drag_acc = 0.0
            for r, _lab, act in self.bottom_buttons():
                if r.collidepoint(ev.pos):
                    run = self.app.run
                    if act == "resume":
                        run.state = "play"
                    elif act == "end":
                        run.end_run(False)
                    else:
                        return True, act
                    return True, None
        # arrastar = rolar (fora da run em andamento e do acampamento)
        if t == pygame.MOUSEMOTION and ev.buttons and ev.buttons[0] and sc not in ("run-play", "hub"):
            self.drag_acc += ev.rel[1]
            while abs(self.drag_acc) >= DRAG_STEP:
                step = 1 if self.drag_acc > 0 else -1
                self.drag_acc -= step * DRAG_STEP
                self.app.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=step, flipped=False,
                                                         precise_x=0.0, precise_y=float(step), touch=True))
        return False, None

    # ------------------------------------------------------------------ desenho
    def draw(self, s, font):
        if not self.enabled:
            return
        sc = self.scene()
        if sc in ("run-play", "hub"):
            self.draw_joystick(s, font, hint=sc == "run-play" and not self.used)
        if sc == "run-play":
            self.draw_dodge(s, font)
            self.draw_pause_button(s)
        btns = self.bottom_buttons()
        if btns:
            strip = pygame.Surface((W, 80), pygame.SRCALPHA)
            strip.fill((12, 12, 18, 235))
            s.blit(strip, (0, H - 80))
            mouse = pygame.mouse.get_pos()
            for r, lab, _act in btns:
                hot = r.collidepoint(mouse)
                pygame.draw.rect(s, (60, 60, 85) if hot else (36, 36, 50), r, border_radius=12)
                pygame.draw.rect(s, (255, 220, 90), r, 2, border_radius=12)
                img = font.render(lab, True, (240, 240, 245))
                s.blit(img, img.get_rect(center=r.center))

    def draw_joystick(self, s, font, hint=False):
        if self.joy_id is None:
            if hint:   # dica até o primeiro toque
                c = V(170, H - 170)
                ring = pygame.Surface((JOY_RADIUS * 2 + 8, JOY_RADIUS * 2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(ring, (255, 255, 255, 40), ring.get_rect().center, JOY_RADIUS, 3)
                s.blit(ring, (c.x - JOY_RADIUS - 4, c.y - JOY_RADIUS - 4))
                img = font.render(L("Drag here to move", "Arraste aqui para andar"), True, (230, 230, 240))
                img.set_alpha(170)
                s.blit(img, img.get_rect(center=(c.x, c.y)))
            return
        base = pygame.Surface((JOY_RADIUS * 2 + 8, JOY_RADIUS * 2 + 8), pygame.SRCALPHA)
        ctr = base.get_rect().center
        pygame.draw.circle(base, (0, 0, 0, 70), ctr, JOY_RADIUS)
        pygame.draw.circle(base, (255, 255, 255, 110), ctr, JOY_RADIUS, 3)
        s.blit(base, (self.joy_c.x - JOY_RADIUS - 4, self.joy_c.y - JOY_RADIUS - 4))
        d = self.joy_p - self.joy_c
        if d.length() > JOY_RADIUS:
            d.scale_to_length(JOY_RADIUS)
        k = self.joy_c + d
        knob = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(knob, (255, 255, 255, 150), (32, 32), 30)
        pygame.draw.circle(knob, (255, 220, 90, 220), (32, 32), 30, 3)
        s.blit(knob, (k.x - 32, k.y - 32))

    def draw_dodge(self, s, font):
        dg = self.app.run.dodge
        sp = dg.spec
        ready = dg.charges > 0
        surf = pygame.Surface((DODGE_R * 2 + 8, DODGE_R * 2 + 8), pygame.SRCALPHA)
        c = surf.get_rect().center
        pygame.draw.circle(surf, (*sp["bg"], 170 if ready else 80), c, DODGE_R)
        if dg.charges < sp["uses"]:   # recarga: arco
            frac = min(1.0, dg.timer / dg.cd)
            rect = pygame.Rect(0, 0, DODGE_R * 2 - 6, DODGE_R * 2 - 6)
            rect.center = c
            pygame.draw.arc(surf, (255, 230, 120, 230), rect, math.pi / 2, math.pi / 2 + frac * 2 * math.pi, 6)
        pygame.draw.circle(surf, (255, 230, 120, 230) if ready else (120, 120, 135, 200), c, DODGE_R, 3)
        s.blit(surf, (DODGE_C.x - DODGE_R - 4, DODGE_C.y - DODGE_R - 4))
        img = font.render(dg.name(_lang()), True, (255, 255, 255))
        s.blit(img, img.get_rect(center=DODGE_C))
        if sp["uses"] > 1:
            b = font.render(str(dg.charges), True, (255, 230, 120))
            s.blit(b, b.get_rect(center=(DODGE_C.x + DODGE_R - 6, DODGE_C.y - DODGE_R + 8)))

    def draw_pause_button(self, s):
        r = PAUSE_RECT
        surf = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 120), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (255, 255, 255, 160), surf.get_rect(), 2, border_radius=12)
        for x in (r.w / 2 - 9, r.w / 2 + 4):
            pygame.draw.rect(surf, (255, 255, 255, 220), (x, 14, 6, r.h - 28), border_radius=2)
        s.blit(surf, r.topleft)


class _Keys:
    def __init__(self, base, extra):
        self.base, self.extra = base, extra

    def __getitem__(self, k):
        return self.extra.get(k, False) or self.base[k]


def _lang():
    import i18n
    return i18n.LANG
