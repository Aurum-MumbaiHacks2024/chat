from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib import messages

from django.views import View
from .models import *
# Create your views here.

class Index(View):
    def get(self, request):
        return render(request, 'core/index.html')
    

class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        
        return render(request, 'core/login.html')
    def post(self, request):
        uname = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=uname).exists():
            user = get_object_or_404(User, username=uname)
            auth = authenticate(username=uname, password=password)
            if auth == None:
                messages.error(request, "Please check your password.")
                return redirect('login')
            else:
                auth_login(request, user)
                return redirect('index')

        else:
            messages.error(request, "User with this email does not exist.")
            return redirect('login')

class Signup(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        
        return render(request, 'core/signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('name')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Please try a different username!")
            return redirect('signup')
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        try:
            password_validation.validate_password(password=password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('/signup')
         
        new_user = User.objects.create(
            username = username,
            password = make_password(password),
            first_name = first_name
        )

        auth_login(request, new_user)

        return redirect('index')

class Logout(View):
    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
            return redirect('login')