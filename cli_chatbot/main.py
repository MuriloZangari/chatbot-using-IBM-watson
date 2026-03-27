from cli_chatbot.watson_client import ask_watson, valida_resposta

from cli_chatbot.chat_history import get_context
import argparse
from cli_chatbot.watson_client import WatsonClientError


def main() -> None:
    parser = argparse.ArgumentParser(description="Chatbot de financiamento de veículos (watsonx.ai)")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Exibe prompt/params e detalhes de erro para troubleshooting.",
    )
    args = parser.parse_args()

    print("🤖 Chatbot de Financiamento de Veículos (Watsonx.ai)")
    print("Digite 'sair' para encerrar.\n")

    # 🔰 Carrega o contexto inicial da conversa
    chat_history = get_context()

    while True:
        pergunta = input("Você: ")
        if pergunta.lower() in ["sair", "exit"]:
            break

        try:
            resposta = ask_watson(pergunta, chat_history=chat_history, debug=args.debug)
        except WatsonClientError as e:
            print(f"⚠️ {e.user_message}")
            if args.debug and e.debug_details:
                print("\n--- DEBUG ---")
                print(e.debug_details)
                print("-------------\n")
            continue

        if args.debug and "debug" in resposta:
            dbg = resposta["debug"]
            print("\n--- DEBUG ---")
            print(f"model_id: {dbg['model_id']}")
            print(f"url: {dbg['url']}")
            print(f"params: {dbg['params']}")
            print("\nPROMPT ENVIADO:\n")
            print(dbg["prompt"])
            print("-------------\n")

        print("Bot:", resposta["resposta"])

        print("-" * 50)

        # Atualiza o histórico de chat
        chat_history.append(f"Usuário: {pergunta}")
        chat_history.append(f"Assistente: {resposta['resposta']}")

        # Valida a resposta gerada
        alertas = valida_resposta(resposta["resposta"])
        if alertas:
            print("⚠️ Alertas:")
            for alerta in alertas:
                print(alerta)


if __name__ == "__main__":
    main()
