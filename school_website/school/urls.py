from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginUser, name='login'),
    path('register/', views.registerUser, name='register'),
    path('dashboard/<str:username>/', views.dashboard, name='dashboard'),
    path('logout/', views.logoutUser, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.change_password, name='forgot_password'),
    path('otp/', views.otp_api, name='otp_api'),
    
    # Payment and transaction related URLs
    path('create_order/', views.create_order, name='create_order'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('update_fee/', views.update_fee, name='update_fee'),
    path('download_receipt/<str:transaction_id>/', views.download_receipt, name='download_receipt'),
]