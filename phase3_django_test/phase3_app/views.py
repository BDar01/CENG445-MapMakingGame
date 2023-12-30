# game_app/views.py
from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, redirect
from asgiref.sync import sync_to_async
from django.contrib import messages
from .client import GameClient 
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def root_view(request):
    client = GameClient('localhost',1423)
    client.load_token()
    if client.token != -1:
        response = client.send_command(json.dumps({'command': "C", 'user_id': client.user_id, 'token': client.token}))
        if "Message" in response and response["Message"] == "Logged in":
            client.logged_in = True
            #if 'username' in response:
            client.username = response['username']
            messages.success(request, 'Already logged in!')
            return redirect('main')
            #else:
                # Handle the case where 'username' is not present in the response
                #messages.error(request, 'Username not found in the server response.')
                #return render(request, 'root.html')
        else:
            client.token = -1
            return render(request, 'root.html')
    else:
        return render(request, 'root.html')

def main_view(request):
    client = GameClient('localhost',1423)
    if not client.logged_in:
        return redirect('root')
    return render(request, 'main.html', {'username': client.username})

# Not corrected implementation using GameClient from client.py
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Check if session_key exists or create a new session

            try:
                client = GameClient('localhost', 1423)
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']
                fullname = form.cleaned_data['fullname']

                print("Check before response.")

                response = client.register_user(username, fullname, email, password)

                print(response['Message'])

                if response['Message'] == 'Username exists. Please try for another username.':
                    messages.error(request, 'Username already exists. Please choose another username.')
                elif response['Message'] == 'User added successfully. Please login.':
                    messages.success(request, 'Registration successful! Please log in.')

                    return redirect('login')
                
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, 'Internal Server Error')
        else:
            messages.error(request, 'Invalid registration form. Please check your input.')

    form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':

        try:
            client = GameClient('localhost', 1423)
            
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                response = client.login_user(username, password)
                print(response)

                if response['Message'] == 'Logged in':
                    client.logged_in = True
                    client.token = response['token']
                    client.user_id = response['user_id']
                    client.username = username
                    client.save_token(client.user_id, client.token)

                    messages.success(request, 'Login successful!')
                    return redirect('main')
                else:
                    messages.error(request, 'Incorrect username or password. Please try again.')
            else:
                messages.error(request, 'Invalid login form. Please check your input.')

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')

    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    try:
        client = GameClient('localhost', 1423)

        if client.logged_in:
            response = client.logout_user()
            print(response)
            if response['Message'] == 'Logged out':
                client.token = -1
                messages.success(request, 'Logout successful!')
            else:
                messages.error(request, 'Logout failed.')
        else:
            messages.info(request, 'You are not logged in.')

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Internal Server Error')

    return redirect('root')

@require_POST
@csrf_exempt
@sync_to_async
def exit_on_close(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if user_id:
            client = GameClient('localhost', 1423)
            command = {'command': 'E', 'user_id': user_id}
            response = client.send_command(json.dumps(command))
            return JsonResponse({'Message': response['Message']})
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'Message': 'Internal Server Error'}, status=500)