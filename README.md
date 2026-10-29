# MRO Brasil 2027 — site remodelado (prévia para aprovação)

Frontend novo, independente de WordPress e plugins. HTML, CSS e JavaScript sem dependências externas; fontes e imagens locais.

## Abrir

- **Sem instalação:** abra `dist/MRO-Brasil-2027-site.html` no navegador (duplo clique). Tudo está incorporado no arquivo; só os links externos (MANTAER, mapa, redes, WhatsApp) dependem de internet.
- **Código-fonte local:** `python3 -m http.server 5207 --directory .` dentro desta pasta e acesse `http://localhost:5207/`. O `index.html` também abre direto por `file://`.
- **Gerar novamente o HTML único e o ZIP:** `python3 scripts/build_single.py`.

Navegação por hash (`#/feira`, `#/participar/visitante`…), compatível com `file://` e com voltar/avançar. Para capturas de QA sem o pop-up, acrescente `?sem-popup` antes do `#`.

## Versões

- **v2 (atual):** direção institucional, menos informação por bloco, animações discretas.
- **v1:** `dist/versoes/v1-MRO-Brasil-2027-site.html`, mantida para comparação.

## Estrutura

```
index.html            páginas (Início, Feira, Participar, Visitante, Expositor, Patrocínio, Reviva 2026, Contato)
src/styles.css        sistema visual
src/app.js            rotas, menu, carrossel, pop-up, galeria e formulário
src/lead-adapter.js   camada de envio — hoje só demonstração; ponto de conexão do CRM
assets/               fontes WOFF2 (Exo 2, Roboto) e imagens otimizadas
scripts/build_single.py  gera dist/ (HTML único + ZIP)
docs/                 arquitetura, pendências, URLs antigas, publicação, CRM e testes
qa/screenshots/       capturas de verificação
```

## Limitações reais desta entrega

- **Formulários são demonstração.** Não enviam nem armazenam dados; a confirmação diz isso. A integração com o Tio CRM não foi feita (ver `docs/INTEGRACAO-CRM.md`).
- **Não publicado.** A prévia está com `noindex` e `robots.txt` bloqueando tudo. Canonical, `og:url` e `og:image` absolutos dependem do domínio definitivo (`docs/PUBLICACAO.md`).
- **Imagens ilustrativas** (hangar, pavilhão, painel) estão identificadas como tal. Não há registros oficiais da edição 2026 nem vídeos ou depoimentos; a página Reviva 2026 mostra estados pendentes.
- Seções **Programação** e **Idealização** não foram publicadas por falta de material aprovado.
- Textos foram redigidos para validação da organização (`docs/PENDENCIAS.md`).
- Nenhuma alteração foi feita no site em produção nem nos painéis de hospedagem.
