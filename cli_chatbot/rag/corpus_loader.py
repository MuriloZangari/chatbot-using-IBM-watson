import json
from pathlib import Path

_MERGED_CORPUS_CACHE: list[dict] | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def corpus_dir() -> Path:
    return _repo_root() / "knowledge" / "corpus"


def load_corpus_json(filename: str = "financiamento_veiculos.json") -> list[dict]:
    """
    Carrega chunks de um único arquivo em knowledge/corpus/{filename}.
    Cada item: { "id", "source", "text", opcional "theme" }.
    """
    path = corpus_dir() / filename
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict) and x.get("text", "").strip()]


def load_all_corpus_json() -> list[dict]:
    """
    Carrega e concatena todos os *.json em knowledge/corpus/ (ordem lexicográfica do nome).
    PoC: índice único para retrieval multi-tema; um arquivo por família de conteúdo.
    """
    global _MERGED_CORPUS_CACHE
    if _MERGED_CORPUS_CACHE is not None:
        return _MERGED_CORPUS_CACHE
    merged: list[dict] = []
    for path in sorted(corpus_dir().glob("*.json")):
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            continue
        merged.extend([x for x in data if isinstance(x, dict) and x.get("text", "").strip()])
    _MERGED_CORPUS_CACHE = merged
    return merged
