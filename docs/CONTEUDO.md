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

## Blog (próxima etapa)
O blog segue o mesmo modelo, com um arquivo por artigo em `content/blog/`, e exige endereços reais por página. Ver `PUBLICACAO.md` item 3.
