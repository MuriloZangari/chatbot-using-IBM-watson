# Pontuação dos chunks (score) — o que é, e o que não é

Este documento explica **como o “score” do retrieval é calculado** neste projeto, e como enquadrar isso em termos de aprendizado de máquina (sem confundir com classificação, agrupamento, etc.).

---

## O que o score representa

Para cada chunk do acervo, o código calcula a **similaridade coseno** entre:

- o **vetor da pergunta** (embedding da query), e  
- o **vetor do texto do chunk** (embedding do trecho).

O valor fica tipicamente entre **-1 e 1** (vetores normalizados na prática costumam ficar na faixa **0 a 1** para textos relacionados). **Não** é probabilidade nem “percentual de acerto”. **Não** existe limiar fixo de corte no código: entram no prompt os **K** melhores (`RAG_TOP_K`), ordenados do maior score para o menor.

Implementação: `cli_chatbot/rag/retriever.py` (`_cosine_sim_matrix`, `retrieve_top_k`).

---

## Estamos usando machine learning?

**Em parte, sim — mas só na etapa de transformar texto em vetor.**

- O **modelo de embeddings** (via `sentence-transformers`, por exemplo `sentence-transformers/all-MiniLM-L6-v2`) é uma rede neural **pré-treinada**: foi treinada com dados e objetivos definidos pelos autores (em geral, aprender representações que preservem **similaridade semântica** entre frases/parágrafos).
- **Neste repositório** não há treinamento nem fine-tuning: carregamos o modelo já pronto e usamos apenas **inferência** (encode da query e dos chunks).

Depois disso, o **ranking** é **determinístico**: matemática de produto interno e normas (similaridade coseno), sem outro modelo aprendendo em cima do score.

---

## Que “tipo de tarefa” é essa?

| Tarefa | Cabe aqui? | Motivo |
|--------|------------|--------|
| **Classificação** | Não (no sentido clássico) | Não há um conjunto fixo de classes nem um classificador que escolhe “rótulo A” ou “B”. O sistema **ranking** documentos por proximidade vetorial. |
| **Agrupamento (clustering)** | Não | Não estamos descobrindo grupos no corpus em tempo de execução; os chunks já existem e só são **ordenados** por relação com a pergunta. |
| **Regras de associação** | Não | Não é o tipo de “se A então B” sobre cestas de itens; é **busca por similaridade** texto–texto. |
| **Recuperação de informação / busca semântica** | **Sim** | É o enquadramento mais correto: dada uma **query**, recuperar os trechos **mais próximos** no espaço de embeddings (**vizinhos mais próximos** / **ranking por relevância**). |
| **Associação query–documento** | Em sentido amplo | Sim: associa-se a pergunta aos documentos mais relevantes em **espaço vetorial**, não por regras manuais. |

Em literatura de RAG e sistemas de busca densa, isso costuma ser chamado de **dense retrieval** ou **bi-encoder retrieval** (um encoder para a query, um para os passagens — aqui o mesmo encoder para ambos).

---

## Qual modelo de aprendizado é usado?

- **Biblioteca:** `sentence-transformers` (Hugging Face).
- **Modelo padrão neste projeto:** `sentence-transformers/all-MiniLM-L6-v2` (configurável por `RAG_EMBEDDING_MODEL`).
- **Arquitetura típica:** encoder tipo **Transformer** (base frequentemente derivada de BERT/MiniLM), treinado para produzir **embeddings de frase**; **dimensão** do vetor depende do checkpoint (ex.: 384 dimensões para esse modelo).
- **Treinamento original** (fora deste repo): em geral envolve **aprendizado contrastivo** ou similar (aproximar pares semânticos, afastar não relacionados). **Aqui** só usamos o peso já treinado.

O **LLM gerador** (ex.: Mistral no watsonx) é **outro** modelo: entra depois, para redigir a resposta a partir do prompt; não calcula o score dos chunks.

---

## Resumo em uma frase

> O **score** é **similaridade coseno** entre embeddings de texto; os embeddings vêm de um **modelo neural pré-treinado** (inferência); a **tarefa** é **recuperação semântica / ranking**, não classificação nem clustering.

---

## Ver também

- `docs/rag-pipeline.md` — pipeline RAG em alto nível  
- `docs/montagem-do-prompt-llm.md` — como os trechos entram no prompt do LLM  
- `docs/integracao-rag-orquestrador-nestjs.md` — mesma lógica no orquestrador (NestJS / Node)  
- `cli_chatbot/rag/retriever.py` — código do score e do top‑K  
