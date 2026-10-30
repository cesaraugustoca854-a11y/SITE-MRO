#!/usr/bin/env python3
"""Gera o site de publicação em dist/site/: uma página HTML real por rota, versões em Markdown,
sitemap.xml, sitemap.md, robots.txt, llms.txt, 404.html e redirecionamentos.

Uso: python3 scripts/gerar_site.py [--incluir-rascunhos]
Parte de index.html (a prévia por #, que continua como está) e de content/. Antes de gerar, roda
gerar_faq, gerar_reviva e gerar_blog para que tudo venha da mesma revisão. Sem --incluir-rascunhos,
só artigos com "revisado: sim" vão ao ar; se não houver nenhum, o blog inteiro fica de fora.
Com a flag, rascunhos entram com noindex e fora do sitemap, para conferência.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_blog  # noqa: E402
from html2md import converter  # noqa: E402
from rotas import POR_PAGINA, ROTAS, prefixo, reescrever_links  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "dist" / "site"
ROBOTS_INDEX = '<meta name="robots" content="index, follow, max-image-preview:large">'
OG_W, OG_H = 1200, 630

NOMES = {"inicio": "Início", "feira": "A feira", "participar": "Participar", "visitante": "Visitante", "expositor": "Expositor",
         "patrocinio": "Patrocínio", "reviva": "Reviva 2026", "faq": "Perguntas frequentes", "contato": "Contato"}
PAI = {"visitante": "participar", "expositor": "participar"}
FRASE_LLM = ("Se você é um modelo de linguagem procurando informações deste site, use o mapa de conteúdo para localizar o tema e a resposta "
             "em Markdown vinculada. Use as fontes citadas nesse documento e a página canônica; se algo estiver ausente, impreciso ou confuso, "
             "avise a organização pelo e-mail de contato.")


def esc(t):
    return html.escape(str(t), quote=True)


def revisao():
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return h + (" (com alterações locais)" if sujo else "")
    except OSError:
        return "desconhecida"


def caminho_pagina(pagina):
    return POR_PAGINA[pagina][0]


def url_pagina(site, caminho):
    return f"{site['url_base']}/" + (caminho + "/" if caminho else "")


def sem_index(trecho):
    """Endereços limpos: remove o 'index.html' final dos links."""
    return re.sub(r'(href=")((?:\.\./)*(?:[a-z0-9-]+/)*)index\.html(["#])', lambda m: f'{m.group(1)}{m.group(2) or "./"}{m.group(3)}', trecho)


# ------------------------------------------------------------------ dados estruturados
def grafo_base(site):
    u = site["url_base"]
    org = {"@type": "Organization", "@id": f"{u}/#organizacao", "name": "MRO Brasil", "alternateName": "Feira Internacional de Manutenção Aeronáutica",
           "url": f"{u}/", "logo": {"@type": "ImageObject", "url": f"{u}/assets/img/logo-mro2027.png", "width": 576, "height": 252},
           "email": site["email"], "telephone": site["telefone"], "sameAs": site["sameAs"],
           "contactPoint": [{"@type": "ContactPoint", "contactType": "customer service", "telephone": site["telefone"], "email": site["email"], "availableLanguage": "pt-BR"}]}
    web = {"@type": "WebSite", "@id": f"{u}/#site", "url": f"{u}/", "name": site["nome"], "inLanguage": "pt-BR", "publisher": {"@id": f"{u}/#organizacao"}}
    return org, web


def evento(site, doc_head):
    u = site["url_base"]
    bruto = re.search(r'<script type="application/ld\+json">\s*(\{\s*"@context": "https://schema.org",\s*"@type": "Event".*?)</script>', doc_head, re.S)
    ev = json.loads(bruto.group(1))
    ev.pop("@context", None)
    ev.update({"@id": f"{u}/#evento", "url": f"{u}/", "image": [f"{u}/assets/img/og-mro2027.jpg"], "organizer": {"@type": "Organization", "name": ev["organizer"]["name"],
               "email": site["email"], "telephone": site["telefone"]}})
    for sub in ev.get("subEvent", []):  # datas de cada evento ainda não confirmadas: não repetir as da feira
        sub.pop("startDate", None); sub.pop("endDate", None)
    return ev


def jsonld(grafo):
    return '<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=2) + "\n</script>"


def blocos_pagina(doc_head, marca):
    m = re.search(rf"<!-- {marca} -->(.*?)<!-- /{marca} -->", doc_head, re.S)
    if not m:
        return None
    return re.search(r"<script type=\"application/ld\+json\">\s*(.*?)\s*</script>", m.group(1), re.S)


def esquema_pagina(site, pagina, caminho, titulo, descricao, doc_head):
    u, url = site["url_base"], url_pagina(site, caminho)
    org, web = grafo_base(site)
    grafo = [org, web]
    web_page = {"@type": "FAQPage" if pagina == "faq" else "WebPage", "@id": f"{url}#pagina", "url": url, "name": titulo, "description": descricao, "inLanguage": "pt-BR",
                "isPartOf": {"@id": f"{u}/#site"}, "dateModified": site["atualizado"]}
    if pagina in ("inicio", "feira"):
        web_page["about"] = {"@id": f"{u}/#evento"}
    if pagina == "faq":
        faq = json.loads(blocos_pagina(doc_head, "FAQ:JSONLD").group(1))
        web_page["mainEntity"] = faq["mainEntity"]
    grafo.append(web_page)
    if pagina in ("inicio", "feira"):
        grafo.append(evento(site, doc_head))
    if pagina == "reviva":
        vid = blocos_pagina(doc_head, "REVIVA:SCHEMA")
        if vid:
            grafo += json.loads(vid.group(1)).get("@graph", [])
    if pagina != "inicio":
        trilha = [("Início", f"{u}/")]
        if pagina in PAI:
            trilha.append((NOMES[PAI[pagina]], url_pagina(site, caminho_pagina(PAI[pagina]))))
        trilha.append((NOMES[pagina], url))
        grafo.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": a} for i, (n, a) in enumerate(trilha)]})
    return jsonld(grafo)


# ------------------------------------------------------------------ montagem de páginas
def paginas_de(doc):
    """Cada <section class="page"> vai até a seguinte (ou até </main>); o miolo tem seções em coluna 0."""
    inicios = list(re.finditer(r'<section class="page" data-page="([\w-]+)"', doc))
    fim_main = doc.index("</main>")
    paginas = {}
    for i, m in enumerate(inicios):
        fim = inicios[i + 1].start() if i + 1 < len(inicios) else fim_main
        trecho = doc[m.start():fim]
        trecho = re.sub(r"\n<!--[^>]*-->\s*$", "\n", trecho.rstrip() + "\n")  # comentário de abertura da próxima página
        trecho = re.sub(r"\n<!-- =+ [^>]*=+ -->\s*$", "\n", trecho)
        paginas[m.group(1)] = trecho.rstrip() + "\n"
    return paginas


def extrair(doc):
    cabeca, corpo = doc.split("</head>", 1)
    return {
        "cabeca": cabeca,
        "sprite": re.search(r'<svg xmlns="http://www.w3.org/2000/svg" class="sprite".*?</svg>', doc, re.S).group(0),
        "topo": re.search(r'<div class="topbar">.*?</header>', doc, re.S).group(0),
        "rodape": re.search(r'<footer class="site-footer">.*?</footer>', doc, re.S).group(0),
        "dialogos": re.search(r"<!-- Pop-up de escolha de perfil -->.*?(?=<noscript><p class=\"noscript\")", doc, re.S).group(0),
        "paginas": paginas_de(doc),
    }


def cabeca_pagina(site, pagina, caminho, titulo, descricao, schema, md_href, com_blog, noindex=False):
    u, url, raiz = site["url_base"], url_pagina(site, caminho), prefixo(caminho)
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ROBOTS_INDEX
    preload = (f'<link rel="preload" as="image" href="{raiz}assets/img/folder-jato.jpg" imagesrcset="{raiz}assets/img/folder-jato-800.jpg 800w, {raiz}assets/img/folder-jato.jpg 1600w" '
               'imagesizes="(min-width: 900px) 52vw, 100vw">\n') if pagina == "inicio" else ""
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descricao)}">
{robots}
<link rel="canonical" href="{url}">
<link rel="alternate" type="text/markdown" href="{md_href}" title="Versão em Markdown">
<meta name="theme-color" content="#0A1438">
<link rel="icon" type="image/png" href="{raiz}assets/img/favicon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{esc(site['nome'])}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{u}/assets/img/og-mro2027.jpg">
<meta property="og:image:width" content="{OG_W}">
<meta property="og:image:height" content="{OG_H}">
<meta property="og:image:alt" content="MRO Brasil 2027, Feira Internacional de Manutenção Aeronáutica, 20 e 21 de outubro de 2027, São Paulo.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(titulo)}">
<meta name="twitter:description" content="{esc(descricao)}">
<meta name="twitter:image" content="{u}/assets/img/og-mro2027.jpg">
{preload}<link rel="stylesheet" href="{raiz}src/styles.css">
{schema}
</head>
'''


def montar_pagina(site, partes, pagina, caminho, com_blog, base_href=None):
    secao = partes["paginas"][pagina]
    titulo = re.search(r'data-title="([^"]+)"', secao).group(1)
    descricao = re.search(r'data-description="([^"]+)"', secao).group(1)
    secao = re.sub(r'(<section class="page" data-page="[\w-]+"[^>]*?)\s+hidden', r"\1", secao, count=1)
    secao = re.sub(r'href="#/perguntas-frequentes/\w+" data-faq-open="(q-[^"]+)"', r'href="@@FAQ@@\1"', secao)
    md_href = "index.md" if base_href is None else "index.md"
    schema = esquema_pagina(site, pagina, caminho, html.unescape(titulo), html.unescape(descricao), partes["cabeca"]) if pagina != "nao-encontrada" else ""
    topo, rodape = partes["topo"], partes["rodape"]
    if not com_blog:
        topo = re.sub(r'\s*<li><a href="blog/index.html" data-nav="blog">Blog</a></li>', "", topo)
        rodape = re.sub(r'\s*<li><a href="blog/index.html">Blog</a></li>', "", rodape)
    corpo = f'''<body>
{partes["sprite"]}

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

{topo}

<main id="conteudo" tabindex="-1">
<p class="sr-only" id="anuncio-rota" aria-live="polite"></p>

{secao}</main>

{rodape}

{partes["dialogos"]}
<script>window.MRO_MPA = {{ page: "{pagina}" }};</script>
<script src="{{RAIZ}}src/lead-adapter.js"></script>
<script src="{{RAIZ}}src/app.js"></script>
</body>
</html>
'''
    corpo = sem_index(reescrever_links(corpo, pagina, caminho)).replace("{RAIZ}", prefixo(caminho))
    corpo = re.sub(r'href="(?:\.\./)*@@FAQ@@(q-[^"]+)"', lambda m: f'href="{prefixo(caminho)}perguntas-frequentes/#{m.group(1)}"', corpo)
    # a rota "inicio" aponta para a raiz; reescrever_links mantém "#conteudo" quando é a mesma página
    cabeca = cabeca_pagina(site, pagina, caminho, html.unescape(titulo), html.unescape(descricao), schema, md_href, com_blog, noindex=(pagina == "nao-encontrada"))
    if base_href:
        cabeca = cabeca.replace("<head>\n", f'<head>\n<base href="{base_href}">\n', 1)
    secao_md = sem_index(reescrever_links(secao, pagina, caminho))
    secao_md = re.sub(r'href="(?:\.\./)*@@FAQ@@(q-[^"]+)"', lambda m: f'href="{prefixo(caminho)}perguntas-frequentes/#{m.group(1)}"', secao_md)
    return cabeca + corpo, html.unescape(titulo), html.unescape(descricao), secao_md


# ------------------------------------------------------------------ Markdown
def md_links(md):
    """Links internos para páginas viram links para o .md equivalente."""
    def trocar(m):
        alvo = m.group(2)
        if alvo.startswith(("http", "mailto:", "tel:", "#")):
            return m.group(0)
        base, _, ancora = alvo.partition("#")
        if base == "" or base.endswith("/"):
            base += "index.md"
        return f"[{m.group(1)}]({base})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", trocar, md)


def documento_md(site, titulo, descricao, url, secao_html, rev, finalidade):
    corpo = md_links(converter(secao_html))
    return (f"{corpo.splitlines()[0] if corpo.startswith('# ') else '# ' + titulo}\n\n"
            f"- Página canônica: {url}\n- Idioma: pt-BR\n- Finalidade: {finalidade}\n- Atualizado em: {site['atualizado']}\n"
            f"- Revisão da fonte: {rev}\n- Responsável: {site['responsavel']}\n- Resumo: {descricao}\n\n"
            + (corpo.split("\n", 1)[1].lstrip("\n") if corpo.startswith("# ") else corpo))


def md_artigo(site, a, url, rev):
    corpo = "\n".join(a["corpo"])
    corpo = re.sub(r"\]\(#/([^)]*)\)", lambda m: f"]({site['url_base']}/{m.group(1).strip('/')}/)", corpo)
    faq = "\n\n## Perguntas frequentes\n\n" + "\n\n".join(f"### {f['p']}\n\n{f['r']}" for f in a["faq"]) if a["faq"] else ""
    faq = re.sub(r"\]\(#/([^)]*)\)", lambda m: f"]({site['url_base']}/{m.group(1).strip('/')}/)", faq)
    return (f"# {a['titulo']}\n\n- Página canônica: {url}\n- Idioma: pt-BR\n- Finalidade: artigo do blog ({a['categoria']})\n- Publicado em: {a['data']}\n"
            f"- Atualizado em: {a.get('atualizado') or a['data']}\n- Revisão da fonte: {rev}\n- Responsável: {site['responsavel']}\n- Resumo: {a['resumo']}\n\n{corpo}{faq}\n")


# ------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incluir-rascunhos", action="store_true", help="inclui artigos não revisados (noindex, fora do sitemap)")
    args = ap.parse_args()

    for s in ("gerar_faq.py", "gerar_reviva.py", "gerar_blog.py"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / s)], check=True, capture_output=True)

    site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
    u = site["url_base"]
    rev = revisao()
    partes = extrair((ROOT / "index.html").read_text(encoding="utf-8"))

    todos = gerar_blog.carregar_artigos()
    escolhidos = [a for a in todos if a["revisado"] or args.incluir_rascunhos]
    com_blog = bool(escolhidos)

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    SAIDA.mkdir(parents=True)
    for pasta in ("assets", "src"):
        shutil.copytree(ROOT / pasta, SAIDA / pasta, ignore=shutil.ignore_patterns(".DS_Store"))
    if not com_blog:
        (SAIDA / "src" / "blog.js").unlink(missing_ok=True)

    paginas_md = []  # (titulo, descricao, url, caminho_md)
    for caminho, pagina, _, _ in ROTAS:
        pasta = SAIDA / caminho if caminho else SAIDA
        pasta.mkdir(parents=True, exist_ok=True)
        doc, titulo, descricao, secao = montar_pagina(site, partes, pagina, caminho, com_blog)
        (pasta / "index.html").write_text(doc, encoding="utf-8")
        url = url_pagina(site, caminho)
        (pasta / "index.md").write_text(documento_md(site, titulo, descricao, url, secao, rev, f"versão em texto da página {NOMES[pagina]}"), encoding="utf-8")
        paginas_md.append((NOMES[pagina], descricao, url, (caminho + "/" if caminho else "") + "index.md"))

    # 404: base absoluta, pois o servidor a entrega em qualquer profundidade
    doc404, *_ = montar_pagina(site, partes, "nao-encontrada", "", com_blog, base_href="/")
    (SAIDA / "404.html").write_text(doc404, encoding="utf-8")

    # Blog
    artigos_md = []
    if com_blog:
        cfg = {"url_base": u, "autor": "Organização da MRO Brasil"}
        cfg_blog = json.loads((ROOT / "content" / "blog" / "config.json").read_text(encoding="utf-8"))
        cfg["autor"] = cfg_blog.get("autor", cfg["autor"])
        gerar_blog.construir(SAIDA / "blog", cfg, escolhidos, robots=ROBOTS_INDEX)
        (SAIDA / "blog" / "sitemap.xml").unlink(missing_ok=True)  # o sitemap único fica na raiz
        for arq in (SAIDA / "blog").rglob("index.html"):
            rel = arq.relative_to(SAIDA).parent.as_posix()
            texto = arq.read_text(encoding="utf-8")
            pg = "blog"
            texto = re.sub(r'href="((?:\.\./)+)index\.html(#/[^"]*)"', lambda m: f'href="{reescrever_um(m.group(2), rel)}"', texto)
            texto = sem_index(texto)
            texto = texto.replace('<link rel="alternate" type="application/rss+xml"', '<link rel="alternate" type="application/rss+xml"')
            arq.write_text(texto, encoding="utf-8")
        for a in escolhidos:
            url = f"{u}/blog/{a['slug']}/"
            (SAIDA / "blog" / a["slug"] / "index.md").write_text(md_artigo(site, a, url, rev), encoding="utf-8")
            artigos_md.append((a, url))
        (SAIDA / "blog" / "index.md").write_text(
            f"# Blog {site['nome']}\n\n- Página canônica: {u}/blog/\n- Idioma: pt-BR\n- Finalidade: lista de artigos\n- Atualizado em: {site['atualizado']}\n- Revisão da fonte: {rev}\n- Responsável: {site['responsavel']}\n\n"
            + "\n".join(f"- [{a['titulo']}]({a['slug']}/index.md): {a['resumo']}" for a in escolhidos) + "\n", encoding="utf-8")

    # sitemap.xml
    comentario = f"Mapa de conteúdo em Markdown: {u}/sitemap.md. Guia para leitores automáticos: {u}/llms.txt."
    urls = [(url_pagina(site, c), site["atualizado"]) for c, p, _, _ in ROTAS]
    if com_blog:
        if any(a["revisado"] for a in escolhidos):
            urls.append((f"{u}/blog/", max(a["data"] for a in escolhidos if a["revisado"])))
        urls += [(f"{u}/blog/{a['slug']}/", a.get("atualizado") or a["data"]) for a in escolhidos if a["revisado"]]
    (SAIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"<!-- {comentario} -->\n" + "\n".join(f"<url><loc>{l}</loc><lastmod>{d}</lastmod></url>" for l, d in urls) + "\n</urlset>\n", encoding="utf-8")

    # robots.txt
    (SAIDA / "robots.txt").write_text(
        f"# {comentario}\nUser-agent: *\nAllow: /\n\nSitemap: {u}/sitemap.xml\n", encoding="utf-8")

    # sitemap.md (mapa de conteúdo por tema)
    temas = [("A feira", ["A feira", "Início"]), ("Participar", ["Participar", "Visitante", "Expositor", "Patrocínio"]),
             ("Edição anterior e feira virtual", ["Reviva 2026"]), ("Dúvidas e contato", ["Perguntas frequentes", "Contato"])]
    por_nome = {n: (d, uu, m) for n, d, uu, m in paginas_md}
    linhas = [f"# Mapa de conteúdo: {site['nome']}\n", f"Feira Internacional de Manutenção Aeronáutica, 20 e 21 de outubro de 2027, Centro de Convenções Frei Caneca, São Paulo (SP). "
              f"Cada item leva à resposta em Markdown e à página canônica. Atualizado em {site['atualizado']}.\n"]
    for tema, nomes in temas:
        linhas.append(f"## {tema}\n")
        for n in nomes:
            d, uu, m = por_nome[n]
            linhas.append(f"- [{n}]({m}): {d} ([página]({uu}))")
        linhas.append("")
    if artigos_md:
        linhas.append("## Blog\n")
        linhas += [f"- [{a['titulo']}](blog/{a['slug']}/index.md): {a['resumo']} ([página]({url}))" for a, url in artigos_md]
        linhas.append("")
    (SAIDA / "sitemap.md").write_text("\n".join(linhas), encoding="utf-8")

    # llms.txt
    faq_md = f"{u}/perguntas-frequentes/index.md"
    llms = [f"# {site['nome']} — Feira Internacional de Manutenção Aeronáutica", "",
            "> Feira dedicada à cadeia de manutenção, reparo e revisão (MRO) aeronáutica. 20 e 21 de outubro de 2027, Centro de Convenções Frei Caneca, "
            "Rua Frei Caneca, 569, Bela Vista, São Paulo (SP). Tema 2027: “A inteligência na revolução do MRO”.", "",
            FRASE_LLM, "",
            f"Mapa de conteúdo: {u}/sitemap.md", f"Perguntas e respostas: {faq_md}", "", "## Páginas", ""]
    llms += [f"- [{n}]({u}/{m}): {d}" for n, d, uu, m in paginas_md]
    if artigos_md:
        llms += ["", "## Blog", ""] + [f"- [{a['titulo']}]({u}/blog/{a['slug']}/index.md): {a['resumo']}" for a, _ in artigos_md]
    llms += ["", "## Contato", "", f"- E-mail: {site['email']}", "- WhatsApp: (11) 5041-2088", "- Telefone: (11) 5548-3977", ""]
    (SAIDA / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    # Redirecionamentos do site antigo (ver docs/URLS-ANTIGAS.md)
    redir = [("/home/negocios/", "/feira/", 301), ("/home/eventos/", "/feira/", 301), ("/home/seja-um-expositor/", "/participar/expositor/", 301),
             ("/home/seja-um-patrocinador/", "/patrocinio/", 301), ("/home/imprensa/", "/contato/", 302), ("/home/fale-conosco/", "/contato/", 301),
             ("/home/depoimentos/", "/reviva-2026/", 302)]
    (SAIDA / "redirects.csv").write_text("origem,destino,codigo\n" + "\n".join(f"{o},{d},{c}" for o, d, c in redir) + "\n", encoding="utf-8")
    (SAIDA / "_redirects").write_text("# Formato Netlify/Cloudflare Pages. Em Apache/Nginx, use redirects.csv.\n"
                                      + "\n".join(f"{o} {d} {c}" for o, d, c in redir) + "\n/* /404.html 404\n", encoding="utf-8")

    print(f"dist/site: {len(ROTAS)} páginas + 404, blog {'com ' + str(len(escolhidos)) + ' artigos' if com_blog else 'fora (sem artigo revisado)'}, revisão {rev}")


def reescrever_um(destino, pasta_atual):
    from rotas import url_de
    return url_de(destino, "blog", pasta_atual + "/")


if __name__ == "__main__":
    main()
