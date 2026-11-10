"""Troféus (Altar of Trophies, no acampamento).

Cada chefão de fase dropa o seu troféu na primeira vez em que é derrotado (100%, uma vez só: é um desbloqueio
da conta). No altar, cada troféu pode ser ativado ou desativado. Cada troféu ativo:
- aplica um modificador próprio na run (veja TROPHIES);
- sobe 1 nível de dificuldade global: inimigos com mais vida, força e quantidade, mas mais EXP, gold e fragmentos.
"""
import pygame

# por nível de dificuldade global (1 por troféu ativo)
GLOBAL_PER_LEVEL = dict(hp=0.15, dmg=0.10, density=0.10, exp=0.10, gold=0.10, frag=0.10)

# id: (fase do chefão, nome EN, nome PT, efeito EN, efeito PT, símbolo do ícone, cor)
TROPHIES = {
    "tusk": (0, "Colossal Boar Tusk", "Presa do Javali Colossal",
             "Every enemy has a small chance (0.3%) to drop a random class fragment, BUT enemies have +10% armor "
             "and magic defense.",
             "Todo inimigo tem uma chance baixa (0,3%) de dropar um fragmento de classe aleatório, MAS os inimigos "
             "têm +10% de armadura e defesa mágica.", "fist+up", (150, 90, 55)),
    "sap": (1, "Ancient Ent Sap", "Seiva do Ent Ancestral",
            "Every enemy has a small chance (1%) to drop gold (1, 5 or 10), BUT enemies regenerate 1% of their "
            "max HP per second.",
            "Todo inimigo tem uma chance baixa (1%) de dropar gold (1, 5 ou 10), MAS os inimigos regeneram 1% da "
            "vida máxima por segundo.", "drop+heal", (95, 125, 60)),
    "silk": (2, "Spider Queen Silk", "Seda da Rainha Aranha",
             "Your pickup range gets a bonus equal to your movement speed bonus, BUT enemy contact hits have a 25% "
             "chance to slow you (30% for 1.5 s).",
             "O seu alcance de coleta ganha um bônus igual ao seu bônus de velocidade de movimento, MAS os golpes "
             "de contato dos inimigos têm 25% de chance de te deixar lento (30% por 1,5 s).", "trap+magnet",
             (110, 60, 130)),
    "fang": (3, "Shadow Wolf Fang", "Presa do Lobo Sombrio",
             "Your party deals +20% damage to enemies at full HP, BUT enemy contact hits have a 25% chance to make "
             "you bleed (2% of max HP per second for 3 s).",
             "A sua party causa +20% de dano em inimigos com a vida cheia, MAS os golpes de contato dos inimigos "
             "têm 25% de chance de causar sangramento (2% da vida máxima por segundo, por 3 s).", "wolf+burst_up",
             (70, 70, 95)),
    "heart": (4, "Corrupted Guardian Heart", "Coração do Guardião Corrompido",
              "Stages last only 5 minutes (the boss comes at 5:00), BUT twice as many monsters spawn.",
              "As fases duram só 5 minutos (o chefão vem aos 5:00), MAS nascem o dobro de monstros.", "hourglass+bolt",
              (170, 50, 70)),
    # ---- Cidade Abandonada ----
    "crown": (5, "Rat King's Crown", "Coroa do Rei Rato",
              "+25% gold, BUT enemies move 10% faster.",
              "+25% de gold, MAS os inimigos andam 10% mais rápido.", "coins+boot", (120, 100, 80)),
    "dagger": (6, "Bandit Lord's Dagger", "Adaga do Lorde Bandido",
               "Your party gets +5% critical chance, BUT has 10% less max HP.",
               "A sua party ganha +5% de chance crítica, MAS tem 10% a menos de vida máxima.", "dagger+heart",
               (150, 90, 60)),
    "mask": (7, "Plague Doctor's Mask", "Máscara do Médico da Peste",
             "Your party deals +25% damage over time (burn, poison, bleed), BUT heals 20% less.",
             "A sua party causa +25% de dano contínuo (queimadura, veneno, sangramento), MAS cura 20% a menos.",
             "poison+heal", (90, 80, 70)),
    "helm": (8, "Headless Knight's Helm", "Elmo do Cavaleiro Sem Cabeça",
             "Your party gets +4 armor and +4 magic defense, BUT moves 8% slower.",
             "A sua party ganha +4 de armadura e +4 de defesa mágica, MAS anda 8% mais devagar.", "shield+boot",
             (110, 115, 130)),
    "ledger": (9, "Hollow Mayor's Ledger", "Livro-Caixa do Prefeito Oco",
               "+15% EXP, BUT elites appear 50% more often.",
               "+15% de EXP, MAS os elites aparecem 50% mais vezes.", "book+skull", (120, 140, 180)),
    # ---- Catedral ----
    "gheart": (10, "Gargoyle's Stone Heart", "Coração de Pedra da Gárgula",
               "Your party deals +10% damage, BUT enemies hit 15% harder.",
               "A sua party causa +10% de dano, MAS os inimigos batem 15% mais forte.", "rock+sword",
               (120, 120, 135)),
    "seal": (11, "Inquisitor's Seal", "Selo do Inquisidor",
             "Your party gets +6% cooldown reduction, BUT enemies have +12% HP.",
             "A sua party ganha +6% de redução de recarga, MAS os inimigos têm +12% de vida.", "holy+clock",
             (150, 40, 50)),
    "prism": (12, "Prismatic Shard", "Caco Prismático",
              "Your party gets +10% area and +10% range, BUT 12% more enemies appear.",
              "A sua party ganha +10% de área e +10% de alcance, MAS aparecem 12% mais inimigos.", "star+burst",
              (90, 140, 200)),
    "rosary": (13, "Bone Rosary", "Rosário de Ossos",
               "Your party regenerates +3 HP every 5 s and heals 15% more, BUT deals 5% less damage.",
               "A sua party regenera +3 de vida a cada 5 s e cura 15% a mais, MAS causa 5% a menos de dano.",
               "skull+heal", (210, 200, 170)),
    "halo": (14, "Fallen Halo", "Auréola Caída",
             "Your party deals +15% damage, BUT has -3 armor and -3 magic defense.",
             "A sua party causa +15% de dano, MAS tem -3 de armadura e -3 de defesa mágica.", "sun+crack",
             (80, 60, 100)),
    # ---- Subterrâneo ----
    "egg": (15, "Brood Egg", "Ovo da Matriarca",
            "Your party moves 10% faster, BUT enemies have +10% HP.",
            "A sua party anda 10% mais rápido, MAS os inimigos têm +10% de vida.", "orb+boot", (80, 100, 120)),
    "sack": (16, "Goblin King's Sack", "Saco do Rei Goblin",
             "+25% gold, BUT -10% EXP.",
             "+25% de gold, MAS -10% de EXP.", "coins+crack", (130, 160, 70)),
    "ooze": (17, "Titan Ooze", "Gosma do Titã",
             "Your party regenerates +4 HP every 5 s, BUT moves 5% slower.",
             "A sua party regenera +4 de vida a cada 5 s, MAS anda 5% mais devagar.", "drop+heal", (90, 180, 110)),
    "core": (18, "Crystal Core", "Núcleo de Cristal",
             "Your party deals +12% magic damage, BUT 8% less physical damage.",
             "A sua party causa +12% de dano mágico, MAS 8% a menos de dano físico.", "orb+crack", (120, 190, 220)),
    "scale": (19, "Wyrm Scale", "Escama do Wyrm",
              "Your party gets +5 armor, BUT its cooldowns are 6% longer.",
              "A sua party ganha +5 de armadura, MAS as recargas ficam 6% mais longas.", "shield+hourglass",
              (150, 60, 50)),
    # ---- Inferno ----
    "horn": (20, "Imp Prince's Horn", "Chifre do Príncipe Diabrete",
             "Your party deals +20% critical damage, BUT enemies move 8% faster.",
             "A sua party causa +20% de dano crítico, MAS os inimigos andam 8% mais rápido.", "flame+burst_up",
             (220, 70, 50)),
    "collar": (21, "Cerberus Collar", "Coleira do Cérbero",
               "Your party deals +8% damage, BUT 10% more enemies spawn.",
               "A sua party causa +8% de dano, MAS nascem 10% mais inimigos.", "wolf+up", (90, 60, 60)),
    "magma": (22, "Magma Heart", "Coração de Magma",
              "Your party gets +12% area and +10% damage over time, BUT -3 armor.",
              "A sua party ganha +12% de área e +10% de dano contínuo, MAS -3 de armadura.", "rock+flame",
              (200, 90, 40)),
    "warbanner": (23, "Demon General's Banner", "Estandarte do General Demônio",
                  "+20% EXP, BUT enemies deal 12% more damage.",
                  "+20% de EXP, MAS os inimigos causam 12% mais dano.", "banner+warcry", (130, 40, 40)),
    "dcrown": (24, "Demon King's Crown", "Coroa do Rei Demônio",
               "Your party deals +12% damage and gets +4% critical chance, BUT enemies have +15% HP and deal "
               "10% more damage.",
               "A sua party causa +12% de dano e ganha +4% de chance crítica, MAS os inimigos têm +15% de vida e "
               "causam 10% mais dano.", "skull+star", (110, 30, 70)),
}
ORDER = list(TROPHIES)

# troféus dos biomas novos: modificadores simples (party = bônus para todos os membros, como os emblemas;
# enemy = multiplicadores dos inimigos; run = multiplicadores de gold/EXP). Os da floresta têm efeitos próprios
# no código da run (tusk, sap, silk, fang, heart).
MODS = {
    "crown": dict(run={"gold": 1.25}, enemy={"speed": 1.10}),
    "dagger": dict(party={"crit": 5, "hp_pct": -10}),
    "mask": dict(party={"dot_dmg": 25, "heal": -20}),
    "helm": dict(party={"armor": 4, "mres": 4, "speed": -8}),
    "ledger": dict(run={"exp": 1.15}, enemy={"elite": 1.5}),
    "gheart": dict(party={"dmg": 10}, enemy={"dmg": 1.15}),
    "seal": dict(party={"cdr": 6}, enemy={"hp": 1.12}),
    "prism": dict(party={"area": 10, "range": 10}, enemy={"density": 1.12}),
    "rosary": dict(party={"regen5": 3, "heal": 15, "dmg": -5}),
    "halo": dict(party={"dmg": 15, "armor": -3, "mres": -3}),
    "egg": dict(party={"speed": 10}, enemy={"hp": 1.10}),
    "sack": dict(run={"gold": 1.25, "exp": 0.90}),
    "ooze": dict(party={"regen5": 4, "speed": -5}),
    "core": dict(party={"mag_dmg": 12, "phys_dmg": -8}),
    "scale": dict(party={"armor": 5, "cdr": -6}),
    "horn": dict(party={"critdmg": 20}, enemy={"speed": 1.08}),
    "collar": dict(party={"dmg": 8}, enemy={"density": 1.10}),
    "magma": dict(party={"area": 12, "dot_dmg": 10, "armor": -3}),
    "warbanner": dict(run={"exp": 1.20}, enemy={"dmg": 1.12}),
    "dcrown": dict(party={"dmg": 12, "crit": 4}, enemy={"hp": 1.15, "dmg": 1.10}),
}


def by_stage(stage_index):
    for tid, t in TROPHIES.items():
        if t[0] == stage_index:
            return tid
    return None


def name(tid, lang="en"):
    t = TROPHIES[tid]
    return t[2] if lang == "pt" else t[1]


def desc(tid, lang="en"):
    t = TROPHIES[tid]
    return t[4] if lang == "pt" else t[3]


def icon(tid, size=48, dim=False):
    import skill_icons as si
    t = TROPHIES[tid]
    ic = si._render(t[5], t[6], (240, 220, 160), size)
    if dim:
        ic = ic.copy()
        ic.fill((60, 60, 70), special_flags=pygame.BLEND_RGB_MULT)
        ic.set_alpha(150)
    return ic


def global_mults(level):
    """Multiplicadores do nível de dificuldade global."""
    return {k: 1 + v * level for k, v in GLOBAL_PER_LEVEL.items()}
