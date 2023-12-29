# phase3_app/urls.py
from django.urls import path
from .views import root_view, register_view, register_user, login_view, login_user, main_view
'''
urlpatterns = [
    path('', root_view, name='root'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('main/', main_view, name='main_page'),  # Updated to match the view name
]
'''
urlpatterns = [
    path('', root_view, name='root'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
]
