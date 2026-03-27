import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_ID = "mistralai/mistral-medium-2505"
DEFAULT_WATSONX_URL = "https://us-south.ml.cloud.ibm.com"

_model = None


class WatsonClientError(RuntimeError):
    def __init__(self, user_message: str, debug_details: str | None = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.debug_details = debug_details


def _get_watsonx_url() -> str:
    url = os.getenv("WATSONX_URL")
    if url:
        return url

    # Back-compat: if someone configured only the region
    region = os.getenv("WATSONX_REGION")
    if region:
        return f"https://{region}.ml.cloud.ibm.com"

    return DEFAULT_WATSONX_URL


def get_model_id() -> str:
    return os.getenv("WATSONX_MODEL_ID") or DEFAULT_MODEL_ID


def _get_project_id() -> str | None:
    return os.getenv("WATSONX_PROJECT_ID")


def _get_api_key() -> str | None:
    return os.getenv("WATSONX_API_KEY")


def get_model():
    """
    Inicializa o cliente do watsonx.ai sob demanda para evitar falhas no import.
    """
    global _model
    if _model is not None:
        return _model

    api_key = _get_api_key()
    project_id = _get_project_id()
    model_id = get_model_id()
    url = _get_watsonx_url()

    missing = []
    if not api_key:
        missing.append("WATSONX_API_KEY")
    if not project_id:
        missing.append("WATSONX_PROJECT_ID")
    if missing:
        raise WatsonClientError(
            "Credenciais do watsonx.ai não configuradas. "
            f"Defina no `.env`: {', '.join(missing)}.",
            debug_details=f"url={url!r} model_id={model_id!r}",
        )

    try:
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai import Credentials
    except Exception as e:  # pragma: no cover
        raise WatsonClientError(
            "Dependência do watsonx.ai não instalada. Rode `pip install -r requirements.txt`.",
            debug_details=repr(e),
        )

    creds = Credentials(url=url, api_key=api_key)
    _model = ModelInference(model_id=model_id, credentials=creds, project_id=project_id)
    return _model

def get_default_params():
    return {
        "decoding_method": "greedy",        # Obrigatório
        "max_new_tokens": 1000,             # Obrigatório
        "stop_sequences": ["Usuário:"],     # Recomendado

        # Parâmetros opcionais:
        "temperature": 0.2,                 # Menor temperatura = mais determinístico
        "repetition_penalty": 1.1           # Evita repetições excessivas
    }



def ask_watson(pergunta, chat_history=None, debug: bool = False):
    BASE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "base_prompt.txt")
    system_prompt = open(BASE_PROMPT_PATH, encoding="utf-8").read()

    # Junta o histórico da conversa, se houver
    history_text = "\n".join(chat_history) if chat_history else ""

    # Monta o prompt com contexto
    full_prompt = (
        f"{system_prompt}\n\n"
        f"{history_text}\n"
        f"Usuário: {pergunta}\n"
    )

    # Geração da resposta com parâmetros definidos
    params = get_default_params()
    try:
        response = get_model().generate(prompt=full_prompt, params=params)
    except WatsonClientError:
        raise
    except Exception as e:
        raise WatsonClientError(
            "Falha ao gerar resposta no watsonx.ai. Verifique suas credenciais/modelo e tente novamente.",
            debug_details=repr(e),
        )

    text = response['results'][0]['generated_text'].strip()  

    # print(response)  # Debug: mostra a resposta completa do modelo

    if "Usuário:" in text:
        # Remove a parte que simula o usuário
        text = text.split("Usuário:")[0].strip()

    result = {"resposta": text}
    if debug:
        result["debug"] = {
            "model_id": get_model_id(),
            "url": _get_watsonx_url(),
            "params": params,
            "prompt": full_prompt,
        }
    return result

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
