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
    def all_matches_finished(self):
        return self.matches_remaining_count == 0

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

    @property
    def standings_by_group(self):
        """
        Restituisce un dizionario con i team divisi per gruppo e ordinati
        prima per punti, poi per differenza reti (goal_difference).
        """
        standings = defaultdict(list)
        for team in self.teams.all():
            if team.group:
                standings[team.group].append(team)

        for group in standings:
            standings[group].sort(key=lambda t: (t.group_points, t.goal_difference), reverse=True)

        return dict(standings)

    @property
    def final_rankings(self):
        ranks = [None] * 8
        stage_map = {
            'FINAL_1_2': (0, 1),
            'FINAL_3_4': (2, 3),
            'FINAL_5_6': (4, 5),
            'FINAL_7_8': (6, 7),
        }

        for stage, (winner_pos, loser_pos) in stage_map.items():
            match = self.matches.filter(stage=stage, is_finished=True).first()
            if match and match.team1 and match.team2:
                winner = match.winner()
                loser = match.team2 if winner == match.team1 else match.team1
                ranks[winner_pos] = winner
                ranks[loser_pos] = loser

        return ranks

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
        ('SEMI_FINAL', 'Semifinale'),
        ('FINAL_1_2', 'Finale'),
        ('FINAL_3_4', '3º-4º posto'),
        ('FINAL_5_6', '5º-6º posto'),
        ('FINAL_7_8', '7º-8º posto'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1', null=True, blank=True)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', null=True, blank=True)
    score_team1 = models.PositiveIntegerField(default=0)
    score_team2 = models.PositiveIntegerField(default=0)
    set1_team1 = models.PositiveIntegerField(null=True, blank=True)
    set1_team2 = models.PositiveIntegerField(null=True, blank=True)
    set2_team1 = models.PositiveIntegerField(null=True, blank=True)
    set2_team2 = models.PositiveIntegerField(null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    is_finished = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    field = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def duration_minutes(self):
        return 30 if self.stage == 'GROUP' else 60

    def winner(self):
        if not self.is_finished or not self.team1 or not self.team2:
            return None

        if self.stage in ['FINAL_1_2', 'FINAL_3_4']:
            team1_sets = (self.set1_team1 > self.set1_team2) + (self.set2_team1 > self.set2_team2)
            team2_sets = (self.set1_team2 > self.set1_team1) + (self.set2_team2 > self.set2_team1)

            if team1_sets > team2_sets:
                return self.team1
            elif team2_sets > team1_sets:
                return self.team2
            else:
                punti_team1 = (self.set1_team1 or 0) + (self.set2_team1 or 0)
                punti_team2 = (self.set1_team2 or 0) + (self.set2_team2 or 0)
                return self.team1 if punti_team1 > punti_team2 else self.team2
        else:
            return self.team1 if self.score_team1 > self.score_team2 else self.team2
