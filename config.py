import os

class Settings:
    # 项目目录
    PATH: str = os.path.dirname(os.path.abspath(__file__))
    # 机器人 TOKEN
    BOT_TOKEN: str = ""
    # 超级管理员 ID
    ADMIN_ID: int = 
    # 返现比率
    REBATE_RATION: float = round(0.06, 2)
    # 群链接
    GROUP_URL: str = ""
    # 客服链接
    CONTACT_URL: str = ""
    # PostgreSQL配置
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = "bot"

    # 价格配置
    ELECTRICITY_PRICE: dict = {
        "daytime": {
            "price": 2.89,
        },
        "nighttime": {
            "price": 2.98,
        }
    }

    API_URL: str = "https://api.trxu.io"
    API_KEY: str = ""
    API_SECRET: str = ""
    
    # TronScan API配置
    TRON_PRO_API_KEY: str = ""

settings = Settings()