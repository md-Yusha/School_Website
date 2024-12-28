from django.shortcuts import render, redirect
from .models import Student
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request,'index.html')

def student_list(request):
    students = Student.objects.all()  # Get all student records from the database
    return render(request, 'student_list.html', {'students': students})


def student_login(request):
    if request.method == 'POST':
        usn = request.POST['usn']
        password = request.POST['password']

        # Debug: Print the input values
        print(f"Received USN: {usn}, Password: {password}")  # Debug print

        try:
            # Try fetching the student by USN
            student = Student.objects.get(usn=usn)
            print(f"Student found: {student}")  # Debug print

            # Check if password matches
            if student.password == password:
                # Set the USN in the session
                request.session['student_usn'] = student.usn
                print(f"Session set for student with USN: {student.usn}")  # Debug print
                return redirect('student_dashboard')  # Redirect to the dashboard
            else:
                # Password doesn't match
                messages.error(request, 'Invalid credentials')
        except Student.DoesNotExist:
            # No student found for that USN
            messages.error(request, 'No student found with that USN')

    return render(request, 'student_login.html')






# school/views.py

def student_dashboard(request):
    # Get the USN from the session
    usn = request.session.get('student_usn')

    # Debug: Print the session value
    print(f"Logged in student USN: {usn}")  # Debug print

    if usn:
        try:
            # Fetch student from the database
            student = Student.objects.get(usn=usn)
            print(f"Student found for dashboard: {student}")  # Debug print
            return render(request, 'student_dashboard.html', {'student': student})
        except Student.DoesNotExist:
            return redirect('student_login')  # Redirect back to login if student doesn't exist
    else:
        return redirect('student_login')  # Redirect to login if no session
    
def student_logout(request):
    try:
        del request.session['student_usn']  # Clear the student session
    except KeyError:
        pass  # If the session key doesn't exist, just continue
    return redirect('student_login')  # Redirect to login page after logout