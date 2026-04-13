"""
Roteamento opção B: Watson Assistant (fluxos) ou LLM + RAG (watsonx), na mesma PoC.

O modo é escolhido na interface (Gradio); não depende de variáveis no Assistant.
"""
from __future__ import annotations

import json
from typing import Any, Literal

from cli_chatbot.response_router import gerar_resposta
from cli_chatbot.watson_assistant_client import WatsonAssistantConversation

ModoCanal = Literal["assistant", "llm_rag"]


def format_assistant_output(result: dict[str, Any]) -> str:
    """Converte `output.generic` da API v2 em texto legível para o chat."""
    lines: list[str] = []
    out = result.get("output", {})
    generic = out.get("generic") or []
    for g in generic:
        rt = g.get("response_type")
        if rt == "text":
            t = g.get("text")
            if t:
                lines.append(t)
        elif rt == "option":
            title = g.get("title") or ""
            opts = g.get("options") or []
            labels = [o.get("label", "") for o in opts if o.get("label")]
            block = []
            if title:
                block.append(title)
            if labels:
                block.append("  " + " | ".join(labels))
            if block:
                lines.append("\n".join(block))
        else:
            snippet = json.dumps(g, ensure_ascii=False)[:400]
            lines.append(f"[{rt}] {snippet}")

    return "\n\n".join(lines) if lines else "(Resposta do Assistant sem texto exibível.)"


def extract_assistant_intents(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Intents do turno (API v2: output.intents)."""
    intents = (raw.get("output") or {}).get("intents") or []
    out: list[dict[str, Any]] = []
    for it in intents[:15]:
        name = it.get("intent")
        if name is None:
            continue
        conf = it.get("confidence")
        out.append({"intent": name, "confidence": float(conf) if conf is not None else None})
    return out


def gerar_resposta_roteada(
    pergunta: str,
    *,
    modo: ModoCanal,
    wa_conv: WatsonAssistantConversation | None,
    chat_history: list | None,
    debug: bool = False,
) -> tuple[dict[str, Any], WatsonAssistantConversation | None]:
    """
    Retorna (resultado no mesmo formato esperado pelo web_chatbot, conversa WA atualizada).

    resultado usa chaves: resposta, source em {"deterministic","llm","assistant","error"}
    """
    if modo == "llm_rag":
        r = gerar_resposta(pergunta, chat_history=chat_history, debug=debug)
        return r, wa_conv

    if modo == "assistant":
        try:
            conv = wa_conv or WatsonAssistantConversation()
        except OSError as e:
            return (
                {
                    "resposta": (
                        f"Configuração do Watson Assistant incompleta: {e}\n"
                        "Preencha WATSON_ASSISTANT_* no .env (veja .env.example)."
                    ),
                    "source": "error",
                },
                wa_conv,
            )
        try:
            raw = conv.send(pergunta)
        except Exception as e:
            msg = str(e)
            if debug:
                msg = f"{type(e).__name__}: {msg}"
            return (
                {
                    "resposta": f"Erro ao chamar Watson Assistant: {msg}",
                    "source": "error",
                },
                wa_conv,
            )
        text = format_assistant_output(raw)
        wa_intents = extract_assistant_intents(raw)
        out: dict[str, Any] = {
            "resposta": text,
            "source": "assistant",
            "wa_session_id": conv.session_id,
            "wa_intents": wa_intents,
        }
        if debug:
            out["debug"] = {
                "wa_session_id": conv.session_id,
                "router": "watson_assistant_v2",
                "wa_intents": wa_intents,
            }
        return out, conv

    return (
        {"resposta": f"Modo desconhecido: {modo!r}", "source": "error"},
        wa_conv,
    )
