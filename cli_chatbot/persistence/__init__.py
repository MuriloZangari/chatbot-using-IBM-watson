"""Persistência de atendimentos (MongoDB / DocumentDB compatível)."""

from cli_chatbot.persistence.chat_repository import ChatRepository, get_chat_repository

__all__ = ["ChatRepository", "get_chat_repository"]
