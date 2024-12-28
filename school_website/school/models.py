from django.db import models

# Create your models here.
from django.db import models

class Student(models.Model):
    usn = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100)
    mothers_name = models.CharField(max_length=100)
    fathers_phone = models.CharField(max_length=15)
    mothers_phone = models.CharField(max_length=15)
    address = models.TextField()
    aadhar_number = models.CharField(max_length=12, unique=True)
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name