# phase3_app/urls.py
from django.urls import path
from .views import root_view, register_user, logout_user, login_user, main_view, exit_on_close

urlpatterns = [
    path('', root_view, name='root'),
    path('main/', main_view, name='main'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register_user, name='register'),
    path('exit-on-close/', exit_on_close, name='exit_on_close'), 
]

'''
urlpatterns = [
    path('', root_view, name='root'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
]
'''