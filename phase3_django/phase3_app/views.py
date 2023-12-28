# game_app/views.py
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm

def root_view(request):
    return render(request, 'root.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Handle user registration and redirect to login page
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Handle user login and redirect to main page
            return redirect('main')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def main_view(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Access the username of the logged-in user
        username = request.user.username
        # You can now use 'username' in your template or do other actions

        # Display main page with options like new map, logout, and list of existing maps
        return render(request, 'main.html', {'username': username})
    else:
        # If the user is not authenticated, you may want to redirect them to the login page
        return redirect('login')