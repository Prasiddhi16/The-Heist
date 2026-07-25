import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Case,
    Suspect,
    Evidence,
    CaseSubmission,
    SubmissionSuspect,
    SubmissionEvidence,
    SolutionSuspect,
    SolutionEvidence
)
def _get_or_create_submission(case_id, submission_id):
    if submission_id:
        existing = CaseSubmission.objects.filter(
            submission_id=submission_id,
            case_id=case_id
        ).first()
        if existing:
            return existing
    submission = CaseSubmission.objects.create(case_id=case_id)
    SubmissionSuspect.objects.bulk_create([
        SubmissionSuspect(
            submission=submission,
            suspect=s,
            is_accused=False
        )
        for s in Suspect.objects.filter(case_id=case_id)
    ])
    SubmissionEvidence.objects.bulk_create([
        SubmissionEvidence(
            submission=submission,
            evidence=e,
            is_selected=False
        )
        for e in Evidence.objects.filter(case_id=case_id)
    ])
    return submission
@csrf_exempt
def toggle_accuse(request, case_id, suspect_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    submission = _get_or_create_submission(
        case_id,
        body.get('submission_id')
    )
    if body.get('unset'):
        SubmissionSuspect.objects.filter(
            submission=submission
        ).update(is_accused=False)
        return JsonResponse({
            'submission_id': submission.submission_id,
            'accused_suspect_id': None
        })
    suspect = get_object_or_404(
        Suspect,
        suspect_id=suspect_id,
        case_id=case_id
    )
    SubmissionSuspect.objects.filter(
        submission=submission
    ).update(is_accused=False)
    SubmissionSuspect.objects.filter(
        submission=submission,
        suspect=suspect
    ).update(is_accused=True)
    return JsonResponse({
        'submission_id': submission.submission_id,
        'accused_suspect_id': suspect.suspect_id
    })
@csrf_exempt
def toggle_evidence(request, case_id, evidence_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    submission = _get_or_create_submission(
        case_id,
        body.get('submission_id')
    )
    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id,
        case_id=case_id
    )
    row, created = SubmissionEvidence.objects.get_or_create(
        submission=submission,
        evidence=evidence
    )
    row.is_selected = not row.is_selected
    row.save()
    return JsonResponse({
        'submission_id': submission.submission_id,
        'evidence_id': evidence_id,
        'is_selected': row.is_selected
    })
def submission_state(request, case_id):
    submission_id = request.GET.get('submission_id')
    if not submission_id:
        return JsonResponse({
            'accused_suspect_id': None,
            'selected_evidence_ids': [],
            'narrative': ''
        })
    submission = CaseSubmission.objects.filter(
        submission_id=submission_id,
        case_id=case_id
    ).first()
    if not submission:
        return JsonResponse({
            'error': 'Submission not found'
        }, status=404)
    accused = SubmissionSuspect.objects.filter(
        submission=submission,
        is_accused=True
    ).first()
    selected = list(
        SubmissionEvidence.objects.filter(
            submission=submission,
            is_selected=True
        ).values_list(
            'evidence_id',
            flat=True
        )
    )
    return JsonResponse({
        'submission_id': submission.submission_id,
        'accused_suspect_id': accused.suspect_id if accused else None,
        'selected_evidence_ids': selected,
        'narrative': submission.narrative or ''
    })
@csrf_exempt
def save_narrative(request, case_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    submission = _get_or_create_submission(
        case_id,
        body.get('submission_id')
    )
    submission.narrative = body.get('narrative', '')
    submission.save(update_fields=['narrative'])
    return JsonResponse({
        'submission_id': submission.submission_id
    })
def login(request):
    context = {
        "supabase_url": getattr(settings, "SUPABASE_URL", ""),
        "supabase_anon_key": getattr(settings, "SUPABASE_ANON_KEY", ""),
    }
    return render(request, "login.html", context)
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
    case = get_object_or_404(
        Case,
        case_id=case_id
    )
    suspect_list = Suspect.objects.filter(
        case_id=case_id
    )
    return render(request, "suspects.html", {
        "case": case,
        "suspects": suspect_list,
    })
def evidence(request, case_id):
    case = get_object_or_404(
        Case,
        case_id=case_id
    )
    return render(request, "evidence.html", {
        "case": case,
        "evidence_items": case.evidence_items.all(),
    })
def case_resolution(request, case_id=None):
    if case_id is None:
        cases = Case.objects.all().order_by('-created_at')
        return render(
            request,
            'caseresolution.html',
            {
                'case': None,
                'cases': cases
            }
        )
    case = get_object_or_404(
        Case,
        case_id=case_id
    )
    return render(
        request,
        'caseresolution.html',
        {
            'case': case,
            'suspects': Suspect.objects.filter(
                case_id=case_id
            ),
            'evidence_items': Evidence.objects.filter(
                case_id=case_id
            ),
        }
    )
def analysis(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)
    submission_id = request.GET.get('submission_id')
    submission = None
    if submission_id:
        submission = CaseSubmission.objects.filter(
            submission_id=submission_id,
            case_id=case_id
        ).first()
    if not submission:
        submission = (
            CaseSubmission.objects
            .filter(case_id=case_id)
            .order_by('-submission_id')
            .first()
        )
    selected_suspect = None
    selected_evidence = []
    if submission:
        accused_row = (
            SubmissionSuspect.objects
            .filter(submission=submission, is_accused=True)
            .select_related('suspect')
            .first()
        )
        if accused_row:
            selected_suspect = accused_row.suspect
        selected_evidence_ids = SubmissionEvidence.objects.filter(
            submission=submission,
            is_selected=True
        ).values_list('evidence_id', flat=True)
        selected_evidence = list(
            Evidence.objects.filter(
                case_id=case_id,
                evidence_id__in=selected_evidence_ids
            )
        )
    evidence_total = Evidence.objects.filter(case_id=case_id).count()
    evidence_collected = len(selected_evidence)
    evidence_score = (evidence_collected / evidence_total) * 70 if evidence_total > 0 else 0
    suspect_score = 30 if selected_suspect else 0
    readiness_score = round(evidence_score + suspect_score)
    can_file_verdict = selected_suspect is not None and evidence_collected > 0
    top_suspect = (
        Suspect.objects
        .filter(case_id=case_id)
        .order_by('suspect_id')
        .first()
    )
    return render(request, 'analysis.html', {
        'case': case,
        'submission': submission,
        'selected_suspect': selected_suspect,
        'selected_evidence': selected_evidence,
        'evidence_collected': evidence_collected,
        'evidence_total': evidence_total,
        'readiness_score': readiness_score,
        'top_suspect': top_suspect,
        'can_file_verdict': can_file_verdict
    })
@transaction.atomic
def solve_case(request, case_id):
    if request.method != 'POST':
        return redirect(
            'analysis',
            case_id=case_id
        )
    case = get_object_or_404(
        Case,
        case_id=case_id
    )
    submission_id = request.POST.get(
        'submission_id'
    )
    if submission_id:
        submission = CaseSubmission.objects.filter(
            submission_id=submission_id,
            case_id=case_id
        ).first()
    else:
        submission = (
            CaseSubmission.objects
            .filter(case_id=case_id)
            .order_by('-submitted_at')
            .first()
        )
    if not submission:
        return redirect(
            'caseresolution',
            case_id=case_id
        )
    if submission.reviewed:
        return redirect(
            'analysis',
            case_id=case_id
        )
    accused = SubmissionSuspect.objects.filter(
        submission=submission,
        is_accused=True
    ).select_related(
        'suspect'
    ).first()
    selected_evidence = SubmissionEvidence.objects.filter(
        submission=submission,
        is_selected=True
    ).select_related(
        'evidence'
    )
    if not accused or not selected_evidence.exists():
        return redirect(
            f"{reverse('analysis', kwargs={'case_id': case_id})}?submission_id={submission.submission_id}"
        )
    correct_suspect = SolutionSuspect.objects.filter(
        case_id=case_id,
        is_guilty=True
    ).first()
    correct_evidence_ids = set(
        SolutionEvidence.objects.filter(
            case_id=case_id,
            is_key_evidence=True
        ).values_list(
            'evidence_id',
            flat=True
        )
    )
    suspect_correct = (
        correct_suspect is not None
        and accused.suspect_id == correct_suspect.suspect_id
    )
    selected_evidence_ids = set(
        selected_evidence.values_list(
            'evidence_id',
            flat=True
        )
    )
    evidence_correct = (
        selected_evidence_ids == correct_evidence_ids
    )
    submission.is_correct = (
        suspect_correct
        and evidence_correct
    )
    submission.reviewed = True
    submission.reviewer_notes = (
        f"Suspect selection: "
        f"{'Correct' if suspect_correct else 'Incorrect'}. "
        f"Evidence selection: "
        f"{'Correct' if evidence_correct else 'Incorrect'}."
    )
    submission.save(
        update_fields=[
            'is_correct',
            'reviewed',
            'reviewer_notes'
        ]
    )
    return redirect(
        'casehistory'
    )
def casehistory(request):
    submissions = (
        CaseSubmission.objects
        .select_related('case')
        .prefetch_related(
            'submissionsuspect_set__suspect',
            'submissionevidence_set__evidence'
        )
        .order_by('-submitted_at')
    )
    cases_json = []
    for sub in submissions:
        accused = (
            SubmissionSuspect.objects
            .filter(
                submission=sub,
                is_accused=True
            )
            .select_related('suspect')
            .first()
        )
        selected_evidence = (
            SubmissionEvidence.objects
            .filter(
                submission=sub,
                is_selected=True
            )
            .select_related('evidence')
        )
        evidence_list = [
            row.evidence.item_name
            for row in selected_evidence
        ]
        evidence_total = Evidence.objects.filter(
            case_id=sub.case_id
        ).count()
        if sub.is_correct is True:
            outcome = "correct"
        elif sub.is_correct is False:
            outcome = "incorrect"
        else:
            outcome = "pending"
        evidence_accuracy = (
            round(
                (len(evidence_list) / evidence_total) * 100
            )
            if evidence_total
            else 0
        )
        suspect_accuracy = (
            100
            if sub.is_correct is True
            else 0
        )
        accuracy = round(
            (
                evidence_accuracy
                + suspect_accuracy
            ) / 2
        )
        if sub.is_correct is True:
            score = accuracy
        elif sub.is_correct is False:
            score = -(100 - accuracy)
        else:
            score = 0
        cases_json.append({
            "id": sub.submission_id,
            "case_id": sub.case.case_number,
            "title": sub.case.title,
            "date_solved": sub.submitted_at.strftime(
                "%Y-%m-%d"
            ),
            "status": (
                "closed"
                if sub.reviewed
                else "active"
            ),
            "outcome": outcome,
            "accuracy": accuracy,
            "score": score,
            "suspect": {
                "name": (
                    accused.suspect.name
                    if accused
                    else None
                ),
                "occupation": (
                    accused.suspect.occupation
                    if accused
                    else None
                ),
                "motive": (
                    accused.suspect.motive
                    if accused
                    else None
                ),
            } if accused else None,
            "evidence": evidence_list,
            "narrative": sub.narrative or "",
            "reviewed": sub.reviewed,
            "is_correct": sub.is_correct,
            "reviewer_notes": (
                sub.reviewer_notes or ""
            ),
        })
    completed = [
        c
        for c in cases_json
        if c["outcome"] in [
            "correct",
            "incorrect"
        ]
    ]
    correct_count = sum(
        1
        for c in completed
        if c["outcome"] == "correct"
    )
    conviction_rate = (
        round(
            (correct_count / len(completed)) * 100
        )
        if completed
        else 0
    )
    avg_score = (
        round(
            sum(
                c["score"]
                for c in completed
            ) / len(completed)
        )
        if completed
        else 0
    )
    best_score = max(
        (
            c["score"]
            for c in completed
        ),
        default=0
    )
    return render(
        request,
        "casehistory.html",
        {
            "cases_json": mark_safe(
                json.dumps(cases_json)
            ),
            "conviction_rate": conviction_rate,
            "avg_score": avg_score,
            "best_score": best_score,
        }
    )
def review_submission(request, submission_id):
    submission = get_object_or_404(
        CaseSubmission,
        submission_id=submission_id
    )
    suspects_compare = []
    for row in (
        SubmissionSuspect.objects
        .filter(submission=submission)
        .select_related('suspect')
    ):
        solved = (
            SolutionSuspect.objects
            .filter(
                case_id=submission.case_id,
                suspect=row.suspect
            )
            .first()
        )
        suspects_compare.append({
            'name': row.suspect.name,
            'was_accused': row.is_accused,
            'is_actually_guilty': (
                solved.is_guilty
                if solved
                else None
            ),
            'match': (
                solved is not None
                and row.is_accused == solved.is_guilty
            ),
        })
    evidence_compare = []
    for row in (
        SubmissionEvidence.objects
        .filter(submission=submission)
        .select_related('evidence')
    ):
        solved = (
            SolutionEvidence.objects
            .filter(
                case_id=submission.case_id,
                evidence=row.evidence
            )
            .first()
        )
        evidence_compare.append({
            'item_name': row.evidence.item_name,
            'was_selected': row.is_selected,
            'is_actually_key': (
                solved.is_key_evidence
                if solved
                else None
            ),
            'match': (
                solved is not None
                and row.is_selected == solved.is_key_evidence
            ),
        })
    if request.method == 'POST':
        submission.is_correct = (
            request.POST.get('verdict')
            == 'correct'
        )
        submission.reviewer_notes = (
            request.POST.get(
                'notes',
                ''
            )
        )
        submission.reviewed = True
        submission.save()
    return render(
        request,
        'review.html',
        {
            'submission': submission,
            'suspects_compare': suspects_compare,
            'evidence_compare': evidence_compare,
        }
    )