from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
from bot.handlers.handlers import r
import os
import logging 


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from utils.db import db

load_dotenv()
TOKEN = os.getenv("BOT")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await db.setup()
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(r)
    await dp.start_polling(bot)





if __name__ == "__main__":
    asyncio.run(main())