# Como publicar fotos, vídeos, depoimentos e artigos

Tudo é publicado por arquivos neste repositório. Nada vai ao ar sem a marca de autorização.

## Fotos do Reviva 2026
1. Coloque os originais (JPG/PNG, o maior tamanho possível) em `content/originais/reviva/`. Essa pasta não vai para o GitHub.
2. Rode `python3 scripts/preparar_fotos.py`. Ele cria em `assets/img/reviva/` as versões de 480, 960 e 1600 px (AVIF também, se `avifenc` estiver instalado: `brew install libavif`).
3. Em `content/reviva.json`, na lista `fotos`, acrescente:
   ```json
   { "arquivo": "abertura-01", "legenda": "Abertura da feira em 2026", "alt": "Visitantes entrando no pavilhão", "credito": "Nome do fotógrafo", "destaque": false, "autorizado": true }
   ```
   `arquivo` é o nome do original sem a extensão. `alt` descreve a imagem para quem não a vê. `destaque: true` ocupa duas colunas. Sem `"autorizado": true` a foto é ignorada.
4. Rode `python3 scripts/gerar_reviva.py`. Quando houver ao menos uma foto autorizada, as imagens de demonstração saem sozinhas.

## Vídeos
1. Suba o vídeo no YouTube ou no Vimeo (não hospede o arquivo no site).
2. Em `videos`, acrescente:
   ```json
   { "titulo": "Melhores momentos 2026", "plataforma": "youtube", "id": "dQw4w9WgXcQ", "descricao": "Resumo da edição 2026.", "duracao": "2 min", "data": "2026-10-30", "transcricao": "Texto falado no vídeo.", "miniatura": "abertura-01", "autorizado": true }
   ```
   `id` é só o código do vídeo (no YouTube, o que vem depois de `v=`). `data` (AAAA-MM-DD) habilita o schema VideoObject. `miniatura` é o `arquivo` de uma foto já preparada. `transcricao` é recomendada para acessibilidade.
3. O player só carrega depois do clique (YouTube sem cookies, Vimeo com `dnt`). Nenhum rastreador entra na página ao abrir.

## Depoimentos
Em `depoimentos`:
```json
{ "nome": "Nome Sobrenome", "cargo": "Diretora", "empresa": "Empresa", "texto": "Fala autorizada.", "autorizado": true }
```
Marque `autorizado` só com autorização de uso de nome, cargo e fala (idealmente por escrito).

## Publicar
```bash
python3 scripts/gerar_reviva.py
python3 scripts/build_single.py
python3 scripts/qa_cdp.py
git add -A && git commit -m "Acervo Reviva" && git push
```
O script para com mensagem de erro se faltar legenda, texto alternativo, arquivo ou id.

## Blog
Cada artigo é um arquivo em `content/blog/` e vira uma **página HTML real** (`blog/nome-do-artigo/index.html`), com endereço próprio, que os buscadores indexam.

1. Crie `content/blog/nome-do-artigo.md` (o nome do arquivo vira o endereço):
   ```
   ---
   titulo: Título completo do artigo
   titulo_seo: Título curto para o Google (até 60 caracteres)
   resumo: Resumo de 120 a 160 caracteres, com a resposta principal.
   data: 2026-11-05
   categoria: Mercado
   imagem: folder-globo
   imagem_alt: Descrição da imagem para quem não a vê.
   revisado: nao
   ---
   Parágrafo de abertura que já responde a pergunta do título.

   ## Subtítulo
   Texto, listas com "-", **negrito** e [links](#/feira/informacoes).

   ## Perguntas frequentes

   ### Pergunta que alguém digitaria no Google?
   Resposta direta, de uma a três frases.
   ```
   `imagem` é o nome (sem `.jpg`) de um arquivo em `assets/img/`. Links do site usam `#/rota`; links externos usam `https://`.
2. Rode `python3 scripts/gerar_blog.py` (cria artigos, listagem e, quando houver endereço do site, `feed.xml` e `sitemap.xml`).
3. Confira: `python3 scripts/qa_blog.py`.
4. Com `revisado: nao` o artigo mostra o aviso "Rascunho em revisão pela organização". Depois da aprovação, troque para `revisado: sim`: o aviso some e o artigo entra no feed e no sitemap.
5. Antes de publicar de verdade, preencha `url_base` em `content/blog/config.json` (por exemplo `https://www.mrobrasil.com.br`). Isso liga o canonical, o schema completo, o feed e o sitemap.

Cada artigo termina com perguntas frequentes (o mesmo formato do FAQ do site). Elas viram o bloco visível e o schema FAQPage, que é o que mais ajuda o SEO e a visibilidade em respostas de IA. Escreva a resposta direta primeiro e cite só dados confirmados.
