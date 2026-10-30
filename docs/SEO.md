# SEO — auditoria e correções (28/10/2026)

Auditoria do código da versão 2. Nota inicial para publicação: **66/100**. O bloqueio de indexação da prévia (`noindex` e `robots.txt`) é intencional e não entrou na nota.

## Corrigido nesta rodada
- **Títulos** padronizados com o termo do setor, entre 49 e 53 caracteres (`Página | MRO Brasil 2027 · Manutenção Aeronáutica`). A home mantém o nome oficial completo (63 caracteres).
- **Descrições** entre 136 e 159 caracteres em todas as páginas; Participar, Reviva e Contato foram ampliadas.
- **Open Graph / Twitter**: descrição alinhada à da home; `twitter:title` e `twitter:description` incluídos.
- **Dados estruturados (Event)**: incluídos `description` e `inLanguage`, só com fatos confirmados.
- **Imagens**: versões AVIF das 8 fotos (20 a 60% menores) via `<picture>`, com JPEG como alternativa; a imagem principal é pré-carregada em AVIF. O HTML único continua só com JPEG, para não dobrar o tamanho.
- **Logotipo**: PNG reduzido de 600 para 420 px (104 → 64 KB), o dobro do tamanho exibido.

## Pendente para a publicação
| Item | Por que ainda não | Onde |
|---|---|---|
| Endereços reais por página (`/feira`, `/participar/visitante`…) com HTML próprio por rota | O HTML de aprovação precisa da navegação por `#` para abrir direto do disco | `PUBLICACAO.md`, item 3 |
| `canonical`, `og:url`, `og:image` absolutos e `sitemap.xml` | Dependem do domínio definitivo | `PUBLICACAO.md`, itens 2 e 4 |
| Trocar `noindex` e `robots.txt` | Só com aprovação de publicação | `PUBLICACAO.md`, item 1 |
| Redirecionamentos 301 das 13 URLs antigas | Dependem do servidor de publicação | `URLS-ANTIGAS.md` |
| HTTP 404 real para endereços inexistentes | Depende do servidor | — |
| `image` e `url` no JSON-LD | Dependem do domínio definitivo | `PUBLICACAO.md` |
| `BreadcrumbList` e `Organization` | Precisam de URLs reais e créditos institucionais confirmados | — |
| Logotipo em SVG | Falta o arquivo vetorial oficial | `PENDENCIAS.md` |
| `hreflang`, se houver versão em inglês | Decisão editorial | — |

## SEO e GEO por perguntas frequentes (30/10/2026)
A estratégia principal de SEO e de GEO (visibilidade em respostas de IA como ChatGPT, Gemini e Perplexity) é o FAQ.

- **Fonte única:** `content/faq.json` (19 perguntas em 7 grupos). `python3 scripts/gerar_faq.py` gera a página `#/perguntas-frequentes`, o bloco de destaques da home, o schema `FAQPage` no `<head>` e o `llms.txt`. Texto visível e schema nunca divergem.
- **Redação para respostas de IA:** cada resposta começa pela resposta direta, repete o nome da feira (sem depender do contexto da pergunta) e traz números e nomes próprios do folder oficial. Onde não há dado confirmado, a resposta diz isso e indica o canal, em vez de inventar.
- **Perguntas escolhidas pela intenção de busca:** quando é, onde é, tema, o que é MRO, tamanho do mercado, como chegar, estacionamento, quem visita, como visitar, como expor, como patrocinar, eventos, programação, feira virtual, contato.
- **Event** ganhou `organizer` e `subEvent` (os 5 eventos do folder) e o tema da edição na descrição.
- **`llms.txt`** na raiz resume a feira e todas as respostas em texto simples, para rastreadores de IA.
- **Na publicação com rotas reais:** a página `/perguntas-frequentes` deve ter HTML próprio com o `FAQPage`; os demais grupos podem virar âncoras (`/perguntas-frequentes#local`). O Google exibe resultado em FAQ só para sites governamentais e de saúde desde 2023, mas o schema continua útil para a compreensão da página e para mecanismos de IA.

## Blog (30/10/2026)
Páginas reais por artigo, `BlogPosting` + `FAQPage` (+ `BreadcrumbList` quando houver `url_base`), título SEO próprio de até 60 caracteres, resumo como meta description, FAQ no fim de cada artigo e links internos para as rotas do site. `feed.xml` e `sitemap.xml` só são gerados com `url_base` e só incluem artigos com `revisado: sim`. O sitemap do blog deve ser referenciado no `sitemap.xml` principal quando o site migrar para rotas reais.
