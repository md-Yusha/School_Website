from django.contrib import admin
from django.contrib.admin import AdminSite
from django.conf import settings

class CustomAdminSite(AdminSite):
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE

custom_admin_site = CustomAdminSite(name='custom_admin')
