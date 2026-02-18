from tortoise import fields

from database.models import TimestampMixin


class Wallet(TimestampMixin):
    """
    收款钱包类
    """
    id = fields.BigIntField(pk=True, index=True, description='ID')
    wallet = fields.CharField(max_length=255, null=True, description='波场TRC钱包')
    genre = fields.IntField(default=1, description='类型：1:TRX钱包 2:USDT钱包')
    status = fields.IntField(default=0, description='状态：1:启用 2:禁用')

    class Meta:
        table_description = "钱包表"
        table = 'wallets'
