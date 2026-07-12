from django.urls import path
from . import views

urlpatterns = [
    # pages
    path('', views.dashboard, name='dashboard'),
    path('cases/', views.cases, name='cases'),
    
]