from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.apps import apps
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
import numpy as np
import logging

# Import custom admin configurations
from .user_admin import CustomUserAdmin, UserProfileInline, register_userprofile_admin, CreateUserProfileForm
from .transaction_admin import CustomTransactionsAdmin
from .models import UserProfile, Transactions

# Configure logging
logger = logging.getLogger(__name__)

# Middleware to add comprehensive dashboard statistics
class DashboardStatisticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Comprehensive dashboard statistics
        request.dashboard_stats = {
            # Financial Metrics
            'total_revenue': Transactions.objects.filter(status=True).aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'monthly_revenue': Transactions.objects.filter(
                status=True,
                date__month=timezone.now().month,
                date__year=timezone.now().year
            ).aggregate(total=Sum('amount'))['total'] or 0,
            
            # User Metrics
            'total_users': User.objects.count(),
            'active_users': UserProfile.objects.filter(
                user__last_login__gte=timezone.now() - timedelta(days=30)
            ).count(),
            
            # Transaction Metrics
            'total_transactions': Transactions.objects.count(),
            'pending_transactions': Transactions.objects.filter(
                status=False
            ).count(),
            
            # Fee Metrics
            'total_fee_due': UserProfile.objects.aggregate(
                total_fee=Sum('Fee_Due')
            )['total_fee'] or 0,
            'fee_collected': Transactions.objects.filter(status=True).aggregate(
                collected=Sum('amount')
            )['collected'] or 0,
        }
        
        response = self.get_response(request)
        return response

# Create a custom admin site with enhanced statistics display
from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.views import LoginView

class CustomAdminSite(AdminSite):
    site_header = 'School Management Dashboard'
    site_title = 'School Management Admin'
    index_title = 'Dashboard Insights'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def logout(self, request):
        """
        Custom logout method for admin site
        """
        logout(request)
        return redirect('admin:login')

    def get_urls(self):
        """
        Add custom logout URL to admin site
        """
        urls = super().get_urls()
        custom_urls = [
            path('logout/', self.logout, name='logout'),
        ]
        return custom_urls + urls

# Create a custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

# Centralized registration function
def register_all_models():
    # Unregister models from both admin sites first
    try:
        # Unregister existing models
        try:
            admin.site.unregister(User)
        except admin.sites.NotRegistered:
            pass
        
        try:
            admin.site.unregister(UserProfile)
        except admin.sites.NotRegistered:
            pass
        
        try:
            admin.site.unregister(Transactions)
        except admin.sites.NotRegistered:
            pass
        
        # Register models
        admin.site.register(User, CustomUserAdmin)
        admin.site.register(Transactions, CustomTransactionsAdmin)
        
        # Register UserProfile with the new admin
        register_userprofile_admin(admin.site)
        
        # Do the same for custom admin site
        custom_admin_site.register(User, CustomUserAdmin)
        custom_admin_site.register(Transactions, CustomTransactionsAdmin)
        register_userprofile_admin(custom_admin_site)
        
        logger.info("Models registered successfully on both admin sites.")
    
    except Exception as e:
        logger.error(f"Error during model registration: {e}")
        print(f"Error during model registration: {e}")

# Initial registration
register_all_models()
