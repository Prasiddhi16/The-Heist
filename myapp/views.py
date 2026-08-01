import json
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.urls import reverse
from django.db.models import Sum, Count, Avg

from .models import (
    Case,
    UserProfile,
    Suspect,
    Evidence,
    CaseSubmission,
    SubmissionSuspect,
    SubmissionEvidence,
    SolutionSuspect,
    SolutionEvidence
)


def get_supabase_user_id(request):
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        user_id = request.GET.get("user_id")

    if not user_id:
        user_id = request.POST.get("user_id")

    if not user_id:
        return None

    try:
        return uuid.UUID(str(user_id))
    except (ValueError, AttributeError, TypeError):
        return None


def _get_or_create_submission(case_id, submission_id, user_id=None):
    if submission_id:
        existing = CaseSubmission.objects.filter(
            submission_id=submission_id, case_id=case_id, user_id=user_id
        ).first()

        if existing:
            return existing

    submission = CaseSubmission.objects.create(case_id=case_id, user_id=user_id)

    SubmissionSuspect.objects.bulk_create([
        SubmissionSuspect(submission=submission, suspect=suspect, is_accused=False)
        for suspect in Suspect.objects.filter(case_id=case_id)
    ])

    SubmissionEvidence.objects.bulk_create([
        SubmissionEvidence(submission=submission, evidence=evidence, is_selected=False)
        for evidence in Evidence.objects.filter(case_id=case_id)
    ])

    return submission


@csrf_exempt
def toggle_accuse(request, case_id, suspect_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = get_supabase_user_id(request)

    if not user_id:
        body_user_id = body.get("user_id")

        if body_user_id:
            try:
                user_id = uuid.UUID(str(body_user_id))
            except (ValueError, AttributeError, TypeError):
                user_id = None

    submission = _get_or_create_submission(case_id, body.get("submission_id"), user_id)

    if body.get("unset"):
        SubmissionSuspect.objects.filter(submission=submission).update(is_accused=False)

        return JsonResponse({
            "submission_id": str(submission.submission_id),
            "accused_suspect_id": None
        })

    suspect = get_object_or_404(Suspect, suspect_id=suspect_id, case_id=case_id)

    SubmissionSuspect.objects.filter(submission=submission).update(is_accused=False)

    SubmissionSuspect.objects.filter(submission=submission, suspect=suspect).update(is_accused=True)

    return JsonResponse({
        "submission_id": str(submission.submission_id),
        "accused_suspect_id": suspect.suspect_id
    })


@csrf_exempt
def toggle_evidence(request, case_id, evidence_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = get_supabase_user_id(request)

    if not user_id:
        body_user_id = body.get("user_id")

        if body_user_id:
            try:
                user_id = uuid.UUID(str(body_user_id))
            except (ValueError, AttributeError, TypeError):
                user_id = None

    submission = _get_or_create_submission(case_id, body.get("submission_id"), user_id)

    evidence = get_object_or_404(Evidence, evidence_id=evidence_id, case_id=case_id)

    row, created = SubmissionEvidence.objects.get_or_create(submission=submission, evidence=evidence)

    row.is_selected = not row.is_selected
    row.save()

    return JsonResponse({
        "submission_id": str(submission.submission_id),
        "evidence_id": evidence_id,
        "is_selected": row.is_selected
    })


def submission_state(request, case_id):
    submission_id = request.GET.get("submission_id")

    user_id = get_supabase_user_id(request)

    if not submission_id:
        return JsonResponse({
            "accused_suspect_id": None,
            "selected_evidence_ids": [],
            "narrative": ""
        })

    submission = CaseSubmission.objects.filter(
        submission_id=submission_id, case_id=case_id, user_id=user_id
    ).first()

    if not submission:
        return JsonResponse({"error": "Submission not found"}, status=404)

    accused = SubmissionSuspect.objects.filter(submission=submission, is_accused=True).first()

    selected = list(
        SubmissionEvidence.objects
        .filter(submission=submission, is_selected=True)
        .values_list("evidence_id", flat=True)
    )

    return JsonResponse({
        "submission_id": str(submission.submission_id),
        "accused_suspect_id": accused.suspect_id if accused else None,
        "selected_evidence_ids": selected,
        "narrative": submission.narrative or ""
    })


@csrf_exempt
def save_narrative(request, case_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    submission_id = body.get("submission_id")

    if not submission_id:
        return JsonResponse({"error": "submission_id is required"}, status=400)

    user_id = get_supabase_user_id(request)

    if not user_id:
        body_user_id = body.get("user_id")

        if body_user_id:
            try:
                user_id = uuid.UUID(str(body_user_id))
            except (ValueError, AttributeError, TypeError):
                user_id = None

    submission = CaseSubmission.objects.filter(
        submission_id=submission_id, case_id=case_id, user_id=user_id
    ).first()

    if not submission:
        return JsonResponse({"error": "Submission not found"}, status=404)

    submission.narrative = body.get("narrative", "")

    submission.save(update_fields=["narrative"])

    return JsonResponse({
        "success": True,
        "submission_id": str(submission.submission_id)
    })


def login(request):
    context = {
        "supabase_url": getattr(settings, "SUPABASE_URL", ""),
        "supabase_anon_key": getattr(settings, "SUPABASE_ANON_KEY", ""),
    }

    return render(request, "login.html", context)


def dashboard(request):
    case = Case.objects.order_by("-created_at").first()

    return render(request, "dashboard.html", {"case": case})


def cases(request):
    return render(request, "cases.html", {"cases": Case.objects.all()})


def heist(request):
    return render(request, "heist.html")


def suspects(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)

    suspect_list = Suspect.objects.filter(case_id=case_id)

    return render(request, "suspects.html", {"case": case, "suspects": suspect_list})


def evidence(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)

    return render(request, "evidence.html", {
        "case": case,
        "evidence_items": case.evidence_items.all()
    })


def case_resolution(request, case_id=None):
    if case_id is None:
        cases = Case.objects.all().order_by("-created_at")

        return render(request, "caseresolution.html", {"case": None, "cases": cases})

    case = get_object_or_404(Case, case_id=case_id)

    return render(request, "caseresolution.html", {
        "case": case,
        "suspects": Suspect.objects.filter(case_id=case_id),
        "evidence_items": Evidence.objects.filter(case_id=case_id)
    })


def analysis(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)

    user_id = get_supabase_user_id(request)

    submission_id = request.GET.get("submission_id")

    submission = None

    if submission_id:
        submission = CaseSubmission.objects.filter(
            submission_id=submission_id, case_id=case_id
        ).first()

        if submission and user_id:
            if str(submission.user_id) != str(user_id):
                submission = None

    if not submission and user_id:
        submission = CaseSubmission.objects.filter(
            case_id=case_id, user_id=user_id
        ).order_by("-submitted_at").first()

    selected_suspect = None
    selected_evidence = []

    if submission:
        accused_row = SubmissionSuspect.objects.filter(
            submission=submission, is_accused=True
        ).select_related("suspect").first()

        if accused_row:
            selected_suspect = accused_row.suspect

        selected_evidence_ids = SubmissionEvidence.objects.filter(
            submission=submission, is_selected=True
        ).values_list("evidence_id", flat=True)

        selected_evidence = list(
            Evidence.objects.filter(case_id=case_id, evidence_id__in=selected_evidence_ids)
        )

    evidence_total = Evidence.objects.filter(case_id=case_id).count()

    evidence_collected = len(selected_evidence)

    evidence_score = (evidence_collected / evidence_total) * 70 if evidence_total > 0 else 0

    suspect_score = 30 if selected_suspect else 0

    readiness_score = round(evidence_score + suspect_score)

    can_file_verdict = (
        selected_suspect is not None
        and evidence_collected > 0
        and submission is not None
        and submission.is_correct is None
    )

    top_suspect = Suspect.objects.filter(case_id=case_id).order_by("suspect_id").first()

    verdict_done = submission is not None and submission.is_correct is not None

    verdict_correct = bool(submission.is_correct) if verdict_done else False

    verdict_score = submission.score if verdict_done else 0

    verdict_notes = submission.reviewer_notes if verdict_done else ""

    return render(request, "analysis.html", {
        "case": case,
        "submission": submission,
        "selected_suspect": selected_suspect,
        "selected_evidence": selected_evidence,
        "evidence_collected": evidence_collected,
        "evidence_total": evidence_total,
        "readiness_score": readiness_score,
        "top_suspect": top_suspect,
        "can_file_verdict": can_file_verdict,
        "verdict_done": verdict_done,
        "verdict_correct": verdict_correct,
        "verdict_score": verdict_score,
        "verdict_notes": verdict_notes
    })


@transaction.atomic
def solve_case(request, case_id):
    case = get_object_or_404(Case, case_id=case_id)

    if request.method != "POST":
        return redirect("analysis", case_id=case_id)

    user_id = get_supabase_user_id(request)

    if not user_id:
        user_id = request.POST.get("user_id")

        if user_id:
            try:
                user_id = uuid.UUID(str(user_id))
            except (ValueError, AttributeError, TypeError):
                user_id = None

    submission_id = request.POST.get("submission_id")

    if not submission_id:
        return redirect("analysis", case_id=case_id)

    submission = CaseSubmission.objects.filter(
        submission_id=submission_id, case_id=case_id
    ).first()

    if not submission:
        return redirect("analysis", case_id=case_id)

    if user_id:
        if str(submission.user_id) != str(user_id):
            return redirect("analysis", case_id=case_id)

    accused = SubmissionSuspect.objects.filter(submission=submission, is_accused=True).first()

    guilty = SolutionSuspect.objects.filter(case_id=case_id, is_guilty=True).first()

    suspect_correct = (
        accused is not None
        and guilty is not None
        and accused.suspect_id == guilty.suspect_id
    )

    user_evidence = set(
        SubmissionEvidence.objects
        .filter(submission=submission, is_selected=True)
        .values_list("evidence_id", flat=True)
    )

    correct_evidence = set(
        SolutionEvidence.objects
        .filter(case_id=case_id, is_key_evidence=True)
        .values_list("evidence_id", flat=True)
    )

    evidence_correct = user_evidence == correct_evidence

    if suspect_correct and evidence_correct:
        submission.is_correct = True
        submission.score = 100
        submission.reviewer_notes = "Correct suspect and correct evidence selected."

    else:
        submission.is_correct = False

        score = 10

        if suspect_correct:
            score += 40

        if evidence_correct:
            score += 40

        submission.score = score

        if suspect_correct and not evidence_correct:
            submission.reviewer_notes = (
                "Correct suspect, but the selected evidence does not "
                "completely match the key evidence."
            )

        elif not suspect_correct and evidence_correct:
            submission.reviewer_notes = (
                "Correct evidence selected, but the accused suspect does not "
                "match the official solution."
            )

        else:
            submission.reviewer_notes = (
                "The selected suspect and evidence do not completely match "
                "the official solution."
            )

    submission.save(update_fields=["is_correct", "score", "reviewer_notes"])
    print("VERDICT SAVED:", submission.submission_id, submission.user_id, submission.is_correct, submission.score)

    if user_id:
        user_profile = UserProfile.objects.filter(user_id=user_id).first()

        if user_profile:
            completed_submissions = CaseSubmission.objects.filter(
                user_id=user_id, is_correct__isnull=False, score__isnull=False
            )

            solved_count = completed_submissions.count()

            total_score = completed_submissions.aggregate(total=Sum("score"))["total"] or 0

            average_score = round(total_score / solved_count) if solved_count > 0 else 0

            user_profile.cases_solved = solved_count
            user_profile.score = total_score

            if hasattr(user_profile, "average_score"):
                user_profile.average_score = average_score

            update_fields = ["cases_solved", "score", "updated_at"]

            if hasattr(user_profile, "average_score"):
                update_fields.append("average_score")

            user_profile.save(update_fields=update_fields)

    request.session[f"verdict_{case_id}"] = {
        "done": True,
        "correct": submission.is_correct,
        "score": submission.score,
        "notes": submission.reviewer_notes
    }

    return redirect(
        f"{reverse('analysis', kwargs={'case_id': case_id})}?submission_id={submission.submission_id}"
    )


def casehistory(request):
    user_id = get_supabase_user_id(request)

    if not user_id:
        return render(request, "casehistory.html", {
            "cases_json": [],
            "conviction_rate": 0,
            "avg_score": 0,
            "best_score": 0,
            "user": None
        })

    user = UserProfile.objects.filter(user_id=user_id).first()

    submissions = CaseSubmission.objects.filter(
        user_id=user_id, is_correct__isnull=False
    ).select_related("case").order_by("-submitted_at")

    cases_json = []

    for sub in submissions:
        accused = SubmissionSuspect.objects.filter(
            submission=sub, is_accused=True
        ).select_related("suspect").first()

        selected_evidence = SubmissionEvidence.objects.filter(
            submission=sub, is_selected=True
        ).select_related("evidence")

        evidence_list = [row.evidence.item_name for row in selected_evidence]

        correct_evidence = set(
            SolutionEvidence.objects
            .filter(case_id=sub.case_id, is_key_evidence=True)
            .values_list("evidence_id", flat=True)
        )

        selected_evidence_ids = set(row.evidence_id for row in selected_evidence)

        evidence_accuracy = (
            round(len(selected_evidence_ids & correct_evidence) / len(correct_evidence) * 100)
            if correct_evidence
            else 0
        )

        guilty = SolutionSuspect.objects.filter(case_id=sub.case_id, is_guilty=True).first()

        suspect_accuracy = (
            100
            if (accused and guilty and accused.suspect_id == guilty.suspect_id)
            else 0
        )

        accuracy = round((evidence_accuracy + suspect_accuracy) / 2)

        outcome = "correct" if sub.is_correct is True else "incorrect"

        cases_json.append({
            "id": str(sub.submission_id),
            "case_id": sub.case.case_number,
            "title": sub.case.title,
            "date_solved": sub.submitted_at.strftime("%Y-%m-%d") if sub.submitted_at else "",
            "status": "closed",
            "outcome": outcome,
            "accuracy": accuracy,
            "score": sub.score or 0,
            "suspect": {
                "name": accused.suspect.name,
                "occupation": accused.suspect.occupation,
                "motive": accused.suspect.motive
            } if accused else None,
            "evidence": evidence_list,
            "narrative": sub.narrative or "",
            "reviewed": sub.reviewed,
            "is_correct": sub.is_correct,
            "reviewer_notes": sub.reviewer_notes or ""
        })

    completed = cases_json

    correct_count = sum(1 for case_data in completed if case_data["outcome"] == "correct")

    conviction_rate = round(correct_count / len(completed) * 100) if completed else 0

    avg_score = (
        round(sum(case_data["score"] for case_data in completed) / len(completed))
        if completed
        else 0
    )

    best_score = max((case_data["score"] for case_data in completed), default=0)

    return render(request, "casehistory.html", {
        "cases_json": cases_json,
        "conviction_rate": conviction_rate,
        "avg_score": avg_score,
        "best_score": best_score,
        "user": user
    })


def review_submission(request, submission_id):
    submission = get_object_or_404(CaseSubmission, submission_id=submission_id)

    suspects_compare = []

    for row in SubmissionSuspect.objects.filter(submission=submission).select_related("suspect"):
        solved = SolutionSuspect.objects.filter(
            case_id=submission.case_id, suspect=row.suspect
        ).first()

        suspects_compare.append({
            "name": row.suspect.name,
            "was_accused": row.is_accused,
            "is_actually_guilty": solved.is_guilty if solved else None,
            "match": solved is not None and row.is_accused == solved.is_guilty
        })

    evidence_compare = []

    for row in SubmissionEvidence.objects.filter(submission=submission).select_related("evidence"):
        solved = SolutionEvidence.objects.filter(
            case_id=submission.case_id, evidence=row.evidence
        ).first()

        evidence_compare.append({
            "item_name": row.evidence.item_name,
            "was_selected": row.is_selected,
            "is_actually_key": solved.is_key_evidence if solved else None,
            "match": solved is not None and row.is_selected == solved.is_key_evidence
        })

    if request.method == "POST":
        submission.is_correct = request.POST.get("verdict") == "correct"
        submission.reviewer_notes = request.POST.get("notes", "")
        submission.reviewed = True
        submission.save()

    return render(request, "review.html", {
        "submission": submission,
        "suspects_compare": suspects_compare,
        "evidence_compare": evidence_compare
    })


def leaderboard(request):
    users = UserProfile.objects.all()

    leaderboard_data = []

    for user in users:
        completed_submissions = CaseSubmission.objects.filter(
            user_id=user.user_id, is_correct__isnull=False, score__isnull=False
        )

        cases_solved = completed_submissions.count()

        if cases_solved == 0:
            continue

        total_score = completed_submissions.aggregate(total=Sum("score"))["total"] or 0

        average_score = round(total_score / cases_solved)

        correct_cases = completed_submissions.filter(is_correct=True).count()

        incorrect_cases = cases_solved - correct_cases

        accuracy = round(correct_cases / cases_solved * 100)

        leaderboard_data.append({
            "investigator": user.full_name if user.full_name else user.username,
            "username": user.username,
            "rank": user.rank or "Rookie",
            "cases_solved": cases_solved,
            "correct_cases": correct_cases,
            "incorrect_cases": incorrect_cases,
            "total_score": total_score,
            "average_score": average_score,
            "accuracy": accuracy
        })

    leaderboard_data.sort(
        key=lambda x: (x["average_score"], x["total_score"], x["cases_solved"]),
        reverse=True
    )

    for index, entry in enumerate(leaderboard_data, start=1):
        entry["position"] = index

    return render(request, "leaderboard.html", {"leaderboard": leaderboard_data})