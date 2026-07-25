from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path("", views.dashboard, name="home"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cases/", views.cases, name="cases"),
    path("casehistory/", views.casehistory, name="casehistory"),
    path("heist/", views.heist, name="heist"),

    # Case pages
    path(
        "case/<int:case_id>/suspects/",
        views.suspects,
        name="suspects"
    ),
    path(
        "case/<int:case_id>/evidence/",
        views.evidence,
        name="evidence"
    ),

    # Case resolution
    path(
        "resolution/",
        views.case_resolution,
        name="caseresolution"
    ),
    path(
        "case/<int:case_id>/resolution/",
        views.case_resolution,
        name="caseresolution"
    ),

    # Case solving
    # Fixed: views.solve_case does not exist in views.py
    path(
        "case/<int:case_id>/solve/",
        views.case_resolution,
        name="solve_case"
    ),

    # Suspect accusation
    path(
        "case/<int:case_id>/suspects/<int:suspect_id>/accuse/",
        views.toggle_accuse,
        name="toggle_accuse"
    ),

    # Evidence selection
    path(
        "case/<int:case_id>/evidence/<int:evidence_id>/toggle/",
        views.toggle_evidence,
        name="toggle_evidence"
    ),

    # Submission state
    path(
        "case/<int:case_id>/submission-state/",
        views.submission_state,
        name="submission_state"
    ),

    # Save narrative
    path(
        "case/<int:case_id>/narrative/",
        views.save_narrative,
        name="save_narrative"
    ),

    # Case analysis
    path(
        "analysis/<int:case_id>/",
        views.analysis,
        name="analysis"
    ),

    # Review a submission
    path(
        "analysis/submission/<int:submission_id>/",
        views.review_submission,
        name="review_submission"
    ),
]