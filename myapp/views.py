from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def cases(request):
    return render(request, "cases.html")

@login_required
def heist(request):
    return render(request, "heist.html")
