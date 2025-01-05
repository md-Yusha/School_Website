from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings

from .models import UserProfile, Transactions
from .forms import UserRegistrationForm, UserProfileForm

import logging
import re
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    """
    Render the home page
    """
    return render(request, 'index.html', {"user": str(request.user)})

def validate_password_strength(password):
    """
    Validate password strength
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def send_otp(email, action='register'):
    """
    Send OTP to user's email
    """
    try:
        # Use Django's email sending capabilities
        from django.core.mail import send_mail
        
        # Generate secure OTP
        otp = secrets.token_urlsafe(6)[:6].upper()
        
        # Compose email
        subject = 'OTP for School Management System'
        message = f'Your OTP for {action} is: {otp}. This OTP is valid for 10 minutes.'
        
        # Send email
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            [email], 
            fail_silently=False
        )
        
        return otp
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return None

def loginUser(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'{user.username} Login successful.')
            return redirect(f'/dashboard/{user.username}')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'student_dash/login.html')

@login_required
def dashboard(request, username):
    """
    User dashboard with enhanced security
    """
    if not request.user.is_authenticated or str(request.user) != username:
        messages.error(request, 'Unauthorized access.')
        return redirect('login')
    
    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
        
        user_data = {
            'username': user.username,
            'email': user_profile.email,
            'name': user_profile.Name,
            'class': user_profile.Class,
            'father_name': user_profile.Father_name,
            'phone_number': user_profile.phone_number,
            'alt_number': user_profile.alt_number,
            'address': user_profile.address,
            'fee_due': user_profile.Fee_Due,
        }
        
        transactions = Transactions.objects.filter(user=user).order_by('-date')
        
        return render(request, 'student_dash/dashboard.html', {
            "student": user_data,
            'transactions': transactions
        })
    
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'User profile not found.')
        return redirect('login')

def registerUser(request):
    """
    User registration view with enhanced validation
    """
    if request.method == 'POST':
        # Validate form data
        form_data = request.POST
        
        # Validate email
        try:
            validate_email(form_data.get('email'))
        except ValidationError:
            messages.error(request, 'Invalid email address.')
            return render(request, 'student_dash/register.html')
        
        # Check password strength
        password = form_data.get('password')
        is_strong, password_error = validate_password_strength(password)
        if not is_strong:
            messages.error(request, password_error)
            return render(request, 'student_dash/register.html')
        
        # Check OTP
        if 'otp' not in request.session or 'otp_created_at' not in request.session:
            messages.error(request, 'OTP verification required.')
            return render(request, 'student_dash/register.html')
        
        if str(form_data.get('otp')) != str(request.session['otp']):
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'student_dash/register.html')
        
        # Check OTP expiry
        otp_created_time = datetime.fromisoformat(request.session['otp_created_at'])
        if datetime.now() - otp_created_time > timedelta(minutes=10):
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            messages.error(request, 'OTP has expired.')
            return render(request, 'student_dash/register.html')
        
        # Check existing users
        email = form_data.get('email')
        username = form_data.get('username')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'student_dash/register.html')
        
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'student_dash/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            UserProfile.objects.create(
                user=user,
                Name=form_data.get('name'),
                email=email,
                Class=form_data.get('class'),
                Father_name=form_data.get('father_name'),
                phone_number=form_data.get('phone_number'),
                alt_number=form_data.get('alt_number'),
                address=form_data.get('address')
            )
            
            # Clear OTP session
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            messages.error(request, 'An error occurred during registration.')
    
    return render(request, 'student_dash/register.html')

def otp_api(request):
    """
    Generate and send OTP
    """
    if request.method == "POST":
        try:
            data = request.POST
            email = data.get('email')
            action = data.get('action', 'register')
            
            # Validate email
            validate_email(email)
            
            # Check if email exists for forgot password
            if action == 'forgot' and not UserProfile.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email not found!'}, status=400)
            
            # Generate and send OTP
            otp = send_otp(email, action)
            
            if otp:
                request.session['otp'] = otp
                request.session['otp_created_at'] = datetime.now().isoformat()
                request.session.modified = True
                
                return JsonResponse({'message': 'OTP sent!'}, status=201)
            else:
                return JsonResponse({'message': 'Failed to send OTP!'}, status=500)
        
        except ValidationError:
            return JsonResponse({'message': 'Invalid email address!'}, status=400)
        except Exception as e:
            logger.error(f"OTP API error: {e}")
            return JsonResponse({'message': 'An error occurred!'}, status=500)
    
    return JsonResponse({'message': 'Invalid request!'}, status=400)

def change_password(request):
    """
    Password change view with OTP verification
    """
    if request.method == 'POST':
        try:
            data = request.POST
            email = data.get('email')
            otp = data.get('otp')
            new_password = data.get('newPassword')
            
            # Validate OTP
            if 'otp' not in request.session or str(otp) != str(request.session['otp']):
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('change_password')
            
            # Check OTP expiry
            otp_created_time = datetime.fromisoformat(request.session['otp_created_at'])
            if datetime.now() - otp_created_time > timedelta(minutes=10):
                del request.session['otp']
                del request.session['otp_created_at']
                request.session.modified = True
                messages.error(request, 'OTP has expired.')
                return redirect('change_password')
            
            # Validate password strength
            is_strong, password_error = validate_password_strength(new_password)
            if not is_strong:
                messages.error(request, password_error)
                return redirect('change_password')
            
            # Change password
            user_profile = UserProfile.objects.get(email=email)
            user = user_profile.user
            user.set_password(new_password)
            user.save()
            
            # Clear OTP session
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            
            messages.success(request, 'Password changed successfully.')
            return redirect('login')
        
        except UserProfile.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('change_password')
        except Exception as e:
            logger.error(f"Password change error: {e}")
            messages.error(request, 'An error occurred while changing password.')
            return redirect('change_password')
    
    return render(request, 'student_dash/forgot_pass.html')

def logoutUser(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')

        Cashfree.XClientId = "TEST430329ae80e0f32e41a393d78b923034"
        Cashfree.XClientSecret = "TESTaf195616268bd6202eeb3bf8dc458956e7192a85"
        Cashfree.XEnvironment = Cashfree.SANDBOX
        x_api_version = "2023-08-01"

        customerDetails = CustomerDetails(customer_id=str(request.user), customer_phone="9999999999")    
        customerDetails.customer_name = UserProfile.objects.get(user=request.user).Name 
        customerDetails.customer_email = UserProfile.objects.get(user=request.user).email
        order_id = str(request.user)+str(datetime.now()).replace(" ","").replace(":","").replace(".","")
        createOrderRequest = CreateOrderRequest(order_id=order_id, order_amount=float(amount), order_currency="INR", customer_details=customerDetails)
        orderMeta = OrderMeta()
        orderMeta.return_url = "https://www.cashfree.com/devstudio/preview/pg/web/popupCheckout?order_id={order_id}"
        orderMeta.notify_url = "https://www.cashfree.com/devstudio/preview/pg/webhooks/8020517"
        orderMeta.payment_methods = "cc,dc,upi"
        createOrderRequest.order_meta = orderMeta

        try:
            api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
            #print(api_response.data)
            return JsonResponse(serialize_order_entity(api_response.data), status=201)
        except Exception as e:
            print(e)
        return JsonResponse({"error": "Error creating order."}, status=400)
    
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        Cashfree.XClientId = "TEST430329ae80e0f32e41a393d78b923034"
        Cashfree.XClientSecret = "TESTaf195616268bd6202eeb3bf8dc458956e7192a85"
        Cashfree.XEnvironment = Cashfree.SANDBOX
        x_api_version = "2023-08-01"
        try:
            api_response = Cashfree().PGOrderFetchPayments(x_api_version, str(order_id), None)
            res = serialize_payment_entity(api_response.data[0])
            print(res)
            Transactions.objects.create(
            user=request.user,
            amount=res['payment_amount'],
            transaction_id=res['cf_payment_id'],
            status=True if res['payment_status'] == 'SUCCESS' else False,
            payment_mode = "Online-"+str(list(res['payment_method']['actual_instance'].keys())[0]),
            date = res['payment_time']
            )
            if res['payment_status'] == 'SUCCESS':
                UserProfile.objects.filter(user=request.user).update(Fee_Due=UserProfile.objects.get(user=request.user).Fee_Due - res['payment_amount'])
            return JsonResponse(res, status=200)
        except Exception as e:
            print(e)
        return JsonResponse({"error": "Error fetching order status."}, status=400)
    

def update_fee(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('fee')
        users = data.get('queryset')
        for user in users:
            UserProfile.objects.filter(user=User.objects.get(username=user)).update(Fee_Due=F("Fee_Due")+amount)
        messages.success(request, 'Fee updated successfully.')
        return JsonResponse({"message": "Fee updated successfully."}, status=200)
    return JsonResponse({"error": "Error updating fee."}, status=400)

def download_receipt(request, transaction_id):
    # Fetch transaction details from the database
    transaction = get_object_or_404(Transactions, transaction_id=transaction_id)

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{transaction_id}.pdf"'

    # Generate PDF using ReportLab or another library
    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Receipt for Transaction ID: {transaction.transaction_id}")
    p.drawString(100, 780, f"Date: {transaction.date}")
    p.drawString(100, 760, f"Amount: ₹{transaction.amount}")
    p.drawString(100, 740, f"Payment Mode: {transaction.payment_mode}")
    p.drawString(100, 720, f"Status: {'✅' if transaction.status else '❌'}")
    p.showPage()
    p.save()

    return response

def serialize_order_entity(order_entity):
    return {
    "cart_details": order_entity.cart_details,
    "cf_order_id": order_entity.order_id,
    "created_at": order_entity.created_at,
    "customer_details": {
        "customer_id": order_entity.customer_details.customer_id,    
        "customer_name": order_entity.customer_details.customer_name,
        "customer_email": order_entity.customer_details.customer_email,
        "customer_phone": order_entity.customer_details.customer_phone,
        "customer_uid": order_entity.customer_details.customer_uid
    },
    "entity": order_entity.entity,
    "order_amount": order_entity.order_amount,
    "order_currency": order_entity.order_currency,
    "order_expiry_time": order_entity.order_expiry_time,
    "order_id": order_entity.order_id,  
    "order_meta": {
        "return_url": order_entity.order_meta.return_url,
        "notify_url": order_entity.order_meta.notify_url,
        "payment_methods": order_entity.order_meta.payment_methods
    },
    "order_note": order_entity.order_note,
    "order_splits": order_entity.order_splits,
    "order_status": order_entity.order_status,
    "order_tags": order_entity.order_tags,
    "payment_session_id": order_entity.payment_session_id,
    "terminal_data": "",
}

def serialize_payment_method(payment_method):
    return {
        "oneof_schema_1_validator": payment_method.oneof_schema_1_validator,
        "oneof_schema_2_validator": payment_method.oneof_schema_2_validator,
        "oneof_schema_3_validator": payment_method.oneof_schema_3_validator,
        "oneof_schema_4_validator": payment_method.oneof_schema_4_validator,
        "oneof_schema_5_validator": payment_method.oneof_schema_5_validator,
        "oneof_schema_6_validator": payment_method.oneof_schema_6_validator,
        "oneof_schema_7_validator": payment_method.oneof_schema_7_validator,
        "oneof_schema_8_validator": payment_method.oneof_schema_8_validator,
        "actual_instance": {
            "upi": {
                "channel": payment_method.actual_instance.upi.channel,
                "upi_id": payment_method.actual_instance.upi.upi_id
            }
        },
        "one_of_schemas": payment_method.one_of_schemas,
    }

def serialize_payment_entity(payment_entity):
    return {
        "cf_payment_id": payment_entity.cf_payment_id,
        "order_id": payment_entity.order_id,
        "entity": payment_entity.entity,
        "error_details": payment_entity.error_details,
        "is_captured": payment_entity.is_captured,
        "order_amount": payment_entity.order_amount,
        "payment_group": payment_entity.payment_group,
        "payment_currency": payment_entity.payment_currency,
        "payment_amount": payment_entity.payment_amount,
        "payment_time": payment_entity.payment_time,
        "payment_completion_time": payment_entity.payment_completion_time,
        "payment_status": payment_entity.payment_status,
        "payment_message": payment_entity.payment_message,
        "bank_reference": payment_entity.bank_reference,
        "auth_id": payment_entity.auth_id,
        "authorization": payment_entity.authorization,
        "payment_method": serialize_payment_method(payment_entity.payment_method),
    }