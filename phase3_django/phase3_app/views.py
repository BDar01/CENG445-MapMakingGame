# game_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from .client import GameClient 
import json

def root_view(request):
    return render(request, 'root.html')

def main_view(request):
    return render(request, 'main.html', {'username': "user's name"})

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

# Not corrected implementation using GameClient from client.py
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Check if session_key exists or create a new session

            try:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']
                fullname = form.cleaned_data['fullname']

                response = request.game_client.register_user(username, fullname, email, password)

                if response['Message'] == 'Username exists. Please try for another username.':
                    messages.error(request, 'Username already exists. Please choose another username.')
                else:
                    messages.success(request, 'Registration successful! Please log in.')
                    return redirect('login_user')
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, 'Internal Server Error')
        else:
            messages.error(request, 'Invalid registration form. Please check your input.')

    form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        session_key = request.session.session_key

        try:
            form = LoginForm(request.POST)
            if form.is_valid():
                request.game_client.load_token()
                if request.game_client.token != -1:
                    response = request.game_client.send_command(json.dumps({'command': "C", 'user_id': request.game_client.user_id, 'token': request.game_client.token}))
                    if response["Message"] == "Logged in":
                        request.game_client.logged_in = True
                        messages.success(request, 'Already logged in!')
                        return redirect('main_page')
                    else:
                        request.game_client.token = -1

                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                response = request.game_client.login_user(username, password)

                if response['Message'] == 'Logged in':
                    request.game_client.logged_in = True
                    request.game_client.token = response['token']
                    request.game_client.user_id = response['user_id']
                    request.game_client.save_token(request.game_client.user_id, request.game_client.token)

                    messages.success(request, 'Login successful!')
                    return redirect('main_page')
                else:
                    messages.error(request, 'Incorrect username or password. Please try again.')
            else:
                messages.error(request, 'Invalid login form. Please check your input.')

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')

    form = LoginForm()
    return render(request, 'login.html', {'form': form})

