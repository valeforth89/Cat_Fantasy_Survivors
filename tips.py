"""Dicas de introdução (new player experience).

Cada mecânica tem uma pop-up que aparece na primeira vez que ela é usada e que pode ser aberta de novo pelo botão
"?" dentro da tela dela. As dicas já vistas ficam no save (roster.tips_seen).

TIPS[id] = (título EN, título PT, [(texto EN, texto PT), ...])   — uma página por item; "\\n" quebra a linha e
linhas começando com "• " viram itens.
"""

TIPS = {
    "welcome": ("Welcome to Cat Fantasy Survivors!", "Bem-vindo ao Cat Fantasy Survivors!", [
        ("You lead a party of heroes against endless hordes. You only move: every skill attacks on its own.\n"
         "• A run lasts 10 minutes. Survive, collect the EXP gems the enemies drop and pick an upgrade at every "
         "level-up.\n"
         "• At 10:00 the stage boss appears. Defeat it to clear the stage and unlock the next one.\n"
         "• Even if you fall, the party keeps the EXP and the fragments it collected: every run makes you "
         "stronger.",
         "Você comanda uma party de heróis contra hordas sem fim. Você só se move: todas as habilidades atacam "
         "sozinhas.\n"
         "• Uma run dura 10 minutos. Sobreviva, colete as gemas de EXP que os inimigos dropam e escolha uma "
         "melhoria a cada level up.\n"
         "• Aos 10:00 aparece o chefão da fase. Derrote-o para concluir a fase e liberar a próxima.\n"
         "• Mesmo se você cair, a party fica com a EXP e os fragmentos que coletou: toda run te deixa mais "
         "forte."),
        ("This is the camp, your base between runs. Walk with WASD (or drag on the left side on mobile) and walk "
         "into a place to open it:\n"
         "• Portal: choose a stage and start a run.\n"
         "• Tent: manage the party (recruit, classes and skills).\n"
         "• Training Room: test builds against dummies that never die.\n"
         "New places open up at the camp as you progress (each one explains itself the first time).\n"
         "The \"?\" button in each screen shows its explanation again, and the Wiki has everything in detail.",
         "Este é o acampamento, a sua base entre as runs. Ande com WASD (ou arraste no lado esquerdo no celular) e "
         "encoste em um lugar para abrir:\n"
         "• Portal: escolha uma fase e comece uma run.\n"
         "• Barraca: gerencie a party (recrutar, classes e habilidades).\n"
         "• Sala de Treino: teste builds contra bonecos que nunca morrem.\n"
         "Novos lugares aparecem no acampamento conforme você avança (cada um se explica na primeira vez).\n"
         "O botão \"?\" de cada tela mostra a explicação de novo, e a Wiki tem tudo em detalhe."),
    ]),
    "run": ("Your first run", "A sua primeira run", [
        ("• Move with WASD or the arrows; skills fire on their own. SPACE dodges (a quick dash with "
         "invulnerability).\n"
         "• Pick up the EXP gems: each level-up lets you choose an upgrade (keys 1-3 or click).\n"
         "• Elites (enemies with a class hat) are stronger and drop class fragments. Glowing power-ups give "
         "short bonuses.\n"
         "• The meter at the bottom right shows your damage, damage taken, healing and crowd control.\n"
         "• ESC pauses (the pause shows your stats and bonuses; Q ends the run keeping the EXP).",
         "• Ande com WASD ou as setas; as habilidades disparam sozinhas. ESPAÇO esquiva (uma corrida rápida com "
         "invulnerabilidade).\n"
         "• Pegue as gemas de EXP: cada level up deixa você escolher uma melhoria (teclas 1-3 ou clique).\n"
         "• Elites (inimigos com chapéu de classe) são mais fortes e dropam fragmentos de classe. Power-ups "
         "brilhantes dão bônus curtos.\n"
         "• O medidor no canto inferior direito mostra dano, dano recebido, cura e controle.\n"
         "• ESC pausa (o pause mostra seus status e bônus; Q encerra a run mantendo a EXP)."),
    ]),
    "stages": ("Stage select", "Seleção de fase", [
        ("Each biome has 5 stages (I to V), each one harder and with better rewards than the previous one.\n"
         "• Clearing a stage (defeating its boss) unlocks the next one; a star marks the cleared ones.\n"
         "• Clearing stage V unlocks the biome's Endless (no time limit, difficulty keeps rising) and the next "
         "biome.\n"
         "• The panel shows the enemies, the difficulty, the rewards and the accessories each stage can drop.\n"
         "Click a stage and press Start run (or ENTER).",
         "Cada bioma tem 5 fases (I a V), cada uma mais difícil e com recompensas melhores que a anterior.\n"
         "• Concluir uma fase (derrotar o chefão) libera a próxima; uma estrela marca as concluídas.\n"
         "• Concluir a fase V libera o Endless do bioma (sem limite de tempo, a dificuldade só sobe) e o próximo "
         "bioma.\n"
         "• O painel mostra os inimigos, a dificuldade, as recompensas e os acessórios que cada fase pode dropar.\n"
         "Clique numa fase e aperte Iniciar run (ou ENTER)."),
    ]),
    "endless": ("Endless", "Endless", [
        ("The Endless of a biome has no time limit: the run goes on until the hero falls.\n"
         "• Every 2 minutes the difficulty goes up one tier (and so do EXP and gold), and a boss of the biome "
         "appears.\n"
         "• Gold is proportional to the time survived; your best time is saved.\n"
         "• It can drop the accessories of every stage of the biome.",
         "O Endless de um bioma não tem limite de tempo: a run continua até o herói cair.\n"
         "• A cada 2 minutos a dificuldade sobe um degrau (EXP e gold também) e aparece um chefão do bioma.\n"
         "• O gold é proporcional ao tempo sobrevivido; o seu melhor tempo fica salvo.\n"
         "• Pode dropar os acessórios de todas as fases do bioma."),
    ]),
    "rift": ("Endless Rift", "Endless Rift", [
        ("Like an Endless, but mixing everything you have unlocked:\n"
         "• Monsters and bosses from every unlocked stage; the scenery changes after each boss.\n"
         "• It starts at the difficulty of the highest stage you have cleared.\n"
         "• Rift levels: surviving 10 minutes clears the level and unlocks the next one; every 10 minutes you "
         "choose to stay or go up.\n"
         "• It doesn't drop accessories: elites and bosses drop accessory fragments directly.",
         "Como um Endless, mas misturando tudo o que você já liberou:\n"
         "• Monstros e chefões de todas as fases liberadas; o cenário muda depois de cada chefão.\n"
         "• Começa na dificuldade da fase mais alta que você já concluiu.\n"
         "• Níveis da fenda: sobreviver 10 minutos conclui o nível e libera o próximo; a cada 10 minutos você "
         "escolhe ficar ou subir.\n"
         "• Não dropa acessórios: elites e chefões dropam fragmentos de acessório direto."),
    ]),
    "party": ("Party (Tent)", "Party (Barraca)", [
        ("Here you manage the group. Up to 5 members go on each run (the hero always goes).\n"
         "• Recruit new members with gold (each recruit costs more).\n"
         "• Activate / move to the reserve: choose who goes on the run. A bigger party means more enemies, but "
         "allies fight, heal and level up on their own.\n"
         "• Class: change the member's class. Loadout: choose which skills they use.\n"
         "• Every member earns EXP from the runs: the general level and the level of the current class.",
         "Aqui você gerencia o grupo. Até 5 membros vão em cada run (o herói sempre vai).\n"
         "• Recrute membros novos com gold (cada recrutamento custa mais).\n"
         "• Ativar / reserva: escolha quem vai na run. Uma party maior traz mais inimigos, mas os aliados lutam, "
         "curam e sobem de nível sozinhos.\n"
         "• Classe: troca a classe do membro. Loadout: escolhe as habilidades que ele usa.\n"
         "• Todo membro ganha EXP nas runs: o nível geral e o nível da classe atual."),
    ]),
    "classes": ("Classes", "Classes", [
        ("Everyone starts as a Novice. Leveling a class unlocks the next ones:\n"
         "• Novice Lv 10 unlocks the basic classes; a basic class at Lv 25 unlocks one of its two advanced "
         "classes.\n"
         "• Each class has its own skills, passives and attribute (STR, AGI, INT or VIT); new ones unlock as the "
         "class levels up (Progression shows each level).\n"
         "• Reaching the mastery level masters the class: its skills can then be used by other classes in the "
         "mastery slots.\n"
         "Click a class and choose it; the tag filter highlights the classes that have a tag.",
         "Todo mundo começa como Novice. Subir o nível de uma classe libera as próximas:\n"
         "• Novice Nv 10 libera as classes básicas; uma básica no Nv 25 libera uma das suas duas avançadas.\n"
         "• Cada classe tem habilidades, passivas e atributo próprios (FOR, AGI, INT ou VIT); novas liberam "
         "conforme a classe sobe (Progressão mostra cada nível).\n"
         "• Chegar ao nível de maestria masteriza a classe: as habilidades dela passam a poder ser usadas por "
         "outras classes nos espaços de maestria.\n"
         "Clique numa classe e escolha; o filtro de tag destaca as classes que têm uma tag."),
    ]),
    "loadout": ("Loadout", "Loadout", [
        ("Choose the skills the member uses in the run:\n"
         "• Basic attack (fixed, from the class weapon), active skills and passives of the current class.\n"
         "• Mastery slots: skills and passives of other classes you have mastered.\n"
         "• Click a slot on the left, then a skill on the right. Right-click (or DEL) clears a slot.\n"
         "• Use the tag filter (T) to find skills for a build: fire, area, projectile, healing...",
         "Escolha as habilidades que o membro usa na run:\n"
         "• Ataque básico (fixo, da arma da classe), habilidades ativas e passivas da classe atual.\n"
         "• Espaços de maestria: habilidades e passivas de outras classes que você masterizou.\n"
         "• Clique num espaço à esquerda e depois numa habilidade à direita. Botão direito (ou DEL) limpa.\n"
         "• Use o filtro de tag (T) para achar habilidades para uma build: fogo, área, projétil, cura..."),
    ]),
    "training": ("Training Room", "Sala de Treino", [
        ("A field to test formations and builds without risk: the dummies never die and nothing here gives "
         "rewards.\n"
         "• Press T (or the Training button) to open the panel: add dummies (normal, elite, super elite, squad "
         "or boss), choose their strength and whether they attack.\n"
         "• The meter at the bottom right shows DPS / HPS; \"Reset meter\" starts the count again.\n"
         "• Use +1 / +10 level-ups to try the run upgrades, and Manage party to change the group.",
         "Um campo para testar formações e builds sem risco: os bonecos nunca morrem e nada aqui dá recompensa.\n"
         "• Aperte T (ou o botão Treino) para abrir o painel: coloque bonecos (comum, elite, super elite, "
         "esquadrão ou chefão), escolha a força deles e se eles atacam.\n"
         "• O medidor no canto inferior direito mostra DPS / HPS; \"Zerar medidor\" recomeça a contagem.\n"
         "• Use +1 / +10 level ups para testar as melhorias da run, e Gerenciar party para trocar o grupo."),
    ]),
    "chest": ("Chest - Inventory", "Baú - Inventário", [
        ("Everything you collected is stored here: gold, class fragments and accessory fragments.\n"
         "• Class fragments drop from elites and bosses. They are used at the Altar of Mastery (raise a class "
         "max level) and to upgrade necklaces.\n"
         "• Accessory fragments come from duplicate accessories and are used at the Jeweler.",
         "Tudo o que você coletou fica guardado aqui: gold, fragmentos de classe e fragmentos de acessório.\n"
         "• Fragmentos de classe dropam de elites e chefões. Servem no Altar da Maestria (subir o nível máximo de "
         "uma classe) e para melhorar os colares.\n"
         "• Fragmentos de acessório vêm de acessórios repetidos e são usados no Joalheiro."),
    ]),
    "smith": ("Blacksmith", "Ferreiro", [
        ("The blacksmith upgrades the weapon and the helmet of each class with gold.\n"
         "• Upgrades belong to the CLASS: every character using that class gets them.\n"
         "• Weapon: more damage. Helmet: more HP and defenses.\n"
         "Pick a class on the left and upgrade its gear on the right.",
         "O ferreiro melhora a arma e o capacete de cada classe com gold.\n"
         "• As melhorias são da CLASSE: todo personagem usando aquela classe ganha.\n"
         "• Arma: mais dano. Capacete: mais vida e defesas.\n"
         "Escolha uma classe à esquerda e melhore os equipamentos à direita."),
    ]),
    "greed": ("Altar of Greed", "Altar da Ganância", [
        ("The lucky golden cat accepts your spare gold and blesses the WHOLE party for good.\n"
         "• Buy levels of Attack, Defense, Max HP, Range, Area, Critical chance, Critical damage, Cooldown and "
         "Dodge. Every level counts for every character.\n"
         "• Each stat gets 40% more expensive at every level, so spreading the gold over many stats is cheaper.\n"
         "• Defense, Critical chance, Cooldown and Dodge stop at 10 levels (they have caps).\n"
         "Click a stat (or ENTER) to buy.",
         "O gato dourado da sorte aceita o seu gold sobrando e abençoa a party INTEIRA para sempre.\n"
         "• Compre níveis de Ataque, Defesa, Vida máxima, Alcance, Área, Chance crítica, Dano crítico, Recarga e "
         "Esquiva. Cada nível vale para todos os personagens.\n"
         "• Cada atributo fica 40% mais caro a cada nível, então espalhar o gold por vários sai mais barato.\n"
         "• Defesa, Chance crítica, Recarga e Esquiva param em 10 níveis (eles têm limite).\n"
         "Clique num atributo (ou ENTER) para comprar."),
    ]),
    "craft": ("Blacksmith - Armor, Pants & Boots", "Ferreiro - Armadura, Calça e Bota", [
        ("Every monster drops its own material (Wolf Fur, Skeleton Bone...). Elites drop more and bosses drop "
         "some of every material of their biome.\n"
         "• Each biome has 1 armor, 1 pants and 1 boots made with its monsters' materials. Craft them here and "
         "upgrade them up to +10 with more materials.\n"
         "• Armor is defensive, pants mix defense and utility, boots are pure utility. A biome is not better "
         "than another: each set has its own style.\n"
         "• Each item is unique: only one character can wear it, like the accessories.",
         "Cada monstro dropa o seu próprio material (Pelo de Lobo, Osso de Esqueleto...). Elites dropam mais e os "
         "chefões dropam um pouco de cada material do bioma deles.\n"
         "• Cada bioma tem 1 armadura, 1 calça e 1 bota feitas com os materiais dos seus monstros. Crie aqui e "
         "melhore até +10 com mais materiais.\n"
         "• A armadura é defensiva, a calça mistura defesa e utilidade, a bota é só utilidade. Um bioma não é "
         "melhor que o outro: cada conjunto tem o seu estilo.\n"
         "• Cada item é único: só um personagem pode usá-lo, como os acessórios."),
    ]),
    "jeweler": ("Jeweler - Accessories", "Joalheiro - Acessórios", [
        ("Accessories are unique items that drop from elites and bosses (each stage has its own list).\n"
         "• Each character has 2 rings, 1 bracer, 2 trinkets, 1 necklace and 1 emblem. An accessory can only be "
         "worn by one character at a time.\n"
         "• Rings give simple bonuses; bracers work against enemies with statuses; trinkets have chance effects; "
         "necklaces come from classes at Lv 100; emblems help the whole party.\n"
         "• Duplicates become fragments that upgrade accessories (+1 to +5).\n"
         "Click a slot on the left, then an accessory in the list.",
         "Acessórios são itens únicos que dropam de elites e chefões (cada fase tem a sua lista).\n"
         "• Cada personagem tem 2 anéis, 1 bracelete, 2 berloques, 1 colar e 1 emblema. Um acessório só pode "
         "ser usado por um personagem por vez.\n"
         "• Anéis dão bônus simples; braceletes funcionam contra inimigos com status; berloques têm efeitos com "
         "chance; colares vêm das classes no Nv 100; emblemas ajudam a party inteira.\n"
         "• Repetidos viram fragmentos que melhoram os acessórios (+1 a +5).\n"
         "Clique num espaço à esquerda e depois num acessório da lista."),
    ]),
    "altar": ("Altar of Trophies", "Altar dos Troféus", [
        ("Each stage boss drops its trophy the first time it is defeated.\n"
         "• Activating a trophy applies its effect to every run: always a bonus, BUT also a downside.\n"
         "• Each active trophy also adds +1 global difficulty level: tougher and more numerous enemies, but "
         "more EXP, gold and fragments.\n"
         "Click a trophy to activate or deactivate it; the tabs separate them by biome.",
         "Cada chefão de fase dropa o seu troféu na primeira vez que é derrotado.\n"
         "• Ativar um troféu aplica o efeito dele em toda run: sempre um bônus, MAS também uma desvantagem.\n"
         "• Cada troféu ativo também soma +1 nível de dificuldade global: inimigos mais fortes e numerosos, mas "
         "mais EXP, gold e fragmentos.\n"
         "Clique num troféu para ativar ou desativar; as abas separam por bioma."),
    ]),
    "mastery": ("Altar of Mastery", "Altar da Maestria", [
        ("You mastered your first class! This altar raises the max level of a class.\n"
         "• Offer class fragments of a class to raise its max level (each offer costs more).\n"
         "• The extra levels keep giving the class level bonuses and they count for every character.\n"
         "Click a class, then Offer (or ENTER).",
         "Você masterizou a sua primeira classe! Este altar aumenta o nível máximo de uma classe.\n"
         "• Ofereça fragmentos de uma classe para subir o nível máximo dela (cada oferta custa mais).\n"
         "• Os níveis extras continuam dando os bônus de nível da classe e valem para todos os personagens.\n"
         "Clique numa classe e depois em Oferecer (ou ENTER)."),
    ]),
    "dungeons": ("Red Portal - Dungeons", "Portal Vermelho - Masmorras", [
        ("Three short dungeons (about 1 to 1.5 min): a long corridor with only Super Elites and Elite Squads "
         "and a boss at the end.\n"
         "• Cavern = lots of gold · Catacomb = class fragments · Dungeon = accessory fragments.\n"
         "• Clearing a level unlocks the next one (stronger enemies, better rewards); levels have no end.\n"
         "• Each dungeon has its own 4 accessories to drop.",
         "Três masmorras curtas (cerca de 1 a 1,5 min): um corredor longo só com Super Elites e Esquadrões de "
         "Elite e um chefão no fim.\n"
         "• Caverna = muito gold · Catacumba = fragmentos de classe · Masmorra = fragmentos de acessório.\n"
         "• Concluir um nível libera o próximo (inimigos mais fortes, recompensas melhores); os níveis não têm "
         "fim.\n"
         "• Cada masmorra tem os seus 4 acessórios para dropar."),
    ]),
}

# lugares do acampamento: id do desbloqueio -> (nome EN, nome PT, como libera EN, PT)
UNLOCKS = {
    "chest": ("Chest - Inventory", "Baú - Inventário", "your first class fragment", "o seu primeiro fragmento de classe"),
    "smith": ("Blacksmith", "Ferreiro", "clearing Forest III", "concluir a Floresta III"),
    "jeweler": ("Jeweler", "Joalheiro", "your first accessory", "o seu primeiro acessório"),
    "altar": ("Altar of Trophies", "Altar dos Troféus", "your first trophy", "o seu primeiro troféu"),
    "mastery": ("Altar of Mastery", "Altar da Maestria", "mastering a class", "masterizar uma classe"),
    "dungeons": ("Red Portal - Dungeons", "Portal Vermelho - Masmorras", "clearing Forest V", "concluir a Floresta V"),
    "greed": ("Altar of Greed", "Altar da Ganância", "clearing Forest IV or saving 150 gold",
              "concluir a Floresta IV ou juntar 150 de gold"),
    "craft": ("Blacksmith - Armor, Pants & Boots", "Ferreiro - Armadura, Calça e Bota", "your first monster material",
              "o seu primeiro material de monstro"),
}


def title(tid, lang):
    t = TIPS[tid]
    return t[1] if lang == "pt" else t[0]


def pages(tid, lang):
    if lang == "pt":
        from i18n_names import localize_classes
        return [localize_classes(p[1]) for p in TIPS[tid][2]]
    return [p[0] for p in TIPS[tid][2]]
