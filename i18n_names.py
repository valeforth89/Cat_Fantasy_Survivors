"""Traduções (PT) dos nomes das classes, das habilidades ativas, das passivas e das descrições das ativas.

O i18n.py junta estes dicionários ao PT (sem sobrescrever traduções que já existem), então tudo o que passa por
tr() — textos da tela, dicas, wiki — mostra os nomes em português quando o idioma é Português.
Os nomes de magias clássicas (Firaga, Bio, Ultima, Ifrit, Shiva...) continuam iguais, como nas versões em PT.
"""

CLASS_PT = {
    "Novice": "Novato", "Freelancer": "Aventureiro", "Warfarer": "Veterano", "Archer": "Arqueiro",
    "Thaumaturge": "Taumaturgo", "Arcanist": "Arcanista", "Pugilist": "Pugilista", "Lancer": "Lanceiro",
    "Rogue": "Ladino", "Conjurer": "Conjurador", "Gladiator": "Gladiador", "Marauder": "Saqueador", "Bard": "Bardo",
    "Hunter": "Caçador", "Black Mage": "Mago Negro", "Time Mage": "Mago do Tempo", "Summoner": "Invocador",
    "Scholar": "Erudito", "Monk": "Monge", "White Monk": "Monge Branco", "Dragoon": "Cavaleiro Dragão",
    "Templar": "Templário", "Ninja": "Ninja", "Assassin": "Assassino", "White Mage": "Mago Branco",
    "Bishop": "Bispo", "Paladin": "Paladino", "Spellblade": "Lâmina Arcana", "Warrior": "Guerreiro",
    "Berserker": "Berserker",
}

# arma do golpe básico: "Basic Attack (Bow)" -> "Ataque Básico (Arco)"
WEAPON_PT = {
    "Short sword": "Espada curta", "Bow": "Arco", "Bow and harp": "Arco e harpa", "Longbow": "Arco longo",
    "Staff": "Cajado", "Black staff": "Cajado negro", "Staff and hourglass": "Cajado e ampulheta",
    "Grimoire": "Grimório", "Fist weapons": "Armas de punho", "Claws": "Garras", "Holy fists": "Punhos sagrados",
    "Spear": "Lança", "Long spear": "Lança longa", "Spear and banner": "Lança e estandarte", "Dagger": "Adaga",
    "Kunai and shuriken": "Kunai e shuriken", "Daggers": "Adagas", "White staff": "Cajado branco",
    "Scepter": "Cetro", "Sword and shield": "Espada e escudo", "Holy sword and shield": "Espada sagrada e escudo",
    "Enchanted sword": "Espada encantada", "Two-handed axe": "Machado de duas mãos", "War axe": "Machado de guerra",
    "Twin axes": "Machados gêmeos", "Longsword": "Espada longa", "Arsenal": "Arsenal",
}

ACTIVE_PT = {
    # Novato
    "Quick Stab": "Estocada Rápida", "Whirling Blade": "Lâmina Giratória", "Pommel Bash": "Golpe de Pomo",
    "Throwing Daggers": "Adagas de Arremesso", "Dust Kick": "Chute de Poeira", "Rally": "Reagrupar",
    "Heavy Chop": "Talho Pesado", "Wanderer's Edge": "Fio do Andarilho", "Second Wind": "Segundo Fôlego",
    "Driving Lunge": "Investida Impetuosa",
    # Arqueiro
    "Twin Shot": "Tiro Duplo", "Aimed Shot": "Tiro Mirado", "Pinning Arrow": "Flecha Prendedora",
    "Fire Arrow": "Flecha de Fogo", "Hawk Eye": "Olho de Falcão", "Snare Trap": "Armadilha de Laço",
    "Headshot": "Tiro na Cabeça", "Volley": "Saraivada", "Hail of Arrows": "Chuva de Flechas",
    "Storm Arrow": "Flecha da Tempestade",
    # Bardo
    "Melodic Arrow": "Flecha Melódica", "Battle Ballad": "Balada de Batalha", "Dissonant Chord": "Acorde Dissonante",
    "Song of Healing": "Canção de Cura", "Requiem": "Réquiem", "Swift Tempo": "Tempo Ligeiro", "Lullaby": "Canção de Ninar",
    "Echo Arrow": "Flecha Eco", "Anthem of Valor": "Hino do Valor", "Grand Finale": "Grande Final",
    # Caçador
    "Snipe": "Disparo Certeiro", "Hunter's Mark": "Marca do Caçador", "Falcon": "Falcão", "Bear Trap": "Armadilha de Urso",
    "Explosive Arrow": "Flecha Explosiva", "Predator Focus": "Foco do Predador", "Wolf Companion": "Lobo Companheiro",
    "Deadeye": "Olho Mortal", "Multishot": "Tiro Múltiplo", "Arrow Storm": "Tempestade de Flechas",
    # Taumaturgo
    "Spark": "Faísca", "Flame Wave": "Onda de Chamas", "Thunder": "Trovão", "Ice Nova": "Nova de Gelo",
    "Fire Pillar": "Pilar de Fogo", "Chain Lightning": "Corrente de Raios", "Tri-Elemental": "Trielemental",
    "Frost Lance": "Lança de Gelo", "Meteor": "Meteoro",
    # Mago Negro (magias clássicas mantêm o nome)
    "Quake": "Terremoto",
    # Mago do Tempo
    "Haste": "Aceleração", "Slow": "Lentidão", "Comet": "Cometa", "Stop": "Parar", "Reverse": "Reverso",
    "Time Rift": "Fenda Temporal", "Old": "Envelhecer", "Stasis Field": "Campo de Estase",
    # Arcanista
    "Arcane Missile": "Míssil Arcano", "Arcane Burst": "Explosão Arcana", "Rune Circle": "Círculo de Runas",
    "Arcane Orbs": "Orbes Arcanos", "Seeking Runes": "Runas Teleguiadas", "Arcane Shield": "Escudo Arcano",
    "Mana Bolt": "Raio de Mana", "Arcane Explosion": "Detonação Arcana", "Mana Torrent": "Torrente de Mana",
    "Arcane Nova": "Nova Arcana",
    # Invocador
    "Ramuh's Judgment": "Julgamento de Ramuh", "Titan's Landslide": "Deslizamento de Titan",
    "Leviathan's Tide": "Maré de Leviathan", "Ruby Light": "Luz Rubi", "Phoenix Flame": "Chama da Fênix",
    # Erudito
    "Area Cure": "Cura em Área", "Ruin": "Ruína", "Whispering Dawn": "Aurora Sussurrante", "Miasma": "Miasma",
    "Insight": "Discernimento", "Broil": "Abrasar", "Fey Blessing": "Bênção Feérica", "Expedience": "Expediência",
    "Lustrate": "Lustração",
    # Pugilista
    "Jab Combo": "Combo de Jabs", "Uppercut": "Gancho", "Palm Strike": "Golpe de Palma", "Liver Blow": "Golpe no Fígado",
    "Flowing Stance": "Postura Fluida", "Shockwave": "Onda de Choque", "Cross Counter": "Contragolpe Cruzado",
    "Roundhouse Kick": "Chute Giratório", "Knockout Punch": "Soco Nocaute", "Hundred Fists": "Cem Punhos",
    # Monge
    "Snap Punch": "Soco Rápido", "Dragon Kick": "Chute do Dragão", "Tiger Palm": "Palma do Tigre",
    "Inner Focus": "Foco Interior", "Pressure Point": "Ponto de Pressão", "Rising Phoenix": "Fênix Ascendente",
    "Chi Field": "Campo de Chi", "Howling Fist": "Punho Uivante", "Demolish": "Demolir", "Final Heaven": "Céu Final",
    # Monge Branco
    "Purifying Strike": "Golpe Purificador", "Restoring Chi": "Chi Restaurador", "Holy Palm": "Palma Sagrada",
    "Mantra": "Mantra", "Chi Seal": "Selo de Chi", "Inner Peace": "Paz Interior", "Holy Kick": "Chute Sagrado",
    "Serene Breath": "Sopro Sereno", "Stunning Palm": "Palma Atordoante", "Divine Pulse": "Pulso Divino",
    # Lanceiro
    "Lunge": "Estocada", "Sweep": "Varredura", "Impale": "Empalar", "Javelin": "Dardo", "Phalanx": "Falange",
    "Piercing Charge": "Carga Perfurante", "Vault Strike": "Golpe de Salto", "Spear Spin": "Giro da Lança",
    "Skewer Storm": "Tempestade de Espetos", "Javelin Rain": "Chuva de Dardos",
    # Cavaleiro Dragão
    "Dragon Fang": "Presa do Dragão", "Jump": "Salto", "Lance Sweep": "Varredura da Lança",
    "Elemental Breath": "Sopro Elemental", "Dragon Sight": "Visão do Dragão", "High Jump": "Salto Alto",
    "Thunder Spear": "Lança do Trovão", "Wyvern Wings": "Asas de Wyvern", "Dragon Dive": "Mergulho do Dragão",
    # Templário
    "Holy Thrust": "Estocada Sagrada", "Banner of Valor": "Estandarte do Valor", "Consecrate": "Consagrar",
    "Divine Guard": "Guarda Divina", "Condemn": "Condenar", "Lay on Hands": "Imposição de Mãos", "Smite": "Castigo",
    "Crusade": "Cruzada", "Judgment": "Julgamento",
    # Ladino
    "Backstab": "Punhalada nas Costas", "Smoke Bomb": "Bomba de Fumaça", "Gouge": "Golpe Baixo",
    "Thrown Knives": "Facas Arremessadas", "Quick Step": "Passo Rápido", "Mug": "Assaltar",
    "Shadow Strike": "Golpe Sombrio", "Caltrops": "Estrepes", "Kidney Shot": "Golpe no Rim",
    "Fan of Blades": "Leque de Lâminas",
    # Ninja
    "Kunai Barrage": "Rajada de Kunais", "Shadow Clone": "Clone das Sombras", "Giant Shuriken": "Shuriken Gigante",
    # Assassino
    "Ambush": "Emboscada", "Poisoned Daggers": "Adagas Envenenadas", "Shadowstep": "Passo Sombrio",
    "Venom Edge": "Fio Venenoso", "Garrote": "Garrote", "Mutilate": "Mutilar", "Toxic Cloud": "Nuvem Tóxica",
    "Viper Bite": "Picada de Víbora", "Blade Flurry": "Turbilhão de Lâminas", "Death Mark": "Marca da Morte",
    # Conjurador
    "Cure": "Cura", "Natural Elements": "Elementos Naturais", "Natural Elements II": "Elementos Naturais II",
    "Water Bolt": "Raio d'Água", "Regen": "Regeneração", "Gust": "Rajada", "Stoneskin": "Pele de Pedra",
    "Whirlpool": "Redemoinho", "Healing Rain": "Chuva Curativa", "Tailwind": "Vento a Favor", "Earthquake": "Terremoto",
    # Mago Branco
    "Protect": "Proteção", "Banish": "Banir", "Shell": "Concha", "Holy Light": "Luz Sagrada",
    "Divine Ring": "Anel Divino", "Benediction": "Bênção Suprema",
    # Bispo
    "Grand Elements": "Grandes Elementos", "Tornado": "Tornado", "Stone Rain": "Chuva de Pedras", "Gale": "Vendaval",
    "Mud Pool": "Poça de Lama", "Water Lance": "Lança d'Água", "Landslide": "Deslizamento", "Purify": "Purificar",
    "Maelstrom": "Voragem", "Tidal Surge": "Onda da Maré",
    # Gladiador
    "Shield Bash": "Golpe de Escudo", "Challenge": "Desafio", "Riposte": "Contra-ataque", "Shield Wall": "Muralha de Escudo",
    "Arena Spin": "Giro da Arena", "Rallying Cry": "Grito de Reunião", "Ground Stomp": "Pisão", "Second Breath": "Segundo Fôlego",
    "Sword Toss": "Arremesso de Espada", "Champion's Slash": "Corte do Campeão",
    # Paladino
    "Holy Slash": "Corte Sagrado", "Divine Challenge": "Desafio Divino", "Shield of Faith": "Escudo da Fé",
    "Sacred Circle": "Círculo Sagrado", "Healing Light": "Luz Curativa", "Aegis": "Égide",
    "Righteous Charge": "Carga Justa", "Holy Strike": "Golpe Sagrado", "Holy Judgment": "Julgamento Sagrado",
    # Lâmina Arcana
    "Flame Blade": "Lâmina Flamejante", "Glacial Blade": "Lâmina Glacial", "Thunder Blade": "Lâmina do Trovão",
    "Earth Blade": "Lâmina da Terra", "Enchant": "Encantar", "Arcane Wave": "Onda Arcana",
    "Venom Blade": "Lâmina Venenosa", "Elemental Ward": "Proteção Elemental", "Holy Blade": "Lâmina Sagrada",
    "Elemental Fury": "Fúria Elemental",
    # Saqueador
    "Cleave": "Fender", "Intimidating Roar": "Rugido Intimidador", "Ground Slam": "Impacto no Chão",
    "Thick Hide": "Couro Grosso", "Axe Throw": "Arremesso de Machado", "Bloodlust": "Sede de Sangue",
    "Brutal Swing": "Golpe Brutal", "Battle Roar": "Rugido de Batalha", "Earthsplitter": "Racha-Terra",
    "Skull Splitter": "Racha-Crânio",
    # Guerreiro
    "Heavy Cleave": "Fender Pesado", "Provoke": "Provocar", "Iron Will": "Vontade de Ferro", "Earthshaker": "Sacode-Terra",
    "War Cry": "Grito de Guerra", "Warrior's Resolve": "Determinação do Guerreiro", "Decimate": "Dizimar",
    "Overpower": "Sobrepujar", "Axe Storm": "Tempestade de Machados", "Defiance": "Desafio Final",
    # Berserker
    "Furious Chop": "Talho Furioso", "Blood Frenzy": "Frenesi de Sangue", "Leap Slam": "Salto Esmagador",
    "Rend": "Dilacerar", "Whirlwind": "Redemoinho de Aço", "Skullcrack": "Quebra-Crânio", "Bloodbath": "Banho de Sangue",
    "Reckless Charge": "Carga Imprudente", "Rampage": "Fúria Desenfreada", "Execute": "Executar",
    # Aventureiro
    "Piercing Lunge": "Estocada Perfurante", "Whirlwind Edge": "Fio do Redemoinho", "Crosscut": "Corte Cruzado",
    "Flash Powder": "Pó Ofuscante", "Second Nature": "Segunda Natureza", "Earthbreaker": "Quebra-Terra",
    "Arcane Bolt": "Raio Arcano", "Field Dressing": "Curativo de Campo", "Volley of Blades": "Saraivada de Lâminas",
    "Executioner's Cut": "Corte do Carrasco",
    # Veterano
    "Cataclysmic Leap": "Salto Cataclísmico", "Titan Cleaver": "Cutelo do Titã", "Dragonfire": "Fogo de Dragão",
    "Dueling Thrust": "Estocada de Duelo", "Blade Storm": "Tempestade de Lâminas", "Battle Hymn": "Hino de Batalha",
    "Godspear": "Lança Divina", "Warlord's Rally": "Convocação do Senhor da Guerra",
    "Thunder Judgment": "Julgamento do Trovão", "Scorched Earth": "Terra Arrasada",
    # golpes antigos / básicos
    "Strike": "Golpe", "Stone Toss": "Arremesso de Pedra", "Arcing Slash": "Corte em Arco",
    "Throwing Axes": "Machados de Arremesso", "Warbringer": "Arauto da Guerra", "Spear Barrage": "Rajada de Lanças",
    "Arrow": "Flecha", "Arrow Rain": "Chuva de Flechas", "Rapid Punches": "Socos Rápidos",
    "Dagger Slash": "Corte de Adaga", "Slash": "Corte", "Axe Chop": "Machadada", "Piercing Shot": "Tiro Perfurante",
    "Barrage": "Rajada", "Fist Flurry": "Rajada de Punhos", "Chakra Burst": "Explosão de Chakra",
    "Spinning Kick": "Chute Giratório", "Blessing": "Bênção", "Ninjutsu": "Ninjutsu", "Twin Blades": "Lâminas Gêmeas",
    "Fury": "Fúria",
}

# passivas: "Fire Mastery", "Exploit Burning"... são montadas pelas partes; o resto é traduzido à mão
_TAG_NOUN = {
    "Physical": "Físico", "Magical": "Mágico", "Single target": "Alvo Único", "Bleed": "Sangramento",
    "Slash": "Corte", "Projectile": "Projétil", "Piercing": "Perfuração", "Damage over time": "Dano Contínuo",
    "Sound": "Som", "Buff": "Bônus", "Summon": "Invocação", "Fire": "Fogo", "Lightning": "Raio", "Ice": "Gelo",
    "AoE": "Área", "Gravity": "Gravidade", "Time": "Tempo", "Stun": "Atordoamento", "Arcane": "Arcano",
    "Homing": "Teleguiado", "Heal": "Cura", "Melee": "Corpo a Corpo", "Blunt": "Impacto", "Knockback": "Empurrão",
    "Holy": "Sagrado", "Ranged": "Distância", "Poison": "Veneno", "Toxic": "Toxina", "Earth": "Terra",
    "Wind": "Vento", "Water": "Água",
}
_KIND = {"Mastery": "Maestria", "Precision": "Precisão", "Haste": "Celeridade", "Power": "Poder"}
_EXPLOIT = {"Slowed": "Lentos", "Burning": "Queimando", "Poisoned": "Envenenados", "Stunned": "Atordoados",
            "Bleeding": "Sangrando", "Chilled": "Congelados", "Elemental": "Elementos", "Any Debuff": "Enfraquecidos"}
_TRAIN = {"AGI": "AGI", "STR": "FOR", "INT": "INT", "Shield": "Escudo", "Spellsword": "Espadachim Arcano"}

PASSIVE_PT = {
    "Versatile Training": "Treino Versátil", "Endurance": "Resistência", "Vitality": "Vitalidade",
    "Ferocity": "Ferocidade", "Jack of All Trades": "Pau Pra Toda Obra", "Evasion": "Evasão",
    "Steady Aim": "Mira Firme", "Wounding Shots": "Tiros Feridores", "Far Reach": "Longo Alcance",
    "Deadeye": "Olho Mortal", "Stage Presence": "Presença de Palco", "Soothing Melody": "Melodia Calmante",
    "Traveling Minstrel": "Menestrel Viajante", "Lingering Notes": "Notas Persistentes", "Grand Anthem": "Grande Hino",
    "Tracker": "Rastreador", "Camouflage": "Camuflagem", "Wilderness Survival": "Sobrevivência na Selva",
    "Blood Trail": "Rastro de Sangue", "Scavenger": "Catador", "Apex Predator": "Predador Supremo",
    "Warding": "Proteção", "Elemental Attunement": "Sintonia Elemental", "Expansion": "Expansão",
    "Elemental Convergence": "Convergência Elemental", "Arcane Fuel": "Combustível Arcano", "Overcharge": "Sobrecarga",
    "Pyromania": "Piromania", "Cataclysm": "Cataclismo", "Borrowed Time": "Tempo Emprestado",
    "Haste Field": "Campo de Aceleração", "Temporal Shift": "Deslocamento Temporal", "Quick Mind": "Mente Ágil",
    "Chronomancer": "Cronomante", "Spell Weaving": "Tecelagem de Magias", "Arcane Barrier": "Barreira Arcana",
    "Mana Shield": "Escudo de Mana", "Lingering Enchantment": "Encanto Persistente", "Persistence": "Persistência",
    "Arcane Overflow": "Transbordo Arcano", "Binding Circle": "Círculo de Vínculo", "Ritual Circle": "Círculo Ritual",
    "Life Link": "Elo Vital", "Pact of Legions": "Pacto das Legiões", "Studious Mind": "Mente Estudiosa",
    "Erudition": "Erudição", "Field Medicine": "Medicina de Campo", "Benevolence": "Benevolência",
    "Grand Treatise": "Grande Tratado", "Iron Body": "Corpo de Ferro", "Rolling with Punches": "Rolar com os Golpes",
    "Footwork": "Jogo de Pernas", "Swiftness": "Ligeireza", "Iron Fists": "Punhos de Ferro",
    "Inner Focus": "Foco Interior", "Iron Shirt": "Camisa de Ferro", "Ki Flow": "Fluxo de Ki",
    "Brutality": "Brutalidade", "Hundred Fists Doctrine": "Doutrina dos Cem Punhos", "Healing Palm": "Palma Curativa",
    "Serene Guard": "Guarda Serena", "Tranquility": "Tranquilidade", "Pressure Points": "Pontos de Pressão",
    "Calm Mind": "Mente Calma", "Serenity": "Serenidade", "Fortitude": "Fortitude", "Phalanx Drill": "Treino de Falange",
    "Impaler": "Empalador", "Dragon Blood": "Sangue de Dragão", "Dragon Scales": "Escamas de Dragão",
    "Sky Dive": "Mergulho do Céu", "Dragon Fire": "Fogo de Dragão", "Dragon Heart": "Coração de Dragão",
    "Oath of Light": "Juramento da Luz", "Zealot": "Zelote", "Sacred Vow": "Voto Sagrado",
    "Steadfast Faith": "Fé Inabalável", "Smite the Stunned": "Castigar os Atordoados", "Guard": "Guarda",
    "Holy Crusade": "Cruzada Sagrada", "Quick Hands": "Mãos Rápidas", "Opportunist": "Oportunista",
    "Shadowstep": "Passo Sombrio", "Hamstring": "Jarrete", "Shadow Opportunist": "Oportunista das Sombras",
    "Shuriken Drills": "Treino de Shuriken", "Vanishing Act": "Ato de Desaparecer", "Smoke Bomb": "Bomba de Fumaça",
    "Light Feet": "Pés Leves", "Thousand Shadows": "Mil Sombras", "Poisoned Blades": "Lâminas Envenenadas",
    "Mark for Death": "Marcado para Morrer", "Death Sentence": "Sentença de Morte",
    "Earth's Bounty": "Dádiva da Terra", "Verdant Growth": "Crescimento Verdejante", "Stone Skin": "Pele de Pedra",
    "Nature's Embrace": "Abraço da Natureza", "Blessed Aura": "Aura Abençoada", "Purity": "Pureza",
    "Divine Protection": "Proteção Divina", "Holy Judgment": "Julgamento Sagrado", "Divine Grace": "Graça Divina",
    "Sermon": "Sermão", "Consecration": "Consagração", "Faith": "Fé", "Wrath of Nature": "Ira da Natureza",
    "Crowd Pleaser": "Queridinho do Público", "Showmanship": "Espetáculo", "Arena Veteran": "Veterano da Arena",
    "Crowd's Roar": "Rugido da Plateia", "Champion of the Arena": "Campeão da Arena", "Holy Shield": "Escudo Sagrado",
    "Divine Bulwark": "Baluarte Divino", "Lay on Hands": "Imposição de Mãos", "Aegis of Light": "Égide da Luz",
    "Arcane Edge": "Fio Arcano", "Blade Dance": "Dança das Lâminas", "Runic Ward": "Proteção Rúnica",
    "Keen Eye": "Olho Aguçado", "Elemental Edge": "Fio Elemental", "Savage Strength": "Força Selvagem",
    "Pillager": "Pilhador", "Blood Frenzy": "Frenesi de Sangue", "Ravager": "Devastador", "Bloodthirst": "Sede de Sangue",
    "Battle Cry": "Grito de Batalha", "Second Wind": "Segundo Fôlego", "Rallying Presence": "Presença Inspiradora",
    "Shield Bash": "Golpe de Escudo", "Toughness": "Robustez", "Warlord": "Senhor da Guerra",
    "Reckless Swing": "Golpe Imprudente", "Pain Tolerance": "Tolerância à Dor", "Thick Skin": "Pele Grossa",
    "Unending Rage": "Fúria Sem Fim", "Wanderer's Kit": "Kit do Andarilho", "Adaptable": "Adaptável",
    "Seasoned Traveler": "Viajante Experiente", "Versatility": "Versatilidade", "Battle Hardened": "Calejado em Batalha",
    "Commander's Resolve": "Determinação do Comandante", "War Veteran": "Veterano de Guerra",
    "Master of War": "Mestre da Guerra", "Crowd Control": "Controle de Multidão",
}

ACTIVE_DESC_PT = {
    "A heavy chop on the nearest enemy": "Um talho pesado no inimigo mais próximo",
    "A long lunge that pushes the enemy back": "Uma estocada longa que empurra o inimigo",
    "A carefully aimed arrow": "Uma flecha mirada com cuidado",
    "A heavy arrow that slows": "Uma flecha pesada que deixa lento",
    "A lethal shot at a single enemy": "Um tiro letal em um único inimigo",
    "An arrow that sings through the air": "Uma flecha que canta pelo ar",
    "A dissonant chord that weakens nearby enemies": "Um acorde dissonante que enfraquece os inimigos próximos",
    "A sound wave that hits three enemies": "Uma onda sonora que atinge três inimigos",
    "A brave anthem: the party takes less damage": "Um hino corajoso: a party recebe menos dano",
    "A long-range shot at a single enemy": "Um tiro de longo alcance em um único inimigo",
    "Marks the prey: it takes more damage": "Marca a presa: ela recebe mais dano",
    "A perfect shot that never misses its mark": "Um tiro perfeito que nunca erra o alvo",
    "Five arrows in a fan": "Cinco flechas em leque",
    "A fireball that explodes on impact": "Uma bola de fogo que explode no impacto",
    "A lance of ice at a single enemy": "Uma lança de gelo em um único inimigo",
    "A great fireball that explodes": "Uma grande bola de fogo que explode",
    "Lightning strikes three enemies": "Um raio atinge três inimigos",
    "A blizzard that slows enemies in front": "Uma nevasca que deixa lentos os inimigos à frente",
    "A concentrated explosion on a single enemy": "Uma explosão concentrada em um único inimigo",
    "Crushes the nearest enemy with gravity": "Esmaga o inimigo mais próximo com a gravidade",
    "Ages three enemies: they take more damage": "Envelhece três inimigos: eles recebem mais dano",
    "Slows incoming blows: the party takes less damage": "Retarda os golpes recebidos: a party recebe menos dano",
    "A bolt of pure mana at a single enemy": "Um raio de mana pura em um único inimigo",
    "A torrent of raw mana in front of you": "Uma torrente de mana bruta à sua frente",
    "A nova of arcane power around you": "Uma nova de poder arcano ao seu redor",
    "Carbuncle's ray hits a single enemy": "O raio de Carbuncle atinge um único inimigo",
    "A bolt of ruin": "Um raio de ruína",
    "A gentle, frequent heal for the party": "Uma cura suave e frequente para a party",
    "A noxious gas that weakens enemies inside": "Um gás nocivo que enfraquece os inimigos dentro dele",
    "A tactical retreat: the party moves much faster": "Uma retirada tática: a party se move muito mais rápido",
    "A huge heal for the whole party": "Uma cura enorme para a party inteira",
    "A quick sequence of jabs on the nearest enemy": "Uma sequência rápida de jabs no inimigo mais próximo",
    "A body blow that stuns": "Um golpe no corpo que atordoa",
    "A heavy counterpunch": "Um contragolpe pesado",
    "A punch that knocks the enemy out": "Um soco que nocauteia o inimigo",
    "A lightning-fast punch": "Um soco rápido como um raio",
    "Hits a vital point and paralyzes the enemy": "Acerta um ponto vital e paralisa o inimigo",
    "A fist of chi that pierces a line": "Um punho de chi que atravessa uma linha",
    "A crushing blow that weakens the enemy": "Um golpe esmagador que enfraquece o inimigo",
    "A devastating finishing blow": "Um golpe final devastador",
    "A palm of holy light": "Uma palma de luz sagrada",
    "Seals the chi of nearby enemies: weaker and slower": "Sela o chi dos inimigos próximos: mais fracos e lentos",
    "Calm minds: the party's skills recover faster": "Mentes calmas: as habilidades da party recarregam mais rápido",
    "Vaults on the spear and lands on the nearest enemy": "Salta com a lança e cai sobre o inimigo mais próximo",
    "Spins the spear around you": "Gira a lança ao seu redor",
    "Breathes fire, lightning and ice in turns": "Sopra fogo, raio e gelo alternadamente",
    "The dragon's eye guides the party: more damage": "O olho do dragão guia a party: mais dano",
    "A higher, stronger jump on a single enemy": "Um salto mais alto e forte em um único inimigo",
    "A wave of dragon power along the spear": "Uma onda de poder dracônico ao longo da lança",
    "A thrust of holy light": "Uma estocada de luz sagrada",
    "Condemns nearby enemies: they take more damage": "Condena os inimigos próximos: eles recebem mais dano",
    "Smites the nearest enemy and stuns it": "Castiga o inimigo mais próximo e o atordoa",
    "A holy march: the party moves and strikes faster": "Uma marcha sagrada: a party anda e ataca mais rápido",
    "A precise stab from behind": "Uma punhalada precisa pelas costas",
    "A smoke bomb that slows nearby enemies": "Uma bomba de fumaça que deixa lentos os inimigos próximos",
    "A quick gouge that stuns": "Um golpe baixo rápido que atordoa",
    "Scatters spikes that hurt and slow enemies": "Espalha estrepes que ferem e deixam os inimigos lentos",
    "A brutal stab that stuns for a long time": "Uma punhalada brutal que atordoa por muito tempo",
    "A fast shuriken at a single enemy": "Uma shuriken rápida em um único inimigo",
    "Earth release: the ground erupts around you": "Estilo Terra: o chão explode ao seu redor",
    "Wind release: a gale that blows enemies away": "Estilo Vento: um vendaval que afasta os inimigos",
    "Dashes through an enemy in a line": "Avança atravessando um inimigo em linha",
    "Two poisoned stabs": "Duas punhaladas envenenadas",
    "Marks an enemy for death: a huge hit that weakens it": "Marca um inimigo para morrer: um golpe enorme que o enfraquece",
    "Wind, earth and water in turns": "Vento, terra e água alternadamente",
    "Skin of stone: the party takes less damage": "Pele de pedra: a party recebe menos dano",
    "A whirlpool that slows enemies inside": "Um redemoinho que deixa lentos os inimigos dentro dele",
    "A rain that heals everyone": "Uma chuva que cura todo mundo",
    "A tailwind: the party moves and casts faster": "Vento a favor: a party anda e lança magias mais rápido",
    "Wind, earth and water in turns on two enemies": "Vento, terra e água alternadamente em dois inimigos",
    "A tornado that cuts everything inside": "Um tornado que corta tudo o que está dentro",
    "A pool of mud that hurts and slows": "Uma poça de lama que fere e deixa lento",
    "Challenges nearby enemies: they attack you": "Desafia os inimigos próximos: eles atacam você",
    "Rallies the party: less damage taken and more speed": "Reúne a party: menos dano recebido e mais velocidade",
    "Stomps the ground and slows around you": "Pisa forte no chão e deixa lento ao seu redor",
    "A slash of holy light": "Um corte de luz sagrada",
    "A holy challenge: nearby enemies attack you": "Um desafio sagrado: os inimigos próximos atacam você",
    "A slash wrapped in fire": "Um corte envolto em fogo",
    "A freezing thrust that slows": "Uma estocada congelante que deixa lento",
    "A slash charged with lightning": "Um corte carregado de raios",
    "A heavy strike charged with earth": "Um golpe pesado carregado de terra",
    "A thrust coated in poison": "Uma estocada coberta de veneno",
    "A ward of the elements protects the party": "Uma proteção dos elementos protege a party",
    "A roar that makes nearby enemies attack you": "Um rugido que faz os inimigos próximos atacarem você",
    "Shrugs off blows: much less damage taken": "Ignora os golpes: muito menos dano recebido",
    "Throws an axe that pierces": "Arremessa um machado que atravessa",
    "A roar that fires up the party: more damage": "Um rugido que inflama a party: mais dano",
    "Provokes nearby enemies: they attack you": "Provoca os inimigos próximos: eles atacam você",
    "More damage and defense for the party": "Mais dano e defesa para a party",
    "Stands firm for everyone: the party takes less damage": "Fica firme por todos: a party recebe menos dano",
    "A furious chop on the nearest enemy": "Um talho furioso no inimigo mais próximo",
    "A frenzy of blood: faster strikes and movement": "Um frenesi de sangue: golpes e movimento mais rápidos",
    "Rips the enemy open with both axes": "Dilacera o inimigo com os dois machados",
    "Spins with both axes": "Gira com os dois machados",
    "A blow to the head that stuns": "Um golpe na cabeça que atordoa",
    "Charges recklessly through an enemy": "Avança imprudentemente através de um inimigo",
    "Hits the three nearest enemies in a row": "Acerta os três inimigos mais próximos em sequência",
    "A merciless finishing blow": "Um golpe final impiedoso",
    "Two fast cuts on the nearest enemy": "Dois cortes rápidos no inimigo mais próximo",
    "A finishing cut on the nearest enemy": "Um corte final no inimigo mais próximo",
    "A crushing blow on the nearest enemy": "Um golpe esmagador no inimigo mais próximo",
    "A precise thrust at the nearest enemy": "Uma estocada precisa no inimigo mais próximo",
}


_ADJ = {("Physical", "Mastery"): "Maestria Física", ("Physical", "Precision"): "Precisão Física",
        ("Physical", "Haste"): "Celeridade Física", ("Physical", "Power"): "Poder Físico",
        ("Magical", "Mastery"): "Maestria Mágica", ("Magical", "Precision"): "Precisão Mágica",
        ("Magical", "Haste"): "Celeridade Mágica", ("Magical", "Power"): "Poder Mágico"}


def passive_pt(name):
    """Nome base da passiva em PT (sem a classe), ou None."""
    if name in PASSIVE_PT:
        return PASSIVE_PT[name]
    for (tag, kind), pt in _ADJ.items():
        if name == f"{tag} {kind}":
            return pt
    if name.startswith("Exploit "):
        st = _EXPLOIT.get(name[8:])
        return f"Explorar {st}" if st else None
    if name.endswith(" Training") and name[:-9] in _TRAIN:
        return f"Treino de {_TRAIN[name[:-9]]}"
    for en, pt in _KIND.items():
        if name.endswith(" " + en) and name[:-len(en) - 1] in _TAG_NOUN:
            return f"{pt} de {_TAG_NOUN[name[:-len(en) - 1]]}"
    return None


def basic_pt(name):
    """"Basic Attack (Bow)" -> "Ataque Básico (Arco)"."""
    if name.startswith("Basic Attack (") and name.endswith(")"):
        w = name[14:-1]
        return f"Ataque Básico ({WEAPON_PT.get(w, w)})"
    return None


def register(PT, PASSIVE_SHORT_PT):
    """Junta as traduções ao dicionário do i18n sem sobrescrever o que já existe."""
    for d in (CLASS_PT, ACTIVE_PT, ACTIVE_DESC_PT):
        for en, pt in d.items():
            PT.setdefault(en, pt)
    for en, pt in PASSIVE_PT.items():
        PASSIVE_SHORT_PT.setdefault(en, pt)
        PT.setdefault(en, pt)


_CLASS_RX = None


def localize_classes(text):
    """Troca os nomes das classes em inglês dentro de um texto em PT (FAQ, dicas): "Novice Lv 10" -> "Novato Nv 10"
    fica só no nome; o resto do texto já está em PT."""
    global _CLASS_RX
    if _CLASS_RX is None:
        import re
        names = sorted((n for n in CLASS_PT if CLASS_PT[n] != n), key=len, reverse=True)
        _CLASS_RX = re.compile(r"(?<![\w'])(" + "|".join(re.escape(n) for n in names) + r")(?![\w])")
    return _CLASS_RX.sub(lambda m: CLASS_PT[m.group(1)], text)
