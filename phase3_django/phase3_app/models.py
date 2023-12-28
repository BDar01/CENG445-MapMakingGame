from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)  # Use a secure hashing algorithm

class AuthToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=256, unique=True)
