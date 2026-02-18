from tortoise import fields
from tortoise.models import Model


class TimestampMixin(Model):
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True # 表示这是一个抽象基类，不会创建单独的数据表