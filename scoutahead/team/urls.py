from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.team_profile, name='team_profile'),
]
