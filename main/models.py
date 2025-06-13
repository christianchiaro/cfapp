# main/models.py
from django.db import models
from django.db.models import Q, Sum

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    # Potremmo aggiungere uno stato: 'SETUP', 'GROUP_STAGE', 'KNOCKOUT', 'FINISHED'
    status = models.CharField(max_length=20, default='SETUP')

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='teams_p1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='teams_p2')
    group = models.CharField(max_length=1, choices=[('A', 'Group A'), ('B', 'Group B')], null=True, blank=True)

    def __str__(self):
        return self.name

    # Proprietà calcolata per ottenere i punti nel girone
    @property
    def group_points(self):
        # 3 punti per la vittoria, 1 per il pareggio
        wins = Match.objects.filter(
            Q(team1=self, score_team1__gt=models.F('score_team2')) |
            Q(team2=self, score_team2__gt=models.F('score_team1')),
            stage='GROUP', is_finished=True
        ).count()
        draws = Match.objects.filter(
            Q(team1=self) | Q(team2=self),
            score_team1=models.F('score_team2'),
            stage='GROUP', is_finished=True
        ).count()
        return (wins * 3) + (draws * 1)
        
    @property
    def games_played(self):
         return Match.objects.filter(Q(team1=self) | Q(team2=self), stage='GROUP', is_finished=True).count()


class Match(models.Model):
    STAGE_CHOICES = [
        ('GROUP', 'Group Stage'),
        ('SEMI_FINAL', 'Semi Final'),
        ('FINAL_1_2', 'Final 1st-2nd'),
        ('FINAL_3_4', 'Final 3rd-4th'),
        ('FINAL_5_6', 'Final 5th-6th'),
        ('FINAL_7_8', 'Final 7th-8th'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    score_team1 = models.PositiveIntegerField(default=0)
    score_team2 = models.PositiveIntegerField(default=0)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    is_finished = models.BooleanField(default=False)
    
    @property
    def duration_minutes(self):
        return 30 if self.stage == 'GROUP' else 60

    def __str__(self):
        return f"{self.team1} vs {self.team2} ({self.get_stage_display()})"