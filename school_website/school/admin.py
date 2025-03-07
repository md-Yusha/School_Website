from django.contrib import admin
from django.shortcuts import render
from .models import UserProfile, Transactions, PaymentCategory
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from django import forms
from django.db.models import Q
from datetime import datetime, timedelta

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
    search_fields = ('Name', 'registration_number', 'Class', 'phone_number', 'email')
    list_display = ('Name', 'registration_number', 'Class', 'phone_number', 'email', 'Fee_Due', 'view_transactions')
    list_filter = ('Class',)
    ordering = ('Name',)
    actions = [add_fee_due]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('transactions/<int:user_id>/', self.admin_site.admin_view(self.view_transaction_history), name='user-transactions'),
        ]
        return custom_urls + urls

    def view_transactions(self, obj):
        return format_html(
            '<a class="button" href="{}">View Transactions</a>',
            f'/admin/school/userprofile/transactions/{obj.user.id}/'
        )
    view_transactions.short_description = 'Transactions'

    def view_transaction_history(self, request, user_id):
        user_profile = UserProfile.objects.get(user_id=user_id)
        
        # Get all transactions for this user
        all_transactions = Transactions.objects.filter(user_id=user_id).order_by('-date')
        
        # Get one-time fees (only admission and application fees)
        one_time_fees = all_transactions.filter(
            categories__category__in=['admission', 'application']
        ).distinct()

        # Get all monthly fees (tuition)
        monthly_fees = all_transactions.filter(
            categories__category='tuition'
        ).order_by('-date')

        # Create a list of months with payment status
        current_date = datetime.now()
        months = []
        for i in range(12):
            month_date = current_date - timedelta(days=30*i)
            month_str = month_date.strftime('%B %Y')
            
            # Get all transactions for this month
            month_transactions = all_transactions.filter(
                date__year=month_date.year,
                date__month=month_date.month,
                status=True  # Only count successful transactions
            )
            
            # Calculate total amount for this month (all categories)
            total_amount = sum(trans.total_amount for trans in month_transactions)
            
            # Get the latest transaction for this month
            latest_transaction = month_transactions.first()
            
            months.append({
                'month': month_str,
                'paid': bool(latest_transaction),
                'transaction': latest_transaction,
                'total_amount': total_amount
            })

        context = {
            'user_profile': user_profile,
            'one_time_fees': one_time_fees,
            'months': months,
            'opts': self.model._meta,
            'all_transactions': all_transactions,
        }
        return render(request, 'admin/transaction_history.html', context)

class PaymentCategoryInline(admin.TabularInline):
    model = PaymentCategory
    extra = 1
    fields = ('category', 'amount', 'description')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['description'].widget = forms.Textarea(attrs={'rows': 1})
        return formset

class TransactionsAdminForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.pk:  # If this is an existing transaction
            return cleaned_data
        return cleaned_data

class TransactionsAdmin(admin.ModelAdmin):
    form = TransactionsAdminForm
    inlines = [PaymentCategoryInline]
    search_fields = ['transaction_id', 'user__username', 'date']
    list_display = ['get_student_name', 'total_amount', 'date', 'time', 'transaction_id', 'status', 'payment_mode', 'received_by', 'download_receipt']
    list_filter = ['status', 'payment_mode', 'date']
    raw_id_fields = ['user']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/transaction_admin.js',)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj is None:  # This is an add form
            if 'payment_mode' in fields:
                if 'transaction_id' in fields and request.POST.get('payment_mode') == 'Cash':
                    fields.remove('transaction_id')
            if 'total_amount' in fields:
                fields.remove('total_amount')
        return fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        total = sum(category.amount for category in obj.categories.all())
        obj.total_amount = total
        obj.save()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.received_by = request.user.username
            obj.total_amount = 0
            
            if obj.payment_mode == 'Cash':
                from datetime import datetime
                cash_trans_id = f"CASH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                obj.transaction_id = cash_trans_id
            elif not obj.transaction_id:
                from datetime import datetime
                obj.transaction_id = f"ONLINE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        super().save_model(request, obj, form, change)

        if obj.status:
            user_profile = UserProfile.objects.filter(user=obj.user).first()
            if user_profile:
                user_profile.Fee_Due -= obj.total_amount
                user_profile.Fee_Due = max(0, user_profile.Fee_Due)
                user_profile.save()
                messages.success(
                    request,
                    f"User {user_profile.Name}'s fee has been updated successfully."
                )

    def download_receipt(self, obj):
        if obj.status:
            return format_html(
                '<a class="button" href="/download_receipt/{transaction_id}/" target="_blank">Download Receipt</a>',
                transaction_id=obj.transaction_id
            )
        return "N/A"
    download_receipt.short_description = 'Receipt'

    def get_student_name(self, obj):
        return obj.user.profile.Name
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'user__profile__Name'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transactions, TransactionsAdmin)
admin.site.register(PaymentCategory)
