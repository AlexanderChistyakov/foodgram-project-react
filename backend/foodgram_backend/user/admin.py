from django.contrib import admin
from user.models import Follow, User

admin.site.register(Follow)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
