from telebot.asyncio_filters import StateFilter

from tb.filters.admin import AdminFilter


class RegisterFilters:
    def __init__(self, bot):
        self.bot = bot
    def binds(self):
        self.bot.add_custom_filter(StateFilter(self.bot))
        self.bot.add_custom_filter(AdminFilter())
