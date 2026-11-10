"""Acessórios (Joalheiro): anéis, braceletes, berloques e colares.

Regras:
- Cada acessório é ÚNICO: dropa uma vez e vira um desbloqueio da conta (ROSTER.acc_owned).
- Só um personagem por vez pode usar cada acessório (estimula variar as builds).
- Espaços de cada personagem: 2 anéis, 1 bracelete, 2 berloques (o colar fica bloqueado por enquanto).
- Cada fase dropa 2-3 acessórios (STAGE_DROPS); o Endless do bioma dropa os de todas as fases do bioma.
  Os que ainda não têm fase vão aparecer nas próximas fases.
- Cópias repetidas viram fragmentos da categoria (anel, bracelete, berloque), usados no Joalheiro
  para melhorar os acessórios daquela categoria (+1 ... +5; cada nível: +20% nos valores).
- Colares: um por classe, liberado quando algum personagem leva a classe ao nível máximo padrão; qualquer
  classe pode usar; melhorados com os fragmentos da classe do colar.

Tipos:
- Anéis: simples, % de dano / chance crítica / recarga para um tipo de dano; os gerais valem para tudo,
  mas são mais fracos.
- Braceletes: condicionais (contra alvos com status) e efeitos ao causar status.
- Berloques: efeitos com chance (meteoro, corrente de raios, buffs...).
"""
import pygame

from class_passives import effects_text

MAX_LV = 5
LV_STEP = 0.20                       # cada nível: +20% nos valores (chances não mudam)
SLOTS = ("ring1", "ring2", "bracer", "trinket1", "trinket2", "neck", "emblem")
SLOT_CAT = {"ring1": "ring", "ring2": "ring", "bracer": "bracer", "trinket1": "trinket", "trinket2": "trinket",
            "neck": "neck", "emblem": "emblem"}
CATS = ("ring", "bracer", "trinket", "neck", "emblem")
FRAG_CATS = ("ring", "bracer", "trinket", "emblem")   # categorias com fragmentos (cópias repetidas)
CAT_NAME = {"ring": ("Ring", "Anel"), "bracer": ("Bracer", "Bracelete"), "trinket": ("Trinket", "Berloque"),
            "neck": ("Necklace", "Colar"), "emblem": ("Emblem", "Emblema")}
CAT_PLURAL = {"ring": ("Rings", "Anéis"), "bracer": ("Bracers", "Braceletes"), "trinket": ("Trinkets", "Berloques"),
              "neck": ("Necklaces", "Colares"), "emblem": ("Emblems", "Emblemas")}
SLOT_LABEL = {"ring1": ("Ring 1", "Anel 1"), "ring2": ("Ring 2", "Anel 2"), "bracer": ("Bracer", "Bracelete"),
              "trinket1": ("Trinket 1", "Berloque 1"), "trinket2": ("Trinket 2", "Berloque 2"),
              "neck": ("Necklace", "Colar"), "emblem": ("Emblem", "Emblema")}

# chance de drop por abate (sorteia um acessório da fase): em média ~1 acessório por run completa (com sorte, mais).
# Elites comuns: a chance é dividida pelo multiplicador de inimigos da party (party maior = mais elites),
# para a média ficar parecida com 1 ou 5 membros.
DROP_CHANCE = {"boss": 0.25, "super": 0.05, "squad": 0.012, "normal": 0.005}

# acessórios obtidos e nível (o mesmo dicionário fica em roster.acc_owned)
OWNED = {}

ACC = {}


def _add(aid, cat, en, pt, icon, color, eff=None, proc=None, text=None):
    ACC[aid] = dict(id=aid, cat=cat, name=(en, pt), icon=icon, color=color, eff=eff or {}, proc=proc, text=text)


# ------------------------------------------------------------------ anéis (30)
_RING_TYPES = [
    # tag, cor, símbolo, (dano, crítico, recarga) nomes EN/PT
    ("slash", (150, 150, 165), "sword", ("Razor Ring", "Anel da Navalha"), ("Keen Edge Ring", "Anel do Fio Certeiro"),
     ("Swift Blade Ring", "Anel da Lâmina Ligeira")),
    ("piercing", (120, 140, 110), "spear", ("Needle Ring", "Anel da Agulha"), ("Hawkeye Ring", "Anel do Olho de Falcão"),
     ("Quickshot Ring", "Anel do Tiro Rápido")),
    ("blunt", (140, 105, 80), "fist", ("Hammer Ring", "Anel do Martelo"), ("Skullcrack Ring", "Anel Racha-Crânio"),
     ("Rhythm Ring", "Anel do Ritmo")),
    ("fire", (175, 70, 40), "flame", ("Ember Ring", "Anel da Brasa"), ("Flashpoint Ring", "Anel do Ponto de Fulgor"),
     ("Kindling Ring", "Anel da Faísca")),
    ("ice", (70, 130, 180), "snowflake", ("Frost Ring", "Anel da Geada"), ("Shatter Ring", "Anel Estilhaçante"),
     ("Glacier Ring", "Anel da Geleira")),
    ("lightning", (170, 150, 40), "bolt", ("Storm Ring", "Anel da Tempestade"), ("Arc Ring", "Anel do Arco Voltaico"),
     ("Static Ring", "Anel Estático")),
    ("holy", (190, 170, 90), "holy", ("Halo Ring", "Anel da Auréola"), ("Judgment Ring", "Anel do Julgamento"),
     ("Prayer Ring", "Anel da Prece")),
    ("arcane", (120, 80, 170), "rune", ("Mana Ring", "Anel de Mana"), ("Rune Ring", "Anel Rúnico"),
     ("Flux Ring", "Anel do Fluxo")),
]
for _tag, _col, _sym, _n_dmg, _n_crit, _n_cd in _RING_TYPES:
    _add(f"r_{_tag}_dmg", "ring", *_n_dmg, "ring+" + _sym, _col, {f"tagdmg:{_tag}": 12})
    _add(f"r_{_tag}_crit", "ring", *_n_crit, "ring+" + _sym, _col, {f"tagcrit:{_tag}": 6})
    _add(f"r_{_tag}_cd", "ring", *_n_cd, "ring+" + _sym, _col, {f"taghaste:{_tag}": 8})
# gerais (valem para tudo, mais fracos)
_add("r_might", "ring", "Band of Might", "Aro do Poder", "ring+up", (150, 60, 60), {"dmg": 5})
_add("r_haste", "ring", "Band of Haste", "Aro da Pressa", "ring+clock", (60, 120, 150), {"cdr": 4})
_add("r_precision", "ring", "Band of Precision", "Aro da Precisão", "ring+eye", (60, 140, 90), {"crit": 3})
_add("r_ruin", "ring", "Band of Ruin", "Aro da Ruína", "ring+skull", (130, 40, 60), {"critdmg": 10})
_add("r_iron", "ring", "Iron Signet", "Sinete de Ferro", "ring+fist", (110, 110, 120), {"phys_dmg": 7})
_add("r_mystic", "ring", "Mystic Signet", "Sinete Místico", "ring+orb", (90, 70, 160), {"mag_dmg": 7})

# ------------------------------------------------------------------ braceletes (28)
_add("b_pyre", "bracer", "Pyre Bracer", "Bracelete da Pira", "shield+flame", (170, 70, 40),
     {"dmgvs:burning": 20, "critvs:burning": 6})
_add("b_frostbite", "bracer", "Frostbite Bracer", "Bracelete da Ulceração", "shield+snowflake", (70, 130, 180),
     {"dmgvs:chilled": 20, "critvs:chilled": 6})
_add("b_venom", "bracer", "Venom Bracer", "Bracelete do Veneno", "shield+poison", (80, 140, 60),
     {"dmgvs:poisoned": 20, "dot_dmg": 10})
_add("b_butcher", "bracer", "Butcher's Bracer", "Bracelete do Açougueiro", "shield+drop", (150, 40, 50),
     {"dmgvs:bleeding": 20, "critvs:bleeding": 6})
_add("b_concussion", "bracer", "Concussion Bracer", "Bracelete da Concussão", "shield+burst", (150, 120, 60),
     {"dmgvs:stunned": 20, "critvs:stunned": 6})
_add("b_hobble", "bracer", "Hobbling Bracer", "Bracelete do Manco", "shield+clock", (90, 110, 150),
     {"dmgvs:slowed": 20, "critvs:slowed": 6})
_add("b_opportunist", "bracer", "Opportunist's Bracer", "Bracelete do Oportunista", "shield+eye", (120, 90, 140),
     {"dmgvs:debuffed": 12, "critvs:debuffed": 4})
_add("b_prism", "bracer", "Prism Bracer", "Bracelete do Prisma", "shield+star", (110, 150, 170),
     {"cap:elemental": 15, "dot_dmg": 10})
_add("b_momentum", "bracer", "Momentum Bracer", "Bracelete do Embalo", "shield+clock", (170, 130, 50), None,
     dict(on="status", st=("stunned",), chance=1.0, act="buff", buff={"haste": 15}, t=3.0, icd=1.0))
_add("b_kindling", "bracer", "Kindling Bracer", "Bracelete do Estopim", "shield+up", (190, 90, 40), None,
     dict(on="status", st=("burning",), chance=1.0, act="buff", buff={"dmg": 10}, t=4.0, icd=1.0))
_add("b_bloodletter", "bracer", "Bloodletter Bracer", "Bracelete da Sangria", "shield+heart_plus", (160, 40, 60), None,
     dict(on="status", st=("bleeding",), chance=1.0, act="heal", v=1.0, icd=0.5))
_add("b_glacial", "bracer", "Glacial Bracer", "Bracelete Glacial", "shield+shield", (90, 150, 190), None,
     dict(on="status", st=("chilled",), chance=1.0, act="buff", buff={"dr": 10}, t=3.0, icd=1.0))
_add("b_tempest", "bracer", "Tempest Bracer", "Bracelete do Temporal", "shield+boot", (110, 120, 170), None,
     dict(on="status", st=("stunned", "slowed"), chance=1.0, act="buff", buff={"speed": 20}, t=3.0, icd=1.0))
_add("b_hunter", "bracer", "Hunter's Bracer", "Bracelete do Caçador", "shield+bow", (90, 130, 70), None,
     dict(on="kill", st=("slowed", "chilled", "stunned"), chance=1.0, act="buff", buff={"crit": 8}, t=4.0, icd=0.5))
_add("b_executioner", "bracer", "Executioner's Bracer", "Bracelete do Carrasco", "shield+axe", (120, 40, 40),
     {"cap:execute": 25})
_add("b_ambusher", "bracer", "Ambusher's Bracer", "Bracelete da Emboscada", "shield+dagger", (70, 70, 90),
     {"cap:ambush": 30})
_add("b_siphon", "bracer", "Siphon Bracer", "Bracelete do Sifão", "shield+heal", (150, 60, 120),
     {"cap:vampiric": 4})
_add("b_rampage", "bracer", "Rampage Bracer", "Bracelete da Fúria", "shield+warcry", (170, 60, 40),
     {"cap:frenzy": 2})
_add("b_detonation", "bracer", "Detonation Bracer", "Bracelete da Detonação", "shield+bomb", (170, 110, 40),
     {"cap:detonate": 8})
_add("b_thorns", "bracer", "Thorned Bracer", "Bracelete de Espinhos", "shield+crossed", (90, 120, 70),
     {"cap:thorns": 20, "armor": 3})
# novos (biomas Cidade, Catedral e Subterrâneo)
_add("b_bulwark", "bracer", "Bulwark Bracer", "Bracelete do Baluarte", "shield+sword_up", (120, 120, 140), None,
     dict(on="hurt", chance=0.25, act="buff", buff={"dmg": 12}, t=3.0, icd=3.0))
_add("b_reaper", "bracer", "Reaper's Bracer", "Bracelete do Ceifador", "shield+skull", (90, 80, 110), None,
     dict(on="kill", st=("debuffed",), chance=1.0, act="cdr", v=0.2, icd=0.3))
_add("b_toxin", "bracer", "Toxin Bracer", "Bracelete da Toxina", "poison+shield", (110, 170, 70), None,
     dict(on="status", st=("poisoned",), chance=1.0, act="buff", buff={"critdmg": 20}, t=4.0, icd=1.0))
# Inferno
_add("b_brimstone", "bracer", "Brimstone Bracer", "Bracelete de Enxofre", "shield+flame", (200, 160, 60), None,
     dict(on="kill", st=("burning",), chance=1.0, act="heal", v=0.8, icd=0.3))
_add("b_hellfire", "bracer", "Hellfire Bracer", "Bracelete do Fogo Infernal", "shield+meteor", (220, 80, 40),
     {"tagdmg:fire": 8, "dot_dmg": 6})
_add("b_cinder", "bracer", "Cinder Bracer", "Bracelete da Cinza", "shield+up", (120, 90, 80), None,
     dict(on="hurt", chance=0.3, act="buff", buff={"haste": 15}, t=3.0, icd=3.0))
_add("b_damned", "bracer", "Bracer of the Damned", "Bracelete dos Condenados", "shield+skull", (100, 50, 70), None,
     dict(on="status", st=("burning", "stunned"), chance=1.0, act="buff", buff={"crit": 6}, t=3.0, icd=1.0))
_add("b_pact", "bracer", "Pact Bracer", "Bracelete do Pacto", "shield+heart", (140, 30, 50),
     {"cap:vampiric": 2, "dmg": 4})

# ------------------------------------------------------------------ berloques (28)
_add("t_meteor", "trinket", "Meteor Shard", "Fragmento de Meteoro", "meteor+star", (170, 70, 40), None,
     dict(on="status", st=("burning",), chance=0.15, act="nova", el="fire", v=150, r=90, icd=0.5),
     ("When you burn an enemy: {c}% chance a meteor falls on it ({v}% of the hit as fire damage, area).",
      "Ao queimar um inimigo: {c}% de chance de cair um meteoro nele ({v}% do golpe em dano de fogo, em área)."))
_add("t_storm", "trinket", "Storm Coil", "Bobina da Tempestade", "bolt+star", (170, 150, 40), None,
     dict(on="hit", tags=("lightning",), chance=0.20, act="chain", el="lightning", v=60, n=3, icd=0.2),
     ("Lightning hits: {c}% chance to release a chain lightning that jumps to {n} enemies ({v}% of the hit).",
      "Golpes de raio: {c}% de chance de soltar uma corrente de raios que salta para {n} inimigos ({v}% do golpe)."))
_add("t_lucky", "trinket", "Lucky Clover", "Trevo da Sorte", "star+up", (60, 150, 80), None,
     dict(on="crit", chance=0.10, act="buff", buff={"haste": 15, "dmg": 10}, t=4.0, icd=8.0),
     ("Critical hits: {c}% chance to gain {buff} for {t} s.",
      "Acertos críticos: {c}% de chance de ganhar {buff} por {t} s."))
_add("t_frostheart", "trinket", "Frost Heart", "Coração de Gelo", "snowflake+star", (70, 130, 180), None,
     dict(on="status", st=("chilled",), chance=0.10, act="nova", el="ice", v=60, r=110, stun=0.8, icd=1.0),
     ("When you chill an enemy: {c}% chance of a frost nova around it ({v}% of the hit, freezes for 0.8 s).",
      "Ao congelar um inimigo: {c}% de chance de uma nova de gelo ao redor dele ({v}% do golpe, congela por 0,8 s)."))
_add("t_plague", "trinket", "Plague Vial", "Frasco da Peste", "poison+star", (80, 140, 60), None,
     dict(on="status", st=("poisoned",), chance=0.15, act="nova", el="poison", v=40, r=80, icd=0.5),
     ("When you poison an enemy: {c}% chance the poison bursts to nearby enemies ({v}% of the hit, can poison them).",
      "Ao envenenar um inimigo: {c}% de chance de o veneno estourar nos inimigos próximos ({v}% do golpe, pode "
      "envenená-los)."))
_add("t_chalice", "trinket", "Blood Chalice", "Cálice de Sangue", "heart_plus+star", (150, 40, 50), None,
     dict(on="status", st=("bleeding",), chance=0.10, act="heal", v=3.0, icd=0.5),
     ("When you make an enemy bleed: {c}% chance to heal {v}% of your max HP.",
      "Ao fazer um inimigo sangrar: {c}% de chance de curar {v}% da sua vida máxima."))
_add("t_drum", "trinket", "Thunder Drum", "Tambor do Trovão", "note+burst", (150, 110, 60), None,
     dict(on="status", st=("stunned",), chance=0.15, act="nova", el=None, v=80, r=100, knock=250, icd=0.5),
     ("When you stun an enemy: {c}% chance of a shockwave around it ({v}% of the hit, pushes enemies).",
      "Ao atordoar um inimigo: {c}% de chance de uma onda de choque ao redor dele ({v}% do golpe, empurra)."))
_add("t_relic", "trinket", "Saint's Relic", "Relíquia do Santo", "holy+star", (190, 170, 90), None,
     dict(on="hit", tags=("holy",), chance=0.12, act="nova", el="holy", v=150, r=60, icd=0.3),
     ("Holy hits: {c}% chance of a smite on the target ({v}% of the hit, small area).",
      "Golpes sagrados: {c}% de chance de um castigo divino no alvo ({v}% do golpe, área pequena)."))
_add("t_orb", "trinket", "Arcane Orb", "Orbe Arcano", "orb+star", (120, 80, 170), None,
     dict(on="hit", tags=("arcane",), chance=0.15, act="chain", el="arcane", v=100, n=1, icd=0.2),
     ("Arcane hits: {c}% chance to fire an arcane missile at another enemy ({v}% of the hit).",
      "Golpes arcanos: {c}% de chance de disparar um míssil arcano em outro inimigo ({v}% do golpe)."))
_add("t_hourglass", "trinket", "Cracked Hourglass", "Ampulheta Rachada", "hourglass+star", (150, 130, 90), None,
     dict(on="kill", chance=0.05, act="cdr", v=1.0, icd=0.5),
     ("Kills: {c}% chance to cut the remaining cooldown of all your skills by {v} s.",
      "Abates: {c}% de chance de reduzir em {v} s a recarga restante de todas as suas habilidades."))
_add("t_phoenix", "trinket", "Phoenix Feather", "Pena da Fênix", "feather+flame", (200, 100, 40), None,
     dict(on="death", chance=1.0, act="revive", v=50),
     ("Once per run, when you would fall, you rise again with {v}% HP.",
      "Uma vez por run, quando você cairia, levanta de novo com {v}% da vida."))
_add("t_totem", "trinket", "Berserker Totem", "Totem do Berserker", "warcry+star", (160, 50, 40),
     {"cap:lowhp": 25})
_add("t_chime", "trinket", "Wind Chime", "Sino dos Ventos", "tornado+star", (90, 150, 140), None,
     dict(on="dodge", chance=1.0, act="buff", buff={"speed": 20, "crit": 10}, t=3.0, icd=3.0),
     ("When you dodge an attack: gain {buff} for {t} s.",
      "Ao esquivar de um ataque: ganha {buff} por {t} s."))
_add("t_echo", "trinket", "Echo Stone", "Pedra do Eco", "note+star", (100, 100, 140), {"cap:echo": 8})
_add("t_quake", "trinket", "Quake Idol", "Ídolo do Terremoto", "rock+star", (140, 105, 70), None,
     dict(on="hit", tags=("blunt", "earth"), chance=0.10, act="nova", el="earth", v=100, r=90, icd=0.3),
     ("Blunt or earth hits: {c}% chance of an aftershock around the target ({v}% of the hit as earth damage).",
      "Golpes de impacto ou terra: {c}% de chance de um tremor ao redor do alvo ({v}% do golpe em dano de "
      "terra)."))
_add("t_vampfang", "trinket", "Vampire Fang", "Presa de Vampiro", "skull+heal", (140, 30, 50), None,
     dict(on="kill", chance=1.0, act="heal", v=0.5, icd=0.25),
     ("Kills heal you for {v}% of your max HP.", "Abates curam {v}% da sua vida máxima."))
_add("t_warhorn", "trinket", "War Horn", "Trompa de Guerra", "warcry+up", (170, 120, 50), None,
     dict(on="kill", elite=True, chance=1.0, act="party_buff", buff={"dmg": 15}, t=6.0),
     ("Killing an elite or boss gives the whole party {buff} for {t} s.",
      "Abater um elite ou chefão dá à party inteira {buff} por {t} s."))
_add("t_ember", "trinket", "Ember Locket", "Medalhão da Brasa", "flame+burst", (190, 90, 40), None,
     dict(on="kill", st=("burning",), chance=1.0, act="nova_kill", el="fire", v=8, r=70, icd=0.2),
     ("Burning enemies you kill explode for {v}% of their max HP as fire damage.",
      "Inimigos queimando que você abate explodem causando {v}% da vida máxima deles em dano de fogo."))
_add("t_gale", "trinket", "Gale Feather", "Pena do Vendaval", "feather+tornado", (100, 160, 150), None,
     dict(on="hit", tags=("piercing", "projectile"), chance=0.10, act="nova", el="wind", v=50, r=90, knock=400,
          icd=0.3),
     ("Piercing or projectile hits: {c}% chance of a gust around the target ({v}% of the hit, pushes enemies away).",
      "Golpes perfurantes ou de projétil: {c}% de chance de uma rajada ao redor do alvo ({v}% do golpe, empurra os "
      "inimigos)."))
_add("t_lantern", "trinket", "Ghost Lantern", "Lanterna Fantasma", "flame_spirit+star", (120, 170, 210), None,
     dict(on="kill", chance=0.06, act="summon", el=None, v=100, t=5.0, icd=2.0, fixed=True),
     ("Kills: {c}% chance to free a lantern ghost that fights for you for {t} s.",
      "Abates: {c}% de chance de soltar um fantasma da lanterna que luta por você por {t} s."))
_add("t_censer", "trinket", "Holy Censer", "Incensário Sagrado", "holy+heal", (200, 180, 110), None,
     dict(on="hit", tags=None, chance=0.04, act="party_heal", v=1.5, icd=2.0),
     ("Any hit: {c}% chance to spread holy smoke: the whole party heals {v}% of max HP.",
      "Qualquer golpe: {c}% de chance de espalhar fumaça sagrada: a party inteira cura {v}% da vida máxima."))
_add("t_geode", "trinket", "Crystal Geode", "Geodo de Cristal", "rock+burst", (130, 190, 220), None,
     dict(on="crit", chance=0.15, act="nova", el=None, v=80, r=80, icd=0.4),
     ("Critical hits: {c}% chance the target bursts in crystal shards ({v}% of the hit, area).",
      "Acertos críticos: {c}% de chance de o alvo estourar em cacos de cristal ({v}% do golpe, em área)."))
_add("t_hellstone", "trinket", "Hellstone", "Pedra Infernal", "meteor+burst", (230, 90, 40), None,
     dict(on="hit", tags=("fire",), chance=0.15, act="nova", el="fire", v=120, r=80, icd=0.3),
     ("Fire hits: {c}% chance of a hellfire burst on the target ({v}% of the hit as fire damage, area).",
      "Golpes de fogo: {c}% de chance de uma explosão infernal no alvo ({v}% do golpe em dano de fogo, em área)."))
_add("t_demon_eye", "trinket", "Demon Eye", "Olho de Demônio", "eye+flame", (200, 50, 60), None,
     dict(on="crit", chance=0.12, act="chain", el="fire", v=80, n=2, icd=0.3),
     ("Critical hits: {c}% chance to shoot a fire bolt that jumps to {n} enemies ({v}% of the hit).",
      "Acertos críticos: {c}% de chance de disparar um raio de fogo que salta para {n} inimigos ({v}% do golpe)."))
_add("t_ash_urn", "trinket", "Ash Urn", "Urna de Cinzas", "flame+star", (130, 110, 100), None,
     dict(on="status", st=("burning",), chance=0.12, act="nova", el="fire", v=60, r=100, knock=220, icd=0.6),
     ("When you burn an enemy: {c}% chance the ashes blow up around it ({v}% of the hit, pushes enemies).",
      "Ao queimar um inimigo: {c}% de chance de as cinzas explodirem ao redor dele ({v}% do golpe, empurra)."))
_add("t_soulfire", "trinket", "Soulfire Lantern", "Lanterna de Fogo-Alma", "flame_spirit+up", (150, 90, 220), None,
     dict(on="kill", chance=0.10, act="buff", buff={"dmg": 10, "haste": 10}, t=4.0, icd=5.0),
     ("Kills: {c}% chance to gain {buff} for {t} s.", "Abates: {c}% de chance de ganhar {buff} por {t} s."))
_add("t_horn", "trinket", "Infernal Horn", "Chifre Infernal", "warcry+flame", (110, 40, 40),
     {"cap:lowhp": 15, "dmg": 4})
_add("t_static", "trinket", "Static Charm", "Amuleto Estático", "cloudbolt+star", (150, 140, 60), None,
     dict(on="hit", tags=None, chance=0.04, act="chain", el="lightning", v=80, n=2, icd=0.2),
     ("Any hit: {c}% chance to release a chain lightning that jumps to {n} enemies ({v}% of the hit).",
      "Qualquer golpe: {c}% de chance de soltar uma corrente de raios que salta para {n} inimigos ({v}% do golpe)."))


# ------------------------------------------------------------------ colares (1 por classe)
# Liberado quando QUALQUER personagem leva a classe ao nível máximo padrão (100; Novice 50; Freelancer 75).
# O tema vem da classe, mas qualquer classe pode usar.
def _cpt(n):
    import i18n_names
    return i18n_names.CLASS_PT.get(n, n)


def _neck(cid, eff=None, proc=None, text=None, flag=None):
    from data import CLASSES
    n = CLASSES[cid]["name"]
    ACC["n_" + cid] = dict(id="n_" + cid, cat="neck", name=(f"{n}'s Necklace", f"Colar do {_cpt(n)}"), icon=None,
                           color=CLASSES[cid]["color"], eff=eff or {}, proc=proc, text=text, cls=cid, flag=flag)


_neck("freelancer", {"dmg": 4, "crit": 2, "cdr": 2, "hp_pct": 4})
_neck("archer", flag=("ricochet", 30),
      text=("Your projectiles (physical or magical) have a {f}% chance to ricochet to another enemy when they "
            "would disappear on a hit (up to 2 times).",
            "Seus projéteis (físicos ou mágicos) têm {f}% de chance de ricochetear para outro inimigo quando "
            "sumiriam ao acertar (até 2 vezes)."))
_neck("bard", proc=dict(on="hit", tags=None, chance=0.06, act="party_buff", buff={"haste": 10}, t=4.0, icd=6.0),
      text=("Any hit: {c}% chance to play a battle tune: the whole party gains {buff} for {t} s.",
            "Qualquer golpe: {c}% de chance de tocar uma melodia de batalha: a party inteira ganha {buff} por {t} s."))
_neck("hunter", proc=dict(on="hit", tags=("projectile", "ranged"), chance=0.08, act="summon", el=None, v=60, t=6.0,
                          icd=2.0),
      text=("Ranged or projectile hits: {c}% chance to call a hunting falcon for {t} s ({v}% of the hit per strike).",
            "Golpes à distância ou de projétil: {c}% de chance de chamar um falcão de caça por {t} s ({v}% do golpe "
            "por ataque)."))
_neck("thaumaturge", proc=dict(on="hit", tags=("fire", "ice", "lightning"), chance=0.10, act="nova_rand", v=100,
                               r=70, icd=0.3),
      text=("Fire, ice or lightning hits: {c}% chance to cast an extra spell of a random element (fire, ice or "
            "lightning) on the target ({v}% of the hit, area).",
            "Golpes de fogo, gelo ou raio: {c}% de chance de lançar um feitiço extra de elemento aleatório (fogo, "
            "gelo ou raio) no alvo ({v}% do golpe, em área)."))
_neck("black_mage", {"dot_dmg": 20, "mag_dmg": 6})
_neck("time_mage", {"dmgvs:slowed": 15},
      proc=dict(on="kill", chance=1.0, act="cdr", v=0.3, icd=0.3),
      text=("Kills cut the remaining cooldown of all your skills by {v} s.",
            "Abates reduzem em {v} s a recarga restante de todas as suas habilidades."))
_neck("arcanist", proc=dict(on="hit", tags=("magical",), chance=0.08, act="chain", el="arcane", v=100, n=2, icd=0.3),
      text=("Magical hits: {c}% chance to release arcane missiles at {n} other enemies ({v}% of the hit each).",
            "Golpes mágicos: {c}% de chance de soltar mísseis arcanos em {n} outros inimigos ({v}% do golpe cada)."))
_neck("summoner", proc=dict(on="hit", tags=None, chance=0.06, act="summon", el="hit", v=50, t=6.0, icd=1.0),
      text=("Any hit: {c}% chance to evoke a summon of the hit's type (physical, fire, ice...) for {t} s ({v}% of "
            "the hit per strike).",
            "Qualquer golpe: {c}% de chance de evocar uma invocação do tipo do golpe (físico, fogo, gelo...) por {t} "
            "s ({v}% do golpe por ataque)."))
_neck("scholar", {"heal": 20, "cap:sanctuary": 10})
_neck("pugilist", proc=dict(on="hit", tags=("melee",), chance=1.0, act="stack", key="dmg", step=1, max=20, t=3.0,
                            icd=0.15),
      text=("Melee hits build a combo: +{step}% damage per hit (up to +{max}%), reset after {t} s without hitting.",
            "Golpes corpo a corpo montam um combo: +{step}% de dano por golpe (até +{max}%), zera após {t} s sem "
            "acertar."))
_neck("monk", {"dodge": 3}, proc=dict(on="dodge", chance=1.0, act="buff", buff={"dmg": 15, "critdmg": 20}, t=3.0,
                                      icd=2.0),
      text=("When you dodge an attack: gain {buff} for {t} s.", "Ao esquivar de um ataque: ganha {buff} por {t} s."))
_neck("white_monk", {"heal": 10}, proc=dict(on="hit", tags=("holy",), chance=1.0, act="heal", v=0.5, icd=0.3),
      text=("Holy hits heal you for {v}% of your max HP.", "Golpes sagrados curam {v}% da sua vida máxima."))
_neck("lancer", {"range": 15, "tagdmg:piercing": 10})
_neck("dragoon", {"area": 12, "tagdmg:knockback": 12})
_neck("templar", {"cap:anthem": 6, "tagdmg:holy": 8})
_neck("rogue", {"cap:ambush": 20, "crit": 3})
_neck("ninja", proc=dict(on="dodge", chance=1.0, act="summon", el=None, v=150, t=5.0, icd=3.0, fixed=True),
      text=("When you dodge an attack: a shadow clone fights for you for {t} s.",
            "Ao esquivar de um ataque: um clone das sombras luta por você por {t} s."))
_neck("assassin", {"critvs:poisoned": 8, "critvs:bleeding": 8},
      proc=dict(on="crit", chance=0.25, act="poison", v=40, icd=0.1),
      text=("Critical hits: {c}% chance to poison the target ({v}% of the hit over 4 s).",
            "Acertos críticos: {c}% de chance de envenenar o alvo ({v}% do golpe em 4 s)."))
_neck("conjurer", proc=dict(on="hit", tags=("water", "wind", "earth"), chance=0.15, act="nova_same", v=100, r=80,
                            icd=0.3),
      text=("Water, wind or earth hits: {c}% chance of a burst of the same element around the target ({v}% of the "
            "hit).",
            "Golpes de água, vento ou terra: {c}% de chance de uma explosão do mesmo elemento ao redor do alvo ({v}% "
            "do golpe)."))
_neck("white_mage", proc=dict(on="kill", chance=0.05, act="party_heal", v=4.0, icd=1.0),
      text=("Kills: {c}% chance to heal the whole party for {v}% of their max HP.",
            "Abates: {c}% de chance de curar a party inteira em {v}% da vida máxima."))
_neck("bishop", proc=dict(on="hit", tags=("aoe",), chance=0.08, act="nova_same", v=80, r=100, icd=0.4),
      text=("Area hits: {c}% chance to echo the blow in a bigger area ({v}% of the hit, same element).",
            "Golpes em área: {c}% de chance de ecoar o golpe numa área maior ({v}% do golpe, mesmo elemento)."))
_neck("gladiator", proc=dict(on="hurt", chance=0.30, act="retaliate", v=200, r=90, icd=0.5),
      text=("When you take damage: {c}% chance to strike back at nearby enemies ({v}% of the damage taken).",
            "Ao sofrer dano: {c}% de chance de revidar nos inimigos próximos ({v}% do dano sofrido)."))
_neck("paladin", proc=dict(on="hurt", chance=0.20, act="buff", buff={"dr": 20}, t=3.0, icd=4.0),
      text=("When you take damage: {c}% chance to gain {buff} for {t} s.",
            "Ao sofrer dano: {c}% de chance de ganhar {buff} por {t} s."))
_neck("spellblade", flag=("imbue", 20),
      text=("When you deal elemental damage, your physical hits are imbued with that element for 4 s: +{f}% damage "
            "and a chance to cause its status.",
            "Ao causar dano elemental, seus golpes físicos ficam imbuídos com aquele elemento por 4 s: +{f}% de dano "
            "e chance de causar o status dele."))
_neck("marauder", {"cap:rage": 30})
_neck("warrior", proc=dict(on="kill", chance=0.05, act="party_buff", buff={"dmg": 10, "dr": 10}, t=4.0, icd=6.0),
      text=("Kills: {c}% chance to let out a war cry: the whole party gains {buff} for {t} s.",
            "Abates: {c}% de chance de soltar um grito de guerra: a party inteira ganha {buff} por {t} s."))
_neck("berserker", proc=dict(on="hit", tags=None, chance=1.0, act="leech", v=1.5, icd=0.15),
      text=("Your hits heal you for {v}% of the damage dealt.", "Seus golpes curam {v}% do dano causado."))
_neck("freelancer_t2", {"dmg": 6, "cdr": 4, "range": 8, "area": 8})
_neck("warfarer", proc=dict(on="crit", chance=0.10, act="chain", el=None, v=120, n=3, icd=0.5),
      text=("Critical hits: {c}% chance to hurl a volley of spears at {n} other enemies ({v}% of the hit each).",
            "Acertos críticos: {c}% de chance de arremessar uma saraivada de lanças em {n} outros inimigos ({v}% do "
            "golpe cada)."))


# ------------------------------------------------------------------ emblemas (20): como os braceletes, mas para a PARTY
# Os efeitos fixos valem para todos os membros da party; os efeitos com chance disparam com os golpes/abates de
# QUALQUER membro e o bônus vai para a party inteira.
def _emb(aid, en, pt, icon, color, eff=None, proc=None, text=None):
    _add(aid, "emblem", en, pt, "banner+" + icon, color, eff, proc, text)


_emb("e_embers", "Emblem of Embers", "Emblema das Brasas", "flame", (170, 70, 40), {"dmgvs:burning": 12})
_emb("e_frost", "Emblem of Frost", "Emblema da Geada", "snowflake", (70, 130, 180), {"dmgvs:chilled": 12})
_emb("e_venom", "Emblem of Venom", "Emblema do Veneno", "poison", (80, 140, 60), {"dmgvs:poisoned": 12})
_emb("e_blood", "Emblem of Blood", "Emblema do Sangue", "drop", (150, 40, 50), {"dmgvs:bleeding": 12})
_emb("e_shatter", "Emblem of Shattering", "Emblema do Estilhaço", "burst", (150, 120, 60),
     {"dmgvs:stunned": 10, "critvs:stunned": 4})
_emb("e_snare", "Emblem of Snares", "Emblema das Armadilhas", "trap", (90, 110, 150), {"dmgvs:slowed": 12})
_emb("e_hunt", "Emblem of the Hunt", "Emblema da Caçada", "eye", (120, 90, 140), {"critvs:debuffed": 5})
_emb("e_thunder", "Emblem of Thunder", "Emblema do Trovão", "bolt", (170, 150, 40), None,
     dict(on="status", st=("stunned",), chance=1.0, act="party_stack", key="allattr", step=1, max=10, t=5.0, icd=0.3),
     ("When anyone in the party stuns an enemy: the whole party gains +{step} to every attribute for {t} s "
      "(stacks up to {max}x).",
      "Quando alguém da party atordoa um inimigo: a party inteira ganha +{step} em todos os atributos por {t} s "
      "(acumula até {max}x)."))
_emb("e_war", "Emblem of War", "Emblema da Guerra", "warcry", (170, 60, 40), None,
     dict(on="kill", chance=1.0, act="party_stack", key="dmg", step=1, max=15, t=4.0, icd=0.1),
     ("Each kill by the party gives the whole party +{step}% damage for {t} s (stacks up to +{max}%).",
      "Cada abate da party dá à party inteira +{step}% de dano por {t} s (acumula até +{max}%)."))
_emb("e_fervor", "Emblem of Fervor", "Emblema do Fervor", "up", (190, 90, 40), None,
     dict(on="status", st=("burning",), chance=1.0, act="party_buff", buff={"haste": 8}, t=3.0, icd=2.0),
     ("When anyone in the party burns an enemy: the whole party gains {buff} for {t} s.",
      "Quando alguém da party queima um inimigo: a party inteira ganha {buff} por {t} s."))
_emb("e_tide", "Emblem of the Tide", "Emblema da Maré", "wave", (60, 120, 170), None,
     dict(on="status", st=("chilled", "slowed"), chance=1.0, act="party_buff", buff={"dr": 10}, t=3.0, icd=2.0),
     ("When anyone in the party chills or slows an enemy: the whole party gains {buff} for {t} s.",
      "Quando alguém da party congela ou deixa um inimigo lento: a party inteira ganha {buff} por {t} s."))
_emb("e_dawn", "Emblem of Dawn", "Emblema da Aurora", "sun", (200, 170, 80), None,
     dict(on="kill", elite=True, chance=1.0, act="party_heal", v=8.0),
     ("When the party kills an elite or a boss: the whole party heals {v}% of max HP.",
      "Quando a party abate um elite ou chefão: a party inteira cura {v}% da vida máxima."))
_emb("e_mercy", "Emblem of Mercy", "Emblema da Misericórdia", "heal", (90, 160, 110), {"heal": 10, "regen5": 2})
_emb("e_guard", "Emblem of the Guard", "Emblema da Guarda", "shield", (110, 110, 130), {"armor": 3, "mres": 3})
_emb("e_swift", "Emblem of Swiftness", "Emblema da Rapidez", "boot", (60, 140, 120), {"speed": 8})
_emb("e_reach", "Emblem of Reach", "Emblema do Alcance", "spear", (110, 130, 90), {"range": 6, "area": 6})
_emb("e_focus", "Emblem of Focus", "Emblema do Foco", "clock", (60, 120, 150), {"cdr": 3})
_emb("e_sharp", "Emblem of Precision", "Emblema da Precisão", "star", (60, 140, 90), {"crit": 2, "critdmg": 8})
_emb("e_life", "Emblem of Life", "Emblema da Vida", "heart", (160, 60, 80), {"hp_pct": 6})
_emb("e_crusade", "Emblem of the Crusade", "Emblema da Cruzada", "holy", (190, 170, 90), {"dmg": 4})
# novos (biomas Cidade, Catedral e Subterrâneo)
_emb("e_ruin", "Emblem of Ruin", "Emblema da Ruína", "skull", (110, 60, 90), {"dot_dmg": 10})
_emb("e_seeker", "Emblem of the Seeker", "Emblema do Buscador", "magnet", (150, 110, 60), {"magnet": 15})
_emb("e_depths", "Emblem of the Depths", "Emblema das Profundezas", "gravity", (80, 60, 120), None,
     dict(on="status", st=("poisoned", "bleeding"), chance=1.0, act="party_buff", buff={"crit": 5}, t=3.0, icd=2.0),
     ("When anyone in the party poisons or makes an enemy bleed: the whole party gains {buff} for {t} s.",
      "Quando alguém da party envenena ou faz um inimigo sangrar: a party inteira ganha {buff} por {t} s."))

# Inferno
_emb("e_inferno", "Emblem of the Inferno", "Emblema do Inferno", "flame", (230, 80, 40),
     {"dmgvs:burning": 8, "critvs:burning": 4})
_emb("e_brimstone", "Emblem of Brimstone", "Emblema do Enxofre", "skull", (200, 160, 60), None,
     dict(on="kill", elite=True, chance=1.0, act="party_buff", buff={"crit": 10}, t=6.0),
     ("When the party kills an elite or a boss: the whole party gains {buff} for {t} s.",
      "Quando a party abate um elite ou chefão: a party inteira ganha {buff} por {t} s."))
_emb("e_pact", "Emblem of the Pact", "Emblema do Pacto", "heart", (140, 30, 50), {"critdmg": 12})
_emb("e_hellgate", "Emblem of the Hellgate", "Emblema do Portão do Inferno", "vortex", (170, 60, 90),
     {"area": 5, "dot_dmg": 6})
_emb("e_cinders", "Emblem of Cinders", "Emblema das Cinzas", "up", (160, 100, 70), None,
     dict(on="status", st=("burning",), chance=1.0, act="party_stack", key="dmg", step=1, max=10, t=4.0, icd=0.2),
     ("Each time the party burns an enemy: the whole party gains +{step}% damage for {t} s (stacks up to +{max}%).",
      "Cada vez que a party queima um inimigo: a party inteira ganha +{step}% de dano por {t} s (acumula até "
      "+{max}%)."))

# ------------------------------------------------------------------ textos dos procs dos braceletes
_BRACER_TEXT = {
    "b_momentum": ("When you stun an enemy: gain {buff} for {t} s.", "Ao atordoar um inimigo: ganha {buff} por {t} s."),
    "b_kindling": ("When you burn an enemy: gain {buff} for {t} s.", "Ao queimar um inimigo: ganha {buff} por {t} s."),
    "b_bloodletter": ("When you make an enemy bleed: heal {v}% of your max HP.",
                      "Ao fazer um inimigo sangrar: cura {v}% da sua vida máxima."),
    "b_glacial": ("When you chill an enemy: gain {buff} for {t} s.", "Ao congelar um inimigo: ganha {buff} por {t} s."),
    "b_tempest": ("When you stun or slow an enemy: gain {buff} for {t} s.",
                  "Ao atordoar ou deixar um inimigo lento: ganha {buff} por {t} s."),
    "b_hunter": ("When you kill a slowed, chilled or stunned enemy: gain {buff} for {t} s.",
                 "Ao abater um inimigo lento, congelando ou atordoado: ganha {buff} por {t} s."),
    "b_bulwark": ("When you take damage: {c}% chance to gain {buff} for {t} s.",
                  "Ao sofrer dano: {c}% de chance de ganhar {buff} por {t} s."),
    "b_reaper": ("When you kill an enemy with any debuff: cut the remaining cooldown of all your skills by {v} s.",
                 "Ao abater um inimigo com qualquer efeito negativo: reduz em {v} s a recarga restante de todas as "
                 "suas habilidades."),
    "b_toxin": ("When you poison an enemy: gain {buff} for {t} s.", "Ao envenenar um inimigo: ganha {buff} por {t} s."),
    "b_brimstone": ("When you kill a burning enemy: heal {v}% of your max HP.",
                    "Ao abater um inimigo queimando: cura {v}% da sua vida máxima."),
    "b_cinder": ("When you take damage: {c}% chance to gain {buff} for {t} s.",
                 "Ao sofrer dano: {c}% de chance de ganhar {buff} por {t} s."),
    "b_damned": ("When you burn or stun an enemy: gain {buff} for {t} s.",
                 "Ao queimar ou atordoar um inimigo: ganha {buff} por {t} s."),
}
for _aid, _t in _BRACER_TEXT.items():
    ACC[_aid]["text"] = _t

# ------------------------------------------------------------------ drops por fase (o resto: próximas fases)
# cada fase (e cada masmorra, em dungeons.py) dropa sempre 1 anel, 1 bracelete, 1 berloque e 1 emblema (colares: só pelo nível da classe)
STAGE_DROPS = {
    0: ["r_might", "b_butcher", "t_vampfang", "e_blood"],
    1: ["r_haste", "b_opportunist", "t_static", "e_mercy"],
    2: ["r_fire_dmg", "b_concussion", "t_storm", "e_shatter"],
    3: ["r_precision", "b_momentum", "t_lucky", "e_war"],
    4: ["r_ruin", "b_pyre", "t_meteor", "e_embers"],
    # Cidade Abandonada
    5: ["r_slash_dmg", "b_hobble", "t_hourglass", "e_snare"],
    6: ["r_piercing_dmg", "b_ambusher", "t_warhorn", "e_swift"],
    7: ["r_slash_crit", "b_venom", "t_plague", "e_venom"],
    8: ["r_blunt_crit", "b_bulwark", "t_drum", "e_reach"],
    9: ["r_arcane_dmg", "b_reaper", "t_lantern", "e_focus"],
    # Catedral
    10: ["r_holy_crit", "b_kindling", "t_echo", "e_crusade"],
    11: ["r_fire_crit", "b_rampage", "t_ember", "e_fervor"],
    12: ["r_mystic", "b_prism", "t_orb", "e_sharp"],
    13: ["r_holy_cd", "b_bloodletter", "t_censer", "e_life"],
    14: ["r_arcane_crit", "b_detonation", "t_phoenix", "e_ruin"],
    # Subterrâneo
    15: ["r_blunt_cd", "b_tempest", "t_gale", "e_thunder"],
    16: ["r_piercing_crit", "b_hunter", "t_totem", "e_seeker"],
    17: ["r_ice_dmg", "b_toxin", "t_chime", "e_tide"],
    18: ["r_ice_crit", "b_glacial", "t_geode", "e_frost"],
    19: ["r_lightning_dmg", "b_frostbite", "t_frostheart", "e_depths"],
    # Inferno
    20: ["r_fire_cd", "b_brimstone", "t_hellstone", "e_inferno"],
    21: ["r_slash_cd", "b_cinder", "t_soulfire", "e_brimstone"],
    22: ["r_lightning_crit", "b_hellfire", "t_ash_urn", "e_hellgate"],
    23: ["r_piercing_cd", "b_damned", "t_horn", "e_cinders"],
    24: ["r_arcane_cd", "b_pact", "t_demon_eye", "e_pact"],
}
ORDER = {c: [a for a, d in ACC.items() if d["cat"] == c] for c in CATS}

BUFF_FRAC = ("dmg", "haste", "speed", "dr")   # buffs em fração (os outros, crit/critdmg, em pontos %)
BUFF_NAME = {"allattr": ("to every attribute", "em todos os atributos"), "dmg": ("damage", "de dano"), "haste": ("attack speed", "de velocidade de ataque"),
             "speed": ("movement speed", "de velocidade de movimento"), "dr": ("damage reduction", "de redução de dano"),
             "crit": ("critical chance", "de chance crítica"), "critdmg": ("critical damage", "de dano crítico")}


def dungeon_of(aid):
    """Masmorra (portal vermelho) que dropa o acessório, ou None."""
    import dungeons
    for did, d in dungeons.DUNGEONS.items():
        if aid in d["drops"]:
            return did
    return None


def stage_of(aid):
    for s, lst in STAGE_DROPS.items():
        if aid in lst:
            return s
    return None


def pool_for(stage_ids):
    out = []
    for s in stage_ids:
        out += [a for a in STAGE_DROPS.get(s, []) if a not in out]
    return out


_VS_TAG = {"burning": "fire", "chilled": "ice", "poisoned": "poison", "bleeding": "bleed", "stunned": "stun",
           "slowed": "slow"}
_EFF_TAG = {"mag_dmg": "magical", "phys_dmg": "physical", "dot_dmg": "dot", "heal": "heal", "area": "aoe"}
_ACT_TAG = {"summon": "summon", "party_buff": "buff", "party_heal": "heal", "heal": "heal", "nova": "aoe",
            "nova_same": "aoe", "nova_rand": "aoe"}
_TAGS = {}


def tags(aid):
    """Tags do acessório (para o filtro do Joalheiro): as tags que ativam o efeito, o elemento do efeito e as
    tags/estados que os bônus citam (dano contra queimando = fire, dano de corte = slash...)."""
    if aid in _TAGS:
        return _TAGS[aid]
    from tags import TAG_ORDER
    a = ACC[aid]
    out = set()
    for k in a.get("eff") or {}:
        if ":" in k:
            pre, t = k.split(":", 1)
            if pre.startswith("tag"):
                out.add(t)
            elif pre in ("dmgvs", "critvs"):
                out.add(_VS_TAG.get(t, t))
        elif k in _EFF_TAG:
            out.add(_EFF_TAG[k])
    p = a.get("proc")
    if p:
        out.update(p.get("tags") or ())
        if p.get("el"):
            out.add(p["el"])
        if p.get("act") in _ACT_TAG:
            out.add(_ACT_TAG[p["act"]])
    _TAGS[aid] = res = [t for t in TAG_ORDER if t in out]
    return res


def mult(lv):
    return 1 + LV_STEP * lv


def name(aid, lang="en"):
    return ACC[aid]["name"][1 if lang == "pt" else 0]


def short_name(aid, lang="en"):
    """Nome curto para listas (emblemas sem o "Emblem of" / "Emblema da")."""
    n = name(aid, lang)
    if ACC[aid]["cat"] == "emblem":
        for pre in ("Emblem of the ", "Emblem of ", "Emblema das ", "Emblema dos ", "Emblema da ", "Emblema do ",
                    "Emblema de "):
            if n.startswith(pre):
                n = n[len(pre):]
                return n[0].upper() + n[1:]
    return n


def cat_name(cat, lang="en", plural=False):
    return (CAT_PLURAL if plural else CAT_NAME)[cat][1 if lang == "pt" else 0]


def effects(aid, lv=0):
    m = mult(lv)
    return {k: round(v * m, 2) for k, v in ACC[aid]["eff"].items()}


def _g(v):
    return f"{v:g}"


def buff_text(buff, m, lang):
    pt = lang == "pt"
    parts = []
    for k, v in buff.items():
        n = BUFF_NAME[k][1 if pt else 0]
        parts.append(f"+{_g(round(v * m, 1))}{'' if k == 'allattr' else '%'} {n}")
    return (" e " if pt else " and ").join(parts)


def desc(aid, lv=0, lang="en"):
    """Texto do efeito no nível lv (valores já com o bônus de nível)."""
    a = ACC[aid]
    m = mult(lv)
    parts = []
    if a["eff"]:
        txt = effects_text(effects(aid, lv), lang)
        if a["cat"] == "emblem":   # emblemas: os bônus valem para a party inteira
            txt = ("A party inteira: " if lang == "pt" else "Whole party: ") + txt
        else:
            txt = txt[0].upper() + txt[1:] if txt else txt
        parts.append(txt)
    p = a["proc"]
    fl = a.get("flag")
    if (p or fl) and a["text"]:
        t = a["text"][1 if lang == "pt" else 0]
        p = p or {}
        v = p.get("v", 0) * (m if p.get("act") not in ("revive",) and not p.get("fixed") else 1)
        parts.append(t.format(c=_g(round(p.get("chance", 0) * 100, 1)), v=_g(round(v, 2)), n=p.get("n", 0),
                              t=_g(p.get("t", 0)), buff=buff_text(p.get("buff", {}), m, lang),
                              f=_g(round(fl[1] * m, 1)) if fl else 0, step=_g(round(p.get("step", 0) * m, 2)),
                              max=_g(round(p.get("max", 0) * m, 1))))
    return ". ".join(s.rstrip(".") for s in parts) + "."


def icon(aid, size=40, dim=False):
    import skill_icons as si
    a = ACC[aid]
    if a["cat"] == "neck":   # colar: ícone da classe com uma moldura dourada
        ic = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(ic, (40, 34, 24), ic.get_rect(), border_radius=max(4, size // 6))
        inner = si.class_icon(a["cls"], size - 6)
        ic.blit(inner, (3, 3))
        pygame.draw.rect(ic, (230, 190, 90), ic.get_rect(), max(1, size // 16), border_radius=max(4, size // 6))
    else:
        ic = si._render(a["icon"], a["color"], (245, 230, 170), size)
    if dim:
        ic = ic.copy()
        ic.fill((110, 110, 120), special_flags=pygame.BLEND_RGB_MULT)
        ic.set_alpha(170)
    return ic


def cat_icon(cat, size=40):
    import skill_icons as si
    sym = {"ring": "ring", "bracer": "shield", "trinket": "star", "neck": "heart", "emblem": "banner"}[cat]
    return si._render(sym, (60, 60, 75), (200, 200, 215), size)


NECK_DUP_FRAGS = 5   # colar repetido: +5 fragmentos da classe dele


def upgrade_cost(lv, aid=None):
    """Para ir de +lv a +lv+1: anéis/braceletes/berloques gastam fragmentos da categoria (1, 2, 3, 4, 5);
    colares gastam fragmentos da classe deles (5, 10, 15, 20, 25)."""
    if aid is not None and ACC[aid]["cat"] == "neck":
        return 5 * (lv + 1)
    return lv + 1


def neck_class(aid):
    return ACC[aid].get("cls")
