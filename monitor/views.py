from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Warning
from django.contrib.auth import logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'monitor/login.html')

@login_required
def dashboard(request):
    # Check if a POST request is made to create a warning
    if request.method == 'POST':
        # Create a warning (this will trigger the email)
        Warning.objects.create(message="Privilege escalation attempt detected!")
    
    # Fetch all warnings and order them by timestamp
    warnings = Warning.objects.all().order_by('-timestamp') 

    

   

    return render(request, 'monitor/dashboard.html', {'warnings': warnings,})

def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page






