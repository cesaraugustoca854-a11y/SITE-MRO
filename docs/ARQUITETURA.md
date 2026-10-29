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
