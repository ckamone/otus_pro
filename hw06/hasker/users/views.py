# from django.shortcuts import render
from typing import Any, Optional
from django.contrib.auth.models import User
from django.db import models
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from users.forms import RegistrationForm, UpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from users.models import CustomUser
from users.forms import RegistrationForm, UpdateForm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.
class UserLoginView(LoginView):
    template_name = 'users/login_form.html'


class UserLogoutView(LogoutView):
    pass

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'




class RegistrationView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'users/user_form.html'

    def post(self, request, *args, **kwargs):
        context = {}
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            if data.get('password1') == data.get('password2'):
                user = User.objects.create(
                    username=data.get('username'), 
                    email=data.get('email')
                    )
                user.set_password(data.get('password1'))
                user.save()
                avatar = data.get('avatar', None)
                if avatar:
                    user_avatar = CustomUser.objects.create(user=user, avatar=avatar)
                else:
                    user_avatar = CustomUser.objects.create(user=user)
                user_avatar.save()
                context['message'] = 'user created'
            else:
                context['message'] = 'password mismatch'
        else:
            context['message'] = 'invalid form'
        return render(request, "users/result.html", context=context)


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UpdateForm
    template_name = 'users/user_update.html'

    def test_func(self):
        return int(self.request.path.split('/')[-1])==self.request.user.pk

    def get(self, request, *args, **kwargs):
        context = {}
        context['object'] = User.objects.get(pk=kwargs.get('pk'))
        context['form'] = UpdateForm(request.GET)
        c_user = CustomUser.objects.filter(user=kwargs.get('pk'))
        context['avatar'] = c_user[0].avatar

        # return super().get(request, *args, **kwargs)
        return render(request, "users/user_update.html", context=context)
    
    def post(self, request, *args, **kwargs):
        context = {}
        context['message'] = ''
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            change_email = data.get('email', None)
            change_avatar = data.get('avatar', None)
            if change_email or change_avatar:
                user = User.objects.filter(username=request.user)[0]
                if change_email:
                    user.email = change_email
                    user.save()
                    context['message'] += 'updated email; '
                if change_avatar:
                    c_user = CustomUser.objects.filter(user=user)[0]
                    c_user.avatar = change_avatar
                    c_user.save()
                    context['message'] += 'updated avatar;'
            else:
                context['message'] += 'nothing done'
            
            # return super().get(request, *args, **kwargs)
        return render(request, "users/result.html", context=context)


