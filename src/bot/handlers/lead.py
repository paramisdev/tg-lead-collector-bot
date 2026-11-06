import logging
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callbacks.lead import LeadCallback
from bot.keyboards.lead import comment_keyboard, confirm_keyboard
from bot.states.lead import LeadForm

logger = logging.getLogger(__name__)

router = Router(name="lead")

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 80
COMMENT_MAX_LENGTH = 500
PHONE_MIN_LENGTH = 5


def _format_lead(data: dict[str, Any]) -> str:
    comment = data.get("comment") or "—"
    return (
        "<b>Новая заявка</b>\n\n"
        f"<b>Имя:</b> {data.get('name', '')}\n"
        f"<b>Телефон:</b> {data.get('phone', '')}\n"
        f"<b>Комментарий:</b> {comment}"
    )


async def _show_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    comment = data.get("comment") or "—"
    await state.set_state(LeadForm.confirm)
    await message.answer(
        "<b>Проверьте заявку</b>\n\n"
        f"<b>Имя:</b> {data.get('name', '')}\n"
        f"<b>Телефон:</b> {data.get('phone', '')}\n"
        f"<b>Комментарий:</b> {comment}",
        reply_markup=confirm_keyboard(),
    )


@router.callback_query(LeadCallback.filter(F.action == "start"))
async def start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(LeadForm.name)
    if callback.message is not None:
        await callback.message.answer("Как к вам обращаться?")


@router.message(LeadForm.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH:
        await message.answer(
            f"Имя должно быть от {NAME_MIN_LENGTH} до {NAME_MAX_LENGTH} символов. Попробуйте ещё раз."
        )
        return

    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer("Укажите номер телефона, например +7 999 123-45-67.")


@router.message(LeadForm.phone, F.text)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if len(phone) < PHONE_MIN_LENGTH:
        await message.answer("Укажите номер телефона, например +7 999 123-45-67.")
        return

    await state.update_data(phone=phone)
    await state.set_state(LeadForm.comment)
    await message.answer(
        "Добавьте комментарий к заявке или нажмите «Пропустить».",
        reply_markup=comment_keyboard(),
    )


@router.message(LeadForm.comment, F.text)
async def process_comment(message: Message, state: FSMContext) -> None:
    comment = (message.text or "").strip()
    if len(comment) > COMMENT_MAX_LENGTH:
        await message.answer(f"Комментарий не должен превышать {COMMENT_MAX_LENGTH} символов.")
        return

    await state.update_data(comment=comment or None)
    await _show_summary(message, state)


@router.callback_query(LeadCallback.filter(F.action == "skip"), LeadForm.comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(comment=None)
    if callback.message is not None:
        await _show_summary(callback.message, state)


@router.callback_query(LeadCallback.filter(F.action == "confirm"), LeadForm.confirm)
async def confirm_lead(callback: CallbackQuery, state: FSMContext, admin_chat_id: int) -> None:
    data = await state.get_data()
    await state.clear()

    if callback.message is not None:
        await callback.bot.send_message(chat_id=admin_chat_id, text=_format_lead(data))
        await callback.message.edit_text("Спасибо! Заявка отправлена. Мы свяжемся с вами.")

    await callback.answer("Заявка отправлена")
