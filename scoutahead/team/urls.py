from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.team_profile, name='team_profile'),
    path("<str:handle>/", views.player_detail, name='player_detail'),
]
