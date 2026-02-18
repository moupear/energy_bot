from telebot import types
from telebot.async_telebot import AsyncTeleBot

from database.models.user import User
from tb.states import AdminStates
from utils.log import logger


async def start_command(m: types.Message, bot: AsyncTeleBot):
    try:
        cid = m.chat.id
        keyboard = types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("群发消息", callback_data='bulk_bulletin')
            ]
        ])
        count = await User.all().count()
        msg = f"当前用户数量: {count}\n\n"
        await bot.send_message(cid, msg, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"admin_start日志：{e}")

async def bulk(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        await bot.set_state(call.from_user.id, AdminStates.bulletin, cid)
        await bot.send_message(cid, "请输入需要群发的消息")
    except Exception as e:
        logger.error(f"miss日志：{e}")

async def bulk_send(m: types.Message, bot: AsyncTeleBot):
    import asyncio
    try:
        received_message = m.text
        users = await User.all()

        async def send_to_user(user):
            try:
                await bot.send_message(chat_id=user.uid, text=received_message)
            except Exception as ex:
                logger.error(f"发送给{user.uid}的信息失败了: {ex}")

        await asyncio.gather(*[send_to_user(user) for user in users])
        await bot.delete_state(m.from_user.id, m.chat.id)

    except Exception as e:
        logger.error(f"bulk_send日志：{e}")