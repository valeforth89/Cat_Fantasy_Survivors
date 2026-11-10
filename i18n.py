"""Idioma da interface (English / Português).

O jogo é escrito em inglês; com o idioma em português, tudo o que é desenhado na tela passa por tr():
  1. tradução exata (PT);
  2. textos compostos separados por " · " são traduzidos parte a parte;
  3. modelos com partes variáveis (TEMPLATES), ex.: "Kills: {0}" -> "Abates: {0}".
Nomes de personagens continuam como o jogador escreveu; classes e habilidades são traduzidas (i18n_names.py).
"""
import re

LANG = "en"            # "en" ou "pt"
LANGUAGES = {"English": "en", "Português": "pt"}


def set_language(name_or_code):
    global LANG
    LANG = LANGUAGES.get(name_or_code, name_or_code if name_or_code in ("en", "pt") else "en")


def L(en, pt):
    """Escolhe o texto pelo idioma (para trechos montados direto no código)."""
    return pt if LANG == "pt" else en


# ---------------------------------------------------------------------------
# Traduções exatas
# ---------------------------------------------------------------------------
PT = {
    # menu principal / telas
    "survive the horde": "sobreviva à horda", "Start Run": "Iniciar Run", "Stage Select": "Seleção de Fase",
    "Party Setup": "Montar Party", "Inventory": "Inventário", "Configurations": "Configurações", "Quit": "Sair",
    "Back": "Voltar", "FAQ": "FAQ", "PRE-ALPHA": "PRÉ-ALFA", "ALPHA": "ALFA", "CONFIGURATIONS": "CONFIGURAÇÕES",
    "Fullscreen": "Tela cheia", "Difficulty": "Dificuldade", "Damage numbers": "Números de dano",
    "Show FPS": "Mostrar FPS", "FPS limit": "Limite de FPS", "Unlimited": "Ilimitado", "Language": "Idioma", "On": "Ligado", "Off": "Desligado",
    "Easy": "Fácil", "Normal": "Normal", "Hard": "Difícil",
    "Arrows navigate": "Setas navegam", "ENTER / left-right change": "ENTER / esquerda-direita alteram",
    "ESC back": "ESC volta", "ESC cancel": "ESC cancela", "ENTER confirm": "ENTER confirma",
    "STAGE SELECT": "SELEÇÃO DE FASE", "Arrows choose stage": "Setas escolhem a fase", "ENTER start": "ENTER inicia",
    "Start run": "Iniciar run", "SELECTED": "SELECIONADA", "Available": "Disponível", "Enemies": "Inimigos",
    "Rewards": "Recompensas", "Stage difficulty": "Dificuldade da fase",
    "Forest I": "Floresta I", "Forest II": "Floresta II", "Forest III": "Floresta III", "Forest IV": "Floresta IV",
    "Forest V": "Floresta V",
    "Colossal Boar": "Javali Colossal", "Ancient Ent": "Ent Ancestral", "Spider Queen": "Rainha Aranha",
    "Shadow Wolf": "Lobo Sombrio", "Corrupted Guardian": "Guardião Corrompido",
    "Abandoned Town I": "Cidade Abandonada I", "Abandoned Town II": "Cidade Abandonada II",
    "Abandoned Town III": "Cidade Abandonada III", "Abandoned Town IV": "Cidade Abandonada IV",
    "Abandoned Town V": "Cidade Abandonada V",
    "Cathedral I": "Catedral I", "Cathedral II": "Catedral II", "Cathedral III": "Catedral III",
    "Cathedral IV": "Catedral IV", "Cathedral V": "Catedral V",
    "Underground I": "Subterrâneo I", "Underground II": "Subterrâneo II", "Underground III": "Subterrâneo III",
    "Underground IV": "Subterrâneo IV", "Underground V": "Subterrâneo V",
    "Inferno I": "Inferno I", "Inferno II": "Inferno II", "Inferno III": "Inferno III", "Inferno IV": "Inferno IV",
    "Inferno V": "Inferno V", "Inferno": "Inferno", "Inferno Endless": "Inferno Endless",
    "Imp Prince": "Príncipe Diabrete", "Cerberus": "Cérbero", "Magma Colossus": "Colosso de Magma",
    "Demon General": "General Demônio", "Demon King": "Rei Demônio",
    "Imp": "Diabrete", "Hellhound": "Cão Infernal", "Horned Demon": "Demônio Chifrudo", "Salamander": "Salamandra",
    "Infernal Warlock": "Bruxo Infernal",
    "The gates of hell, buried in ash. Imps cackle on the burning rocks.":
        "Os portões do inferno, enterrados em cinzas. Diabretes gargalham sobre as rochas em brasa.",
    "Plains of cracked stone where the hellhounds hunt in packs. Something has three heads.":
        "Planícies de pedra rachada onde os cães infernais caçam em bando. Alguma coisa ali tem três cabeças.",
    "Rivers of magma cut the ground. The salamanders swim in them as if it were water.":
        "Rios de magma cortam o chão. As salamandras nadam neles como se fosse água.",
    "An obsidian fortress lit by hellfire braziers. Its general never lost a battle.":
        "Uma fortaleza de obsidiana iluminada por braseiros do inferno. O general dela nunca perdeu uma batalha.",
    "The throne at the bottom of everything. The Demon King has waited a long time for you.":
        "O trono no fundo de tudo. O Rei Demônio esperou muito tempo por você.",
    "Rat King": "Rei Rato", "Bandit Lord": "Lorde Bandido", "Plague Doctor": "Médico da Peste",
    "Headless Knight": "Cavaleiro Sem Cabeça", "Hollow Mayor": "Prefeito Oco",
    "Grand Gargoyle": "Grande Gárgula", "High Inquisitor": "Alto Inquisidor",
    "Stained Glass Golem": "Golem de Vitral", "Bone Bishop": "Bispo de Ossos", "Fallen Archangel": "Arcanjo Caído",
    "Broodmother": "Matriarca", "Goblin King": "Rei Goblin", "Ooze Titan": "Titã de Gosma",
    "Crystal Golem": "Golem de Cristal", "Deep Wyrm": "Wyrm das Profundezas",
    "Plague Rat": "Rato da Peste", "Feral Hound": "Cão Sarnento", "Bandit Brute": "Bandido Brutamontes",
    "Ghoul": "Carniçal", "Wraith": "Espectro", "Wisp": "Fogo-fátuo", "Cultist": "Cultista", "Gargoyle": "Gárgula",
    "Living Armor": "Armadura Viva", "Fallen Seraph": "Serafim Caído", "Cave Beetle": "Besouro da Caverna",
    "Goblin Miner": "Goblin Minerador", "Rock Golem": "Golem de Pedra", "Slime": "Gosma",
    "Crystal Wyrm": "Verme de Cristal",
    "The town gates hang open. Rats and stray hounds roam the empty streets.":
        "Os portões da cidade estão abertos. Ratos e cães de rua vagam pelas ruas vazias.",
    "Bandits have taken the market square and they don't like visitors.":
        "Bandidos tomaram a praça do mercado e não gostam de visitas.",
    "A sickly fog fills the alleys. The dead no longer stay in their graves.":
        "Uma névoa doentia enche os becos. Os mortos não ficam mais nas covas.",
    "The old barracks burned down. A knight still patrols them, without his head.":
        "O velho quartel pegou fogo. Um cavaleiro ainda faz a ronda, sem a cabeça.",
    "The town hall at night. Its last mayor never left, and neither did his debts.":
        "A prefeitura à noite. O último prefeito nunca foi embora, e as dívidas dele também não.",
    "Candles still burn in the nave. Wisps and cultists guard the doors.":
        "As velas ainda queimam na nave. Fogos-fátuos e cultistas guardam as portas.",
    "Prayers turned into chants. The Inquisition judges anyone who enters.":
        "As preces viraram cânticos. A Inquisição julga quem entra.",
    "Shattered stained glass covers the floor, and the empty armors stand up.":
        "Cacos de vitral cobrem o chão, e as armaduras vazias se levantam.",
    "The crypt below the altar. Its bishop still leads the mass, all bones.":
        "A cripta embaixo do altar. O bispo ainda reza a missa, só ossos.",
    "The bell tower, open to the sky. Something fell from above and never got up.":
        "A torre do sino, aberta para o céu. Algo caiu lá de cima e nunca se levantou.",
    "Mine tunnels lit by lanterns. Beetles swarm and goblins dig.":
        "Túneis de mina iluminados por lanternas. Besouros em enxame e goblins cavando.",
    "The goblins found gold, and a king to keep it.":
        "Os goblins acharam ouro, e um rei para guardá-lo.",
    "Damp caverns where slimes drip from the ceiling.":
        "Cavernas úmidas onde gosmas pingam do teto.",
    "A cave of giant crystals that hum with a deep light.":
        "Uma caverna de cristais gigantes que vibram com uma luz profunda.",
    "The bottom of the world, warm as an oven. The wyrm sleeps here.":
        "O fundo do mundo, quente como um forno. O wyrm dorme aqui.",
    "T tag filter": "T filtro de tag",
    "Continue": "Continuar", "New Save": "Novo Save", "Load Save": "Carregar Save",
    "Dummy": "Boneco", "Great Dummy": "Grande Boneco", "Training Room": "Sala de Treino",
    "Bat": "Morcego", "Wolf": "Lobo", "Boar": "Javali", "Boss": "Chefão", "Skeleton": "Esqueleto", "Zombie": "Zumbi",
    "The forest's edge. Bats, wolves and boars fight over the main trail.":
        "A borda da floresta. Morcegos, lobos e javalis disputam a trilha principal.",
    "The woods grow thick and the packs grow larger. Something ancient stirs among the trees.":
        "A mata fica densa e as matilhas crescem. Algo antigo se move entre as árvores.",
    "Webs cover the branches and boars roam in herds. Little light reaches the ground.":
        "Teias cobrem os galhos e javalis andam em bandos. Pouca luz chega ao chão.",
    "Howls echo through the mist. The wolves here have faced other heroes before.":
        "Uivos ecoam na névoa. Os lobos daqui já enfrentaram outros heróis.",
    "The heart of the forest. Everything here has been corrupted, even its protector.":
        "O coração da floresta. Tudo aqui foi corrompido, até o seu protetor.",
    # party
    "PARTY SETUP": "MONTAR PARTY", "HERO": "HERÓI", "ACTIVE": "ATIVO", "RESERVE": "RESERVA",
    "Hero (always in the party)": "Herói (sempre na party)", "Active in the party": "Ativo na party",
    "In reserve": "Na reserva", "Remove": "Remover", "Activate": "Ativar", "Class": "Classe", "Loadout": "Loadout",
    "Rename": "Renomear", "Dismiss": "Dispensar", "Attributes  (hover for details)": "Atributos  (passe o mouse)",
    "Loadout  (L to edit)": "Loadout  (L para editar)", "New name": "Novo nome",
    "Arrows select": "Setas selecionam", "SPACE activate/remove": "ESPAÇO ativa/remove", "ENTER class": "ENTER classe",
    "L loadout": "L loadout", "R rename": "R renomeia", "N recruit": "N recruta", "DEL dismiss": "DEL dispensa",
    "STR": "FOR", "AGI": "AGI", "INT": "INT", "VIT": "VIT", "HP": "Vida", "Armor": "Armadura",
    "Magic def.": "Def. mágica", "Magic defense": "Defesa mágica", "Dodge": "Esquiva", "Defense": "Defesa",
    "Crit chance": "Chance crít.", "Crit damage": "Dano crít.", "Cooldown": "Recarga", "Regen. HP/5s": "Regen. Vida/5s",
    "Physical damage": "Dano físico", "Magic damage": "Dano mágico", "Critical chance": "Chance crítica",
    "Critical damage": "Dano crítico", "Regeneration": "Regeneração", "Speed": "Velocidade",
    "Pickup range": "Alcance de coleta", "Area": "Área", "Healing": "Cura", "Duration": "Duração",
    "HP recovered continuously during the run.": "Vida recuperada continuamente durante a run.",
    "Chance to fully negate a PHYSICAL hit taken.": "Chance de anular totalmente um golpe FÍSICO recebido.",
    "Subtracted from every PHYSICAL hit taken (a hit always deals at least 1).":
        "Subtraída de todo golpe FÍSICO recebido (um golpe sempre causa ao menos 1).",
    "Subtracted from every MAGICAL or ELEMENTAL hit taken (minimum 1).":
        "Subtraída de todo golpe MÁGICO ou ELEMENTAL recebido (mínimo 1).",
    "Chance for each hit to be critical and deal the extra critical damage.":
        "Chance de cada golpe ser crítico e causar o dano crítico extra.",
    "Extra damage of a critical hit (applied before the target's armor/magic defense).":
        "Dano extra de um golpe crítico (aplicado antes da armadura/defesa mágica do alvo).",
    "Reduces all damage taken by %, after armor/magic defense. Max 75% (with buffs).":
        "Reduz em % todo dano recebido, depois da armadura/defesa mágica. Máx. 75% (com bônus).",
    # classes
    "Starting": "Inicial", "or": "ou", "new": "nova", "locked": "bloqueada", "Progression": "Progressão",
    "Build loadout": "Montar loadout", "Select class": "Escolher classe", "Current class": "Classe atual",
    "MASTERED": "MASTERIZADA", "Unlocks": "Libera", "Level": "Nível", "Mastery": "Maestria",
    "ENTER / double-click select": "ENTER / clique duplo escolhe", "P level progression": "P progressão",
    "Starting class": "Classe inicial", "Basic class": "Classe básica", "Advanced class": "Classe avançada",
    "Balanced": "Equilibrado", "Melee": "Corpo a corpo", "Ranged": "À distância",
    "Actives": "Ativas", "Passives": "Passivas", "ACTIVES": "ATIVAS", "PASSIVES": "PASSIVAS",
    "Basic attack": "Ataque básico", "(empty)": "(vazio)", "(leave empty)": "(deixar vazio)",
    "Arrows select slot": "Setas escolhem o espaço", "ENTER open options": "ENTER abre opções",
    "DEL / right-click clear": "DEL / botão direito limpa",
    "Skill tags:": "Tags das habilidades:",
    "Appears": "Aparece", "Forest": "Floresta", "Abandoned Town": "Cidade Abandonada", "Cathedral": "Catedral",
    "Underground": "Subterrâneo",
    "• Every 2 minutes the difficulty goes up one tier: +50% enemy HP, +30% strength, +50% resistance and +25% EXP and gold.":
        "• A cada 2 minutos a dificuldade sobe um nível: +50% de vida, +30% de força, +50% de resistência dos inimigos e +25% de EXP e gold.",
    "• Every minute a Super Elite or an Elite Squad appears.": "• A cada minuto aparece um Super Elite ou um Esquadrão de Elite.",
    "• Gold is proportional to the time survived, with the reward of the current tier.":
        "• O gold é proporcional ao tempo sobrevivido, com a recompensa do nível atual.",
    "Every minute: a bat horde plus a Super Elite or an Elite Squad. The boss comes with 2 random classes (their weapons and skills) and summons bats.":
        "A cada minuto: uma horda de morcegos e um Super Elite ou um Esquadrão de Elite. O chefão vem com 2 classes aleatórias (armas e habilidades delas) e invoca morcegos.", "Coming soon": "Em breve", "coming soon": "em breve", "ENDLESS": "ENDLESS",
    "Forest Endless": "Floresta Endless", "Abandoned Town Endless": "Cidade Abandonada Endless",
    "Cathedral Endless": "Catedral Endless", "Underground Endless": "Subterrâneo Endless", "Bosses in rotation": "Chefões em rodízio", "M.Def": "Def.M", "Arm.": "Arm.", "Spd.": "Vel.",
    "Clear stage V of a biome to unlock its Endless and stage I of the next biome":
        "Conclua a fase V de um bioma para liberar o Endless dele e a fase I do próximo bioma",
    "Best time: -": "Melhor tempo: -", "Arrows choose stage": "Setas escolhem a fase", "SPACE": "ESPAÇO", "Start": "Iniciar", "BLACKSMITH": "FERREIRO", "JEWELER": "JOALHEIRO",
    "Upgrade the weapon and helmet of the party": "Melhore a arma e o capacete da party",
    "Fragments and gold stored in the chest": "Fragmentos e gold guardados no baú",
    "ESC back to the camp": "ESC volta ao acampamento", "CAMP": "ACAMPAMENTO",
    "WASD move  ·  walk into or click a place to open it  ·  E / ENTER interact  ·  ESC main menu":
        "WASD move  ·  encoste ou clique em um lugar para abrir  ·  E / ENTER interage  ·  ESC menu principal",
    "Accessories": "Acessórios",
    "Accessories (necklace, rings, bracer, trinkets): talk to the Jeweler at the camp.": "Acessórios (colar, anéis, bracelete, berloques): fale com o Joalheiro no acampamento.",
    "Necklaces, rings, bracers and trinkets will be crafted and equipped here.": "Colares, anéis, braceletes e berloques serão criados e equipados aqui.",
    "Coming in a future version": "Chega numa versão futura", "Cleared": "Concluída",
    "T tag highlight": "T destacar tag",
    "Total": "Total", "Sum of every level of the class": "Soma de todos os níveis da classe",
    "ENTER equip": "ENTER equipa", "ESC back to slots": "ESC volta aos espaços",
    "Green = level reached": "Verde = nível alcançado", "Arrows / mouse wheel scroll": "Setas / roda do mouse rolam",
    "PgUp/PgDn page": "PgUp/PgDn paginam", "Arm": "Arm", "MDef": "DMag", "Ddg%": "Esq%", "Reg": "Reg",
    "Crit%": "Crít%", "CDmg%": "DCrít%", "CD%": "Rec%",
    "Base values - attributes, items and run level raise them":
        "Valores base - atributos, itens e o nível na run os aumentam",
    "Passive · always active while equipped": "Passiva · sempre ativa enquanto equipada",
    "Versatile apprentice. Unlocks the basic classes at Lv 10.": "Aprendiz versátil. Libera as classes básicas no Lv 10.",
    "Ranged physical damage.": "Dano físico à distância.",
    "Elemental magic of fire, lightning and ice.": "Magia elemental de fogo, raio e gelo.",
    "Damage spells with a touch of support.": "Magias de dano com um toque de suporte.",
    "Melee physical damage.": "Dano físico corpo a corpo.", "Mid-range physical damage.": "Dano físico a média distância.",
    "Damage and crowd control.": "Dano e controle de grupo.",
    "Fast melee physical damage and critical hits.": "Dano físico corpo a corpo rápido e golpes críticos.",
    "Melee damage and crowd control.": "Dano corpo a corpo e controle de grupo.",
    "An improved Pugilist: faster, more critical hits.": "Um Pugilist aprimorado: mais rápido e com mais críticos.",
    "Light footwork: faster movement and quicker strikes": "Jogo de pés leve: anda mais rápido e golpeia mais depressa",
    "Throws a fan of knives that slow": "Arremessa um leque de facas que desaceleram",
    "Spins the blades in a full circle around you": "Gira as lâminas em um círculo completo ao seu redor",
    "Quick cuts with the dagger": "Cortes rápidos com a adaga", "Dagger": "Adaga",
    "Healing plus wind, earth and water magic.": "Cura e magias de vento, terra e água.",
    "Defense and physical damage.": "Defesa e dano físico.", "Defense and heavy physical damage.": "Defesa e dano físico pesado.",
    "A bit less offensive than the Hunter, but buffs the party.": "Um pouco menos ofensivo que o Hunter, mas fortalece a party.",
    "An improved Archer.": "Um Archer aprimorado.", "An improved Thaumaturge.": "Um Thaumaturge aprimorado.",
    "Time, space and gravity magic, with support.": "Magias de tempo, espaço e gravidade, com suporte.",
    "Focused on damage and summons.": "Focado em dano e invocações.", "Focused on healing and support.": "Focado em cura e suporte.",
    "An improved Pugilist.": "Um Pugilist aprimorado.",
    "A bit less offensive, but with heals and support.": "Um pouco menos ofensivo, mas com curas e suporte.",
    "An improved Lancer, with Jump and elemental breath.": "Um Lancer aprimorado, com Salto e sopro elemental.",
    "A Lancer with a touch of support.": "Um Lancer com um toque de suporte.",
    "Damage and elemental ninjutsu.": "Dano e ninjutsu elemental.", "Pure melee damage and poison.": "Dano corpo a corpo puro e veneno.",
    "Focused on water, wind and earth magic.": "Focado em magias de água, vento e terra.",
    "A Gladiator with holy support magic.": "Um Gladiator com magia sagrada de suporte.",
    "Less defensive, focused on elemental strikes.": "Menos defensivo, focado em golpes elementais.",
    "An improved Marauder.": "Um Marauder aprimorado.", "Less defense, much more damage.": "Menos defesa, muito mais dano.",
    # habilidades (rótulos)
    "Projectile": "Projétil", "Arc strike": "Golpe em arco", "Thrust": "Estocada", "Area impact": "Impacto em área",
    "Cone": "Cone", "Aura": "Aura", "Orbit": "Órbita", "Heal": "Cura", "Buff": "Bônus", "Summon": "Invocação",
    "Lingering area": "Área persistente", "Physical": "Físico", "Magical": "Mágico",
    "Nearest": "Mais próximo", "Random": "Aleatório", "Self": "Em si mesmo", "Party": "Party",
    "Fire": "Fogo", "Ice": "Gelo", "Lightning": "Raio", "Water": "Água", "Wind": "Vento", "Earth": "Terra",
    "Poison": "Veneno", "Holy": "Sagrado", "Arcane": "Arcano", "Sound": "Som", "Gravity": "Gravidade",
    "Time": "Tempo", "Smoke": "Fumaça", "Ready": "Pronta", "Always active": "Sempre ativa",
    "Unavailable - member is down": "Indisponível - membro caído", "no bonus yet": "sem bônus ainda",
    "no items yet": "nenhum item ainda", "Skills": "Habilidades", "Run items": "Itens da run",
    "Bonuses gained this run": "Bônus obtidos nesta run",
    "Basic attack with the class weapon": "Ataque básico com a arma da classe",
    # run
    "PAUSED": "PAUSADO", "LEVEL UP!": "SUBIU DE NÍVEL!", "Allies improve on their own every level.":
        "Os aliados melhoram sozinhos a cada nível.",
    "ESC resume": "ESC continua", "A turn off": "A desliga",
    "Sharp Claws": "Garras Afiadas", "Ball of Yarn": "Novelo de Lã",
    "+10% range: melee attacks reach farther and projectiles fly farther": "+10% de alcance: golpes corpo a corpo alcançam mais longe e projéteis voam mais longe",
    "+10% area: wider attacks, bigger areas and wider cones": "+10% de área: ataques mais largos, áreas maiores e cones mais abertos",
    "+1 Gold": "+1 Gold", "Adds 1 gold to your account right away": "Soma 1 de gold à sua conta na hora",
    "Mystery Box": "Caixa Misteriosa", "Activates a random power-up right away": "Ativa um power-up aleatório na hora",
    "[A] Pick my choice automatically on every next level-up of this run": "[A] Escolher automaticamente a minha opção nos próximos level ups desta run",
    "Range": "Alcance", "Q end the run (the party keeps EXP and fragments)": "Q encerra a run (a party mantém a EXP e os fragmentos)",
    "mouse wheel / Up-Down: more stats": "roda do mouse / cima-baixo: mais status",
    "ENTER back to menu": "ENTER volta ao menu", "R new run with the same party": "R nova run com a mesma party",
    "Damage": "Dano", "Taken": "Recebido", "Damage Done": "Dano Causado", "Damage Taken": "Dano Recebido",
    "Healing Done": "Cura Feita", "No damage dealt yet": "Nenhum dano causado ainda",
    "No damage taken yet": "Nenhum dano recebido ainda", "No healing done yet": "Nenhuma cura feita ainda",
    "Regeneration ": "Regeneração ", "Dodge!": "Esquiva!", "Back!": "Voltou!", "All damage": "Todo dano",
    "Max HP": "Vida máx.", "Max HP (+)": "Vida máx. (+)", "Equipment": "Equipamentos",
    "Weapon and helmet are fixed to the current class and cannot be swapped. Upgrades are saved per class.":
        "Arma e capacete são fixos da classe atual e não podem ser trocados. As melhorias ficam salvas por classe.",
    "Evolved class": "Classe evoluída", "Ultimate class": "Classe suprema", "Crowd Control": "Controle de Grupo",
    "No crowd control yet": "Nenhum controle de grupo ainda", "Stun": "Atordoar", "Freeze": "Congelar",
    "Taunt": "Provocar", "Weaken": "Enfraquecer", "Knockdown": "Derrubar", "Chill": "Gelo", "Knockback": "Empurrão", "Pull": "Puxão", "Capstone (M)": "Capstone (M)",
    "Capstone · only in the 5th class slot (own class) or the 5th mastery slot (another class)":
        "Capstone · só no 5º espaço da classe (a da própria classe) ou no 5º espaço de maestria (de outra classe)",
    "Evolved Novice  ·  into Warfarer when all advanced classes are mastered":
        "Novice evoluído  ·  vira Warfarer quando todas as classes avançadas forem masterizadas",
    "Ultimate evolution of the Novice": "Evolução suprema do Novice",
    "Evolves into any basic class at Lv 10  ·  into Freelancer when all basic classes are mastered":
        "Evolui para qualquer classe básica no Lv 10  ·  vira Freelancer quando todas as básicas forem masterizadas",
    "Choose a passive from a mastered class": "Escolha uma passiva de uma classe masterizada",
    "C / T open filters": "C / T abrem os filtros",
    "Arrows / letter keys choose": "Setas / letras escolhem", "ENTER apply": "ENTER aplica",
    "TAB other filter": "TAB outro filtro", "ESC close": "ESC fecha",
    "No skill matches these filters.": "Nenhuma habilidade com esses filtros.",
    "Choose a active from a mastered class": "Escolha uma ativa de uma classe masterizada",
    "Evolved Novice: masters every basic class. Its slots accept skills of mastered basic classes.":
        "Novice evoluído: domina todas as classes básicas. Seus espaços aceitam habilidades das básicas masterizadas.",
    "The ultimate fighter: masters every class. Its slots accept skills of any mastered class.":
        "O lutador supremo: domina todas as classes. Seus espaços aceitam habilidades de qualquer classe masterizada.",
    "A wide, swift arc with the longsword": "Um arco amplo e veloz com a espada longa",
    "Two axes that pierce enemies": "Dois machados que atravessam inimigos",
    "A long lunge that pierces the line": "Uma investida longa que atravessa a fila",
    "A blinding burst that slows enemies in front": "Uma explosão ofuscante que desacelera os inimigos à frente",
    "Instinct takes over: more damage and faster skills": "O instinto assume: mais dano e habilidades mais rápidas",
    "Smashes the ground and stuns around you": "Esmaga o chão e atordoa ao seu redor",
    "A homing bolt of arcane energy": "Um disparo teleguiado de energia arcana", "Patches up nearby allies": "Remenda os aliados próximos",
    "A full spin with the longsword": "Um giro completo com a espada longa",
    "Blades rain on five random enemies": "Lâminas chovem sobre cinco inimigos aleatórios",
    "A devastating sweep of the whole arsenal": "Uma varredura devastadora com todo o arsenal",
    "Three spears that pierce everything in their path": "Três lanças que atravessam tudo no caminho",
    "Leaps onto the nearest enemy with a huge impact": "Salta sobre o inimigo mais próximo com um impacto enorme",
    "A torrent of dragon fire": "Uma torrente de fogo de dragão",
    "A war song: the party deals more damage and moves faster": "Uma canção de guerra: a party causa mais dano e se move mais rápido",
    "Four blades orbit around you": "Quatro lâminas orbitam ao seu redor", "A rallying cry that heals the party": "Um grito de união que cura a party",
    "Lightning strikes four random enemies": "Raios atingem quatro inimigos aleatórios", "Sets the ground ablaze": "Incendeia o chão",
    "A divine thrust that pierces the horizon": "Uma estocada divina que atravessa o horizonte",
    "Longsword": "Espada longa", "Arsenal": "Arsenal",
    "No active members": "Nenhum membro ativo", "Passives": "Passivas", "no passives equipped": "nenhuma passiva equipada",
    "mouse wheel / PgUp-PgDn: more": "roda do mouse / PgUp-PgDn: mais", "Fragments this run  (inventory total)":
        "Fragmentos nesta run  (total no inventário)", "no fragments yet": "nenhum fragmento ainda",
    "Active buffs": "Bônus ativos", "EXP base": "EXP base", "Gold base": "Gold base",
    "Enemy HP base": "Vida dos inimigos base", "Strength base": "Força base", "Resistance base": "Resistência base",
    "Black staff": "Cajado negro", "Bow": "Arco", "Bow and harp": "Arco e harpa", "Claws": "Garras", "Daggers": "Adagas",
    "Enchanted sword": "Espada encantada", "Fist weapons": "Armas de punho", "Grimoire": "Grimório",
    "Holy fists": "Punhos sagrados", "Holy sword and shield": "Espada e escudo sagrados", "Knives": "Facas",
    "Kunai and shuriken": "Kunai e shuriken", "Long spear": "Lança longa", "Longbow": "Arco longo", "Scepter": "Cetro",
    "Short sword": "Espada curta", "Spear": "Lança", "Spear and banner": "Lança e estandarte", "Staff": "Cajado",
    "Staff and hourglass": "Cajado e ampulheta", "Sword and shield": "Espada e escudo", "Twin axes": "Machados gêmeos",
    "Two-handed axe": "Machado de duas mãos", "War axe": "Machado de guerra", "TAB switch tab": "TAB troca de aba", "Locked": "Bloqueado", "Other": "Outros", "Fish Feast": "Banquete de Peixe",
    "Restores 30 HP": "Recupera 30 de vida", " has appeared!": " apareceu!", "An elite ": "Um elite ",
    "Feather Paws": "Patinhas de Pena", "Ninth Life": "Nona Vida", "Long Whiskers": "Bigodes Longos", "Catnip": "Erva-de-Gato",
    "Cat Nap": "Soneca", "Warm Milk": "Leite Morno",
    "+10% movement speed": "+10% de velocidade de movimento", "+20 max HP": "+20 de vida máxima",
    "+30% pickup range": "+30% de alcance de coleta", "+12% damage": "+12% de dano",
    "-8% cooldown time": "-8% de tempo de recarga", "+2.5 HP regeneration every 5s": "+2,5 de regeneração a cada 5 s",
    "STAGE CLEAR!": "FASE CONCLUÍDA!", "RUN OVER": "FIM DA RUN",
    # inventário / equipamentos
    "INVENTORY": "INVENTÁRIO", "Party equipment": "Equipamentos da party", "Fragments": "Fragmentos",
    "Upgrade": "Melhorar", "MAX": "MÁX", "Coming soon": "Em breve", "Necklace": "Colar", "Ring": "Anel",
    "Bracer": "Bracelete", "Trinket": "Berloque", "Weapon": "Arma", "Helmet": "Capacete",
    "Fixed to the class": "Fixo da classe",
    "Weapon and helmet are fixed to the current class and cannot be swapped.":
        "Arma e capacete são fixos da classe atual e não podem ser trocados.",
    "Upgrades are saved per class: switching back keeps them.":
        "As melhorias ficam salvas por classe: ao voltar para ela, continuam lá.",
    "Other classes (saved upgrades)": "Outras classes (melhorias salvas)", "none yet": "nenhuma ainda",
    "Click a member to view their equipment": "Clique em um membro para ver os equipamentos",
    # FAQ
    "FAQ  -  How the game works": "FAQ  -  Como o jogo funciona",
    "Click a topic or use Up/Down": "Clique em um tópico ou use cima/baixo",
    "mouse wheel / PgUp PgDn to scroll": "roda do mouse / PgUp PgDn para rolar",
}

# descrições das habilidades
PT.update({
    "Slashes enemies in front": "Corta os inimigos à frente", "Throws stones at the nearest enemy": "Atira pedras no inimigo mais próximo",
    "A fast stab in a line": "Uma estocada rápida em linha", "Kicks dirt that slows enemies in front": "Chuta terra que desacelera os inimigos à frente",
    "Throws two daggers at the nearest enemy": "Arremessa duas adagas no inimigo mais próximo",
    "Catches a breath and recovers HP": "Recupera o fôlego e a vida", "A full spin with the short sword": "Um giro completo com a espada curta",
    "A shout that speeds up and strengthens the party": "Um grito que acelera e fortalece a party",
    "Hits the nearest enemy with the pommel and stuns it": "Acerta o inimigo mais próximo com o pomo e o atordoa",
    "A wide, practiced slash": "Um corte amplo e treinado", "Arrow that pierces enemies": "Flecha que atravessa inimigos",
    "Arrows rain down on several enemies": "Flechas chovem sobre vários inimigos", "Fires two arrows at once": "Dispara duas flechas de uma vez",
    "A heavy arrow that pierces and slows": "Uma flecha pesada que atravessa e desacelera", "A fan of five arrows": "Um leque de cinco flechas",
    "A burning arrow that explodes on impact": "Uma flecha em chamas que explode no impacto",
    "Sharpens your aim: more damage, shorter cooldowns": "Afia a mira: mais dano e recargas menores",
    "Sets traps under random enemies that stun": "Arma armadilhas sob inimigos aleatórios que atordoam",
    "A dense hail of arrows over the horde": "Uma densa saraivada de flechas sobre a horda",
    "A lightning arrow that pierces everything": "Uma flecha de raio que atravessa tudo", "Arrows that slow": "Flechas que desaceleram",
    "+20% damage and +10% speed for the party": "+20% de dano e +10% de velocidade para a party",
    "A sound wave that slows everything around": "Uma onda sonora que desacelera tudo ao redor",
    "A soft song that puts nearby enemies to sleep": "Uma canção suave que faz os inimigos próximos dormirem",
    "Three notes fired from the harp": "Três notas disparadas da harpa", "A melody that heals the party": "Uma melodia que cura a party",
    "A fast tune: party moves and recovers faster": "Uma música rápida: a party se move e recarrega mais rápido",
    "A dissonant chord that keeps hurting": "Um acorde dissonante que continua ferindo",
    "A resonant arrow that pierces many enemies": "Uma flecha ressonante que atravessa muitos inimigos",
    "The last note explodes on four enemies": "A última nota explode em quatro inimigos",
    "Two arrows that pierce several enemies": "Duas flechas que atravessam vários inimigos", "A hail of arrows over the horde": "Uma saraivada de flechas sobre a horda",
    "A falcon hunts enemies": "Um falcão caça os inimigos", "A long-range shot that pierces the line": "Um tiro de longo alcance que atravessa a linha",
    "Traps that bite and hold enemies": "Armadilhas que mordem e prendem inimigos", "A wolf fights by your side": "Um lobo luta ao seu lado",
    "Five piercing arrows in a fan": "Cinco flechas perfurantes em leque",
    "Focus on the prey: more damage and faster shots": "Foco na presa: mais dano e tiros mais rápidos",
    "An arrow that explodes in fire": "Uma flecha que explode em fogo", "A storm of arrows covers the field": "Uma tempestade de flechas cobre o campo",
    "Fireball that sets enemies ablaze": "Bola de fogo que incendeia os inimigos", "Cycles fire, lightning and ice": "Alterna fogo, raio e gelo",
    "A small lightning bolt on the nearest enemy": "Um pequeno raio no inimigo mais próximo", "A shard of ice that pierces": "Um fragmento de gelo que atravessa",
    "A wave of fire in front of you": "Uma onda de fogo à sua frente", "Lightning strikes three random enemies": "Raios atingem três inimigos aleatórios",
    "A ring of frost bursts around you": "Um anel de gelo explode ao seu redor", "A column of fire that keeps burning": "Uma coluna de fogo que continua queimando",
    "Three bolts that jump through enemies": "Três raios que saltam entre inimigos", "A meteor falls from the sky": "Um meteoro cai do céu",
    "An exploding fireball": "Uma bola de fogo explosiva", "Lightning strikes in sequence": "Raios caem em sequência",
    "A freezing cone of ice": "Um cone congelante de gelo", "A toxic cloud that rots enemies": "Uma nuvem tóxica que apodrece os inimigos",
    "A blinding explosion on the nearest enemy": "Uma explosão ofuscante no inimigo mais próximo", "A cutting blast of wind": "Uma rajada cortante de vento",
    "A violent earthquake around you": "Um terremoto violento ao seu redor", "A beam of arcane power": "Um feixe de poder arcano",
    "Freezes three enemies solid": "Congela três inimigos por completo", "The ultimate spell: a massive explosion": "A magia suprema: uma explosão enorme",
    "Pulls in and crushes enemies": "Puxa e esmaga os inimigos", "Faster party with shorter cooldowns": "Party mais rápida e com recargas menores",
    "Freezes nearby enemies in time": "Congela no tempo os inimigos próximos", "Slows down time for enemies in front": "Desacelera o tempo dos inimigos à frente",
    "Two comets fall on random enemies": "Dois cometas caem em inimigos aleatórios", "Bends time: much shorter cooldowns": "Dobra o tempo: recargas bem menores",
    "A strong gravity well that pulls enemies in": "Um forte poço gravitacional que puxa os inimigos", "A rift where time hurts": "Uma fenda onde o tempo fere",
    "Rewinds allies' wounds": "Rebobina os ferimentos dos aliados", "A swarm of meteors falls on the horde": "Um enxame de meteoros cai sobre a horda",
    "Homing projectiles": "Projéteis teleguiados", "Reduces damage taken by the party": "Reduz o dano recebido pela party",
    "A bolt of pure mana that pierces": "Um disparo de mana pura que atravessa", "A circle of runes that hurts enemies inside": "Um círculo de runas que fere os inimigos dentro",
    "Orbs of mana orbit around you": "Orbes de mana orbitam ao seu redor", "Concentration: shorter cooldowns and more damage": "Concentração: recargas menores e mais dano",
    "Releases arcane energy around you": "Libera energia arcana ao seu redor", "A spring of mana heals nearby allies": "Uma fonte de mana cura os aliados próximos",
    "Four runes that chase enemies": "Quatro runas que perseguem inimigos", "Two large arcane explosions": "Duas grandes explosões arcanas",
    "Summons an ally that attacks": "Invoca um aliado que ataca", "Summons a fire spirit": "Invoca um espírito de fogo",
    "Summons an ice spirit": "Invoca um espírito de gelo", "Ramuh calls lightning on three enemies": "Ramuh chama raios sobre três inimigos",
    "Titan crushes the ground around you": "Titan esmaga o chão ao seu redor", "Summons two wind spirits": "Invoca dois espíritos do vento",
    "Leviathan unleashes a tidal wave": "Leviathan libera um maremoto", "The phoenix's fire heals the party": "O fogo da fênix cura a party",
    "Bahamut's breath devastates the field": "O sopro de Bahamut devasta o campo", "A strong heal on allies": "Uma cura forte nos aliados",
    "Shares knowledge: party casts faster and hits harder": "Compartilha conhecimento: a party conjura mais rápido e bate mais forte",
    "A gentle heal for the party": "Uma cura suave para a party", "A piercing bolt of ruin": "Um disparo perfurante de ruína",
    "A cloud of noxious gas": "Uma nuvem de gás nocivo", "Consecrates the ground: party takes less damage": "Consagra o chão: a party recebe menos dano",
    "Burns the nearest enemy with arcane fire": "Queima o inimigo mais próximo com fogo arcano", "A powerful blessing that heals everyone": "Uma bênção poderosa que cura todos",
    "A quick flurry of punches": "Uma rajada rápida de socos", "A burst of force around you": "Uma explosão de força ao seu redor",
    "A rising punch that launches the enemy": "Um soco ascendente que lança o inimigo", "A quick sequence of jabs": "Uma sequência rápida de jabs",
    "Hardens the body to take less damage": "Endurece o corpo para receber menos dano", "An open-palm strike that pushes in a line": "Um golpe de palma aberta que empurra em linha",
    "A spinning kick around you": "Um chute giratório ao seu redor", "Fires a wave of ki that pierces": "Dispara uma onda de ki que atravessa",
    "Punches the ground and stuns around you": "Soca o chão e atordoa ao seu redor", "An endless barrage of punches": "Uma saraivada interminável de socos",
    "Very fast punches": "Socos muito rápidos", "A burst of energy around you": "Uma explosão de energia ao seu redor", "A 360° kick": "Um chute de 360°",
    "A flying kick in a line": "Uma voadora em linha", "Focuses the chi: more damage and faster strikes": "Concentra o chi: mais dano e golpes mais rápidos",
    "A palm strike that stuns": "Um golpe de palma que atordoa", "Fires a blast of aura that pierces": "Dispara uma rajada de aura que atravessa",
    "A field of chi that hurts nearby enemies": "Um campo de chi que fere os inimigos próximos", "A fiery spinning kick": "Um chute giratório flamejante",
    "A devastating finishing blow around you": "Um golpe final devastador ao seu redor", "Fast punches": "Socos rápidos",
    "Heals nearby allies": "Cura os aliados próximos", "A holy wave in a line": "Uma onda sagrada em linha", "A holy punch": "Um soco sagrado",
    "A chant that protects and speeds up the party": "Um cântico que protege e acelera a party", "A calm breath that heals allies": "Uma respiração calma que cura os aliados",
    "A holy spinning kick": "Um chute giratório sagrado", "A shield of spirit that blocks damage": "Um escudo de espírito que bloqueia dano",
    "A wide beam of holy light": "Um feixe largo de luz sagrada", "A pulse of holy energy around you": "Um pulso de energia sagrada ao seu redor",
    "Pierces in a straight line": "Perfura em linha reta", "Circular strike": "Golpe circular", "A long-reach lunge": "Uma investida de longo alcance",
    "Sweeps the spear in a wide arc": "Varre com a lança em um arco amplo", "Throws a javelin that pierces": "Arremessa um dardo que atravessa",
    "A deep thrust that stuns": "Uma estocada profunda que atordoa", "A defensive formation for the party": "Uma formação defensiva para a party",
    "Charges through a long line of enemies": "Avança por uma longa fila de inimigos", "Javelins fall on random enemies": "Dardos caem em inimigos aleatórios",
    "Rapid thrusts in front of you": "Estocadas rápidas à sua frente", "Leaps up and lands on the enemy": "Salta e aterrissa sobre o inimigo",
    "A fang-like piercing thrust": "Uma estocada perfurante como uma presa", "A higher, stronger jump": "Um salto mais alto e mais forte",
    "Sweeps the long spear in front": "Varre com a lança longa à frente", "Moves like a wyvern: speed and damage": "Move-se como uma wyvern: velocidade e dano",
    "Breathes fire like a dragon": "Cospe fogo como um dragão", "Throws a spear of lightning that pierces everything": "Arremessa uma lança de raio que atravessa tudo",
    "Dives onto three enemies": "Mergulha sobre três inimigos", "A holy piercing strike": "Um golpe perfurante sagrado",
    "More defense and damage for the party": "Mais defesa e dano para a party", "Raises the banner: more damage for the party": "Ergue o estandarte: mais dano para a party",
    "Consecrates the ground under enemies": "Consagra o chão sob os inimigos", "Throws a lance of light that pierces": "Arremessa uma lança de luz que atravessa",
    "Smites the nearest enemy with light": "Fulmina o inimigo mais próximo com luz", "Divine protection for the party": "Proteção divina para a party",
    "Heals allies with a holy touch": "Cura os aliados com um toque sagrado", "Holy judgment falls on three enemies": "O julgamento sagrado cai sobre três inimigos",
    "A fan of knives that slow": "Um leque de facas que desaceleram", "Stuns nearby enemies": "Atordoa os inimigos próximos",
    "A precise cut from behind": "Um corte preciso pelas costas", "Scatters spikes that hurt enemies walking over": "Espalha espinhos que ferem quem pisa",
    "A knife coated in poison": "Uma faca envenenada", "Moves faster with shorter cooldowns": "Move-se mais rápido com recargas menores",
    "Seven knives in a wide fan": "Sete facas em um leque amplo", "Hits the nearest enemy hard": "Acerta com força o inimigo mais próximo",
    "Appears behind three random enemies": "Aparece atrás de três inimigos aleatórios", "Spins with both blades": "Gira com as duas lâminas",
    "A fan of shuriken": "Um leque de shurikens", "Katon, Raiton and Suiton in sequence": "Katon, Raiton e Suiton em sequência",
    "Five kunai in a fan": "Cinco kunais em leque", "Two shadow clones fight for you": "Dois clones das sombras lutam por você",
    "Fire release: a cone of flames": "Liberação de fogo: um cone de chamas", "Lightning release on three enemies": "Liberação de raio em três inimigos",
    "Water release: a flooding vortex": "Liberação de água: um vórtice inundante", "Body flicker: very fast movement": "Shunshin: movimento muito rápido",
    "A giant shuriken that cuts through everything": "Uma shuriken gigante que corta tudo", "Quick cuts": "Cortes rápidos",
    "Daggers that poison": "Adagas que envenenam", "An area of lingering poison": "Uma área de veneno persistente",
    "Strikes the nearest enemy from the shadows": "Ataca o inimigo mais próximo das sombras", "Coats the blades: more damage and faster cuts": "Envenena as lâminas: mais dano e cortes mais rápidos",
    "Dashes through enemies in a line": "Dispara através dos inimigos em linha", "Strangles the nearest enemy, stunning it": "Estrangula o inimigo mais próximo, atordoando-o",
    "A whirl of blades around you": "Um redemoinho de lâminas ao seu redor", "A poisoned dagger that pierces": "Uma adaga envenenada que atravessa",
    "Marks four enemies for death": "Marca quatro inimigos para a morte", "Cycles water, wind and earth": "Alterna água, vento e terra",
    "A bolt of water": "Um disparo de água", "A gust of wind that pushes enemies": "Uma rajada de vento que empurra os inimigos",
    "A spike of rock under the nearest enemy": "Um espinho de pedra sob o inimigo mais próximo", "A light, frequent heal": "Uma cura leve e frequente",
    "A whirlpool that keeps dragging enemies": "Um redemoinho que continua arrastando inimigos", "The ground shakes around you": "O chão treme ao seu redor",
    "A cyclone that cuts everything inside": "Um ciclone que corta tudo dentro dele", "A huge wave that sweeps enemies away": "Uma onda enorme que varre os inimigos",
    "Holy light on the enemy": "Luz sagrada sobre o inimigo", "A powerful heal": "Uma cura poderosa",
    "A magic barrier that protects and speeds up the party": "Uma barreira mágica que protege e acelera a party",
    "A light, frequent heal on the party": "Uma cura leve e frequente na party", "A homing bolt of light": "Um disparo teleguiado de luz",
    "Beams of light on three enemies": "Feixes de luz sobre três inimigos", "A huge heal for everyone": "Uma cura enorme para todos",
    "A ring of light that hurts nearby enemies": "Um anel de luz que fere os inimigos próximos", "A massive burst of holy light": "Uma enorme explosão de luz sagrada",
    "Stronger water, wind and earth": "Água, vento e terra mais fortes", "Wind that keeps cutting": "Vento que continua cortando",
    "Rocks fall on four enemies": "Pedras caem sobre quatro inimigos", "A lance of pressurized water": "Uma lança de água pressurizada",
    "A strong gale in front of you": "Um vendaval forte à sua frente", "A pool of mud that hurts and holds": "Uma poça de lama que fere e prende",
    "Purifies and heals allies": "Purifica e cura os aliados", "A landslide crushes enemies around you": "Um deslizamento esmaga os inimigos ao seu redor",
    "A huge whirlpool that tears enemies apart": "Um enorme redemoinho que despedaça os inimigos", "Sword strike": "Golpe de espada",
    "Raises the party's defense": "Aumenta a defesa da party", "Bashes the nearest enemy with the shield": "Golpeia o inimigo mais próximo com o escudo",
    "A fast counterattack": "Um contra-ataque rápido", "Recovers HP in the middle of the fight": "Recupera vida no meio da luta",
    "Throws a spare sword that pierces": "Arremessa uma espada reserva que atravessa", "A spinning sword strike": "Um golpe giratório de espada",
    "Raises the shield: much less damage taken": "Ergue o escudo: muito menos dano recebido", "A crushing hit on the nearest enemy": "Um golpe esmagador no inimigo mais próximo",
    "The finishing slash of an arena champion": "O corte final de um campeão da arena", "A holy sword strike": "Um golpe de espada sagrado",
    "Faith hardens the shield": "A fé endurece o escudo", "A holy strike on the nearest enemy": "Um golpe sagrado no inimigo mais próximo",
    "A sacred circle that burns nearby enemies": "Um círculo sagrado que queima os inimigos próximos", "Charges forward with the holy shield": "Avança com o escudo sagrado",
    "A divine shield over the whole party": "Um escudo divino sobre toda a party", "A sanctuary that heals allies": "Um santuário que cura os aliados",
    "Holy judgment on three enemies": "Julgamento sagrado sobre três inimigos", "A fire slash": "Um corte de fogo", "An ice thrust": "Uma estocada de gelo",
    "A 360° electric spin": "Um giro elétrico de 360°", "A slash of cutting wind": "Um corte de vento cortante",
    "A heavy thrust charged with earth": "Uma estocada pesada carregada de terra", "A sword wave of arcane energy": "Uma onda de espada de energia arcana",
    "Enchants the sword: more damage, faster strikes": "Encanta a espada: mais dano, golpes mais rápidos", "A slash coated in poison": "Um corte envenenado",
    "A holy 360° slash": "Um corte sagrado de 360°", "Fire, ice and lightning strike three enemies": "Fogo, gelo e raio atingem três inimigos",
    "A wide, heavy strike": "Um golpe amplo e pesado", "An axe that pierces everything": "Um machado que atravessa tudo",
    "Cleaves through enemies in front": "Fende os inimigos à frente", "More damage and speed for a while": "Mais dano e velocidade por um tempo",
    "Slams the axe on the ground and stuns": "Bate o machado no chão e atordoa", "Recovers HP through sheer rage": "Recupera vida pela pura fúria",
    "Throws two axes that pierce everything": "Arremessa dois machados que atravessam tudo", "A brutal 360° swing": "Um golpe brutal de 360°",
    "A massive overhead chop": "Um golpe descendente enorme", "Splits the earth in a line": "Racha a terra em linha",
    "Overpowers the nearest enemy": "Sobrepuja o inimigo mais próximo", "An iron will: much less damage taken": "Vontade de ferro: muito menos dano recebido",
    "A heavy, wide cleave": "Um golpe pesado e amplo", "Shakes the ground and stuns around you": "Sacode o chão e atordoa ao seu redor",
    "Recovers HP through resolve": "Recupera vida pela determinação", "Throws three axes that pierce everything": "Arremessa três machados que atravessam tudo",
    "A decimating 360° swing": "Um golpe devastador de 360°", "A devastating strike": "Um golpe devastador", "A continuous 360° spin": "Um giro contínuo de 360°",
    "Much more damage and speed (self only)": "Muito mais dano e velocidade (só em si)", "A frenzy of blood: faster and quicker": "Um frenesi de sangue: mais rápido e ágil",
    "A reckless, huge swing": "Um golpe enorme e imprudente", "Leaps onto the nearest enemy": "Salta sobre o inimigo mais próximo",
    "Throws both axes": "Arremessa os dois machados", "An aura of rage that hurts nearby enemies": "Uma aura de fúria que fere os inimigos próximos",
    "Recovers HP in the bloodbath": "Recupera vida no banho de sangue", "An unstoppable 360° storm of axes": "Uma tempestade imparável de machados em 360°",
    "Blades orbit around you": "Lâminas orbitam ao seu redor", "Lightning strikes random enemies": "Raios atingem inimigos aleatórios",
    "Continuously hurts nearby enemies": "Fere continuamente os inimigos próximos",
})

# descrições longas das classes (lore)
PT.update({
    "A wanderer with no master and no banner, who learns a little of everything to survive one more night. Every hero starts here, and here discovers which path to follow.":
        "Um andarilho sem mestre e sem bandeira, que aprende um pouco de tudo para sobreviver a mais uma noite. Todo herói começa aqui, e aqui descobre qual caminho seguir.",
})

# nomes curtos das passivas (usados em "Physical Damage [Gladiator]")
PASSIVE_SHORT_PT = {
    "Physical Damage": "Dano Físico", "Magic Damage": "Dano Mágico", "All Damage": "Todo Dano", "Max HP": "Vida Máx.",
    "Max HP+": "Vida Máx.+", "Speed": "Velocidade", "Cooldown": "Recarga", "Critical Chance": "Chance Crítica",
    "Critical Damage": "Dano Crítico", "Defense": "Defesa", "Area": "Área", "Healing": "Cura", "Duration": "Duração",
    "Regeneration": "Regeneração", "Pickup Range": "Alcance de Coleta", "Armor": "Armadura", "Magic Defense": "Defesa Mágica",
    "Dodge": "Esquiva", "STR": "FOR", "AGI": "AGI", "INT": "INT", "VIT": "VIT",
}

# ---------------------------------------------------------------------------
# Modelos: {0}, {1}... = partes variáveis (traduzidas pelo dicionário exato quando houver)
# ---------------------------------------------------------------------------
TEMPLATES = [
    ("ver. {0} (Pre-Alpha)", "ver. {0} (Pré-Alfa)"), ("ver. {0} (Alpha)", "ver. {0} (Alfa)"),
    ("Auto level-up: {0}", "Escolha automática: {0}"),
    ("No time limit: the run goes on until the hero falls or you quit. It starts at {0} difficulty.",
     "Sem limite de tempo: a run continua até o herói cair ou você encerrar. Começa na dificuldade da {0}."),
    ("• Every 2 minutes a boss appears (with 2 random classes), taking turns among the bosses of {0} I to V and following the scaling.",
     "• A cada 2 minutos aparece um chefão (com 2 classes aleatórias), revezando entre os chefões da {0} I a V e acompanhando o escalonamento."), ("Best time: {0}", "Melhor tempo: {0}"),
    ("Clear {0} to unlock.", "Conclua {0} para liberar."), ("-{0}% cooldown", "-{0}% de recarga"),
    ("+{0}% movement speed", "+{0}% de velocidade de movimento"), ("+{0} max HP", "+{0} de vida máxima"),
    ("+{0}% pickup range", "+{0}% de alcance de coleta"), ("+{0}% damage", "+{0}% de dano"),
    ("-{0}% cooldown time", "-{0}% de tempo de recarga"), ("+{0} HP/5s regeneration", "+{0} de vida/5s"),
    ("+{0}% range", "+{0}% de alcance"), ("+{0}% area", "+{0}% de área"),
    ("Party: {0}", "Party: {0}"), ("Stage: {0}", "Fase: {0}"), ("Difficulty: {0}", "Dificuldade: {0}"),
    ("{0} gold", "{0} gold"), ("+ Recruit new member  ({0} gold)", "+ Recrutar novo membro  ({0} gold)"),
    ("Active: {0}   ·   Members: {1}", "Ativos: {0}   ·   Membros: {1}"),
    ("Level {0} / {1}", "Nível {0} / {1}"), ("Level {0}", "Nível {0}"), ("Passives equipped: {0}", "Passivas equipadas: {0}"),
    ("Class level: {0}", "Nível da classe: {0}"), ("mastery at Lv {0}", "maestria no Lv {0}"),
    ("Current class: {0}", "Classe atual: {0}"), ("CLASSES - {0}", "CLASSES - {0}"), ("LOADOUT - {0}", "LOADOUT - {0}"),
    ("PROGRESSION - {0}", "PROGRESSÃO - {0}"), ("Basic (Novice Lv {0})", "Básicas (Novice Lv {0})"),
    ("Advanced (pick 1 of 2, Lv {0})", "Avançadas (escolha 1 de 2, Lv {0})"),
    ("Evolves at Lv {0} into:  {1}  OR  {2}", "Evolui no Lv {0} para:  {1}  OU  {2}"),
    ("Evolves into any basic class at Lv {0}", "Evolui para qualquer classe básica no Lv {0}"),
    ("Requires {0} Lv {1} (current: {2})", "Requer {0} Lv {1} (atual: {2})"),
    ("Actives ({0})", "Ativas ({0})"), ("Passives ({0})", "Passivas ({0})"),
    ("Active: {0}", "Ativa: {0}"), ("Passive: {0}", "Passiva: {0}"),
    ("Choose a active from {0}", "Escolha uma ativa de {0}"), ("Choose a passive from {0}", "Escolha uma passiva de {0}"),
    ("Unlocks at class Lv {0}", "Liberada no Lv {0} da classe"), ("Unlocks at {0} Lv {1}", "Liberada em {0} Lv {1}"),
    ("{0} Lv {1} (current class)  ·  saved for this class", "{0} Lv {1} (classe atual)  ·  salvo para esta classe"),
    ("{0} Lv {1}  ·  saved for this class", "{0} Lv {1}  ·  salvo para esta classe"),
    ("{0} Lv {1} (current class)", "{0} Lv {1} (classe atual)"),
    ("Bonuses up to Lv {0}: {1}  ... (see Progression)", "Bônus até o Lv {0}: {1}  ... (veja Progressão)"),
    ("Slot 1 - weapon basic attack (fixed)", "Espaço 1 - ataque básico da arma (fixo)"),
    ("slot {0}", "espaço {0}"), ("{0}  (fixed)", "{0}  (fixo)"),
    ("Permanent bonuses earned / class total:   {0}", "Bônus permanentes obtidos / total da classe:   {0}"),
    # stat dicas
    ("STR (Strength): {0}", "FOR (Força): {0}"), ("AGI (Agility): {0}", "AGI (Agilidade): {0}"),
    ("INT (Intelligence): {0}", "INT (Inteligência): {0}"), ("VIT (Vitality): {0}", "VIT (Vitalidade): {0}"),
    ("+{0} damage on skills from {1} classes", "+{0} de dano nas habilidades de classes de {1}"),
    ("Your current class ({0}) uses {1}: its skills gain +{2} damage.", "Sua classe atual ({0}) usa {1}: suas habilidades ganham +{2} de dano."),
    ("Your current class ({0}) doesn't use {1}; applies to mastery skills from {2} classes.",
     "Sua classe atual ({0}) não usa {1}; vale para habilidades de maestria de classes de {2}."),
    ("{0} (Balanced) uses the average of STR/AGI/INT: +{1} damage.", "{0} (Equilibrado) usa a média de FOR/AGI/INT: +{1} de dano."),
    ("+{0} armor ({1} per point)", "+{0} de armadura ({1} por ponto)"),
    ("+{0}% critical damage ({1}% per point)", "+{0}% de dano crítico ({1}% por ponto)"),
    ("+{0}% dodge ({1}% per point)", "+{0}% de esquiva ({1}% por ponto)"),
    ("+{0}% critical chance ({1}% per point)", "+{0}% de chance crítica ({1}% por ponto)"),
    ("+{0} healing on heals from INT classes", "+{0} de cura nas curas de classes de INT"),
    ("+{0} magic defense ({1} per point)", "+{0} de defesa mágica ({1} por ponto)"),
    ("+{0}% cooldown ({1}% per point)", "+{0}% de recarga ({1}% por ponto)"),
    ("+{0} base HP ({1} per point), before the class multiplier", "+{0} de vida base ({1} por ponto), antes do multiplicador da classe"),
    ("+{0} HP/5s regeneration ({1} per point)", "+{0} de regeneração Vida/5s ({1} por ponto)"),
    ("Source: {0}", "Origem: {0}"), ("Max HP: {0}", "Vida máx.: {0}"), ("Armor: {0}", "Armadura: {0}"),
    ("Magic defense: {0}", "Defesa mágica: {0}"), ("Dodge: {0}", "Esquiva: {0}"), ("Defense: {0}", "Defesa: {0}"),
    ("Regeneration: {0} HP every 5 s", "Regeneração: {0} de vida a cada 5 s"),
    ("Critical chance: {0}", "Chance crítica: {0}"), ("Critical damage: {0}", "Dano crítico: {0}"),
    ("Cooldown: {0}", "Recarga: {0}"), ("Reduces the cooldown of all skills (max {0}).", "Reduz a recarga de todas as habilidades (máx. {0})."),
    ("{0} class: {1}", "Classe {0}: {1}"), ("Equipment: {0}", "Equipamentos: {0}"),
    ("{0} from the {1} class", "{0} da classe {1}"), ("+{0}% from passives", "+{0}% das passivas"),
    ("+{0}% from equipment", "+{0}% dos equipamentos"),
    # habilidades (dicas)
    ("Target: {0}", "Alvo: {0}"), ("Damage: {0}", "Dano: {0}"), ("Healing: {0}", "Cura: {0}"),
    ("Damage per second: {0}", "Dano por segundo: {0}"), ("Damage per tick: {0}", "Dano por pulso: {0}"),
    ("Damage per hit: {0}", "Dano por acerto: {0}"), ("Scales with: {0}", "Escala com: {0}"),
    ("Critical: {0}% chance · +{1}% damage", "Crítico: {0}% de chance · +{1}% de dano"),
    ("Tick interval: {0}", "Intervalo: {0}"), ("Count: {0}", "Quantidade: {0}"), ("Range: {0}", "Alcance: {0}"),
    ("Area (radius): {0}", "Área (raio): {0}"), ("Arc: {0}", "Arco: {0}"), ("Width: {0}", "Largura: {0}"),
    ("Spread: {0}", "Abertura: {0}"), ("Pierce: {0}", "Perfuração: {0}"), ("Speed: {0}", "Velocidade: {0}"),
    ("Duration: {0}", "Duração: {0}"), ("Lifetime: {0}", "Tempo de vida: {0}"),
    ("Slow: {0}% for {1}s", "Lentidão: {0}% por {1}s"), ("Stun: {0}", "Atordoamento: {0}"), ("Pull: {0}", "Puxão: {0}"),
    ("Explosion: {0}", "Explosão: {0}"), ("Homing: {0}", "Teleguiado: {0}"), ("Delay: {0}", "Atraso: {0}"),
    ("Buff damage: {0}", "Bônus de dano: {0}"), ("Buff speed: {0}", "Bônus de velocidade: {0}"),
    ("Buff cooldown: {0}", "Bônus de recarga: {0}"), ("Buff defense: {0}", "Bônus de defesa: {0}"),
    ("Recharging - {0}s left", "Recarregando - faltam {0}s"), ("Used by {0} ({1})", "Usada por {0} ({1})"),
    ("{0}   Lv {1}", "{0}   Lv {1}"),
    # run
    ("Kills: {0}", "Abates: {0}"), ("Elite kills: {0}", "Abates de elite: {0}"), ("Run EXP: {0}", "EXP da run: {0}"),
    ("{0}:  {1}  ·  {2} DPS", "{0}:  {1}  ·  {2} DPS"), ("{0}:  {1}  ·  {2} DTPS", "{0}:  {1}  ·  {2} DTPS"),
    ("{0}:  {1}  ·  {2} HPS", "{0}:  {1}  ·  {2} HPS"),
    ("Party full ({0}/{1})", "Party cheia ({0}/{1})"), ("The party is full ({0} members).", "A party está cheia ({0} membros)."),
    ("Requires all basic classes mastered ({0})", "Requer todas as classes básicas masterizadas ({0})"),
    ("Requires all advanced classes mastered ({0})", "Requer todas as classes avançadas masterizadas ({0})"),
    ("Skill tags: {0}", "Tags das habilidades: {0}"), ("Tags: {0}", "Tags: {0}"), ("{0}  (Capstone)", "{0}  (Capstone)"),
    ("Bleed: {0}% of the hit per second for 3s", "Sangramento: {0}% do golpe por segundo por 3s"),
    ("Crowd Control: {0} s", "Controle de Grupo: {0} s"), ("{0}:  {1} s", "{0}:  {1} s"),
    ("Not enough gold: need {0}, you have {1}.", "Gold insuficiente: precisa de {0}, você tem {1}."),
    ("Evolution of {0}  ·  alternative: {1}", "Evolução de {0}  ·  alternativa: {1}"),
    ("CURRENT Lv {0}", "ATUAL Lv {0}"), ("Attribute: {0}", "Atributo: {0}"),
    ("Every minute: a bat horde plus a Super Elite or an Elite Squad. Regular enemies grow stronger until {0} The boss comes with 2 random classes (their weapons and skills) and summons bats.",
     "A cada minuto: uma horda de morcegos e um Super Elite ou um Esquadrão de Elite. Os inimigos comuns ficam mais fortes até {0} O chefão vem com 2 classes aleatórias (armas e habilidades delas) e invoca morcegos."),
    ("Bat hordes every minute. Regular enemies grow stronger until {0} The boss summons bats.",
     "Hordas de morcegos a cada minuto. Os inimigos comuns ficam mais fortes até {0} O chefão invoca morcegos."),
    ("at {0} the boss {1} appears and the timer stops. Defeat it to clear the stage.",
     "aos {0} o chefão {1} aparece e o tempo para. Derrote-o para concluir a fase."),
    ("Stage clear: {0} gold (not cleared: proportional to time played)",
     "Fase concluída: {0} gold (sem concluir: proporcional ao tempo jogado)"),
    ("Enemy HP {0}", "Vida dos inimigos {0}"), ("Strength {0}", "Força {0}"), ("Resistance {0}", "Resistência {0}"),
    ("Gold {0}", "Gold {0}"), ("Damage (start > {0})", "Dano (início > {0})"), ("HP (start > {0})", "Vida (início > {0})"),
    ("Damage Done {0}", "Dano Causado {0}"), ("Damage Taken {0}", "Dano Recebido {0}"), ("Healing Done {0}", "Cura Feita {0}"),
    ("HP x{0}", "Vida x{0}"), ("Defense {0}", "Defesa {0}"), ("Speed x{0}", "Velocidade x{0}"),
    ("Party of {0}: {1}x enemies, HP {2}", "Party de {0}: {1}x inimigos, vida {2}"),
    ("{0} difficulty: HP x{1} amount x{2}", "Dificuldade {0}: vida x{1} quantidade x{2}"),
    ("Regeneration (HP/5s): {0}", "Regeneração (Vida/5s): {0}"),
    ("{0} +{1} (placeholder)", "{0} +{1} (provisório)"),
    ("class levels {0}", "níveis de classe {0}"),
    ("Raw total {0}%", "Total bruto {0}%"), ("max {0}%", "máx. {0}%"),
    ("softcaps at {0}% (bonus worth 1/2) and {1}% (worth 1/5)", "softcaps em {0}% (bônus vale 1/2) e {1}% (vale 1/5)"),
    ("{0} from VIT", "{0} da VIT"), ("{0} from class levels = {1}", "{0} dos níveis de classe = {1}"),
    ("{0} from class levels", "{0} dos níveis de classe"), ("{0} from passives = {1}", "{0} das passivas = {1}"), ("passives {0}", "passivas {0}"),
    ("equipment {0}", "equipamentos {0}"), ("max {0}", "máx. {0}"), ("base {0}", "base {0}"),
    ("character level {0}", "nível do personagem {0}"), ("STR {0}", "FOR {0}"),
    ("{0} base + {1} from VIT + {2} from class levels{3}", "{0} base + {1} da VIT + {2} dos níveis de classe{3}"),
    ("Run level {0}", "Nível da run {0}"), ("Kills {0}", "Abates {0}"), ("Elite kills {0}", "Abates de elite {0}"),
    ("EXP {0}", "EXP {0}"), ("Gold +{0}", "Gold +{0}"), ("Time {0}:{1}", "Tempo {0}:{1}"),
    ("Each party member gained {0} EXP", "Cada membro da party ganhou {0} EXP"), ("total: {0}", "total: {0}"),
    ("+{0} gold ({1}% of the stage time)", "+{0} gold ({1}% do tempo da fase)"), ("+{0} gold from drops", "+{0} gold de drops"), ("+{0} gold", "+{0} gold"),
    ("New stage unlocked: {0}", "Nova fase liberada: {0}"), ("Fragments: {0}", "Fragmentos: {0}"),
    ("{0} MASTERED! Its skills are now available to other classes", "{0} MASTERIZADA! As habilidades dela agora valem para outras classes"),
    ("New classes: {0}", "Novas classes: {0}"), ("New skills: {0}", "Novas habilidades: {0}"),
    ("+1 {0} Fragment", "+1 Fragmento de {0}"), ("Elite {0}", "Elite {0}"),
    ("{0}  —  {1}", "{0}  —  {1}"), ("{0}  (NEW)", "{0}  (NOVA)"), ("{0}  (RELIC)", "{0}  (RELÍQUIA)"),
    # inventário / equipamentos
    ("{0} Fragment", "Fragmento de {0}"), ("Owned: {0}", "Possui: {0}"),
    ("Class fragments: {0}   ·   dropped by Elite enemies, used to upgrade each class's equipment",
     "Fragmentos de classe: {0}   ·   dropados por elites, usados para melhorar os equipamentos de cada classe"),
    ("Dropped by Elite {0} enemies (any enemy can spawn as an elite of a class you have already unlocked).",
     "Dropado por inimigos Elite {0} (qualquer inimigo pode surgir como elite de uma classe que você já liberou)."),
    ("Used to upgrade {0} weapon and helmet.", "Usado para melhorar a arma e o capacete de {0}."),
    ("Upgrade  ({0} {1} Fragments)", "Melhorar  ({0} Fragmentos de {1})"),
    ("You have {0} {1} Fragments", "Você tem {0} Fragmentos de {1}"),
    ("{0}'s equipment  ·  {1}", "Equipamentos de {0}  ·  {1}"),
    ("Upgraded to {0}!", "Melhorado para {0}!"),
    ("Not enough {0} Fragments: need {1}, you have {2}.", "Fragmentos de {0} insuficientes: precisa de {1}, você tem {2}."),
    ("Already at the maximum upgrade (+10).", "Já está na melhoria máxima (+10)."),
    ("Next: {0}", "Próximo: {0}"),
    ("Locked - clear {0}", "Bloqueada - conclua {0}"),
    # passivas
    ("{0} [{1}]", None),   # tratado em tr() (nome curto da passiva + classe)
    ("{0} joined the group for {1} gold (active).", "{0} entrou no grupo por {1} gold (ativo)."),
    ("{0} joined the group for {1} gold (reserve).", "{0} entrou no grupo por {1} gold (reserva)."),
    ("{0} (placeholder)", "{0} (provisório)"),
    ("{0} Bat", "{0} Morcego"), ("{0} Wolf", "{0} Lobo"), ("{0} Boar", "{0} Javali"),
    ("{0} Skeleton", "{0} Esqueleto"), ("{0} Zombie", "{0} Zumbi"),
    ("{0} Plague Rat", "{0} Rato da Peste"), ("{0} Feral Hound", "{0} Cão Sarnento"),
    ("{0} Bandit Brute", "{0} Bandido Brutamontes"), ("{0} Ghoul", "{0} Carniçal"), ("{0} Wraith", "{0} Espectro"),
    ("{0} Wisp", "{0} Fogo-fátuo"), ("{0} Cultist", "{0} Cultista"), ("{0} Gargoyle", "{0} Gárgula"),
    ("{0} Living Armor", "{0} Armadura Viva"), ("{0} Fallen Seraph", "{0} Serafim Caído"),
    ("{0} Cave Beetle", "{0} Besouro da Caverna"), ("{0} Goblin Miner", "{0} Goblin Minerador"),
    ("{0} Rock Golem", "{0} Golem de Pedra"), ("{0} Slime", "{0} Gosma"), ("{0} Crystal Wyrm", "{0} Verme de Cristal"),
    ("{0} Imp", "{0} Diabrete"), ("{0} Hellhound", "{0} Cão Infernal"), ("{0} Horned Demon", "{0} Demônio Chifrudo"),
    ("{0} Salamander", "{0} Salamandra"), ("{0} Infernal Warlock", "{0} Bruxo Infernal"),
    ("{0} Dummy", "Boneco {0}"),
    ("{0}: {1}", "{0}: {1}"),   # genérico "Rótulo: valor" (o rótulo é traduzido pelo dicionário)
]


def _compile(tpl):
    parts = re.split(r"(\{\d\})", tpl)
    rx = "".join("(.+?)" if re.fullmatch(r"\{\d\}", p) else re.escape(p) for p in parts)
    order = [int(p[1]) for p in parts if re.fullmatch(r"\{\d\}", p)]
    return re.compile(rx + r"\Z", re.S), order


import i18n_names as _names   # noqa: E402  (classes, habilidades e passivas em PT)
_names.register(PT, PASSIVE_SHORT_PT)
# textos em PT que citam classes pelo nome em inglês ("Evolução suprema do Novice") passam a usar o nome em PT
for _k, _v in PT.items():
    PT[_k] = _names.localize_classes(_v)
TEMPLATES = [(en, _names.localize_classes(pt) if pt else pt) for en, pt in TEMPLATES]
_COMPILED = [(_compile(en), en, pt) for en, pt in TEMPLATES]
_COMPILED_SEP = [c for c in _COMPILED if "·" in c[1] or "  +  " in c[1]]      # modelos que contêm separadores
_COMPILED_PLAIN = [c for c in _COMPILED if c not in _COMPILED_SEP]
_SEP = re.compile(r"(\s+·\s+|\s+\+\s+)")
_CACHE = {}


def _group(g):
    if g in PT or _SEP.search(g) or any(rx.match(g) for (rx, _), _e, _p in _COMPILED_PLAIN):
        return tr(g)
    return _names.basic_pt(g) or _names.passive_pt(g) or _names.localize_classes(g)   # "Super Novice" -> "Super Novato"


def tr(s):
    """Traduz um texto da interface para o idioma atual."""
    if LANG != "pt" or not isinstance(s, str) or not s.strip():
        return s
    hit = _CACHE.get(s)
    if hit is not None:
        return hit
    out = PT.get(s)
    if out is None:
        stripped = s.strip()
        if stripped != s and stripped in PT:
            out = s.replace(stripped, PT[stripped])
    for group in (_COMPILED_SEP, None, _COMPILED_PLAIN):
        if out is not None:
            break
        if group is None:   # textos compostos "A  ·  B  ·  C" / "A + B": parte a parte
            if _SEP.search(s):
                pieces = _SEP.split(s)
                out = "".join(p if _SEP.fullmatch(p) else tr(p) for p in pieces)
            continue
        for (rx, order), en, pt in group:
            m = rx.match(s)
            if not m:
                continue
            if pt is None:   # passiva "Nome [Classe]"
                name, cls = m.group(1), m.group(2)
                pn = PASSIVE_SHORT_PT.get(name) or _names.passive_pt(name)
                cn = _names.CLASS_PT.get(cls)
                if pn or cn:
                    out = f"{pn or name} [{cn or cls}]"
                    break
                continue
            vals = {}
            for gi, idx in enumerate(order):
                vals[idx] = _group(m.group(gi + 1))
            out = pt
            for idx, v in vals.items():
                out = out.replace("{%d}" % idx, v)
            break
    if out is None:   # golpe básico "Basic Attack (Bow)" / passiva montada pelas partes ("Fire Mastery")
        out = _names.basic_pt(s) or _names.passive_pt(s)
    if out is None:
        out = s
    if len(_CACHE) > 5000:
        _CACHE.clear()
    _CACHE[s] = out
    return out


# lore das classes (descrições longas)
_LORE_PT = {
    "archer": "Um caçador paciente que transforma cada flecha em uma sentença. Mantém a horda à distância e nunca desperdiça um tiro.",
    "bard": "Um arqueiro andarilho cujas canções inflamam os aliados e quebram a vontade do inimigo. Cada verso é uma arma; cada refrão, um escudo.",
    "hunter": "Um mestre da caça que lê o campo de batalha como uma trilha. Suas flechas atravessam fileiras inteiras e seu falcão nunca perde a presa.",
    "thaumaturge": "Um estudioso dos elementos que dobra fogo, raio e gelo à vontade. Frágil de corpo, mas temido por qualquer horda.",
    "black_mage": "Um feiticeiro que trocou a cautela pelo poder bruto. Por onde passa, restam só cinzas, gelo e cheiro de trovão.",
    "time_mage": "Um guardião das engrenagens do tempo e do espaço. Acelera aliados, congela inimigos no instante e esmaga a horda com gravidade.",
    "arcanist": "Um estudioso de grimórios que conjura mísseis arcanos e barreiras protetoras. Prefere vencer com conhecimento a vencer com força.",
    "summoner": "Um arcanista que fez pactos com criaturas de outros planos. Luta de longe enquanto suas invocações rasgam a linha inimiga.",
    "scholar": "Um sábio que estudou anatomia tanto quanto magia. Mantém a party de pé com curas precisas e escudos arcanos.",
    "pugilist": "Um brigão ágil que não precisa de armas: punhos e jogo de pés bastam. Desvia pela horda e acerta golpes rápidos e precisos.",
    "monk": "Um asceta que transformou o próprio corpo em arma. Cada golpe canaliza chakra, e cada chute abre espaço na multidão.",
    "white_monk": "Um monge que encontrou o equilíbrio entre o punho e a cura. Golpeia com palmas sagradas e restaura os aliados com o próprio chi.",
    "lancer": "Um soldado de linha que mantém o inimigo na ponta da lança. Para ele, alcance e disciplina valem mais que força bruta.",
    "dragoon": "Um cavaleiro sem montaria que herdou os segredos dos dragões. Salta sobre a horda e responde com sopros de fogo, raio e gelo.",
    "templar": "Um lanceiro consagrado que luta sob um estandarte sagrado. Sua presença fortalece e protege seus irmãos de armas.",
    "rogue": "Um ladrão ágil que vive de oportunidades. Luta de perto com a adaga, cortando das sombras, e usa bombas de fumaça e algumas facas arremessadas para escapar.",
    "ninja": "Uma sombra treinada em escolas secretas. Domina shurikens e ninjutsus de fogo, raio e água, e some antes do contra-ataque.",
    "assassin": "Uma lâmina silenciosa especializada em venenos. Não busca uma luta justa: busca o fim mais rápido possível.",
    "conjurer": "Um mago das forças naturais que comanda água, vento e terra. Equilibra ataque e cura para manter a party viva.",
    "white_mage": "Uma sacerdotisa da luz e o último refúgio da party. Suas curas fecham feridas e suas bênçãos desviam golpes mortais.",
    "bishop": "Um clérigo de alto escalão que comanda as tempestades da natureza. Tornados, marés e pedras obedecem à sua prece.",
    "gladiator": "Um veterano da arena que confia na espada e no escudo. Segura a linha de frente enquanto os aliados atacam.",
    "paladin": "Um cavaleiro jurado à luz. Combina uma defesa inabalável com magia sagrada de proteção e cura.",
    "spellblade": "Um espadachim que encanta a própria lâmina com fogo, gelo e raio. Troca um pouco de defesa por golpes elementais devastadores.",
    "marauder": "Um saqueador brutal com um machado de duas mãos. Aguenta castigo como poucos e devolve em dobro.",
    "warrior": "Um mestre das armas pesadas, forjado em mil batalhas. Seus gritos de guerra inspiram a party e seus golpes partem fileiras.",
    "berserker": "Um guerreiro tomado pela fúria que abandona toda defesa. Quanto mais a batalha se arrasta, mais perigoso ele fica.",
    "freelancer_t2": "Um Novice que percorreu todos os caminhos básicos até o fim. Mistura espada, machado e magia, e carrega as técnicas de todos os mestres básicos com quem aprendeu.",
    "warfarer": "Uma lenda viva que dominou todas as escolas de guerra e magia. Toda arma é uma extensão da sua vontade, e os segredos de todas as classes atendem ao seu chamado.",
}


def _load_lore():
    try:
        from data import LORE
    except Exception:
        return
    for cid, txt in _LORE_PT.items():
        if cid in LORE:
            PT[LORE[cid]] = _names.localize_classes(txt)


_load_lore()
