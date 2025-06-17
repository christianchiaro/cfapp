# main/models.py
from django.db import models
from django.db.models import Q, Sum
from django.utils.timezone import localtime
from collections import defaultdict

# main/models.py - Aggiungi queste proprietà alla classe Tournament

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    status = models.CharField(max_length=20, default='SETUP')

    def __str__(self):
        return self.name
    
    # Nuove proprietà per le statistiche
    @property
    def matches_finished_count(self):
        return self.matches.filter(is_finished=True).count()
    
    @property
    def matches_remaining_count(self):
        return self.matches.filter(is_finished=False).count()
    
    @property
    def matches_total_count(self):
        return self.matches.count()
    
    @property
    def progress_percentage(self):
        if self.matches_total_count == 0:
            return 0
        return round((self.matches_finished_count / self.matches_total_count) * 100)
    
    @property
    def teams_count(self):
        return self.teams.count()
    
    @property
    def matches_by_start_time(self):
        """
        Ritorna un dizionario con le partite raggruppate per orario (start_time).
        """
        grouped = defaultdict(list)
        for match in self.matches.all().order_by('start_time'):
            # Arrotonda l'orario a blocchi precisi (facoltativo)
            key = localtime(match.start_time).strftime('%H:%M')
            grouped[key].append(match)
        return dict(grouped)
    
    def are_groups_filled(self):
        required_teams_per_group = 4

        if self.teams.count() == 0:
            return False  # ❗Nessuna squadra = gruppi non riempiti

        groups = self.teams.values('group').annotate(count=models.Count('group'))

        for group in groups:
            if group['count'] < required_teams_per_group:
                return False
        return True


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

    @property
    def group_points(self):
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
    def goal_difference(self):
        # Gol fatti
        gf_as_team1 = Match.objects.filter(
            team1=self, stage='GROUP', is_finished=True
        ).aggregate(total=models.Sum('score_team1'))['total'] or 0

        gf_as_team2 = Match.objects.filter(
            team2=self, stage='GROUP', is_finished=True
        ).aggregate(total=models.Sum('score_team2'))['total'] or 0

        goals_for = gf_as_team1 + gf_as_team2

        # Gol subiti
        ga_as_team1 = Match.objects.filter(
            team1=self, stage='GROUP', is_finished=True
        ).aggregate(total=models.Sum('score_team2'))['total'] or 0

        ga_as_team2 = Match.objects.filter(
            team2=self, stage='GROUP', is_finished=True
        ).aggregate(total=models.Sum('score_team1'))['total'] or 0

        goals_against = ga_as_team1 + ga_as_team2

        return goals_for - goals_against


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
    start_time = models.DateTimeField(null=True, blank=True)
    field = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def duration_minutes(self):
        return 30 if self.stage == 'GROUP' else 60

    def __str__(self):
        return f"{self.team1} vs {self.team2} ({self.get_stage_display()})"
