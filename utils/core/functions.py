import random
import string
import hmac
import hashlib
import json
from datetime import datetime

import aiohttp
from database.models.order import Order
from config import settings
from utils.log import logger


def dynamic_energy_unit():
    now = datetime.now().time()
    data = settings.ELECTRICITY_PRICE
    start_time = datetime.strptime("05:00:00", "%H:%M:%S").time()
    end_time =datetime.strptime("13:00:00", "%H:%M:%S").time()

    if start_time < now < end_time:
        return round(data["daytime"]["price"], 2)
    else:
        return round(data["nighttime"]["price"], 2)

async def trx_rate():
    url = "https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=TRX"
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as rsp:
            rsp.raise_for_status()
            result = await rsp.json()
            rate = result['TRX']
            return round(rate * 0.95, 2)

async def fetch_account_address(address):
    url = f"https://apilist.tronscanapi.com/api/accountv2?address={address}"
    headers = {
        "TRON-PRO-API-KEY": settings.TRON_PRO_API_KEY,
        'Accept': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as rsp:
            result = await rsp.json()
            latest_operation_time = result.get('latest_operation_time', '')
            if latest_operation_time and int(latest_operation_time) != 0:
                return {'code': 1, 'msg': f"地址 {address} 已激活，最新操作时间: {latest_operation_time}"}
            else:
                return {'code': 0, 'msg': f"地址 {address} 未激活"}

async def rental_energy(cid, enter_num, period, address):
    if enter_num % 2 == 0:
        energy_num = 65500*enter_num
    else:
        energy_num  = 65000 * enter_num + 1000 * (enter_num - 1)/2

    fullPath = "/api/v1/rent"
    method = "POST"

    data = {
        "energy_amount": float(energy_num), 
        "period": int(0),                  
        "receive_address": str(address), 
    }
    body_str = json.dumps(data, separators=(',', ':'))
    timestamp = int(datetime.now().timestamp())
    message = f"{timestamp}{method}{fullPath}{body_str}"  
    signature = compute_hmac(message, settings.API_SECRET)

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": settings.API_KEY,
        "X-Timestamp": str(timestamp),
        "X-Signature": signature
    }

    url = settings.API_URL + fullPath
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=body_str, headers=headers) as rsp:
            result = await rsp.json()
            print(result)
            if rsp.status == 200 and result['status_code'] == 200:
                random_letters = ''.join(random.choices(string.ascii_uppercase, k=6))
                trade_id = f"{random_letters}-{timestamp}"
                await Order.create(
                    order_id=cid,
                    status=2,
                    wallet=address,
                    trade_id=trade_id,
                    genre=3,
                    amount=energy_num
                )
                return {'code': 1, 'msg': f"能量租用成功， 有效期: {period}"}
    
            else:
                logger.error(f"租用失败, 原因: {result}")
                return {'code': 0, 'msg': f"租用失败, 原因: {result}"}

def compute_hmac(message: str, secret: str) -> str:
    """计算 HMAC-SHA256 签名"""
    h = hmac.new(secret.encode(), message.encode(), hashlib.sha256)
    return h.hexdigest()