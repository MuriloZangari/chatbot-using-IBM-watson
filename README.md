# Watson AI Vehicle Financing Chatbot

A chatbot using IBM Watsonx.ai to answer natural language questions about vehicle financing, installment plans, and interest rates.

This project explores prompt engineering and integration with the IBM Watsonx.ai platform using the official Python SDK.
The chatbot supports both **terminal (CLI)** and **web interface (Gradio)** modes and uses a custom prompt with embedded context ("mini-RAG") to reduce hallucinations.

---

## 🚀 Features

* ✅ Command-line chatbot interface (CLI)
* ✅ Web chatbot interface built with [Gradio](https://gradio.app/)
* ✅ Prompt-based interaction with IBM Foundation Models
* ✅ Integration via `ibm-watsonx-ai` SDK (no endpoint required)
* ✅ Token-based secure authentication via `.env`
* ✅ Custom model configuration: `temperature`, `stop_sequences`, `repetition_penalty`, etc.
* ✅ Lightweight "mini-RAG" technique to inject reliable legal context
* ✅ Modular and extensible Python structure
* ✅ Fully local execution — no server setup required

---

## 📁 Project Structure

```bash
WATSON_AI/
├── cli_chatbot/
│   ├── main.py              # CLI interface
│   ├── watson_client.py     # SDK integration with Watsonx
│   └── chat_context.py      # Mini-RAG contextual memory
├── prompts/
│   └── base_prompt.txt      # Prompt template
├── web_chatbot.py           # Web interface using Gradio
├── .env                     # API credentials (excluded from Git)
├── .gitignore
├── requirements.txt
├── README.md
└── poc-presentation.md      # Presentation slides (Marp format)
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

---

## 🧠 Model Used

* **Model ID:** `ibm/granite-3-3-8b-instruct`
* **Decoding:** `greedy`
* **Parameters:**

  * `max_new_tokens`
  * `temperature`
  * `stop_sequences`
  * `repetition_penalty`

---

## 📄 Mini-RAG Strategy

To avoid hallucinations and improve reliability, the chatbot uses a lightweight Retrieval-Augmented Generation (RAG) simulation:

* `chat_context.py` injects curated domain knowledge (e.g., legal financing rules).
* This context is prepended in every prompt sent to the model.
* The user can click **"📄 Ver contexto"** in the web interface to inspect it.

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
