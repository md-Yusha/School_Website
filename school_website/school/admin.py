from django.contrib import admin
from .models import UserProfile, Transactions
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Transactions)