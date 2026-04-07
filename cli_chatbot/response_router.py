from cli_chatbot.calculadora import calcular_parcela
from cli_chatbot.watson_client import ask_watson


def gerar_resposta(pergunta: str, chat_history=None, debug: bool = False) -> dict:
    """
    Primeiro tenta responder com cálculo determinístico.
    Se não houver dados suficientes para cálculo, usa fallback para o LLM.
    """
    resposta_calculada = calcular_parcela(pergunta)
    if resposta_calculada:
        result = {
            "resposta": resposta_calculada,
            "source": "deterministic",
        }
        if debug:
            result["debug"] = {"router": "deterministic_calculator"}
        return result

    result = ask_watson(pergunta, chat_history=chat_history, debug=debug)
    result["source"] = "llm"
    return result

