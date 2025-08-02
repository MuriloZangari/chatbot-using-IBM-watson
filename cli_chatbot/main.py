from watson_client import ask_watson, valida_resposta
from chat_history import get_context

print("🤖 Chatbot de Financiamento de Veículos (Watsonx.ai)")
print("Digite 'sair' para encerrar.\n")

# 🔰 Carrega o contexto inicial da conversa
chat_history = get_context()

# (opcional) Mostra o contexto carregado na interface
print("🧠 Contexto inicial:")
for item in chat_history:
    print("-", item)
print("-" * 50)

while True:
    pergunta = input("Você: ")
    if pergunta.lower() in ['sair', 'exit']:
        break

    resposta = ask_watson(pergunta, chat_history=chat_history)
    print("Bot:", resposta['resposta'])

    print("-" * 50)

    # Atualiza o histórico de chat
    chat_history.append(f"Usuário: {pergunta}")
    chat_history.append(f"Assistente: {resposta['resposta']}")

    # Valida a resposta gerada
    alertas = valida_resposta(resposta['resposta'])
    if alertas:
        print("⚠️ Alertas:")
        for alerta in alertas:
            print(alerta)
