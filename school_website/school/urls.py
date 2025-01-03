from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerUser,name='register'),
    path('otp_api/',views.otp_api,name='otp_api'),
    path('change_password/',views.change_password,name='change_password'),
    path('create_order/',views.create_order,name='create_order'),
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    path('dashboard/<str:username>/',views.dashboard,name='dashboard'),
]