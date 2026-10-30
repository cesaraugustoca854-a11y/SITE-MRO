#!/usr/bin/env python3
"""Gera as perguntas frequentes a partir de content/faq.json.

Uso: python3 scripts/gerar_faq.py
Atualiza, em index.html, os trechos entre os marcadores FAQ:JSONLD (schema FAQPage),
FAQ:PAGINA (página Perguntas frequentes) e FAQ:DESTAQUES (bloco da home), e reescreve
llms.txt. Assim o texto visível e o schema nunca divergem.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROTA = "#/perguntas-frequentes"
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def para_html(texto):
    """Escapa o texto e converte [rótulo](destino) em link."""
    out, pos = [], 0
    for m in LINK.finditer(texto):
        out.append(html.escape(texto[pos:m.start()], quote=False))
        rotulo, destino = html.escape(m.group(1), quote=False), html.escape(m.group(2))
        if destino.startswith("http"):
            out.append(f'<a href="{destino}" target="_blank" rel="noopener">{rotulo}<span class="sr-only"> (abre em nova aba)</span></a>')
        else:
            out.append(f'<a href="{destino}">{rotulo}</a>')
        pos = m.end()
    out.append(html.escape(texto[pos:], quote=False))
    return "".join(out)


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return "q-" + "-".join(re.findall(r"[a-z0-9]+", t))[:60].rstrip("-")


def para_texto(texto):
    return LINK.sub(r"\1", texto)


def bloco_jsonld(grupos):
    itens = [{"@type": "Question", "name": q["p"], "acceptedAnswer": {"@type": "Answer", "text": para_texto(q["r"])}}
             for g in grupos for q in g["perguntas"]]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "pt-BR", "mainEntity": itens}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def bloco_pagina(grupos):
    partes = []
    for g in grupos:
        itens = "".join(
            f'<details class="faq-item" id="{slug(q["p"])}"><summary>{html.escape(q["p"], quote=False)}</summary>'
            f'<div class="faq-item__a"><p>{para_html(q["r"])}</p></div></details>\n'
            for q in g["perguntas"])
        partes.append(
            f'<section class="faq-group" id="faq-{g["id"]}" aria-labelledby="h-faq-{g["id"]}">\n'
            f'<h2 id="h-faq-{g["id"]}" class="faq-group__title">{html.escape(g["titulo"], quote=False)}</h2>\n'
            f'<div class="faq-list">\n{itens}</div>\n</section>')
    return "\n".join(partes)


def bloco_subnav(grupos):
    return "\n".join(f'<a href="{ROTA}/{g["id"]}" data-spy="faq-{g["id"]}">{html.escape(g["titulo"], quote=False)}</a>' for g in grupos)


def bloco_destaques(grupos):
    itens = "".join(
        f'<li><a href="{ROTA}/{g["id"]}" data-faq-open="{slug(q["p"])}"><span>{html.escape(q["p"], quote=False)}</span>'
        f'<svg class="ico" aria-hidden="true"><use href="#i-arrow"/></svg></a></li>\n'
        for g in grupos for q in g["perguntas"] if q.get("destaque"))
    return f'<ul class="faq-teaser__list">\n{itens}</ul>'


def llms(grupos):
    linhas = [
        "# MRO Brasil 2027 — Feira Internacional de Manutenção Aeronáutica",
        "",
        "> Feira dedicada à cadeia de manutenção, reparo e revisão (MRO) aeronáutica. 20 e 21 de outubro de 2027, "
        "Centro de Convenções Frei Caneca, Rua Frei Caneca, 569, Bela Vista, São Paulo (SP). "
        "Tema 2027: “A inteligência na revolução do MRO”.",
        "",
        "Fonte dos dados: folder oficial MRO Brasil 2027 e organização (Aeromarketing / Delta Fox Eventos).",
        "",
        "## Perguntas frequentes",
        "",
    ]
    for g in grupos:
        linhas.append(f"### {g['titulo']}")
        linhas.append("")
        for q in g["perguntas"]:
            linhas.append(f"**{q['p']}**")
            linhas.append(para_texto(q["r"]))
            linhas.append("")
    return "\n".join(linhas)


def trocar(doc, marca, conteudo):
    padrao = re.compile(rf"(<!-- {marca} -->).*?(<!-- /{marca} -->)", re.S)
    if not padrao.search(doc):
        raise SystemExit(f"Marcador {marca} não encontrado em index.html")
    return padrao.sub(lambda m: m.group(1) + "\n" + conteudo + "\n" + m.group(2), doc)


def main():
    grupos = json.loads((ROOT / "content" / "faq.json").read_text(encoding="utf-8"))["grupos"]
    alvo = ROOT / "index.html"
    doc = alvo.read_text(encoding="utf-8")
    doc = trocar(doc, "FAQ:JSONLD", bloco_jsonld(grupos))
    doc = trocar(doc, "FAQ:SUBNAV", bloco_subnav(grupos))
    doc = trocar(doc, "FAQ:PAGINA", bloco_pagina(grupos))
    doc = trocar(doc, "FAQ:DESTAQUES", bloco_destaques(grupos))
    alvo.write_text(doc, encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(grupos), encoding="utf-8")
    total = sum(len(g["perguntas"]) for g in grupos)
    print(f"{total} perguntas em {len(grupos)} grupos; index.html e llms.txt atualizados")


if __name__ == "__main__":
    main()
