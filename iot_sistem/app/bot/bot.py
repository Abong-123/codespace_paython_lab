import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)
async def send_telegram_message(message: str):
    await bot.send_message(chat_id=CHAT_ID, text=message)