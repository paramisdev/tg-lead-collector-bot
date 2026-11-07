import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callbacks.lead import LeadCallback
from bot.keyboards.lead import (
    cancel_keyboard,
    comment_keyboard,
    confirm_keyboard,
    start_keyboard,
)
from bot.services.lead import Lead, LeadService
from bot.states.lead import LeadForm
from bot.utils.validators import normalize_phone

logger = logging.getLogger(__name__)

router = Router(name="lead")

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 80
COMMENT_MAX_LENGTH = 500

CANCEL_TEXT = "Заявка отменена. Если захотите начать заново — нажмите «Оставить заявку»."


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
    if isinstance(callback.message, Message):
        await callback.message.answer("Как к вам обращаться?", reply_markup=cancel_keyboard())


@router.message(LeadForm.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH:
        await message.answer(
            f"Имя должно быть от {NAME_MIN_LENGTH} до {NAME_MAX_LENGTH} символов. "
            "Попробуйте ещё раз.",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer(
        "Укажите номер телефона, например +7 999 123-45-67.",
        reply_markup=cancel_keyboard(),
    )


@router.message(LeadForm.phone, F.text)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = normalize_phone(message.text or "")
    if phone is None:
        await message.answer(
            "Не удалось распознать номер. Введите телефон в формате +7 999 123-45-67.",
            reply_markup=cancel_keyboard(),
        )
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
        await message.answer(
            f"Комментарий не должен превышать {COMMENT_MAX_LENGTH} символов.",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(comment=comment or None)
    await _show_summary(message, state)


@router.callback_query(LeadCallback.filter(F.action == "skip"), LeadForm.comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(comment=None)
    if isinstance(callback.message, Message):
        await _show_summary(callback.message, state)


@router.callback_query(LeadCallback.filter(F.action == "confirm"), LeadForm.confirm)
async def confirm_lead(
    callback: CallbackQuery,
    state: FSMContext,
    lead_service: LeadService,
) -> None:
    data = await state.get_data()
    lead = Lead(
        name=str(data.get("name", "")),
        phone=str(data.get("phone", "")),
        comment=str(data["comment"]) if data.get("comment") else None,
    )

    try:
        await lead_service.submit(lead)
    except TelegramAPIError:
        logger.exception("Failed to send lead to admin")
        await callback.answer(
            "Не удалось отправить заявку. Попробуйте позже.",
            show_alert=True,
        )
        return

    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text("Спасибо! Заявка отправлена. Мы свяжемся с вами.")

    await callback.answer("Заявка отправлена")


@router.callback_query(LeadCallback.filter(F.action == "cancel"))
async def cancel_lead(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Заявка отменена")
    if isinstance(callback.message, Message):
        await callback.message.edit_text(CANCEL_TEXT, reply_markup=start_keyboard())
