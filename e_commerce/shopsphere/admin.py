from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import CustomUser, OTP, Category, Product, Announcement

class CustomUserAdmin(UserAdmin):
    # Completely redefine fieldsets to move 'email'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Custom Profile Details', {'fields': ('email', 'full_name', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'profile_image', 'gender')}),
        ('Email Verification', {'fields': ('is_email_verified',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Create New User page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Details', {'fields': ('full_name', 'email', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'profile_image', 'gender')}),
    )
    
    list_display = ('username', 'email', 'full_name', 'mobile_no', 'is_staff', 'email_verification_status')
    list_filter = ('is_email_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name', 'mobile_no')
    
    def email_verification_status(self, obj):
        """Display email verification status with color"""
        if obj.is_email_verified:
            return mark_safe(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        else:
            return mark_safe(
                '<span style="color: red; font-weight: bold;">✗ Not Verified</span>'
            )
    email_verification_status.short_description = 'Email Status'


class OTPAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'code', 'created_at', 'expires_at', 'is_verified', 'status')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('code', 'created_at', 'expires_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('OTP Details', {
            'fields': ('code', 'created_at', 'expires_at', 'is_verified')
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def status(self, obj):
        """Display OTP status"""
        if obj.is_verified:
            return mark_safe(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        elif obj.is_expired():
            return mark_safe(
                '<span style="color: red; font-weight: bold;">✗ Expired</span>'
            )
        else:
            return mark_safe(
                '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
            )
    status.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Prevent manual OTP creation from admin"""
        return False


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_class', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'stock', 'is_available', 'created_at')
    list_filter = ('is_available', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'discount_price', 'stock', 'is_available')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text',)
    list_editable = ('is_active',)



