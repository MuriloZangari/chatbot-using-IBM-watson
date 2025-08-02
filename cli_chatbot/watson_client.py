import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

creds = Credentials(
    url="https://us-south.ml.cloud.ibm.com",  # Dallas Region
    api_key=API_KEY
)

model = ModelInference(
    model_id="ibm/granite-3-3-8b-instruct",
    credentials=creds,
    project_id=PROJECT_ID
)

def get_default_params():
    """
    Retorna os parâmetros de geração padrão compatíveis com o modelo Granite.
    Comentado para indicar quais são obrigatórios vs opcionais.

    Referência: IBM Watsonx.ai SDK (ModelInference.generate)
    """

    return {
        "decoding_method": "greedy",        # ✅ Obrigatório (greedy, sample ou beam)
        "max_new_tokens": 2000,              # ✅ Obrigatório (limite máximo de tokens gerados na resposta)

        "temperature": 0,                   # 🔹 Opcional (default = 1.0). Controla a aleatoriedade. 0 = determinístico
        "top_p": 1.0,                       # 🔹 Opcional (default = 1.0). Nucleus sampling — define a faixa de probabilidade acumulada
        "repetition_penalty": 1.0,          # 🔹 Opcional (default = 1.0). Penaliza repetições se > 1.0

        "stop_sequences": ["Usuário:"]       # 🔹 Opcional. Força o modelo a parar ao encontrar a sequência especificada
    }


def ask_watson(pergunta, chat_history=None):
    BASE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "base_prompt.txt")
    system_prompt = open(BASE_PROMPT_PATH, encoding="utf-8").read()

    # Junta o histórico da conversa, se houver
    history_text = "\n".join(chat_history) if chat_history else ""

    # Monta o prompt com contexto
    full_prompt = (
        f"{system_prompt}\n\n"
        f"{history_text}\n"
        f"Usuário: {pergunta}\n"
        f"Assistente:"
    )

    # Geração da resposta com os parâmetros padrão
    response = model.generate(
        prompt=full_prompt,
        params=get_default_params()
    )

    text = response['results'][0]['generated_text'].strip()    

    if "Usuário:" in text:
        # Remove a parte que simula o usuário
        text = text.split("Usuário:")[0].strip()

    return {
        "resposta": text
    }

def valida_resposta(texto):
    """
    Faz uma análise leve da resposta gerada pelo modelo para detectar possíveis alucinações ou inconsistências.
    Retorna uma lista de alertas, se houver.
    """
    alertas = []

    # Heurística 1: menção a leis, resoluções ou normas
    if any(term in texto.lower() for term in ["lei", "resolução", "norma", "constituição"]):
        alertas.append("⚠️ A resposta menciona normas legais. Verifique se a referência é verdadeira.")

    # Heurística 2: múltiplas moedas muito discrepantes
    if texto.count("R$") >= 2:
        try:
            valores = [float(v.replace("R$", "").replace(".", "").replace(",", "."))
                       for v in texto.split() if "R$" in v]
            if len(valores) >= 2:
                maior = max(valores)
                menor = min(valores)
                if menor > 0 and maior / menor > 10:
                    alertas.append("⚠️ O valor total parece desproporcional. Verifique os cálculos.")
        except Exception:
            pass

    # Heurística 3: simulação de turnos de conversa
    if "Usuário:" in texto:
        alertas.append("⚠️ O modelo está simulando falas do usuário. Isso deve ser evitado.")

    return alertas
