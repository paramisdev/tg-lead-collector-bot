from bot.services.lead import Lead, LeadService


class FakeSender:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    async def __call__(self, *, chat_id: int, text: str) -> object:
        self.calls.append((chat_id, text))
        return object()


async def test_submit_sends_lead_to_admin() -> None:
    sender = FakeSender()
    service = LeadService(sender=sender, admin_chat_id=42)

    await service.submit(Lead(name="Иван", phone="+79991234567", comment="Нужен сайт"))

    assert len(sender.calls) == 1
    chat_id, text = sender.calls[0]
    assert chat_id == 42
    assert "Иван" in text
    assert "+79991234567" in text
    assert "Нужен сайт" in text


async def test_submit_escapes_html() -> None:
    sender = FakeSender()
    service = LeadService(sender=sender, admin_chat_id=42)

    await service.submit(Lead(name="<b>Иван</b>", phone="+79991234567", comment="<script>"))

    text = sender.calls[0][1]
    assert "&lt;b&gt;Иван&lt;/b&gt;" in text
    assert "&lt;script&gt;" in text
