"""
URL configuration for school_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from school.admin import custom_admin_site
from school import views

urlpatterns = [
    # Use both default and custom admin sites
    path('admin/', admin.site.urls),
    path('custom-admin/', custom_admin_site.urls),
    
    # Other existing URL patterns
    path('grappelli/', include('grappelli.urls')),
    path('',views.home,name='home'),
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerUser,name='register'),
    path('otp_api/',views.otp_api,name='otp_api'),
    path('change_password/',views.change_password,name='change_password'),
    path('create_order/',views.create_order,name='create_order'),
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    path('update_fee/',views.update_fee,name='update_fee'),
    path('download-receipt/<str:transaction_id>/', views.download_receipt, name='download_receipt'),
    path('dashboard/<str:username>/',views.dashboard,name='dashboard'),
]
