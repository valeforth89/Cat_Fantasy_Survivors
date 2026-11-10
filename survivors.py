"""
Cat Fantasy Survivors — protótipo de jogo no estilo Vampire Survivors / Halls of Torment.

Requisitos: Python 3.9+ e pygame   ->   pip install pygame
Executar:   python survivors.py

Arquivos:
  survivors.py ... ponto de entrada e controle das telas
  data.py ........ constantes, classes, habilidades, inimigos
  roster.py ...... party, níveis persistentes (meta progression) e configurações
  skills.py ...... habilidades automáticas e efeitos
  run.py ......... a partida em si
  menus.py ....... telas de menu
  progression.py . habilidades, passivas e bônus por nível de cada classe (lê classes.xlsx)
  classes.xlsx ... planilha editável com o conteúdo das classes (precisa de: pip install openpyxl)
  save.json ...... progresso da party (criado automaticamente)
  settings.json .. configurações (criado automaticamente)

Controles na partida:
  WASD / setas ......... mover o herói (os outros membros agem sozinhos)
  1, 2, 3 / clique ..... escolher melhoria ao subir de nível
  ESC .................. pausar  (Q no pause encerra a run e entrega a EXP)
"""
import asyncio
import sys

import pygame

import pixel

import storage
from touch import TouchControls
import i18n
import progression as prog
from version import VERSION, STAGE as VERSION_STAGE
from data import W, H
from menus import MenusMixin
from menus_craft import CraftMixin
from roster import Roster, load_settings, save_settings, SAVE_SLOTS, fps_cap
from run import Run
from hub import Hub


class App(MenusMixin, CraftMixin):
    def __init__(self):
        self.settings = load_settings()
        i18n.set_language(self.settings["language"])
        prog.load()  # habilidades e progressão das classes (classes.xlsx ou conteúdo provisório)
        print(f"Class content: {prog.LOAD_INFO['source']}")
        for w in prog.LOAD_INFO["warnings"]:
            print("  warning:", w)
        try:
            slot = max(1, min(SAVE_SLOTS, int(self.settings.get("slot", 1))))
        except (TypeError, ValueError):
            slot = 1
        self.roster = Roster.load(slot)   # último save usado (Continue)
        self.roster.save()
        self.screen = None
        self.apply_display()
        self.fonts = pixel.make_fonts()   # fonte pixelada (Jersey 10) com as medidas da fonte antiga
        self.fps = 0.0
        self.clock_time = 0.0
        self.state = "menu"
        self.sel = 0
        self.party_sel = 0
        self.party_scroll = 0
        self.class_cursor = "freelancer"
        self.rename_buf = ""
        self.confirm_dismiss = False
        self.toast_msg = ""
        self.toast_t = 0.0
        self.tip = None          # pop-up de explicação aberta: [id da dica, página]
        self.lo_cid, self.lo_back = "freelancer", "party"
        self.lv_cid, self.lv_scroll = "freelancer", 0
        self.stage_cursor = self.roster.stage
        self.lo_sel, self.lo_focus, self.lo_list_sel, self.lo_scroll = 1, "slots", 0, 0
        self.run = None
        self.inv_mode = "chest"
        self.hub = Hub(self)   # acampamento (HUB central)
        self.touch = TouchControls(self)   # controles de toque (versão web / celular)
        n_warn = len(prog.LOAD_INFO["warnings"])
        if prog.LOAD_INFO["source"] != "classes.xlsx":
            self.toast("Using placeholder skills (classes.xlsx not loaded)")
        elif n_warn:
            self.toast(f"classes.xlsx loaded with {n_warn} warning(s) - see the terminal")
        pygame.key.stop_text_input()

    def apply_display(self):
        if storage.IS_WEB:   # no navegador a página cuida da escala e da tela cheia
            self.screen = pygame.display.set_mode((W, H))
            if getattr(self, "run", None):
                self.run.screen = self.screen
            return
        flags = pygame.SCALED | (pygame.FULLSCREEN if self.settings["fullscreen"] else 0)
        self.screen = pygame.display.set_mode((W, H), flags)
        if getattr(self, "run", None):
            self.run.screen = self.screen

    def mouse_pos(self):
        return pygame.mouse.get_pos()

    def use_slot(self, slot, new=False):
        """Troca de save: carrega (ou cria, se new) o save do espaço slot e volta ao estado inicial das telas."""
        self.roster = Roster.new(slot) if new else Roster.load(slot)
        self.roster.save()
        self.settings["slot"] = slot
        save_settings(self.settings)
        self.run = None
        self.party_sel = 0
        self.party_scroll = 0
        self.stage_cursor = self.roster.stage
        self.rift_pick = None
        self.dg_pick = None
        self.training_cfg = None
        self.hub.reset()

    def go(self, state):
        if state == "hub" and getattr(self, "training_return", False):   # voltou do "Gerenciar party" do treino
            self.training_return = False
            self.start_training(keep=True)
            return
        self.state = state
        self.sel = 0
        if state == "hub":   # new player experience: novos lugares no acampamento e a dica de boas-vindas
            new = self.roster.check_unlocks()
            if new:
                import tips as tips_mod
                en = ", ".join(tips_mod.UNLOCKS[k][0] for k in new)
                pt = ", ".join(tips_mod.UNLOCKS[k][1] for k in new)
                self.toast(i18n.L(f"New at the camp: {en}!", f"Novo no acampamento: {pt}!"))
            self.show_tip("welcome")
        tid = self.state_tip()
        if tid and state != "hub":
            self.show_tip(tid)

    def start_training(self, keep=False):
        """Sala de Treino (bonecos invencíveis) com a party ativa. Pelo acampamento ela começa vazia; keep=True
        (voltar da party / recomeçar build) recoloca os bonecos que já estavam."""
        if not keep:
            import training
            training.cfg(self)["spawned"] = []
        self.run = Run(self, self.roster.active(), training=True)
        self.state = "run"
        self.show_tip("training")

    def start_run(self, dungeon=None):
        """dungeon = (id, nível) para as masmorras do portal vermelho."""
        self.run = Run(self, self.roster.active(), self.roster.stage, dungeon=dungeon)
        self.state = "run"
        self.show_tip("run")

    # ---------- loop ----------
    def handle_event(self, ev):
        """Retorna False para fechar o jogo."""
        if self.tip is not None:   # pop-up de explicação aberta: captura tudo até fechar
            self.tip_event(ev)
            return True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.state_tip(help_btn=True) and \
                self.help_rect().collidepoint(ev.pos):
            self.show_tip(self.state_tip(help_btn=True), force=True)
            return True
        used, action = self.touch.handle(ev)
        if used:
            if action:
                self.run_action(action)
            return True
        if self.state == "run":
            self.run_action(self.run.handle_event(ev))
            return True
        handler = {
        
            "menu": self.main_event,
            "hub": self.hub.event,
            "jeweler": self.jeweler_event,
            "altar": self.altar_event,
            "mastery": self.mastery_event,
            "greed": self.greed_event,
            "craft": self.craft_event,
            "dungeons": self.dungeons_event,
            "party": self.party_event,
            "classes": self.classes_event,
            "loadout": self.loadout_event,
            "stages": self.stages_event,
            "levels": self.levels_event,
            "rename": self.rename_event,
            "look": self.look_event,
            "config": self.config_event,
            "inventory": self.inventory_event,
            "faq": self.faq_event,
            "saves": self.saves_event,
        }[self.state]
        return handler(ev)

    def run_action(self, action):
        if action == "menu":   # fim da run: volta para o acampamento
            self.run = None
            self.hub.reset()
            self.go("hub")
        elif action == "restart":
            if self.run is not None and self.run.training:
                self.start_training(keep=True)
            elif self.run is not None and self.run.rift:   # Endless Rift: de novo no mesmo nível
                self.rift_pick = self.run.rift_lv
                self.start_run()
            else:
                self.start_run(self.run.dungeon if self.run is not None else None)
        elif action == "party":   # Sala de Treino: gerenciar a party e voltar para a sala
            self.run = None
            self.training_return = True
            self.go("party")
        elif action == "next":   # masmorra concluída: já entra no próximo nível
            nd = self.run.next_dungeon() if self.run is not None else None
            if nd:
                self.start_run(nd)

    def update(self, dt, keys):
        keys = self.touch.keys(keys)   # joystick virtual (celular) "aperta" WASD
        self.clock_time += dt
        self.toast_t = max(0.0, self.toast_t - dt)
        if self.tip is not None:   # pop-up aberta: o jogo fica parado
            return
        if self.state == "run":
            self.run.update(dt, keys)
        elif self.state == "hub":
            self.hub.update(dt, keys)

    def draw(self):
        {
            "run": lambda: self.run.draw(),
            "menu": self.draw_main,
            "hub": self.hub.draw,
            "jeweler": self.draw_jeweler,
            "altar": self.draw_altar,
            "mastery": self.draw_mastery,
            "greed": self.draw_greed,
            "craft": self.draw_craft,
            "dungeons": self.draw_dungeons,
            "party": self.draw_party,
            "classes": self.draw_classes,
            "loadout": self.draw_loadout,
            "stages": self.draw_stages,
            "levels": self.draw_levels,
            "rename": self.draw_rename,
            "look": self.draw_look,
            "config": self.draw_config,
            "inventory": self.draw_inventory,
            "faq": self.draw_faq,
            "saves": self.draw_saves,
        }[self.state]()
        if self.state != "run":
            self.draw_skill_hover()   # tooltip ao passar o mouse sobre qualquer habilidade
        else:
            self.skill_hovers = []
        if self.state != "run" and self.settings["show_fps"]:
            self.text(f"FPS {self.fps:.0f}", "small", (80, 210, 120), (10, 8))
        if self.state_tip(help_btn=True) and self.state != "hub":
            self.draw_help_button(self.help_rect(), self.mouse_pos())
        if self.state != "run" or self.tip is None:
            self.touch.draw(self.screen, self.fonts["normal"])
        if self.tip is not None:
            self.draw_tip()


def main():
    pygame.init()
    pygame.display.set_caption(f"Cat Fantasy Survivors - ver. {VERSION} ({VERSION_STAGE})")
    try:   # ícone da janela
        import skill_icons
        pygame.display.set_icon(skill_icons.game_icon(64))
    except Exception:
        pass
    clock = pygame.time.Clock()
    app = App()
    while frame(app, clock):
        pass
    app.roster.save()
    pygame.quit()
    sys.exit()


def frame(app, clock):
    """Um quadro do jogo. Retorna False quando o jogador fecha o jogo."""
    running = True
    # limite de FPS da configuração (padrão: sem limite; o jogo usa dt, então roda igual em qualquer FPS)
    dt = min(clock.tick(fps_cap(app.settings)) / 1000, 0.05)
    app.fps = clock.get_fps()
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT or not app.handle_event(ev):
            if storage.IS_WEB:   # no navegador não há janela para fechar
                app.toast(i18n.L("Close the browser tab to quit (progress is saved).",
                                 "Feche a aba do navegador para sair (o progresso fica salvo)."))
            else:
                running = False
    app.update(dt, pygame.key.get_pressed())
    app.draw()
    pygame.display.flip()
    return running


async def web_main():
    """Versão web (pygbag): o mesmo laço, devolvendo o controle ao navegador a cada quadro."""
    pygame.init()
    pygame.display.set_caption("Cat Fantasy Survivors")
    clock = pygame.time.Clock()
    app = App()
    while True:
        frame(app, clock)
        await asyncio.sleep(0)


if __name__ == "__main__":
    main()
