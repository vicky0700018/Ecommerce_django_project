from django.urls import path
from .views import *

urlpatterns = [

   path('', home, name='home'),
   path('register/', register, name='register'),
   path('verify-otp/', verify_otp, name='verify_otp'),
   path('resend-otp/', resend_otp, name='resend_otp'),
   path('login/', login, name='login'),
   path('logout/', logout, name='logout'),
]



