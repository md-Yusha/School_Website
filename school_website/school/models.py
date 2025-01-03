from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Fee_Due = models.IntegerField(default=0)
    Class = models.CharField(max_length=3) 
    Father_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    alt_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    payment_mode = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username
    
