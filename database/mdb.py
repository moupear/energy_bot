from tortoise import Tortoise

from config import settings
from database.models import  user, wallet, order
from utils.log import logger

models = [user, wallet, order]

DB_ORM_CONFIG = {
    "connections": {
        "base": {
            'engine': 'tortoise.backends.asyncpg',
            "credentials": {
                'host': settings.POSTGRES_HOST if settings.POSTGRES_HOST else 'localhost',
                'user': settings.POSTGRES_USER if settings.POSTGRES_USER else 'postgres',
                'password': settings.POSTGRES_PASSWORD if settings.POSTGRES_PASSWORD else '123456',
                'port': settings.POSTGRES_PORT if settings.POSTGRES_PORT else 5432,
                'database': settings.POSTGRES_DB if settings.POSTGRES_DB else 'bot'
            }
        }
    },
    "apps": {
        "base": {
            "models": models, "default_connection": "base"
        }
    },
    'use_tz': False,
    'timezone': 'ASIA/Shanghai'
}
async def register_tortoise(generate_schemas: bool = False) -> None:
    await Tortoise.init(config=DB_ORM_CONFIG)
    logger.info("Tortoise-ORM started success")
    if generate_schemas:
        logger.info("Tortoise-ORM generating schema")
        await Tortoise.generate_schemas()

async def close_db_connection():
    await Tortoise.close_connections()