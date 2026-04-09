# Montagem do prompt enviado ao LLM

Este documento descreve **o que entra no prompt** a cada chamada ao modelo via `ask_watson` em `cli_chatbot/watson_client.py`, e como isso se relaciona com RAG, histórico e ramo determinístico.

---

## Visão geral

Em **cada** uso do LLM (watsonx.ai) pelo fluxo `gerar_resposta` → `ask_watson`, o serviço monta um único texto (`full_prompt`) e chama `generate` com esse prompt. O modelo **processa esse texto inteiro** para gerar a resposta.

Ordem lógica do conteúdo:

1. **Prompt base** — conteúdo completo de `prompts/base_prompt.txt` (papel do assistente, tom, regras de cálculo quando aplicável, etc.).
2. **Bloco RAG** (se estiver habilitado e disponível) — instruções de `prompts/rag_instructions.txt` + os **K** trechos do acervo com **maior similaridade** à pergunta atual (`K` = `RAG_TOP_K`, ex.: variável de ambiente).
3. **Histórico da conversa** — turnos anteriores em texto (`chat_history`), quando existir.
4. **Pergunta atual** — no formato `Usuário: {pergunta}`.

Referência no código:

```text
full_prompt =
  base_prompt.txt
+ rag_section (instruções RAG + trechos formatados, ou vazio)
+ history_text
+ "Usuário: " + pergunta
```

Implementação: `cli_chatbot/watson_client.py`, função `ask_watson` (montagem de `full_prompt`) e `_build_rag_section` (montagem do bloco RAG).

---

## Detalhe do bloco RAG

Quando `WATSON_AI_RAG` não está desligado **e** o retrieval está operacional (`sentence-transformers` instalado, corpus carregado, sem erro em `retrieve_top_k`):

- É lido o arquivo `prompts/rag_instructions.txt`.
- São recuperados os **K melhores chunks** por similaridade coseno com a pergunta (`retrieve_top_k` em `cli_chatbot/rag/retriever.py`).
- Os trechos são formatados para o prompt (`format_retrieved_for_prompt`) e inseridos em `### Contexto recuperado do acervo institucional`.

Se o RAG estiver desligado ou indisponível, `rag_section` fica **vazio**; o modelo recebe apenas **base + histórico + pergunta**.

---

## Quando o LLM **não** é chamado

- Perguntas que o **roteador** encaminha para a **calculadora determinística** (`cli_chatbot/calculadora.py`) **não** passam por `ask_watson`: não há montagem desse prompt nem chamada ao modelo para aquela mensagem.

---

## Relação com outros documentos

- Fluxo de retrieval (embeddings, corpus, top‑K): **`docs/rag-pipeline.md`**
- Parâmetros de geração do modelo (greedy, `max_new_tokens`, `stop_sequences`, etc.): **`docs/parametros-geracao-watsonx.md`**
- Convenções do acervo: **`knowledge/README.md`**

---

## Variáveis de ambiente relevantes

| Variável | Efeito no prompt ao LLM |
|----------|-------------------------|
| `WATSON_AI_RAG` | `0` remove o bloco RAG (só base + histórico + pergunta). |
| `RAG_TOP_K` | Quantidade máxima de trechos do acervo incluídos no bloco RAG. |
| `RAG_EMBEDDING_MODEL` | Modelo de embeddings usado no retrieval (não é o LLM gerador). |

O modelo gerador (ex.: `WATSONX_MODEL_ID`) é independente desses parâmetros de retrieval.
