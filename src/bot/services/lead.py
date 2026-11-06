import html
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Lead:
    name: str
    phone: str
    comment: str | None = None


class MessageSender(Protocol):
    async def __call__(self, *, chat_id: int, text: str) -> object: ...


class LeadService:
    def __init__(self, sender: MessageSender, admin_chat_id: int) -> None:
        self._sender = sender
        self._admin_chat_id = admin_chat_id

    async def submit(self, lead: Lead) -> None:
        await self._sender(chat_id=self._admin_chat_id, text=self.format(lead))

    @staticmethod
    def format(lead: Lead) -> str:
        comment = html.escape(lead.comment) if lead.comment else "—"
        lines = [
            "<b>Новая заявка</b>",
            "",
            f"<b>Имя:</b> {html.escape(lead.name)}",
            f"<b>Телефон:</b> {html.escape(lead.phone)}",
            f"<b>Комментарий:</b> {comment}",
        ]
        return "\n".join(lines)
