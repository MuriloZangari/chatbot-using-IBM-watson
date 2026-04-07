import argparse
from cli_chatbot.watson_client import WatsonClientError
from cli_chatbot.watson_client import valida_resposta
from cli_chatbot.chat_history import get_context
from cli_chatbot.response_router import gerar_resposta
from cli_chatbot.persistence.chat_repository import get_chat_repository, safe_append_turn


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

    repo = get_chat_repository()
    session_id = repo.start_session("cli") if repo else None
    if args.debug and session_id:
        print(f"[persistência] Sessão (atendimento): {session_id}\n")

    try:
        while True:
            pergunta = input("Você: ")
            if pergunta.lower() in ["sair", "exit"]:
                break

            try:
                resposta = gerar_resposta(pergunta, chat_history=chat_history, debug=args.debug)
            except WatsonClientError as e:
                print(f"⚠️ {e.user_message}")
                if args.debug and e.debug_details:
                    print("\n--- DEBUG ---")
                    print(e.debug_details)
                    print("-------------\n")
                safe_append_turn(
                    repo,
                    session_id,
                    user_content=pergunta,
                    assistant_content=f"⚠️ {e.user_message}",
                    source="error",
                    assistant_metadata={"debug_details": e.debug_details} if e.debug_details else None,
                )
                continue

            if args.debug and "debug" in resposta and resposta.get("source") == "llm":
                dbg = resposta["debug"]
                print("\n--- DEBUG ---")
                print(f"model_id: {dbg['model_id']}")
                print(f"url: {dbg['url']}")
                print(f"params: {dbg['params']}")
                print("\nPROMPT ENVIADO:\n")
                print(dbg["prompt"])
                print("-------------\n")
            elif args.debug and resposta.get("source") == "deterministic":
                print("\n--- DEBUG ---")
                print("source: deterministic_calculator")
                print("-------------\n")

            print("Bot:", resposta["resposta"])

            print("-" * 50)

            # Atualiza o histórico de chat
            chat_history.append(f"Usuário: {pergunta}")
            chat_history.append(f"Assistente: {resposta['resposta']}")

            # Valida a resposta gerada
            alertas = valida_resposta(resposta["resposta"]) if resposta.get("source") == "llm" else []
            if alertas:
                print("⚠️ Alertas:")
                for alerta in alertas:
                    print(alerta)

            source = resposta.get("source", "llm")
            texto_gravar = resposta["resposta"]
            if alertas:
                texto_gravar = texto_gravar + "\n\n" + "\n".join(alertas)
            meta = {}
            if source == "llm" and "debug" in resposta:
                d = resposta["debug"]
                meta = {"model_id": d.get("model_id"), "url": d.get("url")}
            elif source == "deterministic":
                meta = {"router": "deterministic_calculator"}
            safe_append_turn(
                repo,
                session_id,
                user_content=pergunta,
                assistant_content=texto_gravar,
                source=source,
                assistant_metadata=meta or None,
            )
    finally:
        if repo and session_id:
            try:
                repo.end_session(session_id)
                if args.debug:
                    print(f"\n[persistência] Sessão encerrada: {session_id}")
            except Exception:
                pass


if __name__ == "__main__":
    main()
