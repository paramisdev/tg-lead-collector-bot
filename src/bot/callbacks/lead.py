from typing import Literal

from aiogram.filters.callback_data import CallbackData


class LeadCallback(CallbackData, prefix="lead"):
    action: Literal["start", "skip", "confirm"]
