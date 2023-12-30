# game_app/views.py
from .forms import RegistrationForm, LoginForm, NewMapForm, JoinMapForm
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
        print("Pre-check ", response)
        if "Message" in response and response["Message"] == "Logged in":
            client.logged_in = True
            #if 'username' in response:
            client.username = response['username']
            messages.success(request, response['Message'])
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
    
def list_maps(request):
    client = GameClient('localhost',1423)

    response = client.list_maps()

def new_map(request):
    if request.method == 'POST':
        form = NewMapForm(request.POST)
        try: 
            client = GameClient('localhost', 1423)

            if form.is_valid():
                name = form.cleaned_data['name']
                size = form.cleaned_data['size']
                type = form.cleaned_data['type']

                response = client.new_map(name, size, type)
                request.session['new_map_response'] = response

                return redirect('main')


        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')

async def join_map(request, map_id):
    if request.method == 'POST':
        form = JoinMapForm(request.POST)
        background_image = request.POST.get('background_image', '')
        try: 
            client = GameClient('localhost', 1423)

            if form.is_valid():
                teamname = form.cleaned_data['teamname']
                client.join_map(map_id, teamname)
                
                querymap_response = client.query_map().get("Message", None)
                


                return render(request, 'map.html', {'map_id': map_id, 'teamname': teamname, 'background_image': background_image, 'objects': querymap_response})



        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')


def leave_map(request):
    map_id = request.GET.get('map_id', '')
    teamname = request.GET.get('teamname', '')

    try: 
        client = GameClient('localhost', 1423)
        response = client.leave_map(map_id, teamname)

        request.session['leave_map_response'] = response

        return redirect('main')



    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Internal Server Error')
        return redirect('main')




def main_view(request):
    
    client = GameClient('localhost',1423)
    if not client.logged_in:
        return redirect('root')
    
    new_map_form = NewMapForm()
    join_map_form = JoinMapForm()
    
    maps = client.list_maps().get("Message", None)

    new_map_response_data = request.session.pop('new_map_response', {})
    new_map_response = new_map_response_data.get("Message", None)



    leave_map_response_data = request.session.pop('leave_map_response', {})
    leave_map_response = leave_map_response_data.get("Message", None)

    return render(request, 'main.html', {'username': client.username, 'new_map_form': new_map_form, 'join_map_form': join_map_form, 'new_map_response': new_map_response, 'leave_map_response': leave_map_response,  'maps': maps})

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

               

                if response['Message'] == 'Username exists. Please try for another username.':
                    messages.error(request, response['Message'])
                elif response['Message'] == 'User added successfully. Please login.':
                    messages.success(request, response['Message'])

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

                if response['Message'] == 'Logged in':
                    client.logged_in = True
                    client.token = response['token']
                    client.user_id = response['user_id']
                    client.username = username
                    client.save_token(client.user_id, client.token)

                    messages.success(request, response['Message'])
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
            print("Logout ", response)
            if response['Message'] == 'Logged out':
                client.token = -1
                client.save_token(client.user_id,client.token)
                messages.success(request, response['Message'])
            else:
                messages.error(request, 'Logout failed.')
        else:
            messages.info(request, 'You are not logged in.')

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Internal Server Error')

    return redirect('root')

@csrf_exempt
@require_POST
async def exit_on_close(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if user_id:
            client = GameClient('localhost', 1423)
            command = {'command': 'E', 'user_id': user_id}
            
            # Use sync_to_async to make the fetch operation asynchronous
            async_response = await sync_to_async(client.send_command)((json.dumps(command)))

            return JsonResponse({'Message': async_response['Message']})
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'Message': 'Internal Server Error'}, status=500)