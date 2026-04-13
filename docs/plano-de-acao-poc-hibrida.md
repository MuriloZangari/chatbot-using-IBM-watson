# Plano de ação — PoC híbrida (estudos `WATSON_AI` + Watson Assistant)

**Objetivo:** sequenciar o aprendizado e os entregáveis de forma **estruturada**, alinhada a:

- `docs/pesquisa-chatbot-hibrido-watson.md` — papéis dos produtos, integração Assistant → backend → watsonx, critérios de sucesso da pesquisa;
- `docs/proposta-arquitetura-hibrida-poc.md` — fluxo Action matching → determinístico vs. conversational search, search **dentro** de Action, CTAs após resposta aberta.

**Premissa:** este plano é **para estudo e PoC**; o projeto corporativo (orquestrador, Portal, produção) seguirá políticas e cronograma próprios.

---

## Visão das fases

| Fase | Tema | Resultado esperado |
|------|------|---------------------|
| 0 | Pré-requisitos | Conta IBM, assistente de teste, credenciais documentadas (sem segredos no Git). |
| 1 | PoC Python (já avançada) | RAG, prompts, roteador calculadora ↔ LLM estáveis como **referência de comportamento**. |
| 2 | Modelo mínimo no **Watson Assistant** | Um assistente de laboratório com **Actions** e **fluxo transacional curto** (simulado). |
| 3 | Ramo informativo no Assistant | **Conversational search** (e/ou step alinhado ao acervo) **dentro de uma Action** + **CTAs** para voltar ao determinístico. |
| 4 | Integração **SDK** | Cliente (script ou módulo) que chama `message` / sessão contra o assistente da fase 2–3; opcionalmente encaixe com a PoC Python. |
| 5 | Consolidação | Decisões documentadas, riscos, diagrama alvo, critérios “quando LLM / quando fluxo” — entregáveis da pesquisa. |
| 6 (opcional) | **Watson Orchestrate** | Avaliar só se houver necessidade de multi-agente / orquestração ampla; não é bloqueio das fases 0–5. |

---

## Fase 0 — Pré-requisitos

1. Acesso a **IBM Cloud** (ou ambiente onde o **watsonx Assistant** esteja habilitado para testes).
2. Criar um **assistant** exclusivo para PoC (nome claro, ex.: `poc-hibrido-lab`).
3. Gerar **API key** (e anotar **region URL**, **assistant_id**, versão da API) em local seguro — **não** commitar no repositório; usar `.env` e `.gitignore`.
4. Ler a documentação atual de **Actions**, **conversational search** e limites do plano (quotas).

**Entregável:** checklist preenchido (mesmo que em documento interno do time) com IDs e URLs **sem** expor chaves.

---

## Fase 1 — PoC Python (`WATSON_AI`) como referência

1. Manter o repositório como **laboratório** de: corpus JSON, retrieval, `base_prompt` / `rag_instructions`, parâmetros watsonx (`parametros-geracao-watsonx.md`).
2. Garantir que o **roteador** (determinístico vs. LLM) continue **explícito** no código — espelho conceitual do “Assistant + fallback” da pesquisa.
3. Registrar **perguntas de teste** e respostas aceitáveis (fidelidade ao chunk).

**Entregável:** PoC reproduzível (README + `.env.example` sem segredos).

**Status típico:** grande parte **já realizada**; esta fase é **consolidação** antes de carregar o Assistant.

---

## Fase 2 — Construir modelo mínimo no Watson Assistant (UI)

**Checklist passo a passo:** `docs/guia-poc-watson-assistant-ui.md`.

Objetivo: aprender **Actions** e um **fluxo transacional enxuto** (simulado), sem ainda exigir integração real com Portal.

Sugestão de escopo mínimo:

1. **Uma** Action principal (ex.: “Simulação de atendimento — pagamentos”).
2. **Passos determinísticos:** menu com 2–3 opções → confirmação → mensagem fixa ou **mock** de “sucesso” (sem API real, ou chamada HTTP de teste).
3. Publicar **draft** e testar no **preview** do Assistant.

**Entregável:** fluxo funcional na UI + capturas ou descrição dos steps para o repositório de estudo (opcional: export JSON de backup, se a política permitir).

---

## Fase 3 — Search informativo + CTAs (proposta de arquitetura)

Objetivo: materializar `docs/proposta-arquitetura-hibrida-poc.md` **no produto Assistant**, em escala reduzida.

1. Criar (ou estender) uma Action de contexto, ex.: **“Ajuda sobre pagamentos”**.
2. Incluir um **step** de **conversational search** (conforme documentação IBM vigente) ou equivalente suportado no seu ambiente, alinhado ao conteúdo institucional de teste.
3. **Steps seguintes** com **CTAs** explícitos, por exemplo:
   - “Quer seguir para emitir boleto?” → encaminha para Action da fase 2 (ou subfluxo simulado).
   - “Quer voltar ao menu principal?”
4. Validar o anti-padrão: evitar **só** texto informativo sem saída operacional.

**Entregável:** percurso completo testado no preview + notas de o que funcionou / limitações (search, idioma, acervo).

---

## Fase 4 — Integração via SDK

Objetivo: provar o ciclo **código ↔ Assistant publicado**, como em `pesquisa-chatbot-hibrido-watson.md` (passos 1–2 do usuário via API).

1. Escolher stack: **Python** (`ibm-watson`) ou **Node** (`ibm-watson` / REST), coerente com o time.
2. Implementar **script mínimo** (pode ficar em `WATSON_AI/scripts/` ou repositório separado):
   - criar sessão;
   - enviar mensagens em loop ou cenários fixos;
   - imprimir respostas e **IDs de sessão**.
3. **Opcional avançado:** o script ou um **adapter** na PoC escolhe entre “só Assistant” e “Assistant + chamada watsonx” conforme o desenho corporativo (fase posterior).

**Entregável:** script funcional + README de como executar (variáveis de ambiente nomeadas, sem valores secretos).

---

## Fase 5 — Consolidação (entregáveis da pesquisa)

Conforme `pesquisa-chatbot-hibrido-watson.md` — **Entregáveis esperados** e **Critérios de sucesso**:

1. **Documento de arquitetura alvo** (pode ser evolução de `proposta-arquitetura-hibrida-poc.md` + diagrama Assistant ↔ backend ↔ watsonx).
2. **Lista de decisões:** o que permanece 100% no fluxo; o que pode usar search/LLM; o que exige confirmação humana ou política extra.
3. **Riscos e mitigações:** alucinação, dados sensíveis, compliance, custo e latência.
4. **Tabela “quando LLM / quando fluxo”** — critérios operacionais para o projeto real.

**Entregável:** um único markdown de síntese ou slides para o time — referência para o **orquestrador** e para negócios.

---

## Fase 6 (opcional) — Watson Orchestrate

1. Só iniciar se surgir requisito claro de **multi-agente**, **ferramentas** complexas ou orquestração além do Assistant.
2. Usar `docs/watson-assistant-orchestrate-hibrido.md` como base.
3. **Entregável:** nota de viabilidade (sim/não/depois) sem bloquear as fases 0–5.

---

## Ordem sugerida e dependências

```text
Fase 0 → Fase 1 (paralelo OK) → Fase 2 → Fase 3 → Fase 4 → Fase 5
                                              ↑
                                    Fase 3 depende de Fase 2
                                    Fase 4 depende de Fase 2 (mínimo) e idealmente Fase 3
```

---

## Critérios de conclusão da PoC de estudos

- Conseguir **demonstrar ao vivo** (ou gravado): **fluxo determinístico** no Assistant + **pergunta aberta** com **search** + **CTA** para fluxo conhecido.
- Ter **integração SDK** mínima funcionando.
- Ter **documento de consolidação** (Fase 5) alinhado aos critérios da pesquisa.

---

## Referências cruzadas

| Documento | Uso neste plano |
|-----------|-----------------|
| `pesquisa-chatbot-hibrido-watson.md` | Objetivo da pesquisa, diagrama IBM, analogia MVP vs. alvo, entregáveis. |
| `proposta-arquitetura-hibrida-poc.md` | Fluxo lógico, search em Action, CTAs, regras por tipo de necessidade. |
| `watson-assistant-orchestrate-hibrido.md` | Escopo opcional Orchestrate. |
| `integracao-rag-orquestrador-nestjs.md` | Evolução futura no back-end Node. |

---

*Última atualização: plano inicial alinhado aos documentos de pesquisa e proposta de arquitetura da PoC.*
