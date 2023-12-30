from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50)
    fullname = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class NewMapForm(forms.Form):
    name = forms.CharField(max_length=50)
    size = forms.CharField(max_length=12)
    type = forms.CharField(max_length=50)

class JoinMapForm(forms.Form):
    teamname = forms.CharField(max_length=50, label="Team Name")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)