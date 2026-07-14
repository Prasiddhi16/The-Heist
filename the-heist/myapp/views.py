from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

def cases(request):
    return render(request, 'cases.html')
# Create your views here.

from django.conf import settings

def index(request):
    return render(request, 'home.html', {
        'supabase_url': settings.SUPABASE_URL,
        'supabase_anon_key': settings.SUPABASE_ANON_KEY,
    })