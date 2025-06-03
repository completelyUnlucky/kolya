from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = lambda: ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Создать заказ")],
        [KeyboardButton(text="👤 Личный кабинет")],
        [KeyboardButton(text="💰 Заказ выполнен")],
        [KeyboardButton(text="🛠 Стать фрилансером")]
    ],
    resize_keyboard=True
)