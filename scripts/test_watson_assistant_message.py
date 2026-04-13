#!/usr/bin/env python3
"""
Testa Watson Assistant (API v2): sessão + uma ou várias mensagens no mesmo diálogo.

Uso (na raiz do projeto WATSON_AI):
  python scripts/test_watson_assistant_message.py --list-environments
  python scripts/test_watson_assistant_message.py "quero a segunda via do boleto"
  python scripts/test_watson_assistant_message.py --session-id <uuid> "Sim"
  python scripts/test_watson_assistant_message.py -i

Variáveis: ver `.env.example` (WATSON_ASSISTANT_*).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_chatbot.watson_assistant_client import (  # noqa: E402
    WatsonAssistantConversation,
    build_assistant_v2,
    require_env,
)


def _require(name: str) -> str:
    try:
        return require_env(name)
    except OSError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def _print_dns_connection_hint(exc: BaseException) -> None:
    chain = f"{exc!s} {getattr(exc, '__cause__', '')!s}".lower()
    if not any(
        s in chain
        for s in (
            "name resolution",
            "failed to resolve",
            "temporary failure",
            "iam.cloud.ibm.com",
            "assistant.watson.cloud.ibm.com",
        )
    ):
        return
    print(
        "\n[Dica] Falha de DNS ou rede. O SDK acessa:\n"
        "  - https://iam.cloud.ibm.com (token IAM)\n"
        "  - o host de WATSON_ASSISTANT_URL (ex.: api.au-syd.assistant.watson.cloud.ibm.com)\n"
        "Se `getent hosts iam.cloud.ibm.com` não devolver IP, corrija DNS/VPN/rede (ex.: WSL /etc/resolv.conf).\n",
        file=sys.stderr,
    )


def list_environments() -> None:
    assistant = build_assistant_v2()
    aid = _require("WATSON_ASSISTANT_ID")
    resp = assistant.list_environments(assistant_id=aid).get_result()
    envs = resp.get("environments", [])
    if not envs:
        print(json.dumps(resp, indent=2))
        return
    for e in envs:
        eid = e.get("environment_id") or e.get("id")
        name = e.get("name", "")
        print(f"{eid}\t{name}")


def _print_outputs(result: dict, *, show_intents: bool) -> None:
    out = result.get("output", {})
    generic = out.get("generic") or []
    for g in generic:
        rt = g.get("response_type")
        if rt == "text":
            t = g.get("text")
            if t:
                print(t)
        elif rt == "option":
            title = g.get("title") or ""
            opts = g.get("options") or []
            labels = [o.get("label", "") for o in opts]
            print(title)
            if labels:
                print("  " + " | ".join(labels))
        else:
            print(f"[{rt}] {json.dumps(g, ensure_ascii=False)[:500]}")

    if not show_intents:
        return
    intents = out.get("intents") or []
    if intents:
        print("\n--- intents (debug) ---")
        for it in intents[:5]:
            print(f"  {it.get('intent')}: {it.get('confidence')}")


def _print_session_hint(session_id: str | None) -> None:
    if not session_id:
        return
    print(
        f"\n[assistant] session_id={session_id}\n"
        f"  Continuar o mesmo fluxo: "
        f"python scripts/test_watson_assistant_message.py --session-id {session_id} \"<texto>\"\n",
        file=sys.stderr,
    )


def run_single_turn(
    user_text: str,
    *,
    session_id: str | None,
    show_intents: bool,
) -> None:
    conv = WatsonAssistantConversation(session_id=session_id)
    result = conv.send(user_text)
    _print_session_hint(conv.session_id)
    _print_outputs(result, show_intents=show_intents)


def run_interactive(
    *,
    initial_session_id: str | None,
    show_intents: bool,
) -> None:
    print(
        "Modo interativo. Digite mensagens (Sim, Não, …). "
        "Linha vazia ou 'exit' encerra.\n",
        file=sys.stderr,
    )
    conv = WatsonAssistantConversation(session_id=initial_session_id)
    if initial_session_id:
        print(f"[assistant] reutilizando session_id={initial_session_id}\n", file=sys.stderr)
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            break
        line = line.strip()
        if not line:
            break
        if line.lower() in ("exit", "quit", "q"):
            break
        result = conv.send(line)
        _print_outputs(result, show_intents=show_intents)
        _print_session_hint(conv.session_id)


def main() -> None:
    p = argparse.ArgumentParser(description="Teste Watson Assistant v2 (sessão + mensagem)")
    p.add_argument(
        "--list-environments",
        action="store_true",
        help="Lista environment_id / nome (preencha WATSON_ASSISTANT_ENVIRONMENT_ID no .env)",
    )
    p.add_argument(
        "--session-id",
        default=os.getenv("WATSON_ASSISTANT_SESSION_ID", "").strip() or None,
        help="Reutiliza sessão existente (ou defina WATSON_ASSISTANT_SESSION_ID)",
    )
    p.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Várias mensagens no mesmo diálogo (mesmo session_id)",
    )
    p.add_argument(
        "--no-debug-intents",
        action="store_true",
        help="Não imprime bloco --- intents (debug) ---",
    )
    p.add_argument("text", nargs="*", help="Mensagem do usuário para o Assistant")
    args = p.parse_args()

    show_intents = not args.no_debug_intents

    if args.list_environments:
        list_environments()
        return

    if args.interactive:
        run_interactive(initial_session_id=args.session_id, show_intents=show_intents)
        return

    user_text = " ".join(args.text).strip() or "quero a segunda via do boleto"
    run_single_turn(user_text, session_id=args.session_id, show_intents=show_intents)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError as e:
        _print_dns_connection_hint(e)
        raise
