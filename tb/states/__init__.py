from telebot.asyncio_handler_backends import State, StatesGroup

class AdminStates(StatesGroup):
    bulletin = State()

class UserStates(StatesGroup):
    trx = State()
    usdt = State()