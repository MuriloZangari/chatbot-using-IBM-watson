import gradio as gr
from cli_chatbot.watson_client import ask_watson, valida_resposta
from cli_chatbot.chat_history import get_context

# Estado global da conversa
chat_history = get_context()

def chatbot_interface(pergunta, history_ui):
    """
    Manipula a entrada do usuário, envia para o modelo Watsonx,
    valida a resposta e atualiza o histórico exibido na interface.
    """
    global chat_history

    resposta = ask_watson(pergunta, chat_history)

    # Atualiza histórico interno
    chat_history.append(f"Usuário: {pergunta}")
    chat_history.append(f"Assistente: {resposta['resposta']}")

    # Valida a resposta
    alertas = valida_resposta(resposta['resposta'])
    if alertas:
        resposta['resposta'] += f"\n\n⚠️ " + "\n".join(alertas)

    # Atualiza histórico da interface Gradio
    history_ui.append({"role": "user", "content": pergunta})
    history_ui.append({"role": "assistant", "content": resposta['resposta']})

    return "", history_ui

def limpar_chat():
    """
    Reseta a interface e o histórico da conversa com contexto inicial.
    """
    global chat_history
    chat_history = get_context()

    # Converte o contexto interno em formato para o Chatbot (role/content)
    history_ui = []
    for i in range(0, len(chat_history), 2):
        if i + 1 < len(chat_history):
            history_ui.append({"role": "user", "content": chat_history[i].replace("Usuário: ", "")})
            history_ui.append({"role": "assistant", "content": chat_history[i+1].replace("Assistente: ", "")})
    return history_ui

# Interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 💬 Chatbot de Financiamento de Veículos (Watsonx.ai)")
    gr.Markdown("Digite sua pergunta sobre financiamento, parcelamento ou juros. Ex: `Quero financiar R$ 50.000 em 48x com 1,5% de juros ao mês.`")

    chatbot = gr.Chatbot(type="messages")
    with gr.Row():
        msg = gr.Textbox(placeholder="Digite sua pergunta aqui...", show_label=False)
        send = gr.Button("📤 Enviar")
        clear = gr.Button("🔄 Limpar conversa")

    # Aciona com Enter
    msg.submit(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])
    # Aciona com botão "Enviar"
    send.click(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])
    # Botão "Limpar conversa"
    clear.click(fn=limpar_chat, outputs=[chatbot])

# Executa servidor local
if __name__ == "__main__":
    demo.launch(share=True)
