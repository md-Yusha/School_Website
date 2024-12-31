from django.urls import path
from . import views

urlpatterns = [
    path('bill-input/', views.bill_input, name='bill_input'),
    path('generate-bill/', views.generate_bill, name='generate_bill'),
    path('download-bill/', views.download_bill, name='download_bill'),
]