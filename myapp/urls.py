from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cases/", views.cases, name="cases"),
    path("heist/", views.heist, name="heist"),
]
