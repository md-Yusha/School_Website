from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import UserProfile
from email.mime.text import MIMEText
from random import randint
import smtplib
import json
from datetime import datetime, timedelta
from django.contrib.auth import authenticate,login
# Create your views here.
def home(request):
    return render(request,'index.html')

def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, str(request.user)+'Login successful.')
            return redirect('/dashboard/'+str(request.user))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request,'student_dash/login.html')


def registerUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('name')
        user_class = request.POST.get('class')
        father_name = request.POST.get('father_name')
        phone_number = request.POST.get('phone_number')
        alt_number = request.POST.get('alt_number')
        address = request.POST.get('address')
        otp = request.POST.get('otp')
        if str(otp) != str(request.session['otp']):
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('register')
        otp_created_time = datetime.fromisoformat(request.session['otp_created_at'])
        if datetime.now() - otp_created_time > timedelta(minutes=10):
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            return JsonResponse({"error": "OTP has expired."}, status=400)
        # Validate input (add your own validation logic)
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # Create the User object
        user = User.objects.create(
            username=username,
            password=make_password(password)  # Hash the password
        )
        UserProfile.objects.create(
            user=user,
            Name=name,
            Class=user_class,
            Father_name=father_name,
            phone_number=phone_number,
            alt_number=alt_number,
            address=address,
            email=email
        )

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request,'student_dash/register.html')


def dashboard(request,username):
    if str(request.user) != username:
        return redirect('login')
    user_data = {
        'username': request.user,
        'email': UserProfile.objects.get(user=request.user).email,
        'name': UserProfile.objects.get(user=request.user).Name,
        'class': UserProfile.objects.get(user=request.user).Class,
        'father_name': UserProfile.objects.get(user=request.user).Father_name,
        'phone_number': UserProfile.objects.get(user=request.user).phone_number,
        'alt_number': UserProfile.objects.get(user=request.user).alt_number,
        'address': UserProfile.objects.get(user=request.user).address,
        'fee_due': UserProfile.objects.get(user=request.user).Fee_Due,
    }
    return render(request,'student_dash/dashboard.html',{"student":user_data})
def otp_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        to_email = data.get('email')
        my_email = "rishi71213@gmail.com"
        password = "bowoopqtkinsvbqw"
        gmail_server = "smtp.gmail.com"
        gmail_port = 587
        my_server = smtplib.SMTP(gmail_server,gmail_port)
        my_server.ehlo()
        my_server.starttls()
        my_server.login(my_email,password)
        otp = randint(1000,9999)
        request.session['otp'] = otp
        request.session['otp_created_at'] = datetime.now().isoformat()
        request.session.modified = True
        m = "Hello, Welcome to School! Your OTP is "+str(otp)+" This OTP is valid for 10 minutes."
        msg1 = MIMEText(m, "plain", "utf-8")
        my_server.sendmail(from_addr=my_email,to_addrs=to_email, msg=msg1.as_string())
        print("Email sent!")
        return JsonResponse({'message': 'OTP sent!'}, status=201)
    else:
        print("Problem sending email")
    return JsonResponse({'message': 'OTP not sent!'}, status=400)
