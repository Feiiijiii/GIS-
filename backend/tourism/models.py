from django.contrib.auth.models import User
from django.db import models  # 使用普通的models而不是gis.db.models

class ScenicSpot(models.Model):
    name = models.CharField("景点名称", max_length=100)
    # 使用普通字段代替PointField
    longitude = models.FloatField("经度", default=104.07)
    latitude = models.FloatField("纬度", default=30.67)
    description = models.TextField("描述", blank=True)
    category = models.CharField("分类", max_length=50, choices=[
        ('历史文化', '历史文化'),
        ('美食探索', '美食探索'),
        ('自然风光', '自然风光'),
        ('购物娱乐', '购物娱乐'),
        ('艺术展馆', '艺术展馆'),
        ('古镇民俗', '古镇民俗'),
        ('主题乐园', '主题乐园'),
        ('休闲度假', '休闲度假'),
        ('宗教文化', '宗教文化'),
        ('城市景观', '城市景观'),
        ('其他', '其他'),
    ])
    address = models.CharField("地址", max_length=200, blank=True)
    opening_hours = models.CharField("开放时间", max_length=100, blank=True)
    ticket_price = models.DecimalField("门票价格", max_digits=6, decimal_places=2, blank=True, null=True)
    images = models.JSONField("图片", default=list, blank=True)  # 存储图片URL数组
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    favorited_by = models.ManyToManyField(User, related_name='favorite_spots', verbose_name='收藏用户', blank=True)

    def __str__(self):
        return self.name