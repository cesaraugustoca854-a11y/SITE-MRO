#!/usr/bin/env python3
"""Gera o acervo do Reviva 2026 (fotos, vídeos e depoimentos) a partir de content/reviva.json.

Uso: python3 scripts/gerar_reviva.py
Atualiza em index.html os trechos REVIVA:GALERIA, REVIVA:NOTA e REVIVA:SCHEMA (VideoObject só para vídeo com "data" de publicação).
Regras de honestidade: só entra item com "autorizado": true; foto sem legenda ou texto
alternativo, ou sem arquivo em assets/img/reviva/, para o script com erro. Enquanto não houver
fotos autorizadas, a galeria mostra as 3 imagens de demonstração, claramente marcadas.
"""
import html
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img" / "reviva"
LARGURAS = (480, 960, 1600)
PLATAFORMAS = {
    "youtube": "https://www.youtube-nocookie.com/embed/{id}?autoplay=1&rel=0",
    "vimeo": "https://player.vimeo.com/video/{id}?autoplay=1&dnt=1",
}

ICO_ZOOM = '<span class="g-photo__zoom"><svg class="ico" aria-hidden="true"><use href="#i-expand"/></svg><span class="sr-only">Ampliar imagem</span></span>'


def esc(t):
    return html.escape(str(t), quote=True)


def erro(msg):
    sys.exit(f"ERRO em content/reviva.json: {msg}")


def tamanho_jpeg(arq):
    """Largura e altura lidas do cabeçalho JPEG (sem bibliotecas externas)."""
    dados = arq.read_bytes()
    i = 2
    while i < len(dados):
        if dados[i] != 0xFF:
            i += 1
            continue
        marca = dados[i + 1]
        if marca in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", dados[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", dados[i + 2:i + 4])[0]
    erro(f"não consegui ler o tamanho de {arq.name}")


def foto(f, i):
    for campo in ("arquivo", "legenda", "alt"):
        if not f.get(campo):
            erro(f'foto {i + 1}: falta "{campo}"')
    nome = f["arquivo"]
    versoes = [w for w in LARGURAS if (IMG / f"{nome}-{w}.jpg").exists()]
    if not versoes:
        erro(f'foto "{nome}": rode scripts/preparar_fotos.py (não há arquivos em assets/img/reviva/)')
    base = max(versoes)
    larg, alt_px = tamanho_jpeg(IMG / f"{nome}-{base}.jpg")
    mid = 960 if 960 in versoes else base
    srcset = ", ".join(f"assets/img/reviva/{nome}-{w}.jpg {w}w" for w in versoes)
    avif = [w for w in versoes if (IMG / f"{nome}-{w}.avif").exists()]
    fonte = ""
    if avif:
        fonte = '<source type="image/avif" srcset="' + ", ".join(f"assets/img/reviva/{nome}-{w}.avif {w}w" for w in avif) + '" sizes="(min-width: 900px) 33vw, 100vw">'
    credito = f' Foto: {f["credito"]}.' if f.get("credito") else ""
    legenda_cheia = f["legenda"] + credito
    wide = " g-item--wide" if f.get("destaque") else ""
    return (f'<li class="g-item{wide}" data-type="fotos">\n'
            f'<button type="button" class="g-photo" data-lightbox data-full="assets/img/reviva/{nome}-{base}.jpg" data-caption="{esc(legenda_cheia)}">\n'
            f'<picture>{fonte}<img src="assets/img/reviva/{nome}-{mid}.jpg" srcset="{srcset}" sizes="(min-width: 900px) 33vw, 100vw" '
            f'width="{larg}" height="{alt_px}" alt="{esc(f["alt"])}" loading="lazy" decoding="async"></picture>\n{ICO_ZOOM}\n</button>\n'
            f'<p class="g-caption"><span class="tag">Foto</span> {esc(f["legenda"])}</p>\n</li>')


def video(v, i):
    for campo in ("titulo", "plataforma", "id", "descricao"):
        if not v.get(campo):
            erro(f'vídeo {i + 1}: falta "{campo}"')
    if v["plataforma"] not in PLATAFORMAS:
        erro(f'vídeo "{v["titulo"]}": plataforma deve ser {" ou ".join(PLATAFORMAS)}')
    if not re.fullmatch(r"[A-Za-z0-9_-]{4,20}", str(v["id"])):
        erro(f'vídeo "{v["titulo"]}": "id" deve ser só o código do vídeo, não o link inteiro')
    poster = ""
    if v.get("miniatura"):
        nome = v["miniatura"]
        arq = IMG / f"{nome}-960.jpg"
        if not arq.exists():
            erro(f'vídeo "{v["titulo"]}": miniatura "{nome}" não encontrada (rode preparar_fotos.py)')
        w, h = tamanho_jpeg(arq)
        poster = f'<img src="assets/img/reviva/{nome}-960.jpg" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">'
    duracao = f' <span class="g-video__dur">{esc(v["duracao"])}</span>' if v.get("duracao") else ""
    transc = (f'\n<details class="g-transcript"><summary>Transcrição</summary><p>{esc(v["transcricao"])}</p></details>'
              if v.get("transcricao") else "")
    return (f'<li class="g-item g-item--wide" data-type="videos">\n'
            f'<div class="g-video" data-video="{v["plataforma"]}:{esc(v["id"])}" data-video-title="{esc(v["titulo"])}">{poster}\n'
            f'<button type="button" class="g-video__play" data-video-play><svg class="ico" aria-hidden="true"><use href="#i-play"/></svg>'
            f'<span class="sr-only">Reproduzir vídeo: {esc(v["titulo"])}</span></button></div>\n'
            f'<p class="g-caption"><span class="tag">Vídeo</span> {esc(v["titulo"])}{duracao}</p>\n'
            f'<p class="g-desc">{esc(v["descricao"])}</p>{transc}\n</li>')


def depoimento(d, i):
    for campo in ("nome", "cargo", "empresa", "texto"):
        if not d.get(campo):
            erro(f'depoimento {i + 1}: falta "{campo}"')
    return (f'<li class="g-item" data-type="depoimentos">\n'
            f'<figure class="quote"><svg class="ico quote__ico" aria-hidden="true"><use href="#i-quote"/></svg>\n'
            f'<blockquote><p>{esc(d["texto"])}</p></blockquote>\n'
            f'<figcaption><strong>{esc(d["nome"])}</strong>, {esc(d["cargo"])}, {esc(d["empresa"])}</figcaption></figure>\n</li>')


DEMO_FOTOS = '''<li class="g-item g-item--wide" data-type="fotos">
<button type="button" class="g-photo" data-lightbox data-full="assets/img/demo-feira.jpg" data-caption="Demonstração de layout: circulação de visitantes em pavilhão de feira. Imagem ilustrativa, não é registro da MRO Brasil 2026.">
<picture><source type="image/avif" srcset="assets/img/demo-feira-720.avif"><img src="assets/img/demo-feira-720.jpg" width="720" height="540" alt="Imagem ilustrativa de visitantes circulando entre estandes em um pavilhão de exposições." loading="lazy" decoding="async"></picture>
''' + ICO_ZOOM + '''
</button>
<p class="g-caption"><span class="tag tag--demo">Demonstração</span> Circulação em pavilhão de feira</p>
</li>
<li class="g-item" data-type="fotos">
<button type="button" class="g-photo" data-lightbox data-full="assets/img/demo-painel.jpg" data-caption="Demonstração de layout: painel de debate em auditório. Imagem ilustrativa, não é registro da MRO Brasil 2026.">
<picture><source type="image/avif" srcset="assets/img/demo-painel-720.avif"><img src="assets/img/demo-painel-720.jpg" width="720" height="540" alt="Imagem ilustrativa de painel de debate com quatro participantes e plateia." loading="lazy" decoding="async"></picture>
''' + ICO_ZOOM + '''
</button>
<p class="g-caption"><span class="tag tag--demo">Demonstração</span> Painel de debate</p>
</li>
<li class="g-item" data-type="fotos">
<button type="button" class="g-photo" data-lightbox data-full="assets/img/hero-aviacao.jpg" data-caption="Demonstração de layout: aeronave em hangar de manutenção. Imagem ilustrativa, não é registro da MRO Brasil 2026.">
<picture><source type="image/avif" srcset="assets/img/hero-aviacao-800.avif"><img src="assets/img/hero-aviacao-800.jpg" width="800" height="533" alt="Imagem ilustrativa de aeronave comercial em hangar de manutenção." loading="lazy" decoding="async"></picture>
''' + ICO_ZOOM + '''
</button>
<p class="g-caption"><span class="tag tag--demo">Demonstração</span> Hangar de manutenção</p>
</li>'''

PEND_VIDEO = '''<li class="g-item" data-type="videos">
<div class="pending pending--video">
<svg class="ico pending__ico" aria-hidden="true"><use href="#i-film"/></svg>
<p class="pending__title">Vídeos em preparação</p>
<p class="pending__text">Os vídeos oficiais da edição 2026 serão publicados aqui, com reprodução iniciada por quem visita.</p>
</div>
<p class="g-caption"><span class="tag">Vídeos</span> Acervo oficial pendente</p>
</li>'''

PEND_QUOTE = '''<li class="g-item" data-type="depoimentos">
<figure class="pending pending--quote">
<svg class="ico pending__ico" aria-hidden="true"><use href="#i-quote"/></svg>
<blockquote class="pending__title">Depoimentos em preparação</blockquote>
<figcaption class="pending__text">Falas e identificação de participantes serão publicadas somente com autorização de uso.</figcaption>
</figure>
<p class="g-caption"><span class="tag">Depoimentos</span> Acervo oficial pendente</p>
</li>'''


def autorizados(itens, tipo):
    ok = []
    for n, it in enumerate(itens):
        if it.get("autorizado") is True:
            ok.append((n, it))
        else:
            print(f"  ignorado ({tipo} {n + 1}): sem \"autorizado\": true")
    return ok


def nota(tem_fotos, tem_videos, tem_dep):
    pendentes = []
    if not tem_fotos:
        pendentes.append("as fotos da galeria abaixo ainda são demonstrações de layout")
    if not tem_videos:
        pendentes.append("os vídeos aparecem como pendentes até o envio dos arquivos autorizados")
    if not tem_dep:
        pendentes.append("os depoimentos aparecem como pendentes até o envio dos textos autorizados")
    texto = "<strong>O tour virtual 360° é um registro real da edição 2026.</strong>"
    if pendentes:
        texto += " " + "; ".join(pendentes)[0].upper() + "; ".join(pendentes)[1:] + "."
    return ('<p class="status-note"><svg class="ico" aria-hidden="true"><use href="#i-info"/></svg>'
            f"<span>{texto}</span></p>")


def schema(videos):
    itens = []
    for _, v in videos:
        if v.get("data"):
            itens.append({"@type": "VideoObject", "name": v["titulo"], "description": v["descricao"], "uploadDate": v["data"],
                          "embedUrl": PLATAFORMAS[v["plataforma"]].split("?")[0].format(id=v["id"]), "inLanguage": "pt-BR"})
    if not itens:
        return ""
    return ('<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": itens}, ensure_ascii=False, indent=2)
            + "\n</script>")


def trocar(doc, marca, conteudo):
    padrao = re.compile(rf"(<!-- {marca} -->).*?(<!-- /{marca} -->)", re.S)
    if not padrao.search(doc):
        sys.exit(f"Marcador {marca} não encontrado em index.html")
    return padrao.sub(lambda m: m.group(1) + "\n" + conteudo + "\n" + m.group(2), doc)


def main():
    dados = json.loads((ROOT / "content" / "reviva.json").read_text(encoding="utf-8"))
    fotos = autorizados(dados.get("fotos", []), "foto")
    videos = autorizados(dados.get("videos", []), "vídeo")
    deps = autorizados(dados.get("depoimentos", []), "depoimento")

    blocos = [foto(f, n) for n, f in fotos] or [DEMO_FOTOS]
    blocos += [video(v, n) for n, v in videos] or [PEND_VIDEO]
    blocos += [depoimento(d, n) for n, d in deps] or [PEND_QUOTE]

    alvo = ROOT / "index.html"
    doc = alvo.read_text(encoding="utf-8")
    doc = trocar(doc, "REVIVA:GALERIA", "\n".join(blocos))
    doc = trocar(doc, "REVIVA:NOTA", nota(bool(fotos), bool(videos), bool(deps)))
    doc = trocar(doc, "REVIVA:SCHEMA", schema(videos))
    alvo.write_text(doc, encoding="utf-8")
    print(f"Reviva: {len(fotos)} fotos, {len(videos)} vídeos, {len(deps)} depoimentos publicados")


if __name__ == "__main__":
    main()
