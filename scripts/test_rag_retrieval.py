#!/usr/bin/env python3
"""
Testa só o retrieval sem chamar Watsonx (útil para validar corpus e dependências).
Uso (na raiz do projeto): python scripts/test_rag_retrieval.py

Requer: pip install sentence-transformers numpy
"""
import os
import sys

# Raiz do repo no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from cli_chatbot.rag.retriever import format_retrieved_for_prompt, retrieve_top_k


def main() -> None:
    q = " ".join(sys.argv[1:]) or "tenho duvida sobre financiamento"
    print(f"Query: {q!r}\n")
    retrieved = retrieve_top_k(q)
    if not retrieved:
        print("Nenhum chunk (corpus vazio ou sentence-transformers não instalado).")
        return
    for r in retrieved:
        print(f"--- {r['id']} score={r['score']:.4f} ---")
        print(r["text"][:200] + ("..." if len(r["text"]) > 200 else ""))
        print()
    print("=== Formato prompt ===\n")
    print(format_retrieved_for_prompt(retrieved))


if __name__ == "__main__":
    main()
