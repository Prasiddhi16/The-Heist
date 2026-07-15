from django.shortcuts import render
from django.conf import settings
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
    
def evidence(request):
    return render(request, "evidence.html")


def suspects(request):
    return render(request, "suspects.html")

def caseresolution(request):
    return render(request, "caseresolution.html")

def analysis(request):
    return render(request, "analysis.html")

def history(request):
    return render(request, "history.html")

def leaderboard(request):
    return render(request, "leaderboard.html")

def index(request):
    return render(request, "home.html", {
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key": settings.SUPABASE_ANON_KEY,
    })