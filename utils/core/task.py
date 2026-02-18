import asyncio
from decimal import Decimal
import requests

from config import settings
from database.models.order import Order
from database.models.user import User
from datetime import datetime, timedelta

from database.models.wallet import Wallet
from tb.bot import bot

from utils.core.functions import trx_rate

from tb.handlers.user import back_button
from utils.log import logger


class Listens:
    def __init__(self):
        self.min_trx_amount = Decimal('0.01')
        self.rebate_ration = settings.REBATE_RATION
        self.url_trx = "https://apilist.tronscanapi.com/api/transfer/trx"
        self.url_usdt = "https://apilist.tronscanapi.com/api/transfer/trc20"

    async def trx_variations(self):
        logger.info("启动监听波场trx变化")
        while True:
            try:
                order_list = await Order.filter(status=1, genre=1).all()
                if len(order_list) <= 0:
                    continue

                for o in order_list:
                    wallet = o.wallet
                    current_time = datetime.now()
                    end_timestamp = int(current_time.timestamp() * pow(10, 3))
                    start_timestamp = int((current_time - timedelta(minutes=60)).timestamp() * pow(10, 3))
                    params = {
                        "address": wallet,
                        "start": "0",
                        "limit": "50",
                        "direction": "2",
                        "start_timestamp": start_timestamp,
                        "end_timestamp": end_timestamp,
                        "sort": "-timestamp",
                        "db_version": "1"
                    }
                    headers = {
                        "TRON-PRO-API-KEY": settings.TRON_PRO_API_KEY,
                        'Accept': 'application/json'
                    }
                    rsp = requests.get(self.url_trx, params=params, headers=headers)
                    rsp.raise_for_status()
                    res = rsp.json()
                    if res.get('page_size') == 0:
                        continue
                    for transfer in res.get('data'):
                        await self.transfers(transfer, wallet, 1)
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"监听trx错误: {e}")

    async def usdt_variations(self):
        logger.info("启动监听波场usdt变化")
        while True:
            try:
                order_list = await Order.filter(genre=2, status=1).all()
                if len(order_list) <= 0:
                    continue
                for o in order_list:
                    wallet = o.wallet
                    current_time = datetime.now()
                    end_timestamp = int(current_time.timestamp() * pow(10, 3))
                    start_timestamp = int((current_time - timedelta(minutes=60)).timestamp() * pow(10, 3))
                    params = {
                        "sort": "-timestamp",
                        "limit": "50",
                        "start": "0",
                        "direction": "2",
                        "db_version": "1",
                        "trc20Id": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                        "address": wallet,
                        "start_timestamp": start_timestamp,
                        "end_timestamp": end_timestamp,
                    }
                    headers = {
                        "TRON-PRO-API-KEY": settings.TRON_PRO_API_KEY,
                        'Accept': 'application/json'
                    }
                    rsp = requests.get(self.url_usdt, params=params, headers=headers)
                    rsp.raise_for_status()
                    res = rsp.json()
                    if res.get('page_size') > 0:
                        for transfer in res.get('data'):
                            await self.transfers(transfer, wallet, 2)

                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"监听Usdt错误: {e}")

    async def transfers(self, transfer, wallet, genre):
        if transfer['to'] == wallet and transfer['contract_ret'] == "SUCCESS":
            transfer_amount = float(transfer['amount']) / pow(10, 6)
            if transfer_amount >= self.min_trx_amount:
                amount = Decimal(transfer_amount).quantize(Decimal('0.00'))
                order = await Order.filter(wallet=wallet, amount=amount, genre=genre, status=1).first()
                if order and amount - order.amount == 0:
                    print(int(transfer['block_timestamp']))
                    create_time = datetime.strptime(str(order.created_at), "%Y-%m-%d %H:%M:%S.%f%z").replace(
                        tzinfo=None)
                    create_timestamp = int(create_time.timestamp() * pow(10, 3))
                    if int(transfer['block_timestamp']) > create_timestamp:
                        await self.update_order_and_notify(order, amount, genre)

    async def update_order_and_notify(self, order, amount, genre):
        global new_balance, usdt_rate_trx
        cid = order.order_id
        trade_id = order.trade_id
        info = await User.get(uid=cid)
        lang = info.language
        inviter = info.invited_by
        balance = info.balance
        if genre == 1:
            new_balance = balance + amount
        else:
            rate = await trx_rate()
            usdt_rate_trx = Decimal(rate).quantize(Decimal('0.00'))
            new_balance = info.balance + amount * usdt_rate_trx

        await Order.filter(trade_id=trade_id).update(status=2)
        await User.filter(uid=cid).update(balance=new_balance)
        await bot.delete_message(cid, int(trade_id.split('-')[-1]) + 1)
        msg = "余额充值成功" if lang == "zh_CN" else "Balance recharged successfully"
        await bot.send_message(cid, msg, reply_markup=back_button(lang))
        if inviter:
            inviter_info = await User.get(uid=inviter)
            rebate = Decimal(self.rebate_ration).quantize(Decimal('0.00'))
            inviter_new_balance = Decimal(inviter_info.balance + (
                amount * rebate if genre == 1 else amount * usdt_rate_trx * rebate)).quantize(Decimal('0.00'))
            await User.filter(uid=inviter).update(balance=inviter_new_balance)

    @staticmethod
    async def order_expired():
        logger.info("启动订单是否过期监控")
        while True:
            try:
                orders = await Order.filter(status=1).all()
                for order in orders:
                    create_time = datetime.strptime(str(order.created_at), "%Y-%m-%d %H:%M:%S.%f%z").replace(
                        tzinfo=None)
                    if datetime.now() - create_time > timedelta(minutes=60):
                        trade_id = order.trade_id
                        await Order.filter(trade_id=trade_id).delete()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"order_expired错误日志: {e}")
