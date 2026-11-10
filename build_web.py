"""Gera a versão web (navegador / celular) do Cat Fantasy Survivors com o pygbag.

Uso (no PC, dentro da pasta do jogo):
    pip install pygbag openpyxl
    python build_web.py           -> gera web/build/web (site pronto) e web/build/web.zip (para o itch.io)
    python build_web.py --serve   -> gera e abre um servidor de teste: http://localhost:8000 no PC, ou
                                     http://IP-DO-PC:8000 no celular (mesmo Wi-Fi)

O que ele faz:
1. Copia os .py do jogo para web/fantasy_survivors/ e cria o main.py que o pygbag exige.
2. Converte a classes.xlsx em classes_cache.pkl (no navegador não há openpyxl para ler a planilha).
3. Roda o pygbag, que empacota tudo junto com o Python para WebAssembly.
"""
import os
import pickle
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "web")
APP = os.path.join(OUT, "fantasy_survivors")
SKIP = {"build_web.py", "main.py"}

MAIN_PY = '''# Ponto de entrada da versão web (gerado pelo build_web.py)
import asyncio

import survivors

asyncio.run(survivors.web_main())
'''


def main():
    serve = "--serve" in sys.argv
    if os.path.isdir(APP):
        shutil.rmtree(APP)
    os.makedirs(APP)
    for f in os.listdir(HERE):
        if (f.endswith(".py") and f not in SKIP) or f.endswith(".ttf"):   # .ttf: fonte pixel (Jersey 10)
            shutil.copy(os.path.join(HERE, f), APP)
    with open(os.path.join(APP, "main.py"), "w", encoding="utf-8") as fh:
        fh.write(MAIN_PY)

    # conteúdo das classes: a planilha convertida (o navegador não lê .xlsx)
    sys.path.insert(0, HERE)
    import progression as prog
    prog.load()
    if prog.LOAD_INFO["source"] != "classes.xlsx":
        print("ATENÇÃO: classes.xlsx não foi lida (pip install openpyxl?). A versão web vai usar o conteúdo provisório.")
    else:
        with open(os.path.join(APP, "classes_cache.pkl"), "wb") as fh:
            import data
            extra = {"__classes__": {cid: {k: c[k] for k in ("class_role", "attr", "weapon",
                                                            "role", "ranged", "lore") if k in c}
                                     for cid, c in data.CLASSES.items()},
                     "__roles__": (dict(data.CLASS_ROLE_DEFS), list(data.ROLE_ORDER))}
            pickle.dump(dict(prog.CONTENT, **extra), fh)

    # ícone da página
    try:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        pygame.init()
        import skill_icons
        pygame.image.save(skill_icons.game_icon(64), os.path.join(APP, "favicon.png"))
    except Exception as exc:
        print("sem ícone:", exc)

    cmd = [sys.executable, "-m", "pygbag", "--title", "Cat Fantasy Survivors", "--width", "1280", "--height", "720",
           "--icon", os.path.join(APP, "favicon.png"), "--package", "web.pygame.fantasy_survivors", "--ume_block", "0"]
    tmpl = os.path.join(HERE, "web_template.tmpl")
    if os.path.exists(tmpl):
        cmd += ["--template", tmpl]
    if serve:   # servidor de teste aberto na rede: o celular no mesmo Wi-Fi acessa http://IP-DO-PC:8000
        cmd += ["--bind", "0.0.0.0"]
    else:
        cmd += ["--build", "--archive"]
    cmd.append(APP)
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=OUT, check=True)
    if serve:
        return
    # cópia do zip com o nome do jogo e a versão (a pasta interna continua fantasy_survivors para não perder os
    # saves do navegador)
    sys.path.insert(0, HERE)
    try:
        from version import VERSION
        name = f"CatFantasySurvivors-web-{VERSION}.zip"
    except Exception:
        name = "CatFantasySurvivors-web.zip"
    src = os.path.join(APP, "build", "web.zip")
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(APP, "build", name))
    print(f"\nPronto: web/fantasy_survivors/build/web (site) e web/fantasy_survivors/build/{name} (itch.io)")


if __name__ == "__main__":
    main()
