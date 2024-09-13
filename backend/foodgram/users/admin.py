from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import FollowUser

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'avatar'
    )
    list_editable = (
        'is_staff',
    )
    search_fields = ('email', 'username')
    list_filter = ('username', 'is_staff')
    list_display_links = ('username',)


@admin.register(FollowUser)
class FollowUserAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user'
    )
    list_editable = ('user',)
    search_fields = ('author__username',)
    list_filter = ('author', 'user')
