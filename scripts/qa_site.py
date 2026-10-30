#!/usr/bin/env python3
"""Verificação do site de publicação (dist/site) em Chrome headless, servido por HTTP local.

Confere em cada página: erros de console, imagens, rolagem horizontal (1440/390), robots, canonical,
título e descrição, JSON-LD válido, 1 h1, links internos, versão .md e presença no sitemap.xml;
e os arquivos de descoberta (robots.txt, sitemap.xml, sitemap.md, llms.txt, 404.html).

Uso: python3 scripts/qa_site.py   (sobe um servidor temporário na porta 5209)
"""
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from xml.dom import minidom

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_cdp import WS, CDP, CHROME, ROOT  # noqa: E402

SITE = ROOT / "dist" / "site"
PORTA, PORTA_CDP = 5209, 9338


def arquivo_de(caminho_url):
    p = SITE / caminho_url.lstrip("/")
    return p / "index.html" if p.is_dir() or caminho_url.endswith("/") or caminho_url == "" else p


def main():
    problemas = []
    cfg = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
    base = cfg["url_base"]
    paginas = sorted(SITE.rglob("index.html")) + [SITE / "404.html"]

    # arquivos de descoberta
    for nome in ("robots.txt", "sitemap.xml", "sitemap.md", "llms.txt", "404.html"):
        if not (SITE / nome).exists():
            problemas.append(f"falta {nome}")
    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    if re.search(r"^Disallow:\s*/\s*$", robots, re.M):
        problemas.append("robots.txt bloqueia o site inteiro")
    if f"Sitemap: {base}/sitemap.xml" not in robots:
        problemas.append("robots.txt sem a linha Sitemap")
    dom = minidom.parse(str(SITE / "sitemap.xml"))
    locs = [n.firstChild.data for n in dom.getElementsByTagName("loc")]
    for loc in locs:
        alvo = loc.replace(base, "")
        if not arquivo_de(alvo).exists():
            problemas.append(f"sitemap.xml aponta para {loc}, que não existe")
    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    smd = (SITE / "sitemap.md").read_text(encoding="utf-8")
    for texto, nome in ((llms, "llms.txt"), (smd, "sitemap.md")):
        for alvo in re.findall(r"\]\(([^)]+\.md)\)", texto):
            destino = alvo.replace(base + "/", "") if alvo.startswith(base) else alvo
            if not (SITE / destino).exists():
                problemas.append(f"{nome} aponta para {alvo}, que não existe")

    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORTA), "--bind", "127.0.0.1", "--directory", str(SITE)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORTA_CDP}", f"--user-data-dir={tempfile.mkdtemp()}", "--hide-scrollbars", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    resumo = []
    try:
        time.sleep(1)
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA_CDP}/json")); break
            except OSError:
                time.sleep(0.2)
        c = CDP(WS(next(t for t in tabs if t["type"] == "page")["webSocketDebuggerUrl"]))
        for d in ("Page", "Runtime", "Log", "Network"):
            c.call(f"{d}.enable")
        for pg in paginas:
            rel = pg.relative_to(SITE).as_posix()
            url_path = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            for w, h, m in [(1440, 900, False), (390, 844, True)]:
                c.events.clear()
                c.viewport(w, h, m)
                c.call("Page.navigate", url=f"http://127.0.0.1:{PORTA}{url_path}?sem-popup"); time.sleep(1.3)
                r = c.js("""document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager'); await new Promise(r=>setTimeout(r,800));
                  const cw=document.documentElement.clientWidth;
                  const wide=[...document.querySelectorAll('body *')].filter(e=>{if(e.closest('dialog,.sprite,.sr-only,[hidden]'))return false;const b=e.getBoundingClientRect();if(!(b.width>0&&b.right>cw+1))return false;for(let p=e.parentElement;p&&p!==document.body;p=p.parentElement){const s=getComputedStyle(p);if(s.overflowX!=='visible'&&p.getBoundingClientRect().right<=cw+1)return false}return true}).map(e=>e.tagName+'.'+e.className).slice(0,4);
                  const imgs=[...document.images].filter(i=>i.getAttribute('src')&&(!i.complete||i.naturalWidth===0)).map(i=>i.src.split('/').pop());
                  const links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'));
                  const ld=[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>{try{const j=JSON.parse(s.textContent);return (j['@graph']||[j]).map(x=>x['@type']).join('+')}catch(e){return 'ERRO'}});
                  const meta=n=>(document.querySelector(n)||{}).content||'';
                  return {wide,imgs,links,ld,h1:document.querySelectorAll('h1').length,title:document.title,desc:meta('meta[name=description]'),robots:meta('meta[name=robots]'),
                    canonical:(document.querySelector('link[rel=canonical]')||{}).href||'',md:(document.querySelector('link[rel=alternate][type="text/markdown"]')||{}).href||'',
                    ogimg:meta('meta[property="og:image"]'),twimg:meta('meta[name="twitter:image"]'),ident:window.MRO_MPA&&window.MRO_MPA.page}""")
                erros = [e for e in c.events if e.get("method") == "Runtime.exceptionThrown" or (e.get("method") == "Log.entryAdded" and e["params"]["entry"]["level"] == "error")]
                externos = sorted({e["params"]["request"]["url"].split("?")[0][:60] for e in c.events if e.get("method") == "Network.requestWillBeSent"
                                   and not e["params"]["request"]["url"].startswith(("data:", f"http://127.0.0.1:{PORTA}"))})
                if erros: problemas.append(f"{rel}@{w}: {len(erros)} erro(s) de console: {[(e['params'].get('exceptionDetails') or e['params'].get('entry'))['text'][:80] for e in erros][:2]}")
                if externos: problemas.append(f"{rel}@{w}: requisições externas {externos}")
                if r["wide"]: problemas.append(f"{rel}@{w}: rolagem horizontal {r['wide']}")
                if r["imgs"]: problemas.append(f"{rel}@{w}: imagens quebradas {r['imgs']}")
                if w != 1440:
                    continue
                if r["h1"] != 1: problemas.append(f"{rel}: {r['h1']} h1")
                if "ERRO" in r["ld"]: problemas.append(f"{rel}: JSON-LD inválido")
                if not (25 <= len(r["title"]) <= 70): problemas.append(f"{rel}: título com {len(r['title'])} caracteres")
                if rel != "404.html" and not (100 <= len(r["desc"]) <= 170): problemas.append(f"{rel}: descrição com {len(r['desc'])} caracteres")
                rascunho = "Rascunho em revisão" in pg.read_text(encoding="utf-8")
                if rel == "404.html" or rascunho:
                    if "noindex" not in r["robots"]: problemas.append(f"{rel}: deveria ter noindex")
                else:
                    if "noindex" in r["robots"] or "index" not in r["robots"]: problemas.append(f"{rel}: robots = {r['robots']!r}")
                    esperado = base + url_path
                    if r["canonical"] != esperado: problemas.append(f"{rel}: canonical {r['canonical']} (esperado {esperado})")
                    if not r["ogimg"].startswith(base) or not r["twimg"].startswith(base): problemas.append(f"{rel}: faltam og:image/twitter:image")
                    if esperado not in locs and not rel.startswith("blog/") and rel != "404.html": problemas.append(f"{rel}: ausente do sitemap.xml")
                    if not r["md"] or not (pg.parent / "index.md").exists(): problemas.append(f"{rel}: sem versão .md")
                if rel != "404.html":
                    for href in r["links"]:
                        if href.startswith(("http", "mailto:", "tel:", "#")): continue
                        alvo, _, ancora = href.partition("#")
                        destino = (pg.parent / alvo).resolve() if alvo else pg
                        if destino.is_dir(): destino = destino / "index.html"
                        if not destino.exists(): problemas.append(f"{rel}: link quebrado {href}")
                        elif ancora and ancora not in destino.read_text(encoding="utf-8"):
                            if not re.search(rf'id="{re.escape(ancora)}"', destino.read_text(encoding="utf-8")) and ancora not in ("fotos", "videos", "depoimentos"):
                                problemas.append(f"{rel}: âncora inexistente {href}")
                    if "#/" in " ".join(r["links"]): problemas.append(f"{rel}: restou link com #/")
                resumo.append(f"{rel}: {r['ld']}, {len(r['links'])} links")
        # comportamento interativo no modo de páginas reais
        def abre(caminho, w=1440, h=900, mobile=False, popup=False):
            c.viewport(w, h, mobile)
            c.call("Page.navigate", url=f"http://127.0.0.1:{PORTA}{caminho}" if popup else f"http://127.0.0.1:{PORTA}{caminho}".replace("#", "?sem-popup#", 1) if "#" in caminho else f"http://127.0.0.1:{PORTA}{caminho}?sem-popup")
            time.sleep(1.3)
        W = "const wait=ms=>new Promise(r=>setTimeout(r,ms));"
        abre("/feira/")
        if c.js("return document.querySelector('.site-nav [data-nav=feira]').getAttribute('aria-current')") != "page":
            problemas.append("/feira/: item do menu sem aria-current")
        abre("/participar/visitante/")
        f = c.js(W + "const f=document.querySelector('[data-lead-form]'); if(!f) return 'sem formulário'; f.requestSubmit(); await wait(100); const erros=document.querySelectorAll('[data-form-errors] li').length;"
                 "f.elements.nome.value='Pessoa Teste'; f.elements.email.value='pessoa@exemplo.com'; f.requestSubmit(); await wait(1200);"
                 "return {erros, perfil:(f.querySelector('input[name=perfil]:checked')||{}).value, msg:(document.querySelector('.form-done__msg')||{}).textContent}")
        if f == "sem formulário" or not f.get("erros") or f.get("perfil") != "visitante" or "Nenhuma solicitação foi enviada" not in (f.get("msg") or ""):
            problemas.append(f"/participar/visitante/: formulário em modo demonstração falhou {f}")
        abre("/reviva-2026/#fotos")
        g = c.js(W + "await wait(400); return [...document.querySelectorAll('.g-item')].filter(i=>!i.hidden).map(i=>i.dataset.type)")
        if not g or set(g) != {"fotos"}:
            problemas.append(f"/reviva-2026/#fotos: filtro do acervo {g}")
        l = c.js(W + "document.querySelector('[data-lightbox]').click(); await wait(300); return document.getElementById('dialog-lightbox').open")
        if l is not True:
            problemas.append("/reviva-2026/: ampliação de foto não abriu")
        abre("/perguntas-frequentes/#q-quando-acontece-a-mro-brasil-2027")
        q = c.js(W + "await wait(400); const d=document.getElementById('q-quando-acontece-a-mro-brasil-2027'); return {open:d.open, foco:document.activeElement.tagName}")
        if not q["open"] or q["foco"] != "SUMMARY":
            problemas.append(f"FAQ com âncora não abriu a pergunta {q}")
        abre("/")
        car = c.js(W + "document.querySelector('[data-carousel-next]').click(); await wait(200); return [...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('is-active'))")
        if car != 1:
            problemas.append(f"/: carrossel não avançou ({car})")
        abre("/", popup=True)
        pop = c.js(W + "window.scrollTo(0,400); await wait(700); const d=document.getElementById('dialog-perfil'); return {aberto:d.open, links:[...d.querySelectorAll('a[data-dialog-choice]')].map(a=>a.getAttribute('href'))}")
        if not pop["aberto"] or pop["links"] != ["participar/visitante/", "participar/expositor/", "patrocinio/"]:
            problemas.append(f"/: pop-up de perfil {pop}")
        abre("/feira/", 390, 844, True)
        m = c.js(W + "document.querySelector('.nav-toggle').click(); await wait(200); return document.querySelector('.nav-toggle').getAttribute('aria-expanded')")
        if m != "true":
            problemas.append("/feira/@390: menu móvel não abriu")
    finally:
        proc.terminate(); srv.terminate()
    print("\n".join(resumo))
    print("PROBLEMAS:" if problemas else f"Sem problemas em {len(paginas)} páginas", *problemas, sep="\n")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
