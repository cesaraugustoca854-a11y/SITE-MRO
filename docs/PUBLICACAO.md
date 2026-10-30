# Publicação com páginas reais (SEO, GEO e IA)

A prévia por `#` continua para aprovação. Para publicar, gere o site com endereços reais:

```bash
python3 scripts/gerar_site.py                      # só artigos com revisado: sim
python3 scripts/gerar_site.py --incluir-rascunhos  # conferência: rascunhos com noindex, fora do sitemap
python3 scripts/qa_site.py                         # 14 páginas, dados estruturados, links, interações
```

Sai em `dist/site/` (não vai para o GitHub; é gerado). Suba o **conteúdo dessa pasta** na raiz do domínio.

## O que sai
- Uma página por rota (`/`, `/feira/`, `/participar/`, `/participar/visitante/`, `/participar/expositor/`, `/patrocinio/`, `/reviva-2026/`, `/perguntas-frequentes/`, `/contato/`), cada uma com título, descrição, `canonical`, Open Graph, Twitter Card e `robots: index, follow`.
- Dados estruturados por página: `Organization`, `WebSite`, `WebPage` (ou `FAQPage`), `BreadcrumbList`; `Event` na home e na Feira; `VideoObject` no Reviva quando houver vídeo com data.
- Versão em Markdown de cada página (`index.md` ao lado do `index.html`), `sitemap.md` (mapa por tema) e `llms.txt`, com data, fonte, revisão e responsável.
- `sitemap.xml` (com comentário apontando o `sitemap.md`), `robots.txt` liberado com a linha `Sitemap:`, `404.html` com `noindex`.
- `redirects.csv` e `_redirects` com os redirecionamentos do site antigo (ver `URLS-ANTIGAS.md`). Em Apache/Nginx, converta o CSV.
- Blog: só artigos `revisado: sim` no sitemap e no feed. Sem nenhum revisado, o blog (e o link no menu) fica de fora.

## Antes de colocar no ar
1. Confirmar o endereço final em `content/site.json` (`url_base`; hoje `https://www.mrobrasil.com.br`) e rodar de novo `gerar_site.py`.
2. Servidor: responder `404.html` com **status 404** para endereços inexistentes, servir `index.html` nas pastas, e aplicar os redirecionamentos 301/302.
3. Servir `.md` e `.txt` como `text/markdown; charset=utf-8` e `text/plain; charset=utf-8`.
4. No Google Search Console e no Bing Webmaster: verificar a propriedade e enviar `sitemap.xml` (só depois de publicado; a organização decide).
5. Conferir no ar: `robots.txt`, `sitemap.xml`, `llms.txt`, uma página `.md` e o Teste de Resultados Rich do Google na home, na Feira e no FAQ.
6. Remover o `noindex` não é mais necessário no site de publicação: ele só existe na prévia (`index.html`, `blog/`).

---

# Configuração para a futura publicação

Nada foi publicado. Ao receber aprovação específica:

1. **Indexação**: em `index.html`, trocar `<meta name="robots" content="noindex, nofollow">` por `index, follow`; substituir `robots.txt` por regras definitivas com `Sitemap:`.
2. **Domínio definitivo** (a confirmar; não foi presumido):
   - `<link rel="canonical" href="https://DOMINIO/">` e canônicos por página;
   - `og:url` e `og:image` absolutos (`assets/img/og-mro2027.jpg`, 1200×630, hoje recorte da imagem ilustrativa — trocar pela arte oficial);
   - `url` e `image` no JSON-LD de evento, se desejado.
3. **Rotas reais**: migrar de `#/feira` para `/feira` (History API + reescrita no servidor para `index.html`), ou gerar páginas estáticas por rota. Aplicar os redirecionamentos de `URLS-ANTIGAS.md`.
4. **Sitemap** com as 8 páginas.
5. **Dados estruturados**: o JSON-LD contém só fatos confirmados (nome, datas, local, endereço). Não acrescentar horários, ofertas, preços ou disponibilidade antes da definição.
6. **Desempenho**: servir `assets/` com cache longo; versões WebP/AVIF das fotos podem reduzir ~30–50%. O HTML único (3 MB) é para aprovação, não para produção — publicar a versão com arquivos separados.
7. **Privacidade**: publicar política aprovada e link junto aos formulários; nenhum analytics ou pixel foi incluído — adicionar somente com base legal e banner de consentimento definido.
8. **Formulários**: só ativar após a integração descrita em `INTEGRACAO-CRM.md`; remover os rótulos de demonstração apenas nessa etapa.
