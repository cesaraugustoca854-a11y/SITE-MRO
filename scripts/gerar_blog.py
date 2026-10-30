#!/usr/bin/env python3
"""Gera o blog: uma página HTML real por artigo, a listagem, o feed e o sitemap.

Uso: python3 scripts/gerar_blog.py
Lê content/blog/*.md e content/blog/config.json. Grava blog/index.html e blog/<artigo>/index.html.
Cabeçalho, rodapé e ícones vêm de index.html, então o blog sempre acompanha o site.

Formato do artigo (content/blog/nome-do-artigo.md): cabeçalho entre linhas "---" com
titulo, titulo_seo (opcional, até 60 caracteres, vira o <title>), resumo, data (AAAA-MM-DD), atualizado (opcional), categoria, imagem (nome de um
arquivo de assets/img sem extensão), imagem_alt, revisado (sim ou nao); depois o texto em
Markdown simples (##, ###, listas com "-" ou "1.", **negrito**, [link](destino)). O que vem
depois de "## Perguntas frequentes" são pares "### Pergunta" + resposta, que viram o FAQ
visível e o schema FAQPage. Artigo com revisado: nao mostra aviso de rascunho e não entra
no feed nem no sitemap.
"""
import html
import json
import math
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_reviva import tamanho_jpeg  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "blog"
OUT = ROOT / "blog"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
NOME = "MRO Brasil 2027"


def esc(t):
    return html.escape(str(t), quote=True)


def data_br(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def slug_de(texto):
    import unicodedata
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return "-".join(re.findall(r"[a-z0-9]+", t))[:60].rstrip("-")


# ---------------------------------------------------------------- Markdown simples
def link(destino, raiz):
    if destino.startswith("#/"):
        return f"{raiz}index.html{destino}", ""
    if destino.startswith("http"):
        return destino, ' target="_blank" rel="noopener"'
    return destino, ""


def inline(texto, raiz):
    t = esc(texto)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)

    def l(m):
        href, extra = link(html.unescape(m.group(2)), raiz)
        sr = '<span class="sr-only"> (abre em nova aba)</span>' if extra else ""
        return f'<a href="{esc(href)}"{extra}>{m.group(1)}{sr}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", l, t)


def blocos(linhas, raiz):
    """Converte linhas em HTML. Retorna (html, textos de parágrafo)."""
    out, para, lista, tipo = [], [], [], None

    def fecha_para():
        if para:
            out.append(f"<p>{inline(' '.join(para), raiz)}</p>")
            para.clear()

    def fecha_lista():
        nonlocal tipo
        if lista:
            tag = "ol" if tipo == "ol" else "ul"
            out.append(f"<{tag}>\n" + "\n".join(f"<li>{inline(i, raiz)}</li>" for i in lista) + f"\n</{tag}>")
            lista.clear()
        tipo = None

    for ln in linhas:
        ln = ln.rstrip()
        if not ln:
            fecha_para(); fecha_lista(); continue
        m = re.match(r"^(#{2,3}) (.+)$", ln)
        if m:
            fecha_para(); fecha_lista()
            n = len(m.group(1))
            titulo = m.group(2)
            out.append(f'<h{n} id="{slug_de(titulo)}">{inline(titulo, raiz)}</h{n}>')
            continue
        m = re.match(r"^(?:- |(\d+)\. )(.+)$", ln)
        if m:
            fecha_para()
            novo = "ol" if m.group(1) else "ul"
            if tipo and tipo != novo:
                fecha_lista()
            tipo = novo
            lista.append(m.group(2))
            continue
        fecha_lista()
        para.append(ln)
    fecha_para(); fecha_lista()
    return "\n".join(out)


def ler_artigo(arq, raiz_artigo):
    bruto = arq.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", bruto, re.S)
    if not m:
        sys.exit(f"ERRO em {arq.name}: faltou o cabeçalho entre linhas ---")
    meta = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    for campo in ("titulo", "resumo", "data", "categoria", "imagem", "imagem_alt"):
        if not meta.get(campo):
            sys.exit(f'ERRO em {arq.name}: falta "{campo}" no cabeçalho')
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["data"]):
        sys.exit(f"ERRO em {arq.name}: data deve ser AAAA-MM-DD")
    img = ROOT / "assets" / "img" / f"{meta['imagem']}.jpg"
    if not img.exists():
        sys.exit(f"ERRO em {arq.name}: imagem assets/img/{meta['imagem']}.jpg não existe")
    corpo, _, faq_bruto = m.group(2).partition("\n## Perguntas frequentes")
    faq = []
    atual = None
    for ln in faq_bruto.splitlines():
        if ln.startswith("### "):
            atual = {"p": ln[4:].strip(), "r": []}
            faq.append(atual)
        elif atual is not None and ln.strip():
            atual["r"].append(ln.strip())
    palavras = len(re.findall(r"\w+", corpo)) + sum(len(re.findall(r"\w+", " ".join(f["r"]))) for f in faq)
    meta.update({
        "slug": arq.stem,
        "corpo": corpo.strip().splitlines(),
        "faq": [{"p": f["p"], "r": " ".join(f["r"])} for f in faq],
        "minutos": max(1, math.ceil(palavras / 200)),
        "revisado": meta.get("revisado", "nao").lower() in ("sim", "true", "s"),
    })
    if len(meta["resumo"]) > 170:
        print(f"  aviso ({arq.name}): resumo com {len(meta['resumo'])} caracteres; ideal até 160 para a descrição nos buscadores")
    return meta


# ---------------------------------------------------------------- Casca do site
def casca():
    doc = (ROOT / "index.html").read_text(encoding="utf-8")
    pega = lambda padrao: re.search(padrao, doc, re.S).group(0)
    return {
        "sprite": pega(r'<svg xmlns="http://www.w3.org/2000/svg" class="sprite".*?</svg>'),
        "topo": pega(r'<div class="topbar">.*?</header>'),
        "rodape": pega(r'<footer class="site-footer">.*?</footer>'),
        "robots": pega(r'<meta name="robots"[^>]*>'),
        "robots_noindex": pega(r'<meta name="robots"[^>]*>'),
    }


def reescreve(trecho, raiz, atual=None):
    """Ajusta o HTML copiado de index.html: links de rota e arquivos relativos à pasta do blog."""
    trecho = trecho.replace('<button type="button" class="topbar__btn" data-open-perfil>Escolher perfil</button>',
                            '<a class="topbar__btn" href="#/participar">Participar</a>')
    trecho = trecho.replace('<button type="button" class="btn btn--light" data-open-perfil>Escolher perfil de participação</button>',
                            '<a class="btn btn--light" href="#/participar">Participar da MRO Brasil 2027</a>')
    trecho = re.sub(r'href="#/', f'href="{raiz}index.html#/', trecho)
    trecho = re.sub(r'(src|href)="(?!#|https?:|mailto:|tel:|data:|\.\./)([^"]+)"', lambda m: f'{m.group(1)}="{raiz}{m.group(2)}"', trecho)
    if atual:
        trecho = trecho.replace(f'<a href="{raiz}blog/index.html" data-nav="blog">', f'<a href="{raiz}blog/index.html" data-nav="blog" aria-current="{atual}">')
    return trecho


def pagina(c, raiz, titulo, descricao, corpo, extra_head="", canonico=None, og_tipo="website", og_imagem=None):
    cano = f'<link rel="canonical" href="{esc(canonico)}">\n<meta property="og:url" content="{esc(canonico)}">\n' if canonico else ""
    og_img = f'<meta property="og:image" content="{esc(og_imagem)}">\n' if og_imagem else ""
    tw_img = f'<meta name="twitter:image" content="{esc(og_imagem)}">\n' if og_imagem else ""
    md_alt = '<link rel="alternate" type="text/markdown" href="index.md" title="Versão em Markdown">\n' if canonico else ""
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descricao)}">
{c["robots"]}
<meta name="theme-color" content="#0A1438">
<link rel="icon" type="image/png" href="{raiz}assets/img/favicon.png">
{cano}<meta property="og:type" content="{og_tipo}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{NOME}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
{og_img}<meta name="twitter:card" content="summary_large_image">
{tw_img}{md_alt}
<link rel="stylesheet" href="{raiz}src/styles.css">
{extra_head}</head>
<body>
{reescreve(c["sprite"], raiz)}

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

{{TOPO}}

<main id="conteudo" tabindex="-1">
{corpo}
</main>

{{RODAPE}}

<script src="{raiz}src/blog.js"></script>
</body>
</html>
'''


def imagem_tag(base, alt, raiz, grande=False, eager=False):
    """Imagem do artigo com srcset a partir de -800 e original."""
    orig = ROOT / "assets" / "img" / f"{base}.jpg"
    peq = ROOT / "assets" / "img" / f"{base}-800.jpg"
    w, h = tamanho_jpeg(orig)
    srcset = ""
    if peq.exists():
        pw, _ = tamanho_jpeg(peq)
        srcset = f' srcset="{raiz}assets/img/{base}-800.jpg {pw}w, {raiz}assets/img/{base}.jpg {w}w" sizes="{"(min-width: 900px) 960px, 100vw" if grande else "(min-width: 900px) 400px, 100vw"}"'
    carga = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{raiz}assets/img/{base}.jpg"{srcset} width="{w}" height="{h}" alt="{esc(alt)}" {carga} decoding="async">'


# ---------------------------------------------------------------- Páginas
def cartao(a, raiz, com_tag=True):
    rasc = '<span class="tag tag--demo">Rascunho</span> ' if (com_tag and not a["revisado"]) else ""
    return (f'<li class="blog-card">\n<div class="blog-card__media">{imagem_tag(a["imagem"], a["imagem_alt"], raiz)}</div>\n'
            f'<div class="blog-card__body">\n<p class="kicker">{esc(a["categoria"])}</p>\n'
            f'<h2 class="blog-card__title"><a href="{raiz}blog/{a["slug"]}/index.html">{esc(a["titulo"])}</a></h2>\n'
            f'<p class="blog-card__text">{esc(a["resumo"])}</p>\n'
            f'<p class="blog-card__meta">{rasc}<time datetime="{a["data"]}">{data_br(a["data"])}</time> · {a["minutos"]} min de leitura</p>\n</div>\n</li>')


def gerar_indice(c, artigos, cfg):
    raiz = "../"
    cards = "\n".join(cartao(a, raiz) for a in artigos)
    corpo = f'''<section class="page" aria-labelledby="h-blog">
  <header class="page-head">
    <div class="container">
      <nav class="crumbs" aria-label="Você está em"><ol><li><a href="{raiz}index.html#/">Início</a></li><li aria-current="page">Blog</li></ol></nav>
      <h1 id="h-blog" class="display" tabindex="-1">Blog</h1>
      <p class="lead">Artigos sobre manutenção aeronáutica, o mercado de MRO e a MRO Brasil 2027.</p>
    </div>
  </header>
  <section class="section section--flush" aria-label="Artigos">
    <div class="container">
      <ul class="blog-grid">
{cards}
      </ul>
    </div>
  </section>
</section>'''
    url = cfg.get("url_base")
    schema = ""
    if url:
        schema = ('<script type="application/ld+json">\n' + json.dumps({
            "@context": "https://schema.org", "@type": "Blog", "name": f"Blog {NOME}", "inLanguage": "pt-BR", "url": f"{url}/blog/",
            "blogPost": [{"@type": "BlogPosting", "headline": a["titulo"], "url": f"{url}/blog/{a['slug']}/"} for a in artigos if a["revisado"]]},
            ensure_ascii=False, indent=2) + "\n</script>\n")
    texto = pagina(c, raiz, f"Blog | {NOME} · Manutenção Aeronáutica",
                   "Artigos sobre manutenção aeronáutica, o mercado de MRO e a MRO Brasil 2027, feira internacional realizada em São Paulo.",
                   corpo, schema + (f'<link rel="alternate" type="application/rss+xml" title="Blog {NOME}" href="feed.xml">\n' if url else ""),
                   canonico=f"{url}/blog/" if url else None, og_imagem=f"{url}/assets/img/og-mro2027.jpg" if url else None)
    texto = texto.replace("{TOPO}", reescreve(c["topo"], raiz, "page")).replace("{RODAPE}", reescreve(c["rodape"], raiz))
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(texto, encoding="utf-8")


def faq_html(faq, raiz):
    itens = "".join(
        f'<details class="faq-item"><summary>{esc(f["p"])}</summary><div class="faq-item__a"><p>{inline(f["r"], raiz)}</p></div></details>\n'
        for f in faq)
    return (f'<section class="post__faq" aria-labelledby="h-faq-post">\n<h2 id="h-faq-post" class="faq-group__title">Perguntas frequentes</h2>\n'
            f'<div class="faq-list">\n{itens}</div>\n</section>')


def gerar_artigo(c, a, todos, cfg):
    if not a["revisado"]:
        c = dict(c, robots=c["robots_noindex"])  # rascunho nunca é indexado
    raiz = "../../"
    url = cfg.get("url_base")
    link_abs = f"{url}/blog/{a['slug']}/" if url else None
    aviso = ("" if a["revisado"] else
             '<p class="status-note"><svg class="ico" aria-hidden="true"><use href="#i-info"/></svg>'
             "<span><strong>Rascunho em revisão pela organização.</strong> Este texto ainda não foi aprovado para publicação.</span></p>\n")
    outros = [o for o in todos if o["slug"] != a["slug"]][:2]
    relacionados = ""
    if outros:
        relacionados = ('<section class="post__more" aria-labelledby="h-mais"><div class="container">\n<h2 id="h-mais" class="h3">Continue lendo</h2>\n<ul class="blog-grid blog-grid--2">\n'
                        + "\n".join(cartao(o, raiz) for o in outros) + "\n</ul>\n</div></section>")
    corpo = f'''<section class="page" aria-labelledby="h-post">
  <header class="page-head">
    <div class="container post__head">
      <nav class="crumbs" aria-label="Você está em"><ol><li><a href="{raiz}index.html#/">Início</a></li><li><a href="{raiz}blog/index.html">Blog</a></li><li aria-current="page">{esc(a["categoria"])}</li></ol></nav>
      <p class="eyebrow eyebrow--light"><span class="eyebrow__index">—</span> {esc(a["categoria"])}</p>
      <h1 id="h-post" class="display" tabindex="-1">{esc(a["titulo"])}</h1>
      <p class="lead">{esc(a["resumo"])}</p>
      <p class="post__meta"><time datetime="{a["data"]}">{data_br(a["data"])}</time> · {esc(cfg.get("autor", "Organização da MRO Brasil"))} · {a["minutos"]} min de leitura</p>
    </div>
  </header>
  <article class="section section--flush post">
    <div class="container post__grid">
      <figure class="post__hero">{imagem_tag(a["imagem"], a["imagem_alt"], raiz, grande=True, eager=True)}</figure>
      <div class="post__body prose">
{aviso}{blocos(a["corpo"], raiz)}
{faq_html(a["faq"], raiz) if a["faq"] else ""}
      </div>
    </div>
  </article>
  {relacionados}
  <section class="cta-band" aria-labelledby="h-cta-post">
    <div class="container cta-band__inner">
      <h2 id="h-cta-post" class="h2 h2--light">MRO Brasil 2027: 20 e 21 de outubro, em São Paulo.</h2>
      <div class="actions"><a class="btn btn--primary btn--lg" href="{raiz}index.html#/participar">Participar da MRO Brasil 2027 <svg class="ico" aria-hidden="true"><use href="#i-arrow"/></svg></a></div>
    </div>
  </section>
</section>'''
    grafo = []
    post = {"@type": "BlogPosting", "headline": a["titulo"], "description": a["resumo"], "inLanguage": "pt-BR",
            "datePublished": a["data"], "dateModified": a.get("atualizado") or a["data"],
            "author": {"@type": "Organization", "name": cfg.get("autor", "Organização da MRO Brasil")},
            "publisher": {"@type": "Organization", "name": NOME}}
    if url:
        post["mainEntityOfPage"] = link_abs
        post["image"] = f"{url}/assets/img/{a['imagem']}.jpg"
    grafo.append(post)
    if a["faq"]:
        grafo.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["p"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", f["r"])}} for f in a["faq"]]})
    if url:
        grafo.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{url}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{url}/blog/"},
            {"@type": "ListItem", "position": 3, "name": a["titulo"], "item": link_abs}]})
    schema = '<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=2) + "\n</script>\n"
    titulo = a.get("titulo_seo") or f"{a['titulo']} | Blog {NOME}"
    texto = pagina(c, raiz, titulo, a["resumo"], corpo, schema, canonico=link_abs, og_tipo="article",
                   og_imagem=f"{url}/assets/img/{a['imagem']}.jpg" if url else None)
    texto = texto.replace("{TOPO}", reescreve(c["topo"], raiz, "true")).replace("{RODAPE}", reescreve(c["rodape"], raiz))
    pasta = OUT / a["slug"]
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "index.html").write_text(texto, encoding="utf-8")


def gerar_feed(artigos, cfg):
    url = cfg.get("url_base")
    pub = [a for a in artigos if a["revisado"]]
    if not url:
        print("  url_base vazio em content/blog/config.json: feed.xml e sitemap.xml não gerados")
        for f in ("feed.xml", "sitemap.xml"):
            (OUT / f).unlink(missing_ok=True)
        return
    itens = "\n".join(
        f"<item><title>{esc(a['titulo'])}</title><link>{url}/blog/{a['slug']}/</link><guid>{url}/blog/{a['slug']}/</guid>"
        f"<pubDate>{date.fromisoformat(a['data']).strftime('%a, %d %b %Y')} 00:00:00 +0000</pubDate><description>{esc(a['resumo'])}</description></item>"
        for a in pub)
    (OUT / "feed.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Blog {NOME}</title><link>{url}/blog/</link>'
        f"<description>Artigos sobre manutenção aeronáutica e a MRO Brasil 2027.</description><language>pt-BR</language>\n{itens}\n</channel></rss>\n", encoding="utf-8")
    urls = [f"{url}/blog/"] + [f"{url}/blog/{a['slug']}/" for a in pub]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"<url><loc>{u}</loc></url>" for u in urls) + "\n</urlset>\n", encoding="utf-8")


def destaques_home(artigos):
    """Bloco "Últimos artigos" da home (index.html): só artigos revisados; sem eles, o bloco some."""
    pub = [a for a in artigos if a["revisado"]][:3]
    if pub:
        bloco = ('<section class="section section--tint blog-teaser" aria-labelledby="h-blog-home">\n'
                 '<div class="container">\n<header class="blog-teaser__head">\n<p class="kicker">Blog</p>\n'
                 '<h2 id="h-blog-home" class="h2">Artigos sobre manutenção aeronáutica</h2>\n'
                 '<a class="link-more" href="blog/index.html">Ver todos os artigos <svg class="ico" aria-hidden="true"><use href="#i-arrow"/></svg></a>\n</header>\n'
                 '<ul class="blog-grid">\n' + "\n".join(cartao(a, "", com_tag=False) for a in pub) + '\n</ul>\n</div>\n</section>')
    else:
        bloco = ""
    alvo = ROOT / "index.html"
    doc = alvo.read_text(encoding="utf-8")
    doc = re.sub(r"(<!-- BLOG:DESTAQUES -->).*?(<!-- /BLOG:DESTAQUES -->)", lambda m: m.group(1) + "\n" + bloco + "\n" + m.group(2), doc, flags=re.S)
    alvo.write_text(doc, encoding="utf-8")


def carregar_artigos():
    return sorted((ler_artigo(p, "") for p in SRC.glob("*.md")), key=lambda a: a["data"], reverse=True)


def construir(saida, cfg, artigos, robots=None):
    """Grava listagem e artigos em `saida`. `robots` troca a meta robots das páginas publicáveis."""
    global OUT
    OUT = Path(saida)
    if OUT.exists():
        shutil.rmtree(OUT)
    c = casca()
    if robots:
        c["robots"] = robots
    gerar_indice(c, artigos, cfg)
    for a in artigos:
        gerar_artigo(c, a, artigos, cfg)
    gerar_feed(artigos, cfg)


def main():
    cfg = json.loads((SRC / "config.json").read_text(encoding="utf-8"))
    artigos = carregar_artigos()
    if not artigos:
        sys.exit("Nenhum artigo em content/blog/")
    construir(ROOT / "blog", cfg, artigos)
    destaques_home(artigos)
    print(f"Blog: {len(artigos)} artigos ({sum(a['revisado'] for a in artigos)} revisados)")


if __name__ == "__main__":
    main()
