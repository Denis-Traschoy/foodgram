from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'email', 'username', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_superuser']
    ordering = ['id']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Личная информация',
         {'fields': ('first_name', 'last_name', 'avatar')}
         ),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2',
            ),
        }),
    )
    search_fields = ['email', 'username', 'first_name', 'last_name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'author']
    search_fields = ['user__email', 'author__email']
    autocomplete_fields = ['user', 'author']
