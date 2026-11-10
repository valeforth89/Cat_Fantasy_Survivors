"""Ícones das habilidades (ativas e passivas), desenhados com primitivas e guardados em cache.

O símbolo é escolhido pelo NOME da habilidade (palavras-chave em inglês e no português antigo), depois pelo
elemento e por fim pelo arquétipo. Assim, qualquer habilidade criada ou renomeada na planilha ganha um ícone
coerente automaticamente. Para forçar um símbolo específico, use ICON_OVERRIDES (nome -> símbolo).
"""
import math

import pygame

import pixel
from pygame.math import Vector2 as V

from data import ELEMENTS

BASE = 96                       # tamanho em que o ícone é desenhado (depois é reduzido)
W = (240, 240, 245)
DARK = (25, 25, 32)
STEEL = (205, 210, 220)
WOOD = (150, 105, 60)
GOLD = (245, 205, 80)
RED = (225, 70, 70)
GREEN = (110, 220, 120)
_CACHE = {}

# nome exato da habilidade -> símbolo (para quando a palavra-chave não basta)
ICON_OVERRIDES = {
    "Basic Attack": None,       # (usa a arma; ver weapon_symbol)
    # "principal+selo" = símbolo grande com um selo pequeno no canto
    "Strike": "slash_arc", "Stone Toss": "rock", "Quick Stab": "dagger",
    "Dust Kick": "boot", "Throwing Daggers": "fan_blades", "Second Wind": "heart_plus",
    "Whirling Blade": "spin", "Rally": "banner", "Pommel Bash": "sword+star",
    "Wanderer's Edge": "sword_up", "Twin Shot": "arrows2", "Pinning Arrow": "arrow+clock",
    "Volley": "fan", "Fire Arrow": "arrow+flame", "Hawk Eye": "eye",
    "Snare Trap": "trap", "Hail of Arrows": "rain+arrow", "Storm Arrow": "arrow+bolt",
    "Snipe": "eye+arrow", "Bear Trap": "trap", "Wolf Companion": "wolf",
    "Multishot": "fan", "Predator Focus": "eye", "Explosive Arrow": "arrow+burst",
    "Arrow Storm": "rain+tornado", "Melodic Arrow": "arrow+note", "Battle Ballad": "harp",
    "Requiem": "skull+note", "Lullaby": "moon", "Harp Strings": "note",
    "Song of Healing": "heal+note", "Swift Tempo": "boot+note", "Discord": "note+burst",
    "Echo Arrow": "arrow+wave", "Grand Finale": "star+note", "Spark": "bolt",
    "Frost Shard": "snowflake", "Flame Wave": "wave+flame", "Thunder": "cloudbolt",
    "Ice Nova": "rings+snowflake", "Fire Pillar": "flame+aura", "Chain Lightning": "bolt+arrows2",
    "Meteor": "meteor", "Firaga": "flame", "Thundaga": "cloudbolt",
    "Blizzaga": "snowflake", "Bio": "poison", "Flare": "sun",
    "Aero": "tornado", "Quake": "crack", "Scathe": "missile",
    "Freeze": "snowflake+star", "Ultima": "burst", "Slow": "boot+clock",
    "Comet": "meteor", "Quick": "hourglass+up", "Graviga": "gravity+burst",
    "Time Rift": "vortex+clock", "Reverse": "heal+clock", "Meteor Swarm": "meteor+rain",
    "Arcane Shield": "shield_orb", "Mana Bolt": "orb", "Rune Circle": "rune",
    "Arcane Orbs": "orbit", "Focus": "eye", "Arcane Burst": "rings",
    "Mana Spring": "heal", "Seeking Runes": "rune+missile", "Arcane Explosion": "burst+rune",
    "Shiva": "summon+snowflake", "Ramuh's Judgment": "cloudbolt", "Titan's Landslide": "crack",
    "Garuda": "wing", "Leviathan's Tide": "wave", "Phoenix Flame": "bird+flame",
    "Megaflare": "sun", "Area Cure": "heal", "Insight": "eye",
    "Whispering Dawn": "sun", "Ruin": "rune", "Miasma": "poison",
    "Sacred Soil": "shield", "Broil": "flame", "Fey Blessing": "wing+heal",
    "Rapid Punches": "fist+fist", "Shockwave": "rings", "Uppercut": "fist+up",
    "Jab Combo": "fist+bolt", "Iron Body": "shield", "Flowing Stance": "boot+up", "Dagger Slash": "dagger", "Palm Strike": "fist+wave",
    "Roundhouse Kick": "spin", "Ki Wave": "wave", "Ground Pound": "crack",
    "Hundred Fists": "fist+burst", "Fist Flurry": "fist+fist", "Chakra Burst": "burst",
    "Spinning Kick": "spin", "Dragon Kick": "boot", "Inner Focus": "eye",
    "Tiger Palm": "fist+star", "Aura Blast": "orb", "Chi Field": "aura",
    "Rising Phoenix": "bird+flame", "Final Heaven": "sun", "Restoring Chi": "heal",
    "Holy Palm": "fist+holy", "Purifying Strike": "holy", "Mantra": "up+shield",
    "Serene Breath": "heart_plus", "Holy Kick": "boot+holy", "Spirit Shield": "shield_orb",
    "Radiant Palm": "sun", "Divine Pulse": "aura", "Thrust": "spear+spear",
    "Spear Spin": "spin", "Lunge": "spear+boot", "Sweep": "slash_arc",
    "Javelin": "spear+arrow", "Impale": "spear+star", "Phalanx": "shield+up",
    "Piercing Charge": "spear+burst", "Javelin Rain": "rain", "Skewer Storm": "spear+bolt",
    "Jump": "jump", "Elemental Breath": "tri", "Dragon Fang": "spear+star",
    "High Jump": "jump+up", "Lance Sweep": "slash_arc", "Wyvern Wings": "wing",
    "Fire Breath": "cone+flame", "Thunder Spear": "spear+bolt", "Dragon Dive": "jump+burst",
    "Holy Thrust": "spear+holy", "Blessing": "holy", "Banner of Valor": "banner",
    "Consecrate": "aura", "Holy Lance": "arrow+holy", "Smite": "sun",
    "Divine Guard": "shield+holy", "Lay on Hands": "heal", "Judgment": "holy+burst",
    "Thrown Knives": "fan_blades", "Smoke Bomb": "bomb", "Backstab": "dagger+skull",
    "Caltrops": "trap", "Poison Knife": "dagger+poison", "Quick Step": "boot",
    "Fan of Blades": "spin+dagger", "Mug": "fist", "Shadow Strike": "clone",
    "Deadly Dance": "spin", "Shuriken": "shuriken", "Ninjutsu": "tri",
    "Kunai Barrage": "fan_blades", "Shadow Clone": "clone", "Katon": "cone+flame",
    "Raiton": "cloudbolt", "Suiton": "vortex", "Shunshin": "boot",
    "Giant Shuriken": "shuriken+up", "Twin Blades": "crossed", "Poisoned Daggers": "fan_blades+poison",
    "Toxic Cloud": "poison", "Ambush": "dagger+star", "Venom Edge": "poison+up",
    "Shadowstep": "clone", "Garrote": "trap", "Blade Flurry": "spin",
    "Viper Bite": "dagger+poison", "Death Mark": "skull", "Natural Elements": "tri",
    "Cure": "heal", "Water Bolt": "drop", "Gust": "cone+tornado",
    "Stone Spike": "rock", "Regen": "heart_plus", "Whirlpool": "vortex",
    "Earthquake": "crack", "Cyclone": "tornado", "Tidal Wave": "wave",
    "Holy": "holy", "Curaga": "heal", "Protect": "shield",
    "Shell": "shield_orb", "Regenera": "heart_plus", "Banish": "orb",
    "Holy Light": "sun", "Benediction": "wing", "Divine Ring": "aura",
    "Holyja": "sun+burst", "Grand Elements": "tri", "Tornado": "tornado",
    "Stone Rain": "rock", "Water Lance": "spear+drop", "Gale": "cone+tornado",
    "Mud Pool": "vortex", "Purify": "heart_plus", "Landslide": "crack",
    "Maelstrom": "wave", "Slash": "slash_arc", "Shield Wall": "shield",
    "Shield Bash": "shield+star", "Riposte": "crossed", "Second Breath": "heart_plus",
    "Sword Toss": "sword+arrow", "Arena Spin": "spin", "Fortify": "shield+up",
    "Crushing Blow": "burst", "Champion's Slash": "sword_up", "Holy Slash": "slash_arc+holy",
    "Healing Light": "heal", "Shield of Faith": "shield+holy", "Holy Strike": "holy",
    "Sacred Circle": "aura", "Righteous Charge": "shield+burst", "Aegis": "shield_orb",
    "Sanctuary": "heart_plus", "Holy Judgment": "sun", "Flame Blade": "sword+flame",
    "Glacial Blade": "sword+snowflake", "Thunder Blade": "sword+bolt", "Wind Blade": "sword+tornado",
    "Earth Blade": "sword+rock", "Arcane Wave": "wave", "Enchant": "rune",
    "Venom Blade": "sword+poison", "Holy Blade": "sword+holy", "Elemental Fury": "tri",
    "Axe Chop": "axe+burst", "Axe Throw": "axe+arrow", "Cleave": "slash_arc",
    "Rampage": "warcry", "Ground Slam": "crack", "Bloodlust": "heart_plus",
    "Twin Axe Throw": "axe+arrows2", "Brutal Swing": "spin", "Skull Splitter": "skull",
    "Earthsplitter": "crack+spear", "War Cry": "warcry", "Overpower": "burst",
    "Iron Will": "shield+up", "Heavy Cleave": "slash_arc", "Earthshaker": "crack",
    "Warrior's Resolve": "heart_plus", "Axe Storm": "axe+tornado", "Decimate": "spin",
    "Furious Chop": "axe+burst", "Whirlwind": "tornado", "Fury": "warcry",
    "Blood Frenzy": "warcry+bolt", "Reckless Swing": "slash_arc", "Leap Slam": "jump",
    "Savage Throw": "axe+arrow", "Rage Aura": "aura+warcry", "Bloodbath": "heart_plus",
    "Rampaging Storm": "spin", "Arcane Missile": "missile", "Carbuncle": "gem_beast",
    "Ifrit": "flame_spirit", "Falcon": "bird", "Gravity": "gravity",
    "Haste": "hourglass", "Stop": "clock", "Arrow": "arrow",
    "Arrow Rain": "rain", "Piercing Shot": "arrows2", "Barrage": "rain",
    "Fire": "flame", "Tri-Elemental": "tri",
}

# palavras-chave (minúsculas) -> símbolo; a primeira que aparecer no nome vence
KEYWORDS = [
    (("arrow rain", "rain of", "chuva de flechas", "barrage", "barragem"), "rain"),
    (("piercing shot", "tiro perfurante"), "arrows2"),
    (("melodic", "melódica", "ballad", "balada", "requiem", "réquiem", "song", "sound"), "note"),
    (("arrow", "flecha", "shot", "tiro"), "arrow"),
    (("falcon", "falcão", "hawk", "bird"), "bird"),
    (("carbuncle", "carbúnculo"), "gem_beast"),
    (("ifrit",), "flame_spirit"),
    (("summon", "invoca"), "summon"),
    (("tri-elemental", "elemental breath", "sopro", "ninjutsu", "natural elements", "elementos naturais"), "tri"),
    (("blizzaga", "blizzard", "ice", "gelo", "glacial", "frost"), "snowflake"),
    (("thundaga", "thunder", "lightning", "trovej", "relâmpago", "bolt"), "bolt"),
    (("firaga", "fire", "fogo", "flame", "flamej", "burn"), "flame"),
    (("tornado", "whirlwind", "redemoinho", "wind", "vento", "aero"), "tornado"),
    (("water", "água", "tide", "wave"), "drop"),
    (("stone", "pedra", "rock", "earth", "quake"), "rock"),
    (("gravity", "gravidade"), "gravity"),
    (("stop", "parar", "time"), "clock"),
    (("haste", "acelerar", "quick"), "hourglass"),
    (("toxic", "tóxica", "poison", "envenen", "venom"), "poison"),
    (("smoke", "fumaça", "bomb", "bomba"), "bomb"),
    (("shuriken",), "shuriken"),
    (("knife", "knives", "facas", "dagger", "adaga", "twin blades", "lâminas gêmeas"), "dagger"),
    (("shield wall", "muralha", "shield", "escudo", "protect", "proteção"), "shield"),
    (("blessing", "bênção", "holy", "sagrad", "light", "luz"), "holy"),
    (("curaga", "cure", "cura", "heal", "chi", "restor", "regenera"), "heal"),
    (("war cry", "grito", "fury", "fúria", "rage"), "warcry"),
    (("jump", "salto", "leap"), "jump"),
    (("spin", "giro", "spinning", "giratório", "kick", "chute"), "spin"),
    (("chakra", "shockwave", "onda de choque", "burst", "explos"), "burst"),
    (("punch", "soco", "fist", "punho", "palm", "palma"), "fist"),
    (("thrust", "estocada", "spear", "lança", "lance"), "spear"),
    (("axe", "machad", "chop"), "axe"),
    (("missile", "míssil", "arcane", "arcano"), "missile"),
    (("orbit", "orbita"), "orbit"),
    (("aura",), "aura"),
    (("slash", "corte", "blade", "lâmina", "strike", "golpe", "sword", "espada"), "sword"),
]

ARCHETYPE_SYMBOL = {"shot": "missile", "slash": "sword", "thrust": "spear", "strike": "burst", "cone": "cone",
                    "aura": "aura", "orbit": "orbit", "heal": "heal", "buff": "up", "summon": "summon",
                    "cloud": "poison"}
ELEMENT_SYMBOL = {"fire": "flame", "ice": "snowflake", "lightning": "bolt", "water": "drop", "wind": "tornado",
                  "earth": "rock", "poison": "poison", "holy": "holy", "arcane": "missile", "sound": "note",
                  "gravity": "gravity", "time": "clock", "smoke": "bomb"}

# passivas: efeito -> (símbolo, cor de fundo)
PASSIVE_SYMBOL = {
    "phys_dmg": ("sword_up", (150, 70, 60)), "mag_dmg": ("orb_up", (90, 70, 160)), "dmg": ("burst_up", (160, 90, 40)),
    "hp_pct": ("heart", (150, 50, 70)), "hp_flat": ("heart", (150, 50, 70)), "speed": ("boot", (60, 120, 90)),
    "cdr": ("hourglass", (70, 90, 150)), "crit": ("star", (150, 120, 30)), "critdmg": ("star_up", (160, 90, 30)),
    "defense": ("shield", (80, 90, 110)), "area": ("rings", (60, 110, 120)), "heal": ("heal", (60, 130, 80)),
    "range": ("spear", (70, 110, 150)),
    "duration": ("clock", (90, 80, 140)), "regen5": ("heart_plus", (60, 130, 80)), "magnet": ("magnet", (130, 60, 60)),
    "armor": ("shield", (100, 100, 115)), "mres": ("shield_orb", (80, 70, 150)), "dodge": ("feather", (60, 120, 110)),
    "str": ("fist", (150, 70, 50)), "agi": ("feather", (60, 130, 70)), "int": ("book", (70, 70, 160)),
    "vit": ("heart", (150, 50, 70)),
}

WEAPON_KEYWORDS = [(("bow", "arco"), "bow"), (("staff", "cajado", "scepter", "cetro"), "staff"),
                   (("grimoire", "grimório", "book"), "book"), (("fist", "punho", "claw", "garra"), "fist"),
                   (("spear", "lança"), "spear"), (("knife", "knives", "faca", "dagger", "adaga", "kunai"), "dagger"),
                   (("axe", "machado"), "axe"), (("sword", "espada", "blade"), "sword")]


def _symbol_for(name, kind=None, element=None, cycle=None):
    n = (name or "").lower()
    if name in ICON_OVERRIDES and ICON_OVERRIDES[name]:
        return ICON_OVERRIDES[name]
    if n.startswith("basic attack") or n.startswith("ataque básico"):
        for keys, sym in WEAPON_KEYWORDS:
            if any(k in n for k in keys):
                return sym
        return "sword"
    for keys, sym in KEYWORDS:
        if any(k in n for k in keys):
            return sym
    if cycle:
        return "tri"
    if element in ELEMENT_SYMBOL:
        return ELEMENT_SYMBOL[element]
    return ARCHETYPE_SYMBOL.get(kind, "burst")


# ---------------------------------------------------------------------------
# Desenho dos símbolos (canvas 96x96, centro 48,48)
# ---------------------------------------------------------------------------
def _rot(pts, ang, cx=48, cy=48):
    out = []
    for x, y in pts:
        v = V(x - cx, y - cy).rotate(ang)
        out.append((cx + v.x, cy + v.y))
    return out


def _poly(s, col, pts, w=0):
    pygame.draw.polygon(s, col, pts, w)
    if w == 0:
        pygame.draw.polygon(s, DARK, pts, 3)


def sym_sword(s, acc):
    blade = _rot([(44, 14), (52, 14), (52, 62), (48, 70), (44, 62)], 40)
    _poly(s, STEEL, blade)
    pygame.draw.line(s, GOLD, *_rot([(34, 62), (62, 62)], 40), 8)
    pygame.draw.line(s, WOOD, *_rot([(48, 64), (48, 84)], 40), 8)


def sym_sword_up(s, acc):
    sym_sword(s, acc)
    _up_arrow(s, (70, 70))


def _up_arrow(s, at, col=GREEN):
    x, y = at
    _poly(s, col, [(x, y - 14), (x + 11, y), (x + 4, y), (x + 4, y + 12), (x - 4, y + 12), (x - 4, y), (x - 11, y)])


def sym_spear(s, acc):
    pygame.draw.line(s, WOOD, *_rot([(48, 22), (48, 88)], 45), 7)
    _poly(s, STEEL, _rot([(48, 6), (58, 26), (48, 32), (38, 26)], 45))


def sym_axe(s, acc):
    pygame.draw.line(s, WOOD, *_rot([(48, 16), (48, 88)], 30), 8)
    _poly(s, STEEL, _rot([(50, 16), (76, 10), (80, 34), (76, 50), (50, 40)], 30))


def sym_dagger(s, acc):
    for ang, dx in ((30, -10), (-30, 10)):
        pts = _rot([(45, 18), (51, 18), (51, 56), (48, 62), (45, 56)], ang)
        _poly(s, STEEL, [(x + dx, y) for x, y in pts])
        pygame.draw.line(s, WOOD, *[(x + dx, y) for x, y in _rot([(48, 60), (48, 78)], ang)], 7)


def sym_bow(s, acc):
    pts = [(30 + 26 * math.sin(math.radians(t)), 48 - 38 * math.cos(math.radians(t))) for t in range(0, 181, 15)]
    pygame.draw.lines(s, WOOD, False, pts, 7)
    pygame.draw.line(s, W, pts[0], pts[-1], 2)
    sym_arrow_line(s, (24, 48), (82, 48))


def sym_arrow_line(s, a, b, col=STEEL):
    a, b = V(a), V(b)
    d = (b - a).normalize()
    pygame.draw.line(s, WOOD, a, b - d * 10, 5)
    n = V(-d.y, d.x)
    _poly(s, col, [b, b - d * 16 + n * 8, b - d * 16 - n * 8])
    pygame.draw.line(s, RED, a, a + d * 10 + n * 6, 4)
    pygame.draw.line(s, RED, a, a + d * 10 - n * 6, 4)


def sym_arrow(s, acc):
    sym_arrow_line(s, (16, 80), (80, 16))


def sym_arrows2(s, acc):
    sym_arrow_line(s, (12, 72), (72, 12))
    sym_arrow_line(s, (26, 86), (86, 26))


def sym_rain(s, acc):
    for x, y in ((24, 20), (48, 34), (72, 20), (36, 56), (62, 56)):
        sym_arrow_line(s, (x, y - 14), (x, y + 18))


def sym_staff(s, acc):
    pygame.draw.line(s, WOOD, (30, 86), (62, 22), 7)
    pygame.draw.circle(s, acc, (66, 18), 13)
    pygame.draw.circle(s, DARK, (66, 18), 13, 3)


def sym_book(s, acc):
    _poly(s, acc, [(22, 22), (74, 22), (74, 78), (22, 78)])
    pygame.draw.rect(s, W, (64, 26, 7, 48))
    pygame.draw.circle(s, GOLD, (44, 50), 9)


def sym_fist(s, acc):
    _poly(s, (235, 190, 150), [(26, 34), (66, 30), (74, 44), (72, 70), (34, 74), (24, 58)])
    for x in (36, 48, 60):
        pygame.draw.line(s, DARK, (x, 34), (x + 2, 50), 3)
    pygame.draw.line(s, DARK, (26, 54), (48, 54), 3)


def sym_flame(s, acc):
    outer = [(48, 8), (66, 34), (74, 58), (64, 80), (48, 88), (32, 80), (22, 58), (32, 40), (40, 52), (42, 30)]
    _poly(s, (240, 110, 40), outer)
    _poly(s, (255, 210, 80), [(48, 40), (58, 60), (54, 78), (48, 82), (40, 76), (38, 62)])


def sym_snowflake(s, acc):
    col = (170, 225, 255)
    for a in range(0, 180, 60):
        d = V(0, -36).rotate(a)
        pygame.draw.line(s, col, (48 - d.x, 48 - d.y), (48 + d.x, 48 + d.y), 7)
        for sgn in (1, -1):
            for t in (0.55,):
                p = V(48, 48) + d * t * sgn
                b1 = p + d.rotate(40).normalize() * 12 * sgn
                b2 = p + d.rotate(-40).normalize() * 12 * sgn
                pygame.draw.line(s, col, p, b1, 5)
                pygame.draw.line(s, col, p, b2, 5)
    pygame.draw.circle(s, W, (48, 48), 7)


def sym_bolt(s, acc):
    _poly(s, (255, 235, 90), [(56, 6), (24, 52), (46, 52), (36, 90), (72, 40), (50, 40), (64, 6)])


def sym_tornado(s, acc):
    col = (180, 250, 200)
    for i, (w, y) in enumerate(((60, 18), (48, 32), (38, 46), (28, 60), (18, 74))):
        pygame.draw.arc(s, col, pygame.Rect(48 - w / 2 + i * 3, y - 6, w, 14), 0, math.pi * 2, 5)


def sym_drop(s, acc):
    pts = [(48, 10)] + [(48 + 24 * math.cos(math.radians(a)), 60 + 24 * math.sin(math.radians(a)))
                        for a in range(-30, 211, 15)]
    _poly(s, (80, 150, 255), pts)
    pygame.draw.circle(s, W, (40, 62), 6)


def sym_rock(s, acc):
    _poly(s, (170, 135, 90), [(20, 66), (30, 34), (52, 22), (74, 36), (80, 62), (60, 80), (32, 80)])
    pygame.draw.line(s, DARK, (40, 40), (52, 60), 3)
    pygame.draw.line(s, DARK, (52, 60), (66, 50), 3)


def sym_gravity(s, acc):
    for i in range(4):
        r = 34 - i * 8
        pygame.draw.arc(s, (170, 130, 255), pygame.Rect(48 - r, 48 - r, 2 * r, 2 * r), i * 0.8, i * 0.8 + 4.2, 5)
    pygame.draw.circle(s, DARK, (48, 48), 8)
    pygame.draw.circle(s, (170, 130, 255), (48, 48), 8, 2)


def sym_clock(s, acc):
    pygame.draw.circle(s, (230, 220, 255), (48, 48), 34)
    pygame.draw.circle(s, DARK, (48, 48), 34, 4)
    pygame.draw.line(s, DARK, (48, 48), (48, 24), 5)
    pygame.draw.line(s, DARK, (48, 48), (64, 56), 5)


def sym_hourglass(s, acc):
    _poly(s, (240, 220, 160), [(26, 14), (70, 14), (52, 48), (70, 82), (26, 82), (44, 48)])
    _poly(s, GOLD, [(36, 70), (60, 70), (66, 80), (30, 80)])
    pygame.draw.line(s, WOOD, (20, 12), (76, 12), 6)
    pygame.draw.line(s, WOOD, (20, 84), (76, 84), 6)


def sym_poison(s, acc):
    pts = [(48, 10)] + [(48 + 24 * math.cos(math.radians(a)), 60 + 24 * math.sin(math.radians(a)))
                        for a in range(-30, 211, 15)]
    _poly(s, (140, 220, 70), pts)
    pygame.draw.circle(s, DARK, (40, 58), 5)
    pygame.draw.circle(s, DARK, (56, 58), 5)
    pygame.draw.line(s, DARK, (40, 72), (56, 72), 4)


def sym_bomb(s, acc):
    pygame.draw.circle(s, (60, 60, 70), (44, 56), 26)
    pygame.draw.circle(s, DARK, (44, 56), 26, 3)
    pygame.draw.circle(s, W, (36, 48), 6)
    pygame.draw.line(s, WOOD, (60, 34), (70, 20), 5)
    pygame.draw.circle(s, (255, 170, 60), (72, 16), 7)


def sym_shuriken(s, acc):
    pts = []
    for i in range(8):
        r = 38 if i % 2 == 0 else 12
        a = math.radians(i * 45 + 22)
        pts.append((48 + math.cos(a) * r, 48 + math.sin(a) * r))
    _poly(s, STEEL, pts)
    pygame.draw.circle(s, DARK, (48, 48), 6)


def sym_shield(s, acc):
    _poly(s, (150, 160, 180), [(22, 18), (74, 18), (72, 52), (48, 84), (24, 52)])
    _poly(s, (90, 100, 125), [(48, 24), (66, 24), (64, 52), (48, 74)])


def sym_shield_orb(s, acc):
    sym_shield(s, acc)
    pygame.draw.circle(s, (180, 140, 255), (48, 46), 11)


def sym_holy(s, acc):
    pygame.draw.circle(s, (255, 240, 170), (48, 48), 34)
    pygame.draw.rect(s, W, (42, 18, 12, 60))
    pygame.draw.rect(s, W, (28, 34, 40, 12))
    pygame.draw.circle(s, GOLD, (48, 48), 34, 4)


def sym_heal(s, acc):
    pygame.draw.circle(s, (90, 210, 120), (48, 48), 34)
    pygame.draw.rect(s, W, (40, 22, 16, 52))
    pygame.draw.rect(s, W, (22, 40, 52, 16))


def sym_heart(s, acc):
    pygame.draw.circle(s, (230, 70, 90), (36, 38), 16)
    pygame.draw.circle(s, (230, 70, 90), (60, 38), 16)
    pygame.draw.polygon(s, (230, 70, 90), [(21, 44), (75, 44), (48, 80)])


def sym_heart_plus(s, acc):
    sym_heart(s, acc)
    pygame.draw.rect(s, W, (44, 30, 8, 26))
    pygame.draw.rect(s, W, (35, 39, 26, 8))


def sym_warcry(s, acc):
    _poly(s, (230, 140, 80), [(20, 40), (40, 40), (60, 24), (60, 72), (40, 56), (20, 56)])
    for r in (16, 26):
        pygame.draw.arc(s, W, pygame.Rect(56 - r, 48 - r, 2 * r, 2 * r), -0.8, 0.8, 4)


def sym_jump(s, acc):
    _up_arrow(s, (48, 30), (130, 180, 255))
    pygame.draw.line(s, STEEL, (20, 84), (76, 84), 5)
    sym_spear_small(s)


def sym_spear_small(s):
    pygame.draw.line(s, WOOD, (30, 80), (66, 44), 5)
    pygame.draw.polygon(s, STEEL, [(66, 44), (60, 40), (74, 34), (70, 50)])


def sym_spin(s, acc):
    for a in (0, 120, 240):
        pygame.draw.arc(s, W, pygame.Rect(16, 16, 64, 64), math.radians(a), math.radians(a + 80), 7)
        tip = V(48, 48) + V(32, 0).rotate(-(a + 80))
        pygame.draw.circle(s, W, tip, 6)


def sym_burst(s, acc):
    pts = []
    for i in range(16):
        r = 40 if i % 2 == 0 else 20
        a = math.radians(i * 22.5)
        pts.append((48 + math.cos(a) * r, 48 + math.sin(a) * r))
    _poly(s, acc, pts)
    pygame.draw.circle(s, W, (48, 48), 12)


def sym_burst_up(s, acc):
    sym_burst(s, acc)
    _up_arrow(s, (70, 70))


def sym_missile(s, acc):
    for i, r in enumerate((6, 9, 12)):
        pygame.draw.circle(s, (*acc[:3],), (28 + i * 12, 68 - i * 12), r)
    pygame.draw.circle(s, W, (68, 28), 16)
    pygame.draw.circle(s, acc, (68, 28), 16, 5)


def sym_orb_up(s, acc):
    pygame.draw.circle(s, (180, 140, 255), (42, 48), 24)
    pygame.draw.circle(s, W, (34, 40), 7)
    _up_arrow(s, (70, 70))


def sym_orbit(s, acc):
    pygame.draw.circle(s, W, (48, 48), 30, 3)
    for a in (0, 120, 240):
        p = V(48, 48) + V(30, 0).rotate(a + 30)
        pygame.draw.circle(s, GOLD, p, 9)


def sym_aura(s, acc):
    for r, w in ((36, 4), (26, 4), (14, 0)):
        pygame.draw.circle(s, acc, (48, 48), r, w)


def sym_rings(s, acc):
    for r in (34, 22, 10):
        pygame.draw.circle(s, (150, 230, 240), (48, 48), r, 4)


def sym_ring(s, acc):
    """Anel (joia): aro dourado com uma pedra na cor do acessório."""
    pygame.draw.circle(s, (120, 80, 20), (48, 58), 28, 12)
    pygame.draw.circle(s, (240, 200, 80), (48, 58), 26, 7)
    _poly(s, acc, [(48, 14), (64, 28), (48, 42), (32, 28)])
    _poly(s, (255, 255, 255), [(46, 20), (52, 26), (46, 30)])


def sym_cone(s, acc):
    _poly(s, acc, [(16, 48), (82, 18), (88, 48), (82, 78)])


def sym_up(s, acc):
    _up_arrow(s, (48, 44), GOLD)
    pygame.draw.circle(s, GOLD, (48, 48), 38, 4)


def sym_summon(s, acc):
    pygame.draw.circle(s, acc, (48, 48), 34, 4)
    for a in range(0, 360, 72):
        p = V(48, 48) + V(34, 0).rotate(a - 90)
        q = V(48, 48) + V(34, 0).rotate(a + 54)
        pygame.draw.line(s, acc, p, q, 3)
    pygame.draw.circle(s, W, (48, 48), 8)


def sym_bird(s, acc):
    _poly(s, (200, 160, 100), [(14, 40), (40, 46), (48, 30), (56, 46), (82, 40), (60, 58), (48, 74), (36, 58)])
    pygame.draw.circle(s, DARK, (48, 44), 3)


def sym_gem_beast(s, acc):
    pygame.draw.circle(s, (120, 230, 140), (48, 56), 24)
    pygame.draw.polygon(s, (120, 230, 140), [(30, 40), (26, 16), (42, 34)])
    pygame.draw.polygon(s, (120, 230, 140), [(66, 40), (70, 16), (54, 34)])
    _poly(s, RED, [(48, 34), (56, 44), (48, 54), (40, 44)])


def sym_flame_spirit(s, acc):
    sym_flame(s, acc)
    pygame.draw.circle(s, DARK, (42, 60), 4)
    pygame.draw.circle(s, DARK, (54, 60), 4)


def sym_tri(s, acc):
    for (x, y), col in zip(((48, 22), (26, 64), (70, 64)), ((240, 110, 40), (255, 235, 90), (150, 210, 255))):
        pygame.draw.circle(s, col, (x, y), 17)
        pygame.draw.circle(s, DARK, (x, y), 17, 3)


def sym_note(s, acc):
    pygame.draw.line(s, W, (40, 70), (40, 20), 6)
    pygame.draw.line(s, W, (68, 62), (68, 14), 6)
    pygame.draw.line(s, W, (40, 22), (68, 14), 8)
    pygame.draw.ellipse(s, W, (24, 62, 22, 16))
    pygame.draw.ellipse(s, W, (52, 54, 22, 16))


def sym_star(s, acc):
    pts = []
    for i in range(10):
        r = 38 if i % 2 == 0 else 16
        a = math.radians(i * 36 - 90)
        pts.append((48 + math.cos(a) * r, 50 + math.sin(a) * r))
    _poly(s, GOLD, pts)


def sym_star_up(s, acc):
    sym_star(s, acc)
    _up_arrow(s, (72, 72), (255, 120, 80))


def sym_boot(s, acc):
    _poly(s, (170, 120, 80), [(30, 16), (52, 16), (52, 56), (78, 64), (78, 80), (26, 80)])
    _poly(s, W, [(30, 26), (14, 18), (24, 34)])


def sym_feather(s, acc):
    _poly(s, (220, 240, 230), [(70, 12), (78, 26), (40, 76), (26, 80), (30, 66)])
    pygame.draw.line(s, DARK, (74, 18), (20, 86), 3)


def sym_magnet(s, acc):
    pygame.draw.arc(s, RED, pygame.Rect(20, 18, 56, 56), 0, math.pi, 16)
    pygame.draw.rect(s, RED, (20, 44, 16, 22))
    pygame.draw.rect(s, RED, (60, 44, 16, 22))
    pygame.draw.rect(s, STEEL, (20, 66, 16, 12))
    pygame.draw.rect(s, STEEL, (60, 66, 16, 12))


def sym_coins(s, acc):
    """Pilha de moedas de ouro (power-up de gold)."""
    for i, (cx, cy) in enumerate(((36, 66), (60, 60), (46, 44))):
        pygame.draw.ellipse(s, (150, 105, 20), (cx - 20, cy - 8, 40, 22))
        pygame.draw.ellipse(s, (250, 205, 60), (cx - 20, cy - 12, 40, 22))
        pygame.draw.ellipse(s, (255, 235, 140), (cx - 20, cy - 12, 40, 22), 3)
        pygame.draw.line(s, (200, 150, 30), (cx - 6, cy - 1), (cx + 6, cy - 1), 3)


# ---- símbolos adicionais (habilidades novas das classes) ----
def sym_trap(s, acc):
    pygame.draw.arc(s, STEEL, pygame.Rect(14, 30, 68, 60), math.pi * 0.05, math.pi * 0.95, 8)
    for i in range(6):
        x = 22 + i * 10
        pygame.draw.polygon(s, W, [(x, 52), (x + 5, 36), (x + 10, 52)])
    pygame.draw.rect(s, DARK, (16, 56, 64, 8))
    pygame.draw.rect(s, STEEL, (18, 58, 60, 4))


def sym_wolf(s, acc):
    head = [(22, 30), (32, 12), (42, 28), (54, 28), (64, 12), (74, 30), (76, 52), (48, 84), (20, 52)]
    _poly(s, (160, 160, 175), head)
    _poly(s, (220, 220, 230), [(40, 56), (56, 56), (48, 80)])
    pygame.draw.circle(s, GOLD, (36, 44), 5)
    pygame.draw.circle(s, GOLD, (60, 44), 5)
    pygame.draw.circle(s, DARK, (48, 76), 5)


def sym_clone(s, acc):
    for dx, col in ((-12, (70, 70, 110)), (12, (120, 120, 190))):
        pygame.draw.circle(s, col, (48 + dx, 30), 14)
        _poly(s, col, [(28 + dx, 84), (34 + dx, 48), (62 + dx, 48), (68 + dx, 84)])
        pygame.draw.line(s, W, (40 + dx, 30), (56 + dx, 30), 3)


def sym_meteor(s, acc):
    for i, w in enumerate((16, 12, 8)):
        pygame.draw.line(s, (255, 150 - i * 30, 60), (60 - i * 14, 36 - i * 14), (30 - i * 6, 6 + i * 2), w)
    pygame.draw.circle(s, (255, 170, 60), (60, 60), 24)
    pygame.draw.circle(s, (130, 90, 60), (60, 60), 18)
    pygame.draw.circle(s, DARK, (60, 60), 18, 3)
    pygame.draw.circle(s, (90, 60, 40), (54, 56), 4)


def sym_eye(s, acc):
    pygame.draw.ellipse(s, W, (12, 28, 72, 40))
    pygame.draw.ellipse(s, DARK, (12, 28, 72, 40), 4)
    pygame.draw.circle(s, acc if acc != (200, 200, 215) else (90, 160, 90), (48, 48), 15)
    pygame.draw.circle(s, DARK, (48, 48), 7)
    pygame.draw.circle(s, W, (52, 44), 3)


def sym_banner(s, acc):
    pygame.draw.line(s, WOOD, (28, 10), (28, 88), 7)
    pygame.draw.circle(s, GOLD, (28, 10), 6)
    _poly(s, (200, 60, 60) if acc == (200, 200, 215) else acc, [(32, 16), (80, 16), (70, 34), (80, 52), (32, 52)])
    _poly(s, GOLD, [(50, 24), (56, 34), (50, 44), (44, 34)])


def sym_skull(s, acc):
    pygame.draw.circle(s, W, (48, 42), 28)
    pygame.draw.rect(s, W, (34, 58, 28, 20), border_radius=4)
    pygame.draw.circle(s, DARK, (37, 44), 9)
    pygame.draw.circle(s, DARK, (59, 44), 9)
    pygame.draw.polygon(s, DARK, [(48, 52), (43, 62), (53, 62)])
    for x in (40, 48, 56):
        pygame.draw.line(s, DARK, (x, 68), (x, 78), 3)


def sym_rune(s, acc):
    col = acc if acc != (200, 200, 215) else (200, 140, 255)
    pygame.draw.circle(s, col, (48, 48), 36, 5)
    pygame.draw.circle(s, col, (48, 48), 26, 2)
    pygame.draw.line(s, W, (48, 24), (48, 72), 5)
    pygame.draw.line(s, W, (48, 34), (62, 46), 5)
    pygame.draw.line(s, W, (48, 50), (34, 62), 5)


def sym_sun(s, acc):
    col = (255, 220, 110)
    for a in range(0, 360, 30):
        p = V(48, 48) + V(24, 0).rotate(a)
        q = V(48, 48) + V(40, 0).rotate(a)
        pygame.draw.line(s, col, p, q, 6)
    pygame.draw.circle(s, col, (48, 48), 22)
    pygame.draw.circle(s, W, (48, 48), 13)


def sym_wave(s, acc):
    col = acc if acc != (200, 200, 215) else (130, 200, 255)
    for i, y in enumerate((30, 50, 70)):
        pts = [(12 + x, y + 9 * math.sin((x + i * 10) / 10)) for x in range(0, 73, 4)]
        pygame.draw.lines(s, col, False, pts, 8 - i * 2)
        pygame.draw.lines(s, W, False, pts, 2)


def sym_fan(s, acc):
    for a in (-36, -18, 0, 18, 36):
        d = V(0, -1).rotate(a)
        base = V(48, 82)
        tip = base + d * 66
        pygame.draw.line(s, WOOD, base, tip, 4)
        side = d.rotate(90) * 6
        pygame.draw.polygon(s, STEEL, [tip + d * 6, tip - d * 6 + side, tip - d * 6 - side])


def sym_fan_blades(s, acc):
    for a in (-30, 0, 30):
        blade = _rot([(45, 20), (51, 20), (51, 58), (48, 64), (45, 58)], a, 48, 80)
        _poly(s, STEEL, blade)
        pygame.draw.line(s, WOOD, *_rot([(48, 66), (48, 80)], a, 48, 80), 6)


def sym_crossed(s, acc):
    for ang in (40, -40):
        blade = _rot([(45, 12), (51, 12), (51, 60), (48, 66), (45, 60)], ang)
        _poly(s, STEEL, blade)
        pygame.draw.line(s, GOLD, *_rot([(36, 62), (60, 62)], ang), 6)
        pygame.draw.line(s, WOOD, *_rot([(48, 64), (48, 82)], ang), 6)


def sym_moon(s, acc):
    pygame.draw.circle(s, (240, 230, 160), (44, 50), 30)
    pygame.draw.circle(s, (60, 50, 80), (58, 40), 26)
    for (x, y) in ((70, 18), (80, 30), (64, 74)):
        pygame.draw.circle(s, W, (x, y), 3)


def sym_crack(s, acc):
    pygame.draw.rect(s, (150, 115, 75), (10, 52, 76, 30), border_radius=6)
    pts = [(48, 14), (40, 34), (54, 46), (42, 62), (52, 82)]
    pygame.draw.lines(s, DARK, False, pts, 7)
    pygame.draw.lines(s, (255, 200, 120), False, pts, 2)
    for x, y in ((24, 40), (72, 36), (20, 24), (78, 22)):
        pygame.draw.circle(s, (190, 150, 100), (x, y), 5)


def sym_vortex(s, acc):
    col = acc if acc != (200, 200, 215) else (150, 200, 255)
    pts = [(48 + math.cos(t / 6) * t * 0.9, 48 + math.sin(t / 6) * t * 0.9) for t in range(0, 42)]
    pygame.draw.lines(s, col, False, pts, 7)
    pygame.draw.lines(s, W, False, pts, 2)


def sym_wing(s, acc):
    col = (240, 240, 250) if acc == (200, 200, 215) else acc
    root = V(26, 74)
    for i, (ang, ln) in enumerate(((-80, 62), (-62, 66), (-44, 64), (-26, 58), (-8, 50))):
        d = V(1, 0).rotate(ang)
        side = d.rotate(90) * 8
        tip = root + d * ln
        feather = [root + side * 0.6, root + d * ln * 0.55 + side, tip, root + d * ln * 0.55 - side, root - side * 0.6]
        _poly(s, col, feather)
    pygame.draw.circle(s, col, root, 10)
    pygame.draw.circle(s, DARK, root, 10, 3)


def sym_harp(s, acc):
    pygame.draw.arc(s, GOLD, pygame.Rect(18, 10, 70, 90), math.pi * 0.5, math.pi * 1.1, 8)
    pygame.draw.line(s, GOLD, (24, 74), (76, 74), 8)
    pygame.draw.line(s, GOLD, (54, 12), (76, 74), 7)
    for x in (32, 42, 52, 62):
        pygame.draw.line(s, W, (x, 74), (x, 20 + (x - 32) * 0.3 + 10), 2)


def sym_cloudbolt(s, acc):
    _poly(s, (255, 235, 90), [(54, 40), (36, 66), (48, 66), (40, 90), (66, 58), (54, 58), (62, 40)])
    for x, y, r in ((30, 32, 16), (48, 24, 20), (66, 32, 16)):
        pygame.draw.circle(s, (170, 170, 190), (x, y), r)
    pygame.draw.rect(s, (170, 170, 190), (18, 32, 62, 14), border_radius=7)


def sym_slash_arc(s, acc):
    pygame.draw.arc(s, (200, 230, 255), pygame.Rect(10, 10, 76, 76), math.pi * 0.1, math.pi * 0.9, 6)
    pygame.draw.arc(s, W, pygame.Rect(18, 18, 60, 60), math.pi * 0.15, math.pi * 0.85, 3)
    blade = _rot([(45, 34), (51, 34), (51, 70), (48, 76), (45, 70)], 50)
    _poly(s, STEEL, blade)
    pygame.draw.line(s, GOLD, *_rot([(38, 72), (58, 72)], 50), 6)


def sym_orb(s, acc):
    col = acc if acc != (200, 200, 215) else (200, 140, 255)
    pygame.draw.circle(s, col, (48, 48), 30)
    pygame.draw.circle(s, W, (48, 48), 30, 4)
    pygame.draw.circle(s, W, (38, 38), 9)


# ---------------------------------------------------------------------------
# Itens da partida com tema de gatinho
# ---------------------------------------------------------------------------
PINK = (240, 150, 170)


def _ears(s, cx, cy, r, col, inner=PINK):
    for sx in (-1, 1):
        _poly(s, col, [(cx + sx * r * 0.95, cy - r * 0.35), (cx + sx * r * 0.75, cy - r * 1.35),
                       (cx + sx * r * 0.2, cy - r * 0.85)])
        _poly(s, inner, [(cx + sx * r * 0.8, cy - r * 0.55), (cx + sx * r * 0.7, cy - r * 1.1),
                         (cx + sx * r * 0.4, cy - r * 0.8)])


def sym_catnip(s, acc):
    """Raminho de erva-de-gato."""
    pygame.draw.line(s, (40, 90, 40), (48, 90), (48, 20), 7)
    for k, (y, sx) in enumerate(((22, -1), (36, 1), (50, -1), (64, 1))):
        tip = (48 + sx * 40, y - 6)
        _poly(s, (150, 235, 110) if k % 2 else (120, 215, 90), [(48, y + 10), tip, (48 + sx * 18, y + 18)])
        pygame.draw.line(s, (60, 140, 50), (48, y + 10), (48 + sx * 26, y + 2), 3)
    for k in range(3):
        pygame.draw.circle(s, (215, 180, 255), (40 + k * 8, 12 + (k % 2) * 4), 6)


def sym_paw(s, acc):
    """Patinha (com uma pena: velocidade)."""
    col = (250, 225, 210)
    pygame.draw.ellipse(s, PINK, (30, 46, 36, 30))
    for x, y in ((24, 36), (38, 24), (58, 24), (72, 36)):
        pygame.draw.ellipse(s, PINK, (x - 8, y - 9, 16, 18))
    pygame.draw.ellipse(s, col, (34, 50, 28, 22), 3)
    _poly(s, (220, 240, 255), [(78, 54), (90, 70), (70, 90), (64, 84)])
    pygame.draw.line(s, DARK, (88, 60), (62, 90), 2)


def sym_ninelives(s, acc):
    """Coração com orelhinhas de gato (+vida)."""
    col = (235, 75, 95)
    for sx in (-1, 1):
        _poly(s, col, [(48 + sx * 34, 40), (48 + sx * 30, 6), (48 + sx * 8, 28)])
        _poly(s, (255, 175, 190), [(48 + sx * 28, 32), (48 + sx * 27, 16), (48 + sx * 15, 28)])
    pygame.draw.circle(s, col, (32, 42), 20)
    pygame.draw.circle(s, col, (64, 42), 20)
    _poly(s, col, [(13, 48), (83, 48), (48, 90)])
    pygame.draw.rect(s, DARK, (30, 44, 8, 10))
    pygame.draw.rect(s, DARK, (58, 44, 8, 10))
    _poly(s, (255, 200, 210), [(42, 60), (54, 60), (48, 67)])


def sym_whiskers(s, acc):
    """Focinho com bigodes longos (alcance de coleta)."""
    pygame.draw.circle(s, (240, 230, 220), (48, 52), 20)
    _poly(s, PINK, [(42, 46), (54, 46), (48, 54)])
    for sy in (-6, 2, 10):
        pygame.draw.line(s, W, (36, 54 + sy // 2), (6, 46 + sy * 2), 3)
        pygame.draw.line(s, W, (60, 54 + sy // 2), (90, 46 + sy * 2), 3)
    for x in (10, 86):
        pygame.draw.circle(s, (250, 220, 120), (x, 20), 5, 2)


def sym_catnap(s, acc):
    """Gato enrolado dormindo + Zz (recarga)."""
    pygame.draw.ellipse(s, (210, 160, 110), (14, 44, 66, 38))
    pygame.draw.circle(s, (210, 160, 110), (66, 52), 15)
    _ears(s, 66, 52, 14, (210, 160, 110))
    pygame.draw.line(s, DARK, (60, 54), (65, 54), 2)
    pygame.draw.line(s, DARK, (69, 54), (74, 54), 2)
    pygame.draw.arc(s, (180, 130, 85), pygame.Rect(10, 56, 40, 30), math.pi * 0.6, math.pi * 1.6, 8)
    for k, (x, y, sz) in enumerate(((22, 32, 10), (34, 18, 14))):
        pygame.draw.lines(s, W, False, [(x, y), (x + sz, y), (x, y + sz), (x + sz, y + sz)], 4)


def sym_milk(s, acc):
    """Tigela de leite morno (regeneração)."""
    _poly(s, (90, 140, 210), [(12, 52), (84, 52), (72, 80), (24, 80)])
    pygame.draw.ellipse(s, (250, 250, 245), (14, 44, 68, 16))
    pygame.draw.ellipse(s, (90, 140, 210), (12, 42, 72, 20), 3)
    for x in (34, 50, 64):
        pygame.draw.arc(s, (230, 230, 240), pygame.Rect(x - 6, 14, 12, 24), -math.pi / 2, math.pi / 2, 3)


def sym_claws(s, acc):
    """Três arranhões longos (alcance)."""
    for k in range(3):
        x = 24 + k * 22
        _poly(s, W, [(x + 4, 6), (x + 16, 10), (x - 2, 90), (x - 12, 86)])
        _poly(s, (170, 185, 215), [(x + 8, 14), (x + 12, 16), (x - 4, 80)])


def sym_yarn(s, acc):
    """Novelo de lã (área)."""
    pygame.draw.circle(s, (240, 110, 140), (44, 48), 34)
    for k in range(4):
        pygame.draw.arc(s, (150, 40, 80), pygame.Rect(12 + k * 7, 14 + k * 5, 64 - k * 14, 68 - k * 10),
                        0.3 + k * 0.7, 2.4 + k * 0.7, 4)
    pygame.draw.lines(s, (240, 110, 140), False, [(72, 70), (84, 76), (74, 86), (92, 90)], 6)


def sym_fish(s, acc):
    """Peixe assado (cura)."""
    _poly(s, (150, 180, 210), [(14, 48), (40, 30), (66, 36), (78, 48), (66, 60), (40, 66)])
    _poly(s, (120, 150, 190), [(78, 48), (92, 34), (90, 62)])
    pygame.draw.circle(s, DARK, (28, 44), 4)
    for x in (44, 54, 64):
        pygame.draw.line(s, (90, 110, 150), (x, 38), (x - 4, 58), 2)


def sym_box(s, acc):
    """Caixa de papelão com orelhinhas espiando (invulnerável)."""
    _ears(s, 48, 46, 22, (60, 60, 70))
    pygame.draw.circle(s, (60, 60, 70), (48, 46), 16)
    pygame.draw.circle(s, (250, 220, 80), (42, 44), 3)
    pygame.draw.circle(s, (250, 220, 80), (54, 44), 3)
    pygame.draw.rect(s, (190, 140, 80), (14, 50, 68, 38))
    _poly(s, (215, 165, 100), [(14, 50), (4, 38), (30, 38), (40, 50)])
    _poly(s, (215, 165, 100), [(82, 50), (92, 38), (66, 38), (56, 50)])
    pygame.draw.line(s, (150, 105, 60), (48, 50), (48, 88), 3)


def sym_mystery_box(s, acc):
    """Caixa misteriosa (power-up aleatório)."""
    pygame.draw.rect(s, (190, 140, 80), (16, 36, 64, 50))
    _poly(s, (215, 165, 100), [(16, 36), (8, 22), (40, 22), (48, 36)])
    _poly(s, (215, 165, 100), [(80, 36), (88, 22), (56, 22), (48, 36)])
    pygame.draw.arc(s, (250, 230, 120), pygame.Rect(38, 46, 20, 18), -0.3, math.pi, 5)
    pygame.draw.line(s, (250, 230, 120), (56, 56), (48, 66), 5)
    pygame.draw.rect(s, (250, 230, 120), (45, 72, 6, 6))


def sym_tuna(s, acc):
    """Lata de atum (cura)."""
    pygame.draw.ellipse(s, (180, 185, 200), (12, 56, 72, 24))
    pygame.draw.rect(s, (180, 185, 200), (12, 40, 72, 28))
    pygame.draw.rect(s, (60, 120, 200), (12, 46, 72, 14))
    pygame.draw.ellipse(s, (215, 220, 230), (12, 30, 72, 22))
    _poly(s, (250, 160, 130), [(30, 50), (48, 44), (64, 50), (48, 56)])
    pygame.draw.circle(s, (120, 120, 130), (70, 38), 5, 2)


def sym_laser(s, acc):
    """Ponteiro laser e o pontinho vermelho (crítico)."""
    _poly(s, (190, 190, 205), [(6, 78), (28, 56), (40, 68), (18, 90)])
    pygame.draw.rect(s, (90, 90, 105), (24, 62, 6, 6))
    pygame.draw.line(s, (255, 70, 70), (34, 62), (70, 26), 6)
    pygame.draw.circle(s, (255, 60, 60), (72, 24), 17)
    pygame.draw.circle(s, (255, 210, 210), (72, 24), 7)


def sym_feather_wand(s, acc):
    """Varinha com penas (recarga)."""
    pygame.draw.line(s, (200, 150, 90), (12, 90), (50, 44), 7)
    for k, col in enumerate(((120, 210, 255), (255, 150, 190), (255, 225, 90))):
        a = -0.9 + k * 0.55
        tip = (50 + math.cos(a) * 44, 44 + math.sin(a) * 44)
        nrm = (-math.sin(a) * 9, math.cos(a) * 9)
        _poly(s, col, [(50, 44), (tip[0] + nrm[0] * 0.3, tip[1] + nrm[1] * 0.3),
                       ((50 + tip[0]) / 2 + nrm[0], (44 + tip[1]) / 2 + nrm[1])])
        _poly(s, col, [(50, 44), (tip[0] - nrm[0] * 0.3, tip[1] - nrm[1] * 0.3),
                       ((50 + tip[0]) / 2 - nrm[0], (44 + tip[1]) / 2 - nrm[1])])


def sym_hiss(s, acc):
    """Gato bravo, pelo arrepiado (atordoa a tela)."""
    fur = (175, 175, 190)
    for k in range(9):
        a = math.pi * (1.05 + k * 0.11)
        pygame.draw.line(s, fur, (48, 58), (48 + math.cos(a) * 42, 58 + math.sin(a) * 42), 7)
    pygame.draw.circle(s, fur, (48, 58), 26)
    for sx in (-1, 1):
        _poly(s, fur, [(48 + sx * 26, 50), (48 + sx * 24, 16), (48 + sx * 6, 36)])
    pygame.draw.line(s, (250, 220, 60), (32, 48), (44, 54), 6)
    pygame.draw.line(s, (250, 220, 60), (64, 48), (52, 54), 6)
    _poly(s, (200, 50, 70), [(36, 64), (60, 64), (48, 82)])
    _poly(s, W, [(38, 64), (43, 64), (41, 72)])
    _poly(s, W, [(53, 64), (58, 64), (55, 72)])


def sym_treats(s, acc):
    """Saco de petiscos (puxa as gemas)."""
    _poly(s, (200, 90, 80), [(22, 30), (74, 30), (82, 86), (14, 86)])
    pygame.draw.rect(s, (230, 120, 100), (20, 22, 56, 12))
    pygame.draw.circle(s, (250, 230, 200), (48, 58), 14)
    _poly(s, (200, 90, 80), [(40, 60), (56, 60), (48, 50)])
    for x, y in ((28, 14), (48, 8), (66, 14)):
        pygame.draw.circle(s, (170, 110, 60), (x, y), 5)


def sym_zoomies(s, acc):
    """Gatinho em disparada (dano)."""
    pygame.draw.ellipse(s, (240, 150, 70), (34, 40, 46, 26))
    pygame.draw.circle(s, (240, 150, 70), (76, 42), 13)
    _ears(s, 76, 42, 12, (240, 150, 70))
    pygame.draw.circle(s, DARK, (80, 40), 2)
    for k in range(3):
        pygame.draw.line(s, W, (8, 40 + k * 10), (28, 40 + k * 10), 3)
    for x in (40, 70):
        pygame.draw.line(s, (240, 150, 70), (x, 62), (x - 8, 76), 5)


SYMBOLS = {k[4:]: v for k, v in globals().items() if k.startswith("sym_")}


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
def _accent(spec):
    el = spec.get("element") or (spec.get("cycle") or [None])[0]
    return ELEMENTS[el]["color"] if el in ELEMENTS else (200, 200, 215)


def _render(symbol, bg, acc, size):
    key = (symbol, bg, acc, size)
    surf = _CACHE.get(key)
    if surf is not None:
        return surf
    base = pygame.Surface((BASE, BASE), pygame.SRCALPHA)   # só o símbolo (a moldura é feita em pixel art)
    main, _, badge = symbol.partition("+")
    SYMBOLS.get(main, sym_burst)(base, acc)
    if badge:   # selo pequeno no canto inferior direito
        b = pygame.Surface((BASE, BASE), pygame.SRCALPHA)
        SYMBOLS.get(badge, sym_burst)(b, acc)
        b = pygame.transform.smoothscale(b, (44, 44))
        pygame.draw.circle(base, DARK, (70, 70), 25)
        pygame.draw.circle(base, tuple(min(255, c + 60) for c in bg), (70, 70), 25, 3)
        base.blit(b, (48, 48))
    surf = pixel.pixel_icon(base, bg, size)   # pixel art: grade pequena, poucas cores, contorno e moldura
    if len(_CACHE) > 2000:
        _CACHE.clear()
    _CACHE[key] = surf
    return surf


def active_icon(spec, size=40):
    """Ícone de uma habilidade ativa (ou golpe básico)."""
    acc = _accent(spec)
    bg = tuple(int(c * 0.35) + 18 for c in acc)
    symbol = _symbol_for(spec.get("name"), spec.get("kind"), spec.get("element"), spec.get("cycle"))
    return _render(symbol, bg, acc, size)


TAG_SYMBOL = {"melee": "sword", "ranged": "bow", "projectile": "arrow", "aoe": "burst", "single": "dagger",
              "summon": "summon", "heal": "heal", "buff": "up", "physical": "fist", "magical": "orb",
              "bleed": "drop", "dot": "poison", "stun": "bolt", "slow": "clock", "knockback": "tornado", "pull": "gravity",
              "piercing": "spear", "homing": "missile"}
STAT_PCT_SYMBOL = {"str_pct": ("fist", (150, 70, 50)), "agi_pct": ("feather", (60, 130, 70)),
                   "int_pct": ("book", (70, 70, 160)), "vit_pct": ("heart", (150, 50, 70)),
                   "armor_pct": ("shield", (100, 100, 115)), "mres_pct": ("shield_orb", (80, 70, 150)),
                   "dot_dmg": ("poison", (70, 120, 60)), "buffdur": ("clock", (130, 100, 40))}


def passive_icon(p, size=40):
    """Ícone de uma passiva (pelo tipo de efeito; capstones têm moldura dourada e estrela)."""
    eff = p.get("effects") or {p.get("effect"): p.get("value")}
    key = next(iter(eff), "") or ""
    if p.get("capstone"):
        cap = next((k for k in eff if k.startswith("cap:")), key)
        sym = {"cap:execute": "skull", "cap:detonate": "burst", "cap:vampiric": "heart_plus", "cap:frenzy": "warcry",
               "cap:ambush": "eye", "cap:echo": "hourglass", "cap:sanctuary": "holy", "cap:legion": "summon",
               "cap:elemental": "tri", "cap:thorns": "shield", "cap:anthem": "banner", "cap:bulwark": "shield_orb"}
        return _render(sym.get(cap, "star") + "+star", (120, 90, 20), (250, 210, 70), size)
    kind, _, arg = key.partition(":")
    if kind in ("tagdmg", "tagcrit", "taghaste"):
        base = ELEMENT_SYMBOL.get(arg) or TAG_SYMBOL.get(arg, "burst")
        badge = {"tagdmg": "up", "tagcrit": "star", "taghaste": "hourglass"}[kind]
        bg = (ELEMENTS[arg]["color"] if arg in ELEMENTS else (150, 110, 80))
        bg = tuple(int(c * 0.35) + 20 for c in bg)
        return _render(f"{base}+{badge}", bg, (220, 220, 230), size)
    if kind in ("dmgvs", "critvs"):
        return _render("skull+" + ("star" if kind == "critvs" else "up"), (90, 40, 60), (220, 220, 230), size)
    if key in STAT_PCT_SYMBOL:
        sym, bg = STAT_PCT_SYMBOL[key]
        return _render(sym + "+up", bg, (200, 200, 215), size)
    symbol, bg = PASSIVE_SYMBOL.get(key, ("up", (80, 80, 100)))
    return _render(symbol, bg, (200, 200, 215), size)


def icon_for(spec, kind, size=40):
    return passive_icon(spec, size) if kind == "passive" else active_icon(spec, size)


# itens da partida (level up) -> símbolo
ITEM_SYMBOL = {"Feather Paws": ("paw", (60, 120, 90)), "Ninth Life": ("ninelives", (150, 50, 70)),
               "Long Whiskers": ("whiskers", (130, 60, 60)), "Catnip": ("catnip", (70, 130, 60)),
               "Cat Nap": ("catnap", (70, 90, 150)), "Warm Milk": ("milk", (150, 120, 30)),
               "Fish Feast": ("fish", (150, 90, 50)), "Sharp Claws": ("claws", (70, 110, 150)),
               "Ball of Yarn": ("yarn", (110, 70, 150)), "Mystery Box": ("mystery_box", (130, 100, 30))}


def item_icon(name, size=40):
    symbol, bg = ITEM_SYMBOL.get(name, ("up", (80, 80, 100)))
    return _render(symbol, bg, (200, 200, 215), size)


# ---------------------------------------------------------------------------
# Ícones das classes (emblema da classe sobre a cor dela)
# ---------------------------------------------------------------------------
CLASS_EMBLEM = {
    "freelancer": "sword", "archer": "bow", "thaumaturge": "flame", "arcanist": "book", "pugilist": "fist",
    "lancer": "spear", "rogue": "dagger", "conjurer": "tri", "gladiator": "shield+sword", "marauder": "axe",
    "bard": "harp", "hunter": "wolf", "black_mage": "meteor", "time_mage": "hourglass", "summoner": "summon",
    "scholar": "rune", "monk": "fist+star", "white_monk": "fist+holy", "dragoon": "jump", "templar": "banner",
    "ninja": "shuriken", "assassin": "dagger+poison", "white_mage": "holy", "bishop": "wave",
    "paladin": "shield+holy", "spellblade": "sword+flame", "warrior": "axe+shield", "berserker": "warcry",
    "freelancer_t2": "crossed", "warfarer": "crossed+star",
}


def class_icon(cid, size=40):
    """Ícone quadrado da classe (usado no medidor de dano e onde couber)."""
    from data import CLASSES
    col = CLASSES.get(cid, {}).get("color", (180, 180, 190))
    bg = tuple(int(c * 0.3) + 10 for c in col)
    return _render(CLASS_EMBLEM.get(cid, "burst"), bg, col, size)


def game_icon(size=64):
    """Ícone do jogo (janela e executável): espadas cruzadas sobre fundo dourado."""
    return _render("crossed", (120, 80, 20), (245, 205, 80), size)


def gear_icon(cid, slot, size=56):
    """Ícone da arma (símbolo da arma da classe) ou do capacete (chapéu da classe) de uma classe."""
    from data import CLASSES
    col = CLASSES[cid]["color"]
    bg = tuple(int(c * 0.3) + 12 for c in col)
    if slot == "weapon":
        w = CLASSES[cid]["weapon"].lower()
        sym = next((s for keys, s in WEAPON_KEYWORDS if any(k in w for k in keys)), "sword")
        return _render(sym, bg, col, size)
    key = ("helmet", cid, size)
    surf = _CACHE.get(key)
    if surf is None:
        from icons import draw_class_hat
        base = pygame.Surface((BASE, BASE), pygame.SRCALPHA)
        draw_class_hat(base, cid, (48, 66), 28)
        surf = _CACHE[key] = pixel.pixel_icon(base, bg, size)
    return surf
