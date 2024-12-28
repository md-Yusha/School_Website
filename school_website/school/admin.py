from django.contrib import admin

# Register your models here.
from .models import Student

# Register the Student model to appear in the admin panel
admin.site.register(Student)