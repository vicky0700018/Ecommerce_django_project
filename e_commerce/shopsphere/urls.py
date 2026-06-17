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
]



