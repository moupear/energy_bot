from telebot import types
from telebot.async_telebot import AsyncTeleBot


async def welcome(m: types.ChatMemberUpdated, bot: AsyncTeleBot):
    import asyncio
    new_member = m.new_chat_member
    old_member = m.old_chat_member
    if new_member.status in ['member', 'administrator', 'creator'] and old_member.status == 'left':
        welcome_message = await bot.send_message(m.chat.id, f"欢迎 {new_member.user.first_name} 加入！")
        await asyncio.sleep(10)
        await bot.delete_message(m.chat.id, welcome_message.message_id)