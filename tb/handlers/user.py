import os
import re
import qrcode
import random
import string
import gettext
from decimal import Decimal
from datetime import datetime, timedelta
from tortoise.expressions import F


from telebot import util, types
from telebot.async_telebot import AsyncTeleBot

from config import settings
from database.crud.order import create_pay_order
from database.models.order import Order
from database.models.user import User
from tb.states import UserStates
from utils.core.functions import trx_rate, fetch_account_address, rental_energy, dynamic_energy_unit
from utils.log import logger


def _(language):
    try:
        locale_dir = os.path.join(settings.PATH, "locale")
        gettext.bindtextdomain("messages", locale_dir)
        gettext.textdomain("messages")
        return gettext.translation("messages", locale_dir, languages=[language]).gettext
    except FileNotFoundError:
        return gettext.gettext


def start_button(lang):
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(_(lang)("Energy"), callback_data="energy"),
            types.InlineKeyboardButton(_(lang)("Recharge"), callback_data="recharge"),
        ],
        [
            types.InlineKeyboardButton(_(lang)("Promotion Cashback"), callback_data="promotion_cashback"),
            types.InlineKeyboardButton(_(lang)("Switch Language"), callback_data="switch_language"),
        ],
        [
            types.InlineKeyboardButton(_(lang)("Group"), url=settings.GROUP_URL),
            types.InlineKeyboardButton(_(lang)("Contact Us"), url=settings.CONTACT_URL),
        ]
    ])
    return keyboard


async def start_command(m: types.Message, bot: AsyncTeleBot):
    try:
        cid = m.chat.id

        inviter = util.extract_arguments(m.text)
        name = f"{m.chat.first_name or ''} {m.chat.last_name or ''}".strip()

        user, created = await User.get_or_create(uid=cid, defaults={'name': name, 'invited_by': inviter if inviter else None})
        if not created and user.name != name:
            await User.filter(uid=cid).update(name=name)

        address = user.wallet
        lang = user.language
        balance = user.balance

        msg = (
            _(lang)("Start" if address is None else "Start Using")
            .format(balance, dynamic_energy_unit(), datetime.now().strftime("%Y-%m-%d %H:%M"), address or "")
        )
        await bot.send_message(cid, msg, reply_markup=start_button(lang))
    except Exception as e:
        logger.error(f"start_command日志：{e}")


async def energy(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        msg = _(lang)("Start Using Energy")
        await bot.send_message(cid, msg)
    except Exception as e:
        logger.error(f"energy日志：{e}")


def recharge_button(lang):
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(_(lang)("Recharge Trx"), callback_data="recharge_trx"),
        ],
        [
            types.InlineKeyboardButton(_(lang)("Recharge Usdt"), callback_data="recharge_usdt"),
        ],
        [
            types.InlineKeyboardButton(_(lang)("Back"), callback_data="back"),
        ]
    ])
    return keyboard


async def recharge(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        rate = await trx_rate()
        msg = _(lang)("Recharge Method").format(rate)
        await bot.edit_message_text(msg, cid, call.message.message_id, reply_markup=recharge_button(lang))
    except Exception as e:
        logger.error(f"recharge日志：{e}")


async def recharge_trx(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        msg = _(lang)("Recharge Trx Num")
        await bot.set_state(call.from_user.id, UserStates.trx, cid)
        await bot.send_message(cid, msg)
    except Exception as e:
        logger.error(f"recharge_trx日志：{e}")


async def recharge_usdt(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        msg = _(lang)("Recharge Usdt Num")
        await bot.set_state(call.from_user.id, UserStates.usdt, cid)
        await bot.send_message(cid, msg)
    except Exception as e:
        logger.error(f"recharge_usdt日志：{e}")


def cancel_order_button(lang, trade_id):
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(_(lang)("Cancel Order"), callback_data=f"cancel_order_{trade_id}"),
        ]
    ])
    return keyboard


async def recharge_num(m: types.Message, bot: AsyncTeleBot, genre: int, pay_msg: str, err_msg: str):
    try:
        cid = m.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        trade_id = f"{''.join(random.choices(string.ascii_uppercase, k=6))}-{int(datetime.now().timestamp())}-{m.message_id}"
        enter_amount = m.text
        pattern = r'^\d+(\.\d+)?$'
        if re.match(pattern, enter_amount):
            await create_pay_order(cid, enter_amount, trade_id, genre)
            order = await Order.get(trade_id=trade_id)
            addr = order.wallet
            output_file_path = f"output/{addr}_{'trx' if genre == 1 else 'usdt'}.png"
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
            img = qrcode.make(addr)
            img.save(output_file_path)
            msg = _(lang)(pay_msg).format(order.amount, order.wallet)
            with open(output_file_path, 'rb') as photo:
                await bot.send_photo(cid, photo, msg, reply_markup=cancel_order_button(lang, trade_id))
        else:
            await bot.send_message(cid, _(lang)(err_msg))
        await bot.delete_state(m.from_user.id, m.chat.id)
    except Exception as e:
        logger.error(f"recharge_num日志：{e}")

async def recharge_trx_num(m: types.Message, bot: AsyncTeleBot):
    await recharge_num(m, bot, 1, "Pay Recharge Trx Num", "Pay Recharge Num Err")

async def recharge_usdt_num(m: types.Message, bot: AsyncTeleBot):
    await recharge_num(m, bot, 2, "Pay Recharge Usdt Num", "Pay Recharge Num Err")

async def promotion_cashback(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        bot_username = call.message.json['from']['username']
        user = await User.get(uid=cid)
        lang = user.language
        rebates = f"{settings.REBATE_RATION * 100}%"
        invitation_links = "https://t.me/" + bot_username + f"?start={cid}"
        msg = _(lang)("Promotion Cashback Link").format(rebates, invitation_links)
        await bot.delete_message(cid, call.message.message_id)
        await bot.send_message(cid, msg, reply_markup=back_button(lang))
    except Exception as e:
        logger.error(f"promotion_cashback 日志: {e}")

def language_button():
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton('简体中文', callback_data='language_zh_CN'),
            types.InlineKeyboardButton('English', callback_data='language_en_US'),
        ]
    ])
    return keyboard


async def switch_language(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        await bot.delete_message(cid, call.message.message_id)
        user = await User.get(uid=cid)
        lang = user.language
        msg = _(lang)("Supported Languages")
        await bot.send_message(cid, msg, reply_markup=language_button())
    except Exception as e:
        logger.error(f"switch_language日志：{e}")


async def set_language(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        await bot.delete_message(cid, call.message.message_id)
        lang = call.data[9:]
        await User.filter(uid=cid).update(language=lang)
        await bot.send_message(cid, _(lang)("Set Languages"), reply_markup=back_button(lang))
    except Exception as e:
        logger.error(f"set_language日志：{e}")


def back_button(lang):
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton(_(lang)("Back"), callback_data=f"back"),
        ]
    ])
    return keyboard


async def cancel_order(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        trade_id = call.data[13:]
        msg = _(lang)("Cancel Order Operation").format(trade_id)
        await bot.delete_message(cid, call.message.message_id)
        await Order.filter(trade_id=trade_id).delete()
        await bot.send_message(cid, msg, reply_markup=back_button(lang))
    except Exception as e:
        logger.error(f"cancel_order日志：{e}")

async def private_message(m: types.Message, bot: AsyncTeleBot):
    try:
        cid = m.chat.id
        user = await User.get(uid=cid)
        lang = user.language
        enter_msg = m.text
        if re.match(re.compile(r'^T[a-zA-Z0-9]{33}$'), enter_msg):
            result = await fetch_account_address(enter_msg)
            if result["code"] == 1:
                await User.filter(uid=cid).update(wallet=enter_msg)
                msg = _(lang)("Update Address").format(enter_msg)
                await bot.send_message(cid, msg, reply_markup=back_button(lang))
            else:
                msg = _(lang)("Address Not Activated").format(enter_msg)
                await bot.send_message(cid, msg, reply_markup=back_button(lang))

        elif re.match(re.compile(r'^\d+$'), enter_msg):
            address = user.wallet
            if address is None:
                msg = _(lang)("No Address Set").format(enter_msg)
                await bot.send_message(cid, msg, reply_markup=back_button(lang))
            else:
                balance = user.balance
                sum_energy_price = Decimal(int(enter_msg) * dynamic_energy_unit()).quantize(Decimal('0.00'))
                if balance - sum_energy_price >= 0:
                    result = await rental_energy(cid, int(enter_msg), "1h", address)
                    if result["code"] == 1:
                        await User.filter(uid=cid).update(balance=F('balance') - sum_energy_price)
                        new_time = (datetime.now() + timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S")
                        msg = _(lang)("Rental Energy Num").format(int(enter_msg), sum_energy_price, address, new_time)
                        await bot.send_message(cid, msg, reply_markup=back_button(lang))
                    else:
                        msg = _(lang)("Energy Insufficient")
                        await bot.send_message(cid, msg)
                        await bot.send_message(settings.ADMIN_ID, f"{result[msg]}")
                else:
                    msg = _(lang)("Balance Insufficient").format(sum_energy_price, balance)
                    await bot.send_message(cid, msg, reply_markup=back_button(lang))
    except Exception as e:
        logger.error(f"private_message日志：{e}")

async def back(call: types.CallbackQuery, bot: AsyncTeleBot):
    try:
        cid = call.message.chat.id
        user = await User.get(uid=cid)
        address = user.wallet
        lang = user.language
        balance = user.balance

        msg = (
            _(lang)("Start" if address is None else "Start Using")
            .format(balance, dynamic_energy_unit(), datetime.now().strftime("%Y-%m-%d %H:%M"), address or "")
        )
        await bot.edit_message_text(msg, cid, call.message.message_id, reply_markup=start_button(lang))
        await bot.delete_state(call.from_user.id, cid)
    except Exception as e:
        logger.error(f"back日志：{e}")
