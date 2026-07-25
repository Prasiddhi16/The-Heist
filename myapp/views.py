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
        return render(request, 'caseresolution.html', {'case': None, 'cases': cases})
    case = Case.objects.get(case_id=case_id)
    return render(request, 'caseresolution.html', {'case': case})
def casehistory(request):
    # Dummy case list
    cases = [
        {
            "name": "Bank Heist",
            "date_solved": "2026-07-20",
            "suspect_name": "John Doe",
            "outcome": "correct",
            "accuracy": 85,
            "score": 120,
        },
        {
            "name": "Museum Theft",
            "date_solved": "2026-07-18",
            "suspect_name": "Jane Smith",
            "outcome": "incorrect",
            "accuracy": 60,
            "score": -40,
        },
    ]

    # Dummy stats
    conviction_rate = 50
    avg_score = 40
    best_score = 120

    return render(request, "casehistory.html", {
        "cases": cases,
        "conviction_rate": conviction_rate,
        "avg_score": avg_score,
        "best_score": best_score,
    })
