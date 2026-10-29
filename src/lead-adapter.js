/*
 * Camada de envio de interesse (lead).
 *
 * Nesta entrega o modo é exclusivamente "demonstracao": nada sai do navegador,
 * nada é gravado em storage, arquivo ou rede. O retorno apenas sinaliza que a
 * demonstração terminou.
 *
 * Integração futura (Tio CRM — https://tiocrm.com.br/): substituir o corpo de
 * `enviar` por uma chamada a um endpoint próprio do servidor (nunca ao CRM
 * direto do navegador, para não expor credenciais). O servidor valida os
 * dados, aplica idempotência por `idEnvio`, grava em fila durável e só então
 * responde com sucesso. Ver docs/INTEGRACAO-CRM.md.
 */
(function () {
  "use strict";

  var MODO = "demonstracao";

  function novoIdEnvio() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    return "env-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  /**
   * Monta o payload previsto para o CRM. Na demonstração ele é descartado.
   * @param {{perfil:string,nome:string,email:string,empresa:string,telefone:string,mensagem:string}} dados
   */
  function montarPayload(dados) {
    return {
      idEnvio: novoIdEnvio(),
      campanha: "MRO Brasil 2027",
      perfil: dados.perfil,
      contato: {
        nome: dados.nome.trim(),
        email: dados.email.trim().toLowerCase(),
        empresa: dados.empresa.trim() || null,
        telefone: dados.telefone.trim() || null
      },
      mensagem: dados.mensagem.trim() || null,
      origem: { pagina: location.hash || "#/", enviadoEm: new Date().toISOString() }
    };
  }

  function enviar(dados) {
    var payload = montarPayload(dados);
    if (MODO === "demonstracao") {
      payload = null; // descartado: nenhum envio e nenhum armazenamento
      return new Promise(function (resolve) {
        setTimeout(function () { resolve({ status: "demonstracao" }); }, 700);
      });
    }
    return Promise.reject(new Error("Integração com CRM não configurada."));
  }

  window.MROLeads = { modo: MODO, enviar: enviar };
})();
