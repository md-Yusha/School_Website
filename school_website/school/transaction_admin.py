from django.contrib import admin
from .models import Transactions, UserProfile
import numpy as np

class CustomTransactionsAdmin(admin.ModelAdmin):
    def student_name(self, obj):
        try:
            return obj.user.profile.Name
        except (UserProfile.DoesNotExist, AttributeError):
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
    student_name.short_description = 'Student Name'

    def student_class(self, obj):
        try:
            return obj.user.profile.Class
        except (UserProfile.DoesNotExist, AttributeError):
            return ''
    student_class.short_description = 'Class'

    def safe_amount(self, obj):
        return 0 if obj.amount is None or (isinstance(obj.amount, float) and np.isnan(obj.amount)) else obj.amount
    safe_amount.short_description = 'Amount (₹)'

    def status_display(self, obj):
        return 'Completed' if obj.status else 'Pending'
    status_display.short_description = 'Payment Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__profile')

    # Comprehensive list display with necessary transaction details
    list_display = (
        'transaction_id',     # Unique transaction identifier
        'student_name',       # Full name of the student
        'student_class',      # Student's class
        'safe_amount',        # Transaction amount
        'date',               # Date of transaction
        'payment_mode',       # Payment method
        'status_display'      # Transaction status
    )

    # Focused search fields
    search_fields = (
        'transaction_id',          # Search by transaction ID
        'user__username',          # Search by username
        'user__profile__Name',     # Search by student name
        'user__profile__Class'     # Search by student class
    )

    # Relevant list filters
    list_filter = (
        'status',                  # Filter by transaction status
        'payment_mode',            # Filter by payment method
        'user__profile__Class'     # Filter by student class
    )

    # Simplified fieldsets for detail view
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'transaction_id', 
                'user',             # Shows full user details
                'amount', 
                'status', 
                'payment_mode'
            )
        }),
        ('Transaction Date', {
            'fields': (
                'date',
            )
        })
    )

    # Exclude the date field from editable fields
    exclude = ('date',)

    # Customize ordering
    ordering = ('-date',)  # Most recent transactions first

    # Read-only fields
    readonly_fields = ('date', 'transaction_id')

    # Custom form to handle display of additional user information
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Add a method to display user profile information
        def get_user_profile_info(self):
            if self.instance and self.instance.user:
                try:
                    profile = self.instance.user.profile
                    return f"Name: {profile.Name}, Class: {profile.Class}"
                except UserProfile.DoesNotExist:
                    return "No profile information available"
            return "No user selected"
        
        # Add a display-only field for user profile information
        form.user_profile_info = property(get_user_profile_info)
        
        return form

# Function to register the transaction admin
def register_transaction_admin(admin_site):
    # Remove any existing registration first
    try:
        admin_site.unregister(Transactions)
    except admin.sites.NotRegistered:
        pass
    
    # Register with the custom admin
    admin_site.register(Transactions, CustomTransactionsAdmin)

# Export the admin class for direct import if needed
__all__ = ['CustomTransactionsAdmin', 'register_transaction_admin']
