import os


def get_context():
    """
    Contexto inicial injetado no prompt (simulação de turno fixo), separado do RAG por arquivo.

    Para testar **apenas** retrieval + LLM (sem este seed), defina no `.env`:
    `WATSON_AI_RAG_SKIP_SEED=1`
    """
    if os.getenv("WATSON_AI_RAG_SKIP_SEED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return []

    return [
        "Usuário: Contexto sobre prazo legal para financiamento de veículos",
        "Assistente: Segundo o Banco Central do Brasil e a Resolução CMN nº 4.744/2019, o prazo máximo para financiamento de veículos é determinado pelas instituições financeiras, respeitando critérios internos de risco. É comum encontrar prazos de até 60 ou 72 meses (5 a 6 anos) para veículos novos. Não existe uma lei federal que fixe esse prazo. As condições variam conforme perfil do cliente, tipo de financiamento e política do banco.",
    ]