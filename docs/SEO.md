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
| `organizer`, `image` e `url` no JSON-LD | Organizadora de 2027 e domínio não confirmados | `PENDENCIAS.md` |
| `BreadcrumbList` e `Organization` | Precisam de URLs reais e créditos institucionais confirmados | — |
| Logotipo em SVG | Falta o arquivo vetorial oficial | `PENDENCIAS.md` |
| `hreflang`, se houver versão em inglês | Decisão editorial | — |
