from django.contrib import admin
from .models import ScenicSpot

@admin.register(ScenicSpot)
class ScenicSpotAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'address', 'ticket_price', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'category')
        }),
        ('位置信息', {
            'fields': ('address', 'longitude', 'latitude')
        }),
        ('其他信息', {
            'fields': ('opening_hours', 'ticket_price', 'images')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
# Register your models here.
