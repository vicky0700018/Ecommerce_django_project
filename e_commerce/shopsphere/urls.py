from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('product/', product, name='product'),
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
]
