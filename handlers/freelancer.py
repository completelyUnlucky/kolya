from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import Session, Order, User
from utils.cryptobot import create_invoice

router = Router()


class CompleteOrderState(StatesGroup):
    order_id = State()


@router.message(F.text == "💰 Заказ выполнен")
async def request_order_id(message: Message, state: FSMContext):
    await message.answer("Введите ID заказа, который вы выполнили:")
    await state.set_state(CompleteOrderState.order_id)


@router.message(CompleteOrderState.order_id)
async def send_payment_link(message: Message, state: FSMContext):
    try:
        order_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный ID заказа.")
        return

    db_session = Session()
    freelancer = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    order = db_session.query(Order).get(order_id)

    if not freelancer or freelancer.role != "freelancer":
        await message.answer("❌ Вы не фрилансер!")
        return

    if not order:
        await message.answer("❌ Заказ не найден.")
        return

    base_price = order.price
    commission = base_price * 0.05
    total_price = round(base_price + commission, 2)

    try:
        invoice_url = create_invoice(amount_usdt=total_price, order_id=order_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=invoice_url)]
        ])

        await message.bot.send_message(
            chat_id=order.user.telegram_id,
            text=f"✅ Исполнитель @{freelancer.username} завершил заказ.\n"
                 f"Сумма: {base_price} USDT\n"
                 f"Комиссия (5%): {commission:.2f} USDT\n"
                 f"Итого к оплате: {total_price:.2f} USDT",
            reply_markup=keyboard
        )
        await message.answer("✅ Ссылка на оплату отправлена заказчику.")
    except Exception as e:
        await message.answer(f"❌ Не удалось создать счёт: {str(e)}")

    await state.clear()
