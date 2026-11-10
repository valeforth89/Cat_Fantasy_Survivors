"""Dados do jogo: constantes, cores, elementos, inimigos, classes e habilidades."""

W, H = 1280, 720
FPS = 60
MAX_ENEMIES = 450

# Escala dos inimigos pelo tamanho da party: nº de membros -> (quantidade de inimigos, vida dos inimigos)
# A quantidade multiplica a frequência de spawn, o tamanho das hordas e o limite de inimigos na tela.
PARTY_SCALING = {
    1: (1.0, 1.0),
    2: (1.6, 1.08),
    3: (2.2, 1.16),
    4: (2.8, 1.25),
    5: (3.4, 1.33),
}
STAGE_TIME = 10 * 60    # cada fase dura 10 minutos; aos 10:00 o chefão aparece e o timer trava
REVIVE_TIME = 20.0      # segundos para um aliado caído voltar à luta (com metade da vida)

BG = (16, 16, 22)
GRID = (30, 30, 42)
WHITE = (235, 235, 240)
GREY = (120, 120, 135)
DARK = (40, 40, 52)
PANEL = (28, 28, 38)
RED = (220, 60, 60)
GREEN = (80, 210, 120)
BLUE = (90, 160, 255)
YELLOW = (250, 210, 70)

# --------------------------------------------------------------------------
# Elementos e seus efeitos ao acertar
# --------------------------------------------------------------------------
ELEMENTS = {
    "fire": dict(name="Fire", color=(255, 120, 50)),
    "ice": dict(name="Ice", color=(140, 210, 255)),
    "lightning": dict(name="Lightning", color=(255, 250, 130)),
    "water": dict(name="Water", color=(70, 140, 255), knock=150),
    "wind": dict(name="Wind", color=(170, 250, 190), knock=220),
    "earth": dict(name="Earth", color=(190, 150, 90)),
    "poison": dict(name="Poison", color=(150, 230, 80)),
    "holy": dict(name="Holy", color=(255, 240, 170)),
    "arcane": dict(name="Arcane", color=(200, 140, 255)),
    "sound": dict(name="Sound", color=(255, 170, 230)),
    "gravity": dict(name="Gravity", color=(150, 110, 230)),
    "time": dict(name="Time", color=(220, 200, 255)),
    "smoke": dict(name="Smoke", color=(170, 170, 180)),
}


# Chance de status por golpe, conforme o elemento (golpes mágicos/elementais)
#   dot = (tipo, % do golpe por segundo, duração); slow = (multiplicador de velocidade, duração); stun = segundos
ELEMENT_STATUS = {
    "fire": dict(chance=0.35, dot=("burn", 0.3, 3.0)),        # Queimando
    "poison": dict(chance=0.5, dot=("poison", 0.4, 4.0)),     # Envenenado
    "ice": dict(chance=0.4, slow=(0.5, 2.0)),                 # Congelando (lentidão)
    "water": dict(chance=0.3, slow=(0.75, 1.5)),              # Encharcado (lentidão leve) + empurrão
    "lightning": dict(chance=0.25, stun=0.25),                # Atordoado
    "earth": dict(chance=0.25, stun=0.4),                     # Derrubado
    "holy": dict(chance=0.15, stun=0.3),                      # Ofuscado (atordoado)
    "sound": dict(chance=0.2, stun=0.2),                      # Zonzo (atordoado)
    "arcane": dict(chance=0.2, slow=(0.7, 1.5)),
    "gravity": dict(chance=0.3, slow=(0.6, 2.0)),
    "time": dict(chance=0.3, slow=(0.5, 2.0)),
    "smoke": dict(chance=0.25, slow=(0.7, 2.0)),
}
# golpes físicos (sem elemento): o tipo de golpe define o status
PHYS_STATUS = {
    "slash": dict(chance=0.3, dot=("bleed", 0.25, 3.0)),      # cortante -> Sangrando
    "piercing": dict(chance=0.3, dot=("bleed", 0.25, 3.0)),   # perfurante -> Sangrando
    "blunt": dict(chance=0.2, stun=0.3),                      # impacto -> Atordoado
}


def element_color(el, default=WHITE):
    return ELEMENTS[el]["color"] if el in ELEMENTS else default


# --------------------------------------------------------------------------
# Inimigos
# --------------------------------------------------------------------------
ENEMY_TYPES = {
    # armor = armadura (subtrai dano físico), mres = defesa mágica (subtrai dano mágico/elemental)
    # dmgtype = tipo do dano de contato que o inimigo causa ("phys" ou "mag")
    # morcego: o mais fraco e mais rápido · lobo: intermediário · javali: o mais forte, lento e resistente
    "morcego": dict(hp=6, speed=130, dmg=6, r=9, color=(130, 80, 170), xp=1, armor=0, mres=0, dmgtype="phys"),
    "lobo": dict(hp=22, speed=95, dmg=11, r=13, color=(125, 125, 140), xp=2, armor=1, mres=0.5, dmgtype="phys"),
    "javali": dict(hp=90, speed=60, dmg=20, r=21, color=(130, 85, 55), xp=8, armor=3, mres=1, dmgtype="phys"),
    # esqueleto (a partir da Floresta III): rápido para o tamanho, muita armadura e pouca defesa mágica
    "esqueleto": dict(hp=40, speed=88, dmg=15, r=14, color=(225, 220, 200), xp=4, armor=3, mres=0, dmgtype="phys"),
    # zumbi (a partir da Floresta V): lento, muita vida, bate forte e resiste a magia
    "zumbi": dict(hp=150, speed=46, dmg=26, r=17, color=(110, 150, 90), xp=10, armor=1, mres=3, dmgtype="phys"),
    # chefão (nome e cor vêm da fase); a vida NÃO cresce com o tempo, só com a fase/party/dificuldade
    "chefe": dict(hp=4000, speed=72, dmg=30, r=40, color=(150, 90, 60), xp=150, armor=6, mres=4, dmgtype="phys"),
    # ---- Cidade Abandonada ----
    # rato: enxame rápido · cão: intermediário · bruto: forte e lento · carniçal (III+) · espectro (V, dano mágico)
    "rato": dict(hp=6, speed=135, dmg=6, r=9, color=(120, 110, 100), xp=1, armor=0, mres=0, dmgtype="phys"),
    "cao": dict(hp=24, speed=100, dmg=11, r=13, color=(140, 110, 80), xp=2, armor=0.5, mres=0.5, dmgtype="phys"),
    "bruto": dict(hp=95, speed=58, dmg=21, r=21, color=(150, 120, 95), xp=8, armor=3, mres=0.5, dmgtype="phys"),
    "carnical": dict(hp=45, speed=84, dmg=16, r=14, color=(130, 140, 120), xp=4, armor=1, mres=1.5, dmgtype="phys"),
    "espectro": dict(hp=130, speed=55, dmg=24, r=17, color=(150, 170, 200), xp=10, armor=0, mres=4, dmgtype="mag"),
    # ---- Catedral ----
    # fogo-fátuo: enxame mágico · cultista · gárgula: muita armadura · armadura viva (III+) · serafim caído (V)
    "fatuo": dict(hp=5, speed=140, dmg=6, r=8, color=(140, 200, 255), xp=1, armor=0, mres=1, dmgtype="mag"),
    "cultista": dict(hp=20, speed=90, dmg=12, r=13, color=(120, 40, 50), xp=2, armor=0.5, mres=1.5, dmgtype="mag"),
    "gargula": dict(hp=100, speed=55, dmg=20, r=21, color=(120, 120, 130), xp=8, armor=4, mres=1, dmgtype="phys"),
    "armadura": dict(hp=50, speed=80, dmg=15, r=15, color=(150, 155, 170), xp=4, armor=5, mres=0, dmgtype="phys"),
    "serafim": dict(hp=140, speed=60, dmg=27, r=18, color=(70, 60, 80), xp=10, armor=2, mres=3, dmgtype="mag"),
    # ---- Subterrâneo ----
    # besouro: enxame com casco · goblin minerador · golem de pedra · gosma (III+) · verme de cristal (V)
    "besouro": dict(hp=7, speed=125, dmg=6, r=9, color=(70, 90, 110), xp=1, armor=1, mres=0, dmgtype="phys"),
    "goblin": dict(hp=22, speed=98, dmg=11, r=13, color=(110, 150, 70), xp=2, armor=1, mres=0.5, dmgtype="phys"),
    "golem": dict(hp=110, speed=50, dmg=22, r=22, color=(120, 105, 90), xp=8, armor=5, mres=2, dmgtype="phys"),
    "gosma": dict(hp=45, speed=80, dmg=14, r=15, color=(110, 190, 120), xp=4, armor=0, mres=2, dmgtype="mag"),
    "verme": dict(hp=150, speed=60, dmg=28, r=18, color=(130, 90, 170), xp=10, armor=3, mres=2, dmgtype="phys"),
    # ---- Inferno ----
    # diabrete: enxame que cospe fogo · cão infernal · demônio chifrudo: forte e lento · salamandra (III+, rastro de
    # fogo, resiste a magia) · bruxo infernal (V, mantém distância e chama colunas de fogo; dano mágico)
    "diabrete": dict(hp=7, speed=135, dmg=7, r=9, color=(200, 60, 50), xp=1, armor=0, mres=1, dmgtype="mag"),
    "cao_inferno": dict(hp=26, speed=102, dmg=12, r=13, color=(60, 45, 45), xp=2, armor=1, mres=1, dmgtype="phys"),
    "demonio": dict(hp=120, speed=52, dmg=23, r=22, color=(150, 45, 45), xp=8, armor=4, mres=2, dmgtype="phys"),
    "salamandra": dict(hp=50, speed=82, dmg=16, r=15, color=(230, 120, 40), xp=4, armor=1, mres=3, dmgtype="mag"),
    "bruxo": dict(hp=150, speed=60, dmg=29, r=18, color=(90, 40, 90), xp=10, armor=1, mres=4, dmgtype="mag"),
}

ENEMY_NAMES = {"morcego": "Bat", "lobo": "Wolf", "javali": "Boar", "esqueleto": "Skeleton", "zumbi": "Zombie",
               "chefe": "Boss", "dummy": "Dummy",
               "rato": "Plague Rat", "cao": "Feral Hound", "bruto": "Bandit Brute", "carnical": "Ghoul",
               "espectro": "Wraith",
               "fatuo": "Wisp", "cultista": "Cultist", "gargula": "Gargoyle", "armadura": "Living Armor",
               "serafim": "Fallen Seraph",
               "besouro": "Cave Beetle", "goblin": "Goblin Miner", "golem": "Rock Golem", "gosma": "Slime",
               "verme": "Crystal Wyrm",
               "diabrete": "Imp", "cao_inferno": "Hellhound", "demonio": "Horned Demon", "salamandra": "Salamander",
               "bruxo": "Infernal Warlock"}
# Papéis dos inimigos de cada bioma (o bioma define quem faz cada papel, veja BIOMES):
# swarm = enxame fraco e rápido · mid = intermediário · heavy = forte e lento (fases I-V)
# new3 = inimigo novo a partir da fase III do bioma · new5 = outro novo na fase V
ROLES = ("swarm", "mid", "heavy", "new3", "new5")
# papel novo: (posição da fase no bioma a partir da qual aparece, tempo da run em que começa)
ROLE_FROM = {"new3": (2, 30), "new5": (4, 90)}
# compatibilidade (Floresta)
ENEMY_FROM_STAGE = {"esqueleto": (2, 30), "zumbi": (4, 90)}

# --------------------------------------------------------------------------
# Fases: cada uma mais difícil que a anterior e com mais recompensa
# hp / dmg / res = multiplicadores de vida, força (dano) e resistência (armadura e defesa mágica) dos inimigos
# reward = multiplicador de EXP e gold
# --------------------------------------------------------------------------
GOLD_STAGE_BASE = 5   # gold por concluir a Floresta I (proporcional ao tempo se não concluir)


def _stage(i, name, desc, boss, boss_color, boss_sprite):
    return dict(index=i, name=name, desc=desc, boss=boss, boss_color=boss_color, boss_sprite=boss_sprite,
                hp=1 + 0.5 * i, dmg=1 + 0.3 * i, res=1 + 0.5 * i, reward=1 + 0.25 * i)


STAGES = [
    _stage(0, "Forest I", "The forest's edge. Bats, wolves and boars fight over the main trail.",
           "Colossal Boar", (150, 90, 55), "javali"),
    _stage(1, "Forest II", "The woods grow thick and the packs grow larger. Something ancient stirs among the trees.",
           "Ancient Ent", (95, 125, 60), "ent"),
    _stage(2, "Forest III", "Webs cover the branches and boars roam in herds. Little light reaches the ground.",
           "Spider Queen", (110, 60, 130), "aranha"),
    _stage(3, "Forest IV", "Howls echo through the mist. The wolves here have faced other heroes before.",
           "Shadow Wolf", (70, 70, 95), "lobo"),
    _stage(4, "Forest V", "The heart of the forest. Everything here has been corrupted, even its protector.",
           "Corrupted Guardian", (170, 50, 70), "guardiao"),
    # ---- Cidade Abandonada ----
    _stage(5, "Abandoned Town I", "The town gates hang open. Rats and stray hounds roam the empty streets.",
           "Rat King", (120, 100, 80), "rei_rato"),
    _stage(6, "Abandoned Town II", "Bandits have taken the market square and they don't like visitors.",
           "Bandit Lord", (150, 90, 60), "lorde_bandido"),
    _stage(7, "Abandoned Town III", "A sickly fog fills the alleys. The dead no longer stay in their graves.",
           "Plague Doctor", (90, 80, 70), "medico"),
    _stage(8, "Abandoned Town IV", "The old barracks burned down. A knight still patrols them, without his head.",
           "Headless Knight", (110, 115, 130), "cavaleiro"),
    _stage(9, "Abandoned Town V", "The town hall at night. Its last mayor never left, and neither did his debts.",
           "Hollow Mayor", (120, 140, 180), "prefeito"),
    # ---- Catedral ----
    _stage(10, "Cathedral I", "Candles still burn in the nave. Wisps and cultists guard the doors.",
           "Grand Gargoyle", (120, 120, 135), "grande_gargula"),
    _stage(11, "Cathedral II", "Prayers turned into chants. The Inquisition judges anyone who enters.",
           "High Inquisitor", (150, 40, 50), "inquisidor"),
    _stage(12, "Cathedral III", "Shattered stained glass covers the floor, and the empty armors stand up.",
           "Stained Glass Golem", (90, 140, 200), "vitral"),
    _stage(13, "Cathedral IV", "The crypt below the altar. Its bishop still leads the mass, all bones.",
           "Bone Bishop", (210, 200, 170), "bispo"),
    _stage(14, "Cathedral V", "The bell tower, open to the sky. Something fell from above and never got up.",
           "Fallen Archangel", (80, 60, 100), "arcanjo"),
    # ---- Subterrâneo ----
    _stage(15, "Underground I", "Mine tunnels lit by lanterns. Beetles swarm and goblins dig.",
           "Broodmother", (80, 100, 120), "matriarca"),
    _stage(16, "Underground II", "The goblins found gold, and a king to keep it.",
           "Goblin King", (130, 160, 70), "rei_goblin"),
    _stage(17, "Underground III", "Damp caverns where slimes drip from the ceiling.",
           "Ooze Titan", (90, 180, 110), "titan_gosma"),
    _stage(18, "Underground IV", "A cave of giant crystals that hum with a deep light.",
           "Crystal Golem", (120, 190, 220), "golem_cristal"),
    _stage(19, "Underground V", "The bottom of the world, warm as an oven. The wyrm sleeps here.",
           "Deep Wyrm", (150, 60, 50), "wyrm"),
    # ---- Inferno ----
    _stage(20, "Inferno I", "The gates of hell, buried in ash. Imps cackle on the burning rocks.",
           "Imp Prince", (220, 70, 50), "principe_diabrete"),
    _stage(21, "Inferno II", "Plains of cracked stone where the hellhounds hunt in packs. Something has three heads.",
           "Cerberus", (70, 50, 50), "cerbero"),
    _stage(22, "Inferno III", "Rivers of magma cut the ground. The salamanders swim in them as if it were water.",
           "Magma Colossus", (200, 90, 40), "colosso_magma"),
    _stage(23, "Inferno IV", "An obsidian fortress lit by hellfire braziers. Its general never lost a battle.",
           "Demon General", (130, 40, 40), "general_demonio"),
    _stage(24, "Inferno V", "The throne at the bottom of everything. The Demon King has waited a long time for you.",
           "Demon King", (110, 30, 70), "rei_demonio"),
]

# Biomas: cada um tem 5 fases (I-V) e uma versão Endless, liberada ao concluir a fase V do bioma.
# Concluir a fase V de um bioma libera a fase I do próximo. Biomas sem fases ainda estão "em breve".
BIOMES = [
    dict(id="forest", name="Forest", stages=[0, 1, 2, 3, 4], color=(90, 160, 80),
         enemies=dict(swarm="morcego", mid="lobo", heavy="javali", new3="esqueleto", new5="zumbi")),
    dict(id="town", name="Abandoned Town", stages=[5, 6, 7, 8, 9], color=(170, 140, 110),
         enemies=dict(swarm="rato", mid="cao", heavy="bruto", new3="carnical", new5="espectro")),
    dict(id="cathedral", name="Cathedral", stages=[10, 11, 12, 13, 14], color=(170, 160, 210),
         enemies=dict(swarm="fatuo", mid="cultista", heavy="gargula", new3="armadura", new5="serafim")),
    dict(id="underground", name="Underground", stages=[15, 16, 17, 18, 19], color=(150, 120, 90),
         enemies=dict(swarm="besouro", mid="goblin", heavy="golem", new3="gosma", new5="verme")),
    dict(id="inferno", name="Inferno", stages=[20, 21, 22, 23, 24], color=(230, 90, 50),
         enemies=dict(swarm="diabrete", mid="cao_inferno", heavy="demonio", new3="salamandra", new5="bruxo")),
]
ENDLESS_BASE = 100            # id de fase das versões Endless: 100 + índice do bioma
ENDLESS_TIER_TIME = 120.0     # a cada 2 minutos a dificuldade (e a recompensa) sobe um degrau
ENDLESS_BOSS_TIME = 120.0     # e aparece um chefão (revezando entre os chefões I..V do bioma)


def is_endless(stage_id):
    return stage_id >= ENDLESS_BASE


def endless_biome(stage_id):
    return BIOMES[stage_id - ENDLESS_BASE]


def stage_pos(stage_id):
    """Posição da fase dentro do bioma (0 = fase I ... 4 = fase V)."""
    for b in BIOMES:
        if stage_id in b["stages"]:
            return b["stages"].index(stage_id)
    return 0


def role_kind(biome, role):
    return biome["enemies"][role]


def roles_at(pos):
    """Papéis de inimigos que existem numa fase na posição pos do bioma."""
    return [r for r in ROLES if r not in ROLE_FROM or pos >= ROLE_FROM[r][0]]


def biome_of(stage_id):
    if is_endless(stage_id):
        return endless_biome(stage_id)
    for b in BIOMES:
        if stage_id in b["stages"]:
            return b
    return BIOMES[0]


DIFFICULTIES = {
    # nome: (vida dos inimigos, frequência de spawn)
    "Easy": (0.75, 0.75),
    "Normal": (1.0, 1.0),
    "Hard": (1.35, 1.3),
}

ATTR_NAMES = {"str": "STR", "agi": "AGI", "int": "INT", "vit": "VIT", "bal": "Balanced"}
ATTRS = ("str", "agi", "int", "vit")

# Nível de CLASSE necessário para cada habilidade da classe (1ª, 2ª, 3ª)
SKILL_UNLOCK = [1, 5, 15]
SKILL_MAX = 5          # nível máximo de uma habilidade dentro da partida
MAX_RELICS = 2         # relíquias extras que o herói pode pegar por partida


def S(kind, name, desc, **params):
    """Cria a especificação de uma habilidade.

    kind = arquétipo: shot, slash, thrust, strike, cone, aura, orbit, heal, buff, summon, cloud
    dmgtype = "phys" (escala com FOR) ou "mag" (escala com INT)
    """
    params.setdefault("dmgtype", "mag")
    return dict(kind=kind, name=name, desc=desc, **params)


# --------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------
CLASSES = {}


def add_class(cid, name, tier, parent, attr, color, weapon, role, skills, ranged=True):
    # Vida, Defesa, Ataque e Velocidade base vêm da role da classe (CLASS_ROLE_DEFS)
    CLASSES[cid] = dict(id=cid, name=name, tier=tier, parent=parent, attr=attr, color=color,
                        weapon=weapon, role=role, skills=skills, ranged=ranged)


# ---- Inicial ----
# id interno "freelancer" = Novice (mantido para os saves antigos)
add_class("freelancer", "Novice", 0, None, "bal", (200, 190, 170), "Short sword",
          "Versatile apprentice. Unlocks the basic classes at Lv 10.", [
              S("slash", "Strike", "Slashes enemies in front", dmg=12, cd=0.9, radius=85, arc=120, dmgtype="phys"),
              S("shot", "Stone Toss", "Throws stones at the nearest enemy", dmg=8, cd=1.1, speed=450, dmgtype="phys"),
          ], ranged=False)

# ---- Evoluções do Novice ----
add_class("freelancer_t2", "Freelancer", 3, "freelancer", "bal", (230, 200, 120), "Longsword",
          "Evolved Novice: masters every basic class. Its slots accept skills of mastered basic classes.", [
              S("slash", "Arcing Slash", "A wide, swift arc with the longsword", dmg=20, cd=0.8, radius=100, arc=150,
                dmgtype="phys"),
              S("shot", "Throwing Axes", "Two axes that pierce enemies", dmg=16, cd=1.2, count=2, spread=12, speed=520,
                pierce=2, size=8, dmgtype="phys"),
          ], ranged=False)
add_class("warfarer", "Warfarer", 4, "freelancer_t2", "bal", (255, 170, 60), "Arsenal",
          "The ultimate fighter: masters every class. Its slots accept skills of any mastered class.", [
              S("slash", "Warbringer", "A devastating sweep of the whole arsenal", dmg=34, cd=0.8, radius=110, arc=170,
                knock=180, dmgtype="phys"),
              S("shot", "Spear Barrage", "Three spears that pierce everything in their path", dmg=26, cd=1.2, count=3,
                spread=14, speed=620, pierce=4, size=7, dmgtype="phys"),
          ], ranged=False)

# ---- Básicas (Novice Nv 10) ----
add_class("archer", "Archer", 1, "freelancer", "agi", (120, 200, 90), "Bow",
          "Ranged physical damage.", [
              S("shot", "Arrow", "Arrow that pierces enemies", dmg=11, cd=0.7, speed=680, pierce=2, size=5, dmgtype="phys"),
              S("strike", "Arrow Rain", "Arrows rain down on several enemies", dmg=9, cd=2.5, count=6, radius=35,
                target="random", dmgtype="phys"),
          ])
add_class("thaumaturge", "Thaumaturge", 1, "freelancer", "int", (230, 110, 60), "Staff",
          "Elemental magic of fire, lightning and ice.", [
              S("shot", "Fire", "Fireball that sets enemies ablaze", dmg=10, cd=0.9, speed=420, size=8, element="fire"),
              S("strike", "Tri-Elemental", "Cycles fire, lightning and ice", dmg=20, cd=2.4, count=2, radius=55,
                target="random", cycle=["fire", "lightning", "ice"]),
          ])
add_class("arcanist", "Arcanist", 1, "freelancer", "int", (170, 120, 230), "Grimoire",
          "Damage spells with a touch of support.", [
              S("shot", "Arcane Missile", "Homing projectiles", dmg=8, cd=0.8, count=2, speed=380, homing=4.0,
                element="arcane"),
              S("buff", "Arcane Shield", "Reduces damage taken by the party", cd=12, duration=6, target="party",
                effects={"dr": 0.25}),
          ])
add_class("pugilist", "Pugilist", 1, "freelancer", "agi", (230, 150, 90), "Fist weapons",
          "Fast melee physical damage and critical hits.", [
              S("slash", "Rapid Punches", "A quick flurry of punches", dmg=7, cd=0.3, radius=60, arc=90, knock=60,
                dmgtype="phys"),
              S("strike", "Shockwave", "A burst of force around you", dmg=22, cd=3.5, radius=110, target="self",
                knock=300, dmgtype="phys"),
          ], ranged=False)
add_class("lancer", "Lancer", 1, "freelancer", "str", (90, 150, 220), "Spear",
          "Mid-range physical damage.", [
              S("thrust", "Thrust", "Pierces in a straight line", dmg=16, cd=0.8, length=150, width=26, dmgtype="phys"),
              S("slash", "Spear Spin", "Circular strike", dmg=14, cd=2.6, radius=115, arc=360, dmgtype="phys"),
          ], ranged=False)
add_class("rogue", "Rogue", 1, "freelancer", "agi", (150, 150, 170), "Dagger",
          "Melee damage and crowd control.", [
              S("slash", "Dagger Slash", "Quick cuts with the dagger", dmg=10, cd=0.45, radius=70, arc=110,
                dmgtype="phys"),
              S("strike", "Smoke Bomb", "Stuns nearby enemies", dmg=6, cd=6, radius=130, target="self",
                stun=1.2, element="smoke", dmgtype="phys"),
          ], ranged=False)
add_class("conjurer", "Conjurer", 1, "freelancer", "int", (100, 200, 170), "Staff",
          "Healing plus wind, earth and water magic.", [
              S("strike", "Natural Elements", "Cycles water, wind and earth", dmg=14, cd=1.4, radius=60,
                target="nearest", cycle=["water", "wind", "earth"]),
              S("heal", "Cure", "Heals nearby allies", amount=8, cd=5, radius=320),
          ])
add_class("gladiator", "Gladiator", 1, "freelancer", "str", (200, 200, 210), "Sword and shield",
          "Defense and physical damage.", [
              S("slash", "Slash", "Sword strike", dmg=13, cd=0.8, radius=90, arc=140, dmgtype="phys"),
              S("buff", "Shield Wall", "Raises the party's defense", cd=14, duration=6, target="party",
                effects={"dr": 0.3}),
          ], ranged=False)
add_class("marauder", "Marauder", 1, "freelancer", "str", (190, 80, 70), "Two-handed axe",
          "Defense and heavy physical damage.", [
              S("slash", "Axe Chop", "A wide, heavy strike", dmg=24, cd=1.4, radius=110, arc=170, knock=200,
                dmgtype="phys"),
              S("shot", "Axe Throw", "An axe that pierces everything", dmg=18, cd=2.8, speed=380, pierce=99,
                size=11, life=1.8, dmgtype="phys"),
          ], ranged=False)

# ---- Avançadas (classe básica Nv 25) ----
add_class("bard", "Bard", 2, "archer", "agi", (240, 170, 220), "Bow and harp",
          "A bit less offensive than the Hunter, but buffs the party.", [
              S("shot", "Melodic Arrow", "Arrows that slow", dmg=12, cd=0.7, speed=650, pierce=2,
                slow=(0.7, 1.0), element="sound", dmgtype="phys"),
              S("buff", "Battle Ballad", "+20% damage and +10% speed for the party", cd=10, duration=7,
                target="party", effects={"dmg": 0.2, "speed": 0.1}),
              S("strike", "Requiem", "A sound wave that slows everything around", dmg=16, cd=4.5, radius=170,
                target="self", slow=(0.5, 2.5), element="sound"),
          ])
add_class("hunter", "Hunter", 2, "archer", "agi", (90, 170, 60), "Longbow",
          "An improved Archer.", [
              S("shot", "Piercing Shot", "Two arrows that pierce several enemies", dmg=15, cd=0.6, count=2,
                spread=6, speed=780, pierce=4, size=5, dmgtype="phys"),
              S("strike", "Barrage", "A hail of arrows over the horde", dmg=13, cd=2.2, count=9, radius=38,
                target="random", dmgtype="phys"),
              S("summon", "Falcon", "A falcon hunts enemies", cd=8, count=1, dmg=14, life=7, speed=330, size=8,
                color=(200, 160, 90), dmgtype="phys"),
          ])
add_class("black_mage", "Black Mage", 2, "thaumaturge", "int", (120, 100, 220), "Black staff",
          "An improved Thaumaturge.", [
              S("shot", "Firaga", "An exploding fireball", dmg=16, cd=1.0, speed=400, size=10, explode=70,
                element="fire"),
              S("strike", "Thundaga", "Lightning strikes in sequence", dmg=26, cd=2.0, count=3, radius=55, target="random",
                element="lightning"),
              S("cone", "Blizzaga", "A freezing cone of ice", dmg=22, cd=3.0, radius=200, arc=60, element="ice"),
          ])
add_class("time_mage", "Time Mage", 2, "thaumaturge", "int", (200, 180, 255), "Staff and hourglass",
          "Time, space and gravity magic, with support.", [
              S("strike", "Gravity", "Pulls in and crushes enemies", dmg=18, cd=2.6, radius=110, target="nearest",
                pull=380, element="gravity"),
              S("buff", "Haste", "Faster party with shorter cooldowns", cd=11, duration=6, target="party",
                effects={"speed": 0.2, "haste": 0.25}),
              S("strike", "Stop", "Freezes nearby enemies in time", dmg=8, cd=8, radius=220, target="self",
                stun=1.8, element="time"),
          ])
add_class("summoner", "Summoner", 2, "arcanist", "int", (230, 120, 160), "Grimoire",
          "Focused on damage and summons.", [
              S("shot", "Arcane Missile", "Homing projectiles", dmg=10, cd=0.8, count=2, speed=380, homing=4.0,
                element="arcane"),
              S("summon", "Carbuncle", "Summons an ally that attacks", cd=6, count=1, dmg=10, life=8, speed=260,
                size=10, color=(120, 230, 140)),
              S("summon", "Ifrit", "Summons a fire spirit", cd=12, count=1, dmg=26, life=7, speed=240, size=16,
                color=(255, 110, 50), element="fire"),
          ])
add_class("scholar", "Scholar", 2, "arcanist", "int", (150, 220, 250), "Grimoire",
          "Focused on healing and support.", [
              S("shot", "Arcane Missile", "Homing projectiles", dmg=9, cd=0.8, count=2, speed=380, homing=4.0,
                element="arcane"),
              S("heal", "Area Cure", "A strong heal on allies", amount=12, cd=5, radius=350),
              S("buff", "Arcane Shield", "Reduces damage taken by the party", cd=10, duration=6, target="party",
                effects={"dr": 0.3}),
          ])
add_class("monk", "Monk", 2, "pugilist", "agi", (240, 130, 60), "Claws",
          "An improved Pugilist: faster, more critical hits.", [
              S("slash", "Fist Flurry", "Very fast punches", dmg=10, cd=0.25, radius=65, arc=100, knock=60,
                dmgtype="phys"),
              S("strike", "Chakra Burst", "A burst of energy around you", dmg=32, cd=3.0, radius=130,
                target="self", knock=320, dmgtype="phys"),
              S("slash", "Spinning Kick", "A 360° kick", dmg=20, cd=2.0, radius=95, arc=360, knock=160,
                dmgtype="phys"),
          ], ranged=False)
add_class("white_monk", "White Monk", 2, "pugilist", "agi", (250, 240, 200), "Holy fists",
          "A bit less offensive, but with heals and support.", [
              S("slash", "Fist Flurry", "Fast punches", dmg=8, cd=0.28, radius=65, arc=100, knock=60,
                dmgtype="phys"),
              S("heal", "Restoring Chi", "Heals nearby allies", amount=9, cd=5, radius=300),
              S("thrust", "Holy Palm", "A holy wave in a line", dmg=22, cd=1.8, length=170, width=40,
                element="holy", dmgtype="phys"),
          ], ranged=False)
add_class("dragoon", "Dragoon", 2, "lancer", "str", (70, 120, 210), "Long spear",
          "An improved Lancer, with Jump and elemental breath.", [
              S("thrust", "Thrust", "Pierces in a straight line", dmg=20, cd=0.75, length=170, width=28, dmgtype="phys"),
              S("strike", "Jump", "Leaps up and lands on the enemy", dmg=45, cd=4, radius=95, target="nearest",
                delay=0.6, knock=280, dmgtype="phys"),
              S("cone", "Elemental Breath", "Cycles fire, lightning and ice", dmg=18, cd=2.8, radius=190, arc=55,
                cycle=["fire", "lightning", "ice"]),
          ], ranged=False)
add_class("templar", "Templar", 2, "lancer", "str", (220, 210, 140), "Spear and banner",
          "A Lancer with a touch of support.", [
              S("thrust", "Holy Thrust", "A holy piercing strike", dmg=18, cd=0.8, length=160, width=30,
                element="holy", dmgtype="phys"),
              S("slash", "Spear Spin", "Circular strike", dmg=16, cd=2.4, radius=120, arc=360, dmgtype="phys"),
              S("buff", "Blessing", "More defense and damage for the party", cd=12, duration=6, target="party",
                effects={"dr": 0.15, "dmg": 0.1}),
          ], ranged=False)
add_class("ninja", "Ninja", 2, "rogue", "agi", (120, 120, 210), "Kunai and shuriken",
          "Damage and elemental ninjutsu.", [
              S("shot", "Shuriken", "A fan of shuriken", dmg=10, cd=0.6, count=3, spread=12, speed=650, pierce=2,
                size=5, dmgtype="phys"),
              S("cone", "Ninjutsu", "Katon, Raiton and Suiton in sequence", dmg=20, cd=2.5, radius=180, arc=60,
                cycle=["fire", "lightning", "water"]),
              S("strike", "Smoke Bomb", "Stuns nearby enemies", dmg=8, cd=6, radius=140, target="self",
                stun=1.3, element="smoke", dmgtype="phys"),
          ])
add_class("assassin", "Assassin", 2, "rogue", "agi", (170, 60, 100), "Daggers",
          "Pure melee damage and poison.", [
              S("slash", "Twin Blades", "Quick cuts", dmg=12, cd=0.4, radius=70, arc=120, dmgtype="phys"),
              S("shot", "Poisoned Daggers", "Daggers that poison", dmg=8, cd=1.0, count=3, spread=14, speed=620,
                element="poison", dmgtype="phys"),
              S("cloud", "Toxic Cloud", "An area of lingering poison", dmg=6, cd=5, radius=90, duration=4,
                element="poison", dmgtype="phys"),
          ], ranged=False)
add_class("white_mage", "White Mage", 2, "conjurer", "int", (245, 245, 255), "White staff",
          "Focused on healing and support.", [
              S("strike", "Holy", "Holy light on the enemy", dmg=22, cd=1.8, radius=70, target="nearest",
                element="holy"),
              S("heal", "Curaga", "A powerful heal", amount=16, cd=4.5, radius=380),
              S("buff", "Protect", "Reduces damage taken by the party", cd=12, duration=7, target="party",
                effects={"dr": 0.3}),
          ])
add_class("bishop", "Bishop", 2, "conjurer", "int", (90, 170, 220), "Scepter",
          "Focused on water, wind and earth magic.", [
              S("strike", "Natural Elements II", "Stronger water, wind and earth", dmg=22, cd=1.2, count=2,
                radius=70, target="random", cycle=["water", "wind", "earth"]),
              S("cloud", "Tornado", "Wind that keeps cutting", dmg=8, cd=4.5, radius=100, duration=3.5,
                element="wind"),
              S("heal", "Cure", "Heals nearby allies", amount=9, cd=6, radius=320),
          ])
add_class("paladin", "Paladin", 2, "gladiator", "str", (250, 220, 120), "Holy sword and shield",
          "A Gladiator with holy support magic.", [
              S("slash", "Holy Slash", "A holy sword strike", dmg=17, cd=0.8, radius=95, arc=150,
                element="holy", dmgtype="phys"),
              S("buff", "Shield Wall", "Raises the party's defense", cd=12, duration=7, target="party",
                effects={"dr": 0.35}),
              S("heal", "Healing Light", "Heals nearby allies", amount=10, cd=6, radius=300),
          ], ranged=False)
add_class("spellblade", "Spellblade", 2, "gladiator", "str", (230, 90, 200), "Enchanted sword",
          "Less defensive, focused on elemental strikes.", [
              S("slash", "Flame Blade", "A fire slash", dmg=18, cd=0.8, radius=95, arc=150, element="fire",
                dmgtype="phys"),
              S("thrust", "Glacial Blade", "An ice thrust", dmg=20, cd=1.6, length=180, width=34, element="ice",
                dmgtype="phys"),
              S("slash", "Thunder Blade", "A 360° electric spin", dmg=24, cd=2.6, radius=120, arc=360,
                element="lightning", dmgtype="phys"),
          ], ranged=False)
add_class("warrior", "Warrior", 2, "marauder", "str", (210, 60, 50), "War axe",
          "An improved Marauder.", [
              S("slash", "Axe Chop", "A wide, heavy strike", dmg=30, cd=1.3, radius=115, arc=180, knock=220,
                dmgtype="phys"),
              S("shot", "Axe Throw", "An axe that pierces everything", dmg=24, cd=2.4, speed=400, pierce=99,
                size=12, life=1.8, dmgtype="phys"),
              S("buff", "War Cry", "More damage and defense for the party", cd=12, duration=6, target="party",
                effects={"dmg": 0.15, "dr": 0.15}),
          ], ranged=False)
add_class("berserker", "Berserker", 2, "marauder", "str", (255, 80, 80), "Twin axes",
          "Less defense, much more damage.", [
              S("slash", "Furious Chop", "A devastating strike", dmg=36, cd=1.2, radius=120, arc=190, knock=240,
                dmgtype="phys"),
              S("slash", "Whirlwind", "A continuous 360° spin", dmg=16, cd=1.0, radius=100, arc=360, dmgtype="phys"),
              S("buff", "Fury", "Much more damage and speed (self only)", cd=12, duration=6, target="self",
                effects={"dmg": 0.5, "speed": 0.2, "haste": 0.2}),
          ], ranged=False)

# --------------------------------------------------------------------------
# Roles: definem o comportamento (IA dos aliados, aggro) e o scaling base da classe
# (multiplicadores de Vida, Defesa/Defesa mágica, Ataque e Velocidade). Editáveis na aba Index da classes.xlsx.
# --------------------------------------------------------------------------
CLASS_ROLE_DEFS = {
    "All-Rounder": dict(hp=1.0, defense=1.0, attack=1.0, speed=1.0,
                        desc="Classe equilibrada, sem pontos fortes nem fracos. Avança nos inimigos próximos sem se "
                             "afastar muito do grupo (corpo a corpo) ou acompanha o grupo atacando de longe (à "
                             "distância)",
                        desc_en="Balanced class with no strengths or weaknesses. Charges nearby enemies without "
                                "straying far from the party (melee) or follows the party attacking from afar "
                                "(ranged)."),
    "Ranged Assassin": dict(hp=0.8, defense=0.8, attack=1.3, speed=1.1,
                            desc="Mantém distância dos alvos",
                            desc_en="Keeps its distance from the targets."),
    "Support": dict(hp=1.1, defense=1.1, attack=0.8, speed=1.0,
                    desc="Se mantém próximo do grupo",
                    desc_en="Stays close to the party."),
    "Caster": dict(hp=0.8, defense=0.8, attack=1.4, speed=1.0,
                   desc="Mantém distância dos alvos",
                   desc_en="Keeps its distance from the targets."),
    "Melee Assassin": dict(hp=0.7, defense=0.7, attack=1.4, speed=1.2,
                           desc="Mais agressivo que o normal. Pode se afastar mais do grupo de forma a perseguir e "
                                "chegar mais rapido nos alvos",
                           desc_en="More aggressive than normal. Can stray further from the party to chase and "
                                   "reach targets faster."),
    "Tank": dict(hp=1.3, defense=1.3, attack=0.5, speed=0.9,
                 desc="Se mantém próximo do grupo, prioriza inimigos que estão proximos de outros membros. Chama "
                      "mais atenção e aggro dos inimigos",
                 desc_en="Stays close to the party and goes after enemies that are near other members. Draws more "
                         "of the enemies' attention (aggro)."),
    "Healer": dict(hp=1.0, defense=1.1, attack=0.8, speed=1.1,
                   desc="Fica perto do grupo, um pouco atrás, longe dos inimigos. Prioriza curar e proteger",
                   desc_en="Stays close to the party, a bit behind and away from enemies. Focuses on healing and "
                           "protecting."),
}
ROLE_ORDER = list(CLASS_ROLE_DEFS)
ROLE_PT = {"All-Rounder": "Versátil", "Ranged Assassin": "Assassino à distância", "Support": "Suporte",
           "Caster": "Conjurador", "Melee Assassin": "Assassino corpo a corpo", "Tank": "Tanque",
           "Healer": "Curandeiro"}
TANK_THREAT = 1.6     # tanks chamam mais atenção: os inimigos os veem como se estivessem 1,6x mais perto
DEF_TO_DR = 0.5       # cada 0,1 de Defesa acima/abaixo de 1 = +/-5% de redução de todo dano

CLASS_ROLES = {
    "freelancer": "All-Rounder", "freelancer_t2": "All-Rounder", "warfarer": "All-Rounder",
    "archer": "Ranged Assassin", "bard": "Support", "hunter": "Ranged Assassin",
    "thaumaturge": "Caster", "black_mage": "Caster", "time_mage": "Support",
    "arcanist": "Caster", "summoner": "Caster", "scholar": "Healer",
    "pugilist": "Melee Assassin", "monk": "Melee Assassin", "white_monk": "Support",
    "lancer": "All-Rounder", "dragoon": "All-Rounder", "templar": "Support",
    "rogue": "Melee Assassin", "ninja": "Caster", "assassin": "Melee Assassin",
    "conjurer": "Healer", "white_mage": "Healer", "bishop": "Caster",
    "gladiator": "Tank", "paladin": "Tank", "spellblade": "All-Rounder",
    "marauder": "Tank", "warrior": "Tank", "berserker": "Melee Assassin",
}
for _cid, _c in CLASSES.items():
    _c["class_role"] = CLASS_ROLES.get(_cid, "All-Rounder")


def role_of(cid):
    return CLASS_ROLE_DEFS.get(CLASSES[cid].get("class_role"), CLASS_ROLE_DEFS["All-Rounder"])


def role_name(cid, lang="en"):
    r = CLASSES[cid].get("class_role", "All-Rounder")
    return ROLE_PT.get(r, r) if lang == "pt" else r


# --------------------------------------------------------------------------
# Descrições (provisórias) das classes
# --------------------------------------------------------------------------
LORE = {
    "freelancer_t2": "A Novice who walked every basic path to its end. Blends sword, axe and magic, and carries the "
                     "techniques of every basic master it learned from.",
    "warfarer": "A living legend who mastered every school of war and magic. Every weapon is an extension of their "
                "will, and every class's secrets answer their call.",
    "freelancer": "A wanderer with no master and no banner, who learns a little of everything to survive one more "
                  "night. Every hero starts here, and here discovers which path to follow.",
    "archer": "A patient hunter who turns every arrow into a verdict. Keeps the horde at bay and never wastes a shot.",
    "bard": "A roaming archer whose songs fire up allies and break the enemy's will. Every verse is a weapon; "
            "every chorus, a shield.",
    "hunter": "A master of the hunt who reads the battlefield like a trail. Their arrows pierce whole ranks and "
              "their falcon never loses its prey.",
    "thaumaturge": "A scholar of the elements who bends fire, lightning and ice at will. Frail of body, but feared "
                   "by any horde.",
    "black_mage": "A sorcerer who traded caution for raw power. Wherever they go, only ash, ice and the smell of "
                  "thunder remain.",
    "time_mage": "A keeper of the gears of time and space. Speeds up allies, freezes enemies in the moment and "
                 "crushes the horde with gravity.",
    "arcanist": "A grimoire scholar who conjures arcane missiles and protective barriers. Prefers to win with "
                "knowledge rather than strength.",
    "summoner": "An arcanist who made pacts with creatures from other planes. Fights from afar while their summons "
                "tear through the enemy line.",
    "scholar": "A sage who studied anatomy as much as magic. Keeps the party standing with precise heals and "
               "arcane shields.",
    "pugilist": "A nimble brawler who needs no weapons: fists and footwork are enough. Dodges through the horde "
                "and lands quick, precise blows.",
    "monk": "An ascetic who turned their own body into a weapon. Every blow channels chakra, and every kick clears "
            "space in the crowd.",
    "white_monk": "A monk who found balance between fist and healing. Strikes with holy palms and restores allies "
                  "with their own chi.",
    "lancer": "A line soldier who keeps the enemy at spear's point. To them, reach and discipline are worth more "
              "than brute force.",
    "dragoon": "A knight without a mount who inherited the secrets of dragons. Leaps over the horde and answers "
               "with breaths of fire, lightning and ice.",
    "templar": "A consecrated lancer who fights under a holy banner. Their presence strengthens and protects their "
               "brothers in arms.",
    "rogue": "An agile thief who lives on opportunity. Fights up close with a dagger, cutting from the shadows, and "
             "uses smoke bombs and a few thrown knives to escape.",
    "ninja": "A shadow trained in secret schools. Masters shuriken and fire, lightning and water ninjutsu, and "
             "vanishes before the counterattack.",
    "assassin": "A silent blade specialized in poisons. Doesn't look for a fair fight: looks for the fastest "
                "possible end.",
    "conjurer": "A mage of natural forces who commands water, wind and earth. Balances offense and healing to keep "
                "the party alive.",
    "white_mage": "A priestess of light and the party's last refuge. Her heals close wounds and her blessings "
                  "deflect deadly blows.",
    "bishop": "A high-ranking cleric who commands nature's storms. Tornadoes, tides and stones obey their prayer.",
    "gladiator": "An arena veteran who trusts sword and shield. Holds the front line while allies attack.",
    "paladin": "A knight sworn to the light. Combines unshakable defense with holy magic of protection and healing.",
    "spellblade": "A swordsman who enchants their own blade with fire, ice and lightning. Trades some defense for "
                  "devastating elemental strikes.",
    "marauder": "A brutal raider wielding a two-handed axe. Takes punishment like few others and pays it back "
                "twice over.",
    "warrior": "A master of heavy weapons, forged in a thousand battles. Their war cries inspire the party and "
               "their blows split ranks.",
    "berserker": "A warrior seized by fury who abandons all defense. The longer the battle drags on, the more "
                 "dangerous they become.",
}
for _cid, _txt in LORE.items():
    CLASSES[_cid]["lore"] = _txt

# --------------------------------------------------------------------------
# Efeitos dos atributos
# --------------------------------------------------------------------------
BASE_CHAR_DAMAGE = 10     # dano do personagem = 10 + atributo principal da classe (as habilidades causam % disso)
DMG_PER_ATTR = 1.0        # +1 de dano por ponto do atributo da classe da habilidade
ARMOR_PER_STR = 0.1       # FOR: +0,1 de armadura por ponto
DODGE_PER_AGI = 0.1       # AGI: +0,1% de esquiva por ponto
MRES_PER_INT = 0.1        # INT: +0,1 de defesa mágica por ponto
HP_PER_VIT = 5            # VIT: +5 de vida por ponto
REGEN5_PER_VIT = 0.1      # VIT: +0,1 de regeneração de vida a cada 5 s (hp/5s) por ponto
MAX_DODGE = 75.0          # esquiva máxima (%)
CRIT_PER_AGI = 0.1        # AGI: +0,1% de chance crítica por ponto
CRITDMG_PER_STR = 0.2     # FOR: +0,2% de dano crítico por ponto
CDR_PER_INT = 0.1         # INT: +0,1% de cooldown (redução do tempo de recarga) por ponto
BASE_CRIT_DMG = 50.0      # crítico causa +50% de dano (base)
MAX_CRIT = 100.0
MAX_CDR = 60.0            # redução máxima de recarga (%)
# Retorno decrescente das porcentagens (chance crítica, esquiva e recarga): até 1/3 do máximo cada ponto vale
# inteiro; de 1/3 a 2/3 vale metade (1º softcap); acima de 2/3 vale só 1/5 (2º softcap). Dano crítico não tem.
SOFTCAP_STEPS = ((1 / 3, 1.0), (2 / 3, 0.5), (1.0, 0.2))


def soft_pct(raw, cap):
    """Valor efetivo de uma porcentagem com retorno decrescente (raw = soma bruta dos bônus)."""
    if raw <= 0:
        return raw
    out, prev = 0.0, 0.0
    for frac, rate in SOFTCAP_STEPS:
        top = cap * frac
        room = (top - prev) / rate        # quanto de bônus bruto cabe nesta faixa
        if raw <= room:
            return min(cap, out + raw * rate)
        out, raw, prev = top, raw - room, top
    return cap


def soft_marks(cap):
    """(1º softcap, 2º softcap) em % efetiva."""
    return cap * SOFTCAP_STEPS[0][0], cap * SOFTCAP_STEPS[1][0]


GENERAL_LEVEL_STAT = 1    # cada nível geral do personagem dá +1 de FOR, AGI, INT e VIT

BASIC_ORDER = ["archer", "thaumaturge", "arcanist", "pugilist", "lancer", "rogue", "conjurer", "gladiator", "marauder"]
ADVANCED = {b: [c for c, d in CLASSES.items() if d["parent"] == b] for b in BASIC_ORDER}

# Relíquias: habilidades genéricas que o herói pode pegar ao subir de nível na partida
RELICS = [
    S("orbit", "Orbiting Blades", "Blades orbit around you", dmg=8, count=2, radius=75, speed=3.0),
    S("strike", "Lightning Bolt", "Lightning strikes random enemies", dmg=22, cd=2.2, radius=45, target="random",
      element="lightning"),
    S("aura", "Holy Aura", "Continuously hurts nearby enemies", dmg=4, cd=0.5, radius=75, element="holy"),
]
import balance as _bal   # noqa: E402  (dano das relíquias em % do dano do personagem, como as ativas)
for _r in RELICS:
    _bal.tune_active(_r)

# Itens passivos (só o herói): nome -> (descrição, nível máximo)
PASSIVES = {
    "Feather Paws": ("+10% movement speed", 5),
    "Ninth Life": ("+20 max HP", 5),
    "Long Whiskers": ("+30% pickup range", 5),
    "Catnip": ("+12% damage", 5),
    "Cat Nap": ("-8% cooldown time", 5),
    "Warm Milk": ("+2.5 HP regeneration every 5s", 5),
    "Sharp Claws": ("+10% range: melee attacks reach farther and projectiles fly farther", 5),
    "Ball of Yarn": ("+10% area: wider attacks, bigger areas and wider cones", 5),
}
