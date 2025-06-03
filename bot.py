import asyncio
from aiogram import Bot, Dispatcher
from handlers import start, order, profile, payment
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключение роутеров
dp.include_router(start.router)
dp.include_router(order.router)
dp.include_router(profile.router)
dp.include_router(payment.router)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())