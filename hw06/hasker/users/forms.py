from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from users.models import CustomUser
from django import forms


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(help_text='')
    email = forms.CharField(help_text='')
    password1 = forms.CharField(help_text='', widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(help_text='', widget=forms.PasswordInput, label='Password confirmation')
    avatar = forms.ImageField(help_text='', label='Avatar', required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','avatar')


class UpdateForm(forms.ModelForm):
    password = None
    avatar = forms.ImageField(help_text='', label='Avatar', required=False)

    class Meta:
        model = User
        fields = ('email','avatar')