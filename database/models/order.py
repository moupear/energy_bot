from tortoise import fields

from database.models import TimestampMixin



class Order(TimestampMixin):
    """
    订单类
    """
    id = fields.BigIntField(pk=True, index=True, description='ID')
    order_id = fields.CharField(max_length=255, null=False, description='交易ID')
    trade_id = fields.CharField(max_length=255, null=False, description='订单号')
    wallet = fields.CharField(max_length=255, null=True, description='波场TRC钱包')
    genre = fields.IntField(default=0, description='订单类型') # 1=TRX支付 2=USDT支付 3=能量
    amount = fields.DecimalField(max_digits=15, decimal_places=2, default=0.00, description='交易金额, 数量等')
    status = fields.IntField(default=0, description='状态') # 1=等待 2=成功 3=过期

    class Meta:
        table_description = "订单表"
        table = 'orders'
