"""
Cliente mínimo Watson Assistant v2: uma sessão + várias mensagens (mesmo session_id).

Usado pelo script de teste e preparado para integração na PoC (Gradio / roteador).
"""
from __future__ import annotations

import os
from typing import Any


def require_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise OSError(f"Defina {name} no ambiente ou .env")
    return v


def build_assistant_v2():
    """Instância AssistantV2 autenticada (IAM + URL do .env)."""
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_watson import AssistantV2

    apikey = require_env("WATSON_ASSISTANT_APIKEY")
    url = require_env("WATSON_ASSISTANT_URL")
    version = os.getenv("WATSON_ASSISTANT_VERSION", "2021-06-14").strip() or "2021-06-14"

    authenticator = IAMAuthenticator(apikey)
    assistant = AssistantV2(version=version, authenticator=authenticator)
    assistant.set_service_url(url)
    return assistant


class WatsonAssistantConversation:
    """
    Mantém session_id entre turnos. O primeiro `send` cria sessão na API;
    os seguintes reutilizam o mesmo session_id (fluxo determinístico no Assistant).
    """

    def __init__(
        self,
        *,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self._client = build_assistant_v2()
        self._assistant_id = require_env("WATSON_ASSISTANT_ID")
        self._environment_id = require_env("WATSON_ASSISTANT_ENVIRONMENT_ID")
        self._session_id = session_id
        raw_uid = user_id if user_id is not None else os.getenv("WATSON_ASSISTANT_USER_ID", "poc-local-user")
        self._user_id = (raw_uid or "").strip() or "poc-local-user"

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def send(self, text: str) -> dict[str, Any]:
        if self._session_id is None:
            sess = self._client.create_session(
                assistant_id=self._assistant_id,
                environment_id=self._environment_id,
            ).get_result()
            self._session_id = sess["session_id"]

        return self._client.message(
            assistant_id=self._assistant_id,
            environment_id=self._environment_id,
            session_id=self._session_id,
            user_id=self._user_id,
            input={"message_type": "text", "text": text},
        ).get_result()
