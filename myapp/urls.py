from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cases/", views.cases, name="cases"),
    path("casehistory/", views.casehistory, name="casehistory"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("heist/", views.heist, name="heist"),
    path(
    "api/set-session-user/",
    views.set_session_user,
    name="set_session_user",
),

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
    path('api/search/', views.global_search, name='global_search'),
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

    path(
    "case/<int:case_id>/solve/",
    views.solve_case,
    name="solve_case"
),

    path(
        "case/<int:case_id>/suspects/<int:suspect_id>/accuse/",
        views.toggle_accuse,
        name="toggle_accuse"
    ),

    path(
        "case/<int:case_id>/evidence/<int:evidence_id>/toggle/",
        views.toggle_evidence,
        name="toggle_evidence"
    ),

    path(
        "case/<int:case_id>/submission-state/",
        views.submission_state,
        name="submission_state"
    ),

    path(
        "case/<int:case_id>/narrative/",
        views.save_narrative,
        name="save_narrative"
    ),

    path(
        "analysis/<int:case_id>/",
        views.analysis,
        name="analysis"
    ),

    path(
        "analysis/submission/<int:submission_id>/",
        views.review_submission,
        name="review_submission"
    ),
    
]