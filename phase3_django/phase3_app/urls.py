# phase3_app/urls.py
from django.urls import path
from .views import root_view,register_view, login_view, main_view

urlpatterns = [
    path('', root_view, name='root'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('main/', main_view, name='main'),
]