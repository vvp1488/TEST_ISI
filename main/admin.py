from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Thread, Message
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants')


class UserAdminWithToken(UserAdmin):
    readonly_fields = ('token', )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Token"),{"fields": ("token",)}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    def token(self, obj):
        try:
            token = AccessToken.for_user(obj)
            return str(token)
        except:
            return ('N/A')


admin.site.unregister(User)
admin.site.register(User, UserAdminWithToken)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message)