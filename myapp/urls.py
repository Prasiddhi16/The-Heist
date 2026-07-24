from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="home"), 
    
    path("case/<int:case_id>/suspects/", views.suspects, name="suspects"),
    path("case/<int:case_id>/evidence/", views.evidence, name="evidence"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cases/", views.cases, name="cases"),
    path("heist/", views.heist, name="heist"),
    path("resolution/", views.caseresolution, name="caseresolution"),
]
