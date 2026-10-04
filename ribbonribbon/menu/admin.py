from django.contrib import admin
from django.utils.html import mark_safe
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    # 一覧表示に表示する項目
    list_display = [
        'id', 'name', 'quantity', 'condition', 'description', 
        'packaging_method', 'trade_preference', 'created_at', 'updated_at', 'picture_display'
    ]
    
    # 詳細画面に表示する項目
    fields = [
        'id', 'picture', 'name', 'quantity', 'condition', 'description',
        'packaging_method', 'trade_preference', 'created_at', 'updated_at'
    ]
    
    # 作成日時と更新日時を編集不可に設定
    readonly_fields = ['created_at', 'updated_at']

    # 画像をHTMLで表示するメソッドを作成
    def picture_display(self, obj):
        if obj.picture:
            return mark_safe(f'<img src="{obj.picture.url}" width="100" />')
        return "No image"
    
    picture_display.short_description = '出品画像'  # 表示名の設定
    
    # フィルターを追加（任意）
    list_filter = ['condition', 'trade_preference']

    # 検索バーに追加する項目
    search_fields = ['name', 'description']

    # 新規作成・編集画面でフィールドの順番を指定（任意）
    ordering = ['created_at']
