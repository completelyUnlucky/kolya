from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from db import Session, User, Order
from config import CHANNEL_ID

router = Router()

# === FSM для создания заказа ===
class CreateOrderState(StatesGroup):
    text = State()
    price = State()


# === Команда "Создать заказ" ===
@router.message(F.text == "📦 Создать заказ")
async def create_order_start(message: Message, state: FSMContext):
    await message.answer("Введите текст вашего заказа:")
    await state.set_state(CreateOrderState.text)


@router.message(CreateOrderState.text)
async def order_text_received(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Укажите стоимость заказа (в USDT):")
    await state.set_state(CreateOrderState.price)


@router.message(CreateOrderState.price)
async def order_price_received(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ Введите корректное число.")
        return

    data = await state.get_data()
    order_text = data["text"]

    db_session = Session()
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()

    if not user:
        await message.answer("❌ Вы не зарегистрированы. Напишите /start")
        await state.clear()
        return

    new_order = Order(
        text=order_text,
        price=price,
        user_id=user.telegram_id
    )
    db_session.add(new_order)
    db_session.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Откликнуться", callback_data=f"apply_{new_order.id}")]
    ])

    await message.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Новый заказ:\n\n{order_text}\n\nЦена: {price} USDT\nID: {new_order.id}",
        reply_markup=keyboard
    )

    await message.answer("Ваш заказ опубликован в канале.")
    await state.clear()


# === Кнопка "Откликнуться" в канале ===
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
        text=f"Фрилансер @{freelancer.username} откликнулся на ваш заказ.\n"
             f"Профиль: https://t.me/{freelancer.username}\n" 
             f"Нажмите ниже, чтобы принять исполнителя.",
        reply_markup=keyboard
    )
    await callback.answer("Вы откликнулись!")


# === Кнопка "Подтвердить фрилансера" ===
@router.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_freelancer(callback: CallbackQuery):
    _, fid, oid = callback.data.split("_")
    db_session = Session()
    freelancer = db_session.query(User).filter_by(telegram_id=int(fid)).first()
    order = db_session.query(Order).get(int(oid))

    if not freelancer or not order:
        await callback.answer("❌ Данные не найдены")
        return

    try:
        await callback.bot.send_message(
            chat_id=freelancer.telegram_id,
            text=f"Заказчик @{callback.from_user.username} принял вас!\n"
                 f"Текст заказа:\n{order.text}"
        )
        await callback.message.edit_text("✅ Исполнитель уведомлен о принятии.")
    except Exception as e:
        await callback.answer(f"❌ Не удалось отправить сообщение: {str(e)}")