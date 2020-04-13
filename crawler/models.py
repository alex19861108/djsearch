from django.db import models

# Create your models here.


class Resource(models.Model):
    """ 资源方 """
    name = models.CharField(verbose_name="英文名, 唯一标识", primary_key=True, db_index=True, unique=True, null=False, blank=False, max_length=20)
    cn_name = models.CharField(verbose_name="中文名", unique=True, max_length=20, null=False)
    config = models.TextField(verbose_name="资源配置")
    mapping = models.TextField(verbose_name="ES中的mapping配置", null=False)
    create_time = models.DateTimeField(verbose_name="接入时间", auto_now_add=True)
    contact = models.CharField(verbose_name="联系人", max_length=20)
    desc = models.TextField(verbose_name="资源描述")
    can_index = models.BooleanField(verbose_name="是否可以建索引", default=True)
    can_search = models.BooleanField(verbose_name="是否可以被搜索", default=True)
    order = models.IntegerField(verbose_name="排序序号", default=0)

    class Meta:
        db_table = "resource"
