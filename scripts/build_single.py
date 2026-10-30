#!/usr/bin/env python3
"""Gera o HTML independente (CSS, JS, fontes e imagens incorporados) e o ZIP de entrega.

Uso:  python3 scripts/build_single.py
Saída: dist/MRO-Brasil-2027-site.html e dist/MRO-Brasil-2027-site-remodelado.zip
"""
import base64
import mimetypes
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT_HTML = DIST / "MRO-Brasil-2027-site.html"
OUT_ZIP = DIST / "MRO-Brasil-2027-site-remodelado.zip"

MIME = {".woff2": "font/woff2", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml"}
_cache = {}


def data_uri(rel_path: str) -> str:
    path = (ROOT / rel_path).resolve()
    if path not in _cache:
        mime = MIME.get(path.suffix) or mimetypes.guess_type(path.name)[0]
        _cache[path] = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
    return _cache[path]


def inline_css() -> str:
    css = (ROOT / "src/styles.css").read_text(encoding="utf-8")
    return re.sub(r'url\("\.\./(assets/[^"]+)"\)', lambda m: f'url("{data_uri(m.group(1))}")', css)


def build_html() -> str:
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    # Pré-carregamentos apontam para arquivos externos; no arquivo único não se aplicam.
    html = re.sub(r'<link rel="preload"[^>]*>\n?', "", html)
    html = html.replace('<link rel="stylesheet" href="src/styles.css">', f"<style>\n{inline_css()}\n</style>")

    def inline_script(m):
        js = (ROOT / m.group(1)).read_text(encoding="utf-8")
        assert "</script" not in js
        return f"<script>\n{js}\n</script>"

    html = re.sub(r'<script src="(src/[^"]+)"></script>', inline_script, html)

    # Uma única resolução por imagem: remove srcset/sizes e incorpora o src.
    html = re.sub(r'<source type="image/avif"[^>]*>', "", html)  # AVIF fica só na versão com arquivos separados
    html = re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", html)
    html = re.sub(r'"(assets/img/[^"]+)"', lambda m: f'"{data_uri(m.group(1))}"', html)

    html = html.replace("<head>", "<head>\n<!-- Arquivo gerado por scripts/build_single.py a partir de index.html. Não editar diretamente. -->", 1)
    leftovers = re.findall(r'(?:src|href)="(?:assets|src)/[^"]*"', html)
    assert not leftovers, leftovers
    return html


def build_zip():
    files = [(OUT_HTML, OUT_HTML.name), (ROOT / "README.md", "README.md")]
    files += [(p, f"docs/{p.name}") for p in sorted((ROOT / "docs").glob("*.md"))]
    files += [(p, f"qa/capturas/{p.name}") for p in sorted((ROOT / "qa/screenshots").glob("*.jpg"))]
    files += [(p, f"qa/{p.name}") for p in sorted((ROOT / "qa").glob("*.json"))]
    for rel in ["index.html", "robots.txt", "llms.txt"]:
        files.append((ROOT / rel, f"codigo-fonte/{rel}"))
    for folder in ["src", "assets", "scripts", "content", "blog"]:
        for p in sorted((ROOT / folder).rglob("*")):
            if p.is_file() and p.name != ".DS_Store":
                files.append((p, f"codigo-fonte/{p.relative_to(ROOT)}"))
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            z.write(src, f"MRO-Brasil-2027-site-remodelado/{arc}")


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    OUT_HTML.write_text(build_html(), encoding="utf-8")
    build_zip()
    print(f"{OUT_HTML.relative_to(ROOT)}  {OUT_HTML.stat().st_size / 1e6:.2f} MB")
    print(f"{OUT_ZIP.relative_to(ROOT)}  {OUT_ZIP.stat().st_size / 1e6:.2f} MB")
