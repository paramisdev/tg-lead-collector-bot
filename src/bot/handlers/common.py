from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.lead import start_keyboard

router = Router(name="common")

WELCOME_TEXT = (
    "Здравствуйте! Поможем с вашей задачей.\n\nОставьте заявку — свяжемся с вами в ближайшее время."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=start_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await state.clear()

    if current_state is None:
        await message.answer("Активной заявки нет.", reply_markup=start_keyboard())
        return

    await message.answer("Заявка отменена.", reply_markup=start_keyboard())
