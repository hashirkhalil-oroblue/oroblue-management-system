from django.shortcuts import render , redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def  login_pg(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username = username):
            messages.error(request, "Username Invalid ! ")
            return redirect('login_pg')
        
        user = authenticate(username = username , password = password)

        if User is None:
            messages.error(request, "Username Invalid ! ")
            return redirect('login_pg')
        else:
            login(request, user)
            return redirect('dashboard')


    return render(request, 'login.html')

def logout_pg(request):
    logout(request)
    return redirect('login_pg')
