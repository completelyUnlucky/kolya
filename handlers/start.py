from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from db import Session, User
from keys import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    db_session = Session()
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        new_user = User(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            username=message.from_user.username,
            role='user'
        )
        db_session.add(new_user)
        db_session.commit()
    await message.answer("Добро пожаловать!", reply_markup=main_menu())


@router.message(F.text == "🛠 Стать фрилансером")
async def become_freelancer(message: Message):
    db_session = Session()
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()

    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        return

    if user.role == "freelancer":
        await message.answer("✅ Вы уже фрилансер!")
        return

    user.role = "freelancer"
    db_session.commit()

    await message.answer("🎉 Теперь вы фрилансер! Можете откликаться на заказы.")
