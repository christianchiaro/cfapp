from django.contrib import admin
from .models import Tournament, Player, Team, Match

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'status')
    search_fields = ('name',)
    list_filter = ('status', 'start_date')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'player1', 'player2', 'group')
    list_filter = ('tournament', 'group')
    search_fields = ('name',)
    raw_id_fields = ('player1', 'player2')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'team1', 'score_team1', 'score_team2', 'team2', 'stage', 'is_finished')
    list_filter = ('stage', 'is_finished', 'tournament')
    search_fields = ('team1__name', 'team2__name')
