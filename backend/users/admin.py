from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# from django.contrib.auth.admin import UserAdmin

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
        'avatar',
    )
    list_editable = (
        'is_staff',
    )
    search_fields = ('email', 'username',)
    list_filter = ('username', 'is_staff',)
    list_display_links = ('username',)

    def save_model(self, request, obj, form, change):
        """
        Prevent user's password to be saved without hashing
        in DB if user is created by admin.
        """
        if obj.password:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(FollowUser)
class FollowUserAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )
    list_editable = ('user',)
    search_fields = ('author__username',)
    list_filter = ('author', 'user',)
