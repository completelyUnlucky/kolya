from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db import Session, User

router = Router()


@router.message(Command("profile"))
@router.message(F.text == "👤 Личный кабинет")
async def show_profile(message: Message):
    db_session = Session()
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()

    if not user:
        await message.answer("❌ Вы не зарегистрированы. Напишите /start")
        return

    await message.answer(f"""
    👤 Ваш профиль:

    Telegram ID: <code>{user.telegram_id}</code>
    Имя: {user.name}
    Username: @{user.username if user.username else 'не указан'}
    Роль: {user.role.capitalize()}
    Рейтинг: ⭐ {user.rating:.1f}

    """.strip(), parse_mode="HTML")
