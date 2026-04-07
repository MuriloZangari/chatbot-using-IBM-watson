from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from cli_chatbot.persistence.mongo_client import get_database

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatRepository:
    """Grava atendimentos (sessões) e mensagens; compatível com fluxo determinístico + LLM."""

    def __init__(self, db) -> None:
        self._db = db
        self._sessions = db.chat_sessions
        self._messages = db.chat_messages

    def start_session(self, channel: str, user_id: str | None = None) -> str:
        session_id = str(uuid.uuid4())
        doc = {
            "_id": session_id,
            "session_id": session_id,
            "channel": channel,
            "status": "active",
            "user_id": user_id,
            "started_at": _utcnow(),
            "ended_at": None,
        }
        self._sessions.insert_one(doc)
        return session_id

    def end_session(self, session_id: str | None) -> None:
        if not session_id:
            return
        self._sessions.update_one(
            {"_id": session_id},
            {"$set": {"status": "ended", "ended_at": _utcnow()}},
        )

    def _next_turn(self, session_id: str) -> int:
        n = self._messages.count_documents({"session_id": session_id})
        return (n // 2) + 1

    def append_turn(
        self,
        session_id: str,
        user_content: str,
        assistant_content: str,
        source: str,
        assistant_metadata: dict[str, Any] | None = None,
        user_metadata: dict[str, Any] | None = None,
    ) -> None:
        turn = self._next_turn(session_id)
        base = {"session_id": session_id, "turn": turn, "created_at": _utcnow()}
        self._messages.insert_one(
            {
                **base,
                "role": "user",
                "content": user_content,
                "source": None,
                "metadata": user_metadata or {},
            }
        )
        self._messages.insert_one(
            {
                **base,
                "role": "assistant",
                "content": assistant_content,
                "source": source,
                "metadata": assistant_metadata or {},
            }
        )


def get_chat_repository() -> ChatRepository | None:
    db = get_database()
    if db is None:
        return None
    return ChatRepository(db)


def safe_append_turn(
    repo: ChatRepository | None,
    session_id: str | None,
    *,
    user_content: str,
    assistant_content: str,
    source: str,
    assistant_metadata: dict[str, Any] | None = None,
) -> None:
    if repo is None or not session_id:
        return
    try:
        repo.append_turn(
            session_id,
            user_content,
            assistant_content,
            source,
            assistant_metadata=assistant_metadata,
        )
    except Exception as e:
        logger.warning("Falha ao gravar turno no MongoDB: %s", e)
