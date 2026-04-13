# Roteamento PoC: Watson Assistant (determinístico) ↔ LLM + RAG

Objetivo: descrever o fluxo alvo quando a PoC passar a usar **dois backends** — diálogo no **Assistant** e respostas abertas no **watsonx + RAG** — e como o usuário **volta** ao fluxo guiado.

## Papéis

| Camada | Função |
|--------|--------|
| **Watson Assistant** | Fluxos transacionais (Actions), coleta de dados, validações, menus e CTAs. Uma **sessão** (`session_id`) mantém o estado do diálogo. |
| **LLM + RAG (watsonx)** | Perguntas informativas fora do menu, baixa confiança no Assistant, ou ramo explícito “dúvida geral” com acervo (`knowledge/corpus`). |

## Estado na aplicação (Gradio / API)

- **`wa_session_id`**: ID retornado pela API do Assistant após `create_session` (ou reutilizado entre turnos). Obrigatório para continuar o mesmo fluxo (ex.: responder “Sim” depois da pergunta do Portal).
- **`modo`**: `assistant` | `llm_rag` — indica qual backend processa a **próxima** mensagem do usuário.
- **`user_id`**: estável por usuário/chat (já exigido pela API em muitas instâncias); alinhar com persistência de atendimento se houver.

## Fluxo recomendado (alto nível)

1. **Entrada** sempre pode ir primeiro ao **Assistant** com a mensagem do usuário e o `session_id` atual (criar sessão só na primeira interação ou após “reset”).
2. **Inspecionar a resposta** do Assistant (texto, opções, `intents`, `context`):
   - Se o fluxo **continua no Assistant** (pergunta com opções, slot, próximo passo) → manter `modo=assistant`, mostrar resposta, aguardar próximo turno **no mesmo `session_id`**.
3. **Fallback para LLM + RAG** quando:
   - o desenho no Assistant tiver um **nó/ação** “pergunta livre” / “não entendi” / confiança baixa que **dispare** o backend; ou
   - a PoC decidir por **heurística** (fora do Assistant) que a mensagem é informativa e não deve avançar slot — então `modo=llm_rag`, chamar `gerar_resposta` / `ask_watson` com histórico adequado.
4. **Voltar ao Assistant**:
   - **Preferencial (produto):** no próprio Assistant, um intent/ação “voltar ao menu” / “falar com atendimento” / CTA que retoma o fluxo; a app volta a enviar mensagens com o **mesmo** `session_id` se o contexto ainda fizer sentido, ou **nova sessão** se o fluxo exigir recomeço.
   - **Na PoC:** após uma resposta RAG, exibir botões ou texto fixo: *“Para segunda via de boleto, digite…”* que o usuário envia como nova mensagem ao Assistant (com sessão existente ou nova, conforme regra de negócio).

## Interface Watson Assistant (opção B — roteamento na app)

**Não é obrigatório** criar variáveis de contexto nem “variáveis” especiais só para o Python: o roteamento **Assistente vs Acervo** é feito no **Gradio** (`modo` radio), não no produto IBM.

- **O que você já deve ter na UI:** Actions e fluxos como hoje (segunda via, simulação, etc.).
- **Opcional (UX):** mensagens de CTA no Assistant (“*Para dúvidas gerais, use o modo Acervo no chat da PoC*”) — texto fixo, **sem** integração extra.
- **Não precisa** ligar **Conversational Search** nem Elasticsearch para a opção B; o RAG fica no **Python** (`knowledge/corpus`).

## Contrato na implementação (código)

- Um turno Assistant: `WatsonAssistantConversation.send` em `cli_chatbot/watson_assistant_client.py`.
- Roteador: `gerar_resposta_roteada` em `cli_chatbot/hybrid_router.py` (`modo` = `assistant` | `llm_rag`).
- UI: `web_chatbot.py` — radio **Onde enviar a próxima mensagem**; **Limpar conversa** zera também a sessão do Assistant na memória.
- **Voltar ao fluxo:** o usuário seleciona de novo **Assistente** e continua (mesma `wa_session_id` até limpar o chat).

## Script de teste (CLI)

- Uma mensagem: `python scripts/test_watson_assistant_message.py "texto"` (cria sessão e imprime `session_id` em stderr).
- Continuar: `--session-id <uuid>` ou `WATSON_ASSISTANT_SESSION_ID`.
- Várias mensagens no mesmo terminal: `-i` / `--interactive`.

Documentos relacionados: `docs/proposta-arquitetura-hibrida-poc.md`, `docs/plano-de-acao-poc-hibrida.md`.
