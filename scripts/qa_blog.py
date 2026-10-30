#!/usr/bin/env python3
"""Verificação do blog (Chrome headless): erros de console, imagens, rolagem horizontal,
links relativos, rotas do site e JSON-LD de cada página gerada em blog/.

Uso: python3 scripts/qa_blog.py   (abre os arquivos direto do disco)
"""
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_cdp import WS, CDP, CHROME, ROOT  # noqa: E402

PORT = 9337
ROTA = re.compile(r"^#/(|feira(/(sobre|publico|eventos|oportunidades|informacoes))?|participar(/(visitante|expositor)(/formulario)?)?|patrocinio(/formulario)?|reviva-2026(/(fotos|videos|depoimentos|feira-virtual))?|perguntas-frequentes(/(sobre|local|visitar|expor|eventos|virtual|contato))?|contato)$")


def main():
    paginas = sorted((ROOT / "blog").rglob("index.html"))
    prof = tempfile.mkdtemp(prefix="mro-blog-")
    proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}", "--hide-scrollbars", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    problemas, resumo = [], []
    try:
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json")); break
            except OSError:
                time.sleep(0.2)
        c = CDP(WS(next(t for t in tabs if t["type"] == "page")["webSocketDebuggerUrl"]))
        for d in ("Page", "Runtime", "Log"):
            c.call(f"{d}.enable")
        for pg in paginas:
            nome = str(pg.relative_to(ROOT))
            for w, h, m in [(1440, 900, False), (390, 844, True), (360, 740, True)]:
                c.events.clear()
                c.viewport(w, h, m)
                c.call("Page.navigate", url=pg.as_uri()); time.sleep(1.2)
                r = c.js("""document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager'); await new Promise(r=>setTimeout(r,700));
                  const cw=document.documentElement.clientWidth;
                  const wide=[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&b.right>cw+1&&!e.closest('.sprite,.sr-only')}).map(e=>e.tagName+'.'+e.className).slice(0,4);
                  const imgs=[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src.split('/').pop());
                  const links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'));
                  const ld=[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>{try{JSON.parse(s.textContent);return 'ok'}catch(e){return 'ERRO'}});
                  const h1=document.querySelectorAll('h1').length;
                  return {wide, imgs, links, ld, h1, title:document.title, desc:(document.querySelector('meta[name=description]')||{}).content||''}""")
                erros = [e for e in c.events if e.get("method") == "Runtime.exceptionThrown" or (e.get("method") == "Log.entryAdded" and e["params"]["entry"]["level"] == "error")]
                if r["wide"]: problemas.append(f"{nome}@{w}: rolagem horizontal {r['wide']}")
                if r["imgs"]: problemas.append(f"{nome}@{w}: imagens quebradas {r['imgs']}")
                if erros: problemas.append(f"{nome}@{w}: erros de console {len(erros)}")
                if w == 1440:
                    if r["h1"] != 1: problemas.append(f"{nome}: {r['h1']} h1")
                    if "ERRO" in r["ld"]: problemas.append(f"{nome}: JSON-LD inválido")
                    if not (30 <= len(r["title"]) <= 70): problemas.append(f"{nome}: título com {len(r['title'])} caracteres")
                    if not (100 <= len(r["desc"]) <= 170): problemas.append(f"{nome}: descrição com {len(r['desc'])} caracteres")
                    for href in r["links"]:
                        if href.startswith(("http", "mailto:", "tel:", "#conteudo")): continue
                        alvo, _, ancora = href.partition("#")
                        if ancora and not ROTA.match("#" + ancora): problemas.append(f"{nome}: rota inválida {href}")
                        if alvo and not (pg.parent / alvo).resolve().exists(): problemas.append(f"{nome}: arquivo inexistente {href}")
                    resumo.append(f"{nome}: {len(r['links'])} links, JSON-LD {r['ld']}")
    finally:
        proc.terminate()
    print("\n".join(resumo))
    print("PROBLEMAS:" if problemas else "Sem problemas em", *(problemas or [f"{len(paginas)} páginas x 3 larguras"]), sep="\n")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
