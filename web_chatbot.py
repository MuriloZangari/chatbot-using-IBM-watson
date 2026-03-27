import gradio as gr
from cli_chatbot.watson_client import WatsonClientError, ask_watson, get_model_id, valida_resposta
from cli_chatbot.chat_history import get_context

# Estado global da conversa (interno ao modelo)
chat_history = get_context()

model_name = get_model_id().split("/")[-1]  # Extrai o nome do modelo para exibir na interface

def chatbot_interface(pergunta, history_ui):
    """
    Manipula a entrada do usuário, envia para o modelo Watsonx,
    valida a resposta e atualiza o histórico exibido na interface.
    """
    global chat_history

    # Chamada ao modelo
    try:
        resposta = ask_watson(pergunta, chat_history)
    except WatsonClientError as e:
        history_ui.append({"role": "user", "content": pergunta})
        history_ui.append({"role": "assistant", "content": f"⚠️ {e.user_message}"})
        return "", history_ui

    # Atualiza histórico interno
    chat_history.append(f"Usuário: {pergunta}")
    chat_history.append(f"Assistente: {resposta['resposta']}")

    # Valida a resposta
    alertas = valida_resposta(resposta['resposta'])
    if alertas:
        resposta['resposta'] += f"\n\n " + "\n".join(alertas)

    # Atualiza histórico da interface Gradio
    history_ui.append({"role": "user", "content": pergunta})
    history_ui.append({"role": "assistant", "content": resposta['resposta']})

    return "", history_ui

def limpar_chat():
    """
    Limpa o histórico exibido na interface e reseta o chat_history interno
    para o contexto inicial (mini-RAG).
    """
    global chat_history
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
    
    chatbot = gr.Chatbot(type="messages")

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
    demo.launch(share=True)
