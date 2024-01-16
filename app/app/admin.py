from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Item, Price, UserSettings


class PriceInline(admin.TabularInline):
    """
    Create an inline for the Price model to display the price history of an item.
    Within the item panel, we can see the price history of the item.
    """

    model = Price
    extra = 0
    fields = ("price", "currency", "timestamp")
    readonly_fields = ("timestamp",)
    can_delete = False
    verbose_name_plural = "Prices"
    show_change_link = False

    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    timestamp_display.short_description = "Timestamp"


class UserSettingsInLine(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = "User Settings"
    fk_name = "user"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [PriceInline]
    list_display = ("item_name", "item_url", "category")
    list_filter = ("category",)

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
    list_display = ("price", "timestamp", "item")
    list_filter = ("timestamp", "item__item_name")


class UserAdmin(admin.ModelAdmin):
    inlines = [UserSettingsInLine]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
