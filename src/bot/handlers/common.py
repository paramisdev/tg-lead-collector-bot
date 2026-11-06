from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.lead import start_keyboard

router = Router(name="common")

WELCOME_TEXT = (
    "Здравствуйте! Поможем с вашей задачей.\n\n"
    "Оставьте заявку — свяжемся с вами в ближайшее время."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=start_keyboard())
