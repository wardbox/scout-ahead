from django.shortcuts import render
from team.models import Game, Player, Team

def team_profile(request, pk):
    team = Team.objects.get(pk=pk)
    players = team.players
    context = {
        'team': team,
        'players': players.all()
    }
    return render(request, 'team_profile.html', context)

def player_detail(request, handle):
    player = Player.objects.get(handle=handle)
    context = {
        'player': player
    }
    return render(request, 'player_detail.html', context)