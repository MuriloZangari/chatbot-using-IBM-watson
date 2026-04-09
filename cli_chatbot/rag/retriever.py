"""
Retrieval semântico simples (MVP RAG):
- Embeddings locais com sentence-transformers
- Similaridade coseno entre a pergunta e cada chunk
"""
from __future__ import annotations

import os
from typing import Any

import numpy as np

from cli_chatbot.rag.corpus_loader import load_all_corpus_json, load_corpus_json

_embedder = None
_chunks_by_file: dict[str, list[dict]] = {}

# Chave única para índice que concatena todos os JSON em knowledge/corpus/
_CORPUS_ALL_KEY = "__all__"


def is_rag_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _embedding_model_id() -> str:
    """ID Hugging Face do modelo; aceita atalho sem org (ex.: all-MiniLM-L6-v2)."""
    default = "sentence-transformers/all-MiniLM-L6-v2"
    raw = os.getenv("RAG_EMBEDDING_MODEL", default).strip()
    if not raw:
        return default
    if "/" not in raw:
        return f"sentence-transformers/{raw}"
    return raw


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(_embedding_model_id())
    return _embedder


def _cosine_sim_matrix(query_vec: np.ndarray, doc_matrix: np.ndarray) -> np.ndarray:
    """query_vec: (d,), doc_matrix: (n, d) -> scores (n,)"""
    qn = np.linalg.norm(query_vec)
    dn = np.linalg.norm(doc_matrix, axis=1)
    if qn == 0 or np.any(dn == 0):
        return np.zeros(doc_matrix.shape[0])
    return (doc_matrix @ query_vec) / (dn * qn)


def get_chunks(corpus_filename: str | None = None) -> list[dict]:
    """
    `corpus_filename=None` (padrão): carrega todos os *.json em knowledge/corpus/.
    Caso contrário, apenas o arquivo indicado (testes ou acervo isolado).
    """
    key = _CORPUS_ALL_KEY if corpus_filename is None else corpus_filename
    if key not in _chunks_by_file:
        if corpus_filename is None:
            _chunks_by_file[key] = load_all_corpus_json()
        else:
            _chunks_by_file[key] = load_corpus_json(corpus_filename)
    return _chunks_by_file[key]


def retrieve_top_k(
    query: str,
    top_k: int | None = None,
    *,
    corpus_filename: str | None = None,
) -> list[dict[str, Any]]:
    """
    Retorna os top_k chunks mais similares à query.

    Cada item retornado inclui: id, source, text, score (0 a 1 aprox.); opcional theme.
    Por padrão `corpus_filename=None` indexa todos os JSON em knowledge/corpus/.
    """
    if not query or not query.strip():
        return []

    # Padrão RAG_TOP_K (env, ex.: 6): com índice multi-tema, valores menores reduzem ruído.
    k = top_k if top_k is not None else int(os.getenv("RAG_TOP_K", "6"))
    chunks = get_chunks(corpus_filename)
    if not chunks:
        return []

    if not is_rag_available():
        return []

    texts = [c["text"] for c in chunks]
    embedder = _get_embedder()
    doc_emb = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    q_emb = embedder.encode([query.strip()], convert_to_numpy=True, show_progress_bar=False)[0]

    scores = _cosine_sim_matrix(q_emb, doc_emb)
    order = np.argsort(-scores)[:k]

    out: list[dict[str, Any]] = []
    for i in order:
        idx = int(i)
        c = chunks[idx].copy()
        c["score"] = float(scores[idx])
        out.append(c)

    # Se todos os chunks do acervo entraram no resultado e o tema é único, ordenar por `id`.
    # Com vários `theme` no mesmo índice, não reordenar — evita misturar narrativas distintas.
    if len(out) == len(chunks) and len(chunks) > 1:
        themes = {str(x.get("theme") or "") for x in out}
        if len(themes) <= 1:
            out.sort(key=lambda x: str(x.get("id", "")))

    return out


def format_retrieved_for_prompt(retrieved: list[dict]) -> str:
    """Formata trechos recuperados para injeção no prompt."""
    if not retrieved:
        return "(Nenhum trecho recuperado — acervo vazio ou retrieval indisponível.)"

    lines = []
    for i, r in enumerate(retrieved, 1):
        sid = r.get("id", "?")
        src = r.get("source", "")
        th = r.get("theme")
        score = r.get("score", 0)
        txt = r.get("text", "").strip()
        tema = f" tema={th}" if th else ""
        lines.append(f"[{i}] id={sid} fonte={src}{tema} relevância={score:.3f}\n{txt}")
    return "\n\n".join(lines)
