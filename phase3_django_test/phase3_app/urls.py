# phase3_app/urls.py
from django.urls import path
from .views import root_view, register_user, logout_user, login_user, main_view, exit_on_close, new_map, join_map, leave_map, update_map, drop_object, move_player

urlpatterns = [
    path('', root_view, name='root'),
    path('main/', main_view, name='main'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('exit-on-close/', exit_on_close, name='exit_on_close'), 
    path('main/new_map/', new_map, name='new_map'),
    path('main/join_map/<int:map_id>', join_map, name = 'join_map'),
    path('main/leave_map', leave_map, name='leave_map'),
    path('update_map/', update_map, name='update_map'),
    path('drop_object/', drop_object, name='drop_object'),
    path('move_player/', move_player, name='move_player')
]

'''
urlpatterns = [
    path('', root_view, name='root'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
]
'''