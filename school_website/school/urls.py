from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('students/', views.student_list, name='student_list'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.student_logout, name='student_logout'),
]