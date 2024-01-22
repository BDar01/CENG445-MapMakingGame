# game_app/views.py
from .forms import RegistrationForm, LoginForm, NewMapForm, JoinMapForm
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import loader

from asgiref.sync import sync_to_async
from .client import GameClient 
import secrets
import json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def root_view(request):
    # Set a cookie for every browser session
    if not request.COOKIES.get('my_game_cookie'):
        cookie_val = secrets.token_hex(16) 
        response = render(request, 'root.html')
        response.set_cookie('my_game_cookie', cookie_val, max_age=None)  # None means the cookie will expire when the user closes the browser
        return response

    
    client = GameClient(request.COOKIES.get('my_game_cookie'))
    client.load_token()

    if client.token != -1:
        response = client.send_command(json.dumps({'command': "C", 'user_id': client.user_id, 'token': client.token}))
        print("Pre-check ", response)
        if "Message" in response and response["Message"] == "Logged in":
            client.logged_in = True
            client.username = response['username']
            messages.success(request, response['Message'])
            return redirect('main')
        else:
            client.token = -1
            return render(request, 'root.html')
    else:
        return render(request, 'root.html')


def list_maps(request):
    client = GameClient(request.COOKIES.get('my_game_cookie'))

    response = client.list_maps()

def new_map(request):
    if request.method == 'POST':
        form = NewMapForm(request.POST)
        try: 
            client = GameClient(request.COOKIES.get('my_game_cookie'))

            if form.is_valid():
                name = form.cleaned_data['name']
                type = form.cleaned_data['type']
                size = None
                if type == "arena":
                    size = '612x408'
                elif type == "labyrinth":
                    size = '1300x975'

                response = client.new_map(name, size, type)
                request.session['new_map_response'] = response
                return redirect('main')


        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')


def join_map(request, map_id):    
    # Check if the user has already joined a map
    if request.method == 'POST':
        form = JoinMapForm(request.POST)
        background_image = request.POST.get('background_image', '')
        player_vision = request.POST.get('player_vision','')
        try: 
            client = GameClient(request.COOKIES.get('my_game_cookie'))

            if form.is_valid():
                teamname = form.cleaned_data['teamname']
                message = client.join_map(map_id, teamname)
                if message["Message"] == "Player is dead. Please join a map.":
                    response = client.leave_map(map_id, teamname)

                    request.session['leave_map_response'] = message

                    return redirect('main')

                player_name = message["Message"].split(" ")[1]

                # Retrieve the message from the session
                msg = request.session.pop('msg', None)
                if msg == None:
                    msg = 'Empty'
                
                querymap_response = client.query_map().get("Message", None)

                repo_response = client.show_repo().get("Message", None)

                health_response = client.show_health().get("Message", None)

                return render(request, 'map.html', {'map_id': map_id, 'teamname': teamname, 'playername': player_name, 'background_image': background_image, 'objects': querymap_response, 'repo': repo_response, 'health': health_response, 'msg': msg, 'player_vision': player_vision})

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')

def update_map(request):
    try:
        # Get the map_id, teamname, and background_image from the request parameters
        map_id = request.GET.get('map_id')
        teamname = request.GET.get('teamname')
        playername = request.GET.get('playername')
        background_image = request.GET.get('background_image')

        client = GameClient(request.COOKIES.get('my_game_cookie'))
        querymap_response = client.query_map().get("Message", None)
        repo_response = client.show_repo().get("Message", None)
        health_response = client.show_health().get("Message", None)
            
        # Load the template and render it with the updated data
        template = loader.get_template('map.html')
        html_content = template.render({'map_id': map_id, 'teamname': teamname, 'playername': playername, 'background_image': background_image, 'objects': querymap_response, 'repo': repo_response, 'health': health_response}, request)

        return HttpResponse(html_content)

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Internal Server Error')
        return HttpResponseBadRequest(str(e))
    
def drop_object(request):
    if request.method == 'GET':
        map_id = request.GET.get('map_id')
        teamname = request.GET.get('teamname')
        playername = request.GET.get('playername')
        background_image = request.GET.get('background_image')
        object = request.GET.get('object')
        try: 
            client = GameClient(request.COOKIES.get('my_game_cookie'))

            drop_response = client.drop_object(object)
            msg = drop_response['Message']
            print("Drop_object response: ", msg)

            request.session['msg'] = msg  # Set the message in the session
                
            querymap_response = client.query_map().get("Message", None)
            repo_response = client.show_repo().get("Message", None)
            health_response = client.show_health().get("Message", None)

            # Load the template and render it with the updated data
            template = loader.get_template('map.html')
            html_content = template.render({'map_id': map_id, 'teamname': teamname, 'playername': playername, 'background_image': background_image, 'objects': querymap_response, 'repo': repo_response, 'health': health_response}, request)

            return HttpResponse(html_content)

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
            return HttpResponseBadRequest(str(e))
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')


def move_player(request):
    if request.method == 'GET':
        map_id = request.GET.get('map_id')
        teamname = request.GET.get('teamname')
        playername = request.GET.get('playername')
        background_image = request.GET.get('background_image')
        direction = request.GET.get('direction')
        try: 
            client = GameClient(request.COOKIES.get('my_game_cookie'))

            move_response = client.move_player(direction)
            msg = move_response['Message']
            print("Move_player response: ", msg)

            request.session['msg'] = msg  # Set the message in the session
                
            querymap_response = client.query_map().get("Message", None)
            repo_response = client.show_repo().get("Message", None)
            health_response = client.show_health().get("Message", None)

            # Load the template and render it with the updated data
            template = loader.get_template('map.html')
            html_content = template.render({'map_id': map_id, 'teamname': teamname, 'playername': playername, 'background_image': background_image, 'objects': querymap_response, 'repo': repo_response, 'health': health_response}, request)

            return HttpResponse(html_content)

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Internal Server Error')
            return HttpResponseBadRequest(str(e))
    else:
        messages.error(request, 'Invalid registration form. Please check your input.')

    return redirect('main')

def leave_map(request):
    map_id = request.GET.get('map_id', '')
    teamname = request.GET.get('teamname', '')

    try: 
        client = GameClient(request.COOKIES.get('my_game_cookie'))
        response = client.leave_map(map_id, teamname)

        request.session['leave_map_response'] = response

        return redirect('main')

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, 'Internal Server Error')
        return redirect('main')


def main_view(request):
    
    client = GameClient(request.COOKIES.get('my_game_cookie'))
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


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Check if session_key exists or create a new session
            try:
                client = GameClient(request.COOKIES.get('my_game_cookie'))
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
            client = GameClient(request.COOKIES.get('my_game_cookie'))
            
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
        client = GameClient(request.COOKIES.get('my_game_cookie'))

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
            
            async_response = await sync_to_async(client.send_command)((json.dumps(command)))

            return JsonResponse({'Message': async_response['Message']})
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'Message': 'Internal Server Error'}, status=500)