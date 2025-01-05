from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)

from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    Name = forms.CharField(max_length=100, required=True, label='Full Name')
    email = forms.EmailField(max_length=100, required=True)
    Class = forms.CharField(max_length=3, required=True, label='Class')
    Fee_Due = forms.IntegerField(initial=0, required=False, label='Fee Due')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Create or update UserProfile
            try:
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'Name': self.cleaned_data.get('Name', user.username),
                        'email': self.cleaned_data.get('email', user.email),
                        'Class': self.cleaned_data.get('Class', ''),
                        'Fee_Due': self.cleaned_data.get('Fee_Due', 0)
                    }
                )
                
                if not created:
                    profile.Name = self.cleaned_data.get('Name', profile.Name)
                    profile.email = self.cleaned_data.get('email', profile.email)
                    profile.Class = self.cleaned_data.get('Class', profile.Class)
                    profile.Fee_Due = self.cleaned_data.get('Fee_Due', profile.Fee_Due)
                    profile.save()
            
            except Exception as e:
                logger.error(f"Error creating UserProfile: {e}")
                raise ValidationError(f"Could not create user profile: {e}")
        
        return user

class CustomUserChangeForm(UserChangeForm):
    Name = forms.CharField(max_length=100, required=True, label='Full Name')
    email = forms.EmailField(max_length=100, required=True)
    Class = forms.CharField(max_length=3, required=True, label='Class')
    Fee_Due = forms.IntegerField(initial=0, required=False, label='Fee Due')
    Father_name = forms.CharField(max_length=100, required=False, label='Father\'s Name')
    phone_number = forms.CharField(max_length=15, required=False, label='Phone Number')
    alt_number = forms.CharField(max_length=15, required=False, label='Alternate Number')
    address = forms.CharField(widget=forms.Textarea, required=False, label='Address')

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Update or create UserProfile
            try:
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'Name': self.cleaned_data.get('Name', user.username),
                        'email': self.cleaned_data.get('email', user.email),
                        'Class': self.cleaned_data.get('Class', ''),
                        'Fee_Due': self.cleaned_data.get('Fee_Due', 0),
                        'Father_name': self.cleaned_data.get('Father_name', ''),
                        'phone_number': self.cleaned_data.get('phone_number', ''),
                        'alt_number': self.cleaned_data.get('alt_number', ''),
                        'address': self.cleaned_data.get('address', '')
                    }
                )
                
                if not created:
                    profile.Name = self.cleaned_data.get('Name', profile.Name)
                    profile.email = self.cleaned_data.get('email', profile.email)
                    profile.Class = self.cleaned_data.get('Class', profile.Class)
                    profile.Fee_Due = self.cleaned_data.get('Fee_Due', profile.Fee_Due)
                    profile.Father_name = self.cleaned_data.get('Father_name', profile.Father_name)
                    profile.phone_number = self.cleaned_data.get('phone_number', profile.phone_number)
                    profile.alt_number = self.cleaned_data.get('alt_number', profile.alt_number)
                    profile.address = self.cleaned_data.get('address', profile.address)
                    profile.save()
            
            except Exception as e:
                logger.error(f"Error updating UserProfile: {e}")
                raise ValidationError(f"Could not update user profile: {e}")
        
        return user

class CreateUserProfileForm(forms.ModelForm):
    """
    Enhanced form for creating a user profile with comprehensive validation
    """
    # Personal Information
    Name = forms.CharField(
        max_length=100, 
        required=True, 
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control profile-name-input',
            'placeholder': 'Enter Full Name',
            'style': 'border-color: #4CAF50; font-weight: bold;'
        })
    )
    email = forms.EmailField(
        max_length=100, 
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control profile-email-input',
            'placeholder': 'Enter Email Address',
            'style': 'border-color: #2196F3;'
        })
    )

    # Academic Information
    Class = forms.CharField(
        max_length=3, 
        required=True, 
        label='Class',
        widget=forms.TextInput(attrs={
            'class': 'form-control profile-class-input',
            'placeholder': 'e.g., 10A',
            'style': 'border-color: #FF9800;'
        })
    )
    
    # Financial Information
    Fee_Due = forms.IntegerField(
        initial=0, 
        required=False, 
        label='Fee Due (₹)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control profile-fee-input',
            'placeholder': 'Total Fee Amount',
            'style': 'border-color: #9C27B0;'
        })
    )

    # Additional Details
    Father_name = forms.CharField(
        max_length=100, 
        required=False, 
        label='Father\'s Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control profile-father-input',
            'placeholder': 'Enter Father\'s Name',
            'style': 'border-color: #795548;'
        })
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=False, 
        label='Primary Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control profile-phone-input',
            'placeholder': 'Enter Primary Phone Number',
            'style': 'border-color: #3F51B5;'
        })
    )
    alt_number = forms.CharField(
        max_length=15, 
        required=False, 
        label='Alternate Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control profile-alt-phone-input',
            'placeholder': 'Enter Alternate Phone Number',
            'style': 'border-color: #FF5722;'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control profile-address-input',
            'placeholder': 'Enter Full Address',
            'rows': 3,
            'style': 'border-color: #009688;'
        }), 
        required=False, 
        label='Residential Address'
    )

    # Password fields for user creation
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control profile-password-input',
            'placeholder': 'Enter Password',
            'style': 'border-color: #673AB7;'
        }),
        required=True
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control profile-confirm-password-input',
            'placeholder': 'Confirm Password',
            'style': 'border-color: #673AB7;'
        }),
        required=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'Name', 'email', 'Class', 'Fee_Due', 
            'Father_name', 'phone_number', 'alt_number', 'address'
        ]

    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone_number(self):
        """
        Validate phone number format
        """
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone

    def clean(self):
        """
        Validate password fields
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError({
                'password2': "Passwords do not match."
            })

        # Password complexity validation
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError({
                    'password1': "Password must be at least 8 characters long."
                })
            if not any(char.isdigit() for char in password1):
                raise forms.ValidationError({
                    'password1': "Password must contain at least one digit."
                })
            if not any(char.isupper() for char in password1):
                raise forms.ValidationError({
                    'password1': "Password must contain at least one uppercase letter."
                })

        return cleaned_data

    def save(self, commit=True):
        """
        Custom save method with enhanced user and profile creation
        """
        try:
            # Create the UserProfile instance
            profile = super().save(commit=False)
            
            # Prepare user data
            username = self.cleaned_data['email'].split('@')[0]
            email = self.cleaned_data['email']
            password = self.cleaned_data['password1']
            name_parts = self.cleaned_data['Name'].split()
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name_parts[0] if name_parts else '',
                last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            )
            
            # Link profile to user
            profile.user = user
            
            if commit:
                profile.save()
                logger.info(f"UserProfile created successfully for {profile.Name}")
            
            return profile
        
        except Exception as e:
            logger.error(f"Error creating UserProfile: {e}")
            raise ValidationError(f"Could not create user profile: {e}")

    def __init__(self, *args, **kwargs):
        """
        Customize form initialization
        """
        super().__init__(*args, **kwargs)
        
        # Add custom help text and error messages
        self.fields['Name'].help_text = 'Enter your full name as it appears on official documents.'
        self.fields['email'].help_text = 'Enter a valid email address. This will be used for login.'
        self.fields['Class'].help_text = 'Enter your current class (e.g., 10A, 12B)'
        self.fields['phone_number'].help_text = 'Optional: Enter your primary contact number'
        
        # Mark required fields
        for field_name in ['Name', 'email', 'Class', 'password1', 'password2']:
            self.fields[field_name].required = True
            self.fields[field_name].widget.attrs['required'] = 'required'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    verbose_name_plural = 'Profile'
    
    # Enhanced fieldsets with styling and grouping
    fieldsets = (
        ('Personal Information', {
            'classes': ('collapse', 'wide', 'extrapretty'),
            'fields': (
                ('Name', 'Father_name'),
                ('email', 'Class')
            )
        }),
        ('Contact Details', {
            'classes': ('collapse', 'wide', 'extrapretty'),
            'fields': (
                ('phone_number', 'alt_number'),
                'address'
            )
        }),
        ('Financial Information', {
            'classes': ('collapse', 'wide', 'extrapretty'),
            'fields': (
                'Fee_Due',
            )
        })
    )

    # Custom styling for the inline
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Add custom CSS classes to form fields
        formset.form.base_fields['Name'].widget.attrs.update({
            'class': 'vTextField admin-user-name',
            'placeholder': 'Enter Full Name'
        })
        formset.form.base_fields['email'].widget.attrs.update({
            'class': 'vEmailField admin-user-email',
            'placeholder': 'Enter Email Address'
        })
        formset.form.base_fields['Class'].widget.attrs.update({
            'class': 'vTextField admin-user-class',
            'placeholder': 'e.g., 10A'
        })
        formset.form.base_fields['Fee_Due'].widget.attrs.update({
            'class': 'vIntegerField admin-user-fee',
            'placeholder': 'Total Fee Due'
        })
        
        return formset

class UserProfileAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for UserProfile
    """
    form = CreateUserProfileForm
    
    # Comprehensive list display
    list_display = (
        'profile_image_display',
        'Name', 
        'email', 
        'Class', 
        'Fee_Due', 
        'phone_number',
        'account_status'
    )
    
    # Search and filter capabilities
    search_fields = ['Name', 'email', 'Class', 'phone_number']
    list_filter = ['Class', 'Fee_Due']
    
    # Fieldsets with enhanced styling
    fieldsets = (
        ('Personal Information', {
            'classes': ('wide', 'extrapretty', 'collapse'),
            'fields': (
                ('Name', 'Father_name'),
                ('email', 'Class')
            )
        }),
        ('Contact Details', {
            'classes': ('wide', 'extrapretty', 'collapse'),
            'fields': (
                ('phone_number', 'alt_number'),
                'address'
            )
        }),
        ('Financial Information', {
            'classes': ('wide', 'extrapretty', 'collapse'),
            'fields': (
                'Fee_Due',
            )
        }),
        ('Authentication', {
            'classes': ('wide', 'extrapretty', 'collapse'),
            'fields': (
                'password1', 'password2'
            )
        })
    )
    
    # Add password fields to the form
    add_form = CreateUserProfileForm
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Use different form for adding and changing
        """
        if not obj:
            # Adding a new UserProfile
            return self.add_form
        
        # Editing an existing UserProfile
        return super().get_form(request, obj, **kwargs)
    
    def profile_image_display(self, obj):
        """
        Display a placeholder profile image
        """
        return mark_safe(
            f'<img src="/static/admin/img/default-profile.svg" '
            f'style="width: 50px; height: 50px; border-radius: 50%;" '
            f'alt="Profile Image">'
        )
    profile_image_display.short_description = 'Profile'
    
    def account_status(self, obj):
        """
        Display account status with color-coded badge
        """
        if obj.user.is_active:
            return mark_safe('<span style="color:green;">✓ Active</span>')
        return mark_safe('<span style="color:red;">✗ Inactive</span>')
    account_status.short_description = 'Status'

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = [UserProfileInline]
    
    # Comprehensive list display with styled columns
    list_display = (
        'display_full_details',  # Custom method to show all details
    )

    # Override list_filter to show necessary filters
    list_filter = (
        'is_active',          # Filter by account status
        'profile__Class'      # Filter by class
    )

    # Override search_fields to enable searching
    search_fields = (
        'username',           # Search by username
        'profile__Name',      # Search by student name
        'profile__Class'      # Search by class
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        if not obj:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)
    
    def get_fieldsets(self, request, obj=None):
        # Get the original fieldsets
        original_fieldsets = list(super().get_fieldsets(request, obj))
        
        # Safely modify fieldsets
        for fieldset in original_fieldsets:
            if fieldset and len(fieldset) > 1 and 'Personal info' in str(fieldset[0]):
                fieldset[1]['fields'] += (
                    'profile__Name', 
                    'profile__Class', 
                    'profile__Fee_Due'
                )
        
        return original_fieldsets
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure UserProfile is created/updated
        """
        # Save the User first
        super().save_model(request, obj, form, change)
        
        # Create or update UserProfile
        try:
            # Try to get existing profile or create a new one
            profile, created = UserProfile.objects.get_or_create(
                user=obj,
                defaults={
                    'Name': form.cleaned_data.get('Name', obj.username),
                    'email': form.cleaned_data.get('email', obj.email),
                    'Class': form.cleaned_data.get('Class', ''),
                    'Fee_Due': form.cleaned_data.get('Fee_Due', 0)
                }
            )
            
            # If profile exists but not created, update it
            if not created:
                profile.Name = form.cleaned_data.get('Name', profile.Name)
                profile.email = form.cleaned_data.get('email', profile.email)
                profile.Class = form.cleaned_data.get('Class', profile.Class)
                profile.Fee_Due = form.cleaned_data.get('Fee_Due', profile.Fee_Due)
                profile.save()
        
        except Exception as e:
            # Log the error or handle it appropriately
            logger.error(f"Error creating/updating UserProfile: {e}")
            raise ValidationError(f"Could not create user profile: {e}")
    
    def display_full_details(self, obj):
        try:
            # Retrieve UserProfile details
            profile = obj.profile
            
            # Construct a comprehensive display string with HTML styling
            details = [
                f"<strong>Username:</strong> {obj.username}",
                f"<strong>Name:</strong> {profile.Name}",
                f"<strong>Class:</strong> {profile.Class}",
                f"<strong>Fee Due:</strong> ₹{profile.Fee_Due}",
                f"<strong>Email:</strong> {profile.email}",
                f"<strong>Active:</strong> {'Yes' if obj.is_active else 'No'}"
            ]
            
            # Return a formatted HTML string
            return ' | '.join(details)
        
        except UserProfile.DoesNotExist:
            # Fallback if no profile exists
            return f"<strong>Username:</strong> {obj.username} (No Profile)"
    
    display_full_details.short_description = 'User Details'
    display_full_details.allow_tags = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

# Function to register the custom admin
def register_user_admin(admin_site):
    try:
        # Unregister the existing User admin
        admin_site.unregister(User)
    except admin.sites.NotRegistered:
        # If not registered, it's fine to continue
        pass
    
    # Register the custom User admin
    admin_site.register(User, CustomUserAdmin)

# Register the UserProfile admin
def register_userprofile_admin(admin_site):
    try:
        admin_site.unregister(UserProfile)
    except admin.sites.NotRegistered:
        pass
    
    admin_site.register(UserProfile, UserProfileAdmin)

# Export the admin class for direct import if needed
__all__ = ['CreateUserProfileForm', 'UserProfileAdmin', 'register_userprofile_admin']
