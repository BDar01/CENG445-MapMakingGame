from django.contrib import admin
from .models import UserProfile, AuthToken

admin.site.register(UserProfile)
admin.site.register(AuthToken)

