from django.contrib import admin

from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    """Админка пользователей."""
    list_display = ('email', 'username', 'first_name')
    list_filter = ('email', 'username', 'first_name')


class SubscribeAdmin(admin.ModelAdmin):
    """Админка подписок."""
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
