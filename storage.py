"""Leitura e gravação dos saves.

- No PC (python survivors.py ou executável): arquivos .json ao lado do jogo, como sempre.
- Na versão web (navegador, pygbag): o navegador não guarda arquivos entre uma visita e outra, então os
  saves vão para o localStorage do navegador (ficam no celular/PC de quem joga, por site).
"""
import os
import sys

IS_WEB = sys.platform == "emscripten"
PREFIX = "fantasy_survivors/"


def _local_storage():
    import platform   # na web (pygbag) este módulo dá acesso ao "window" do navegador
    return platform.window.localStorage


def read_text(path):
    """Conteúdo do save (texto) ou None se não existir."""
    if IS_WEB:
        try:
            v = _local_storage().getItem(PREFIX + os.path.basename(path))
            return None if v is None else str(v)
        except Exception:
            return None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def write_text(path, text):
    if IS_WEB:
        try:
            _local_storage().setItem(PREFIX + os.path.basename(path), text)
        except Exception:
            pass
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        pass
