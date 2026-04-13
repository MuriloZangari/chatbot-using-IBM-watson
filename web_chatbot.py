import gradio as gr
import os
from cli_chatbot.watson_client import WatsonClientError, get_model_id, valida_resposta
from cli_chatbot.hybrid_router import gerar_resposta_roteada
from cli_chatbot.persistence.chat_repository import get_chat_repository, safe_append_turn

# Histórico em texto para o ramo LLM (turnos anteriores); sem seed fixo.
chat_history: list[str] = []
# Sessão de atendimento (MongoDB); None até a primeira mensagem ou se persistência desligada
current_session_id = None
# Watson Assistant: mesma conversa API entre mensagens (session_id interno da IBM)
wa_assistant_conv = None

model_name = get_model_id().split("/")[-1]  # Extrai o nome do modelo para exibir na interface
WEB_DEBUG = os.getenv("WEB_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}

def chatbot_interface(pergunta, history_ui, modo):
    """
    Roteia por `modo`: Watson Assistant (fluxos) ou LLM+RAG (watsonx).
    """
    global chat_history, current_session_id, wa_assistant_conv

    repo = get_chat_repository()
    if repo and current_session_id is None:
        try:
            current_session_id = repo.start_session("web")
            if WEB_DEBUG:
                print(f"[persistência] Nova sessão (atendimento): {current_session_id}")
        except Exception as ex:
            if WEB_DEBUG:
                print(f"[persistência] Falha ao iniciar sessão: {ex}")

    try:
        resposta, wa_assistant_conv = gerar_resposta_roteada(
            pergunta,
            modo=modo,
            wa_conv=wa_assistant_conv,
            chat_history=chat_history,
            debug=WEB_DEBUG,
        )
    except WatsonClientError as e:
        history_ui.append({"role": "user", "content": pergunta})
        history_ui.append({"role": "assistant", "content": f"⚠️ {e.user_message}"})
        if WEB_DEBUG:
            print(f"[WEB_DEBUG] source=error pergunta={pergunta!r} erro={e.user_message}")
            if e.debug_details:
                print(f"[WEB_DEBUG] error_details={e.debug_details}")
        safe_append_turn(
            repo,
            current_session_id,
            user_content=pergunta,
            assistant_content=f"⚠️ {e.user_message}",
            source="error",
            assistant_metadata={"debug_details": e.debug_details} if e.debug_details else None,
        )
        return "", history_ui

    if resposta.get("source") == "error":
        history_ui.append({"role": "user", "content": pergunta})
        history_ui.append({"role": "assistant", "content": f"⚠️ {resposta['resposta']}"})
        safe_append_turn(
            repo,
            current_session_id,
            user_content=pergunta,
            assistant_content=f"⚠️ {resposta['resposta']}",
            source="error",
            assistant_metadata=None,
        )
        return "", history_ui

    source = resposta.get("source", "unknown")
    if source == "deterministic":
        source_label = "determinístico"
    elif source == "llm":
        source_label = "llm"
    elif source == "assistant":
        source_label = "watson assistant"
    else:
        source_label = str(source)
    if WEB_DEBUG:
        print(f"[WEB_DEBUG] source={source} modo={modo!r} pergunta={pergunta!r}")
        if "debug" in resposta:
            print(f"[WEB_DEBUG] debug={resposta['debug']}")
        if resposta.get("rag"):
            print(f"[WEB_DEBUG] rag={resposta['rag']}")

    # Atualiza histórico interno
    chat_history.append(f"Usuário: {pergunta}")
    chat_history.append(f"Assistente: {resposta['resposta']}")

    # Valida a resposta
    alertas = valida_resposta(resposta["resposta"]) if resposta.get("source") == "llm" else []
    if alertas:
        resposta['resposta'] += f"\n\n " + "\n".join(alertas)

    resposta_com_badge = f"🔎 Fonte: `{source_label}`\n\n{resposta['resposta']}"

    # Intents do Watson Assistant (debug), alinhado ao script CLI
    if source == "assistant" and resposta.get("wa_intents"):
        intent_lines = []
        for it in resposta["wa_intents"]:
            conf = it.get("confidence")
            conf_s = str(conf) if conf is not None else "—"
            intent_lines.append(f"  • `{it.get('intent', '?')}`: {conf_s}")
        resposta_com_badge += "\n\n---\n**Intents (debug):**\n" + "\n".join(intent_lines)

    # Trechos recuperados pelo RAG (apenas ramo LLM), para aprendizado / auditoria
    if source == "llm" and resposta.get("rag") and resposta["rag"].get("chunks"):
        rag_lines = []
        for c in resposta["rag"]["chunks"]:
            th = c.get("theme")
            tema = f" — `{th}`" if th else ""
            rag_lines.append(
                f"  • `{c.get('id', '?')}` — score {float(c.get('score', 0)):.3f}{tema} — `{c.get('source', '')}`"
            )
        resposta_com_badge += "\n\n---\n**Trechos RAG enviados ao modelo:**\n" + "\n".join(rag_lines)

    meta: dict = {}
    if source == "llm":
        if "debug" in resposta:
            d = resposta["debug"]
            meta = {"model_id": d.get("model_id"), "url": d.get("url")}
        if resposta.get("rag"):
            meta = {**meta, "rag": resposta["rag"]}
    elif source == "deterministic":
        meta = {"router": "deterministic_calculator"}
    elif source == "assistant":
        meta = {
            "wa_session_id": resposta.get("wa_session_id"),
            "wa_intents": resposta.get("wa_intents"),
        }
    safe_append_turn(
        repo,
        current_session_id,
        user_content=pergunta,
        assistant_content=resposta_com_badge,
        source=source,
        assistant_metadata=meta or None,
    )

    # Atualiza histórico da interface Gradio
    history_ui.append({"role": "user", "content": pergunta})
    history_ui.append({"role": "assistant", "content": resposta_com_badge})

    return "", history_ui

def limpar_chat():
    """Limpa o histórico exibido e o histórico interno usado no prompt do LLM."""
    global chat_history, current_session_id, wa_assistant_conv
    repo = get_chat_repository()
    if repo and current_session_id:
        try:
            repo.end_session(current_session_id)
            if WEB_DEBUG:
                print(f"[persistência] Sessão encerrada: {current_session_id}")
        except Exception as ex:
            if WEB_DEBUG:
                print(f"[persistência] Falha ao encerrar sessão: {ex}")
    current_session_id = None
    wa_assistant_conv = None
    chat_history = []
    return []

def ver_prompt_base():
    """
    Lê e exibe o conteúdo do prompt base como mensagem do assistente.
    """
    try:
        with open("prompts/base_prompt.txt", "r") as f:
            prompt_text = f.read()
    except FileNotFoundError:
        prompt_text = "⚠️ Arquivo 'base_prompt.txt' não encontrado."

    return [{"role": "assistant", "content": f"📄 **Prompt-base usado no modelo:**\n\n{prompt_text}"}]


# Interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 💬 PoC — Watson Assistant + watsonx (LLM/RAG)")
    gr.Markdown(
        "**Assistente:** fluxos modelados no Watson Assistant (menus, segunda via, etc.). "
        "**Acervo:** perguntas abertas com RAG + watsonx (calculadora continua no ramo Acervo quando aplicável)."
    )
    gr.Markdown(f"### Modelo watsonx (ramo Acervo): `{model_name}`")

    modo = gr.Radio(
        choices=[
            ("Assistente — fluxos (Watson Assistant)", "assistant"),
            ("Acervo — LLM + RAG (watsonx)", "llm_rag"),
        ],
        value="assistant",
        label="Onde enviar a próxima mensagem",
    )

    chatbot = gr.Chatbot(type="messages", height=650)

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Digite sua pergunta aqui...",
            show_label=False,
            scale=8  # ocupa 80% da largura
        )
        enviar = gr.Button("📨 Enviar", scale=2)

    with gr.Row():
        clear = gr.Button("🔄 Limpar conversa")
        prompt_base = gr.Button("📄 Ver prompt-base")


    # Enviar pergunta com Enter ou botão
    msg.submit(fn=chatbot_interface, inputs=[msg, chatbot, modo], outputs=[msg, chatbot])
    enviar.click(fn=chatbot_interface, inputs=[msg, chatbot, modo], outputs=[msg, chatbot])

    # Limpar interface
    clear.click(fn=limpar_chat, outputs=[chatbot])

    # Ver prompt-base
    prompt_base.click(fn=ver_prompt_base, outputs=[chatbot])

# Executa servidor local e gera link público
if __name__ == "__main__":
    if WEB_DEBUG:
        print("[WEB_DEBUG] Modo debug web ativo (WEB_DEBUG=true).")
    from cli_chatbot.persistence.mongo_client import get_database, is_mongodb_configured

    db_name = os.getenv("MONGODB_DATABASE", "watson_ai_chat").strip() or "watson_ai_chat"
    if is_mongodb_configured():
        _db = get_database()
        if _db is not None:
            print(f"✓ Persistência MongoDB ativa (database: {db_name}).")
        else:
            print(
                "⚠️ MONGODB_URI está no .env, mas a conexão falhou. "
                "Nada será gravado; veja o aviso do Python acima (logging)."
            )
    else:
        print(
            "ℹ Persistência MongoDB desligada: defina MONGODB_URI no arquivo .env na raiz do projeto."
        )
    demo.launch(share=True)
