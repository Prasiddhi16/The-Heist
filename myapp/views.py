import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import (Case, Suspect, Evidence, CaseSubmission,
                      SubmissionSuspect, SubmissionEvidence,
                      SolutionSuspect, SolutionEvidence)


def _get_or_create_submission(case_id, submission_id):
    if submission_id:
        existing = CaseSubmission.objects.filter(submission_id=submission_id, case_id=case_id).first()
        if existing:
            return existing
    submission = CaseSubmission.objects.create(case_id=case_id)
    SubmissionSuspect.objects.bulk_create([
        SubmissionSuspect(submission=submission, suspect=s, is_accused=False)
        for s in Suspect.objects.filter(case_id=case_id)
    ])
    SubmissionEvidence.objects.bulk_create([
        SubmissionEvidence(submission=submission, evidence=e, is_selected=False)
        for e in Evidence.objects.filter(case_id=case_id)
    ])
    return submission


@csrf_exempt
def toggle_accuse(request, case_id, suspect_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    body = json.loads(request.body or '{}')
    submission = _get_or_create_submission(case_id, body.get('submission_id'))

    SubmissionSuspect.objects.filter(submission=submission).update(is_accused=False)
    SubmissionSuspect.objects.filter(submission=submission, suspect_id=suspect_id).update(is_accused=True)

    return JsonResponse({'submission_id': submission.submission_id, 'accused_suspect_id': suspect_id})


@csrf_exempt
def toggle_evidence(request, case_id, evidence_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    body = json.loads(request.body or '{}')
    submission = _get_or_create_submission(case_id, body.get('submission_id'))

    row = SubmissionEvidence.objects.get(submission=submission, evidence_id=evidence_id)
    row.is_selected = not row.is_selected
    row.save()

    return JsonResponse({'submission_id': submission.submission_id, 'evidence_id': evidence_id, 'is_selected': row.is_selected})


def submission_state(request, case_id):
    submission_id = request.GET.get('submission_id')
    if not submission_id:
        return JsonResponse({'accused_suspect_id': None, 'selected_evidence_ids': [], 'narrative': ''})
    submission = CaseSubmission.objects.filter(submission_id=submission_id, case_id=case_id).first()
    accused = SubmissionSuspect.objects.filter(submission_id=submission_id, is_accused=True).first()
    selected = list(SubmissionEvidence.objects.filter(submission_id=submission_id, is_selected=True).values_list('evidence_id', flat=True))
    return JsonResponse({
        'accused_suspect_id': accused.suspect_id if accused else None,
        'selected_evidence_ids': selected,
        'narrative': submission.narrative if submission else '',
    })


@csrf_exempt
def save_narrative(request, case_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    body = json.loads(request.body or '{}')
    submission = _get_or_create_submission(case_id, body.get('submission_id'))
    submission.narrative = body.get('narrative', '')
    submission.save()
    return JsonResponse({'submission_id': submission.submission_id})


def analysis(request):
    submissions = CaseSubmission.objects.select_related('case').all()
    return render(request, 'analysis.html', {'submissions': submissions})


def review_submission(request, submission_id):
    submission = get_object_or_404(CaseSubmission, submission_id=submission_id)

    suspects_compare = []
    for row in SubmissionSuspect.objects.filter(submission=submission).select_related('suspect'):
        solved = SolutionSuspect.objects.filter(case_id=submission.case_id, suspect=row.suspect).first()
        suspects_compare.append({
            'name': row.suspect.name,
            'was_accused': row.is_accused,
            'is_actually_guilty': solved.is_guilty if solved else None,
            'match': (solved is not None and row.is_accused == solved.is_guilty),
        })

    evidence_compare = []
    for row in SubmissionEvidence.objects.filter(submission=submission).select_related('evidence'):
        solved = SolutionEvidence.objects.filter(case_id=submission.case_id, evidence=row.evidence).first()
        evidence_compare.append({
            'item_name': row.evidence.item_name,
            'was_selected': row.is_selected,
            'is_actually_key': solved.is_key_evidence if solved else None,
            'match': (solved is not None and row.is_selected == solved.is_key_evidence),
        })

    if request.method == 'POST':
        submission.is_correct = request.POST.get('verdict') == 'correct'
        submission.reviewer_notes = request.POST.get('notes', '')
        submission.reviewed = True
        submission.save()

    return render(request, 'review.html', {
        'submission': submission,
        'suspects_compare': suspects_compare,
        'evidence_compare': evidence_compare,
    })
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
    return render(request, 'caseresolution.html', {
        'case': case,
        'suspects': Suspect.objects.filter(case_id=case_id),
        'evidence_items': Evidence.objects.filter(case_id=case_id),
    })
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
