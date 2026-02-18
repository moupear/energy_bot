from telebot.asyncio_filters import SimpleCustomFilter

from config import settings


class AdminFilter(SimpleCustomFilter):
    """
    Filter for admin users
    """
    key = 'admin'
    async def check(self, message):
        return int(message.from_user.id) == settings.ADMIN_ID