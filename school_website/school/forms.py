from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile
import re

class UserRegistrationForm(forms.ModelForm):
    """
    Form for user registration with comprehensive validation
    """
    username = forms.CharField(
        max_length=50,
        help_text='Choose a unique username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )
    email = forms.EmailField(
        max_length=100,
        help_text='Enter a valid email address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        }),
        help_text='Password must be at least 8 characters long, contain uppercase, lowercase, digit, and special character'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        """
        Validate username
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        """
        Validate email
        """
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_password1(self):
        """
        Validate password strength
        """
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")
        
        return password

    def clean(self):
        """
        Validate password confirmation
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError({
                'password2': "Passwords do not match."
            })
        
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    """
    Form for creating and updating user profile
    """
    Name = forms.CharField(
        max_length=100,
        help_text='Enter full name as on official documents',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        max_length=100,
        help_text='Enter a valid email address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    Class = forms.CharField(
        max_length=3,
        help_text='Enter current class (e.g., 10A)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Class'
        })
    )
    Father_name = forms.CharField(
        max_length=100,
        required=False,
        help_text='Enter father\'s name (optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Father\'s Name'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Enter primary contact number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    alt_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Enter alternate contact number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Alternate Phone Number'
        })
    )
    address = forms.CharField(
        required=False,
        help_text='Enter full residential address',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Residential Address',
            'rows': 3
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'Name', 'email', 'Class', 
            'Father_name', 'phone_number', 
            'alt_number', 'address'
        ]

    def clean_phone_number(self):
        """
        Validate phone number format
        """
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone

    def clean_alt_number(self):
        """
        Validate alternate phone number format
        """
        phone = self.cleaned_data.get('alt_number')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Alternate phone number must contain only digits.")
        return phone
