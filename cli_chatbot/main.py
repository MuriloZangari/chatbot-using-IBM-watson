from watson_client import ask_watson

print("🤖 Chatbot de Financiamento de Veículos (Watsonx.ai)")
print("Digite 'sair' para encerrar.\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() in ['sair', 'exit']:
        break

    resposta = ask_watson(pergunta)
    print("Bot:", resposta)
