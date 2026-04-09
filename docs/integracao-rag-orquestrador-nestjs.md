# PoC Python e orquestrador (NestJS / Node): mesma ideia, outra stack

Este documento amarra o que o **WATSON_AI** faz hoje em Python ao que **pode** ser feito no **orquestrador** (TypeScript, NestJS), para deixar claro: **não há dependência intrínseca de Python** para o retrieval com score — só foi o caminho mais rápido para a PoC.

---

## 1. O que é portável (lógica)

O fluxo RAG deste repositório resume-se a:

1. Ter um **acervo de chunks** (texto + metadados, ex.: JSON).
2. Obter um **vetor (embedding)** para a pergunta e um para cada chunk (mesmo modelo, mesma dimensão).
3. Calcular **similaridade coseno** (ou equivalente com vetores normalizados).
4. **Ordenar** e selecionar os **K** melhores (`top‑K`).
5. Montar o **prompt** para o LLM com instruções + trechos recuperados.

Os passos **2–4** são **operações matemáticas e de ordenação**; implementá-las em **TypeScript** é direto (arrays, `Float32Array`, função de coseno, `sort`). O que muda é **onde** os embeddings são produzidos (ver secção 3).

**Conclusão:** o comportamento da PoC **tem equivalente** no orquestrador: mesma entrada/saída conceitual (pergunta → lista de chunks ranqueados → contexto para o LLM).

---

## 2. Papel do orquestrador (NestJS) na arquitetura alvo

No desenho da Fase 3, o orquestrador continua como **middleware** entre canais, **Watson Assistant** (fluxos determinísticos) e integrações (Portal, etc.). O ramo **informativo com LLM + RAG** pode:

- ser acionado **apenas** quando o roteamento de negócio assim definir (ex.: intenção “dúvida aberta”);
- chamar um **serviço de retrieval** (interno ou externo) e depois o **gerador** (watsonx ou outro);
- manter **sessão, auditoria e políticas** no NestJS, independentemente da linguagem do motor de embeddings.

Ou seja: NestJS **orquestra**; não é obrigatório que o modelo de embedding rode **dentro** do mesmo processo Node — embora possa.

---

## 3. Onde gerar embeddings (opções para produção / orquestrador)

| Opção | Descrição | Notas |
|--------|-----------|--------|
| **A. Microsserviço (ex. Python)** | Manter um serviço HTTP com a lógica atual (`sentence-transformers` + corpus) exposta por API. O NestJS **chama** e recebe os `id` dos chunks + textos + scores. | Reutiliza a PoC com poucas mudanças; time precisa operar mais um serviço. |
| **B. Embeddings no Node** | Usar bibliotecas de inferência em JS/TS (ex.: **Transformers.js**, pacote `@xenova/transformers`) para carregar um modelo compatível e gerar vetores no próprio processo. | Menos serviços; validar CPU/RAM e modelo alinhado ao acervo. |
| **C. API de embeddings gerenciada** | IBM watsonx ou outro provedor com endpoint **embeddings**; o Nest envia textos e recebe vetores. | Sem servidor Python; custo, latência e **mesmo modelo** que o usado para indexar o corpus. |
| **D. Vector store** | Ingerir vetores no Pinecone, Weaviate, **pgvector**, OpenSearch kNN, etc.; a query envia só o embedding da pergunta e o **ranking** vem do motor. | Escala com corpus grande; operação de índice separada. |

Em todos os casos, o **ranking por score** continua sendo: **similaridade vetorial + ordenação** — igual à ideia do `retriever.py`, só que o “encode” pode ser outro runtime.

---

## 4. Contratos e consistência

- **Mesmo modelo de embedding** entre indexação do corpus e consulta em produção; caso contrário, scores e ordem não são comparáveis à PoC.
- **Formato do corpus** pode permanecer **JSON de chunks** (`id`, `source`, `text`, `theme`, …), compartilhado entre repositórios ou gerado por pipeline de conteúdo.
- **Top‑K** e prompts (`base`, instruções RAG) são **parâmetros de produto**, configuráveis por ambiente — como `RAG_TOP_K` na PoC.

---

## 5. Relação com os outros documentos deste repositório

| Documento | Conteúdo |
|-----------|----------|
| `docs/rag-pipeline.md` | Pipeline RAG da PoC (corpus, embeddings locais, top‑K). |
| `docs/montagem-do-prompt-llm.md` | Ordem do prompt enviado ao LLM. |
| `docs/pontuacao-chunks-e-embeddings.md` | O que é o score, tipo de tarefa (retrieval), modelo de embedding. |

---

## 6. Síntese

| Pergunta | Resposta |
|----------|----------|
| A PoC “só funciona em Python”? | **Não.** Python foi a escolha da PoC para `sentence-transformers`. A **lógica** é portável. |
| O orquestrador em NestJS consegue o mesmo efeito? | **Sim**, orquestrando retrieval + LLM e implementando ou chamando a parte de embeddings conforme uma das opções acima. |
| O que precisa ser decidido no projeto? | Onde rodam os embeddings (A–D), onde fica o corpus em produção e como versionar o modelo de embedding. |

Nada neste documento substitui o desenho de arquitetura aprovado pelo time; serve para **alinhar expectativa técnica** entre a PoC e o back-end Node.
