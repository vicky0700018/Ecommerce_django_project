from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import (
    CustomUser,
    OTP,
    Category,
    Product,
    Announcement,
    TeamMember,
    Gallery,
    ContactMessage,
    Order,
    Feedback,
    Cart,
    Wishlist,
    ContactPageConfiguration,
    Inventory
)

class CustomUserAdmin(UserAdmin):
    # Completely redefine fieldsets to move 'email'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Custom Profile Details', {'fields': ('email', 'full_name', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'city', 'pincode', 'profile_image', 'gender')}),
        ('Email Verification', {'fields': ('is_email_verified',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Create New User page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Details', {'fields': ('full_name', 'email', 'mobile_no', 'alternate_mobile_no', 'dob', 'address', 'city', 'pincode', 'profile_image', 'gender')}),
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
    list_display = ('name', 'sku', 'category', 'price', 'discount_price', 'stock', 'is_available', 'created_at')
    list_filter = ('is_available', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('sku', 'price', 'discount_price', 'stock', 'is_available')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text',)
    list_editable = ('is_active',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'role', 'description_snippet', 'image_preview')
    search_fields = ('employee_name', 'role', 'description')

    def description_snippet(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_snippet.short_description = 'Description'

    def image_preview(self, obj):
        if obj.employee_image:
            return mark_safe(f'<img src="{obj.employee_image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = 'Photo'


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'image_preview')
    search_fields = ('title',)
    list_filter = ('created_at',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'user',
        'amount',
        'payment_method',
        'payment_id',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at'
    )

    search_fields = (
        'order_id',
        'payment_id',
        'full_name',
        'email'
    )

    readonly_fields = (
        'order_id',
        'payment_id',
        'created_at'
    )


from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'stars', 'status_display', 'action_buttons')
    list_filter = ('rating', 'is_approved', 'is_rejected', 'created_at')
    search_fields = ('product__name', 'message')

    def product_name(self, obj):
        url = reverse('admin:shopsphere_feedback_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_name.short_description = 'PRODUCT NAME'
    product_name.admin_order_field = 'product__name'

    def stars(self, obj):
        return obj.rating
    stars.short_description = 'STARS'
    stars.admin_order_field = 'rating'

    def status_display(self, obj):
        if obj.is_approved:
            return 'Approved'
        elif obj.is_rejected:
            return 'Rejected'
        return 'Pending'
    status_display.short_description = 'STATUS'

    def action_buttons(self, obj):
        approve_url = reverse('admin:feedback_approve_custom', args=[obj.id])
        reject_url = reverse('admin:feedback_reject_custom', args=[obj.id])
        view_url = reverse('admin:feedback_view_custom', args=[obj.id])
        return format_html(
            '<a href="{}">View</a> | <a href="{}">Approve</a> | <a href="{}">Reject</a>',
            view_url, approve_url, reject_url
        )
    action_buttons.short_description = 'ACTION'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:feedback_id>/approve-custom/', self.admin_site.admin_view(self.approve_fb), name='feedback_approve_custom'),
            path('<int:feedback_id>/reject-custom/', self.admin_site.admin_view(self.reject_fb), name='feedback_reject_custom'),
            path('<int:feedback_id>/view-custom/', self.admin_site.admin_view(self.view_fb), name='feedback_view_custom'),
        ]
        return custom_urls + urls

    def approve_fb(self, request, feedback_id):
        fb = self.get_object(request, feedback_id)
        if fb:
            fb.is_approved = True
            fb.is_rejected = False
            fb.save()
            self.message_user(request, f"Feedback for {fb.product.name} approved.")
        return redirect('admin:shopsphere_feedback_changelist')

    def reject_fb(self, request, feedback_id):
        fb = self.get_object(request, feedback_id)
        if fb:
            fb.is_approved = False
            fb.is_rejected = True
            fb.save()
            self.message_user(request, f"Feedback for {fb.product.name} rejected.")
        return redirect('admin:shopsphere_feedback_changelist')

    def view_fb(self, request, feedback_id):
        fb = self.get_object(request, feedback_id)
        if fb:
            self.message_user(request, f"Message from {fb.user.full_name} ({fb.user.email}) regarding {fb.product.name}: {fb.message}")
        return redirect('admin:shopsphere_feedback_changelist')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'product__name')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'product__name')


@admin.register(ContactPageConfiguration)
class ContactPageConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'address', 'working_hours')
    
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_sku', 'get_stock', 'warehouse_location', 'last_restocked')
    search_fields = ('product__name', 'product__sku')
    list_filter = ('last_restocked', 'warehouse_location')
    list_editable = ('warehouse_location',)

    def get_sku(self, obj):
        return obj.product.sku
    get_sku.short_description = 'SKU'
    get_sku.admin_order_field = 'product__sku'

    def get_stock(self, obj):
        return obj.product.stock
    get_stock.short_description = 'STOCK'
    get_stock.admin_order_field = 'product__stock'



