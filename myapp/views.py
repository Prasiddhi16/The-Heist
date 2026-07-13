from django.shortcuts import render, get_object_or_404
from .models import Case, Suspect, Evidence

def home(request):
    return render(request, "login.html")   # root → login page

def login_view(request):
    return render(request, "login.html")

def dashboard(request):
    return render(request, "dashboard.html")

def cases(request):
    return render(request, "cases.html", {"cases": Case.objects.all()})
def heist(request):
    return render(request, "heist.html")
    
def suspects(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    return render(request, "suspects.html", {
        "case": case,
        "suspects": case.suspects.all(),
    })

def evidence(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    return render(request, "evidence.html", {
        "case": case,
        "evidence_items": case.evidence_items.all(),
    })