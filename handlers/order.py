from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import Session, User, Order
from config import CHANNEL_ID

router = Router()

class CreateOrderState(StatesGroup):
    text = State()


@router.message(F.text == "📦 Создать заказ")
async def create_order_start(message: Message, state: FSMContext):
    await message.answer("Введите текст вашего заказа:")
    await state.set_state(CreateOrderState.text)


@router.message(CreateOrderState.text)
async def process_order_text(message: Message, state: FSMContext):
    db_session = Session()
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()

    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        await state.clear()
        return

    new_order = Order(
        text=message.text,
        user_id=user.telegram_id
    )
    db_session.add(new_order)
    db_session.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Откликнуться", callback_data=f"apply_{new_order.id}")]
    ])

    await message.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Новый заказ:\n\n{message.text}\n\nID: {new_order.id}",
        reply_markup=keyboard
    )

    await message.answer("Ваш заказ опубликован в канале.")
    await state.clear()


# ==== Кнопка "Откликнуться" ====
@router.callback_query(lambda c: c.data.startswith("apply_"))
async def apply_to_order(callback: CallbackQuery):
    try:
        order_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный ID заказа")
        return

    db_session = Session()
    freelancer = db_session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    order = db_session.query(Order).get(order_id)

    if not order:
        await callback.answer("❌ Заказ не найден")
        return

    if not freelancer or freelancer.role != "freelancer":
        await callback.answer("❌ Вы не фрилансер!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"confirm_{freelancer.telegram_id}_{order_id}")]
    ])

    await callback.bot.send_message(
        chat_id=order.user.telegram_id,
        text=f"Фрилансер @{freelancer.username} откликнулся на ваш заказ.",
        reply_markup=keyboard
    )
    await callback.answer("Вы откликнулись!")


@router.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_freelancer(callback: CallbackQuery):
    _, fid, oid = callback.data.split("_")
    db_session = Session()
    freelancer = db_session.query(User).filter_by(telegram_id=int(fid)).first()
    order = db_session.query(Order).get(int(oid))

    if not freelancer:
        await callback.answer("❌ Фрилансер не найден")
        return

    try:
        await callback.bot.send_message(
            chat_id=freelancer.telegram_id,
            text=f"Заказчик @{callback.from_user.username} принял ваш отклик.\n"
                 f"Текст заказа:\n{order.text}"
        )
        await callback.message.edit_text("Информация отправлена исполнителю.")
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")