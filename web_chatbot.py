import gradio as gr
import os
from cli_chatbot.watson_client import WatsonClientError, get_model_id, valida_resposta
from cli_chatbot.chat_history import get_context
from cli_chatbot.response_router import gerar_resposta
from cli_chatbot.persistence.chat_repository import get_chat_repository, safe_append_turn

# Estado global da conversa (interno ao modelo)
chat_history = get_context()
# Sessão de atendimento (MongoDB); None até a primeira mensagem ou se persistência desligada
current_session_id = None

model_name = get_model_id().split("/")[-1]  # Extrai o nome do modelo para exibir na interface
WEB_DEBUG = os.getenv("WEB_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}

def chatbot_interface(pergunta, history_ui):
    """
    Manipula a entrada do usuário, envia para o modelo Watsonx,
    valida a resposta e atualiza o histórico exibido na interface.
    """
    global chat_history, current_session_id

    repo = get_chat_repository()
    if repo and current_session_id is None:
        try:
            current_session_id = repo.start_session("web")
            if WEB_DEBUG:
                print(f"[persistência] Nova sessão (atendimento): {current_session_id}")
        except Exception as ex:
            if WEB_DEBUG:
                print(f"[persistência] Falha ao iniciar sessão: {ex}")

    # Chamada ao modelo
    try:
        resposta = gerar_resposta(pergunta, chat_history=chat_history, debug=WEB_DEBUG)
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

    source = resposta.get("source", "unknown")
    source_label = "determinístico" if source == "deterministic" else "llm"
    if WEB_DEBUG:
        print(f"[WEB_DEBUG] source={source} pergunta={pergunta!r}")
        if "debug" in resposta:
            print(f"[WEB_DEBUG] debug={resposta['debug']}")

    # Atualiza histórico interno
    chat_history.append(f"Usuário: {pergunta}")
    chat_history.append(f"Assistente: {resposta['resposta']}")

    # Valida a resposta
    alertas = valida_resposta(resposta["resposta"]) if resposta.get("source") == "llm" else []
    if alertas:
        resposta['resposta'] += f"\n\n " + "\n".join(alertas)

    resposta_com_badge = f"🔎 Fonte: `{source_label}`\n\n{resposta['resposta']}"

    meta: dict = {}
    if source == "llm" and "debug" in resposta:
        d = resposta["debug"]
        meta = {"model_id": d.get("model_id"), "url": d.get("url")}
    elif source == "deterministic":
        meta = {"router": "deterministic_calculator"}
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
    """
    Limpa o histórico exibido na interface e reseta o chat_history interno
    para o contexto inicial (mini-RAG).
    """
    global chat_history, current_session_id
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
    chat_history = get_context()
    return []

def ver_contexto():
    """
    Mostra o conteúdo atual do contexto interno usado no modelo.
    """
    context = get_context()
    output = "\n".join(context)
    return [{"role": "assistant", "content": f"📄 Contexto inicial (mini-RAG):\n\n{output}"}]

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
    gr.Markdown("# 💬 Chatbot de Financiamento de Veículos (Watsonx.ai)")
    gr.Markdown("Digite sua pergunta sobre financiamento, parcelamento ou juros. Ex: `Quero financiar R$ 50.000 em 48x com 1,5% de juros ao mês. Qual seria o valor das parcelas se eu desse uma entrada de R$ 10.000?`")
    gr.Markdown(f"### Modelo: `{model_name}`")
    
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
        contexto = gr.Button("📄 Ver contexto")
        prompt_base = gr.Button("📄 Ver prompt-base")


    # Enviar pergunta com Enter ou botão
    msg.submit(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])
    enviar.click(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])

    # Limpar interface
    clear.click(fn=limpar_chat, outputs=[chatbot])

    # Ver contexto (mini-RAG)
    contexto.click(fn=ver_contexto, outputs=[chatbot])

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
