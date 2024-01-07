from django.contrib import admin
from .models import Item, Price
# Register your models here.
# class PriceInline(admin.TabularInline):
#     model = Price
#     extra = 0
#     fields = ('price', 'currency', 'timestamp_display')
#     readonly_fields = ('timestamp_display',)
#     can_delete = False
#     verbose_name_plural = 'Prices'
#     show_change_link = False

#     def timestamp_display(self, obj):
#         return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

#     timestamp_display.short_description = 'Timestamp'

class PriceInline(admin.TabularInline):
    model = Price
    extra = 0
    fields = ('price', 'currency', 'timestamp')
    readonly_fields = ('timestamp',)
    can_delete = False
    verbose_name_plural = 'Prices'
    show_change_link = False
    
    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    timestamp_display.short_description = 'Timestamp'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [PriceInline]
    list_display = ('item_name', 'item_url', 'category')
    list_filter = ('category',)
    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return False
        return super().has_delete_permission(request, obj)
    
@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('price', 'timestamp', 'item')
    list_filter = ('timestamp', 'item__item_name')
