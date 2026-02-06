from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def fallback_message(message: Message):
    await message.answer("Используй кнопки меню. Если нужно начать, отправь /start.")
