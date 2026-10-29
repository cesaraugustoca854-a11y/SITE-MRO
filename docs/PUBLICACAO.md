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
