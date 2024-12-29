from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.loginUser,name='login'),
    path('register/',views.registerUser,name='register'),
    path('otp_api/',views.otp_api,name='otp_api'),
    path('dashboard/<str:username>/',views.dashboard,name='dashboard'),
]