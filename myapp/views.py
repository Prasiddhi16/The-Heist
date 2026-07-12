from django.shortcuts import render
def dashboard(request):
    return render(request, 'dashboard.html')

def cases(request):
    return render(request, 'cases.html')
# Create your views here.
