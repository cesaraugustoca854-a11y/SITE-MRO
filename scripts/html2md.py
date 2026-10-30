"""Converte o HTML de uma página em Markdown (só biblioteca padrão), sem a estrutura do site."""
import html
import re
from html.parser import HTMLParser

CLASSES_PULAR = ("eyebrow", "kicker", "crumbs", "media-tag", "subnav", "gauge__ring", "g-photo__zoom", "skip-link")
PULAR = {"script", "style", "svg", "button", "form", "dialog", "template", "nav", "noscript", "iframe", "picture", "source"}


class Conversor(HTMLParser):
    def __init__(self, base_url=""):
        super().__init__(convert_charrefs=True)
        self.saida, self.pilha, self.listas, self.base = [], [], [], base_url
        self.link, self.pular = None, 0
        self.em_summary = False

    def _txt(self, t):
        self.saida.append(t)

    def _quebra(self, n=2):
        atual = "".join(self.saida)
        faltam = n - (len(atual) - len(atual.rstrip("\n")))
        if atual and faltam > 0:
            self.saida.append("\n" * faltam)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if tag in PULAR or any(c in cls for c in CLASSES_PULAR) or "sr-only" in cls and tag != "span" or a.get("aria-hidden") == "true" and tag not in ("a",):
            self.pular += 1; self.pilha.append((tag, True)); return
        if tag in ("br", "img", "hr", "link", "meta", "input"):
            if tag == "br":
                self._txt(", ")
            if tag == "img" and a.get("alt"):
                self._txt(f"*Imagem: {a['alt']}*")
            return
        self.pilha.append((tag, False))
        if self.pular:
            return
        if "sr-only" in cls:
            self.pular += 1; self.pilha[-1] = (tag, True); return
        if tag in ("h1", "h2", "h3", "h4"):
            self._quebra(); self._txt("#" * int(tag[1]) + " ")
        elif tag == "summary":
            self._quebra(); self._txt("### "); self.em_summary = True
        elif tag in ("p", "figure", "section", "article", "details", "dl", "blockquote", "figcaption"):
            self._quebra()
            if tag == "blockquote": self._txt("> ")
        elif tag in ("ul", "ol"):
            self._quebra(1); self.listas.append([tag, 0])
        elif tag == "li":
            self._quebra(1)
            if self.listas:
                self.listas[-1][1] += 1
                self._txt("  " * (len(self.listas) - 1) + ("- " if self.listas[-1][0] == "ul" else f"{self.listas[-1][1]}. "))
        elif tag == "dt":
            self._quebra(1); self._txt("- **")
        elif tag == "dd":
            self._txt(": ")
        elif tag in ("strong", "b"):
            self._txt("**")
        elif tag == "a" and a.get("href") and not a["href"].startswith("#"):
            self.link = a["href"]; self._txt("[")

    def handle_endtag(self, tag):
        if not self.pilha:
            return
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                _, pulou = self.pilha.pop(i)
                break
        else:
            return
        if pulou:
            self.pular -= 1; return
        if self.pular:
            return
        if tag in ("h1", "h2", "h3", "h4", "summary", "p", "li", "dd", "dt", "figcaption", "blockquote"):
            if tag == "dt":
                self._txt("**"); return
            self._quebra(1 if tag in ("li", "dd") else 2)
            if tag == "summary": self.em_summary = False
        elif tag in ("ul", "ol"):
            if self.listas: self.listas.pop()
            self._quebra(2)
        elif tag in ("strong", "b"):
            self._txt("**")
        elif tag == "span":
            self._txt(" ")
        elif tag == "a" and self.link:
            href = self.link
            if href.startswith("tel:") or href.startswith("mailto:"):
                self.saida.append("]"); self.saida[-1] = "]"
                self._txt(f"({href})")
            else:
                self._txt(f"]({href})")
            self.link = None

    def handle_data(self, data):
        if self.pular:
            return
        t = re.sub(r"\s+", " ", data)
        if t.strip() or (t and self.saida and not "".join(self.saida).endswith(("\n", " "))):
            self._txt(t)

    def markdown(self):
        txt = "".join(self.saida)
        txt = re.sub(r"[ \t]+\n", "\n", txt)
        txt = re.sub(r"\n +(?=\S)", "\n", txt)
        txt = re.sub(r"\n{3,}", "\n\n", txt)
        txt = re.sub(r"\*\*\s*\*\*", "", txt)
        txt = re.sub(r"(\*\*[^*\n]+\*\*)(?=[A-Za-zÀ-ÿ0-9])", r"\1 ", txt)
        txt = re.sub(r"[ ]{2,}", " ", txt)
        txt = re.sub(r"\[ +", "[", txt)
        txt = re.sub(r" +\]\(", "](", txt)
        return txt.strip() + "\n"


def converter(trecho_html):
    c = Conversor()
    c.feed(trecho_html)
    return c.markdown()
