# Registro de testes — 28/10/2026 (versão 2, institucional)

A versão 2 redesenhou cabeçalho, home e páginas internas (direção mais institucional, menos informação por bloco, animações discretas). Todos os cenários abaixo foram executados novamente sobre a versão 2. A versão 1 está em `dist/versoes/` para comparação.

Ferramentas: Chrome headless via DevTools Protocol (`scripts/qa_cdp.py`, emulação real de 1440, 1024, 768, 390 e 360 px) e navegador integrado do Claude Code (verificação manual em 1440 e 390 px). Executado contra **o servidor local** (`http://localhost:5207/`) e contra **o HTML independente aberto por `file://`** (`dist/MRO-Brasil-2027-site.html`). Relatórios brutos: `qa/relatorio-qa-servidor-local.json` e `qa/relatorio-qa-html-unico.json`. Capturas: `qa/screenshots/*.jpg`.

| Critério | Servidor local | HTML único (file://) |
|---|---|---|
| 8 rotas + 404 abrem a página certa, com título e H1 próprios | ok | ok |
| Voltar e avançar do navegador | ok | ok |
| Links internos (`#/…`) sem destino inválido | 0 inválidos | 0 inválidos |
| Pop-up não abre no carregamento; abre na primeira rolagem (ou após 5 s); não reaparece ao recarregar na mesma sessão | ok | ok |
| Fechamento por Escape devolve o foco ao conteúdo; fechar não abre formulário | ok | ok |
| “Quero visitar” leva a Visitante com perfil Visitante no formulário | ok | ok |
| Reabrir a escolha pelo site (rodapé, home, Participar) | ok (manual) | ok |
| Carrossel: anterior, próximo, seleção direta, pausa/reprodução, setas do teclado | ok | ok |
| Altura estável entre slides; slides inativos `inert` | ok | ok |
| Carrossel pausa com foco, cursor, toque e diálogo aberto; movimento reduzido inicia pausado | ok (código e manual) | — |
| Convite MANTAER → `https://mantaer.com.br/associe-se/` em nova aba | ok | ok |
| Expositor/patrocinador exigem Empresa; visitante não | ok | ok |
| Erros: resumo focado com links aos campos, mensagens associadas (`aria-describedby`, `aria-invalid`) | ok | ok |
| Troca de perfil e de página preserva o preenchimento | ok | ok (servidor) |
| Duplo envio bloqueado durante a demonstração | ok | ok |
| Confirmação: “Demonstração concluída. Nenhuma solicitação foi enviada e nenhum dado foi armazenado.” | ok | ok |
| Nenhum dado pessoal em `localStorage`/`sessionStorage` (só a marca do pop-up) | ok | ok |
| Galeria: filtros com rota própria, ampliação, anterior/próxima, setas, Escape, foco de volta à miniatura | ok | ok |
| Elementos ultrapassando a largura da tela (8 páginas × 5 larguras = 40 combinações) | nenhum | nenhum |
| Imagens quebradas | 0 | 0 |
| Erros de console | 0 | 0 |
| Animações: entrada ao rolar, zoom lento do banner, painel do banner; desativadas com movimento reduzido | ok (manual) | ok |
| Requisições externas ao carregar (CDN, fontes, analytics) | 0 | 0 |

## Acessibilidade aplicada
Link “Pular para o conteúdo”; landmarks (`header`, `nav` rotulados, `main`, `footer`); um H1 estável por página (na home, fora do carrossel); foco visível com contraste em fundo claro e escuro; alvos ≥ 44 px; `<dialog>` modal (foco contido, Escape, retorno de foco); `aria-current` em menu, filtros e indicador do carrossel; região `aria-live` para troca manual de destaque e de rota; textos alternativos descritivos e imagens ilustrativas identificadas; `prefers-reduced-motion` respeitado. Contraste: botão vermelho `#C8161D` com branco ≈ 5,8:1; texto `#14245E` sobre branco ≈ 13:1; texto secundário `#4A5675` ≈ 7,5:1.

## Não verificado / limitações
- Leitores de tela reais (VoiceOver/NVDA) e Safari/Firefox não foram testados; a verificação foi em Chromium.
- Dispositivos físicos não testados (emulação de viewport).
- Skills `ui-ux-pro-max` e `frontend-design` não estão instaladas nesta sessão; as skills de acessibilidade e SEO disponíveis não foram executadas formalmente — os critérios equivalentes (WCAG 2.2 AA e SEO técnico) foram aplicados e conferidos manualmente.
- `qa/screenshots/*.png` são as capturas originais sem compressão; o ZIP leva as versões `.jpg`.

## Rodada da auditoria de UI/UX (28/10/2026)
Aplicados os grupos A e B: contraste dos números do carrossel (1,35:1 → 7,3:1) e rótulos curtos no celular; data do cabeçalho legível por leitores de tela; pré-carregamento da fonte de títulos (700) e da imagem principal corrigidos; alvos de toque de 44 px na faixa superior e espaçamento de 8 px nos controles do carrossel; animação de entrada mais curta (450 ms, 16 px) com tempos centralizados em variáveis; 5,7 KB de CSS antigo removidos; pop-up após rolagem ou 5 s; galeria Reviva com um aviso por tipo pendente; menu interno da Feira fixo e marcando a seção atual; banner móvel com uma ação principal. Durante a revisão foi encontrado e corrigido um defeito da v2: o cabeçalho da Reviva 2026 perdia o fundo escuro. Todos os cenários foram executados novamente com resultado ok.
