from django.db import models
import uuid

class Page(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name="商品ID")
    picture = models.ImageField(
        upload_to='menu/picture/', blank=True, null=True, verbose_name="出品画像")

    name = models.CharField(max_length=100, verbose_name="出品グッズ名", default="未設定のグッズ名")
    quantity = models.PositiveIntegerField(verbose_name="個数", default=1)
    CONDITION_CHOICES = [
        ('new', '新品'),
        ('like_new', '新品同様'),
        ('good', '良好'),
        ('fair', 'やや傷あり'),
        ('poor', '悪い'),
    ]
    condition = models.CharField(
        max_length=10, choices=CONDITION_CHOICES, default='new', verbose_name="グッズの状態")
    description = models.TextField(max_length=2000, verbose_name="出品グッズの説明", default="説明がありません")
    packaging_method = models.TextField(verbose_name="梱包方法", default="簡易包装")
    TRADE_CHOICES = [
        ('exchange', '交換'),
        ('purchase', '買取り'),
    ]
    trade_preference = models.CharField(
        max_length=10, choices=TRADE_CHOICES, default='purchase', verbose_name="ご希望のお取引")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    wanted_item_name = models.CharField(max_length=100, verbose_name="希望グッズ名", default="未設定の希望グッズ名")
    wanted_item_details = models.TextField(max_length=2000, verbose_name="希望グッズの詳細", default="希望内容がありません")
    price = models.PositiveIntegerField(verbose_name="価格", default=0)

    def __str__(self):
        return self.name