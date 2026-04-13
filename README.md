# Watson AI Vehicle Financing Chatbot

A chatbot using IBM Watsonx.ai to answer natural language questions about vehicle financing, installment plans, and interest rates.

This project explores prompt engineering and integration with the IBM Watsonx.ai platform using the official Python SDK.
The chatbot supports both **terminal (CLI)** and **web interface (Gradio)** modes and uses **RAG** over a JSON corpus plus optional conversation history in the prompt.

---

## 🚀 Features

* ✅ Command-line chatbot interface (CLI)
* ✅ Web chatbot interface built with [Gradio](https://gradio.app/)
* ✅ Prompt-based interaction with IBM Foundation Models
* ✅ Integration via `ibm-watsonx-ai` SDK (no endpoint required)
* ✅ Token-based secure authentication via `.env`
* ✅ Custom model configuration: `temperature`, `stop_sequences`, `repetition_penalty`, etc.
* ✅ Contexto legal opcional em `chat_history.py` (seed fixo; desligável com `WATSON_AI_RAG_SKIP_SEED`)
* ✅ **RAG com retrieval semântico** (`knowledge/corpus`, `cli_chatbot/rag`, embeddings locais)
* ✅ Modular and extensible Python structure
* ✅ Fully local execution — no server setup required

---

## 📁 Project Structure

```bash
WATSON_AI/
├── cli_chatbot/
│   ├── main.py
│   ├── watson_client.py     # Watsonx + injeção RAG
│   ├── hybrid_router.py     # Assistant ↔ LLM+RAG (web)
│   ├── response_router.py   # Determinístico → LLM
│   ├── calculadora.py
│   └── rag/
│       ├── retriever.py
│       └── corpus_loader.py
├── knowledge/
│   ├── corpus/              # JSON chunks para RAG
│   └── README.md
├── prompts/
│   ├── base_prompt.txt
│   └── rag_instructions.txt
├── docs/
│   ├── rag-pipeline.md                    # Fluxo RAG (retrieval)
│   ├── montagem-do-prompt-llm.md          # O que entra no prompt a cada chamada ao LLM
│   ├── pontuacao-chunks-e-embeddings.md   # Score, embeddings, tipo de tarefa (ML)
│   ├── integracao-rag-orquestrador-nestjs.md  # PoC Python ↔ orquestrador TypeScript
│   ├── parametros-geracao-watsonx.md          # Greedy, temperature, stop_sequences, etc.
│   ├── watson-assistant-orchestrate-hibrido.md  # Assistant SDK vs Orchestrate vs PoC híbrida
│   ├── proposta-arquitetura-hibrida-poc.md      # Fluxo: actions + search + CTA (proposta)
│   ├── plano-de-acao-poc-hibrida.md             # Etapas 0–6: Assistant, SDK, consolidação
│   ├── guia-poc-watson-assistant-ui.md          # Checklist: primeiro fluxo no Assistant (UI)
│   └── roteamento-assistant-llm-poc.md          # Assistant ↔ LLM+RAG e retorno ao fluxo
├── scripts/
│   ├── test_rag_retrieval.py  # Testa retrieval sem Watsonx
│   └── test_watson_assistant_message.py  # Assistant API v2 (sessão multi-turn)
├── web_chatbot.py
├── .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-user/watson-ai-vehicle-financing-poc.git
cd watson-ai-vehicle-financing-poc
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Create a `.env` file in the root directory with your IBM Watsonx credentials:

```env
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
```

### Persistência de atendimentos (MongoDB / DocumentDB, opcional)

Se `MONGODB_URI` estiver definido, o app grava **sessões** (`chat_sessions`) e **mensagens** (`chat_messages`) por turno, com `source` = `deterministic`, `llm` ou `error` (fluxo híbrido).

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=watson_ai_chat
```

Sem `MONGODB_URI`, o chat funciona normalmente e nada é gravado.

No **MongoDB Compass**, conecte com a mesma URI e inspecione o database `MONGODB_DATABASE`.

---

## 💬 Run the Chatbot (CLI Mode)

```bash
cd cli_chatbot
python main.py
```

To exit, type `sair` or `exit`.

---

## 🌐 Run the Chatbot (Web Interface)

```bash
python web_chatbot.py
```

* Opens a Gradio interface in your browser.
* Set `share=True` to generate a public test link.
* Run this command from the repository root so the relative path `prompts/base_prompt.txt` resolves correctly.

---

## 🧠 Model Used

* **Model ID (current in code):** `mistralai/mistral-medium-2505`
* **Decoding:** `greedy`
* **Parameters:**

  * `max_new_tokens`
  * `temperature`
  * `stop_sequences`
  * `repetition_penalty`

---

## 📄 Histórico no prompt (LLM)

Turnos anteriores da sessão entram como texto no prompt do ramo LLM.

---

## 🔍 RAG (MVP — corpus + embeddings)

O projeto usa **retrieval semântico** sobre um acervo em JSON:

* **Corpus:** `knowledge/corpus/*.json` — vários arquivos (ex.: financiamento, cobranças/negativação); todos são fundidos num único índice. Detalhes em `knowledge/README.md`.
* **Embeddings locais:** `sentence-transformers` (modelo padrão `all-MiniLM-L6-v2`); similaridade coseno entre a pergunta e cada chunk.
* **Prompt:** `watson_client.ask_watson` injeta os top-k trechos (`RAG_TOP_K`, padrão **6**) + `prompts/rag_instructions.txt` antes do histórico e da pergunta. Com vários temas no índice, ajuste `RAG_TOP_K` se necessário.

**Variáveis de ambiente:**

| Variável | Significado |
|----------|-------------|
| `WATSON_AI_RAG` | `1` (padrão) liga RAG; `0` desliga. |
| `RAG_TOP_K` | Número de trechos recuperados (padrão `6`; ajuste se o índice crescer ou para reduzir ruído entre temas). |
| `RAG_EMBEDDING_MODEL` | Modelo Hugging Face para embeddings (opcional). |

Fluxo técnico: **`docs/rag-pipeline.md`** (retrieval). Montagem do prompt completo (base + RAG + histórico): **`docs/montagem-do-prompt-llm.md`**. Parâmetros de geração (watsonx): **`docs/parametros-geracao-watsonx.md`**.

**Testar só o retrieval (sem Watsonx):**

```bash
python3 scripts/test_rag_retrieval.py "tenho duvida sobre financiamento"
python3 scripts/test_rag_retrieval.py "estou negativado no serasa"
```

**Primeira execução:** o modelo de embeddings é baixado (~80 MB).

**Documentação do acervo:** `knowledge/README.md`

---

## 🖥️ Presentation

The PoC implementation and design decisions are documented in:

```
poc-presentation.md
```

Open in **[Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)** and export to PDF if needed.

---

## 👨‍💻 Author

**Murilo Zangari**
🌐 [murilozangari.com](https://murilozangari.com)
🔗 [LinkedIn](https://www.linkedin.com/in/murilozangari)
