from tortoise import fields

from database.models import TimestampMixin

class User(TimestampMixin):
    """
    用户类
    """
    id = fields.BigIntField(pk=True, index=True, description='ID')
    uid = fields.BigIntField(unique=True, description='UID')
    name = fields.CharField(max_length=64, null=True, description='昵称')
    balance = fields.DecimalField(max_digits=8, decimal_places=2, default=0.00, description='余额')
    wallet = fields.CharField(max_length=255, null=True, description='波场TRC钱包')
    language = fields.CharField(max_length=16, default='zh_CN', description='语言')
    invited_by = fields.BigIntField(null=True, description='邀请者')

    class Meta:
        table_description = "用户表"
        table = 'users'
