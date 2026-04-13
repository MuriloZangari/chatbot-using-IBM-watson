# RAG (MVP) — como funciona neste projeto

## O que é “RAG de verdade” aqui

1. **Acervo** — textos em `knowledge/corpus/*.json` (chunks com `id`, `source`, `text`; opcional `theme`). **Todos** os `.json` da pasta entram no mesmo índice (concatenados na ordem do nome do arquivo).
2. **Embeddings** — cada chunk vira um vetor com `sentence-transformers` (modelo configurável via `RAG_EMBEDDING_MODEL`).
3. **Consulta** — a pergunta do usuário vira vetor; calcula-se **similaridade coseno** com todos os chunks.
4. **Top-K** — os `RAG_TOP_K` trechos com maior similaridade entram no prompt (padrão **6**; com índice pequeno, o efeito prático é limitado ao número de chunks existentes). Com vários temas, reduza `RAG_TOP_K` se quiser menos trechos concorrentes no prompt.
5. **Geração** — o modelo LLM responde **condicionado** a esse contexto (trechos escolhidos pela pergunta, não texto fixo genérico).

**Como isso entra no prompt completo enviado ao LLM** (base + RAG + histórico + pergunta): ver **`docs/montagem-do-prompt-llm.md`**.

**O que é o score dos chunks, classificação vs. retrieval, modelo de embeddings:** ver **`docs/pontuacao-chunks-e-embeddings.md`**.

**Equivalência com o orquestrador (NestJS):** ver **`docs/integracao-rag-orquestrador-nestjs.md`**.

## Onde no código

| Peça | Arquivo |
|------|---------|
| Corpus | `knowledge/corpus/*.json` (ex.: `financiamento_veiculos.json`, `cobrancas_negativacao.json`, `gravame.json`) |
| Carregamento | `cli_chatbot/rag/corpus_loader.py` (`load_all_corpus_json`, `load_corpus_json`) |
| Retrieval | `cli_chatbot/rag/retriever.py` (`retrieve_top_k`, `format_retrieved_for_prompt`) |
| Injeção no prompt | `cli_chatbot/watson_client.py` (`_build_rag_section` → `ask_watson`) |
| Desligar RAG | `.env`: `WATSON_AI_RAG=0` |

## Perguntas de teste sugeridas

- `Tenho dúvida sobre financiamento` — chunk `fin_001` (texto completo do fluxo).
- `Estou negativado no Serasa` — chunk `neg_001`.
- `Paguei mas ainda recebo cobrança` — chunk `cob_001`.
- Perguntas sobre **gravame** / DETRAN / SNG — chunk `grav_001` (`gravame.json`).
- Perguntas com números para cálculo continuam no **ramo determinístico** (`calculadora.py`), sem passar pelo RAG.

## Próximos passos (evolução)

- Ingestão a partir de export do Watson Assistant ou CMS corporativo.
- Re-ranking, filtros por metadata (`source`, canal).
- Embeddings via API IBM (em vez de local), se política de infra exigir.
