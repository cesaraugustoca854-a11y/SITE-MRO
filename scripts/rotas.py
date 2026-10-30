"""Tabela de rotas do site (espelha ROUTES em src/app.js) e conversão de #/rota em endereço real."""
import re

# caminho -> (página, seções com âncora, filtros do acervo)
ROTAS = [
    ("", "inicio", {}, []),
    ("feira", "feira", {"sobre": "feira-sobre", "publico": "feira-publico", "eventos": "feira-eventos", "oportunidades": "feira-oportunidades", "informacoes": "feira-informacoes"}, []),
    ("participar", "participar", {}, []),
    ("participar/visitante", "visitante", {"formulario": "visitante-formulario"}, []),
    ("participar/expositor", "expositor", {"formulario": "expositor-formulario"}, []),
    ("patrocinio", "patrocinio", {"formulario": "patrocinio-formulario"}, []),
    ("reviva-2026", "reviva", {"feira-virtual": "reviva-virtual"}, ["fotos", "videos", "depoimentos"]),
    ("perguntas-frequentes", "faq", {"sobre": "faq-sobre", "local": "faq-local", "visitar": "faq-visitar", "expor": "faq-expor", "eventos": "faq-eventos", "virtual": "faq-virtual", "contato": "faq-contato"}, []),
    ("contato", "contato", {}, []),
]
POR_PAGINA = {r[1]: r for r in ROTAS}


def profundidade(caminho):
    return len([p for p in caminho.split("/") if p])


def prefixo(caminho):
    """Caminho relativo de volta à raiz a partir da pasta da página."""
    return "../" * profundidade(caminho)


def url_de(destino, pagina_atual, caminho_atual):
    """Converte '#/feira/eventos' em endereço relativo. Mesma página vira só a âncora."""
    resto = destino[2:].strip("/").lower()
    for caminho, pagina, secoes, filtros in sorted(ROTAS, key=lambda r: -len(r[0])):
        if resto == caminho or (caminho and resto.startswith(caminho + "/")) or (not caminho and resto == ""):
            extra = resto[len(caminho):].strip("/")
            ancora = secoes.get(extra) or (extra if extra in filtros else "")
            if pagina == pagina_atual and ancora:
                return f"#{ancora}"
            base = prefixo(caminho_atual) + (caminho + "/" if caminho else "")
            return (base or "./") + (f"#{ancora}" if ancora else "")
    return destino


def reescrever_links(trecho, pagina_atual, caminho_atual):
    """Reescreve href="#/rota", e arquivos relativos (assets/, src/, blog/) conforme a profundidade."""
    raiz = prefixo(caminho_atual)
    trecho = re.sub(r'href="(#/[^"]*)"', lambda m: f'href="{url_de(m.group(1), pagina_atual, caminho_atual)}"', trecho)
    trecho = re.sub(r'(src|href)="(?!#|https?:|mailto:|tel:|data:|\.\./)(?!\./)([^"]+)"',
                    lambda m: f'{m.group(1)}="{raiz}{m.group(2)}"', trecho)
    # listas de imagens e ampliações: srcset="a.jpg 800w, b.jpg 1600w", imagesrcset e data-full
    trecho = re.sub(r'(srcset|imagesrcset)="([^"]+)"', lambda m: f'{m.group(1)}="' + ", ".join(
        (raiz + x.strip() if x.strip().startswith("assets/") else x.strip()) for x in m.group(2).split(",")) + '"', trecho)
    return re.sub(r'data-full="(assets/[^"]+)"', lambda m: f'data-full="{raiz}{m.group(1)}"', trecho)
