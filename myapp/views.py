from django.shortcuts import render, get_object_or_404
from .models import Case, Suspect, Evidence
from django.conf import settings

def login(request):
    context = {
        "supabase_url": getattr(settings, "SUPABASE_URL", ""),
        "supabase_anon_key": getattr(settings, "SUPABASE_ANON_KEY", ""),
    }
    return render(request, "login.html")

def dashboard(request):
    case = Case.objects.first()
    return render(request, "dashboard.html", {
        "case": case,
    })

def cases(request):
    return render(request, "cases.html", {
        "cases": Case.objects.all()
    })

def heist(request):
    return render(request, "heist.html")
    
def suspects(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)
    suspect_list = Suspect.objects.filter(case_id=case_id) 
    
    return render(request, "suspects.html", {
        "case": case,
        "suspects": suspect_list,
    })

def evidence(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)
    return render(request, "evidence.html", {
        "case": case,
        "evidence_items": case.evidence_items.all(),
    })
def case_resolution(request, case_id=None):
    if case_id is None:
        cases = Case.objects.all().order_by('-created_at')
        return render(request, 'case_resolution.html', {'case': None, 'cases': cases})
    case = Case.objects.get(case_id=case_id)
    return render(request, 'case_resolution.html', {'case': case})
def casehistory(request):
    return render(request, "casehistory.html")