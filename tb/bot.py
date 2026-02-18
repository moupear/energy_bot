from telebot import apihelper
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from config import settings
from tb.filters import RegisterFilters
from tb.handlers import RegisterHandlers
from utils.log import logger

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = AsyncTeleBot(settings.BOT_TOKEN, state_storage=StateMemoryStorage(), parse_mode='HTML')

h = RegisterHandlers(bot=bot)
h.admin()
h.users()
h.group()

f = RegisterFilters(bot=bot)
f.binds()

async def run_bot():
    try:
        logger.info("Start Bot")
        await bot.infinity_polling(skip_pending=True, timeout=30)
    except Exception as e:
        logger.error(f"Start Bot Error: {e}")
