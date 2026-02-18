import asyncio
from database.mdb import register_tortoise
from tb.bot import run_bot
from utils.core.task import Listens
from utils.log import logger

task = Listens()

async def run():
    try:
        await asyncio.gather(
            register_tortoise(),
            run_bot(),
            task.order_expired(),
            task.trx_variations(),
            task.usdt_variations(),
        )
    except Exception as e:
        logger.info(f"Start Error: {e}")

if __name__ == '__main__':
    asyncio.run(run())

    