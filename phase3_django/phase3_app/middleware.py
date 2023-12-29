from .client import GameClient

class GameClientMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'game_client' not in request.session:
            game_client = GameClient('localhost', 1423, request.session.session_key)
            request.session['game_client_data'] = {
                'logged_in': game_client.logged_in,
                'user_id': game_client.user_id,
                'token': game_client.token,
                'connected': game_client.connected,
            }
        else:
            game_client_data = request.session['game_client_data']
            game_client = GameClient('localhost', 1423, request.session.session_key)
            game_client.__dict__.update(game_client_data)

        request.game_client = game_client

        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'render') and callable(response.render):
            response.render()

        if isinstance(response.content, bytes):
            response.content = response.content.decode('utf-8')

        return response
