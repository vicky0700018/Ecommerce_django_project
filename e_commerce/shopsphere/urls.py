from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('product/', product, name='product'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('category/', category, name='category'),
    path('gallery/', gallery, name='gallery'),
    path('about-us/', about_us, name='about_us'),
    path('contact/', contact, name='contact'),
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('wishlist/', wishlist, name='wishlist'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('create-order/', create_order, name='create_order'),
    
    path('save-order/', save_order, name='save_order'),

    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('refund-policy/', refund_policy, name='refund_policy'),
    path('shipping-policy/', shipping_policy, name='shipping_policy'),
    path('terms-conditions/', terms_conditions, name='terms_conditions'),
    path('our-mission/', our_mission, name='our_mission'),
    path('our-vision/', our_vision, name='our_vision'),
    path('profile/', profile, name='profile'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('orders/', orders, name='orders'),
    
    # Inventory Management Routes
    path('inventory/', inventory_view, name='inventory'),
    path('inventory/update-stock/', update_stock, name='inventory_update_stock'),
    path('inventory/toggle-availability/', toggle_availability, name='inventory_toggle_availability'),

    # Order Listing Actions
    path('orders/<str:order_id>/', order_detail, name='order_detail'),
    path('orders/<str:order_id>/details/', order_details_api, name='order_details_api'),
    path('orders/<str:order_id>/invoice/', download_invoice, name='download_invoice'),
    path('orders/<str:order_id>/delete/', delete_order, name='delete_order'),

    # Feedback System Routes
    path('feedback/submit/', submit_feedback, name='submit_feedback'),
    path('admin-dashboard/feedback/', feedback_admin_view, name='feedback_admin'),
    path('admin-dashboard/feedback/<int:feedback_id>/approve/', approve_feedback, name='approve_feedback'),
    path('admin-dashboard/feedback/<int:feedback_id>/reject/', reject_feedback, name='reject_feedback'),

    # Cart & Wishlist Sync API Routes
    path('cart/sync/', sync_cart_api, name='sync_cart_api'),
    path('cart/get/', get_cart_api, name='get_cart_api'),
    path('wishlist/sync/', sync_wishlist_api, name='sync_wishlist_api'),
    path('wishlist/get/', get_wishlist_api, name='get_wishlist_api'),
]
