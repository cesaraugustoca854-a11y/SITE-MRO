#!/usr/bin/env python3
"""Prepara as fotos do acervo: gera as versões otimizadas para o site.

Uso: python3 scripts/preparar_fotos.py
Lê content/originais/reviva/*.jpg|jpeg|png e grava em assets/img/reviva/ as larguras
480, 960 e 1600 px em JPEG (e em AVIF, se o programa avifenc estiver instalado).
Usa o sips do macOS. Nunca altera os originais.
"""
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGEM = ROOT / "content" / "originais" / "reviva"
DESTINO = ROOT / "assets" / "img" / "reviva"
LARGURAS = (480, 960, 1600)


def slug(nome):
    t = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return "-".join(re.findall(r"[a-z0-9]+", t))


def largura(arq):
    saida = subprocess.run(["sips", "-g", "pixelWidth", str(arq)], capture_output=True, text=True).stdout
    return int(saida.split("pixelWidth:")[1].split()[0])


def main():
    if not shutil.which("sips"):
        sys.exit("Este script usa o sips (macOS). Em outro sistema, exporte as larguras 480, 960 e 1600 à mão.")
    fotos = sorted(p for p in ORIGEM.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not fotos:
        sys.exit(f"Nenhuma foto em {ORIGEM.relative_to(ROOT)}")
    DESTINO.mkdir(parents=True, exist_ok=True)
    avif = shutil.which("avifenc")
    for foto in fotos:
        nome, larg = slug(foto.stem), largura(foto)
        for w in LARGURAS:
            if w > larg and w != LARGURAS[0]:
                continue  # não amplia
            saida = DESTINO / f"{nome}-{w}.jpg"
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", str(w), str(foto), "--out", str(saida)],
                           check=True, capture_output=True)
            if avif:
                subprocess.run([avif, "-q", "55", str(saida), str(saida.with_suffix(".avif"))], check=True, capture_output=True)
        print(f"{foto.name} -> arquivo \"{nome}\"")
    if not avif:
        print("Aviso: avifenc não encontrado; geradas só as versões JPEG (instale com: brew install libavif).")


if __name__ == "__main__":
    main()
