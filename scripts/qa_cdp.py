#!/usr/bin/env python3
"""Verificação automatizada com Chrome headless via DevTools Protocol (somente biblioteca padrão).

Uso: python3 scripts/qa_cdp.py [URL]
Padrão: file:// do HTML independente em dist/. Grava capturas em qa/screenshots/ e
imprime um relatório JSON com os resultados dos cenários.
"""
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333
SHOTS = ROOT / "qa" / "screenshots"


class WS:
    """Cliente WebSocket mínimo (texto, sem extensões)."""

    def __init__(self, url):
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]

    def send(self, text):
        data = text.encode()
        mask = os.urandom(4)
        n = len(data)
        head = bytes([0x81])
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise ConnectionError("socket fechado")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        msg = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            msg += self._read(n)
            if b1 & 0x80:
                return msg.decode()


class CDP:
    def __init__(self, ws):
        self.ws, self.i, self.events = ws, 0, []

    def call(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})
            self.events.append(m)

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=f"(async()=>{{{expr}}})()", awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"])
        return r["result"].get("value")

    def viewport(self, w, h, mobile=False):
        self.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)

    def shot(self, name, full=True):
        if full:  # carrega imagens tardias antes da captura de página inteira
            self.js("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');"
                    "await Promise.all([...document.images].filter(i=>i.getAttribute('src')&&!i.complete).map(i=>new Promise(r=>{i.onload=i.onerror=r})));"
                    "document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in')); document.querySelectorAll('[data-turbina]').forEach(f=>f.classList.add('is-drawn','is-exploded')); await new Promise(r=>setTimeout(r,1000));")
        metrics = self.call("Page.getLayoutMetrics")
        h = int(metrics["cssContentSize"]["height"]) if full else None
        params = {"format": "png", "captureBeyondViewport": full}
        if full:
            w = int(metrics["cssLayoutViewport"]["clientWidth"])
            params["clip"] = {"x": 0, "y": 0, "width": w, "height": min(h, 16000), "scale": 1}
        data = self.call("Page.captureScreenshot", **params)["data"]
        (SHOTS / f"{name}.png").write_bytes(base64.b64decode(data))


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else (ROOT / "dist" / "MRO-Brasil-2027-site.html").as_uri()
    SHOTS.mkdir(parents=True, exist_ok=True)
    prof = tempfile.mkdtemp(prefix="mro-qa-")
    proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                             "--no-first-run", "--hide-scrollbars", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                break
            except OSError:
                time.sleep(0.2)
        page = next(t for t in tabs if t["type"] == "page")
        c = CDP(WS(page["webSocketDebuggerUrl"]))
        for d in ["Page", "Runtime", "Log", "Network"]:
            c.call(f"{d}.enable")
        report = run(c, url)
        errors = [e["params"] for e in c.events if e.get("method") in ("Runtime.exceptionThrown",)
                  or (e.get("method") == "Log.entryAdded" and e["params"]["entry"]["level"] == "error")
                  or (e.get("method") == "Runtime.consoleAPICalled" and e["params"]["type"] == "error")]
        requests = sorted({e["params"]["request"]["url"].split("?")[0][:80] for e in c.events
                           if e.get("method") == "Network.requestWillBeSent"
                           and not e["params"]["request"]["url"].startswith(("data:", "file:"))})
        report["console_errors"] = errors
        report["network_requests_externos"] = requests
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        proc.terminate()


def go(c, url, hash_="#/", w=1440, h=900, mobile=False, popup=False):
    c.viewport(w, h, mobile)
    sep = "" if popup else "?sem-popup"
    c.call("Page.navigate", url=url.split("#")[0].split("?")[0] + sep + hash_)
    time.sleep(1.2)


def run(c, url):
    R = {"url": url}
    wait = "const wait=ms=>new Promise(r=>setTimeout(r,ms));"

    # 1. Pop-up: aparece uma vez por sessão
    go(c, url, popup=True)
    R["popup_antes_de_rolar"] = c.js("return document.getElementById('dialog-perfil').open")
    c.js("window.scrollTo(0, 400); await new Promise(r=>setTimeout(r,600))")
    R["popup_primeira_visita"] = c.js("return document.getElementById('dialog-perfil').open")
    c.shot("01-popup-desktop", full=False)
    R["popup_escape"] = c.js(wait + "document.getElementById('dialog-perfil').dispatchEvent(new Event('cancel',{cancelable:true}));"
                             "document.getElementById('dialog-perfil').close(); await wait(100);"
                             "return {aberto: document.getElementById('dialog-perfil').open, foco: document.activeElement.id}")
    c.call("Page.reload")
    time.sleep(1.5)
    R["popup_apos_recarregar"] = c.js("return document.getElementById('dialog-perfil').open")
    R["popup_escolha_visitante"] = c.js(wait + "const d=document.getElementById('dialog-perfil'); document.querySelector('[data-open-perfil]').click(); await wait(100);"
                                        "d.querySelector('a[href=\"#/participar/visitante\"]').click(); await wait(300);"
                                        "return {aberto:d.open, rota:location.hash, perfil:document.querySelector('input[name=perfil]:checked').value}")

    # 2. Rotas, títulos e histórico
    R["rotas"] = c.js(wait + "const out={}; for (const h of ['#/','#/feira','#/participar','#/participar/visitante','#/participar/expositor','#/patrocinio','#/reviva-2026','#/contato','#/inexistente']) {"
                      "location.hash=h; await wait(120); const p=document.querySelector('[data-page]:not([hidden])');"
                      "out[h]=p.dataset.page+' | '+document.title+' | h1: '+p.querySelector('h1').textContent.trim().slice(0,40);} "
                      "history.back(); await wait(150); out.voltar=location.hash; history.forward(); await wait(150); out.avancar=location.hash; return out")
    R["links_internos_invalidos"] = c.js("const valid=/^#\\/(|feira(\\/(sobre|publico|oportunidades|informacoes))?|participar(\\/(visitante|expositor)(\\/formulario)?)?|patrocinio(\\/formulario)?|reviva-2026(\\/(fotos|videos|depoimentos|feira-virtual))?|contato)$/;"
                                         "return [...document.querySelectorAll('a[href^=\"#\"]')].map(a=>a.getAttribute('href')).filter(h=>!valid.test(h) && h!=='#conteudo' && !h.startsWith('#f-'))")
    R["imagens_quebradas"] = c.js(wait + "for (const p of document.querySelectorAll('[data-page]')) p.hidden=false; document.querySelectorAll('img[loading]').forEach(i=>i.loading='eager'); await wait(800);"
                                  "const bad=[...document.images].filter(i=>i.getAttribute('src') && (!i.complete || i.naturalWidth===0)).map(i=>i.alt); location.hash='#/feira'; await wait(50); location.hash='#/'; await wait(100); return bad")

    # 3. Formulários
    R["formularios"] = c.js(wait + "const R={}; location.hash='#/participar/expositor'; await wait(200); const f=document.querySelector('[data-lead-form]'); const g=n=>f.elements[n];"
                            "g('nome').value='Pessoa Teste'; g('email').value='pessoa@exemplo.com'; f.requestSubmit(); await wait(50);"
                            "R.expositor_sem_empresa=[...document.querySelectorAll('[data-form-errors] li')].map(l=>l.textContent);"
                            "f.querySelector('input[value=visitante]').click(); await wait(50); f.requestSubmit(); f.requestSubmit(); await wait(50);"
                            "R.visitante_sem_empresa_valido=document.querySelector('[data-submit]').disabled; await wait(1000);"
                            "R.confirmacao=document.querySelector('.form-done__msg').textContent; R.storage={local:localStorage.length, session:Object.keys(sessionStorage)}; return R")

    # 4. Carrossel
    R["carrossel"] = c.js(wait + "location.hash='#/'; await wait(200); const act=()=>[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('is-active'));"
                          "const out={}; document.querySelector('[data-carousel-next]').click(); out.proximo=act(); document.querySelector('[data-carousel-prev]').click(); out.anterior=act();"
                          "document.querySelectorAll('.carousel__tab')[2].click(); out.selecao_direta=act(); const t=document.querySelector('[data-carousel-toggle]'); t.click(); out.pausa=t.textContent.trim();"
                          "out.mantaer=document.querySelector('#slide-3 a').href; t.click(); return out")

    # 5. Capturas responsivas e verificação de rolagem horizontal
    R["rolagem_horizontal"] = {}
    pages = [("inicio", "#/"), ("feira", "#/feira"), ("participar", "#/participar"), ("visitante", "#/participar/visitante"),
             ("expositor", "#/participar/expositor"), ("patrocinio", "#/patrocinio"), ("reviva", "#/reviva-2026"), ("contato", "#/contato")]
    for w, h, mobile, tag in [(1440, 900, False, "1440"), (1024, 768, False, "1024"), (768, 1024, True, "768"), (390, 844, True, "390"), (360, 740, True, "360")]:
        for name, hsh in pages:
            go(c, url, hsh, w, h, mobile)
            over = c.js("const cw=document.documentElement.clientWidth; return [...document.querySelectorAll('body *')].filter(el=>{"
                        "if(el.closest('[hidden],dialog,.sprite,.sr-only')) return false; const r=el.getBoundingClientRect();"
                        "if(!(r.width>0 && r.right>cw+1 && getComputedStyle(el).visibility!=='hidden')) return false;for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){const cs=getComputedStyle(p);if(cs.overflowX!=='visible' && p.getBoundingClientRect().right<=cw+1) return false;} return true}).map(el=>el.tagName+'.'+el.className).slice(0,5)")
            R["rolagem_horizontal"][f"{name}@{tag}"] = "ok" if not over else over
            if tag in ("1440", "390") or name in ("inicio", "reviva"):
                c.shot(f"{name}-{tag}")
    c.js("sessionStorage.clear()")
    go(c, url, "#/", 390, 844, True, popup=True)
    c.js("await new Promise(r=>setTimeout(r,5400))")
    c.shot("01-popup-390", full=False)
    go(c, url, "#/reviva-2026/fotos", 390, 844, True)
    c.js("document.querySelector('[data-lightbox]').click(); await new Promise(r=>setTimeout(r,400))")
    c.shot("02-galeria-ampliada-390", full=False)
    go(c, url, "#/participar/visitante/formulario", 390, 844, True)
    c.js("document.querySelector('[data-lead-form]').requestSubmit(); await new Promise(r=>setTimeout(r,200)); document.querySelector('[data-form-errors]').scrollIntoView({behavior:'instant'})")
    c.shot("03-formulario-erros-390", full=False)
    go(c, url, "#/", 390, 844, True)
    c.js("document.querySelector('.nav-toggle').click()")
    c.shot("04-menu-movel-390", full=False)

    # 6. Banner: parallax e captura de cada destaque
    go(c, url, "#/", 1440, 900, False)
    R["banner_parallax"] = c.js("window.scrollTo(0,300); await new Promise(r=>setTimeout(r,300)); const b=document.getElementById('destaques'); const s=b.querySelector('.slide.is-active');"
                                "const out={parallax:b.style.getPropertyValue('--parallax'), foto:getComputedStyle(s.querySelector('.banner__media img')).translate, cartao:getComputedStyle(s.querySelector('.banner__media')).transform}; window.scrollTo(0,0); return out")
    for w, h, mobile in [(1440, 900, False), (390, 844, True)]:
        go(c, url, "#/", w, h, mobile)
        c.js("document.querySelector('[data-carousel-toggle]').click()")
        for n in range(3):
            c.js(f"document.querySelectorAll('.carousel__tab')[{n}].click(); window.scrollTo(0,0); await new Promise(r=>setTimeout(r,1600))")
            r = c.js("const r=document.getElementById('destaques').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]")
            data = c.call("Page.captureScreenshot", format="png", clip={"x": r[0], "y": r[1], "width": r[2], "height": r[3], "scale": 1})["data"]
            (SHOTS / f"banner-{n + 1}-{w}.png").write_bytes(base64.b64decode(data))
    return R


if __name__ == "__main__":
    main()
