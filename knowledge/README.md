# Acervo para RAG (PoC / estudo)

Convenções definidas **para o mini projeto** (não são “oficiais” de produto): objetivo é simular a fase 3 — perguntas abertas puxando texto alinhado ao chatbot determinístico atual.

## Arquivos em `corpus/`

| Arquivo | Conteúdo (origem fase 2) |
|---------|----------------------------|
| `financiamento_veiculos.json` | Um chunk (`fin_001`): texto completo de **Tirar dúvidas → Sobre financiamento** (mesma resposta do fluxo determinístico, um único vetor no índice). |
| `cobrancas_negativacao.json` | Dois chunks: **Tirar dúvidas → Cobranças** (comunicação após pagamento) e submenu **Negativações** (`cob_001`, `neg_001`). |
| `gravame.json` | Um chunk (`grav_001`): **Tirar dúvidas → Solicitações → Gravame** (DETRAN, SNG, CRV-e, recomendações, contatos). |

**Índice único:** o retrieval carrega **todos** os `*.json` desta pasta e concatena os chunks (ordem dos arquivos: nome do arquivo). Não é preciso alterar código ao adicionar um novo JSON.

## Um arquivo por tema ou um chunk por tema?

- **Um arquivo por família de menu / assunto** (como acima): facilita revisão, diff no Git e responsabilidade por arquivo.
- **Vários chunks por arquivo** quando o mesmo menu tem **subtemas com intenções diferentes** (ex.: “já paguei e recebi cobrança” vs. “negativado no Serasa”). O embedding encontra o trecho certo sem misturar tudo num único vetor gigante.
- **Um chunk único por resposta completa de um mesmo tema** — `financiamento_veiculos.json` usa um só chunk (`fin_001`) com todo o texto do menu “Sobre financiamento” (alinhado ao envio em blocos no WhatsApp, mas um vetor no índice).
- **Vários chunks no mesmo arquivo** — em `cobrancas_negativacao.json` há dois (`cob_001`, `neg_001`) porque são subtemas com intenções diferentes (comunicação pós-pagamento vs. negativação).

Campos por chunk (PoC):

- `id` — estável, prefixo por assunto (`fin_*`, `cob_*`, `neg_*`, `grav_*`).
- `source` — rótulo legível da origem no chatbot fase 2 (rastreio).
- `text` — texto fiel ao fluxo (sem o convite “escolha outra opção do menu” quando for só navegação).
- `theme` (opcional mas recomendado) — agrupa semanticamente (`financiamento`, `cobrancas_comunicacao`, `negativacao`). Usado para não reordenar narrativas distintas quando o índice inteiro entra no top‑k.

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `WATSON_AI_RAG` | `1` (padrão) liga RAG; `0` desliga e usa só o prompt base + histórico. |
| `RAG_TOP_K` | Trechos enviados ao prompt (padrão `6`). Com **vários temas** no índice, valores menores (ex.: `2`–`3`) reduzem ruído; o tamanho do índice cresce conforme novos `.json` em `corpus/`. |
| `RAG_EMBEDDING_MODEL` | Modelo Hugging Face para embeddings (padrão: `sentence-transformers/all-MiniLM-L6-v2`). Na primeira execução o modelo é baixado (~80 MB). |

## Como testar (exemplos de pergunta aberta)

Só retrieval, sem Watsonx: `python3 scripts/test_rag_retrieval.py "sua pergunta"`.

- Financiamento: `Tenho dúvida sobre financiamento` — deve priorizar `fin_001`.
- Cobrança após pagamento: `Já paguei o boleto mas recebi cobrança no WhatsApp` — deve priorizar `cob_001`.
- Negativação: `Meu nome está no Serasa por causa do financiamento` — deve priorizar `neg_001`.
- Gravame: `O que é gravame no financiamento do carro?` ou `Como funciona a baixa do gravame no DETRAN?` — deve priorizar `grav_001`.

Quando o retrieval devolve **todos** os chunks do **mesmo** `theme`, eles podem ser reordenados por `id` para preservar narrativa; com **vários** `theme` no resultado completo, essa reordenação global não é aplicada.
