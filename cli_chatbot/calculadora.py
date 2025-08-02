import re

def calcular_parcela(texto):
    """
    Detecta se o texto possui dados suficientes para calcular a parcela
    e retorna a resposta formatada se possível.
    """
    # Regex para capturar os valores
    match = re.search(
        r"financiar\s*R?\$?\s*([\d\.]+)\s*(?:em)?\s*(\d+)\s*(?:vezes|x|parcelas|meses)[^\d]*([\d,\.]+)%", 
        texto, re.IGNORECASE
    )

    if not match:
        return None  # Não há dados suficientes

    try:
        valor = float(match.group(1).replace(".", "").replace(",", "."))
        parcelas = int(match.group(2))
        taxa_mensal = float(match.group(3).replace(",", ".")) / 100

        # Fórmula: Parcela = (valor * taxa) / [1 - (1 + taxa)^-n]
        numerador = valor * taxa_mensal
        denominador = 1 - (1 + taxa_mensal) ** -parcelas
        parcela = numerador / denominador

        return (
            f"📊 **Cálculo automático detectado:**\n\n"
            f"Valor financiado: R$ {valor:,.2f}\n"
            f"Parcelas: {parcelas} meses\n"
            f"Juros mensais: {taxa_mensal * 100:.2f}%\n\n"
            f"**Parcela estimada:** R$ {parcela:,.2f}\n\n"
            f"🧠 Cálculo realizado com precisão via Python.\n"
            f"📌 Fórmula: Parcela = (valor * taxa) / [1 - (1 + taxa)^-n]\n"
            f"⚠️ Esta é uma estimativa. Confirme as taxas reais com sua instituição financeira."
        )

    except Exception:
        return None
