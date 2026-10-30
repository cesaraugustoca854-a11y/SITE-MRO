# Conteúdo oficial pendente

Itens que a organização precisa fornecer ou aprovar antes da publicação. Nada desta lista foi inventado no site; onde falta material, há estado pendente identificado ou a seção foi omitida.

## Edição 2027
- [x] Datas, local e endereço confirmados pelo folder oficial 2027: 20 e 21/10/2027, Centro de Convenções Frei Caneca, Rua Frei Caneca, 569 — Bela Vista.
- [ ] **Erro no folder impresso:** no painel central da página 1, ao lado do logotipo, a data aparece como “20 e 21 de outubro 2026”. As demais ocorrências dizem 2027. Corrigir antes de imprimir/divulgar.
- [ ] Andar/pavilhão da edição 2027.
- [ ] Horários de funcionamento.
- [ ] Programação (habilita a entrada “Programação” no menu).
- [ ] Regras de credenciamento/acesso de visitantes e eventual checkout futuro.
- [ ] Logotipo em vetor (SVG/PDF). O logotipo usado é o PNG de `prototipo/public/assets/logo-mro2027.png`, apenas recortado.
- [x] Key visual 2027: as artes em holograma azul do folder (jato, globo, plateia, técnicos) foram recortadas do PDF e estão em `assets/img/folder-*.jpg`, com a legenda “Arte do folder MRO Brasil 2027”. Quando houver os arquivos originais em alta, substituir os recortes.

## Textos
- [ ] Revisão e aprovação de todos os textos (Sobre a feira, Perfil do público, Visitante, Expositor, Patrocínio, mensagens de formulário). Redação técnica proposta com base no site atual e no briefing.
- [x] Perfil do público: substituído pelos dados do folder (mais de 4 mil visitantes; 85% decidem ou influenciam compras; 38% diretores/presidentes/VP/proprietários; 24% gerentes/coordenadores/supervisores; lista de funções).
- [ ] Fonte e ano-base dos números de mercado do folder (4º maior mercado de MRO do mundo, US$ 2,5 bilhões/ano, +2.000 empresas). O site atribui os dados “à organização da MRO Brasil”.
- [ ] Eventos da feira: confirmar nomes oficiais e numeração de edição em 2027 (folder: Fórum Nacional de Formação em Manutenção Aeronáutica 3ª, Encontro com a ANAC 3ª, Brazilian Supply Chain Summit 3ª, Encontro Nacional das Oficinas de Manutenção 2ª, Competição de Manutenção Aeronáutica 3ª), datas e horários de cada um.
- [ ] Organizador: o site cita “Aeromarketing / Delta Fox Eventos”, como no rodapé do folder. Confirmar a grafia institucional.
- [ ] Créditos institucionais de 2027 (organização, supervisão, apoios). O site atual cita “organizado por Delta Fox Eventos, com supervisão de MANTAER” para 2026; a prévia só menciona Delta Fox como canal de atendimento.

## Perguntas frequentes
- [ ] Validar as 19 respostas de `content/faq.json` com a organização. Respostas sobre horários, credenciamento, programação e cotas dizem honestamente que a informação ainda será divulgada; atualizar quando houver dado oficial e rodar `python3 scripts/gerar_faq.py`.

## Blog
- [ ] Revisar e aprovar os 3 artigos rascunho em `content/blog/` (IA no MRO, mercado brasileiro, como expor). Foram escritos só com dados do folder; as definições das seis frentes de IA são explicações gerais, não afirmações da organização. Depois, `revisado: sim`.
- [ ] Definir autoria (hoje "Organização da MRO Brasil") e a periodicidade de novos artigos.
- [ ] Endereço final do site em `content/blog/config.json` (`url_base`).

## Idealização (seção não publicada)
- [ ] Nome, tratamento/cargo correto, papel no projeto, biografia final, fotografia e autorização de uso.

## Reviva 2026
- Fluxo de publicação por arquivos: `docs/CONTEUDO.md` (`content/reviva.json`, `scripts/preparar_fotos.py`, `scripts/gerar_reviva.py`).
- [ ] Fotos oficiais da edição 2026, com legendas e autorização (substituir as 3 demonstrações e os espaços pendentes).
- [ ] Vídeos (arquivo MP4/WebM ou link de plataforma) com miniatura e legenda/transcrição.
- [ ] Depoimentos com nome, cargo, empresa e autorização de uso de imagem e fala.
- Observação: a galeria do site atual é da edição **2024** e não foi reclassificada como 2026.

## Patrocínio e exposição
- [ ] Apresentação institucional aprovada para patrocinadores; cotas, valores e contrapartidas, se e quando definidos.
- [ ] Condições de exposição 2027 (plantas, formatos), se forem publicadas.
- [ ] Prazo de retorno da equipe comercial (hoje o site não promete prazo).

## Contato, MANTAER e jurídico
- [x] Canais confirmados pelo folder 2027: WhatsApp (11) 5041-2088, telefone (11) 5548-3977, e-mail contato@deltafoxeventos.com.br. O WhatsApp (61) 99102-1608, que vinha do site antigo, foi substituído.
- [ ] Horário de atendimento (seg. a sex., 8h–17h) ainda vem do site antigo; reconfirmar.
- [ ] Perfil do Instagram: o link atual é `instagram.com/mrobrasil2024`; confirmar o perfil vigente.
- [ ] Logotipo da MANTAER em maior resolução (o disponível tem 250×73 px).
- [ ] Política de privacidade e de cookies aprovadas; texto de finalidade para os formulários; consentimento separado para comunicações de marketing.

## CRM (adiado)
- [ ] Ver `INTEGRACAO-CRM.md`.
