from tb.handlers import user, admin, group
from tb.states import AdminStates
from tb.states import UserStates

class RegisterHandlers:
    def __init__(self, bot):
        self.bot = bot
    def admin(self):
        self.bot.register_message_handler(admin.start_command, commands=['start'], admin=True, pass_bot=True)
        self.bot.register_callback_query_handler(admin.bulk, func=lambda c: c.data == 'bulk_bulletin', pass_bot=True)
        self.bot.register_message_handler(admin.bulk_send, content_types=["text"], state=AdminStates.bulletin, pass_bot=True)

    def users(self):
        self.bot.register_message_handler(user.start_command, commands=['start'], admin=False, pass_bot=True)
        self.bot.register_callback_query_handler(user.energy, func=lambda c: c.data == 'energy', pass_bot=True)

        self.bot.register_callback_query_handler(user.recharge, func=lambda c: c.data == 'recharge', pass_bot=True)
        self.bot.register_callback_query_handler(user.recharge_trx, func=lambda c: c.data == 'recharge_trx', pass_bot=True)
        self.bot.register_message_handler(user.recharge_trx_num, state=UserStates.trx, pass_bot=True)
        self.bot.register_callback_query_handler(user.recharge_usdt, func=lambda c: c.data == 'recharge_usdt', pass_bot=True)
        self.bot.register_message_handler(user.recharge_usdt_num, state=UserStates.usdt, pass_bot=True)

        self.bot.register_callback_query_handler(user.promotion_cashback, func=lambda c: c.data == 'promotion_cashback', pass_bot=True)

        self.bot.register_callback_query_handler(user.switch_language, func=lambda c: c.data == 'switch_language', pass_bot=True)
        self.bot.register_callback_query_handler(user.set_language, func=lambda c: c.data.startswith('language_'), pass_bot=True)

        self.bot.register_callback_query_handler(user.cancel_order, func=lambda c: c.data.startswith('cancel_order_'), pass_bot=True)
        self.bot.register_callback_query_handler(user.back, func=lambda c: c.data == 'back', pass_bot=True)
        self.bot.register_message_handler(user.private_message, chat_types=['private'], pass_bot=True)

    def group(self):
        self.bot.register_chat_member_handler(group.welcome, func=lambda message: True, pass_bot=True)