from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="home"), 
    path("case/<int:case_id>/suspects/", views.suspects, name="suspects"),
    path("case/<int:case_id>/evidence/", views.evidence, name="evidence"),
    path('login/', views.login, name='login'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("casehistory/", views.casehistory, name="casehistory"),
    path("analysis/", views.analysis, name="analysis"), 
    path("cases/", views.cases, name="cases"),
    path("heist/", views.heist, name="heist"),
    path('resolution/', views.case_resolution, name='caseresolution'),
    path('case/<int:case_id>/resolution/', views.case_resolution, name='caseresolution'),
]
