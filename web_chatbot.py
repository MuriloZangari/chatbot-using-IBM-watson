import gradio as gr
from cli_chatbot.watson_client import ask_watson, valida_resposta
from cli_chatbot.chat_history import get_context

# Estado global da conversa (interno ao modelo)
chat_history = get_context()

def chatbot_interface(pergunta, history_ui):
    """
    Manipula a entrada do usuário, envia para o modelo Watsonx,
    valida a resposta e atualiza o histórico exibido na interface.
    """
    global chat_history

    # Chamada ao modelo
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
    Limpa apenas o histórico exibido na interface (não reseta o chat_history).
    """
    return []

def ver_contexto():
    """
    Mostra o conteúdo atual do contexto interno usado no modelo.
    """
    context = get_context()
    output = "\n".join(context)
    return [{"role": "assistant", "content": f"📄 Contexto inicial (mini-RAG):\n\n{output}"}]

# Interface Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 💬 Chatbot de Financiamento de Veículos (Watsonx.ai)")
    gr.Markdown("Digite sua pergunta sobre financiamento, parcelamento ou juros. Ex: `Quero financiar R$ 50.000 em 48x com 1,5% de juros ao mês.`")

    chatbot = gr.Chatbot(type="messages")

    with gr.Row():
        msg = gr.Textbox(placeholder="Digite sua pergunta aqui...", show_label=False)
        enviar = gr.Button("📨 Enviar")
        clear = gr.Button("🔄 Limpar conversa")
        contexto = gr.Button("📄 Ver contexto")

    # Enviar pergunta com Enter ou botão
    msg.submit(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])
    enviar.click(fn=chatbot_interface, inputs=[msg, chatbot], outputs=[msg, chatbot])

    # Limpar interface
    clear.click(fn=limpar_chat, outputs=[chatbot])

    # Ver contexto (mini-RAG)
    contexto.click(fn=ver_contexto, outputs=[chatbot])

# Executa servidor local e gera link público
if __name__ == "__main__":
    demo.launch(share=True)
