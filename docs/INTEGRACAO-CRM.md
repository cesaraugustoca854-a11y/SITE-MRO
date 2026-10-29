# Integração com o Tio CRM — adiada

Estado: **não implementada**. Nenhum envio, API, webhook ou banco de dados existe nesta entrega.

## Onde conectar
`src/lead-adapter.js` concentra o envio. Hoje `MODO = "demonstracao"` e o payload é descartado. O formulário (`src/app.js`, módulo `Form`) só conhece `MROLeads.enviar(dados)` e trata sucesso/erro; a interface não muda quando a integração entrar.

Payload previsto (já montado no adaptador):
```json
{ "idEnvio": "uuid", "campanha": "MRO Brasil 2027", "perfil": "visitante|expositor|patrocinador",
  "contato": { "nome": "", "email": "normalizado", "empresa": null, "telefone": null },
  "mensagem": null, "origem": { "pagina": "#/participar/visitante", "enviadoEm": "ISO-8601" } }
```

## Requisitos (briefing, seção 5)
- Endpoint próprio no servidor; credenciais do CRM nunca no navegador.
- Validação também no servidor; idempotência por `idEnvio` (duplo clique, reenvio).
- Sucesso só após confirmação do CRM ou gravação em fila durável; em falha, manter os dados no formulário e permitir nova tentativa (o front já faz isso no caminho de erro).
- Deduplicação por e-mail normalizado; interesses separados por perfil e edição.
- Registrar campanha, perfil, página de origem, data/hora e UTMs.
- Aviso de privacidade com finalidade; consentimento de marketing separado.

## A levantar com o fornecedor
Documentação de API/webhook ou formulário incorporável, ambiente de testes, campos e etapas, responsáveis pelo recebimento. Em 28/10/2026 apenas a tela de login de https://tiocrm.com.br/ foi consultada; não há documentação pública localizada.
