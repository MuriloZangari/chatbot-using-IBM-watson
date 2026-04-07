import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Carrega .env da raiz do repositório (não depende do CWD nem da ordem de imports).
_root = Path(__file__).resolve().parents[2]
load_dotenv(_root / ".env")

_client = None
_db: Any = None
_logger = logging.getLogger(__name__)


def is_mongodb_configured() -> bool:
    return bool(os.getenv("MONGODB_URI", "").strip())


def get_database():
    """
    Retorna o database MongoDB ou None se URI não configurada / falha de conexão.
    """
    global _client, _db
    if not is_mongodb_configured():
        return None
    if _db is not None:
        return _db
    try:
        from pymongo import MongoClient
    except ImportError:
        _logger.warning(
            "Persistência MongoDB desativada: instale com `pip install pymongo`."
        )
        return None
    uri = os.getenv("MONGODB_URI", "").strip()
    name = os.getenv("MONGODB_DATABASE", "watson_ai_chat").strip() or "watson_ai_chat"
    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client[name]
        _ensure_indexes(_db)
        _logger.info("MongoDB conectado: db=%s uri=%s", name, uri.split("@")[-1] if "@" in uri else uri)
    except Exception as e:
        _client = None
        _db = None
        _logger.warning(
            "MongoDB indisponível (persistência desativada): %s. URI=%s db=%s",
            e,
            uri[:80] + ("..." if len(uri) > 80 else ""),
            name,
        )
    return _db


def _ensure_indexes(db) -> None:
    try:
        db.chat_sessions.create_index("started_at")
        db.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
        db.chat_messages.create_index("session_id")
    except Exception:
        pass
