from django.contrib import admin
from team.models import Player, Team, Game

class PlayerAdmin(admin.ModelAdmin):
    pass

class TeamAdmin(admin.ModelAdmin):
    pass

class GameAdmin(admin.ModelAdmin):
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Game, GameAdmin)
