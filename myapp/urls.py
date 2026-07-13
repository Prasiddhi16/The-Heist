from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),          # root → login
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cases/", views.cases, name="cases"),
    path("heist/", views.heist, name="heist"),
    path("cases/<int:case_id>/suspects/", views.suspects, name="suspects"),
    path("cases/<int:case_id>/evidence/", views.evidence, name="evidence"),
]
