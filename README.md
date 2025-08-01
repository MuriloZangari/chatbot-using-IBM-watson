# Watson AI Vehicle Financing Chatbot (PoC)

A simple proof-of-concept chatbot using IBM Watsonx.ai to answer natural language questions about vehicle financing, installment plans, and interest rates.

This project explores prompt engineering and integration with the IBM Watsonx.ai platform using the official Python SDK.  
The chatbot runs in a terminal (CLI) and uses a custom prompt to interact with the Granite Foundation Model, without the need to create an endpoint.

---

## 🚀 Features

- ✅ Command-line chatbot interface
- ✅ Prompt-based interaction with IBM Foundation Models
- ✅ Integration via `ibm-watsonx-ai` SDK (no endpoint required)
- ✅ Custom model configuration: `temperature`, `stop_sequences`, `repetition_penalty`, etc.
- ✅ Token-based secure authentication via `.env`
- ✅ Simple and extensible structure
- ✅ Runs entirely locally (no server)

---

## 📁 Project Structure

```bash
WATSON_AI/
├── cli_chatbot/
│   ├── main.py              # Entry point for CLI
│   └── watson_client.py     # SDK integration with Watsonx.ai
├── prompts/
│   └── base_prompt.txt      # System prompt template
├── .env                     # Environment variables (excluded from Git)
├── .gitignore
├── README.md
└── poc-presentation.md      # Markdown slides for presentation (Marp)
````

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-user/watson-ai-vehicle-financing-poc.git
cd watson-ai-vehicle-financing-poc
```

### 2. Create a virtual environment and activate it

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Create a `.env` file in the root directory with your IBM Cloud credentials:

```env
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
```

Do **not** commit this file — it is excluded via `.gitignore`.

---

## 💬 Running the chatbot

```bash
cd cli_chatbot
python main.py
```

Example:

```
Você: Quero financiar R$ 50.000 em 36x com 1,5% de juros. Quanto vou pagar por parcela?
Bot: [Resposta gerada com base no modelo Granite]
```

To exit, type `sair` or `exit`.

---

## 🧠 Model used

* Model: `ibm/granite-3-3-8b-instruct`
* Decoding: `greedy`
* Params: `max_new_tokens`, `temperature`, `stop_sequences`, `repetition_penalty`

---

## 🖥️ Presentation

Slides with technical decisions and implementation details are available in:

```
poc-presentation.md
```

This file is compatible with **[Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)** — open it and export to PDF.

---

## 👨‍💻 Author

**Murilo Zangari**
🌐 [murilozangari.com](https://murilozangari.com)
🔗 [LinkedIn](https://www.linkedin.com/in/murilozangari)

---