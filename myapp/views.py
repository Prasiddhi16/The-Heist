from django.shortcuts import render

def home(request):
    return render(request, "login.html")   # root → login page

def login_view(request):
    return render(request, "login.html")

def dashboard(request):
    return render(request, "dashboard.html")

def cases(request):
    return render(request, "cases.html")

def heist(request):
    return render(request, "heist.html")
