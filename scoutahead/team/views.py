from django.shortcuts import render
from team.models import Game, Player, Team

def team_profile(request, pk):
    team = Team.objects.get(pk=pk)
    context = {
        'team': team
    }
    return render(request, 'team_profile.html', context)