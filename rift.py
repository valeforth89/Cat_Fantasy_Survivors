"""Endless Rift: fase do portal de fases que funciona como o Endless da Floresta, com algumas diferenças.

- Inimigos, elites e chefões sorteados entre TODAS as fases já liberadas pelo jogador (de qualquer bioma; os
  biomas novos entram na lista sozinhos quando forem liberados). A ordem em que aparecem é a mesma do Endless.
- O cenário muda a cada chefão derrotado (ou, se ele não morrer, quando o próximo chegar): sorteado entre os
  cenários das fases liberadas.
- A dificuldade base é a da fase mais alta que o jogador já concluiu.
- Nível da fenda (como nas masmorras): +30% vida, +15% força, +20% resistência e +20% recompensa por nível.
  Sobreviver 10 minutos conclui o nível e libera o próximo; a cada 10 minutos o jogo pergunta se o jogador
  quer continuar no mesmo nível ou subir, e o tempo segue correndo.
- Não dropa acessórios (por enquanto): elites e chefões dropam fragmentos de acessório direto.
- Libera ao concluir a Floresta I.
"""
from data import STAGES, BIOMES
import dungeons as dgm

RIFT_ID = 99               # id na seleção de fase (as fases normais são 0..N; os Endless dos biomas, 100+)
LEVEL_TIME = 600.0         # 10 minutos sobrevividos concluem o nível
COLOR = (170, 90, 230)
# chance de fragmento de acessório por tipo de inimigo forte (o chefão sempre dá 1)
FRAG_CHANCE = {"boss": 1.0, "super": 0.15, "squad": 0.03, "normal": 0.01}


def unlocked(roster):
    return roster.stages_cleared >= 1


def stage_pool(roster):
    """Fases liberadas (inimigos, chefões e cenários da fenda)."""
    return [i for i in range(len(STAGES)) if roster.stage_unlocked(i)] or [0]


def base_stage(roster):
    """Fase mais alta já concluída (define a dificuldade inicial)."""
    return STAGES[max(0, min(len(STAGES), roster.stages_cleared) - 1)]


def mults(level):
    return dgm.mults(level)


def biome_name_of(idx):
    for b in BIOMES:
        if idx in b["stages"]:
            return b["name"]
    return BIOMES[0]["name"]
