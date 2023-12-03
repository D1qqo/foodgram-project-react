from django.contrib import admin

from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    """Класс админки пользователей."""
    list_display = ('email', 'username', 'first_name')
    list_filter = ('email', 'username', 'first_name')


class SubscribeAdmin(admin.ModelAdmin):
    """Класс админки подписок."""
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
