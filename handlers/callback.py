from aiogram import Router
from aiogram.types import CallbackQuery

callback_router = Router()


@callback_router.callback_query()
async def handle_unknown_callbacks(callback: CallbackQuery):
    """Noma'lum callback handlerlar uchun"""
    await callback.answer("❌ Noma'lum komanda!")