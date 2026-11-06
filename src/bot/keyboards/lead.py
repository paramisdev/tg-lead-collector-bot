from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.lead import LeadCallback


def start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Оставить заявку", callback_data=LeadCallback(action="start"))
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отменить", callback_data=LeadCallback(action="cancel"))
    return builder.as_markup()


def comment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пропустить", callback_data=LeadCallback(action="skip"))
    builder.button(text="Отменить", callback_data=LeadCallback(action="cancel"))
    builder.adjust(1)
    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить", callback_data=LeadCallback(action="confirm"))
    builder.button(text="Отменить", callback_data=LeadCallback(action="cancel"))
    builder.adjust(1)
    return builder.as_markup()
