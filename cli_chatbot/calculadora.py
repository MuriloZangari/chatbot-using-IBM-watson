import re

def _parse_number(raw: str) -> float:
    raw = raw.strip().replace("R$", "").replace(" ", "")
    if "," in raw and "." in raw:
        # Formato BR: 12.345,67
        if raw.rfind(",") > raw.rfind("."):
            normalized = raw.replace(".", "").replace(",", ".")
        else:
            # Formato EN: 12,345.67
            normalized = raw.replace(",", "")
    elif "," in raw:
        normalized = raw.replace(".", "").replace(",", ".")
    else:
        # Heurística simples para "50.000"
        parts = raw.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            normalized = "".join(parts)
        else:
            normalized = raw
    return float(normalized)


def _format_brl(valor: float) -> str:
    # 12,345.67 -> 12.345,67
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _extract_calculation_inputs(texto: str):
    valor_match = re.search(r"(?:financiar|financiamento)\s*(?:de)?\s*R?\$?\s*([\d\.,]+)", texto, re.IGNORECASE)
    parcelas_match = re.search(r"(\d+)\s*(?:x|vezes|parcelas|meses)", texto, re.IGNORECASE)
    taxa_match = re.search(r"([\d\.,]+)\s*%", texto, re.IGNORECASE)
    entrada_match = re.search(r"entrada\s*(?:de)?\s*R?\$?\s*([\d\.,]+)", texto, re.IGNORECASE)

    if not (valor_match and parcelas_match and taxa_match):
        return None

    valor_total = _parse_number(valor_match.group(1))
    parcelas = int(parcelas_match.group(1))
    taxa_mensal = _parse_number(taxa_match.group(1)) / 100.0
    entrada = _parse_number(entrada_match.group(1)) if entrada_match else 0.0

    valor_financiado = valor_total - entrada
    if parcelas <= 0 or valor_financiado <= 0:
        return None

    return valor_total, valor_financiado, entrada, parcelas, taxa_mensal


def calcular_parcela(texto: str):
    """
    Detecta dados de financiamento na pergunta e calcula a parcela de forma determinística.
    Retorna texto formatado em caso de sucesso; caso contrário, retorna None.
    """
    dados = _extract_calculation_inputs(texto)
    if not dados:
        return None

    valor_total, valor_financiado, entrada, parcelas, taxa_mensal = dados

    if taxa_mensal == 0:
        parcela = valor_financiado / parcelas
    else:
        # Fórmula Price: Parcela = (valor * taxa) / [1 - (1 + taxa)^-n]
        numerador = valor_financiado * taxa_mensal
        denominador = 1 - (1 + taxa_mensal) ** (-parcelas)
        parcela = numerador / denominador

    entrada_txt = f"Entrada: R$ {_format_brl(entrada)}\n" if entrada > 0 else ""
    return (
        "📊 **Cálculo determinístico (Python) aplicado:**\n\n"
        f"Valor do veículo: R$ {_format_brl(valor_total)}\n"
        f"{entrada_txt}"
        f"Valor financiado: R$ {_format_brl(valor_financiado)}\n"
        f"Parcelas: {parcelas} meses\n"
        f"Juros mensais: {taxa_mensal * 100:.2f}%\n\n"
        f"**Parcela estimada:** R$ {_format_brl(parcela)}\n\n"
        "📌 Fórmula: Parcela = (valor * taxa) / [1 - (1 + taxa)^-n]\n"
        "⚠️ Esta é uma estimativa. Confirme as taxas reais com sua instituição financeira."
    )
