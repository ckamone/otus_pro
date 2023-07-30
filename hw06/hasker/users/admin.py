from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# # Define an inline admin descriptor for Custom model
# # which acts a bit like a singleton
class CustomInline(admin.StackedInline):
    model = CustomUser
    can_delete = False
    verbose_name_plural = "Avatars"


# # Define a new User admin
class CustomizedUserAdmin(UserAdmin):
    inlines = [CustomInline]


# # Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)