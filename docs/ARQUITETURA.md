# MRO Brasil 2027 — Arquitetura, jornadas e sistema visual

Registro de decisões anterior à implementação. Fontes: briefing 2027, `proposta/ESCOPO-BRIEFING-2027.md`, `levantamento/` (site atual) e `prototipo/AGENTS.md`.

## 1. Arquitetura de informação

| Rota (prévia) | Caminho sugerido na publicação | Conteúdo | H1 |
|---|---|---|---|
| `#/` | `/` | Carrossel (2027, Reviva 2026, MANTAER), dados da edição, caminhos por perfil, apresentação, convites | MRO Brasil 2027 — Feira Internacional de Manutenção Aeronáutica |
| `#/feira` | `/feira` | Sobre a feira · Perfil do público · Oportunidades de participação · Informações práticas 2027 | A feira |
| `#/participar` | `/participar` | Escolha de perfil: Visitante e Expositor; acesso secundário a Patrocínio | Participar da MRO Brasil 2027 |
| `#/participar/visitante` | `/participar/visitante` | Explicação, limites do registro, formulário demonstrativo | Participar como visitante |
| `#/participar/expositor` | `/participar/expositor` | Caminho comercial, limites, formulário demonstrativo | Expor na MRO Brasil 2027 |
| `#/patrocinio` | `/patrocinio` | Apresentação institucional, convite à conversa, formulário | Patrocínio |
| `#/reviva-2026` | `/reviva-2026` | Filtros Fotos/Vídeos/Depoimentos, galeria com ampliação, estados pendentes | Reviva a MRO Brasil 2026 |
| `#/contato` | `/contato` | Canais confirmados da organização, local, redes | Contato |

Subdestinos com histórico próprio: `#/feira/sobre`, `#/feira/publico`, `#/feira/oportunidades`, `#/feira/informacoes`, `#/participar/visitante/formulario`, `#/participar/expositor/formulario`, `#/patrocinio/formulario`, `#/reviva-2026/fotos|videos|depoimentos`.

Navegação por hash: funciona no HTML independente (`file://`), com voltar/avançar. Na publicação, migrar para caminhos reais com reescrita no servidor.

Fora do menu: **Programação** (sem conteúdo confirmado) e **Idealização** (sem material aprovado).

## 2. Jornadas

- **Visitante**: pop-up “Quero visitar” ou Participar → Visitante → informações e limites → formulário (perfil Visitante; empresa opcional) → “Demonstração concluída”. Sem compra, ingresso ou credenciamento.
- **Expositor**: pop-up “Quero expor” ou Participar → Expositor → caminho comercial e limites → formulário (empresa obrigatória) → demonstração concluída. Sem reserva nem contratação.
- **Patrocinador**: pop-up “Quero patrocinar”, menu Patrocínio ou acesso secundário em Participar → apresentação → formulário (empresa obrigatória) → demonstração concluída. Sem cotas, preços ou contrapartidas.
- Qualquer formulário permite trocar o perfil sem perder o preenchimento; o perfil de origem é aplicado ao abrir a página correspondente.

## 3. Sistema visual

- **Cores** (extraídas do logotipo e das variáveis globais do Elementor do site atual):
  - Marinho institucional `#0A1438` (blocos escuros), texto `#14245E`, profundo `#01063A`.
  - Azul de interação `#1F5BD8` (links, foco, estados); azul secundário `#0D3F7D`.
  - Vermelho da marca `#E12429` (detalhes, “2027”, textos grandes); vermelho de botão `#C8161D` (contraste 5,8:1 com branco).
  - Superfícies `#FFFFFF`, `#F3F5F9`, linhas `#D8DEEA`.
- **Tipografia**: Exo 2 (400/600/700/800) para títulos e números; Roboto (400/500/700) para texto. Fontes locais em WOFF2.
  Escala fluida: display 44–92 px, H2 30–52 px, H3 20–26 px, corpo 17–18 px, rótulos 13 px em caixa alta espaçada.
- **Espaçamento**: base 8 px; seções 72–144 px; contêiner máx. 1280 px; margem lateral mínima 16 px.
- **Motivos gráficos**: fios finos com marcações de régua, índices numerados (01, 02…), cantos de enquadramento nas fotografias, grade técnica muito sutil nos blocos escuros, recorte diagonal das fotos inspirado em perfil de asa. Sem glassmorphism nem gradientes decorativos.
- **Componentes**: cabeçalho com submenu Participar; carrossel; listas editoriais numeradas (em vez de cartões); blocos institucionais escuros; avisos de limite; formulário com resumo de erros; diálogos (`<dialog>`) para perfil e galeria; estados de conteúdo pendente.

## 4. Navegação e CTAs

- Cabeçalho: Feira · Participar (Visitante, Expositor) · Patrocínio · Reviva 2026 · Contato. Botão principal vermelho **Participar** → escolha de perfil.
- Uma ação principal por contexto: home → “Conheça as formas de participação”; páginas de perfil → CTA específico do formulário; Feira → “Quero participar” ao final dos blocos.
- Rodapé: participação, patrocínio, contato, MANTAER, dados da edição e botão para reabrir a escolha de perfil.
- Sem botões fixos sobre o conteúdo no celular.

## 5. Direção aprovada (28/10/2026)

O cliente aprovou a **versão 2, institucional**, depois de considerar a v1 com "cara de landing page genérica":
- masthead com título fixo da feira, banner com foto ampla e painel azul-marinho sólido;
- vermelho reservado à ação principal e a pequenos detalhes; tipografia sóbria, sem números vazados gigantes;
- poucos blocos por página, com mais respiro; ficha da edição no lugar de faixas promocionais;
- abas de seção em Participar;
- animações discretas (entrada ao rolar, zoom lento do banner, transições de hover), sempre desativadas com `prefers-reduced-motion`.

Mudanças futuras devem seguir essa direção.

## 6. Personalidade visual (29/10/2026)

Depois da v2, o cliente achou o site "quadrado, sem personalidade" em comparação ao site atual. A v4 mantém a organização aprovada e traz de volta a linguagem da marca: banner da home como **palco de radar** (azul-profundo com luz azul elétrica, anéis de radar, grade técnica e uma rota de voo que o avião cruza uma vez), foto como cartão em perspectiva, títulos do banner em caixa alta (vernáculo do site atual), controles circulares, bordas diagonais nas faixas escuras e ícones em círculos. A luz azul fica restrita ao palco, aos cabeçalhos das páginas internas (mesmo palco, com foto em cartão, anéis e arco pontilhado de rota) e aos blocos da feira virtual.

Feira virtual 2026: tour 360° desenvolvido com a Orbitpan (https://app.orbitpan.com.br/mrobrasil/), carregado somente por clique.

## 7. Animação "Peça por peça" (29/10/2026)

Inspirada em referências do repositório awesome-opus5-5-videos (turbofan desmontável em estágios e "linha de lápis promovida" a desenho técnico), sem reaproveitar código. Na home, entre "A feira" e "Como participar": turbofan em corte, em SVG gerado por `scripts/gerar_turbina.py`, em papel de desenho técnico. Ao entrar na tela as linhas se desenham; em seguida o motor se desmonta nos 5 estágios (fan, compressor, câmara de combustão, turbina, bocal), na ordem do escoamento. O botão "Montar/Desmontar o motor" alterna; montado, o ar flui (bypass em azul, núcleo em vermelho), animado só enquanto visível. Com movimento reduzido, o motor aparece desmontado e parado. No celular, os nomes viram legenda numerada.

## 8. Identidade do folder 2027 e perguntas frequentes
- **Identidade:** camada “v5” no fim de `src/styles.css`. Tokens `--teal` (#00B1C4, ciano da marca) e `--teal-ink` (#00707D, versão com contraste AA sobre fundo claro), `--slate` (cinza grafite do painel de contato do folder), `--abyss` e `--cut` (tamanho do chanfro). Classe utilitária `.chamfer` para os cantos cortados do folder. Filete vermelho antes dos rótulos e do tema da edição.
- **Artes:** `assets/img/folder-{jato,globo,conferencia,tecnica}.jpg`, recortadas do PDF do folder a 3× (só JPEG: o `sips` do macOS gera AVIF que o Chrome não decodifica).
- **Home:** faixa do palco com o tema; “Nosso mercado é gigante” (`.market`); eventos (`.events-teaser`); destaques do FAQ (`.faq-teaser`). A seção de cartões Reviva/MANTAER saiu, pois repetia o carrossel.
- **Feira:** anéis de perfil do público (`.gauges`, valor em `--v`), seção Eventos (`#/feira/eventos`) e informações de acesso.
- **FAQ:** rota `#/perguntas-frequentes/{grupo}`; links da home com `data-faq-open` abrem a pergunta exata (o roteador troca o alvo do scroll pelo `<details>` correspondente).

## 9. Blog e acervo por arquivos
- **Reviva:** `content/reviva.json` → `scripts/gerar_reviva.py` (galeria, nota de status, VideoObject); `scripts/preparar_fotos.py` cria as versões otimizadas. Vídeo com player sob demanda.
- **Blog:** `content/blog/*.md` → `scripts/gerar_blog.py`. É a única parte com **páginas HTML reais** (`blog/…/index.html`), fora do roteador por `#`. Cabeçalho, rodapé e ícones são copiados de `index.html` (sempre sincronizados) e os links de rota viram `../index.html#/rota`. Só o menu usa JavaScript (`src/blog.js`). `scripts/qa_blog.py` verifica as páginas.
- **HTML único (`dist/`):** não contém o blog, que precisa de arquivos separados. A pasta `site-completo/` (entregue na área de trabalho) reúne `index.html`, `src/`, `assets/` e `blog/` para abrir tudo junto.

## 10. Site de publicação (páginas reais)
`scripts/gerar_site.py` lê `index.html` (a prévia) e `content/` e escreve `dist/site/`. O `app.js` entra em "modo páginas" quando a página define `window.MRO_MPA`: o roteador por `#` é substituído pela página do próprio HTML, e o `#` serve só de âncora ou de filtro do acervo. `scripts/rotas.py` converte `#/rota` em endereços relativos; `scripts/html2md.py` gera as versões em Markdown. Páginas sem carrossel ou sem acervo funcionam porque `Carousel` e `Gallery` retornam stubs quando faltam os elementos.
