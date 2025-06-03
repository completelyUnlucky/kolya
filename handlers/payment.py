from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from db import Session, Order

router = Router()


class PaymentState(StatesGroup):
    order_id = State()


# === Команда /pay или кнопка "Оплатить" ===
@router.message(F.text == "💳 Оплатить заказ")
async def start_payment(message: Message, state: FSMContext):
    await message.answer("Введите ID заказа, который хотите оплатить:")
    await state.set_state(PaymentState.order_id)


@router.message(PaymentState.order_id)
async def process_order_id(message: Message, state: FSMContext):
    try:
        order_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный ID заказа.")
        return

    db_session = Session()
    order = db_session.query(Order).get(order_id)

    if not order:
        await message.answer("❌ Заказ не найден.")
        await state.clear()
        return

    # Считаем сумму с комиссией
    base_price = order.price
    commission = base_price * 0.05
    total_price = base_price + commission

    # Генерируем ссылку на оплату через CryptoBot
    invoice_link = f"https://t.me/CryptoBot?start=IVlqkAgAAAAdGZhbmtzX2JvdF8xfDB8MTIzNDU2Nzg5f{total_price:.2f}USDT"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через CryptoBot", url=invoice_link)]
    ])

    await message.answer(
        f"Сумма заказа: {base_price} USDT\n"
        f"Комиссия (5%): {commission:.2f} USDT\n"
        f"Итого к оплате: {total_price:.2f} USDT",
        reply_markup=keyboard
    )

    await state.clear()