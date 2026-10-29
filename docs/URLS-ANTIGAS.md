# Inventário do site atual e redirecionamentos sugeridos

Fonte: `levantamento/paginas.json` (13 páginas publicadas + 1 rascunho). Os destinos usam os caminhos sugeridos para a publicação (sem `#`); na prévia equivalem a `#/…`.

| URL atual | Conteúdo observado | Destino sugerido | Tipo | Observação |
|---|---|---|---|---|
| `/` | Home MRO Brasil 2026 (datas 2026, hotéis, palestrantes 2025/2026) | `/` | — | Conteúdo substituído pela edição 2027 |
| `/home/negocios/` | Proposta comercial, perfil de decisores, “balcão de peças/serviços” 2026 | `/feira#oportunidades` | 301 | Balcões não confirmados para 2027 |
| `/home/eventos/` | Eventos paralelos | `/feira` | 301 | Reativar como Programação quando houver conteúdo |
| `/home/seja-um-expositor/` | Convite a expositores, galeria 2024 | `/participar/expositor` | 301 | |
| `/home/seja-um-patrocinador/` | Convite a patrocinadores | `/patrocinio` | 301 | |
| `/home/imprensa/` | Imprensa | `/contato` | 302 | Temporário até haver área de imprensa |
| `/home/fale-conosco/` | Formulário CF7, telefones, e-mail | `/contato` | 301 | |
| `/home/depoimentos/` | Vídeos de depoimentos (edições anteriores) | `/reviva-2026/depoimentos` | 302 | Não reclassificar vídeos antigos como 2026 |
| `/home/como-foi-a-mro-brasil-2024/` | Galeria 2024 | manter como arquivo (`/edicoes/2024`) | 301 | Decidir se o arquivo 2024 será mantido |
| `/home/expositores-para-2025/` | Lista de expositores 2025 | arquivo (`/edicoes/2025/expositores`) ou 410 | 301/410 | Decisão editorial |
| `/home/expositores-de-2026/` | Lista de expositores 2026 | `/reviva-2026` ou arquivo próprio | 301 | Lista não migrada nesta entrega |
| `/politica-de-privacidade/` | Política vigente | manter até nova política aprovada | — | |
| `/politica-de-cookies/` | Política vigente | manter até nova política aprovada | — | |
| `/?page_id=13600` (rascunho) | Landing page 2024 | não migrar | — | Rascunho não publicado |

## Ativos a preservar
- Logotipos MRO por edição (2024, 2026, 2027) e MANTAER.
- Galeria 2024 (`wp-content/uploads/…`), vídeos de depoimentos e listas de expositores 2025/2026 — não foram baixados integralmente (ver `levantamento/LEIA-ME.md`).
- Fontes Exo 2 e Roboto (agora locais em WOFF2).
- Perfis sociais: LinkedIn `company/mrobrasil`, Facebook `mrobrasil`, Instagram `mrobrasil2024`.
