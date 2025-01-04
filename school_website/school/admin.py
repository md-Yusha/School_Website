from django.contrib import admin
from django.shortcuts import render
from .models import UserProfile, Transactions
from django.contrib.admin import SimpleListFilter
from django.contrib import messages

admin.site.site_header = "School Admin"
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
    list_display = ['user', 'amount', 'date', 'transaction_id', 'status', 'payment_mode']
    list_filter = ['status', 'payment_mode', 'date']
    raw_id_fields = ['user']
    def save_model(self, request, obj, form, change):
        """
        Override save_model to perform additional actions when a transaction is saved.
        """
        # Save the transaction first
        super().save_model(request, obj, form, change)

        # Perform custom logic: Update user's fee due on successful transaction
        if obj.status == True:  # Assuming 'success' is the status for a successful transaction
            user_profile = UserProfile.objects.filter(user=obj.user).first()
            if user_profile:
                user_profile.Fee_Due -= obj.amount  # Deduct transaction amount from Fee Due
                user_profile.Fee_Due = max(0, user_profile.Fee_Due)  # Ensure Fee Due is not negative
                user_profile.save()
                messages.success(
                    request,
                    f"User {user_profile.Name}'s fee has been updated successfully."
                )

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transactions, TransactionsAdmin)
