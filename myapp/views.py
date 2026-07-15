from django.shortcuts import render, get_object_or_404
from .models import Case, Suspect, Evidence

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
def caseresolution(request):
    return render(request, "caseresolution.html")
def casehistory(request):
    return render(request, "casehistory.html")