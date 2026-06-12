from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Completely redefine fieldsets to move 'email'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Custom Profile Details', {'fields': ('email', 'full_name', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'profile_image', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Create New User page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Details', {'fields': ('full_name', 'email', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'profile_image', 'gender')}),
    )
    
    list_display = ('username', 'email', 'full_name', 'mobile_no', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)
