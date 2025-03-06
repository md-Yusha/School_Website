from django.contrib import admin
from django.shortcuts import render
from .models import UserProfile, Transactions
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html

admin.site.site_header = "\n"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the School Admin"

class AmountRangeFilter(SimpleListFilter):
    title = 'Amount Range'
    parameter_name = 'amount_range'

    def lookups(self, request, model_admin):
        return (
            ('0-100', '0 - 100'),
            ('100-500', '100 - 500'),
            ('500-1000', '500 - 1000'),
            ('1000+', '1000+'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value == '0-100':
                return queryset.filter(Fee_Due__gte=0, Fee_Due__lte=100)
            elif value == '100-500':
                return queryset.filter(Fee_Due__gte=100, Fee_Due__lte=500)
            elif value == '500-1000':
                return queryset.filter(Fee_Due__gte=500, Fee_Due__lte=1000)
            elif value == '1000+':
                return queryset.filter(Fee_Due__gte=1000)
        return queryset

def add_fee_due(modeladmin, request, queryset):
    usrs = []
    for q in queryset:
        usrs.append(q.user)
    return render(request, 'admin/fee_due_form.html', {'users': usrs})

add_fee_due.short_description = "Set Fee Due for selected users"

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'email']
    list_display = ['user', 'Name', 'email', 'Fee_Due', 'Class']
    list_filter = (AmountRangeFilter,)
    actions = [add_fee_due] 

class TransactionsAdmin(admin.ModelAdmin):
    search_fields = ['transaction_id', 'user__username', 'date']
    list_display = ['user', 'amount', 'date', 'transaction_id', 'status', 'payment_mode', 'received_by', 'download_receipt']
    list_filter = ['status', 'payment_mode', 'date']
    raw_id_fields = ['user']
    
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj is None:  # This is an add form
            if 'payment_mode' in fields:
                # Only hide transaction_id for cash payments
                if 'transaction_id' in fields and request.POST.get('payment_mode') == 'Cash':
                    fields.remove('transaction_id')
        return fields

    def save_model(self, request, obj, form, change):
        if not change:  # This is a new transaction being added
            # Set received_by to current admin's username
            obj.received_by = request.user.username
            
            # Only generate transaction ID for cash payments
            if obj.payment_mode == 'Cash':
                from datetime import datetime
                cash_trans_id = f"CASH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                obj.transaction_id = cash_trans_id
            # For online payments, ensure transaction_id is provided
            elif not obj.transaction_id:
                from datetime import datetime
                obj.transaction_id = f"ONLINE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update user's fee due on successful transaction
        if obj.status:
            user_profile = UserProfile.objects.filter(user=obj.user).first()
            if user_profile:
                user_profile.Fee_Due -= obj.amount
                user_profile.Fee_Due = max(0, user_profile.Fee_Due)
                user_profile.save()
                messages.success(
                    request,
                    f"User {user_profile.Name}'s fee has been updated successfully."
                )
        
        super().save_model(request, obj, form, change)

    def download_receipt(self, obj):
        if obj.status:  # Only show download button for successful transactions
            return format_html(
                '<a class="button" href="/download_receipt/{transaction_id}/" target="_blank">Download Receipt</a>',
                transaction_id=obj.transaction_id
            )
        return "N/A"
    download_receipt.short_description = 'Receipt'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transactions, TransactionsAdmin)
