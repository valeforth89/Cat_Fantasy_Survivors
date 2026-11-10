"""Conteúdo da Wiki, aba Guia (antigo FAQ; botão Wiki do menu principal e do acampamento).

A cada build nova, adicione um item no topo de "Patch notes" (EN e PT). Mantenha os números aqui em sincronia com data.py / run.py / roster.py / elites.py / powerups.py quando as regras
mudarem. Nas respostas, "\\n" quebra a linha e linhas começando com "• " viram itens de lista.
"""

FAQ = [
    ("Getting started", [
        ("What is Cat Fantasy Survivors?",
         "A survivor-style action game: you move the hero and every skill fires on its own.\n"
         "Survive the horde for 10 minutes, defeat the stage boss and use what you earn to grow your roster.\n"
         "A run is played by a party of up to 5 members."),
        ("How do saves work?",
         "There are 3 save slots (the save you already had is Save 1). In the main menu:\n"
         "• Continue: goes back to the last save you used.\n"
         "• New Save: creates a save from zero in a slot (a slot that already has progress asks you to click "
         "again before erasing it).\n"
         "• Load Save: shows the 3 slots as cards with a summary: the hero (with the current class, name and "
         "level), the completion % and how many stages, accessories, trophies and classes at Lv 100 you have, plus "
         "the highest Endless Rift level.\n"
         "The game saves on its own (on the PC: save.json, save2.json and save3.json next to the game; in the "
         "browser version: in the browser)."),
        ("What is the camp?",
         "Continue in the main menu takes you to the camp, the central hub of the game. Walk with WASD and walk into "
         "a place (or click it, or press E / ENTER next to it) to open it:\n"
         "• Portal (north of the campfire): stage select; press Start run there.\n"
         "• Tent: Party Setup (recruit, activate members, change class and loadout).\n"
         "• Training Room (straw dummies, southeast): test formations, builds and your DPS / HPS.\n"
         "These three are there from the start. The others appear as you progress (a NEW! tag marks them until "
         "you use them):\n"
         "• Chest (next to the portal): inventory with your fragments and gold · after your first fragment.\n"
         "• Blacksmith (next to the forge): upgrade the weapon and helmet of each class · after clearing Forest "
         "III.\n"
         "• Jeweler: accessories · after your first accessory.\n"
         "• Altar of Trophies (west of the portal): activate the trophies dropped by the bosses · after your "
         "first trophy.\n"
         "• Altar of Mastery (west of the camp): offer class fragments to raise class max levels · after you "
         "master a class.\n"
         "• Red Portal (east of the chest): the dungeons · after clearing Forest V.\n"
         "Each place explains itself the first time you use it; the \"?\" button in its screen shows the "
         "explanation again.\n"
         "The active members rest around the campfire. ESC goes back to the main menu; after a run you return to "
         "the camp."),
        ("How do I play a run?",
         "• Move with WASD or the arrow keys; skills attack automatically. SPACE dodges.\n"
         "• Enemies drop EXP gems: collect them to level up during the run and pick an upgrade (keys 1-3 or click).\n"
         "• ESC pauses. In the pause screen, Q ends the run and the party still keeps the EXP."),
        ("How does the dodge work?",
         "Press SPACE to dodge in the direction the hero is facing. Only the hero dodges, and the type depends on "
         "the main attribute of the current class:\n"
         "• STR - Charge: rushes a medium distance and pushes away (and stuns briefly) every enemy it touches. "
         "Medium cooldown (6 s), 2 uses.\n"
         "• AGI - Dodge: a fast, longer dash that passes through enemies without taking damage. Short cooldown "
         "(2.2 s), 1 use.\n"
         "• INT - Blink: teleports far ahead; where the hero appears, an impact pushes nearby enemies away in 360°. "
         "Long cooldown (9 s), 1 use.\n"
         "• Cooldown reduction (INT, passives, items and attack speed buffs) also shortens the dodge cooldown.\n"
         "• Balanced classes (Novice, Freelancer, Warfarer) use Dodge.\n"
         "The icon next to the hotkeys shows the cooldown and the remaining uses."),
        ("Who do I control?",
         "Only the hero (yellow outline).\n"
         "The other party members act on their own: they follow the hero, fight and upgrade their skills "
         "automatically every time the run level goes up."),
        ("How does a run end?",
         "• The hero falls (allies can fall and come back, the hero cannot).\n"
         "• You quit from the pause screen.\n"
         "• The stage boss is defeated (stage clear)."),
    ]),
    ("Attributes & stats", [
        ("What do STR, AGI, INT and VIT do?",
         "Per point:\n"
         "• STR: +0.1 armor and +0.2% critical damage.\n"
         "• AGI: +0.1% dodge and +0.1% critical chance.\n"
         "• INT: +0.1 magic defense and +0.1% cooldown reduction.\n"
         "• VIT: +5 max HP and +0.1 HP regeneration every 5 s.\n"
         "Character damage = 10 + the main attribute of your current class (STR, AGI or INT; Novice, Freelancer "
         "and Warfarer use the average of the three), times the Attack of the class role (Tank x0.5, Caster x1.4...). "
         "Every attack deals a % of it. Healing still grows with the "
         "INT of the healing skill's class."),
        ("Where do attributes come from?",
         "• Every character starts with 5 in each attribute.\n"
         "• Each character level adds +1 to STR, AGI, INT and VIT.\n"
         "• Class levels add permanent bonuses (see Classes). Up to Lv 100 a class gives 18 points of its main "
         "attribute and 5 of each of the other two.\n"
         "• Extra class levels from the Altar of Mastery add +1 of the class main attribute each.\n"
         "• Some passives, +10 equipment and accessories add attribute points directly."),
        ("What are armor, magic defense and dodge?",
         "• Armor is subtracted from every physical hit you take.\n"
         "• Magic defense is subtracted from every magical hit (minimum 1 damage).\n"
         "• Dodge is the chance to completely ignore a physical hit (max 75%, with diminishing returns)."),
        ("What are diminishing returns (softcaps)?",
         "Critical chance, dodge and cooldown get harder to raise as they grow. Each one has 2 softcaps, at 1/3 "
         "and 2/3 of its maximum:\n"
         "• Up to the 1st softcap every bonus counts in full.\n"
         "• Between the 1st and the 2nd softcap a bonus counts half.\n"
         "• Above the 2nd softcap a bonus counts only 1/5.\n"
         "Critical chance: softcaps at 33% and 67% (max 100%). Dodge: 25% and 50% (max 75%). Cooldown: 20% and "
         "40% (max 60%).\n"
         "Critical damage has no softcap. The status details show your raw total next to the effective value."),
        ("What is Defense (%)?",
         "A percentage reduction of all damage taken, applied after armor or magic defense.\n"
         "It comes from the class (e.g. Gladiator 15%), passives and buffs such as Shield Wall. Capped at 75%."),
        ("How do critical hits work?",
         "Every hit rolls your critical chance (max 100%, with diminishing returns).\n"
         "A critical deals +50% damage plus your extra critical damage (from STR, class levels and passives).\n"
         "Critical hits show as yellow numbers with '!'."),
        ("What is Cooldown (%)?",
         "Cooldown reduction: every skill recharges that much faster (max 60%, with diminishing returns).\n"
         "It stacks with the run item Cat Nap and with haste buffs."),
        ("How does HP regeneration work?",
         "Regeneration is shown as HP every 5 seconds and is applied continuously.\n"
         "It comes from VIT, class levels, passives and the Warm Milk item."),
    ]),
    ("Damage & statuses", [
        ("How is skill damage calculated?",
         "1. Character damage (10 + main attribute of the current class) x the skill's damage % (basic attack: "
         "100% per second of cooldown).\n"
         "2. x skill run level bonus (+25% per level).\n"
         "3. x damage bonuses (Physical or Magic damage %, All damage %, tag bonuses, equipment, accessories, "
         "Catnip, buffs).\n"
         "4. Critical roll.\n"
         "5. The enemy's armor or magic defense is subtracted (minimum 1)."),
        ("Physical or magical?",
         "• Physical damage is reduced by armor.\n"
         "• Magical damage is reduced by magic defense.\n"
         "• Any elemental hit counts as magical.\n"
         "STR/AGI classes mostly deal physical damage, INT classes mostly magical."),
        ("What statuses can a hit cause?",
         "Every hit has a chance to cause a status, decided by the skill's element. Physical hits without an element "
         "use the kind of blow (Slash, Piercing or Blunt).\n"
         "• Fire: 35% Burning (30% of the hit per second for 3 s).\n"
         "• Poison: 50% Poisoned (40% of the hit per second for 4 s).\n"
         "• Ice: 40% Chilled (50% slower for 2 s).\n"
         "• Water: 30% Slowed (25% slower for 1.5 s) and always pushes back.\n"
         "• Wind: no status, but always pushes enemies back hard.\n"
         "• Lightning: 25% Stunned (0.25 s).\n"
         "• Earth: 25% Stunned / knocked down (0.4 s).\n"
         "• Holy: 15% Stunned (0.3 s).\n"
         "• Sound: 20% Stunned (0.2 s).\n"
         "• Arcane: 20% Slowed (30% slower for 1.5 s).\n"
         "• Gravity: 30% Slowed (40% slower for 2 s).\n"
         "• Time: 30% Slowed (50% slower for 2 s).\n"
         "• Smoke: 25% Slowed (30% slower for 2 s).\n"
         "• Slash (swords, axes, claws): 30% Bleeding (25% of the hit per second for 3 s).\n"
         "• Piercing (spears, arrows, daggers): 30% Bleeding.\n"
         "• Blunt (fists, kicks, shields, slams): 20% Stunned (0.3 s).\n"
         "Skills that list their own slow, stun or pull always apply it. Big enemies are stunned for less time. "
         "The skill tooltip shows the status chance of each skill."),
        ("Which statuses do passives check?",
         "• Burning, Poisoned, Bleeding, Chilled, Stunned and Slowed.\n"
         "• 'Any debuff' counts all of them.\n"
         "• 'Elemental status' counts Burning, Chilled, Poisoned and Stunned."),
        ("How does healing work?",
         "Heal skills restore (base amount + points in the skill's class attribute) x skill run level bonus x "
         "Healing %.\n"
         "They target allies in range that are missing HP; healing above max HP is wasted."),
        ("What is the damage meter?",
         "The panel in the bottom-right corner (like WoW's Recount). Click a tab or press TAB.\n"
         "• Damage, Taken and Healing: hover a member to see the breakdown per skill (or per enemy for damage "
         "taken).\n"
         "• CC: crowd control each member applied (Stun, Freeze, Knockdown, Slow, Chill, Knockback, Pull), in "
         "seconds, and which skills caused it.\n"
         "Only effective numbers are counted: no overkill and no overhealing."),
    ]),
    ("Skills & loadout", [
        ("How many skills can a character use?",
         "7 active slots:\n"
         "• Slot 1: the fixed weapon Basic Attack.\n"
         "• Slots 2-5: actives of the current class.\n"
         "• Slots 6-7: mastery slots.\n"
         "10 passive slots:\n"
         "• Slots 1-4: passives of the current class; slot 5: its Capstone.\n"
         "• Slots 6-9: mastery slots; slot 10: the Capstone of another mastered class."),
        ("What are mastery slots?",
         "When a class reaches its mastery level (Lv 50, Novice Lv 25), all its skills become available in the "
         "mastery slots of any other class of that character. This is the core of building hybrids.\n"
         "A mastered class shows a star next to its level.\n"
         "The list of a mastery slot has two dropdown menus, Class and Tag:\n"
         "• Click them or press C / T to open.\n"
         "• Type a letter to jump to an item.\n"
         "• Right-click a filter to clear it."),
        ("How do skills unlock?",
         "Each class has 10 actives and 10 passives unlocked by class level:\n"
         "• Actives: Lv 1, 5, 10 ... 45.\n"
         "• Passives: Lv 3, 8, 13 ... 48.\n"
         "• Novice unlocks everything by Lv 25.\n"
         "See the Progression button in the class screen."),
        ("Is the loadout saved?",
         "Yes, per character and per class. Switching classes loads that class's loadout.\n"
         "New skills fill empty slots automatically; slots you clear on purpose stay empty.\n"
         "The first time you switch to a class, the game asks whether to copy the mastery slots of your current "
         "class to it (skills that don't fit are skipped)."),
        ("How do skills improve during a run?",
         "Each run level-up lets the hero raise one skill or passive (max Lv 5).\n"
         "Active skills, per level:\n"
         "• +25% damage or healing, -6% cooldown and +8% area.\n"
         "• Lv 3 and Lv 5: +1 projectile / strike / orb.\n"
         "• Lv 4: +1 pierce on projectiles and +1 summon.\n"
         "Passives: each level adds 50% of the original value (a 6% passive becomes 9%, 12%, 15% and 18%).\n"
         "Allies upgrade a random skill or passive every level.\n"
         "Random level-ups: on the level-up screen, tick the box (or press A) and pick a card; from then on every "
         "level-up of that run is picked at random for you. It does not affect the Fish Feast / +1 Gold / "
         "Mystery Box choice (that one has its own box). In the pause screen, A turns it off."),
        ("What are the run items?",
         "Level-up cards can also offer items for the hero (max Lv 5 each, they only last for the run):\n"
         "• Feather Paws: +10% speed.\n"
         "• Ninth Life: +20 HP.\n"
         "• Long Whiskers: +30% pickup range.\n"
         "• Catnip: +12% damage.\n"
         "• Cat Nap: -8% cooldown.\n"
         "• Warm Milk: +2.5 HP/5s.\n"
         "• Sharp Claws: +10% range.\n"
         "• Ball of Yarn: +10% area."),
        ("What do Range and Area do?",
         "• Range: melee attacks reach farther (arc and cone radius, thrust length) and projectiles fly farther "
         "before disappearing.\n"
         "• Area: wider and bigger attacks: thrust width, arc and cone angle, projectile size, and the size of "
         "impacts, auras, explosions and lingering areas.\n"
         "Both come from the run items Sharp Claws and Ball of Yarn and from some class passives (Far Reach: "
         "Archer, Lancer; Expansion: Thaumaturge, Black Mage, Bishop, Marauder, Dragoon)."),
        ("What happens when everything is upgraded?",
         "When the hero has no skill, passive or item left to upgrade, each level-up offers:\n"
         "• Fish Feast: restores 30 HP.\n"
         "• +1 Gold: added to your gold right away.\n"
         "• Mystery Box: a random power-up is activated right away.\n"
         "Tick the box (or press A) and the next card you pick becomes automatic for every next level-up of that "
         "run. It must be ticked again in the next run; in the pause screen, A turns it off."),
        ("What are the skill archetypes?",
         "• Projectile, Arc strike, Thrust, Area impact, Cone.\n"
         "• Aura: constant damage around you.\n"
         "• Orbit: orbs spinning around you.\n"
         "• Heal, Buff (party or self bonuses), Summon (temporary allies).\n"
         "• Lingering area: ground damage over time.\n"
         "Hover any skill icon to see its exact numbers."),
    ]),
    ("Classes", [
        ("What is the Altar of Mastery?",
         "The crystal altar at the west of the camp. Offer Fragments of a class to raise that class's max level by "
         "1 for EVERY character (e.g. White Mage +1: the White Mage max level becomes 101 for everyone).\n"
         "• Cost in fragments of that class: 1, 2, 4, 8, 16, 32... (doubles each level).\n"
         "• Extra levels give +1 of the class main attribute (STR, AGI or INT) and +5 HP each, instead of the "
         "normal level bonuses. Balanced classes (Novice, Freelancer, Warfarer) alternate STR, AGI and INT.\n"
         "• Like other class levels, these bonuses are permanent and count in every class.\n"
         "• The altar level is the sum of every level offered. Each altar level gives +2.5% fragments: every "
         "fragment you pick up is worth 1 + 2.5% per level, so fragments now have decimals (e.g. 1.025)."),
        ("How does the class tree work?",
         "• Everyone starts as Novice.\n"
         "• Novice Lv 10 unlocks the 9 basic classes.\n"
         "• Each basic class at Lv 25 unlocks its two advanced classes (e.g. Archer -> Bard or Hunter; you can "
         "train both).\n"
         "The 'Highlight tag' dropdown at the top (or T) highlights the classes that have skills with that tag, and "
         "the matching skills in the class details."),
        ("What are Freelancer and Warfarer?",
         "Evolutions of the Novice:\n"
         "• Freelancer (max Lv 100): needs all 9 basic classes mastered. Its class slots also accept actives and "
         "passives of mastered basic classes.\n"
         "• Warfarer (max Lv 100): needs all 18 advanced classes mastered. Its slots accept skills of any mastered "
         "class.\n"
         "The capstone rule still applies: own capstone in slot 5, another class's capstone in slot 10."),
        ("How do class levels work?",
         "Every class levels up to Lv 100 (Novice and Freelancer included); the Altar of Mastery can raise this "
         "limit. Mastery stays at Lv 50 (Novice Lv 25).\n"
         "The run EXP goes to the character's general level and to the current class level.\n"
         "Levels that do not unlock a skill give permanent stat bonuses focused on the class's core attribute, "
         "plus VIT/HP or regeneration every few levels."),
        ("Are class bonuses permanent?",
         "Yes. The stat bonuses of every class level a character has reached apply no matter which class they are "
         "using. Training several classes makes a character stronger overall."),
        ("What does each class change besides skills?",
         "• Main attribute: STR, AGI or INT (Novice, Freelancer and Warfarer are balanced).\n"
         "• Weapon and basic attack.\n"
         "• Role (Tank, Caster...): base HP, Defense, Attack and Speed, the skill style and how it behaves as "
         "an ally.\n"
         "• Melee or ranged.\n"
         "You can see them in the class screen."),
        ("What are roles?",
         "Every class has a role that sets its base scaling, what its skills focus on and how it moves as an AI "
         "ally:\n"
         "• All-Rounder (HP x1, Def x1, Atk x1, Spd x1): melee skills split between single target and area, plus a "
         "defensive or support skill. Charges nearby enemies without straying far from the party.\n"
         "• Ranged Assassin (HP x0.8, Def x0.8, Atk x1.3, Spd x1.1): ranged, mostly single target. Keeps its "
         "distance.\n"
         "• Caster (HP x0.8, Def x0.8, Atk x1.4, Spd x1): mostly area spells. Keeps its distance.\n"
         "• Melee Assassin (HP x0.7, Def x0.7, Atk x1.4, Spd x1.2): single-target melee and crowd control. Chases "
         "targets further away.\n"
         "• Support (HP x1.1, Def x1.1, Atk x0.8, Spd x1): party buffs, enemy debuffs (Weaken, slow, stun) and some "
         "healing. Stays close to the party.\n"
         "• Healer (HP x1, Def x1.1, Atk x0.8, Spd x1.1): heals and protection. Stays close, a bit behind.\n"
         "• Tank (HP x1.3, Def x1.3, Atk x0.5, Spd x0.9): area, defense and some support, with an area Taunt. "
         "Protects the other members and draws the enemies' attention.\n"
         "Defense multiplies armor and magic defense and changes the damage reduction by 5% per 0.1 (Tank: 15% "
         "less damage taken; Melee Assassin: 15% more). Attack multiplies the character damage."),
        ("What do Taunt and Weaken do?",
         "• Taunt: enemies hit attack the character who taunted them for a few seconds (bosses: half the time). "
         "Every tank has at least one area Taunt.\n"
         "• Weaken: enemies hit take more damage from everyone for 4 seconds (e.g. +20%).\n"
         "Both show in the CC meter."),
    ]),
    ("Tags & passives", [
        ("What are skill tags?",
         "Every active skill has tags based on what it does and on its theme:\n"
         "• Range: Melee, Ranged.\n"
         "• Form: Projectile, AoE, Single target, Summon, Heal, Buff.\n"
         "• Damage type: Physical, Magical.\n"
         "• Element: Fire, Ice, Lightning, Water, Wind, Earth, Poison, Holy, Arcane, Sound, Gravity, Time, Smoke.\n"
         "• Kind of blow: Slash, Piercing, Blunt.\n"
         "• Effects: Bleed, Damage over time, Stun, Slow, Knockback, Pull, Homing.\n"
         "Tags are shown in every skill tooltip, and the class screen lists the tags of each class."),
        ("How do passives use tags?",
         "• +% damage for skills with a tag (e.g. Fire skills).\n"
         "• +% critical chance for a tag (e.g. Projectile skills).\n"
         "• -% cooldown for a tag (e.g. Melee skills).\n"
         "• Damage and critical chance against enemies with a status (e.g. Bleeding).\n"
         "Others raise STR/AGI/INT/VIT by %, armor, magic defense or dodge."),
        ("What is a Capstone?",
         "The 10th passive of each class (unlocked at Lv 48, Novice Lv 25): a stronger passive with a special "
         "mechanic. Examples:\n"
         "• Execute: bonus damage below 30% HP.\n"
         "• Detonate: enemies explode on death.\n"
         "• Vampiric: crits heal.\n"
         "• Frenzy: kills stack damage.\n"
         "• Echo: skills may recharge instantly.\n"
         "• Legion: stronger summons.\n"
         "• Anthem: party damage. Also Thorns, Bulwark and more.\n"
         "Only one own capstone (slot 5) and one capstone of another mastered class (slot 10) can be equipped."),
    ]),
    ("Builds", [
        ("What builds are possible?",
         "Mix a class with the mastered skills of others. Examples:\n"
         "• A Gladiator tank using a mastered White Mage's heals.\n"
         "• A Black Mage with Time Mage's Haste for constant spell spam.\n"
         "• An Assassin with Rogue's stuns and Hunter's traps.\n"
         "• A Berserker stacking damage passives from Marauder and Warrior."),
        ("Which attribute should I focus on?",
         "The main attribute of your current class: all your damage scales with it, even skills borrowed from "
         "other classes.\n"
         "• STR also gives armor and crit damage.\n"
         "• AGI gives dodge and crit chance.\n"
         "• INT gives magic defense and cooldown.\n"
         "• VIT is good for everyone."),
        ("How should I build a party?",
         "A classic party of 5 has:\n"
         "• A front-liner (Gladiator, Paladin, Warrior).\n"
         "• A healer or support (Conjurer, White Mage, Scholar, Bard).\n"
         "• Damage dealers.\n"
         "Allies use whatever is equipped in their loadout."),
    ]),
    ("Enemies & spawns", [
        ("What enemies are there?",
         "• Bats: weak and fast.\n"
         "• Wolves: from 0:20.\n"
         "• Boars: slow, tough and armored, from 1:20.\n"
         "• Skeletons (Forest III onward, from 0:30): fast for their size, heavy armor but weak to magic.\n"
         "• Zombies (Forest V, from 1:30): slow, lots of HP, hit hard and resist magic.\n"
         "Each biome has its own 5 enemies with the same roles (a weak swarm, a mid one from 0:20, a heavy one from "
         "1:20, a new one from stage III and another new one in stage V):\n"
         "• Abandoned Town: Plague Rat, Feral Hound, Bandit Brute; Ghoul (III+, resists magic a bit); Wraith (V, "
         "magic damage, high magic defense, no armor).\n"
         "• Cathedral: Wisp (magic), Cultist (magic); Gargoyle (lots of armor); Living Armor (III+, very high "
         "armor, no magic defense); Fallen Seraph (V, magic damage).\n"
         "• Underground: Cave Beetle (armored swarm), Goblin Miner, Rock Golem (very tough); Slime (III+, resists "
         "magic, no armor); Crystal Wyrm (V, the strongest).\n"
         "• Inferno: Imp (spits fireballs), Hellhound (pounces), Horned Demon (very tough, axe cleave); Salamander "
         "(III+, fire trail, resists magic); Infernal Warlock (V, hellfire pillars, magic damage).\n"
         "Each stage ends with a boss (each biome has 5 bosses, one per stage)."),
        ("What is the scenery like?",
         "The forests have grass, bushes, flowers and rocks, which are only decoration, and trees, which block the "
         "party's movement: walk around them. Enemies pass under the trees. Each run generates a different forest, "
         "and the later forests are darker (webs in Forest III, dead trees in Forest V).\n"
         "The other biomes work the same way, with their own obstacles and decoration, and each stage changes a "
         "little:\n"
         "• Abandoned Town: cobblestone streets, ruined houses, wells and carts (market in II, fog and graves in "
         "III, burned town in IV, night with lamps in V).\n"
         "• Cathedral: stone floor, pillars and angel statues (red carpet in I, banners in II, stained glass in "
         "III, crypt with coffins in IV, purple bell tower in V).\n"
         "• Underground: rocky floor, stalagmites and boulders (mine with rails in I, gold veins in II, slime in "
         "III, crystal cave in IV, lava in V).\n"
         "• Inferno: basalt cracked with lava, obsidian spikes, brimstone and skull piles (ash and cages in I, "
         "bones in II, magma rivers in III, obsidian fortress with braziers in IV, the Demon King's throne with "
         "purple runes in V)."),
        ("What are power-ups?",
         "Rare drops: 0.2% from normal enemies, 25% from elites. Walk over them with the hero.\n"
         "• Tuna Can: the party heals 20% of max HP.\n"
         "• Cardboard Box: party invulnerable for 10 s.\n"
         "• Zoomies: +30% damage for 10 s.\n"
         "• Laser Pointer: +20% critical chance and +50% critical damage for 10 s.\n"
         "• Feather Wand: skills recharge 40% faster for 10 s.\n"
         "• Big Hiss: stuns every enemy on screen for 3 s.\n"
         "• Treat Bag: pulls every EXP gem.\n"
         "• Gold: coins that go straight to your gold (usually 1, sometimes 5, rarely 10). They fly to the hero "
         "on their own, like fragments (the other power-ups must be touched). They are kept even if the run ends in defeat.\n"
         "When they are off-screen, a pin on the edge shows the icon, the direction and the distance. Power-ups "
         "with a duration show their icon and remaining time at the bottom left of the screen."),
        ("How do enemies spawn?",
         "• Groups spawn just off-screen around the hero, faster and bigger as time passes (+1 enemy per group "
         "every 45 s).\n"
         "• Every minute a ring of bats surrounds the party.\n"
         "• Enemy HP and damage grow with the run timer."),
        ("What happens at 10:00?",
         "The timer stops and the stage boss appears. It calls a ring of 12 bats every 12 seconds.\n"
         "• The boss comes with 2 random classes (among the ones you unlocked): it carries both weapons and casts "
         "skills of both classes.\n"
         "• It is 3x tougher than before and its skills hit hard: watch the red circles.\n"
         "• It drops 5 Fragments of each of its two classes, its trophy the first time (see Altar of Trophies) and "
         "has a 25% chance to drop an accessory.\n"
         "Defeat it to clear the stage and unlock the next one."),
        ("What are Super Elites and Elite Squads?",
         "Every minute of the run (until 10:00) one of the two appears, with a warning on screen:\n"
         "• Super Elite: an elite 10x stronger than a normal one, with a gold ring and a bigger name. Drops 10 "
         "Fragments of its class.\n"
         "• Elite Squad: 5 random elites, each 2x stronger than a normal elite. Each one drops 2 Fragments of its "
         "class."),
        ("What are elite enemies?",
         "Any normal enemy has a small chance (1.2%) to spawn as an elite of a class you already unlocked on any "
         "character (max 3 at a time).\n"
         "• Classes used by your current party are 3x more likely, but any unlocked class can still appear.\n"
         "• Their name shows class and monster, e.g. Marauder Wolf.\n"
         "• They wear the class hat, have 10x HP, 2.5x contact damage and double defenses.\n"
         "• They cast every skill of their class at your party. Red circles on the ground show where their attacks "
         "will land: move out of them."),
        ("What do elites drop?",
         "• 10x EXP.\n"
         "• A Fragment of their class, used to upgrade that class's weapon and helmet (see Equipment) or offered "
         "at the Altar of Mastery (see Classes).\n"
         "• A higher chance of power-ups.\n"
         "• A small chance of an accessory of the stage (see Equipment).\n"
         "Like EXP, fragments are kept even if the hero dies or you quit the run. The pause screen shows those "
         "collected in the run and your inventory total."),
    ]),
    ("Stages & difficulty", [
        ("What is the Endless Rift?",
         "A stage at the bottom of the stage select (unlocked by clearing Forest I). It plays like the Endless: no "
         "time limit, the difficulty goes up one tier every 2 minutes, a boss every 2 minutes and a Super Elite or "
         "Elite Squad every minute. The differences:\n"
         "• Monsters, elites and bosses come from every stage you have unlocked, of any biome (new biomes join the "
         "pool when you unlock them). The order they appear in is the same as in the Endless.\n"
         "• The scenery changes after each boss is defeated (or when the next boss arrives, if it is still alive): "
         "a random scenery among the unlocked stages.\n"
         "• Base difficulty: the highest stage you have cleared.\n"
         "• Rift level (like the dungeons): each level adds +30% enemy HP, +15% strength, +20% resistance and "
         "+20% rewards. Surviving 10 minutes clears the level and unlocks the next; every 10 minutes the game asks "
         "if you want to stay or go up, and the timer keeps going. The selection starts at the highest unlocked "
         "level.\n"
         "• It doesn't drop accessories (for now): bosses always drop 1 accessory fragment, Super Elites 15%, "
         "squad elites 3% and other elites 1%. Class fragments, EXP and gold work as in the Endless."),
        ("What is the Training Room?",
         "The straw dummies at the camp (southeast) lead to a fenced field to test formations, builds and DPS / HPS "
         "with the active party. It starts empty: you place the dummies you want. Nothing there gives rewards (no EXP, "
         "gold, fragments or drops).\n"
         "• Dummies never die: when their life runs out it fills up again, and the meter (bottom right) counts all "
         "the damage. \"Reset meter\" starts the count again.\n"
         "• T (or the Training button) opens the panel: add normal dummies (choose how many), or an Elite, Super "
         "Elite, Elite Squad or Boss dummy of the chosen class (or random).\n"
         "• Dummy strength: base monster (Bat, Wolf, Boar, Skeleton, Zombie: life, armor, magic defense and "
         "damage), stage and run time (0:00 to 10:00), like in a real run.\n"
         "• \"Dummies attack\": on, they chase you, hit you and use their class skills; off, they stand still. "
         "The hero never falls in the Training Room (gets up right away with full life).\n"
         "• +1 / +10 level-ups to try the run upgrades; \"Restart build\" starts over. \"Manage party\" opens the "
         "party screen and brings you back to the room; \"Back to camp\" (or Q in the pause) leaves."),
        ("What are the dungeons?",
         "The red portal at the camp (east of the chest) leads to 3 dungeons: Cavern, Catacomb and Dungeon.\n"
         "• Each one is a long corridor: walk to the end, fighting what is in the way. Only Super Elites and Elite "
         "Squads appear, with monsters drawn from every monster in the game, and at the end there is a random "
         "boss with 5 classes, stronger than the stage bosses. A dungeon takes about 1 to 1.5 minutes.\n"
         "• Main reward: Cavern = lots of gold (every elite drops gold coins, the boss drops many, plus a clear "
         "bonus); Catacomb = class fragments (doubled, plus fragments of random classes on clear); Dungeon = "
         "accessory fragments (rings, bracers or trinkets from Super Elites, squads and the boss, plus a clear "
         "bonus).\n"
         "• After clearing a level, the results screen lets you go straight to the next level (button or N).\n"
         "• Each dungeon drops 4 accessories of its own, one of each type (shown in the selection screen).\n"
         "• Infinite levels: clearing level N unlocks level N+1 of that dungeon. Each level: +30% enemy HP, +15% "
         "strength, +20% resistance and +20% rewards. You can replay any unlocked level.\n"
         "• Dungeons do not give the stage gold reward or trophies, but give EXP and class fragments as usual."),
        ("What is the Altar of Trophies?",
         "The altar next to the portal at the camp. Each stage boss drops its trophy the first time it is "
         "defeated (100%, only once; Endless bosses count too; stages cleared before the altar existed grant "
         "their trophy too). At the altar, click a trophy to activate or "
         "deactivate it. Each active trophy:\n"
         "• applies its own modifier to the run;\n"
         "• adds +1 global difficulty level: enemies +15% HP, +10% strength and +10% density; +10% EXP and gold; "
         "+10% fragments (each fragment picked up is worth 10% more). The EXP bonus multiplies all EXP; the gold "
         "bonus multiplies the stage gold reward and every gold coin dropped.\n"
         "Trophies (good side first, BUT then the downside):\n"
         "• Colossal Boar Tusk (Forest I): every enemy has a 0.3% chance to drop a random class fragment, BUT "
         "enemies have +10% armor and magic defense.\n"
         "• Ancient Ent Sap (Forest II): every enemy has a 1% chance to drop gold (1, 5 or 10), BUT enemies "
         "regenerate 1% max HP per second.\n"
         "• Spider Queen Silk (Forest III): your pickup range gets a bonus equal to your movement speed bonus, BUT "
         "enemy contact hits have a 25% chance to slow you (30% for 1.5 s).\n"
         "• Shadow Wolf Fang (Forest IV): the party deals +20% damage to enemies at full HP, BUT enemy contact "
         "hits have a 25% chance to make you bleed (2% max HP per second for 3 s).\n"
         "• Corrupted Guardian Heart (Forest V): stages last only 5 minutes (the boss comes at "
         "5:00), BUT twice as many monsters spawn.\n"
         "The other biomes have 20 more trophies, all with the same logic (a bonus, BUT a downside): extra gold, "
         "EXP or party bonuses (crit, armor, area, damage, regeneration...) traded for faster, tougher or more "
         "numerous enemies or a party penalty. The altar shows them in one tab per biome."),
        ("What are biomes?",
         "Stages are grouped in biomes, each with 5 stages (I to V) and an Endless version:\n"
         "• Forest, Abandoned Town, Cathedral, Underground and Inferno (25 stages in all).\n"
         "Clearing stage V of a biome unlocks stage I of the next biome and the Endless of that biome. The stage "
         "select (the portal at the camp) shows each biome with a preview of its stages; a star marks cleared "
         "stages."),
        ("How does Endless work?",
         "• No time limit: the run goes on until the hero falls or you quit.\n"
         "• It starts at the difficulty of stage I of the biome, and every 2 minutes it goes up one tier (+50% "
         "enemy HP, +30% strength, +50% resistance, +25% EXP and gold).\n"
         "• Every minute a Super Elite or an Elite Squad appears, and the biome's new enemies (from stages III and "
         "V) join as the tier goes up.\n"
         "• Every 2 minutes a boss appears, taking turns among the bosses of stages I to V and following the "
         "scaling. Defeating it does not end the run.\n"
         "• Gold is proportional to the time survived. Your best time per biome is saved.\n"
         "• It can drop the accessories of every stage of the biome."),
        ("How do stages scale?",
         "Forest I to Inferno V (25 stages in a row). Each stage, compared to the previous one, adds:\n"
         "• +50% enemy HP and +30% enemy damage.\n"
         "• +50% enemy armor and magic defense.\n"
         "• +25% EXP and gold rewards."),
        ("What does the difficulty change?",
         "• Easy: 75% enemy HP and spawn rate.\n"
         "• Normal: 100%.\n"
         "• Hard: 135% HP and 130% spawn rate.\n"
         "Change it in Configurations."),
        ("Does party size change the game?",
         "Yes. More members means more enemies and tougher ones:\n"
         "• 2 members: x1.6 enemies, +8% HP.\n"
         "• 3 members: x2.2 enemies, +16% HP.\n"
         "• 4 members: x2.8 enemies, +25% HP.\n"
         "• 5 members: x3.4 enemies, +33% HP."),
    ]),
    ("Equipment", [
        ("How do armor, pants and boots work?",
         "They are crafted at the Blacksmith (tab Armor, Pants & Boots) with materials that monsters drop.\n"
         "• Every monster drops its own material (Wolf -> Wolf Fur, Skeleton -> Skeleton Bone...): 2% of normal "
         "kills, 40% of elites (x2), Super Elites always (x4), and bosses drop 3 of every material of their "
         "biome. Materials are kept even if the run ends in a defeat.\n"
         "• Each biome has 1 armor, 1 pants and 1 boots (15 items). Craft with the recipe, then upgrade up to +10 "
         "with more of the same materials (each level: +12% values; +10 = x2.2).\n"
         "• Armor is defensive, pants mix defense and utility, boots are pure utility/quality of life. Every "
         "biome's set has the same stat budget: Underground is not better than Forest, just different.\n"
         "• Each item is unique: only one party member can wear it (like accessories), and each member wears 1 "
         "armor, 1 pants and 1 boots."),
        ("What equipment does a character use?",
         "A weapon and a helmet that belong to their CURRENT class (e.g. Rogue's Dagger and Rogue's Helmet).\n"
         "They are fixed: they cannot be swapped or moved to another class.\n"
         "Equipment belongs to the CLASS, not to the character: every character who is a Rogue uses the same "
         "Rogue's Dagger, with the same upgrade level, no matter who paid for it."),
        ("How do I upgrade them?",
         "Camp -> Blacksmith -> pick a class in the list (it shows every class with its weapon and helmet level; "
         "a dot marks classes someone is using) -> Upgrade.\n"
         "Each upgrade costs Fragments of that class and gold:\n"
         "• +1 costs 1 fragment and 2 gold, +2 costs 2 and 4 ... +10 costs 10 and 20.\n"
         "• In total: 55 fragments and 110 gold per item.\n"
         "The maximum is +10 and the name shows the level (e.g. +3 Rogue's Dagger)."),
        ("What do upgrades give?",
         "• Weapon: +3% all damage and +0.5% critical chance per level.\n"
         "• Helmet: +3% max HP, +1 armor and +1 magic defense per level.\n"
         "They apply in runs and in the stats shown in Party Setup."),
        ("What happens at +10?",
         "A +10 item gives EVERY character a PERMANENT bonus that counts in every class.\n"
         "Weapon: +5 of the class attribute (balanced classes +2 STR, AGI and INT).\n"
         "Helmet:\n"
         "• STR classes: +2 armor, +4% critical damage, +3 VIT.\n"
         "• AGI classes: +1.5% dodge, +1.5% critical chance, +3 VIT.\n"
         "• INT classes: +2 magic defense, +1.5% cooldown, +3 VIT.\n"
         "• Balanced classes: +1 armor, +1 magic defense, +3 VIT."),
        ("What happens when I change class?",
         "Upgrades are saved per class and shared by all characters.\n"
         "If the Warrior helmet is +2 and you switch to Arcanist, you use the Arcanist helmet (its own level). "
         "Any character who becomes a Warrior uses the +2 helmet."),
        ("What are accessories?",
         "Unique items made at the Jeweler (camp): 2 rings, 1 bracer, 2 trinkets, 1 necklace and 1 emblem per character. The "
         "Jeweler list shows where each one comes from (stage or class level).\n"
         "• Rings (30): simple bonuses: damage, critical chance or cooldown for one damage type (slash, piercing, "
         "blunt, fire, ice, lightning, holy, arcane). General rings work for everything but are weaker.\n"
         "• Bracers (23): conditional: more damage or critical chance against burning, chilled, poisoned, "
         "bleeding, stunned or slowed enemies, and effects when you cause a status (attack speed, damage, healing...).\n"
         "• Trinkets (23): chance effects: meteors when you burn, chain lightning, buffs on critical hits, a "
         "phoenix that revives you once per run...\n"
         "Each accessory drops once and becomes an account unlock. Only one character can wear it at a time: "
         "equipping it on someone else takes it off the first one."),
        ("Where do accessories drop?",
         "Each stage drops 4 different accessories: always 1 ring, 1 bracer, 1 trinket and 1 emblem "
         "(the stage select shows them; a check marks the ones you "
         "already have). The Endless of a biome can drop the accessories of all its stages. On average a full run "
         "gives about 1 accessory (more with luck), so it takes about 8 runs to find all 4 of a stage.\n"
         "• Bosses: 25% per kill. Super Elites: 5%. Squad elites: 1.2%. Other elites: 0.5% (divided by the party's "
         "enemy multiplier, so bigger parties don't get more drops just from having more elites).\n"
         "• Each dungeon of the red portal also drops 4 accessories of its own (1 of each type).\n• Necklaces don't drop: they unlock with the class level.\n"
         "• Accessories that are not in any stage or dungeon yet will drop in the next stages."),
        ("What happens with duplicates?",
         "A duplicate becomes a fragment of its category (Ring, Bracer, Trinket, Emblem). At the Jeweler, "
         "fragments upgrade any accessory of that category from +1 to +5 (costs 1, 2, 3, 4 and 5). Each level "
         "gives +20% to the accessory values (chances stay the same)."),
        ("What are necklaces?",
         "One necklace per class (30). They don't drop: each necklace unlocks "
         "when any character takes its class to the normal max level (Lv 100), and classes already there get it "
         "right away.\n"
         "• The class sets the theme, but any class can wear it. Examples: Archer: projectiles may ricochet; "
         "Spellblade: elemental damage imbues your physical hits; Summoner: hits may evoke a summon of the hit's "
         "type; Pugilist: melee combo; Gladiator: strikes back when hit; Berserker: life steal.\n"
         "• Necklaces are upgraded (+1 to +5) with the fragments of their own class: 5, 10, 15, 20 and 25."),
        ("What are emblems?",
         "A slot for 1 emblem per character (23 emblems). They work like bracers, but for the WHOLE PARTY:\n"
         "• Fixed bonuses go to every party member (e.g. Emblem of Embers: the party deals +12% damage to burning "
         "enemies; Emblem of the Guard: +3 armor and magic defense for everyone).\n"
         "• Effects with a trigger fire with the hits and kills of ANY party member and give the bonus to the whole "
         "party (e.g. Emblem of Thunder: whenever anyone stuns an enemy, the party gains +1 to every attribute for "
         "5 s, stacking up to 10x; Emblem of War: each kill adds +1% damage for the party, up to +15%).\n"
         "• Like other accessories they are unique (one character at a time), drop in stages and dungeons (one per "
         "place; the others in future stages) and duplicates become Emblem fragments to upgrade them.")
    ]),
    ("Party, EXP & gold", [
        ("What is the Altar of Greed?",
         "The golden lucky cat at the lower-left of the camp (unlocked after Forest IV or 150 gold). It turns "
         "spare gold into permanent bonuses for the WHOLE party.\n"
         "• Attack +2%, Max HP +3%, Range +2%, Area +2% and Critical damage +4% per level, with no limit.\n"
         "• Defense +1%, Critical chance +0.5%, Cooldown -0.5% and Dodge +0.5% per level, up to 10 levels "
         "(they have caps).\n"
         "• The first level of any stat costs 20 gold and each level of THAT stat costs 40% more than the last, "
         "so spreading the gold over many stats goes further."),
        ("How big is the party?",
         "• A run is played by a party of 5 members at most: the hero plus up to 4 active allies.\n"
         "• You can recruit up to 20 characters in total; the ones that are not active wait in reserve.\n"
         "• In Party Setup (the tent at the camp), select a member and use Activate / Remove to choose who goes to the run.\n"
         "• Only active members receive EXP from the run."),
        ("How does recruiting work?",
         "Camp -> Tent (Party Setup) -> Recruit.\n"
         "• The first recruit costs 5 gold and each next one costs double (5, 10, 20, 40 ...).\n"
         "• A new recruit becomes active if the party has a free spot; otherwise it goes to the reserve."),
        ("How do I change a cat's appearance?",
         "Every character is a cat. A new recruit gets a random look.\n"
         "Camp -> Tent (Party Setup) -> select the member -> Look (or A).\n"
         "• You can choose fur color, pattern (solid, tabby, tuxedo, spotted, points, bicolor), marking color, eye "
         "color, tail and ears. Randomize draws a new look; Undo changes goes back to how it was.\n"
         "• The helmet/hat, the weapon and the tunic color always come from the current class."),
        ("How does EXP work?",
         "Everything collected in the run is added up. At the end, every active member receives the same total EXP "
         "for their character level (no maximum) and their current class level (which keeps its maximum)."),
        ("What happens when an ally falls?",
         "They come back after 20 seconds with half HP (a bar shows the countdown).\n"
         "If the hero falls, the run ends."),
        ("How do I earn gold?",
         "• Stage reward: 5 gold x the stage reward (Forest I x1, each next stage +25%). If you do not clear the "
         "stage, you get a part proportional to the time survived. In Endless it is proportional to the time "
         "survived, with the reward of the current tier.\n"
         "• Gold coins: dropped as a power-up (usually 1, sometimes 5, rarely 10; elites drop power-ups much more "
         "often). They fly to the hero on their own and go straight to your gold, even if the run ends in defeat.\n"
         "• Ancient Ent Sap trophy: every enemy has a 1% chance to drop coins.\n"
         "• When everything is upgraded, the +1 Gold level-up card.\n"
         "• The global difficulty level of the Altar of Trophies adds +10% gold per level: it multiplies the stage "
         "reward, every coin and the +1 Gold card.\n"
         "Gold is spent on recruits (Party Setup) and equipment upgrades (Blacksmith). The pause screen shows the "
         "gold collected in the run; the results screen shows the stage reward and the gold from drops."),
    ]),
    ("Version & language", [
        ("What does the version number mean?",
         "The version is shown on the title screen.\n"
         "• Alpha: 0.0.X. A bigger update (new features or many changes) raises X, e.g. 0.0.6 -> 0.0.7.\n"
         "• Small adjustments get a fourth number: 0.0.6.1, 0.0.6.2 ...\n"
         "• 0.1.X will be the Beta, and 1.X.X the full release."),
        ("Can I play in Portuguese?",
         "Yes. Configurations -> Language switches between English and Português.\n"
         "Character, class and skill names stay in English."),
        ("Can I play on the phone (web version)?",
         "Yes: the web version runs in the browser, on the phone (landscape) or on the PC.\n"
         "• Drag your finger on the left side of the screen to walk (virtual joystick).\n"
         "• The round button at the bottom right is the dodge; the II button at the top right pauses.\n"
         "• Taps work as mouse clicks in every menu; drag up or down to scroll lists.\n"
         "• Pause and results have big buttons (Resume / End run, Back to camp / Play again); the camp has a Menu "
         "button.\n"
         "• Progress is saved in the browser (separate from the PC save).\n"
         "• To keep the phone smooth, the web version keeps fewer enemies on screen at the same time."),
    ]),
    ("Editing content", [
        ("Can I change skills and class bonuses?",
         "Yes. classes.xlsx (next to the game or next to the .exe) has one sheet per class with the 10 actives, "
         "10 passives and the stat bonus of every level.\n"
         "The game reads it on start; if it is missing it uses the built-in content."),
    ]),
    ("Patch notes", [
        ("0.0.31",
         "• New biome: Inferno (stages I to V and Inferno Endless), unlocked by clearing Underground V. Ash, lava "
         "rivers, an obsidian fortress and the Demon King's throne.\n"
         "• 5 new enemies (Imp, Hellhound, Horned Demon, Salamander, Infernal Warlock), each with its own attack, "
         "and 5 bosses (Imp Prince, Cerberus, Magma Colossus, Demon General, Demon King).\n"
         "• 5 new trophies, 15 new accessories (bracers, trinkets and emblems) and 5 rings that now drop in the "
         "Inferno stages.\n"
         "• 5 new monster materials and 3 new Blacksmith items (Demonhide Cuirass, Salamander Leggings, Hellhound "
         "Treads).\n"
         "• The Inferno monsters and bosses also join the dungeons and the Endless Rift.\n"
         "• Art: removed the old drawings that were no longer used (lighter game). Elite hats, boss weapons and "
         "the hit flash now follow the pixel art of the sprites.\n"
         "• Settings: new FPS limit option (60, 120, 144 or Unlimited; the default is now Unlimited).",
         ),
        ("0.0.30",
         "• Corrupted Guardian Heart (trophy): the game no longer runs at 2x speed. Now stages last 5 minutes (the "
         "boss comes at 5:00, the stage progresses twice as fast) and twice as many monsters spawn.\n"
         "• Heroes' sprites take the colors of the equipped armor, pants and boots from the Blacksmith.\n"
         "• Inventory: new Monster materials tab with every material, how many you have, who drops it and the "
         "recipes that use it.\n"
         "• Jeweler: tag filter for the accessories, like the one for skills (tags also show in the tooltip).\n"
         "• Portuguese: class and skill names (actives, passives and descriptions) are now translated.\n"
         "• Builds: the executable and the .zip files (PC and web) are now named CatFantasySurvivors.",
         ),
        ("0.0.29.1",
         "• Stage select: removed the list of bosses and sceneries from the Endless Rift panel (it overflowed the "
         "panel once every biome was unlocked).",
         ),
        ("0.0.29",
         "• Enemy sprites rethought to match the heroes' look (big heads, chunky bodies and paws): Wolf, Feral "
         "Hound, Plague Rat, Rat King, Corrupted Guardian, Cave Beetle, Matriarch, Crystal Wyrm and Deep Wyrm "
         "(now a crystal serpent), Wraith (a hooded ghost cat). Humanoids are cats: the Goblin Miner and the "
         "Goblin King are now green goblin cats and the High Inquisitor got a real cat face. The Stained Glass "
         "Golem is now a construct of leaded glass panes with a rose-window head. Every monster, elite and boss now "
         "uses the same pixel grid as the cats (the pixel grows with the sprite size), so big monsters and bosses "
         "have the same chunky pixel art as the heroes.\n"
         "• Altar of Greed (new at the camp, after Forest IV or 150 gold): spend gold on permanent bonuses for the "
         "whole party: Attack, Defense, Max HP, Range, Area, Critical chance, Critical damage, Cooldown and Dodge. "
         "Each stat costs 40% more per level, so spreading the gold goes further; Defense, Critical chance, "
         "Cooldown and Dodge stop at 10 levels so they don't break their caps.\n"
         "• Armor, Pants & Boots: every monster now drops its own material (Wolf Fur, Skeleton Bone, Slime Gel...). "
         "At the Blacksmith (new tab) each biome's materials craft 1 armor, 1 pants and 1 boots, upgradable up to "
         "+10. Armor is defensive, pants mix defense and utility, boots are pure utility, and every biome's set "
         "has its own identity with the same stat budget. Each item is unique: one party member at a time.\n"
         "• Wiki: new tables (Armor, pants, boots & materials; Altar of Greed) and guide entries.",
         ),
        ("0.0.28.2",
         "• Walking animation: the cats now really walk instead of sliding. While moving, the paws step forward and "
         "back with little legs, one paw lifts as it passes the other, the body bobs, the tail sways and the "
         "weapon hand swings with the step. The steps follow the distance walked (faster = quicker steps) and "
         "stop when the character stops. Applies to the heroes in runs, the hero in the camp, shadow clones and "
         "the cats on the title screen.",
         ),
        ("0.0.28.1",
         "• Hit timing: every animation now matches the moment of the damage. Slashes, thrusts, cones, arrow "
         "rain and traps appear at full size on the first frame (their damage is instant), meteors and comets "
         "fall during the warning and land exactly when the damage happens, auras pulse each time they hit and "
         "the Thorns capstone shows a spark on the enemy hit back. Projectiles keep dealing damage only when they "
         "touch the enemy.\n"
         "• Debuff animations on enemies and on your party: Bleeding drips blood, Poisoned releases green "
         "bubbles, Burning shows flames, Chilled sparkles with frost, Stunned has stars spinning over the head "
         "and Slowed shows blue ripples at the feet.",
         ),
        ("0.0.28",
         "• Skill animations: every skill of the heroes, elites and monsters now has animated pixel art that "
         "matches its class and name: arrows, kunai, spinning shuriken and axes, fireballs, ice shards, music "
         "notes, sword swooshes, spear thrusts, magic beams, meteors, lightning from the sky, pillars of holy "
         "light, rune circles, bear traps, arrow rain, burning ground, toxic bubbles and more. Summons got their "
         "own sprites (wolf, falcon, elemental spirits; shadow clones are a dark copy of the cat).\n"
         "• Each animation covers exactly the skill's hitbox: impacts and lingering areas show the damage "
         "circle, slashes and cones show their sector, thrusts show the line width and projectiles are the size "
         "of their hit radius.\n"
         "• Heals, buffs, Taunted (!) and Weakened (arrow) enemies have their own markers. Monster moves (sonar, "
         "bile, club smash, dive, bombs, fallen light...) and their dust trails are animated too.\n"
         "• Run items renamed with a cat theme and new icons: Catnip (damage), Feather Paws (speed), Ninth Life "
         "(HP), Long Whiskers (pickup range), Cat Nap (cooldown), Warm Milk (regeneration), Sharp Claws (range), "
         "Ball of Yarn (area), Fish Feast (heal) and Mystery Box (random power-up). Power-ups: Tuna Can, "
         "Cardboard Box, Zoomies, Laser Pointer, Feather Wand, Big Hiss and Treat Bag.",
         ),
        ("0.0.27.2",
         "• Title screen: instead of monsters, cats of every class with random looks now walk around in the "
         "background.",
         ),
        ("0.0.27.1",
         "• Removed the per-class HP, Defense (%) and Speed multipliers: base HP, Defense, Attack and Speed now come "
         "only from the class role (Index sheet of classes.xlsx). The class sheets no longer have those rows.\n"
         "• New text for the All-Rounder role.",
         ),
        ("0.0.27",
         "• Roles: every class now has a role (All-Rounder, Ranged Assassin, Caster, Melee Assassin, Support, "
         "Healer or Tank) that sets its base HP, Defense, Attack and Speed and how it behaves as an AI ally. "
         "Casters and Ranged Assassins keep their distance, Supports and Healers stay close to the party, Melee "
         "Assassins chase targets further, and Tanks go after enemies near the other members and draw more "
         "aggro. The role of each class and the multipliers are on the Index sheet of classes.xlsx.\n"
         "• Active skills of every class were redone around their roles, keeping each class's identity: "
         "All-Rounders mix single-target and area strikes with a support skill; Ranged Assassins focus on "
         "single-target shots; Casters on area spells; Melee Assassins on single-target hits and stuns; Supports "
         "on party buffs, enemy debuffs and some healing; Healers on heals and protection; Tanks on area, defense "
         "and support, each with at least one area Taunt.\n"
         "• New effects: Taunt (enemies hit attack the caster) and Weaken (enemies hit take more damage for 4 s). "
         "Both show in skill tooltips and in the CC meter.\n"
         "• Class screen: shows the role and its multipliers (hover for the behavior). Wiki: new Roles table, Role "
         "column in Classes and new entries in the guide.\n"
         "• Saved loadouts keep their slots, but the skills in them are the new ones.",
         ),
        ("0.0.26",
         "• Monsters: every monster now has its own behavior and a signature move. Bats hover close and use a "
         "sonar cone that slows; wolves speed up near prey and bite to cause Bleeding; boars charge (Stun + "
         "knockback); skeletons throw bones; zombies spit slowing bile puddles; rats zigzag with a plague bite; "
         "hounds pounce; brutes smash with a club (Stun); ghouls go into a frenzy when hurt; wraiths blink and "
         "wail (slowing nova); wisps explode; cultists keep their distance and cast dark bolts; gargoyles dive; "
         "living armors thrust a lance; seraphs smite two targets (Stun); beetles roll; goblins throw bombs; "
         "golems slam (Stun); slimes leave a slowing trail; worms erupt under you. Every attack shows a warning "
         "area before it lands.\n"
         "• Elites keep the signature move of their monster on top of their class skills. Bosses are unchanged.\n"
         "• New effects on your party: Stunned (with a short immunity afterwards), Slowed, Bleeding and knockback.\n"
         "• Wiki: the Enemies table has a new \"Signature move\" column.\n"
         "• Deaths: a little dust cloud now covers the defeated enemy, which stays on the ground for a moment "
         "with X eyes and then fades away.\n"
         "• Skill tooltips show the damage % and, in parentheses, the damage with the character's current stats "
         "(e.g. Damage: 90% (14)).",
         ),
        ("0.0.25.1",
         "• Damage scaling: character damage is now 10 + the main attribute of your current class (STR, AGI or "
         "INT), instead of STR + AGI + INT. Novice, Freelancer and Warfarer use the average of the three. Skill "
         "percentages did not change (basic attack 100% per second of cooldown), and the damage at high levels "
         "is back to the old range."),
        ("0.0.25",
         "• Skill tuning pass. Character damage is now STR + AGI + INT, and every attack deals a % of it "
         "(skill tooltips and the Wiki show the %).\n"
         "• Basic attack: 100% per second of cooldown. Light weapons (daggers, claws, fists) hit faster and "
         "weaker; heavy and two-handed weapons (spears, longswords, axes, Two-handed axe 1.6 s) hit slower and "
         "harder, with the same damage per second.\n"
         "• Actives: damage per use grows with the cooldown (a 5 s skill hits much harder than a 3 s one). Area, "
         "several targets, piercing, explosions, homing, stun, slow, knockback and elemental effects make a skill "
         "a bit weaker than a pure single-target hit. Lingering areas deal % per second, auras % per tick, orbits "
         "and summons % per touch.\n"
         "• Heals and buffs were not changed. At high levels damage is higher than before, since all three "
         "attributes now count."),
        ("0.0.24.7",
         "• The 3 dungeons of the Red Portal were redrawn in pixel art with the same level of detail:\n"
         "• Cavern: damp rock floor in plates with cracks, puddles, pebbles and ore; rock walls in strata with "
         "crystal clusters, stalactites (and stalagmites) and gold veins; crystals and glowing mushrooms on the "
         "floor.\n"
         "• Catacomb: bone-white flagstones with wax, bone chips and carved skulls; an ossuary wall of stacked cat "
         "skulls and bones; arched niches with skulls, skull candle holders with flickering flames and wrapped "
         "bodies in wall tombs; bones and candles on the floor.\n"
         "• Dungeon (prison): uneven dark flagstones with moss, damp stains and straw; big stone blocks on the "
         "walls with damp streaks; torches with animated flames, chains with shackles and barred cells with "
         "glowing eyes blinking in the dark; straw piles, buckets and loose chains on the floor.\n"
         "• Walls cast a shadow on the floor, the boss gate is a stone arch with glowing runes, and the dungeon "
         "previews are no longer blurred."),
        ("0.0.24.6",
         "• The Cathedral level of detail now reaches every stage:\n"
         "• Forest: trees with roots, bark and leafy clumps with light and shadow; twisted dead trees with forked "
         "branches and hanging moss (Forest V); bushes with berries, flowers with petals, mossy rocks, and new "
         "mushrooms, stumps and fallen logs.\n"
         "• Abandoned Town: brick well with a plank roof, crank, rope and bucket; carts with spoked wheels (one "
         "broken), sacks and crates, or a striped market awning with fruit; graves with a carved cross, epitaph, "
         "dirt mound, flowers and a candle; plank crates, stave barrels, brick rubble, grain sacks, fruit "
         "baskets, cat bones, embers in ashes and iron street lamps.\n"
         "• Underground: layered stalagmites with mineral bands, mine supports with nails, braces, a lit lantern "
         "and rails; crusted lava pools with bubbles; angular pebbles, puddles with reflections, glowing "
         "mushrooms, faceted crystals, rails with sleepers, tipped mine carts, gold nuggets and melted bones."),
        ("0.0.24.5",
         "• Cathedral props redrawn with much more detail: gothic columns (stepped base, clustered shafts with "
         "light and shadow, stone blocks, carved capital, ivy and cracks), broken columns with fallen pieces, "
         "praying cat-angel statues (hooded ears, folded wings, robe folds, halo, bronze plaque, moss), stone "
         "sarcophagi with a carved cat-knight and the lid slightly open.\n"
         "• New in the Cathedral: iron candelabras with three lit candles and wooden church pews.\n"
         "• Better floor details: candle clusters with dripping wax, angular rubble and cat skulls with bones."),
        ("0.0.24.4",
         "• Camp: fixed the floor showing separate squares (the bigger ground tile was being drawn on top of "
         "itself). The dirt clearing around the campfire and the trail to the portal are now pixel art with a "
         "dithered edge.\n"
         "• Training Room: new pixel art floor (packed dirt with straw and grass around the fence)."),
        ("0.0.24.3",
         "• Scenery redrawn in pixel art for the Abandoned Town, Cathedral and Underground, in the same style as "
         "the Forest: rounded cobblestones with light and shadow, dirt between them, moss, weeds and puddles; a "
         "gothic floor of light and dark diamond slabs with bevels, wear, cracks, broken slabs, candle wax and "
         "stone rose windows; cave floors made of rock plates split by cracks (glowing lava cracks in Underground "
         "V), pebbles and ore flecks.\n"
         "• Ground tiles are twice as big, so the pattern no longer repeats on screen.\n"
         "• New houses (timber frame, tiled roof, chimney, shutters and plank door), angular boulders, faceted "
         "crystal clusters, stained glass light on the floor and worn rugs with fringes."),
        ("0.0.24.2",
         "• Monsters and bosses lost the round \"ball\" body of the old look and got real silhouettes: wolves, "
         "hounds, boars, rats and the Corrupted Guardian (now a corrupted stag) seen from the side with four legs; "
         "bats with membrane wings; a walking tree Ent; a Spider Queen with abdomen and jointed legs; crouching "
         "gargoyles; long beetles; goblins and golems with bodies, arms and legs; worms with tapering segments. "
         "The cat folk (bandits, zombie, ghoul, knights, seraphs) now have a torso, legs and clothes.\n"
         "• Camp: the Tent (striped canvas, open flaps with a lantern inside, ropes, rug and crates), the Forge "
         "(stone base, timber frame, plank roof, chimney with sparks, brick furnace, bellows, weapon rack, barrel "
         "and sign), the Stage Portal (carved stone arch with glowing runes, pillars, steps, keystone crystal, "
         "spiral vortex and floating stones) and the Red Portal (obsidian monoliths, burning cracks and embers) "
         "were redrawn with much more detail."),
        ("0.0.24.1",
         "• Humanoid enemies are cats now: Skeleton, Zombie, Bandit Brute, Ghoul, Wraith, Cultist, Living Armor, Fallen "
         "Seraph and the bosses Bandit Lord, Plague Doctor, Headless Knight, Hollow Mayor, High Inquisitor, Bone "
         "Bishop and Fallen Archangel got cat ears, muzzle and whiskers, cat eyes and a tail. Animals and "
         "monsters (bats, wolves, spiders, gargoyles, slimes, goblins...) stay as they were."),
        ("0.0.24",
         "• New name: Cat Fantasy Survivors.\n"
         "• New pixel art look for the whole game, darker and gothic (inspired by Blasphemous, Last Faith and "
         "Chasm): pixel font, the world drawn in 2x2 pixel blocks with dark outlines and light/shadow on every "
         "sprite, textured pixel floors, color grading with vignette, and stepped corners on the interface.\n"
         "• Every icon (skills, passives, classes, items, accessories, trophies, power-ups and equipment) was "
         "redrawn as pixel art: small grid, few colors, 1-pixel outline and a beveled frame. Rings now look like "
         "rings.\n"
         "• The heroes are cats! Every character is a cat wearing the helmet/hat and weapon of its class, with "
         "the tunic in the class color.\n"
         "• Cat appearance: recruits get a random look, and Party Setup has a new Look button (A) to customize "
         "fur color, pattern, marking color, eyes, tail and ears. Older characters keep the look they had.\n"
         "• The Blacksmith and the Jeweler at the camp are cats too."),
        ("0.0.23.4",
         "• Fewer repeated passives: no passive effect appears in more than 3 classes now. Melee Haste, Exploit "
         "Stunned, Melee Mastery, Exploit Bleeding/Burning/Slowed/Any Debuff, Heal Haste, Melee/Fire/AoE Precision, "
         "Holy Mastery, Benevolence, Expansion and the repeated damage passives were swapped in some classes for "
         "other tags or new passives (e.g. Pressure Points, Hamstring, Shield Bash, Exploit Elemental, Ravager).\n"
         "• Passive balance: every passive is now worth the same budget. A passive with 2 effects gives less of "
         "each than the passive with only that effect (e.g. Fortitude: +15% armor; Iron Shirt: +9% armor and "
         "+1.5 HP/5s). Damage with a broad tag (melee, ranged, projectile, AoE, single target, physical, magical) "
         "is +10%; with a narrow tag (fire, holy, bleed, knockback...) +12%. Many values changed a little."),
        ("0.0.23.3",
         "• Defensive passives are no longer repeated: only one of each is left: Fortitude (Lancer), Evasion "
         "(Archer), Warding (Thaumaturge) and Endurance (Novice). The other classes got 26 new passives in their "
         "place (e.g. Iron Shirt, Camouflage, Divine Bulwark, Pain Tolerance).\n"
         "• Buff Haste (cooldown of buff skills) stays only on Bard and Time Mage. Arcanist, Templar, Gladiator and "
         "Warrior now have a buff duration passive instead (+15% duration of buff skills).\n"
         "• New passive effect: buff duration (buffdur in classes.xlsx)."),
        ("0.0.23.2",
         "• Class levels: up to Lv 100 each class now gives 18 points of its main attribute and 5 of each of the "
         "other two (it used to be 28 and 0). The total is the same.\n"
         "• Diminishing returns: critical chance, dodge and cooldown now have 2 softcaps, at 1/3 and 2/3 of the "
         "maximum. Above the 1st a bonus counts half, above the 2nd only 1/5 (crit 33%/67%, dodge 25%/50%, "
         "cooldown 20%/40%). Critical damage is unchanged. See the Wiki.\n"
         "• Less redundant passives: there is now only one % attribute passive of each kind: STR Training (Lancer), "
         "AGI Training (Archer), INT Training (Thaumaturge), and Versatile Training and Vitality (Novice). The "
         "other classes got 55 new passives in their place (e.g. Pyromania, Shadowstep, Lay on Hands, Second Wind)."),
        ("0.0.23.1",
         "• Buff timers: next to the power-ups (bottom left) the run now also shows the buffs of skills and "
         "accessories. Power-ups are square icons with a gold border and a bar; buffs are round icons with a ring "
         "that empties over time (blue = skill, purple = accessory, green = passive). Hover one to see its name "
         "and effect.\n"
         "• Bosses: no more red circle on them. The areas a boss hits around itself are now drawn under it, in "
         "the skill's color, so the boss stays visible.\n"
         "• Camp: the gold counter left the camp screen; gold is shown in the Chest (inventory)."),
        ("0.0.23",
         "• New player experience: a new save starts with only the Portal, the Tent and the Training Room at the "
         "camp. The other places appear as you progress (Chest: first fragment · Blacksmith: Forest III · "
         "Jeweler: first accessory · Altar of Trophies: first trophy · Altar of Mastery: first mastered class · "
         "Red Portal: Forest V), with a NEW! tag and a notice.\n"
         "• Explanations: a welcome pop-up on a new save, and a pop-up the first time you use each mechanic (stage "
         "select, Endless, Endless Rift, first run, party, classes, loadout, Training Room, chest, blacksmith, "
         "jeweler, altars and dungeons). Every one of these screens has a \"?\" button to see it again. Saves "
         "from before this update keep everything unlocked and don't show the pop-ups.\n"
         "• The FAQ is now the Wiki, with two tabs: Guide (the old FAQ) and Database: tables with icons of every "
         "class (how to unlock), skill and passive (class and unlock level), accessory (effect and how to get it), "
         "trophy, stage and dungeon (boss, enemies, drops), enemy (stats), power-up, run item, element, status and "
         "tag, built from the game data. A search bar (click it or press /) searches both tabs.\n"
         "• Loadout: the class's own active and passive slots now have a tag filter too (T), not only the "
         "mastery slots."),
        ("0.0.22.2",
         "• Camp: the Altar of Trophies sprite now shows the same 4 biome balls (they fill up as each biome's "
         "trophies are activated) instead of one dot per trophy, which no longer fit."),
        ("0.0.22.1",
         "• Altar of Trophies: the biome tabs no longer have icons sticking out; each tab has a ball in the "
         "biome's color that fills up as that biome's trophies are activated."),
        ("0.0.22",
         "• New biomes: Abandoned Town, Cathedral and Underground, 5 stages each (20 stages in all), each with "
         "its own scenery (with small changes from stage to stage, like the forests), 5 new enemies and 5 bosses "
         "with their own sprites. Same logic as the forest: 3 enemies in stages I and II, a new one from stage "
         "III and another new one in stage V; the difficulty keeps going up stage after stage; each biome has its "
         "Endless.\n"
         "• Abandoned Town: Plague Rat, Feral Hound, Bandit Brute, Ghoul, Wraith · bosses Rat King, Bandit Lord, "
         "Plague Doctor, Headless Knight, Hollow Mayor.\n"
         "• Cathedral: Wisp, Cultist, Gargoyle, Living Armor, Fallen Seraph · bosses Grand Gargoyle, High "
         "Inquisitor, Stained Glass Golem, Bone Bishop, Fallen Archangel.\n"
         "• Underground: Cave Beetle, Goblin Miner, Rock Golem, Slime, Crystal Wyrm · bosses Broodmother, Goblin "
         "King, Ooze Titan, Crystal Golem, Deep Wyrm.\n"
         "• 15 new trophies (one per new boss), always a trade-off; the Altar of Trophies now has one tab per "
         "biome.\n"
         "• Accessory drops in every new stage (1 ring, 1 bracer, 1 trinket, 1 emblem), using the accessories "
         "that had no source yet, plus 9 new ones: Bulwark, Reaper's and Toxin Bracers; Ghost Lantern, Holy Censer "
         "and Crystal Geode; Emblems of Ruin, of the Seeker and of the Depths.\n"
         "• The dungeons and the Endless Rift now use the monsters of every unlocked stage.\n"
         "• Save slots: Continue, New Save and Load Save in the main menu, 3 slots with a summary card each.\n"
         "• Class selection screen: the \"Current class\" text was removed (the class is already highlighted in "
         "the tree)."),
        ("0.0.21.1",
         "• Class selection screen: new Back button (top right), like the other screens (ESC still works)."),
        ("0.0.21",
         "• New stage: Endless Rift (bottom of the stage select, unlocked by clearing Forest I). Like the Endless, "
         "but with monsters, elites and bosses from every unlocked stage, a random unlocked scenery after each "
         "boss and the base difficulty of the highest stage you have cleared.\n"
         "• Rift levels (like the dungeons): surviving 10 minutes clears the level and unlocks the next; every 10 "
         "minutes you choose to stay or go up, and the timer keeps going.\n"
         "• No accessories in the rift (for now): elites and bosses drop accessory fragments directly."),
        ("0.0.20.1",
         "• Training Room: it now starts empty; place the dummies you want in the panel (T). When you come back "
         "from \"Manage party\" or use \"Restart build\", the same dummies are placed again."),
        ("0.0.20",
         "• New: Training Room. The straw dummies at the camp lead to a fenced field to test formations, builds and "
         "DPS / HPS. Dummies never die; add normal ones (choose how many) or Elite, Super Elite, Elite Squad and Boss "
         "dummies of any class, choose their strength (base monster, stage, run time) and whether they attack. "
         "Also: reset meter, +1 / +10 level-ups, restart build, manage party and back to camp (panel: T).\n"
         "• New straw training dummy sprites."),
        ("0.0.19.3",
         "• Necklaces are back to being unlocked only by taking their class to Lv 100 (they no longer drop). Each "
         "stage and dungeon now drops 4 accessories: 1 ring, 1 bracer, 1 trinket and 1 emblem.\n"
         "• Bosses no longer have the colored circles around them (they made the fight hard to see).\n"
         "• Dungeon cleared: the results screen has a \"Run next level\" button (or N) that starts the next level "
         "right away with the same party."),
        ("0.0.19.2",
         "• New level-up option: tick \"Pick the next level-ups of this run at random\" (or press A) and every next "
         "level-up of the run is picked at random automatically. It does not affect the Roast Chicken / +1 Gold / "
         "Random Power-up choice. In the pause screen, A turns it off.\n"
         "• Fix: the Jeweler crashed when showing the source of necklaces that drop in a dungeon."),
        ("0.0.19.1",
         "• Accessory drops reorganized: every stage and every dungeon now drops exactly 1 ring, 1 bracer, 1 "
         "trinket, 1 necklace and 1 emblem. Necklaces can now also drop (they still unlock at class Lv 100); a "
         "duplicate necklace becomes 5 fragments of its class.\n"
         "• Stage select: the accessory drops wrap into more lines (the Endless panel no longer overflows) and "
         "show how many you have found. The dungeon cards show the 5 drops as icons.\n"
         "• Dungeon selection: the level always starts at the highest unlocked level; shorter texts."),
        ("0.0.19",
         "• New accessory slot: Emblem (1 per character, 20 emblems). Like bracers, but for the whole party: fixed "
         "bonuses go to every member and triggered effects fire with any member's hits and kills (e.g. Emblem of "
         "Thunder: stuns give the party +1 to every attribute for 5 s, stacking up to 10x).\n"
         "• Each Forest stage also drops one emblem (Blood, Mercy, Shattering, War, Embers); the others come in "
         "future stages. Duplicates become Emblem fragments; the Dungeon can also give them."),
        ("0.0.18",
         "• Red Portal at the camp with 3 dungeons: Cavern (lots of gold), Catacomb (class fragments) and Dungeon "
         "(accessory fragments). Long corridors with only Super Elites and Elite Squads (monsters drawn from every "
         "monster in the game) and a random boss with 5 classes at the end; ~1 to 1.5 min each.\n"
         "• Infinite levels per dungeon: clearing a level unlocks the next one (harder, more rewards).\n"
         "• Each dungeon drops 3 accessories of its own; the selection screen shows the drops, levels, difficulty "
         "and rewards."),
        ("0.0.17.4",
         "• Novice and Freelancer now level up to Lv 100, like every other class, following the same pattern of "
         "level bonuses (mastery stays at Novice Lv 25 and Freelancer Lv 50). Their necklaces now unlock at Lv 100 "
         "(necklaces already unlocked are kept)."),
        ("0.0.17.3",
         "• The development stage is now called Alpha (formerly Pre-Alpha); the version numbers stay the same.\n"
         "• FAQ reviewed: gold (all the ways to earn it and the global bonus), attributes, damage, class levels, "
         "elites, boss, Endless and power-ups updated with the latest systems."),
        ("0.0.17.2",
         "• Run HUD: the run items list at the bottom left was removed (they are still in the pause screen). In its "
         "place, active power-ups show their icon with the remaining time (bar, seconds and blinking near the end)."),
        ("0.0.17.1",
         "• Accessory drop chance raised: about 1 accessory per full run on average (more with luck), similar for "
         "small and big parties.\n"
         "• Gold coins now fly to the hero on their own, like fragments.\n"
         "• Fix: cooldown reduction now also shortens the dodge (Charge / Dodge / Blink) cooldown."),
        ("0.0.17",
         "• Necklaces: one per class (30), unlocked when any character takes the class to its normal max level. "
         "The class sets the theme (ricochet, elemental imbue, summons, combo, retaliation, life steal...), but "
         "any class can wear it. Upgraded with that class's fragments.\n"
         "• The Jeweler list shows where each accessory comes from (stage or class level).\n"
         "• The chest (inventory) also shows the accessory fragments (rings, bracers, trinkets)."),
        ("0.0.16",
         "• Accessories at the Jeweler: 30 rings, 20 bracers and 20 trinkets (necklaces later). Unique account "
         "unlocks, one character at a time, 2 rings + 1 bracer + 2 trinkets per character.\n"
         "• Each Forest stage drops 2-3 of them (bosses and elites, low chance); the Endless drops those of the "
         "whole biome. The stage select shows the possible drops and marks the ones you have.\n"
         "• Duplicates become category fragments that upgrade accessories (+1 to +5, +20% values per level)."),
        ("0.0.15.1",
         "• Gold coins are pulled by the pickup range (other power-ups still need to be touched).\n"
         "• Trophy texts show the good side first, BUT then the downside.\n"
         "• Fix: the global difficulty fragment bonus now always applies: each fragment picked up is worth +10% per "
         "level (before, it was a chance of a double drop).\n"
         "• Fix: the global gold bonus now also multiplies the gold coins dropped (and the +1 Gold level-up option), "
         "not only the stage gold reward.\n"
         "• The FAQ opened from the main menu uses the same simple background as from the camp."),
        ("0.0.15",
         "• Web version (browser and phone, landscape): virtual joystick, dodge and pause buttons, big buttons on "
         "the pause and results screens, a Menu button at the camp, drag to scroll, progress saved in the browser. "
         "The PC version is unchanged.\n"
         "• build_web.py generates the web version (pygbag)."),
        ("0.0.14.1",
         "• Trophies are granted retroactively: every stage already cleared gives its boss trophy."),
        ("0.0.14",
         "• Altar of Mastery at the camp: offer class fragments to raise a class's max level by 1 for every "
         "character (cost 1, 2, 4, 8...). Extra levels give +1 main attribute and +5 HP. Each level offered raises "
         "the altar level, and each altar level gives +2.5% fragments (fragments now have decimals).\n"
         "• Blacksmith: equipment upgrades now belong to the class and are shared by every character. The screen "
         "lists every class with its weapon and helmet level. Old saves keep the highest upgrade any character "
         "had for each class."),
        ("0.0.13",
         "• Altar of Trophies at the camp, next to the portal. Each stage boss drops its trophy the first time it "
         "is defeated. Active trophies add a run modifier and +1 global difficulty level each (tougher, stronger "
         "and more enemies, but more EXP, gold and fragments). Trophies: Colossal Boar Tusk, Ancient Ent Sap, "
         "Spider Queen Silk, Shadow Wolf Fang and Corrupted Guardian Heart (2x game speed).\n"
         "• The first time a character switches to a class, the game asks whether to copy the mastery slots of the "
         "current class."),
        ("0.0.12",
         "• New stage select organized by biome: Forest (stages I to V and Endless), with Abandoned Town, "
         "Cathedral and Underground coming soon. Each stage tile shows a preview of its scenery and its boss.\n"
         "• Clearing stage V of a biome unlocks stage I of the next biome and the biome's Endless.\n"
         "• Endless mode: no time limit, difficulty and rewards go up every 2 minutes, a Super Elite or Elite Squad "
         "every minute and a rotating boss every 2 minutes. Best time saved per biome."),
        ("0.0.11",
         "• Manual dodge on SPACE (hero only), in the facing direction: Charge for STR classes (medium distance, "
         "pushes enemies, 2 uses), Dodge for AGI and balanced classes (fast long dash through enemies) and Blink "
         "for INT classes (long teleport with a 360° impact that pushes enemies). Each has its own icon with "
         "cooldown and uses next to the hotkeys.\n"
         "• The Configurations screen uses the same background as the main menu; the camp menus have a simpler "
         "background without monsters."),
        ("0.0.10",
         "• Main menu simplified: Start, Configurations and Quit (FAQ and version kept). The background cycles "
         "through every stage in random order, with all regular monsters and one of each boss.\n"
         "• New camp (central hub): a closed forest clearing with a campfire, where you walk to each function: "
         "Portal (stage select), Tent (party), Blacksmith (equipment upgrades), Chest (inventory: fragments and "
         "gold) and Jeweler (accessories, coming soon). Walk into, click or press E to open.\n"
         "• Equipment upgrades moved from the inventory to the Blacksmith; after a run you return to the camp."),
        ("0.0.9.1",
         "• The character level no longer has a maximum (class levels keep their maximum)."),
        ("0.0.9",
         "• Forest scenery: grass ground, bushes, flowers, rocks and trees that block the party's movement. Each "
         "forest has its own colors (webs in Forest III, dead trees in Forest V).\n"
         "• New enemies: Skeleton (Forest III onward) and Zombie (Forest V), with their own sprites. They can also "
         "appear as elites."),
        ("0.0.8",
         "• Every minute of the run a Super Elite (10x stronger than an elite, drops 10 fragments) or an Elite "
         "Squad (5 elites 2x stronger, 2 fragments each) appears, with a warning.\n"
         "• Stronger bosses: 3x HP, harder skills, and 2 random classes per run, carrying both weapons and using "
         "skills of both. They drop 5 fragments of each class.\n"
         "• Class screen: 'Highlight tag' dropdown that highlights the classes and the skills with the selected tag."),
        ("0.0.7",
         "• New run items: Long Reach (+10% range) and Expansion Rune (+10% area).\n"
         "• Range now controls melee reach and projectile distance; Area controls width, size and angle (thrust "
         "width, arc and cone angle, projectile size, impacts and auras).\n"
         "• New range passives (Far Reach: Archer, Lancer) and area passives (Expansion: Marauder, Dragoon).\n"
         "• When everything is upgraded, level-ups offer Roast Chicken, +1 Gold or a Random Power-up, with an option "
         "to pick automatically for the rest of the run.\n"
         "• Versioning: small adjustments now use a fourth number (0.0.7.1, 0.0.7.2 ...)."),
        ("0.0.6",
         "• Pugilist, Monk and White Monk are now AGI classes: AGI level bonuses, AGI passives (Evasion, Blunt/AoE "
         "precision), faster movement, lower HP, and Iron Body became Flowing Stance (speed and faster strikes).\n"
         "• Rogue is now a melee class: dagger basic attack (Dagger Slash), Fan of Blades spins around you, Poison "
         "Knife was replaced by Thrown Knives, and its passives focus on melee, bleed and slash.\n"
         "• Class screen: the bonus summary line was removed; the Progression table now ends with a Total row."),
        ("0.0.5",
         "• New FAQ tab: Patch notes, with a short summary of every update."),
        ("0.0.4",
         "• Gold coins added to the power-up drops: usually 1 gold, sometimes 5, rarely 10. They go straight to your "
         "gold and are kept even if the run ends in defeat.\n"
         "• The pause screen shows the gold collected in the run; the results screen shows gold from drops separately.\n"
         "• Recruiting cost doubles again for each recruit (5, 10, 20, 40 ...)."),
        ("0.0.3",
         "• Roster of up to 20 characters; the party in a run is still 5 (hero + 4 active allies), the rest wait in "
         "reserve.\n"
         "• Statuses are now a chance per hit, based on the element (Fire burns, Ice chills, Lightning stuns...) or, for "
         "physical hits, on the kind of blow: Slash and Piercing cause Bleeding, Blunt causes Stun.\n"
         "• Every physical skill now has a kind of blow; skill tooltips show the status chance.\n"
         "• Skill tags reviewed to match each skill's name and theme (melee/ranged, AoE/single target, Slash/"
         "Piercing/Blunt).\n"
         "• FAQ rewritten as lists, one item per line, with a new section about statuses.\n"
         "• Texts that were cut off now wrap or scroll (class screen, inventory, pause, loadout, results, stages).\n"
         "• Fragments tab shows all 31 classes; power-up drop rates lowered (0.2% normal, 25% elites)."),
        ("0.0.2",
         "• Capstones: the last passive of each class has a special mechanic (Execute, Detonate, Vampiric, Frenzy, "
         "Echo...). Slot 5 holds your class's capstone, slot 10 another mastered class's.\n"
         "• Skill tags, and passives redesigned around them: tag damage, crit and cooldown, % attributes, % armor, "
         "dodge, magic defense and bonuses against enemies with a status.\n"
         "• Class and skill descriptions show their tags.\n"
         "• Damage meter: new CC tab with crowd control time per type and skill.\n"
         "• Power-ups: potion, barrier, fury, crit, haste, thunder scroll and magnet, with a pin when off-screen.\n"
         "• Freelancer renamed to Novice; new evolutions Freelancer (Lv 75) and Warfarer (Lv 100).\n"
         "• Equipment upgrades also cost gold; +10 items give a permanent bonus.\n"
         "• Party limited to 5 members; a star marks mastered classes; elites are named [Class] [Monster].\n"
         "• Passives can be leveled to Lv 5 during runs; the pause bonuses list scrolls.\n"
         "• Mastery slots get Class and Tag dropdown filters."),
        ("0.0.1",
         "• First Pre-Alpha build with a version number on the title screen.\n"
         "• Language option: English / Português.\n"
         "• Inventory with party equipment: a fixed weapon and helmet per class, upgraded to +10 with class "
         "fragments and saved per class.\n"
         "• Fragments dropped by elites; the pause screen shows those collected in the run, and they are kept on "
         "death or quit.\n"
         "• Elites are more likely to be classes of your current party."),
    ]),
]

FAQ_PT = [
    ("Primeiros passos", [
        ("O que é Cat Fantasy Survivors?",
         "Um jogo de ação no estilo survivor: você move o herói e todas as habilidades disparam sozinhas.\n"
         "Sobreviva à horda por 10 minutos, derrote o chefão da fase e use o que ganhar para aumentar o seu "
         "elenco.\n"
         "Cada run é jogada por uma party de até 5 membros."),
        ("Como funcionam os saves?",
         "São 3 espaços de save (o save que você já tinha é o Save 1). No menu principal:\n"
         "• Continuar: volta para o último save usado.\n"
         "• Novo Save: cria um save do zero num espaço (um espaço que já tem progresso pede um segundo clique antes "
         "de apagar).\n"
         "• Carregar Save: mostra os 3 espaços como cards com um resumo: o herói (com a classe atual, nome e "
         "nível), a % de completude e quantas fases, acessórios, troféus e classes no Nv 100 você tem, além do "
         "maior nível da Endless Rift.\n"
         "O jogo salva sozinho (no PC: save.json, save2.json e save3.json ao lado do jogo; na versão do navegador: "
         "no próprio navegador)."),
        ("O que é o acampamento?",
         "Continuar no menu principal leva ao acampamento, o HUB central do jogo. Ande com WASD e encoste em um lugar "
         "(ou clique nele, ou aperte E / ENTER perto dele) para abrir:\n"
         "• Portal (ao norte da fogueira): seleção de fase; aperte Iniciar run nela.\n"
         "• Barraca: Montar Party (recrutar, ativar membros, trocar classe e loadout).\n"
         "• Sala de Treino (bonecos de palha, a sudeste): teste formações, builds e o seu DPS / HPS.\n"
         "Esses três já estão lá desde o início. Os outros aparecem conforme você avança (um selo NOVO! marca "
         "até você usar):\n"
         "• Baú (perto do portal): inventário com seus fragmentos e gold · depois do primeiro fragmento.\n"
         "• Ferreiro (ao lado da forja): melhorar a arma e o capacete de cada classe · depois de concluir a "
         "Floresta III.\n"
         "• Joalheiro: acessórios · depois do primeiro acessório.\n"
         "• Altar dos Troféus (a oeste do portal): ative os troféus dropados pelos chefões · depois do primeiro "
         "troféu.\n"
         "• Altar da Maestria (no oeste do acampamento): ofereça fragmentos para subir o nível máximo das classes "
         "· depois de masterizar uma classe.\n"
         "• Portal Vermelho (a leste do baú): as masmorras · depois de concluir a Floresta V.\n"
         "Cada lugar se explica na primeira vez que você usa; o botão \"?\" da tela dele mostra a explicação de "
         "novo.\n"
         "Os membros ativos descansam em volta da fogueira. ESC volta ao menu principal; depois de uma run você "
         "volta ao acampamento."),
        ("Como jogo uma run?",
         "• Mova com WASD ou as setas; as habilidades atacam sozinhas. ESPAÇO esquiva.\n"
         "• Os inimigos soltam gemas de EXP: colete-as para subir de nível durante a run e escolher uma melhoria "
         "(teclas 1-3 ou clique).\n"
         "• ESC pausa. No pause, Q encerra a run e a party mantém a EXP."),
        ("Como funciona a esquiva?",
         "Aperte ESPAÇO para esquivar na direção para onde o herói está virado. Só o herói esquiva, e o tipo "
         "depende do atributo principal da classe atual:\n"
         "• FOR - Investida (Charge): avança uma distância média e empurra (e atordoa por um instante) todo inimigo "
         "em que encostar. Recarga média (6 s), 2 usos.\n"
         "• AGI - Esquiva (Dodge): um deslocamento rápido e mais longo que atravessa os inimigos sem sofrer dano. "
         "Recarga curta (2,2 s), 1 uso.\n"
         "• INT - Blink: teleporta para longe; onde o herói aparece, um impacto empurra os inimigos próximos em "
         "360°. Recarga longa (9 s), 1 uso.\n"
         "• A redução de recarga (INT, passivas, itens e buffs de velocidade de ataque) também encurta a recarga da "
         "esquiva.\n"
         "• Classes equilibradas (Novice, Freelancer, Warfarer) usam a Esquiva.\n"
         "O ícone ao lado das hotkeys mostra a recarga e os usos restantes."),
        ("Quem eu controlo?",
         "Só o herói (contorno amarelo).\n"
         "Os outros membros agem sozinhos: seguem o herói, lutam e melhoram as habilidades automaticamente toda vez "
         "que o nível da run sobe."),
        ("Como uma run termina?",
         "• O herói cai (aliados caem e voltam, o herói não).\n"
         "• Você sai pelo pause.\n"
         "• O chefão da fase é derrotado (fase concluída)."),
    ]),
    ("Atributos e status", [
        ("O que FOR, AGI, INT e VIT fazem?",
         "Por ponto:\n"
         "• FOR: +0,1 de armadura e +0,2% de dano crítico.\n"
         "• AGI: +0,1% de esquiva e +0,1% de chance crítica.\n"
         "• INT: +0,1 de defesa mágica e +0,1% de redução de recarga.\n"
         "• VIT: +5 de vida máxima e +0,1 de regeneração a cada 5 s.\n"
         "Dano do personagem = 10 + o atributo principal da sua classe atual (FOR, AGI ou INT; Novice, Freelancer "
         "e Warfarer usam a média dos três), vezes o Ataque da role da classe (Tanque x0,5, Conjurador x1,4...). "
         "Todo ataque causa uma % dele. A cura continua crescendo com a INT da "
         "classe da habilidade de cura."),
        ("De onde vêm os atributos?",
         "• Todo personagem começa com 5 em cada atributo.\n"
         "• Cada nível do personagem dá +1 em FOR, AGI, INT e VIT.\n"
         "• Os níveis de classe dão bônus permanentes (veja Classes). Até o Lv 100 uma classe dá 18 pontos do "
         "atributo principal e 5 de cada um dos outros dois.\n"
         "• Os níveis extras de classe do Altar da Maestria dão +1 do atributo principal da classe cada.\n"
         "• Algumas passivas, equipamentos +10 e acessórios dão pontos de atributo direto."),
        ("O que são armadura, defesa mágica e esquiva?",
         "• A armadura é subtraída de todo golpe físico recebido.\n"
         "• A defesa mágica é subtraída de todo golpe mágico (mínimo 1 de dano).\n"
         "• A esquiva é a chance de ignorar totalmente um golpe físico (máx. 75%, com retorno decrescente)."),
        ("O que é retorno decrescente (softcap)?",
         "Chance crítica, esquiva e recarga ficam mais difíceis de subir conforme crescem. Cada uma tem 2 softcaps, "
         "em 1/3 e 2/3 do máximo:\n"
         "• Até o 1º softcap todo bônus vale inteiro.\n"
         "• Entre o 1º e o 2º softcap um bônus vale metade.\n"
         "• Acima do 2º softcap um bônus vale só 1/5.\n"
         "Chance crítica: softcaps em 33% e 67% (máx. 100%). Esquiva: 25% e 50% (máx. 75%). Recarga: 20% e 40% "
         "(máx. 60%).\n"
         "Dano crítico não tem softcap. Os detalhes de status mostram o total bruto ao lado do valor efetivo."),
        ("O que é Defesa (%)?",
         "Uma redução percentual de todo dano recebido, aplicada depois da armadura ou da defesa mágica.\n"
         "Vem da classe (ex.: Gladiator 15%), das passivas e de bônus como Shield Wall. Limite de 75%."),
        ("Como funcionam os críticos?",
         "Cada golpe rola a sua chance crítica (máx. 100%, com retorno decrescente).\n"
         "Um crítico causa +50% de dano mais o seu dano crítico extra (da FOR, dos níveis de classe e das "
         "passivas).\n"
         "Críticos aparecem como números amarelos com '!'."),
        ("O que é Recarga (%)?",
         "Redução de recarga: toda habilidade recarrega essa porcentagem mais rápido (máx. 60%, com retorno "
         "decrescente).\n"
         "Soma com o item Soneca e com bônus de aceleração."),
        ("Como funciona a regeneração?",
         "A regeneração aparece como vida a cada 5 segundos e é aplicada continuamente.\n"
         "Vem da VIT, dos níveis de classe, das passivas e do item Leite Morno."),
    ]),
    ("Dano e status", [
        ("Como o dano das habilidades é calculado?",
         "1. Dano do personagem (10 + atributo principal da classe atual) x a % de dano da habilidade (golpe "
         "básico: 100% por segundo de recarga).\n"
         "2. x bônus de nível na run (+25% por nível).\n"
         "3. x bônus de dano (Dano físico ou mágico %, Todo dano %, bônus de tag, equipamentos, acessórios, "
         "Erva-de-Gato, bônus temporários).\n"
         "4. Rolagem de crítico.\n"
         "5. A armadura ou defesa mágica do inimigo é subtraída (mínimo 1)."),
        ("Físico ou mágico?",
         "• Dano físico é reduzido pela armadura.\n"
         "• Dano mágico é reduzido pela defesa mágica.\n"
         "• Qualquer golpe elemental conta como mágico.\n"
         "Classes de FOR/AGI causam mais dano físico; de INT, mágico."),
        ("Que status um golpe pode causar?",
         "Todo golpe tem uma chance de causar um status, definida pelo elemento da habilidade. Golpes físicos sem "
         "elemento usam o tipo de golpe (Corte, Perfurante ou Impacto).\n"
         "• Fogo: 35% Queimando (30% do golpe por segundo durante 3 s).\n"
         "• Veneno: 50% Envenenado (40% do golpe por segundo durante 4 s).\n"
         "• Gelo: 40% Congelando (50% mais lento por 2 s).\n"
         "• Água: 30% Lento (25% mais lento por 1,5 s) e sempre empurra.\n"
         "• Vento: sem status, mas sempre empurra os inimigos com força.\n"
         "• Raio: 25% Atordoado (0,25 s).\n"
         "• Terra: 25% Atordoado / derrubado (0,4 s).\n"
         "• Sagrado: 15% Atordoado (0,3 s).\n"
         "• Som: 20% Atordoado (0,2 s).\n"
         "• Arcano: 20% Lento (30% mais lento por 1,5 s).\n"
         "• Gravidade: 30% Lento (40% mais lento por 2 s).\n"
         "• Tempo: 30% Lento (50% mais lento por 2 s).\n"
         "• Fumaça: 25% Lento (30% mais lento por 2 s).\n"
         "• Corte (espadas, machados, garras): 30% Sangrando (25% do golpe por segundo durante 3 s).\n"
         "• Perfurante (lanças, flechas, adagas): 30% Sangrando.\n"
         "• Impacto (socos, chutes, escudos, pancadas): 20% Atordoado (0,3 s).\n"
         "Habilidades que têm lentidão, atordoamento ou puxão próprios sempre aplicam o efeito. Inimigos grandes "
         "ficam atordoados por menos tempo. A dica de cada habilidade mostra a chance de status dela."),
        ("Quais status as passivas verificam?",
         "• Queimando, Envenenado, Sangrando, Congelando, Atordoado e Lento.\n"
         "• 'Qualquer debuff' conta todos eles.\n"
         "• 'Status elemental' conta Queimando, Congelando, Envenenado e Atordoado."),
        ("Como funciona a cura?",
         "Habilidades de cura recuperam (quantidade base + pontos no atributo da classe dela) x bônus de nível na "
         "run x Cura %.\n"
         "Elas miram aliados no alcance que estão sem vida cheia; cura acima da vida máxima é perdida."),
        ("O que é o medidor de dano?",
         "O painel no canto inferior direito (como o Recount do WoW). Clique na aba ou aperte TAB.\n"
         "• Dano, Recebido e Cura: passe o mouse sobre um membro para ver o detalhe por habilidade (ou por "
         "inimigo, no dano recebido).\n"
         "• CC: o controle de grupo que cada membro aplicou (Atordoar, Congelar, Derrubar, Lentidão, Gelo, "
         "Empurrão, Puxão), em segundos, e quais habilidades causaram.\n"
         "Só conta o que teve efeito: sem dano excedente e sem cura desperdiçada."),
    ]),
    ("Habilidades e loadout", [
        ("Quantas habilidades um personagem usa?",
         "7 espaços de ativas:\n"
         "• Espaço 1: o Ataque Básico fixo da arma.\n"
         "• Espaços 2-5: ativas da classe atual.\n"
         "• Espaços 6-7: espaços de maestria.\n"
         "10 espaços de passivas:\n"
         "• Espaços 1-4: passivas da classe atual; espaço 5: a Capstone dela.\n"
         "• Espaços 6-9: maestria; espaço 10: a Capstone de outra classe masterizada."),
        ("O que são os espaços de maestria?",
         "Quando uma classe chega ao nível de maestria (Lv 50, Novice Lv 25), todas as habilidades dela ficam "
         "disponíveis nos espaços de maestria de qualquer outra classe do personagem. É a base das builds "
         "híbridas.\n"
         "Uma classe masterizada mostra uma estrela ao lado do nível.\n"
         "A lista de um espaço de maestria tem dois menus suspensos, Classe e Tag:\n"
         "• Clique neles ou aperte C / T para abrir.\n"
         "• Digite uma letra para pular para um item.\n"
         "• Botão direito em um filtro limpa o filtro."),
        ("Como as habilidades são liberadas?",
         "Cada classe tem 10 ativas e 10 passivas liberadas pelo nível da classe:\n"
         "• Ativas: Lv 1, 5, 10 ... 45.\n"
         "• Passivas: Lv 3, 8, 13 ... 48.\n"
         "• O Novice libera tudo até o Lv 25.\n"
         "Veja o botão Progressão na tela de classes."),
        ("O loadout fica salvo?",
         "Sim, por personagem e por classe. Trocar de classe carrega o loadout dela.\n"
         "Habilidades novas ocupam espaços vazios sozinhas; espaços que você limpou de propósito continuam vazios.\n"
         "Na primeira vez que você troca para uma classe, o jogo pergunta se quer copiar para ela os slots de "
         "maestria da classe atual (habilidades que não couberem são ignoradas)."),
        ("Como as habilidades melhoram na run?",
         "A cada nível da run o herói melhora uma habilidade ou passiva (máx. Lv 5).\n"
         "Ativas, por nível:\n"
         "• +25% de dano ou cura, -6% de recarga e +8% de área.\n"
         "• Lv 3 e Lv 5: +1 projétil / impacto / orbe.\n"
         "• Lv 4: +1 perfuração nos projéteis e +1 invocação.\n"
         "Passivas: cada nível soma 50% do valor original (uma passiva de 6% vira 9%, 12%, 15% e 18%).\n"
         "Os aliados melhoram uma habilidade ou passiva aleatória a cada nível.\n"
         "Level ups aleatórios: na tela de level up, marque a caixa (ou aperte A) e escolha uma carta; daí em diante "
         "todo level up daquela run é escolhido ao acaso por você. Não afeta a escolha entre Banquete de Peixe / +1 Gold "
         "/ Caixa Misteriosa (essa tem a caixa própria). No pause, A desliga."),
        ("O que são os itens da run?",
         "As cartas de nível também oferecem itens para o herói (máx. Lv 5 cada, duram só a run):\n"
         "• Patinhas de Pena: +10% de velocidade.\n"
         "• Nona Vida: +20 de vida.\n"
         "• Bigodes Longos: +30% de alcance de coleta.\n"
         "• Erva-de-Gato: +12% de dano.\n"
         "• Soneca: -8% de recarga.\n"
         "• Leite Morno: +2,5 de vida/5s.\n"
         "• Garras Afiadas: +10% de alcance.\n"
         "• Novelo de Lã: +10% de área."),
        ("O que Alcance e Área fazem?",
         "• Alcance: golpes corpo a corpo chegam mais longe (raio dos arcos e cones, comprimento das estocadas) e "
         "os projéteis voam mais longe antes de sumir.\n"
         "• Área: ataques mais largos e maiores: largura das estocadas, ângulo dos arcos e cones, tamanho dos "
         "projéteis e o tamanho de impactos, auras, explosões e áreas persistentes.\n"
         "Os dois vêm dos itens da run Garras Afiadas e Novelo de Lã e de algumas passivas de classe (Far Reach: "
         "Archer, Lancer; Expansion: Thaumaturge, Black Mage, Bishop, Marauder, Dragoon)."),
        ("O que acontece quando tudo já foi melhorado?",
         "Quando o herói não tem mais habilidade, passiva ou item para melhorar, cada level up oferece:\n"
         "• Banquete de Peixe: recupera 30 de vida.\n"
         "• +1 Gold: somado ao seu gold na hora.\n"
         "• Caixa Misteriosa: um power-up aleatório é ativado na hora.\n"
         "Marque a caixa (ou aperte A) e a próxima carta escolhida vira automática em todos os próximos level ups "
         "daquela run. Ela precisa ser marcada de novo na próxima run; no pause, A desliga."),
        ("Quais são os tipos de habilidade?",
         "• Projétil, Golpe em arco, Estocada, Impacto em área, Cone.\n"
         "• Aura: dano constante ao seu redor.\n"
         "• Órbita: orbes girando ao seu redor.\n"
         "• Cura, Bônus (para a party ou para si), Invocação (aliados temporários).\n"
         "• Área persistente: dano no chão ao longo do tempo.\n"
         "Passe o mouse em qualquer ícone para ver os números exatos."),
    ]),
    ("Classes", [
        ("O que é o Altar da Maestria?",
         "O altar de cristal no oeste do acampamento. Ofereça Fragmentos de uma classe para subir em 1 o nível "
         "máximo daquela classe para TODOS os personagens (ex.: White Mage +1: o nível máximo do White Mage vira "
         "101 para todo mundo).\n"
         "• Custo em fragmentos da classe: 1, 2, 4, 8, 16, 32... (dobra a cada nível).\n"
         "• Os níveis extras dão +1 do atributo principal da classe (FOR, AGI ou INT) e +5 de vida cada, no lugar "
         "dos bônus normais. Classes equilibradas (Novice, Freelancer, Warfarer) alternam FOR, AGI e INT.\n"
         "• Como os outros níveis de classe, esses bônus são permanentes e valem em todas as classes.\n"
         "• O nível do altar é a soma de todos os níveis oferecidos. Cada nível do altar dá +2,5% de fragmentos: "
         "cada fragmento coletado vale 1 + 2,5% por nível, então os fragmentos agora têm decimais (ex.: 1,025)."),
        ("Como funciona a árvore de classes?",
         "• Todos começam como Novice.\n"
         "• O Novice Lv 10 libera as 9 classes básicas.\n"
         "• Cada classe básica no Lv 25 libera suas duas avançadas (ex.: Archer -> Bard ou Hunter; dá para treinar "
         "as duas).\n"
         "O menu suspenso 'Destacar tag' no topo (ou T) destaca as classes que têm habilidades com aquela tag, e as "
         "habilidades correspondentes nos detalhes da classe."),
        ("O que são Freelancer e Warfarer?",
         "Evoluções do Novice:\n"
         "• Freelancer (Lv máx. 100): precisa das 9 classes básicas masterizadas. Os espaços da classe também "
         "aceitam ativas e passivas das básicas masterizadas.\n"
         "• Warfarer (Lv máx. 100): precisa das 18 avançadas masterizadas. Os espaços aceitam habilidades de "
         "qualquer classe masterizada.\n"
         "A regra das capstones continua: a própria no espaço 5, a de outra classe no espaço 10."),
        ("Como funcionam os níveis de classe?",
         "Todas as classes vão até o Lv 100 (Novice e Freelancer também); o Altar da Maestria pode subir esse "
         "limite. A maestria continua no Lv 50 (Novice Lv 25).\n"
         "A EXP da run vai para o nível geral do personagem e para o nível da classe atual.\n"
         "Níveis que não liberam habilidade dão bônus permanentes de status focados no atributo principal da "
         "classe, além de VIT/vida ou regeneração a cada alguns níveis."),
        ("Os bônus de classe são permanentes?",
         "Sim. Os bônus de todos os níveis de classe que o personagem já alcançou valem em qualquer classe que ele "
         "estiver usando. Treinar várias classes deixa o personagem mais forte no geral."),
        ("O que cada classe muda além das habilidades?",
         "• Atributo principal: FOR, AGI ou INT (Novice, Freelancer e Warfarer são equilibrados).\n"
         "• Arma e ataque básico.\n"
         "• Role (Tanque, Conjurador...): Vida, Defesa, Ataque e Velocidade base, o estilo das habilidades e como "
         "ela age como aliada.\n"
         "• Corpo a corpo ou à distância.\n"
         "Tudo aparece na tela de classes."),
        ("O que são as roles?",
         "Toda classe tem uma role que define o scaling base, o foco das habilidades e como ela se move como "
         "aliada controlada pela IA:\n"
         "• Versátil / All-Rounder (Vida x1, Def x1, Atq x1, Vel x1): habilidades corpo a corpo divididas entre "
         "alvo único e área, mais uma defensiva ou de suporte. Avança nos inimigos próximos sem se afastar muito do "
         "grupo.\n"
         "• Assassino à distância (Vida x0,8, Def x0,8, Atq x1,3, Vel x1,1): à distância, mais alvo único. Mantém "
         "distância.\n"
         "• Conjurador / Caster (Vida x0,8, Def x0,8, Atq x1,4, Vel x1): mais magias em área. Mantém distância.\n"
         "• Assassino corpo a corpo (Vida x0,7, Def x0,7, Atq x1,4, Vel x1,2): alvo único corpo a corpo e "
         "controle. Persegue os alvos mais longe.\n"
         "• Suporte (Vida x1,1, Def x1,1, Atq x0,8, Vel x1): buffs no grupo, debuffs nos inimigos (Enfraquecer, "
         "lentidão, atordoar) e um pouco de cura. Fica perto do grupo.\n"
         "• Curandeiro / Healer (Vida x1, Def x1,1, Atq x0,8, Vel x1,1): curas e proteção. Fica perto, um pouco "
         "atrás.\n"
         "• Tanque (Vida x1,3, Def x1,3, Atq x0,5, Vel x0,9): área, defesa e um pouco de suporte, com uma "
         "Provocação em área. Protege os outros membros e chama a atenção dos inimigos.\n"
         "A Defesa multiplica a armadura e a defesa mágica e muda a redução de dano em 5% a cada 0,1 (Tanque: 15% "
         "menos dano recebido; Assassino corpo a corpo: 15% mais). O Ataque multiplica o dano do personagem."),
        ("O que fazem Provocar e Enfraquecer?",
         "• Provocar (Taunt): os inimigos atingidos atacam o personagem que provocou por alguns segundos "
         "(chefões: metade do tempo). Todo tanque tem ao menos uma Provocação em área.\n"
         "• Enfraquecer (Weaken): os inimigos atingidos recebem mais dano de todos por 4 segundos (ex.: +20%).\n"
         "Os dois aparecem no medidor de CC."),
    ]),
    ("Tags e passivas", [
        ("O que são as tags das habilidades?",
         "Toda ativa tem tags tiradas do que ela faz e do tema dela:\n"
         "• Alcance: Corpo a corpo, À distância.\n"
         "• Forma: Projétil, Área, Alvo único, Invocação, Cura, Bônus.\n"
         "• Tipo de dano: Físico, Mágico.\n"
         "• Elemento: Fogo, Gelo, Raio, Água, Vento, Terra, Veneno, Sagrado, Arcano, Som, Gravidade, Tempo, "
         "Fumaça.\n"
         "• Tipo de golpe: Corte, Perfurante, Impacto.\n"
         "• Efeitos: Sangramento, Dano contínuo, Atordoamento, Lentidão, Empurrão, Puxão, Teleguiado.\n"
         "As tags aparecem na dica de cada habilidade, e a tela de classes mostra as tags de cada classe."),
        ("Como as passivas usam as tags?",
         "• +% de dano para habilidades com uma tag (ex.: de Fogo).\n"
         "• +% de chance crítica para uma tag (ex.: de Projétil).\n"
         "• -% de recarga para uma tag (ex.: de Corpo a corpo).\n"
         "• Dano e chance crítica contra inimigos com um status (ex.: Sangrando).\n"
         "Outras aumentam FOR/AGI/INT/VIT em %, armadura, defesa mágica ou esquiva."),
        ("O que é uma Capstone?",
         "A 10ª passiva de cada classe (liberada no Lv 48; Novice no Lv 25): uma passiva mais forte com uma "
         "mecânica especial. Exemplos:\n"
         "• Execute: dano extra abaixo de 30% de vida.\n"
         "• Detonate: inimigos explodem ao morrer.\n"
         "• Vampiric: críticos curam.\n"
         "• Frenzy: abates acumulam dano.\n"
         "• Echo: habilidades podem recarregar na hora.\n"
         "• Legion: invocações mais fortes.\n"
         "• Anthem: dano da party. Também Thorns, Bulwark e outras.\n"
         "Só dá para equipar uma capstone da própria classe (espaço 5) e uma de outra classe masterizada "
         "(espaço 10)."),
    ]),
    ("Builds", [
        ("Que builds são possíveis?",
         "Misture uma classe com as habilidades masterizadas de outras. Exemplos:\n"
         "• Um Gladiator tanque com as curas de um White Mage masterizado.\n"
         "• Um Black Mage com o Haste do Time Mage para lançar magias sem parar.\n"
         "• Um Assassin com os atordoamentos do Rogue e as armadilhas do Hunter.\n"
         "• Um Berserker acumulando passivas de dano do Marauder e do Warrior."),
        ("Em qual atributo devo focar?",
         "No atributo principal da sua classe atual: todo o seu dano escala com ele, até o das habilidades "
         "emprestadas de outras classes.\n"
         "• FOR também dá armadura e dano crítico.\n"
         "• AGI dá esquiva e chance crítica.\n"
         "• INT dá defesa mágica e recarga.\n"
         "• VIT é bom para todos."),
        ("Como montar uma party?",
         "Uma party clássica de 5 tem:\n"
         "• Alguém na linha de frente (Gladiator, Paladin, Warrior).\n"
         "• Um curador ou suporte (Conjurer, White Mage, Scholar, Bard).\n"
         "• Causadores de dano.\n"
         "Os aliados usam o que estiver no loadout deles."),
    ]),
    ("Inimigos e spawns", [
        ("Quais inimigos existem?",
         "• Morcegos: fracos e rápidos.\n"
         "• Lobos: a partir de 0:20.\n"
         "• Javalis: lentos, resistentes e com armadura, a partir de 1:20.\n"
         "• Esqueletos (da Floresta III em diante, a partir de 0:30): rápidos para o tamanho, muita armadura, mas "
         "fracos contra magia.\n"
         "• Zumbis (Floresta V, a partir de 1:30): lentos, muita vida, batem forte e resistem a magia.\n"
         "Cada bioma tem os seus 5 inimigos com os mesmos papéis (um enxame fraco, um intermediário a partir de "
         "0:20, um forte a partir de 1:20, um novo a partir da fase III e outro novo na fase V):\n"
         "• Cidade Abandonada: Rato da Peste, Cão Sarnento, Bandido Brutamontes; Carniçal (III+, resiste um pouco a "
         "magia); Espectro (V, dano mágico, muita defesa mágica, sem armadura).\n"
         "• Catedral: Fogo-fátuo (mágico), Cultista (mágico); Gárgula (muita armadura); Armadura Viva (III+, "
         "armadura altíssima, sem defesa mágica); Serafim Caído (V, dano mágico).\n"
         "• Subterrâneo: Besouro da Caverna (enxame com casco), Goblin Minerador, Golem de Pedra (muito resistente); "
         "Gosma (III+, resiste a magia, sem armadura); Verme de Cristal (V, o mais forte).\n"
         "• Inferno: Diabrete (cospe bolas de fogo), Cão Infernal (dá o bote), Demônio Chifrudo (muito resistente, "
         "machadada); Salamandra (III+, rastro de fogo, resiste a magia); Bruxo Infernal (V, colunas do inferno, "
         "dano mágico).\n"
         "Cada fase termina com um chefão (cada bioma tem 5 chefões, um por fase)."),
        ("Como é o cenário?",
         "As florestas têm grama, arbustos, flores e pedras, que são só decoração, e árvores, que bloqueiam o "
         "movimento da party: contorne-as. Os inimigos passam por baixo das árvores. Cada run gera uma floresta "
         "diferente, e as últimas florestas são mais sombrias (teias na Floresta III, árvores secas na Floresta V).\n"
         "Os outros biomas funcionam do mesmo jeito, com obstáculos e decoração próprios, e cada fase muda um "
         "pouco:\n"
         "• Cidade Abandonada: ruas de pedra, casas em ruínas, poços e carroças (mercado na II, névoa e covas na "
         "III, cidade queimada na IV, noite com lampiões na V).\n"
         "• Catedral: piso de pedra, pilares e estátuas de anjo (tapete vermelho na I, estandartes na II, vitrais "
         "na III, cripta com caixões na IV, torre do sino roxa na V).\n"
         "• Subterrâneo: chão de rocha, estalagmites e pedregulhos (mina com trilhos na I, veios de ouro na II, "
         "gosma na III, caverna de cristal na IV, lava na V).\n"
         "• Inferno: basalto rachado com lava, espinhos de obsidiana, enxofre e pilhas de caveiras (cinzas e "
         "gaiolas na I, ossos na II, rios de magma na III, fortaleza de obsidiana com braseiros na IV, o trono do "
         "Rei Demônio com runas roxas na V)."),
        ("O que são power-ups?",
         "Drops raros: 0,2% dos inimigos comuns, 25% dos elites. Passe por cima com o herói.\n"
         "• Lata de Atum: a party recupera 20% da vida máxima.\n"
         "• Caixa de Papelão: party invulnerável por 10 s.\n"
         "• Surto Felino: +30% de dano por 10 s.\n"
         "• Ponteiro Laser: +20% de chance crítica e +50% de dano crítico por 10 s.\n"
         "• Varinha de Penas: habilidades recarregam 40% mais rápido por 10 s.\n"
         "• Chiado Feroz: atordoa todos os inimigos da tela por 3 s.\n"
         "• Saco de Petiscos: puxa todas as gemas de EXP.\n"
         "• Gold: moedas que vão direto para o seu gold (geralmente 1, às vezes 5, raramente 10). Elas voam "
         "sozinhas até o herói, como os fragmentos (os outros power-ups precisam ser tocados). Ficam salvas mesmo "
         "se a run terminar em derrota.\n"
         "Fora da tela, um pin na borda mostra o ícone, a direção e a distância. Os power-ups com duração mostram o "
         "ícone e o tempo restante no canto inferior esquerdo da tela."),
        ("Como os inimigos aparecem?",
         "• Grupos surgem logo fora da tela ao redor do herói, cada vez mais rápido e maiores (+1 inimigo por "
         "grupo a cada 45 s).\n"
         "• A cada minuto um anel de morcegos cerca a party.\n"
         "• A vida e o dano dos inimigos crescem com o tempo da run."),
        ("O que acontece aos 10:00?",
         "O tempo para e o chefão da fase aparece. Ele chama um anel de 12 morcegos a cada 12 segundos.\n"
         "• O chefão vem com 2 classes aleatórias (entre as que você liberou): carrega as duas armas e usa "
         "habilidades das duas classes.\n"
         "• Ele é 3x mais resistente que antes e as habilidades dele batem forte: fique de olho nos círculos "
         "vermelhos.\n"
         "• Ele dropa 5 Fragmentos de cada uma das duas classes, o troféu dele na primeira vez (veja Altar dos "
         "Troféus) e tem 25% de chance de dropar um acessório.\n"
         "Derrote-o para concluir a fase e liberar a próxima."),
        ("O que são Super Elites e Esquadrões de Elite?",
         "A cada minuto da run (até os 10:00) aparece um dos dois, com um alerta na tela:\n"
         "• Super Elite: um elite 10x mais forte que um comum, com anel dourado e nome maior. Dropa 10 Fragmentos "
         "da classe dele.\n"
         "• Esquadrão de Elite: 5 elites aleatórios, cada um 2x mais forte que um elite comum. Cada um dropa 2 "
         "Fragmentos da sua classe."),
        ("O que são inimigos de elite?",
         "Qualquer inimigo comum tem uma chance pequena (1,2%) de surgir como elite de uma classe que você já "
         "liberou em qualquer personagem (máx. 3 ao mesmo tempo).\n"
         "• As classes da party atual têm 3x mais chance, mas qualquer classe liberada ainda pode aparecer.\n"
         "• O nome mostra classe e monstro, ex.: Marauder Wolf.\n"
         "• Usam o chapéu da classe, têm 10x a vida, 2,5x o dano de contato e o dobro das defesas.\n"
         "• Lançam todas as habilidades da classe contra a party. Círculos vermelhos no chão mostram onde os "
         "ataques vão cair: saia deles."),
        ("O que os elites dropam?",
         "• 10x EXP.\n"
         "• Um Fragmento da classe, usado para melhorar a arma e o capacete daquela classe (veja Equipamentos) ou "
         "oferecido no Altar da Maestria (veja Classes).\n"
         "• Mais chance de power-ups.\n"
         "• Uma chance pequena de um acessório da fase (veja Equipamentos).\n"
         "Assim como a EXP, os fragmentos ficam salvos mesmo se o herói morrer ou você sair da run. O pause mostra "
         "os obtidos na run e o total do inventário."),
    ]),
    ("Fases e dificuldade", [
        ("O que é a Endless Rift?",
         "Uma fase embaixo da seleção de fase (libera ao concluir a Floresta I). Funciona como o Endless: sem limite "
         "de tempo, a dificuldade sobe um degrau a cada 2 minutos, um chefão a cada 2 minutos e um Super Elite ou "
         "Esquadrão de Elite a cada minuto. As diferenças:\n"
         "• Monstros, elites e chefões vêm de todas as fases que você já liberou, de qualquer bioma (biomas novos "
         "entram na lista quando forem liberados). A ordem em que aparecem é a mesma do Endless.\n"
         "• O cenário muda depois de cada chefão derrotado (ou quando o próximo chefão chega, se ele ainda estiver "
         "vivo): um cenário sorteado entre as fases liberadas.\n"
         "• Dificuldade base: a da fase mais alta que você já concluiu.\n"
         "• Nível da fenda (como nas masmorras): cada nível soma +30% de vida, +15% de força, +20% de resistência e "
         "+20% de recompensa. Sobreviver 10 minutos conclui o nível e libera o próximo; a cada 10 minutos o jogo "
         "pergunta se você quer ficar ou subir, e o tempo continua. A seleção começa no maior nível liberado.\n"
         "• Não dropa acessórios (por enquanto): chefões sempre dropam 1 fragmento de acessório, Super Elites 15%, "
         "elites de esquadrão 3% e outros elites 1%. Fragmentos de classe, EXP e gold funcionam como no Endless."),
        ("O que é a Sala de Treino?",
         "Os bonecos de palha do acampamento (a sudeste) levam a um campo cercado para testar formações, builds e "
         "DPS / HPS com a party ativa. Ela começa vazia: você coloca os bonecos que quiser. Nada lá dá recompensa (sem "
         "EXP, gold, fragmentos ou drops).\n"
         "• Os bonecos nunca morrem: quando a vida acaba ela enche de novo, e o medidor (canto inferior direito) "
         "conta todo o dano. \"Zerar medidor\" recomeça a contagem.\n"
         "• T (ou o botão Treino) abre o painel: adicione bonecos comuns (escolha quantos), ou um boneco Elite, "
         "Super Elite, Esquadrão de Elite ou Chefão da classe escolhida (ou aleatória).\n"
         "• Força dos bonecos: monstro base (Morcego, Lobo, Javali, Esqueleto, Zumbi: vida, armadura, defesa mágica "
         "e dano), fase e tempo da run (0:00 a 10:00), como numa run de verdade.\n"
         "• \"Os bonecos atacam\": ligado, eles perseguem, batem e usam as habilidades da classe; desligado, ficam "
         "parados. O herói não cai na Sala de Treino (levanta na hora com a vida cheia).\n"
         "• +1 / +10 level ups para testar as melhorias da run; \"Recomeçar build\" começa de novo. \"Gerenciar "
         "party\" abre a tela da party e volta para a sala; \"Voltar ao acampamento\" (ou Q no pause) sai."),
        ("O que são as masmorras?",
         "O portal vermelho do acampamento (a leste do baú) leva a 3 masmorras: Caverna, Catacumba e Masmorra.\n"
         "• Cada uma é um corredor longo: ande até o fim enfrentando o que estiver no caminho. Só aparecem Super "
         "Elites e Esquadrões de Elite, com monstros sorteados entre todos os monstros do jogo, e no fim há um "
         "chefão aleatório com 5 classes, mais forte que os chefões das fases. Uma masmorra leva cerca de 1 a 1,5 "
         "minuto.\n"
         "• Recompensa principal: Caverna = muito gold (todo elite derruba moedas, o chefão derruba muitas, mais "
         "um bônus ao concluir); Catacumba = fragmentos de classe (em dobro, mais fragmentos de classes aleatórias "
         "ao concluir); Masmorra = fragmentos de acessório (anéis, braceletes ou berloques dos Super Elites, "
         "esquadrões e chefão, mais um bônus ao concluir).\n"
         "• Depois de concluir um nível, a tela de resultado deixa ir direto para o próximo (botão ou N).\n"
         "• Cada masmorra dropa 4 acessórios próprios, um de cada tipo (mostrados na tela de seleção).\n"
         "• Níveis infinitos: concluir o nível N libera o nível N+1 daquela masmorra. Cada nível: +30% de vida, "
         "+15% de força, +20% de resistência dos inimigos e +20% de recompensas. Dá para repetir qualquer nível "
         "liberado.\n"
         "• As masmorras não dão o gold de fase nem troféus, mas dão EXP e fragmentos de classe normalmente."),
        ("O que é o Altar dos Troféus?",
         "O altar ao lado do portal no acampamento. Cada chefão de fase dropa o seu troféu na primeira vez que é "
         "derrotado (100%, uma vez só; chefões do Endless também valem; fases concluídas antes do altar existir "
         "também concedem o troféu). No altar, clique em um troféu para "
         "ativar ou desativar. Cada troféu ativo:\n"
         "• aplica o seu modificador na run;\n"
         "• soma +1 nível de dificuldade global: inimigos com +15% de vida, +10% de força e +10% de quantidade; "
         "+10% de EXP e gold; +10% de fragmentos (cada fragmento coletado vale 10% a mais). O bônus de EXP "
         "multiplica toda a EXP; o de gold multiplica o gold da fase e cada moeda dropada.\n"
         "Troféus (primeiro o lado bom, MAS depois o lado ruim):\n"
         "• Presa do Javali Colossal (Floresta I): todo inimigo tem 0,3% de chance de dropar um fragmento de "
         "classe aleatório, MAS os inimigos têm +10% de armadura e defesa mágica.\n"
         "• Seiva do Ent Ancestral (Floresta II): todo inimigo tem 1% de chance de dropar gold (1, 5 ou 10), MAS os "
         "inimigos regeneram 1% da vida máxima por segundo.\n"
         "• Seda da Rainha Aranha (Floresta III): seu alcance de coleta ganha um bônus igual ao seu bônus de "
         "velocidade, MAS os golpes de contato dos inimigos têm 25% de chance de te deixar lento (30% por 1,5 s).\n"
         "• Presa do Lobo Sombrio (Floresta IV): a party causa +20% de dano em inimigos com a vida cheia, MAS os "
         "golpes de contato dos inimigos têm 25% de chance de causar sangramento (2% da vida máxima por segundo, "
         "por 3 s).\n"
         "• Coração do Guardião Corrompido (Floresta V): as fases duram só 5 minutos (o chefão vem aos "
         "5:00), MAS nascem o dobro de monstros.\n"
         "Os outros biomas têm mais 20 troféus, todos com a mesma lógica (um bônus, MAS uma desvantagem): gold, EXP "
         "ou bônus da party (crítico, armadura, área, dano, regeneração...) em troca de inimigos mais rápidos, "
         "fortes ou numerosos, ou de uma penalidade na party. O altar mostra uma aba por bioma."),
        ("O que são os biomas?",
         "As fases são agrupadas em biomas, cada um com 5 fases (I a V) e uma versão Endless:\n"
         "• Floresta, Cidade Abandonada, Catedral, Subterrâneo e Inferno (25 fases no total).\n"
         "Concluir a fase V de um bioma libera a fase I do próximo bioma e o Endless daquele bioma. A seleção de "
         "fase (o portal do acampamento) mostra cada bioma com uma prévia das fases; uma estrela marca as fases "
         "concluídas."),
        ("Como funciona o Endless?",
         "• Sem limite de tempo: a run continua até o herói cair ou você encerrar.\n"
         "• Começa na dificuldade da fase I do bioma e, a cada 2 minutos, sobe um nível de dificuldade (+50% de "
         "vida, +30% de força, +50% de resistência dos inimigos, +25% de EXP e gold).\n"
         "• A cada minuto aparece um Super Elite ou um Esquadrão de Elite, e os inimigos novos do bioma (das fases "
         "III e V) entram conforme a dificuldade sobe.\n"
         "• A cada 2 minutos aparece um chefão, revezando entre os chefões das fases I a V e acompanhando o "
         "escalonamento. Derrotá-lo não encerra a run.\n"
         "• O gold é proporcional ao tempo sobrevivido. O seu melhor tempo em cada bioma fica salvo.\n"
         "• Pode dropar os acessórios de todas as fases do bioma."),
        ("Como as fases aumentam?",
         "Da Floresta I ao Inferno V (25 fases em sequência). Cada fase, em relação à anterior, soma:\n"
         "• +50% de vida e +30% de dano dos inimigos.\n"
         "• +50% de armadura e defesa mágica dos inimigos.\n"
         "• +25% de EXP e gold."),
        ("O que a dificuldade muda?",
         "• Fácil: 75% da vida e do ritmo de inimigos.\n"
         "• Normal: 100%.\n"
         "• Difícil: 135% de vida e 130% de ritmo.\n"
         "Mude em Configurações."),
        ("O tamanho da party muda o jogo?",
         "Sim. Mais membros significam mais inimigos e mais fortes:\n"
         "• 2 membros: x1,6 inimigos, +8% de vida.\n"
         "• 3 membros: x2,2 inimigos, +16% de vida.\n"
         "• 4 membros: x2,8 inimigos, +25% de vida.\n"
         "• 5 membros: x3,4 inimigos, +33% de vida."),
    ]),
    ("Equipamentos", [
        ("Como funcionam armadura, calça e bota?",
         "São criadas no Ferreiro (aba Armadura, Calça e Bota) com materiais que os monstros dropam.\n"
         "• Cada monstro dropa o seu material (Lobo -> Pelo de Lobo, Esqueleto -> Osso de Esqueleto...): 2% dos "
         "abates comuns, 40% dos elites (x2), Super Elites sempre (x4), e os chefões dropam 3 de cada material do "
         "bioma. Os materiais ficam mesmo se a run acabar em derrota.\n"
         "• Cada bioma tem 1 armadura, 1 calça e 1 bota (15 itens). Crie com a receita e melhore até +10 com mais "
         "dos mesmos materiais (cada nível: +12% nos valores; +10 = x2,2).\n"
         "• A armadura é defensiva, a calça mistura defesa e utilidade e a bota é só utilidade / qualidade de vida. "
         "O conjunto de cada bioma tem o mesmo orçamento de status: o do Subterrâneo não é melhor que o da Floresta, "
         "só diferente.\n"
         "• Cada item é único: só um membro da party pode usá-lo (como os acessórios), e cada membro usa 1 "
         "armadura, 1 calça e 1 bota."),
        ("Que equipamentos um personagem usa?",
         "Uma arma e um capacete da sua classe ATUAL (ex.: Adaga do Rogue e Elmo do Rogue).\n"
         "Eles são fixos: não podem ser trocados nem levados para outra classe.\n"
         "O equipamento é da CLASSE, não do personagem: todo personagem que estiver como Rogue usa a mesma Adaga "
         "do Rogue, com o mesmo nível de melhoria, não importa quem pagou."),
        ("Como melhoro?",
         "Acampamento -> Ferreiro -> escolha uma classe na lista (ela mostra todas as classes com o nível da arma e "
         "do capacete; um ponto marca as classes que alguém está usando) -> Melhorar.\n"
         "Cada melhoria custa Fragmentos daquela classe e gold:\n"
         "• +1 custa 1 fragmento e 2 de gold, +2 custa 2 e 4 ... +10 custa 10 e 20.\n"
         "• No total: 55 fragmentos e 110 de gold por item.\n"
         "O máximo é +10 e o nome mostra o nível (ex.: +3 Adaga do Rogue)."),
        ("O que as melhorias dão?",
         "• Arma: +3% de todo dano e +0,5% de chance crítica por nível.\n"
         "• Capacete: +3% de vida máxima, +1 de armadura e +1 de defesa mágica por nível.\n"
         "Valem nas runs e nos status mostrados em Montar Party."),
        ("O que acontece no +10?",
         "Um item +10 dá a TODOS os personagens um bônus PERMANENTE, válido em todas as classes.\n"
         "Arma: +5 do atributo da classe (classes equilibradas +2 de FOR, AGI e INT).\n"
         "Capacete:\n"
         "• Classes de FOR: +2 de armadura, +4% de dano crítico, +3 de VIT.\n"
         "• Classes de AGI: +1,5% de esquiva, +1,5% de chance crítica, +3 de VIT.\n"
         "• Classes de INT: +2 de defesa mágica, +1,5% de recarga, +3 de VIT.\n"
         "• Equilibradas: +1 de armadura, +1 de defesa mágica, +3 de VIT."),
        ("E quando eu troco de classe?",
         "As melhorias ficam salvas por classe e valem para todos os personagens.\n"
         "Se o capacete do Warrior está +2 e você vira Arcanist, passa a usar o capacete do Arcanist (com o nível "
         "dele). Qualquer personagem que virar Warrior usa o capacete +2."),
        ("O que são os acessórios?",
         "Itens únicos do Joalheiro (acampamento): 2 anéis, 1 bracelete, 2 berloques, 1 colar e 1 emblema por personagem. A "
         "lista do Joalheiro mostra de onde vem cada um (fase ou nível de classe).\n"
         "• Anéis (30): bônus simples: dano, chance crítica ou recarga de um tipo de dano (corte, perfurante, "
         "impacto, fogo, gelo, raio, sagrado, arcano). Os anéis gerais valem para tudo, mas são mais fracos.\n"
         "• Braceletes (23): condicionais: mais dano ou chance crítica contra inimigos queimando, congelando, "
         "envenenados, sangrando, atordoados ou lentos, e efeitos ao causar status (velocidade de ataque, dano, "
         "cura...).\n"
         "• Berloques (23): efeitos com chance: meteoros ao queimar, corrente de raios, buffs no crítico, uma fênix "
         "que te levanta uma vez por run...\n"
         "Cada acessório dropa uma vez e vira um desbloqueio da conta. Só um personagem pode usar cada um por vez: "
         "equipar em outro tira do primeiro."),
        ("Onde os acessórios dropam?",
         "Cada fase dropa 4 acessórios diferentes: sempre 1 anel, 1 bracelete, 1 berloque e 1 emblema "
         "(a seleção de fase mostra quais; uma marca indica os que você "
         "já tem). O Endless de um bioma pode dropar os acessórios de todas as fases dele. Em média, uma run "
         "completa dá cerca de 1 acessório (mais, com sorte), então leva umas 8 runs para achar os 4 de uma fase.\n"
         "• Chefões: 25% por abate. Super Elites: 5%. Elites de esquadrão: 1,2%. Outros elites: 0,5% (dividido pelo "
         "multiplicador de inimigos da party, para party maior não ganhar mais drops só por ter mais elites).\n"
         "• Cada masmorra do portal vermelho também dropa 4 acessórios próprios (1 de cada tipo).\n• Os colares não dropam: liberam pelo nível da classe.\n"
         "• Os acessórios que ainda não estão em nenhuma fase ou masmorra vão dropar nas próximas fases."),
        ("E as cópias repetidas?",
         "Uma cópia repetida vira um fragmento da categoria (Anel, Bracelete, Berloque, Emblema). No Joalheiro, os "
         "fragmentos melhoram qualquer acessório daquela categoria de +1 a +5 (custos 1, 2, 3, 4 e 5). Cada nível dá "
         "+20% nos valores do acessório (as chances não mudam)."),
        ("O que são os colares?",
         "Um colar por classe (30). Eles não dropam: cada colar é "
         "liberado quando qualquer personagem leva a classe dele ao nível máximo normal (Nv 100), e classes que já "
         "estão lá ganham na hora.\n"
         "• A classe dá o tema, mas qualquer classe pode usar. Exemplos: Archer: projéteis podem ricochetear; "
         "Spellblade: dano elemental imbui seus golpes físicos; Summoner: golpes podem evocar uma invocação do tipo "
         "do golpe; Pugilist: combo corpo a corpo; Gladiator: revida ao sofrer dano; Berserker: roubo de vida.\n"
         "• Os colares são melhorados (+1 a +5) com os fragmentos da própria classe: 5, 10, 15, 20 e 25."),
        ("O que são os emblemas?",
         "Um espaço para 1 emblema por personagem (23 emblemas). Funcionam como os braceletes, mas para a PARTY "
         "INTEIRA:\n"
         "• Os bônus fixos valem para todos os membros (ex.: Emblema das Brasas: a party causa +12% de dano em "
         "inimigos queimando; Emblema da Guarda: +3 de armadura e defesa mágica para todos).\n"
         "• Os efeitos com gatilho disparam com os golpes e abates de QUALQUER membro e dão o bônus para a party "
         "inteira (ex.: Emblema do Trovão: sempre que alguém atordoa um inimigo, a party ganha +1 em todos os "
         "atributos por 5 s, acumulando até 10x; Emblema da Guerra: cada abate dá +1% de dano para a party, até "
         "+15%).\n"
         "• Como os outros acessórios, são únicos (um personagem por vez), dropam nas fases e masmorras (um por "
         "lugar; os outros em fases futuras) e as cópias repetidas viram fragmentos de Emblema "
         "para melhorá-los.")
    ]),
    ("Party, EXP e gold", [
        ("O que é o Altar da Ganância?",
         "O gato dourado da sorte no canto inferior esquerdo do acampamento (liberado depois da Floresta IV ou com "
         "150 de gold). Ele transforma o gold sobrando em bônus permanentes para a party INTEIRA.\n"
         "• Ataque +2%, Vida máxima +3%, Alcance +2%, Área +2% e Dano crítico +4% por nível, sem limite.\n"
         "• Defesa +1%, Chance crítica +0,5%, Recarga -0,5% e Esquiva +0,5% por nível, até 10 níveis (eles têm "
         "limite).\n"
         "• O primeiro nível de qualquer atributo custa 20 de gold e cada nível DAQUELE atributo custa 40% a mais "
         "que o anterior, então espalhar o gold rende mais."),
        ("De que tamanho é a party?",
         "• Uma run é jogada por uma party de no máximo 5 membros: o herói e até 4 aliados ativos.\n"
         "• Você pode recrutar até 20 personagens no total; os que não estão ativos ficam na reserva.\n"
         "• Em Montar Party (a barraca do acampamento), selecione um membro e use Ativar / Remover para escolher quem vai para a run.\n"
         "• Só os membros ativos recebem a EXP da run."),
        ("Como funciona o recrutamento?",
         "Acampamento -> Barraca (Montar Party) -> Recrutar.\n"
         "• O primeiro recruta custa 5 de gold e cada seguinte custa o dobro (5, 10, 20, 40 ...).\n"
         "• O novo recruta entra ativo se houver vaga na party; senão, vai para a reserva."),
        ("Como mudo a aparência de um gato?",
         "Todo personagem é um gato. Um recruta novo vem com uma aparência aleatória.\n"
         "Acampamento -> Barraca (Montar Party) -> selecione o membro -> Aparência (ou A).\n"
         "• Dá para escolher cor da pelagem, padrão (liso, rajado, smoking, malhado, siamês, bicolor), cor das "
         "marcas, cor dos olhos, cauda e orelhas. Aleatório sorteia outra aparência; Desfazer volta ao que era.\n"
         "• O capacete/chapéu, a arma e a cor da túnica sempre vêm da classe atual."),
        ("Como funciona a EXP?",
         "Tudo o que é coletado na run é somado. No fim, cada membro ativo recebe o mesmo total de EXP para o nível "
         "do personagem (sem limite) e para o nível da classe atual (que continua com limite)."),
        ("O que acontece quando um aliado cai?",
         "Ele volta depois de 20 segundos com metade da vida (uma barra mostra a contagem).\n"
         "Se o herói cair, a run termina."),
        ("Como ganho gold?",
         "• Recompensa da fase: 5 de gold x a recompensa da fase (Floresta I x1, cada fase seguinte +25%). Se não "
         "concluir a fase, você ganha uma parte proporcional ao tempo sobrevivido. No Endless é proporcional ao "
         "tempo sobrevivido, com a recompensa da dificuldade atual.\n"
         "• Moedas de gold: dropadas como power-up (geralmente 1, às vezes 5, raramente 10; os elites dropam "
         "power-ups com muito mais frequência). Elas voam sozinhas até o herói e vão direto para o seu gold, mesmo "
         "se a run terminar em derrota.\n"
         "• Troféu Seiva do Ent Ancestral: todo inimigo tem 1% de chance de dropar moedas.\n"
         "• Quando tudo está melhorado, a carta +1 Gold do level up.\n"
         "• O nível de dificuldade global do Altar dos Troféus soma +10% de gold por nível: multiplica a recompensa "
         "da fase, cada moeda e a carta +1 Gold.\n"
         "O gold é gasto em recrutas (Montar Party) e melhorias de equipamento (Ferreiro). O pause mostra o gold "
         "coletado na run; a tela de resultado mostra a recompensa da fase e o gold dos drops."),
    ]),
    ("Versão e idioma", [
        ("O que significa o número da versão?",
         "A versão aparece na tela inicial.\n"
         "• Alfa: 0.0.X. Uma atualização maior (funcionalidades novas ou várias mudanças) sobe o X, ex.: 0.0.6 -> "
         "0.0.7.\n"
         "• Ajustes pequenos ganham um quarto número: 0.0.6.1, 0.0.6.2 ...\n"
         "• 0.1.X vai ser o Beta e 1.X.X o lançamento completo."),
        ("Posso jogar em português?",
         "Sim. Configurações -> Idioma alterna entre English e Português.\n"
         "Os nomes de personagens, classes e habilidades continuam em inglês."),
        ("Dá para jogar no celular (versão web)?",
         "Sim: a versão web roda no navegador, no celular (deitado) ou no PC.\n"
         "• Arraste o dedo no lado esquerdo da tela para andar (joystick virtual).\n"
         "• O botão redondo no canto inferior direito é a esquiva; o botão II no canto superior direito pausa.\n"
         "• Os toques funcionam como cliques em todos os menus; arraste para cima ou para baixo para rolar listas.\n"
         "• O pause e o resultado têm botões grandes (Continuar / Encerrar run, Voltar ao acampamento / Jogar de "
         "novo); o acampamento tem um botão Menu.\n"
         "• O progresso fica salvo no navegador (separado do save do PC).\n"
         "• Para o celular não engasgar, a versão web mantém menos inimigos na tela ao mesmo tempo."),
    ]),
    ("Editando o conteúdo", [
        ("Posso mudar habilidades e bônus das classes?",
         "Sim. A classes.xlsx (ao lado do jogo ou do .exe) tem uma aba por classe com as 10 ativas, as 10 passivas e "
         "o bônus de status de cada nível.\n"
         "O jogo lê a planilha ao abrir; se ela não existir, usa o conteúdo embutido."),
    ]),
    ("Patch notes", [
        ("0.0.31",
         "• Bioma novo: Inferno (fases I a V e Inferno Endless), liberado ao concluir o Subterrâneo V. Cinzas, rios "
         "de lava, uma fortaleza de obsidiana e o trono do Rei Demônio.\n"
         "• 5 inimigos novos (Diabrete, Cão Infernal, Demônio Chifrudo, Salamandra, Bruxo Infernal), cada um com o "
         "seu golpe, e 5 chefões (Príncipe Diabrete, Cérbero, Colosso de Magma, General Demônio, Rei Demônio).\n"
         "• 5 troféus novos, 15 acessórios novos (braceletes, berloques e emblemas) e 5 anéis que agora dropam "
         "nas fases do Inferno.\n"
         "• 5 materiais de monstro novos e 3 itens novos no Ferreiro (Couraça de Couro de Demônio, Calça de "
         "Escama de Salamandra, Botas do Cão Infernal).\n"
         "• Os monstros e chefões do Inferno também entram nas masmorras e na Endless Rift.\n"
         "• Arte: removidos os desenhos antigos que não eram mais usados (jogo mais leve). Os chapéus dos elites, "
         "as armas dos chefões e o piscar ao levar dano agora seguem a pixel art dos sprites.\n"
         "• Configurações: nova opção Limite de FPS (60, 120, 144 ou Ilimitado; o padrão agora é Ilimitado).",
         ),
        ("0.0.30",
         "• Coração do Guardião Corrompido (troféu): o jogo não roda mais 2x mais rápido. Agora as fases duram 5 "
         "minutos (o chefão vem aos 5:00, a fase avança 2x mais rápido) e nascem o dobro de monstros.\n"
         "• O sprite dos heróis ganha as cores da armadura, calça e bota do Ferreiro que estiverem equipadas.\n"
         "• Inventário: nova aba Materiais de monstros com todos os materiais, quantos você tem, quem dropa e as "
         "receitas que usam cada um.\n"
         "• Joalheiro: filtro por tag nos acessórios, como o das habilidades (as tags também aparecem na dica).\n"
         "• Português: os nomes das classes e das habilidades (ativas, passivas e descrições) agora são traduzidos.\n"
         "• Builds: o executável e os .zip (PC e web) agora se chamam CatFantasySurvivors.",
         ),
        ("0.0.29.1",
         "• Seleção de fase: removida a lista de chefões e cenários do painel da Endless Rift (ela vazava do painel "
         "com todos os biomas liberados).",
         ),
        ("0.0.29",
         "• Sprites dos inimigos repensados para combinar com o visual dos heróis (cabeça grande, corpo e patas "
         "gordinhos): Lobo, Cão Sarnento, Rato da Peste, Rei Rato, Guardião Corrompido, Besouro da Caverna, "
         "Matriarca, Verme de Cristal e Wyrm das Profundezas (agora uma serpente de cristal), Espectro (um "
         "gato-fantasma de capuz). Humanoides são gatos: o Goblin Minerador e o Rei Goblin viraram gatos-goblin "
         "verdes e o Alto Inquisidor ganhou uma cara de gato de verdade. O Golem de Vitral agora é um construto "
         "de painéis de vidro com caixilhos de chumbo e uma rosácea na cabeça. Todos os monstros, elites e chefões "
         "agora usam a mesma grade de pixels dos gatos (o pixel cresce com o tamanho do sprite), então monstros "
         "grandes e chefões têm a mesma pixel art 'gordinha' dos heróis.\n"
         "• Altar da Ganância (novo no acampamento, depois da Floresta IV ou com 150 de gold): gaste gold em bônus "
         "permanentes para a party inteira: Ataque, Defesa, Vida máxima, Alcance, Área, Chance crítica, Dano "
         "crítico, Recarga e Esquiva. Cada atributo custa 40% a mais por nível, então espalhar o gold rende mais; "
         "Defesa, Chance crítica, Recarga e Esquiva param em 10 níveis para não estourar os limites.\n"
         "• Armadura, Calça e Bota: cada monstro agora dropa o seu material (Pelo de Lobo, Osso de Esqueleto, Gel "
         "de Gosma...). No Ferreiro (aba nova), os materiais de cada bioma criam 1 armadura, 1 calça e 1 bota, que "
         "melhoram até +10. A armadura é defensiva, a calça mistura defesa e utilidade, a bota é só utilidade, e o "
         "conjunto de cada bioma tem identidade própria com o mesmo orçamento de status. Cada item é único: um "
         "membro da party por vez.\n"
         "• Wiki: tabelas novas (Armaduras, calças, botas e materiais; Altar da Ganância) e entradas no guia.",
         ),
        ("0.0.28.2",
         "• Animação de caminhada: os gatos agora andam de verdade em vez de deslizar. Em movimento, as patinhas "
         "dão passos para frente e para trás com perninhas, uma pata levanta ao passar pela outra, o corpo sobe e "
         "desce, a cauda balança e a mão da arma acompanha o passo. Os passos seguem a distância andada (mais "
         "rápido = passos mais rápidos) e param quando o personagem para. Vale para os heróis nas partidas, o "
         "herói no acampamento, os clones de sombra e os gatos da tela inicial.",
         ),
        ("0.0.28.1",
         "• Momento do acerto: toda animação agora bate com o momento do dano. Cortes, estocadas, cones, chuva "
         "de flechas e armadilhas aparecem inteiros já no primeiro quadro (o dano deles é na hora), meteoros e "
         "cometas caem durante o aviso e chegam exatamente quando o dano acontece, as auras pulsam a cada acerto "
         "e a capstone Thorns mostra uma faísca no inimigo atingido de volta. Os projéteis continuam causando "
         "dano só quando encostam no inimigo.\n"
         "• Animações dos debuffs nos inimigos e na sua party: Sangrando pinga sangue, Envenenado solta bolhas "
         "verdes, Queimando mostra chamas, Congelando brilha com gelo, Atordoado tem estrelinhas girando sobre a "
         "cabeça e Lento mostra ondinhas azuis nos pés.",
         ),
        ("0.0.28",
         "• Animações das habilidades: toda habilidade dos heróis, elites e monstros agora tem animação em pixel "
         "art de acordo com a classe e o nome: flechas, kunai, shuriken e machados girando, bolas de fogo, "
         "estilhaços de gelo, notas musicais, cortes de espada, estocadas de lança, raios mágicos, meteoros, "
         "raios caindo do céu, pilares de luz sagrada, círculos de runas, armadilhas, chuva de flechas, chão em "
         "chamas, bolhas tóxicas e mais. As invocações ganharam sprites próprios (lobo, falcão, espíritos "
         "elementais; os clones de sombra são uma cópia escura do gato).\n"
         "• Cada animação cobre exatamente a hitbox da habilidade: impactos e áreas persistentes mostram o "
         "círculo de dano, cortes e cones mostram o setor, estocadas mostram a largura da linha e os projéteis "
         "têm o tamanho do raio de acerto.\n"
         "• Curas, bônus e inimigos Provocados (!) e Enfraquecidos (seta) têm marcadores próprios. Os golpes dos "
         "monstros (sonar, bile, porretada, mergulho, bombas, luz caída...) e a poeira das investidas também são "
         "animados.\n"
         "• Itens da run renomeados com tema de gatinho e ícones novos: Erva-de-Gato (dano), Patinhas de Pena "
         "(velocidade), Nona Vida (vida), Bigodes Longos (alcance de coleta), Soneca (recarga), Leite Morno "
         "(regeneração), Garras Afiadas (alcance), Novelo de Lã (área), Banquete de Peixe (cura) e Caixa "
         "Misteriosa (power-up aleatório). Power-ups: Lata de Atum, Caixa de Papelão, Surto Felino, Ponteiro "
         "Laser, Varinha de Penas, Chiado Feroz e Saco de Petiscos.",
         ),
        ("0.0.27.2",
         "• Tela inicial: no lugar dos monstros, gatinhos de todas as classes com aparência aleatória passeiam no "
         "fundo.",
         ),
        ("0.0.27.1",
         "• Removidos os multiplicadores de Vida, Defesa (%) e Velocidade de cada classe: Vida, Defesa, Ataque e "
         "Velocidade base agora vêm só da role da classe (aba Index da classes.xlsx). As abas das classes não têm "
         "mais essas linhas.\n"
         "• Texto novo da role Versátil (All-Rounder).",
         ),
        ("0.0.27",
         "• Roles: toda classe agora tem uma role (Versátil, Assassino à distância, Conjurador, Assassino corpo a "
         "corpo, Suporte, Curandeiro ou Tanque) que define a Vida, Defesa, Ataque e Velocidade base e como ela age "
         "como aliada controlada pela IA. Conjuradores e Assassinos à distância mantêm distância, Suportes e "
         "Curandeiros ficam perto do grupo, Assassinos corpo a corpo perseguem os alvos mais longe e Tanques vão "
         "atrás dos inimigos perto dos outros membros e chamam mais aggro. A role de cada classe e os "
         "multiplicadores ficam na aba Index da classes.xlsx.\n"
         "• As habilidades ativas de todas as classes foram refeitas em torno da role, mantendo a identidade de "
         "cada classe: Versáteis misturam golpes em alvo único e em área com uma habilidade de suporte; Assassinos "
         "à distância focam em tiros em alvo único; Conjuradores em magias em área; Assassinos corpo a corpo em "
         "golpes em alvo único e atordoamento; Suportes em buffs no grupo, debuffs nos inimigos e um pouco de "
         "cura; Curandeiros em curas e proteção; Tanques em área, defesa e suporte, cada um com ao menos uma "
         "Provocação em área.\n"
         "• Efeitos novos: Provocar (os inimigos atingidos atacam quem provocou) e Enfraquecer (os inimigos "
         "atingidos recebem mais dano por 4 s). Os dois aparecem nas dicas das habilidades e no medidor de CC.\n"
         "• Tela de classes: mostra a role e os multiplicadores (passe o mouse para ver o comportamento). Wiki: "
         "tabela nova de Roles, coluna Role em Classes e entradas novas no guia.\n"
         "• Os loadouts salvos mantêm os slots, mas as habilidades neles são as novas.",
         ),
        ("0.0.26",
         "• Monstros: cada monstro agora tem comportamento próprio e um golpe exclusivo. Morcegos ficam por perto "
         "e usam um sonar em cone que deixa lento; lobos aceleram perto da presa e mordem causando Sangramento; "
         "javalis dão investida (Atordoamento + empurrão); esqueletos arremessam ossos; zumbis cospem poças de "
         "bile que deixam lento; ratos andam em zigue-zague com mordida da peste; cães saltam no alvo; brutos "
         "batem com o porrete (Atordoamento); carniçais entram em frenesi quando feridos; espectros piscam e "
         "lamentam (onda que deixa lento); fogos-fátuos explodem; cultistas mantêm distância e lançam raios "
         "sombrios; gárgulas mergulham; armaduras vivas estocam com a lança; serafins golpeiam dois alvos "
         "(Atordoamento); besouros rolam; goblins jogam bombas; golens dão pancada no chão (Atordoamento); gosmas "
         "deixam um rastro que deixa lento; vermes irrompem embaixo de você. Todo ataque mostra uma área de aviso "
         "antes de acertar.\n"
         "• Elites mantêm o golpe exclusivo do monstro além das habilidades de classe. Chefes não mudaram.\n"
         "• Novos efeitos no seu grupo: Atordoado (com imunidade curta depois), Lento, Sangramento e empurrão.\n"
         "• Wiki: a tabela de Inimigos ganhou a coluna \"Golpe exclusivo\".\n"
         "• Mortes: uma nuvenzinha de poeira cobre o inimigo derrotado, que fica no chão por um instante com "
         "olhos em X e depois some.\n"
         "• As dicas das habilidades mostram a % de dano e, entre parênteses, o dano com os status atuais do "
         "personagem (ex.: Dano: 90% (14)).",
         ),
        ("0.0.25.1",
         "• Escala de dano: o dano do personagem agora é 10 + o atributo principal da sua classe atual (FOR, AGI "
         "ou INT), no lugar de FOR + AGI + INT. Novice, Freelancer e Warfarer usam a média dos três. As "
         "porcentagens das habilidades não mudaram (golpe básico 100% por segundo de recarga), e o dano em níveis "
         "altos voltou para a faixa de antes."),
        ("0.0.25",
         "• Passe de tuning das habilidades. O dano do personagem agora é FOR + AGI + INT, e todo ataque causa "
         "uma % dele (a dica da habilidade e a Wiki mostram a %).\n"
         "• Golpe básico: 100% por segundo de recarga. Armas leves (adagas, garras, punhos) batem mais rápido e "
         "mais fraco; armas pesadas e de duas mãos (lanças, espadas longas, machados, Machado de duas mãos "
         "1,6 s) batem mais devagar e mais forte, com o mesmo dano por segundo.\n"
         "• Ativas: o dano por uso cresce com a recarga (uma habilidade de 5 s bate bem mais forte que uma de "
         "3 s). Área, vários alvos, perfurar, explosão, teleguiado, atordoar, lentidão, empurrão e efeitos "
         "elementais deixam a habilidade um pouco mais fraca do que um golpe de dano puro em um alvo. Áreas "
         "persistentes causam % por segundo, auras % por pulso, órbitas e invocações % por toque.\n"
         "• Curas e bônus não mudaram. Em níveis altos o dano fica maior que antes, porque os três atributos "
         "contam agora."),
        ("0.0.24.7",
         "• As 3 masmorras do Portal Vermelho foram redesenhadas em pixel art com o mesmo nível de detalhe:\n"
         "• Caverna: chão de rocha úmida em placas com fendas, poças, pedrinhas e minério; paredes de rocha em "
         "camadas com cristais, estalactites (e estalagmites) e veios de ouro; cristais e cogumelos que brilham no "
         "chão.\n"
         "• Catacumba: lajes claras com cera, lascas de osso e caveiras entalhadas; parede de ossuário com "
         "caveiras de gato e ossos empilhados; nichos em arco com caveiras, velas sobre crânios com chamas "
         "tremulando e corpos enrolados em túmulos na parede; ossos e velas no chão.\n"
         "• Masmorra (prisão): lajes escuras irregulares com musgo, manchas de umidade e palha; blocos de pedra "
         "grandes nas paredes com escorrido de umidade; tochas com chama animada, correntes com algemas e celas "
         "com grades e olhos piscando no escuro; montes de palha, baldes e correntes soltas no chão.\n"
         "• As paredes fazem sombra no chão, o portão do chefão é um arco de pedra com runas acesas e as prévias "
         "das masmorras não ficam mais borradas."),
        ("0.0.24.6",
         "• O nível de detalhe da Catedral agora vale para todas as fases:\n"
         "• Floresta: árvores com raízes, casca e copa em tufos de folhas com luz e sombra; árvores secas "
         "retorcidas com galhos bifurcados e musgo pendurado (Floresta V); arbustos com frutinhas, flores com "
         "pétalas, pedras com musgo, e cogumelos, tocos e troncos caídos novos.\n"
         "• Cidade Abandonada: poço de tijolos com telhadinho de tábuas, manivela, corda e balde; carroças com "
         "rodas de raios (uma quebrada), sacos e caixotes, ou toldo listrado de feira com frutas; túmulos com cruz "
         "entalhada, epitáfio, monte de terra, flores e vela; caixotes de tábuas, barris de aduelas, entulho de "
         "tijolos, sacos de grãos, cestos de frutas, ossos de gato, brasas nas cinzas e postes de lampião.\n"
         "• Subterrâneo: estalagmites em camadas com faixas minerais, escoras de mina com pregos, mãos-francesas, "
         "lanterna acesa e trilho; poços de lava com crosta e bolhas; pedrinhas angulosas, poças com reflexo, "
         "cogumelos que brilham, cristais facetados, trilhos com dormentes, carrinhos de mina tombados, pepitas de "
         "ouro e ossos derretidos."),
        ("0.0.24.5",
         "• Objetos da Catedral redesenhados com muito mais detalhe: colunas góticas (base em degraus, feixe de "
         "colunas com luz e sombra, blocos de pedra, capitel entalhado, hera e trincas), colunas quebradas com "
         "pedaços caídos, estátuas de anjo-gato rezando (capuz com orelhas, asas dobradas, dobras do manto, "
         "auréola, placa de bronze, musgo) e sarcófagos de pedra com um cavaleiro-gato entalhado e a tampa "
         "entreaberta.\n"
         "• Novos na Catedral: candelabros de ferro com três velas acesas e bancos de igreja de madeira.\n"
         "• Detalhes do chão melhores: velas com cera escorrendo, entulho de blocos angulosos e caveiras de gato "
         "com ossos."),
        ("0.0.24.4",
         "• Acampamento: corrigido o chão aparecendo em quadrados separados (o ladrilho maior estava sendo "
         "desenhado por cima dele mesmo). A clareira de terra em volta da fogueira e a trilha até o portal agora "
         "são pixel art com a borda pontilhada.\n"
         "• Sala de Treino: chão novo em pixel art (terra batida com palha e grama em volta da cerca)."),
        ("0.0.24.3",
         "• Cenários redesenhados em pixel art na Cidade Abandonada, na Catedral e no Subterrâneo, no mesmo estilo "
         "da Floresta: paralelepípedos arredondados com luz e sombra, terra entre as pedras, musgo, mato e poças; "
         "piso gótico em losangos claros e escuros com bisel, desgaste, trincas, lajes quebradas, cera de vela e "
         "rosáceas de pedra; chão de caverna em placas de rocha separadas por fendas (fendas de lava acesas no "
         "Subterrâneo V), pedrinhas e pontos de minério.\n"
         "• Os ladrilhos do chão ficaram com o dobro do tamanho, então o padrão não se repete mais na tela.\n"
         "• Casas novas (enxaimel, telhado de telhas, chaminé, venezianas e porta de tábuas), rochedos angulosos, "
         "cristais facetados, luz dos vitrais no chão e tapetes gastos com franjas."),
        ("0.0.24.2",
         "• Monstros e chefões perderam o corpo de \"bolinha\" do visual antigo e ganharam silhuetas de verdade: "
         "lobos, cães, javalis, ratos e o Guardião Corrompido (agora um cervo corrompido) vistos de lado com quatro "
         "patas; morcegos com asas de membrana; o Ent como uma árvore que anda; a Rainha Aranha com abdômen e patas "
         "articuladas; gárgulas agachadas; besouros compridos; goblins e golems com corpo, braços e pernas; vermes "
         "com gomos afinando. O povo-gato (bandidos, zumbi, carniçal, cavaleiros, serafins) agora tem tronco, "
         "pernas e roupa.\n"
         "• Acampamento: a Barraca (lona listrada, abas abertas com lanterna dentro, cordas, tapete e caixotes), a "
         "Forja (base de pedra, enxaimel, telhado de tábuas, chaminé com faíscas, fornalha de tijolos, fole, "
         "suporte de armas, barril e placa), o Portal das fases (arco de pedra talhada com runas acesas, pilares, "
         "degraus, cristal na pedra-chave, redemoinho em espiral e pedras flutuando) e o Portal Vermelho "
         "(monólitos de obsidiana, rachaduras em brasa e fagulhas) foram redesenhados com muito mais detalhe."),
        ("0.0.24.1",
         "• Os inimigos humanoides agora são gatos: Esqueleto, Zumbi, Bandido Brutamontes, Carniçal, Espectro, Cultista, "
         "Armadura Viva, Serafim Caído e os chefões Lorde Bandido, Médico da Peste, Cavaleiro Sem Cabeça, Prefeito "
         "Oco, Alto Inquisidor, Bispo de Ossos e Arcanjo Caído ganharam orelhas, focinho e bigodes, olhos de gato "
         "e cauda. Animais e monstros (morcegos, lobos, aranhas, gárgulas, gosmas, goblins...) continuam como "
         "eram."),
        ("0.0.24",
         "• Nome novo: Cat Fantasy Survivors.\n"
         "• Visual novo em pixel art no jogo inteiro, mais escuro e gótico (inspirado em Blasphemous, Last Faith e "
         "Chasm): fonte pixelada, mundo desenhado em blocos de 2x2 pixels com contorno escuro e luz/sombra em "
         "todos os sprites, chão com textura em pixel, acabamento de cor com vinheta e cantos em degraus na "
         "interface.\n"
         "• Todos os ícones (habilidades, passivas, classes, itens, acessórios, troféus, power-ups e equipamentos) "
         "foram redesenhados em pixel art: grade pequena, poucas cores, contorno de 1 pixel e moldura chanfrada. "
         "Os anéis agora parecem anéis.\n"
         "• Os heróis são gatos! Todo personagem é um gato usando o capacete/chapéu e a arma da classe, com a "
         "túnica na cor da classe.\n"
         "• Aparência dos gatos: recrutas vêm com aparência aleatória, e Montar Party tem o botão Aparência (A) "
         "para personalizar cor da pelagem, padrão, cor das marcas, olhos, cauda e orelhas. Os personagens que "
         "você já tinha mantêm a aparência de antes.\n"
         "• O Ferreiro e o Joalheiro do acampamento também são gatos."),
        ("0.0.23.4",
         "• Menos passivas repetidas: nenhum efeito de passiva aparece em mais de 3 classes agora. Melee Haste, "
         "Exploit Stunned, Melee Mastery, Exploit Bleeding/Burning/Slowed/Any Debuff, Heal Haste, Melee/Fire/AoE "
         "Precision, Holy Mastery, Benevolence, Expansion e as passivas de dano repetidas foram trocadas em algumas "
         "classes por outras tags ou passivas novas (ex.: Pressure Points, Hamstring, Shield Bash, Exploit "
         "Elemental, Ravager).\n"
         "• Balanceamento das passivas: toda passiva agora vale o mesmo orçamento. Uma passiva com 2 efeitos dá "
         "menos de cada um do que a passiva só daquele efeito (ex.: Fortitude: +15% de armadura; Iron Shirt: +9% "
         "de armadura e +1,5 de vida/5s). Dano de tag ampla (corpo a corpo, à distância, projétil, área, alvo "
         "único, físico, mágico) é +10%; de tag específica (fogo, sagrado, sangramento, empurrão...) +12%. Vários "
         "valores mudaram um pouco."),
        ("0.0.23.3",
         "• Passivas defensivas sem repetição: agora existe só uma de cada: Fortitude (Lancer), Evasion (Archer), "
         "Warding (Thaumaturge) e Endurance (Novice). As outras classes ganharam 26 passivas novas no lugar (ex.: "
         "Iron Shirt, Camouflage, Divine Bulwark, Pain Tolerance).\n"
         "• Buff Haste (recarga das habilidades de buff) ficou só no Bard e no Time Mage. Arcanist, Templar, "
         "Gladiator e Warrior agora têm uma passiva de duração de buff no lugar (+15% de duração das habilidades "
         "de buff).\n"
         "• Novo efeito de passiva: duração de buff (buffdur na classes.xlsx)."),
        ("0.0.23.2",
         "• Níveis de classe: até o Lv 100 cada classe agora dá 18 pontos do atributo principal e 5 de cada um dos "
         "outros dois (antes eram 28 e 0). O total é o mesmo.\n"
         "• Retorno decrescente: chance crítica, esquiva e recarga agora têm 2 softcaps, em 1/3 e 2/3 do máximo. "
         "Acima do 1º um bônus vale metade, acima do 2º só 1/5 (crítico 33%/67%, esquiva 25%/50%, recarga "
         "20%/40%). O dano crítico não mudou. Veja a Wiki.\n"
         "• Passivas menos repetidas: agora só existe uma passiva de % de atributo de cada tipo: STR Training "
         "(Lancer), AGI Training (Archer), INT Training (Thaumaturge), e Versatile Training e Vitality (Novice). "
         "As outras classes ganharam 55 passivas novas no lugar (ex.: Pyromania, Shadowstep, Lay on Hands, Second "
         "Wind)."),
        ("0.0.23.1",
         "• Tempo dos buffs: ao lado dos power-ups (canto inferior esquerdo) a run agora mostra também os buffs "
         "de habilidades e acessórios. Power-ups são ícones quadrados com moldura dourada e barra; buffs são "
         "ícones redondos com um anel que esvazia com o tempo (azul = habilidade, roxo = acessório, verde = "
         "passiva). Passe o mouse para ver o nome e o efeito.\n"
         "• Chefões: sem círculo vermelho neles. As áreas que o chefão acerta ao redor de si agora são desenhadas "
         "por baixo dele, na cor da habilidade, e o chefão continua visível.\n"
         "• Acampamento: o contador de gold saiu da tela do acampamento; o gold aparece no Baú (inventário)."),
        ("0.0.23",
         "• Experiência de novo jogador: um save novo começa só com o Portal, a Barraca e a Sala de Treino no "
         "acampamento. Os outros lugares aparecem conforme você avança (Baú: primeiro fragmento · Ferreiro: "
         "Floresta III · Joalheiro: primeiro acessório · Altar dos Troféus: primeiro troféu · Altar da Maestria: "
         "primeira classe masterizada · Portal Vermelho: Floresta V), com um selo NOVO! e um aviso.\n"
         "• Explicações: uma pop-up de boas-vindas num save novo e uma pop-up na primeira vez que você usa cada "
         "mecânica (seleção de fase, Endless, Endless Rift, primeira run, party, classes, loadout, Sala de "
         "Treino, baú, ferreiro, joalheiro, altares e masmorras). Toda tela dessas tem um botão \"?\" para ver "
         "de novo. Saves de antes desta atualização continuam com tudo liberado e sem as pop-ups.\n"
         "• O FAQ agora é a Wiki, com duas abas: Guia (o antigo FAQ) e Database: tabelas com ícone de todas as "
         "classes (como liberar), habilidades e passivas (classe e nível em que liberam), acessórios (efeito e como "
         "obter), troféus, fases e masmorras (chefão, inimigos, drops), inimigos (atributos), power-ups, itens da "
         "run, elementos, status e tags, montadas a partir dos dados do jogo. Uma barra de pesquisa (clique nela ou "
         "aperte /) procura nas duas abas.\n"
         "• Loadout: os espaços de ativas e passivas da própria classe agora também têm filtro por tag (T), não "
         "só os de maestria."),
        ("0.0.22.2",
         "• Acampamento: o sprite do Altar dos Troféus agora mostra as mesmas 4 bolinhas dos biomas (enchem "
         "conforme os troféus de cada bioma são ativados) no lugar de um pontinho por troféu, que não cabiam mais."),
        ("0.0.22.1",
         "• Altar dos Troféus: as abas dos biomas não têm mais ícones vazando; cada aba tem uma bolinha na cor do "
         "bioma que vai enchendo conforme os troféus daquele bioma são ativados."),
        ("0.0.22",
         "• Biomas novos: Cidade Abandonada, Catedral e Subterrâneo, 5 fases cada (20 fases no total), cada um com "
         "cenário próprio (com pequenas mudanças de fase para fase, como as florestas), 5 inimigos novos e 5 "
         "chefões com sprites próprios. Mesma lógica da floresta: 3 inimigos nas fases I e II, um novo a partir da "
         "fase III e outro novo na fase V; a dificuldade continua subindo fase após fase; cada bioma tem o seu "
         "Endless.\n"
         "• Cidade Abandonada: Rato da Peste, Cão Sarnento, Bandido Brutamontes, Carniçal, Espectro · chefões Rei "
         "Rato, Lorde Bandido, Médico da Peste, Cavaleiro Sem Cabeça, Prefeito Oco.\n"
         "• Catedral: Fogo-fátuo, Cultista, Gárgula, Armadura Viva, Serafim Caído · chefões Grande Gárgula, Alto "
         "Inquisidor, Golem de Vitral, Bispo de Ossos, Arcanjo Caído.\n"
         "• Subterrâneo: Besouro da Caverna, Goblin Minerador, Golem de Pedra, Gosma, Verme de Cristal · chefões "
         "Matriarca, Rei Goblin, Titã de Gosma, Golem de Cristal, Wyrm das Profundezas.\n"
         "• 15 troféus novos (um por chefão novo), sempre com uma troca; o Altar dos Troféus agora tem uma aba por "
         "bioma.\n"
         "• Drops de acessório em todas as fases novas (1 anel, 1 bracelete, 1 berloque, 1 emblema), usando os "
         "acessórios que ainda não tinham fonte, mais 9 novos: Braceletes do Baluarte, do Ceifador e da Toxina; "
         "Lanterna Fantasma, Incensário Sagrado e Geodo de Cristal; Emblemas da Ruína, do Buscador e das "
         "Profundezas.\n"
         "• As masmorras e a Endless Rift agora usam os monstros de todas as fases liberadas.\n"
         "• Saves: Continuar, Novo Save e Carregar Save no menu principal, 3 espaços com um card de resumo cada.\n"
         "• Tela de seleção de classe: o texto \"Classe atual\" saiu (a classe já fica destacada na árvore)."),
        ("0.0.21.1",
         "• Tela de seleção de classe: novo botão Voltar (canto superior direito), como nas outras telas (o ESC "
         "continua funcionando)."),
        ("0.0.21",
         "• Nova fase: Endless Rift (embaixo da seleção de fase, libera ao concluir a Floresta I). Como o Endless, "
         "mas com monstros, elites e chefões de todas as fases liberadas, um cenário liberado sorteado depois de "
         "cada chefão e a dificuldade base da fase mais alta que você já concluiu.\n"
         "• Níveis da fenda (como nas masmorras): sobreviver 10 minutos conclui o nível e libera o próximo; a cada "
         "10 minutos você escolhe ficar ou subir, e o tempo continua.\n"
         "• Sem acessórios na fenda (por enquanto): elites e chefões dropam fragmentos de acessório direto."),
        ("0.0.20.1",
         "• Sala de Treino: agora começa vazia; coloque os bonecos que quiser pelo painel (T). Ao voltar do "
         "\"Gerenciar party\" ou usar \"Recomeçar build\", os mesmos bonecos são colocados de novo."),
        ("0.0.20",
         "• Novo: Sala de Treino. Os bonecos de palha do acampamento levam a um campo cercado para testar formações, "
         "builds e DPS / HPS. Os bonecos nunca morrem; adicione comuns (escolha quantos) ou bonecos Elite, Super "
         "Elite, Esquadrão de Elite e Chefão de qualquer classe, escolha a força (monstro base, fase, tempo da run) "
         "e se eles atacam. Também: zerar medidor, +1 / +10 level ups, recomeçar build, gerenciar party e voltar ao "
         "acampamento (painel: T).\n"
         "• Novos sprites de bonecos de treino de palha."),
        ("0.0.19.3",
         "• Os colares voltam a ser liberados só levando a classe ao Nv 100 (não dropam mais). Cada fase e masmorra "
         "agora dropa 4 acessórios: 1 anel, 1 bracelete, 1 berloque e 1 emblema.\n"
         "• Os chefões não têm mais os círculos coloridos em volta (atrapalhavam a visão da luta).\n"
         "• Masmorra concluída: a tela de resultado tem o botão \"Ir para o próximo nível\" (ou N), que já começa o "
         "próximo nível com a mesma party."),
        ("0.0.19.2",
         "• Nova opção no level up: marque \"Escolher ao acaso os próximos level ups desta run\" (ou aperte A) e todos "
         "os próximos level ups da run são escolhidos ao acaso automaticamente. Não afeta a escolha entre Frango "
         "Assado / +1 Gold / Power-up Aleatório. No pause, A desliga.\n"
         "• Correção: o Joalheiro travava ao mostrar a origem dos colares que dropam numa masmorra."),
        ("0.0.19.1",
         "• Drops de acessório reorganizados: toda fase e toda masmorra agora dropa exatamente 1 anel, 1 bracelete, "
         "1 berloque, 1 colar e 1 emblema. Os colares agora também podem dropar (continuam liberando no Nv 100 da "
         "classe); um colar repetido vira 5 fragmentos da classe dele.\n"
         "• Seleção de fase: os drops de acessório quebram em mais linhas (o painel do Endless não vaza mais) e "
         "mostram quantos você já achou. Os cartões das masmorras mostram os 5 drops como ícones.\n"
         "• Seleção de masmorra: o nível sempre começa no mais alto liberado; textos mais curtos."),
        ("0.0.19",
         "• Novo espaço de acessório: Emblema (1 por personagem, 20 emblemas). Como os braceletes, mas para a party "
         "inteira: os bônus fixos valem para todos e os efeitos com gatilho disparam com os golpes e abates de "
         "qualquer membro (ex.: Emblema do Trovão: atordoar dá à party +1 em todos os atributos por 5 s, acumulando "
         "até 10x).\n"
         "• Cada fase da Floresta também dropa um emblema (Sangue, Misericórdia, Estilhaço, Guerra, Brasas); os outros "
         "vêm em fases futuras. Cópias repetidas viram fragmentos de Emblema; a Masmorra também pode dar."),
        ("0.0.18",
         "• Portal Vermelho no acampamento com 3 masmorras: Caverna (muito gold), Catacumba (fragmentos de classe) e "
         "Masmorra (fragmentos de acessório). Corredores longos só com Super Elites e Esquadrões de Elite (monstros "
         "sorteados entre todos os do jogo) e um chefão aleatório com 5 classes no fim; ~1 a 1,5 min cada.\n"
         "• Níveis infinitos em cada masmorra: concluir um nível libera o próximo (mais difícil, mais recompensa).\n"
         "• Cada masmorra dropa 3 acessórios próprios; a tela de seleção mostra os drops, níveis, dificuldade e "
         "recompensas."),
        ("0.0.17.4",
         "• Novice e Freelancer agora vão até o Lv 100, como as outras classes, seguindo o mesmo padrão de bônus por "
         "nível (a maestria continua no Novice Lv 25 e no Freelancer Lv 50). Os colares deles agora liberam no Lv 100 "
         "(colares já liberados continuam)."),
        ("0.0.17.3",
         "• A fase de desenvolvimento agora se chama Alfa (antes Pré-Alfa); a numeração das versões continua a mesma.\n"
         "• FAQ revisado: gold (todas as formas de ganhar e o bônus global), atributos, dano, níveis de classe, "
         "elites, chefão, Endless e power-ups atualizados com os sistemas mais recentes."),
        ("0.0.17.2",
         "• HUD da run: a lista de itens da run no canto inferior esquerdo saiu (eles continuam no pause). No lugar, "
         "os power-ups ativos mostram o ícone com o tempo restante (barra, segundos e piscando perto do fim)."),
        ("0.0.17.1",
         "• Chance de drop de acessórios aumentada: em média cerca de 1 acessório por run completa (mais, com sorte), "
         "parecido para party pequena ou grande.\n"
         "• As moedas de gold agora voam sozinhas até o herói, como os fragmentos.\n"
         "• Correção: a redução de recarga agora também encurta a recarga da esquiva (Investida / Esquiva / Blink)."),
        ("0.0.17",
         "• Colares: um por classe (30), liberados quando algum personagem leva a classe ao nível máximo normal. A "
         "classe dá o tema (ricochete, imbuir elemento, invocações, combo, revide, roubo de vida...), mas qualquer "
         "classe pode usar. Melhorados com os fragmentos da classe.\n"
         "• A lista do Joalheiro mostra de onde vem cada acessório (fase ou nível de classe).\n"
         "• O baú (inventário) também mostra os fragmentos de acessório (anéis, braceletes, berloques)."),
        ("0.0.16",
         "• Acessórios no Joalheiro: 30 anéis, 20 braceletes e 20 berloques (colares depois). Desbloqueios únicos "
         "da conta, um personagem por vez, 2 anéis + 1 bracelete + 2 berloques por personagem.\n"
         "• Cada fase da Floresta dropa 2-3 deles (chefões e elites, chance baixa); o Endless dropa os do bioma "
         "todo. A seleção de fase mostra os drops possíveis e marca os que você já tem.\n"
         "• Cópias repetidas viram fragmentos da categoria que melhoram os acessórios (+1 a +5, +20% nos valores "
         "por nível)."),
        ("0.0.15.1",
         "• As moedas de gold são puxadas pelo alcance de coleta (os outros power-ups ainda precisam ser tocados).\n"
         "• Os textos dos troféus mostram primeiro o lado bom, MAS depois o lado ruim.\n"
         "• Correção: o bônus de fragmentos da dificuldade global agora sempre vale: cada fragmento coletado vale "
         "+10% por nível (antes era uma chance de cair em dobro).\n"
         "• Correção: o bônus de gold da dificuldade global agora também multiplica as moedas dropadas (e a opção "
         "+1 Gold do level up), não só o gold da fase.\n"
         "• O FAQ aberto pelo menu principal usa o mesmo fundo simples do acampamento."),
        ("0.0.15",
         "• Versão web (navegador e celular, deitado): joystick virtual, botões de esquiva e pause, botões grandes "
         "no pause e no resultado, botão Menu no acampamento, arrastar para rolar, progresso salvo no navegador. "
         "A versão de PC não muda.\n"
         "• build_web.py gera a versão web (pygbag)."),
        ("0.0.14.1",
         "• Troféus retroativos: toda fase já concluída concede o troféu do seu chefão."),
        ("0.0.14",
         "• Altar da Maestria no acampamento: ofereça fragmentos de classe para subir em 1 o nível máximo da "
         "classe para todos os personagens (custo 1, 2, 4, 8...). Os níveis extras dão +1 do atributo principal e "
         "+5 de vida. Cada nível oferecido sobe o nível do altar, e cada nível do altar dá +2,5% de fragmentos (os "
         "fragmentos agora têm decimais).\n"
         "• Ferreiro: as melhorias de equipamento agora são da classe e valem para todos os personagens. A tela "
         "lista todas as classes com o nível da arma e do capacete. Saves antigos ficam com a maior melhoria que "
         "algum personagem tinha em cada classe."),
        ("0.0.13",
         "• Altar dos Troféus no acampamento, ao lado do portal. Cada chefão de fase dropa o seu troféu na primeira "
         "vez que é derrotado. Troféus ativos somam um modificador na run e +1 nível de dificuldade global cada "
         "(inimigos mais resistentes, mais fortes e em maior número, mas mais EXP, gold e fragmentos). Troféus: "
         "Presa do Javali Colossal, Seiva do Ent Ancestral, Seda da Rainha Aranha, Presa do Lobo Sombrio e Coração "
         "do Guardião Corrompido (jogo 2x mais rápido).\n"
         "• Na primeira vez que um personagem troca para uma classe, o jogo pergunta se quer copiar os slots de "
         "maestria da classe atual."),
        ("0.0.12",
         "• Nova seleção de fase organizada por bioma: Floresta (fases I a V e Endless), com Cidade Abandonada, "
         "Catedral e Subterrâneo em breve. Cada fase mostra uma prévia do cenário e o chefão.\n"
         "• Concluir a fase V de um bioma libera a fase I do próximo bioma e o Endless do bioma.\n"
         "• Modo Endless: sem limite de tempo, dificuldade e recompensa sobem a cada 2 minutos, um Super Elite ou "
         "Esquadrão de Elite a cada minuto e um chefão em rodízio a cada 2 minutos. Melhor tempo salvo por bioma."),
        ("0.0.11",
         "• Esquiva manual no ESPAÇO (só o herói), na direção para onde ele está virado: Investida para classes de "
         "FOR (distância média, empurra inimigos, 2 usos), Esquiva para AGI e equilibradas (deslocamento rápido e "
         "longo que atravessa inimigos) e Blink para INT (teleporte longo com impacto em 360° que empurra os "
         "inimigos). Cada uma tem seu ícone com recarga e usos ao lado das hotkeys.\n"
         "• A tela de Configurações usa o mesmo fundo do menu principal; os menus do acampamento têm um fundo mais "
         "simples, sem monstros."),
        ("0.0.10",
         "• Menu principal simplificado: Iniciar, Configurações e Sair (FAQ e versão continuam). O fundo alterna "
         "entre todas as fases em ordem aleatória, com todos os monstros comuns e um de cada chefão.\n"
         "• Novo acampamento (HUB central): uma clareira fechada na floresta com uma fogueira, onde você anda até "
         "cada função: Portal (seleção de fase), Barraca (party), Ferreiro (melhoria dos equipamentos), Baú "
         "(inventário: fragmentos e gold) e Joalheiro (acessórios, em breve). Encoste, clique ou aperte E para abrir.\n"
         "• A melhoria dos equipamentos saiu do inventário e foi para o Ferreiro; depois de uma run você volta ao "
         "acampamento."),
        ("0.0.9.1",
         "• O nível do personagem não tem mais limite (os níveis de classe continuam com limite)."),
        ("0.0.9",
         "• Cenário da floresta: chão de grama, arbustos, flores, pedras e árvores que bloqueiam o movimento da "
         "party. Cada floresta tem suas cores (teias na Floresta III, árvores secas na Floresta V).\n"
         "• Inimigos novos: Esqueleto (da Floresta III em diante) e Zumbi (Floresta V), com sprites próprios. Eles "
         "também podem aparecer como elites."),
        ("0.0.8",
         "• A cada minuto da run aparece um Super Elite (10x mais forte que um elite, dropa 10 fragmentos) ou um "
         "Esquadrão de Elite (5 elites 2x mais fortes, 2 fragmentos cada), com alerta.\n"
         "• Chefões mais fortes: 3x a vida, habilidades mais pesadas, e 2 classes aleatórias por run, carregando as "
         "duas armas e usando habilidades das duas. Dropam 5 fragmentos de cada classe.\n"
         "• Tela de classes: menu suspenso 'Destacar tag' que destaca as classes e as habilidades com a tag escolhida."),
        ("0.0.7",
         "• Novos itens da run: Alcance Longo (+10% de alcance) e Runa da Expansão (+10% de área).\n"
         "• O Alcance agora controla o alcance corpo a corpo e a distância dos projéteis; a Área controla largura, "
         "tamanho e ângulo (largura das estocadas, ângulo de arcos e cones, tamanho de projéteis, impactos e auras).\n"
         "• Novas passivas de alcance (Far Reach: Archer, Lancer) e de área (Expansion: Marauder, Dragoon).\n"
         "• Quando tudo já foi melhorado, o level up oferece Frango Assado, +1 Gold ou um Power-up Aleatório, com a "
         "opção de escolher automaticamente até o fim da run.\n"
         "• Versionamento: ajustes pequenos agora usam um quarto número (0.0.7.1, 0.0.7.2 ...)."),
        ("0.0.6",
         "• Pugilist, Monk e White Monk agora são classes de AGI: bônus de nível em AGI, passivas de AGI (Evasion, "
         "precisão de Impacto/Área), mais velocidade, menos vida, e o Iron Body virou Flowing Stance (velocidade e "
         "golpes mais rápidos).\n"
         "• O Rogue agora é corpo a corpo: ataque básico de adaga (Dagger Slash), o Fan of Blades gira ao seu redor, "
         "a Poison Knife foi trocada por Thrown Knives, e as passivas focam em corpo a corpo, sangramento e corte.\n"
         "• Tela de classes: a linha de resumo de bônus saiu; a tabela de Progressão agora termina com uma linha de "
         "Total."),
        ("0.0.5",
         "• Nova aba no FAQ: Patch notes, com um resumo de cada atualização."),
        ("0.0.4",
         "• Moedas de gold entraram nos drops de power-up: geralmente 1 gold, às vezes 5, raramente 10. Vão direto "
         "para o seu gold e ficam salvas mesmo se a run terminar em derrota.\n"
         "• O pause mostra o gold coletado na run; a tela de resultado mostra o gold de drops separado.\n"
         "• O custo de recrutar voltou a dobrar a cada recruta (5, 10, 20, 40 ...)."),
        ("0.0.3",
         "• Elenco de até 20 personagens; a party na run continua de 5 (herói + 4 aliados ativos), os outros ficam "
         "na reserva.\n"
         "• Os status agora são uma chance por golpe, pelo elemento (Fogo queima, Gelo congela, Raio atordoa...) ou, "
         "nos golpes físicos, pelo tipo de golpe: Corte e Perfurante causam Sangramento, Impacto causa Atordoamento.\n"
         "• Toda habilidade física tem um tipo de golpe; a dica das habilidades mostra a chance de status.\n"
         "• Tags das habilidades revisadas para combinar com o nome e o tema (corpo a corpo/à distância, área/alvo "
         "único, Corte/Perfurante/Impacto).\n"
         "• FAQ reescrito em listas, um item por linha, com uma seção nova sobre status.\n"
         "• Textos que cortavam agora quebram linha ou rolam (classes, inventário, pause, loadout, resultado, fases).\n"
         "• A aba de fragmentos mostra as 31 classes; chance de power-up reduzida (0,2% comuns, 25% elites)."),
        ("0.0.2",
         "• Capstones: a última passiva de cada classe tem uma mecânica especial (Execute, Detonate, Vampiric, "
         "Frenzy, Echo...). O espaço 5 leva a capstone da sua classe e o 10 a de outra classe masterizada.\n"
         "• Tags nas habilidades e passivas refeitas em torno delas: dano, crítico e recarga por tag, % de "
         "atributo, % de armadura, esquiva, defesa mágica e bônus contra inimigos com status.\n"
         "• As descrições de classes e habilidades mostram as tags.\n"
         "• Medidor de dano: nova aba CC com o tempo de controle por tipo e por habilidade.\n"
         "• Power-ups: poção, barreira, fúria, crítico, aceleração, pergaminho do trovão e ímã, com pin fora da tela.\n"
         "• Freelancer virou Novice; novas evoluções Freelancer (Lv 75) e Warfarer (Lv 100).\n"
         "• As melhorias de equipamento também custam gold; itens +10 dão bônus permanente.\n"
         "• Party limitada a 5 membros; estrela nas classes masterizadas; elites chamados [Classe] [Monstro].\n"
         "• Passivas sobem até o Lv 5 durante a run; a lista de bônus do pause tem rolagem.\n"
         "• Espaços de maestria ganharam filtros suspensos de Classe e Tag."),
        ("0.0.1",
         "• Primeira build Pré-Alfa com número de versão na tela inicial.\n"
         "• Opção de idioma: English / Português.\n"
         "• Inventário com os equipamentos da party: arma e capacete fixos por classe, melhorados até +10 com "
         "fragmentos da classe e salvos por classe.\n"
         "• Fragmentos dropados pelos elites; o pause mostra os obtidos na run, e eles ficam salvos em morte ou saída.\n"
         "• Elites têm mais chance de serem das classes da party atual."),
    ]),
]


_FAQ_PT_LOCAL = None


def faq_for(lang):
    """FAQ do idioma. Em PT os nomes das classes aparecem traduzidos (menos nas Patch notes, que ficam como foram
    escritas)."""
    global _FAQ_PT_LOCAL
    if lang != "pt":
        return FAQ
    if _FAQ_PT_LOCAL is None:
        from i18n_names import localize_classes as loc
        _FAQ_PT_LOCAL = [(sec, entries) if sec == "Patch notes" else
                         (sec, [tuple(loc(x) if isinstance(x, str) else x for x in e) for e in entries])
                         for sec, entries in FAQ_PT]
    return _FAQ_PT_LOCAL
