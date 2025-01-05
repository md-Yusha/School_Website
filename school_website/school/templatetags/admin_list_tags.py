from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def display_admin_field(obj, field_name):
    """
    Safely display a field value for admin list view
    """
    try:
        # Get the method or attribute
        method = getattr(obj, field_name, None)
        
        # If it's a method, call it
        if callable(method):
            value = method()
        else:
            value = method
        
        # Convert to string and mark as safe
        return mark_safe(str(value))
    except Exception:
        return ''
