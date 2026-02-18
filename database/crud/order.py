from decimal import Decimal

from database.models.order import Order
from database.models.wallet import Wallet


async def calculate_available_wallet(amount, wallets, genre):
    available_wallet = ""
    for w in wallets:
        address =w.wallet
        result = await Order.filter(wallet=address, amount=amount, genre=genre, status=1).first()
        if not result:
            available_wallet = address
            break
    return available_wallet


async def create_pay_order(telegram_id, amount, trade_id, genre):
    available_wallet = ""
    available_amount = Decimal(amount)
    usdt_amount_per_increment = Decimal('0.01')
    wallets = await Wallet.filter(status=1, genre=genre).all()
    for _ in range(100):
        result = await calculate_available_wallet(available_amount, wallets, genre)
        if not result:
            available_amount += usdt_amount_per_increment
            continue
        available_wallet = result
        break
    await Order.create(
        order_id=telegram_id,
        trade_id=trade_id,
        wallet=available_wallet,
        genre=genre,
        amount=available_amount,
        status=1
    )
