from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import IntegrityError
from django.db.models import Count, Q
from django.utils.timezone import make_aware
from datetime import datetime, time, timedelta
from main.models import Tournament, Team, Player, Match
from itertools import combinations, chain
from collections import defaultdict, deque
import random
from django.db import transaction
from django.utils.text import slugify
from django.db import transaction

def aggiorna_messages(request):
    html = render_to_string('main/partials/components/toasts/toast.html', request=request)
    return HttpResponse(html)

def homepage(request):
    tornei = Tournament.objects.all().order_by('-start_date')
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/homepage/home.html', {'tornei': tornei})
    else:
        return render(request, 'base.html', {'tornei': tornei})

def homepage_partial(request):
    tornei = Tournament.objects.all().order_by('-start_date')
    return render(request, 'main/partials/homepage/home.html', {'tornei': tornei})

def elimina_torneo_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    torneo.delete()
    messages.success(request, "Torneo eliminato con successo.")
    tornei = Tournament.objects.all().order_by('-start_date')
    html = render_to_string('main/partials/homepage/home.html', {'tornei': tornei}, request=request)
    response = HttpResponse(html)
    response['HX-Trigger'] = 'refreshMessages'
    return response

def crea_torneo_partial(request):
    if request.method == "GET":
        # Controlla se è una richiesta HTMX
        if request.headers.get('HX-Request'):
            return render(request, 'main/partials/torneo/home.html')
        else:
            # Se non è HTMX, restituisci la pagina completa
            return render(request, 'base.html', {'content_template': 'main/partials/torneo/home.html'})
    
    if request.method == "POST":
        name = request.POST.get('name')
        start_date_raw = request.POST.get('start_date')
        if not name or not start_date_raw:
            messages.error(request, "Nome e data di inizio sono obbligatori!")
            response = HttpResponse(status=400)
            response['HX-Trigger'] = 'refreshMessages'
            return response

        try:
            start_date = datetime.strptime(start_date_raw, "%Y-%m-%dT%H:%M")
        except ValueError:
            messages.error(request, "Formato data/ora non valido.")
            response = HttpResponse(status=400)
            response['HX-Trigger'] = 'refreshMessages'
            return response

        try:
            tournament = Tournament.objects.create(name=name, start_date=start_date)
            messages.success(request, f"Torneo {tournament.name} creato correttamente")
            response = HttpResponse()
            response['HX-Trigger'] = 'refreshMessages'
            response['HX-Redirect'] = reverse('home_torneo', args=[tournament.id])
            return response
        except Exception as e:
            messages.error(request, f'Errore durante la creazione: {str(e)}')
            response = HttpResponse(status=500)
            response['HX-Trigger'] = 'refreshMessages'
            return response

    return render(request, 'main/partials/torneo/home.html')

def home_torneo_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/home-torneo.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})

def gestisci_partecipanti_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)

    # 🔄 Se è POST, aggiungi partecipante
    if request.method == "POST":
        nome = request.POST.get("nome")
        if nome:
            Player.objects.create(name=nome)

    # 🔍 Sempre aggiorna i dati
    players = Player.objects.all()
    player_teams = {
        player: list(chain(
            player.teams_p1.filter(tournament=torneo),
            player.teams_p2.filter(tournament=torneo)
        )) for player in players
    }

    context = {
        'torneo': torneo,
        'player_teams': player_teams,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_giocatori.html', context)
    else:
        return render(request, 'base.html', context)

def gestisci_partecipanti_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)

    # 🔄 Se è POST, prova ad aggiungere un partecipante
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        if nome:
            nome = nome.title()

            # Controlla se ha già raggiunto 16 partecipanti
            player_ids = set(
                Team.objects.filter(tournament=torneo).values_list('player1_id', flat=True)
            ).union(
                Team.objects.filter(tournament=torneo).values_list('player2_id', flat=True)
            )
            free_players = Player.objects.exclude(id__in=player_ids)

            if Player.objects.count() >= 16 and nome not in [p.name for p in free_players]:
                messages.error(request, "Hai raggiunto il numero massimo di 16 partecipanti.")
            else:
                player, created = Player.objects.get_or_create(name=nome)

                if not created:
                    is_in_team = Team.objects.filter(tournament=torneo).filter(
                        Q(player1=player) | Q(player2=player)
                    ).exists()

                    if is_in_team:
                        messages.error(request, f"{player.name} è già in una squadra di questo torneo.")
                    else:
                        messages.info(request, f"{player.name} era già presente, ma non assegnato a nessuna squadra.")
                else:
                    messages.success(request, f"Giocatore {player.name} aggiunto con successo.")

    # 🔍 Aggiorna dati sempre
    players = Player.objects.all()
    player_teams = {
        player: list(chain(
            player.teams_p1.filter(tournament=torneo),
            player.teams_p2.filter(tournament=torneo)
        )) for player in players
    }

    context = {
        'torneo': torneo,
        'player_teams': player_teams,
    }

    if request.headers.get('HX-Request'):
        response = render(request, 'main/partials/torneo/gestisci_giocatori.html', context)
    else:
        response = render(request, 'base.html', context)

    response['HX-Trigger'] = 'refreshMessages'
    return response
    
# Lista di almeno 50 nomi divertenti
NOMI_DIVERTENTI = [
    "Padeloni Furiosi", "Smash Brothers", "Gli Incordati", "Team Bandeja", "Padel No Cry",
    "Ace Ventura", "La Doppia Parete", "I Ribattitori", "Let's Padel", "I Pallettari",
    "Padel & Furious", "Gli Smashati", "Serve & Spritz", "Tanta Roba Padel", "Set & Muretto",
    "Gli Scappati di Casa", "The Net Set", "Gli Acefali", "Smash & Go", "Team Vibora",
    "Gli Arrabbiati", "The Racchettari", "Paddle Pop", "Racchette Spaziali", "Colpi Proibiti",
    "Padelwood", "Viva la Vibora", "Tennis Who?", "Palla Viva", "I Padelisti Anonimi",
    "Palle al Muro", "Doppio Fallo", "Gli Addobbati", "Match Pointless", "I Tappetoni",
    "Re della Gabbia", "La Chiamata Out", "Padel is the New Black", "Gabbia Time",
    "Paddle Express", "Team Pallonetto", "Sotto Rete", "I Padelizzati", "The 40-30",
    "Bandeja Boys", "Non Vale il Vetri", "Palle Sgonfie", "Game, Set, Spritz",
    "I Muri Parlano", "Stiamo a Padel", "Padel Power", "Break Time", "I Raccattapalle"
]

def shuffle_partecipanti_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    players = list(Player.objects.all())

    # Identifica giocatori già inseriti in una squadra del torneo
    player_in_team_ids = set(chain(
        Team.objects.filter(tournament=torneo).values_list('player1_id', flat=True),
        Team.objects.filter(tournament=torneo).values_list('player2_id', flat=True),
    ))
    players_without = [p for p in players if p.id not in player_in_team_ids]

    def generate_unique_name(used):
        nome = random.choice(NOMI_DIVERTENTI)
        k = 1
        base = nome
        while nome in used:
            nome = f"{base} {k}"
            k += 1
        used.add(nome)
        return nome

    used_names = set()
    with transaction.atomic():
        if players_without:
            random.shuffle(players_without)
            for i in range(0, len(players_without), 2):
                if i + 1 >= len(players_without): break
                p1, p2 = players_without[i], players_without[i+1]
                team_name = generate_unique_name(used_names)
                group = random.choice(['A', 'B'])
                Team.objects.create(
                    name=team_name,
                    tournament=torneo,
                    player1=p1,
                    player2=p2,
                    group=group
                )
        else:
            if not request.user.is_authenticated:
                messages.error(request, f'Solo il mio capo supremo Christian può fare reshuffle.')
                response = HttpResponse(status=500)
                response['HX-Trigger'] = 'refreshMessages'
                return response

            Team.objects.filter(tournament=torneo).delete()
            random.shuffle(players)
            for i in range(0, len(players), 2):
                if i + 1 >= len(players): break
                p1, p2 = players[i], players[i+1]
                team_name = generate_unique_name(used_names)
                group = random.choice(['A', 'B'])
                Team.objects.create(
                    name=team_name,
                    tournament=torneo,
                    player1=p1,
                    player2=p2,
                    group=group
                )

    return gestisci_partecipanti_partial(request, torneo_id)

def regolamento_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all()
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/regolamento.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})

def gestisci_squadre_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all()
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})

def gestisci_squadre_create_team(request, torneo_id):
    """View per creare una nuova squadra"""
    if request.method == 'POST':
        team_name = request.POST.get('team_name', '').strip().title()
        player1_name = request.POST.get('player1', '').strip().title()
        player2_name = request.POST.get('player2', '').strip().title()
        group = request.POST.get('group')
        tournament_id = request.POST.get('tournament_id')
        torneo = get_object_or_404(Tournament, id=tournament_id)
        teams = torneo.teams.all()  

        try:
            # Validazioni
            if not all([team_name, player1_name, player2_name, tournament_id]):
                messages.error(request, 'Tutti i campi obbligatori devono essere compilati.')
                response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
                response['HX-Trigger'] = 'refreshMessages'
                return response

            if player1_name == player2_name:
                messages.error(request, 'I due giocatori devono essere diversi.')
                response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
                response['HX-Trigger'] = 'refreshMessages'
                return response

            # Se non è loggato e specifica il girone, blocca
            if group and not request.user.is_authenticated:
                messages.error(request, 'Lascia il campo Girone vuoto. Non sei il mio capo supremo.')
                response = HttpResponse(status=500)
                response['HX-Trigger'] = 'refreshMessages'
                return response
            
            # Recupera gli oggetti
            tournament = get_object_or_404(Tournament, id=tournament_id)
            player1, created = Player.objects.get_or_create(name=player1_name)
            player2, created = Player.objects.get_or_create(name=player2_name)

            # Verifica che i giocatori non siano già in una squadra dello stesso torneo
            existing_teams_p1 = Team.objects.filter(tournament=tournament).filter(
                Q(player1=player1) | Q(player2=player1)
            )
            existing_teams_p2 = Team.objects.filter(tournament=tournament).filter(
                Q(player1=player2) | Q(player2=player2)
            )

            if existing_teams_p1.exists():
                messages.error(request, f'{player1.name} è già in una squadra di questo torneo.')
                response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
                response['HX-Trigger'] = 'refreshMessages'
                return response

            if existing_teams_p2.exists():
                messages.error(request, f'{player2.name} è già in una squadra di questo torneo.')
                response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
                response['HX-Trigger'] = 'refreshMessages'
                return response

            # Se il gruppo non è specificato, scegline uno a caso
            if not group:  # This checks for both None and empty string
                group = random.choice(['A', 'B'])

            # Se il gruppo non è specificato, scegline uno a caso
            if not group:
                group = random.choice(['A', 'B'])

            # Check if the selected group has fewer than 4 teams
            group_team_count = Team.objects.filter(tournament=tournament, group=group).count()
            if group_team_count >= 4:
                other_group = 'B' if group == 'A' else 'A'
                if Team.objects.filter(tournament=tournament, group=other_group).count() < 4:
                    group = other_group
                    message = f'Il girone {group} è pieno. La squadra è stata inserita nel girone {other_group}.'
                else:
                    messages.error(request, 'Numero masimo di squadre raggiunto.')
                    response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
                    response['HX-Trigger'] = 'refreshMessages'
                    return response
            else:
                message = f'Squadra "{team_name}" creata con successo!'

            # Crea la squadra
            team = Team.objects.create(
                name=team_name,
                tournament=tournament,
                player1=player1,
                player2=player2,
                group=group
            )

            messages.success(request, message)

        except IntegrityError:
            messages.error(request, 'Errore nella creazione della squadra. Verifica che il nome non sia già utilizzato.')
        except Exception as e:
            messages.error(request, f'Errore imprevisto: {str(e)}')

        response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
        response['HX-Trigger'] = 'refreshMessages'
        return response

    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all()  

    # Se non è POST, renderizza la pagina di gestione
    response = render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
    response['HX-Trigger'] = 'refreshMessages'
    return response

def genera_gironi_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = list(torneo.teams.all())
    import random
    random.shuffle(teams)
    for i, team in enumerate(teams):
        team.group = 'A' if i < len(teams) / 2 else 'B'
        team.save()
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/squadre_partecipanti.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})

def avvia_torneo_partial(request, torneo_id):
    if not request.user.is_authenticated:
        messages.error(request, "Solo il mio capo supremo Christian può avviare il torneo.")
        response = HttpResponse(status=403)
        response['HX-Trigger'] = 'refreshMessages'
        return response
    
    torneo = get_object_or_404(Tournament, id=torneo_id)
    torneo.status = 'GROUP_STAGE'
    torneo.save()

    def generate_schedule(torneo):
        teams_by_group = defaultdict(list)
        for team in torneo.teams.all():
            teams_by_group[team.group].append(team)

        matchups_by_group = {
            group: deque(combinations(teams, 2))
            for group, teams in teams_by_group.items()
        }

        schedule = []
        start_time = torneo.start_date
        match_duration = timedelta(minutes=45)

        team_field4_usage = defaultdict(int)  # Traccia quante volte ogni team ha giocato su campo 4

        while matchups_by_group['A'] or matchups_by_group['B']:
            played_teams = set()
            round_matchups = []

            # Coda temporanea per reinserire match saltati
            temp_matchups = {'A': deque(), 'B': deque()}

            # Riempi un turno con al massimo 4 partite
            while len(round_matchups) < 4:
                for group in ['A', 'B']:
                    if not matchups_by_group[group]:
                        continue
                    match = matchups_by_group[group].popleft()
                    t1, t2 = match

                    # Assicura che le squadre non abbiano già giocato in questo turno
                    if t1 in played_teams or t2 in played_teams:
                        temp_matchups[group].append(match)
                        continue

                    round_matchups.append((t1, t2, group))
                    played_teams.update([t1, t2])

                    if len(round_matchups) == 4:
                        break

            # Re-inserisce i match saltati
            for group in ['A', 'B']:
                matchups_by_group[group].extendleft(reversed(temp_matchups[group]))

            # Assegna i campi 1-4 nel rispetto dei vincoli
            assigned_fields = set()
            for t1, t2, group in round_matchups:
                for field in [1, 2, 3, 4]:
                    if field in assigned_fields:
                        continue
                    if field == 4 and (team_field4_usage[t1] >= 2 or team_field4_usage[t2] >= 2):
                        continue

                    assigned_fields.add(field)
                    if field == 4:
                        team_field4_usage[t1] += 1
                        team_field4_usage[t2] += 1

                    schedule.append({
                        'tournament': torneo,
                        'team1': t1,
                        'team2': t2,
                        'start_time': start_time,
                        'field': field,
                        'stage': 'GROUP',
                        'is_finished': False
                    })
                    break

            start_time += match_duration

        return schedule

    # Generate the schedule
    schedule = generate_schedule(torneo)

    # Save the matches to the database
    for match_data in schedule:
        Match.objects.create(
            tournament=match_data['tournament'],
            team1=match_data['team1'],
            team2=match_data['team2'],
            stage=match_data['stage'],
            is_finished=match_data['is_finished'],
            start_time=match_data['start_time'],
            field=match_data['field'],
        )

    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/home-torneo.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})

def avvia_fasi_finali_partial(request, torneo_id):
    if not request.user.is_authenticated:
        messages.error(request, "Solo il mio capo supremo Christian può avviare le fasi finali.")
        response = HttpResponse(status=403)
        response['HX-Trigger'] = 'refreshMessages'
        return response

    torneo = get_object_or_404(Tournament, id=torneo_id)

    # Classifica per gruppo
    def classifica_gruppo(gruppo):
        squadre = list(Team.objects.filter(tournament=torneo, group=gruppo))
        return sorted(
            squadre,
            key=lambda t: (t.group_points, t.goal_difference),
            reverse=True
        )

    classifica_A = classifica_gruppo('A')
    classifica_B = classifica_gruppo('B')

    if len(classifica_A) < 4 or len(classifica_B) < 4:
        messages.error(request, "Non ci sono abbastanza squadre per avviare le fasi finali.")
        response = HttpResponse(status=400)
        response['HX-Trigger'] = 'refreshMessages'
        return response

    # Semifinali + finaline 5/6 e 7/8
    partite = [
        ('SEMI_FINAL', classifica_A[0], classifica_B[1]),  # 1A vs 2B
        ('SEMI_FINAL', classifica_B[0], classifica_A[1]),  # 1B vs 2A
        ('FINAL_5_6', classifica_A[2], classifica_B[2]),   # 3A vs 3B
        ('FINAL_7_8', classifica_A[3], classifica_B[3]),   # 4A vs 4B
    ]

    # Conta usi di campo 4
    team_field4_usage = defaultdict(int)
    for match in torneo.matches.filter(field=4):
        team_field4_usage[match.team1] += 1
        team_field4_usage[match.team2] += 1

    # Campo preferenziale se non occupato
    def scegli_campo(t1, t2, occupati):
        for campo in range(1, 5):
            if campo in occupati:
                continue
            if campo == 4:
                if t1 and team_field4_usage[t1] >= 2:
                    continue
                if t2 and team_field4_usage[t2] >= 2:
                    continue
            if campo == 4:
                if t1:
                    team_field4_usage[t1] += 1
                if t2:
                    team_field4_usage[t2] += 1
            return campo
        return 1

    nuove_partite = []

    # Evita doppioni
    if torneo.matches.filter(stage__in=[s for s, *_ in partite + partite_finali]).exists():
        messages.warning(request, "Le fasi finali sembrano già essere state create.")
        response = HttpResponse(status=400)
        response['HX-Trigger'] = 'refreshMessages'
        return response

    # Semifinali + finali 5/6, 7/8 → 16:15
    start_time_16_15 = make_aware(datetime.combine(torneo.start_date.date(), time(hour=16, minute=15)))
    durata_30min = timedelta(minutes=30)
    for stage, t1, t2 in partite:
        # 🔒 Escludi solo i campi già occupati a quell'orario
        campi_occupati = [
            m['field'] for m in nuove_partite
            if m['start_time'] == start_time_16_15
        ]
        campo = scegli_campo(t1, t2, campi_occupati)
        nuove_partite.append({
            'tournament': torneo,
            'team1': t1,
            'team2': t2,
            'start_time': start_time_16_15,
            'field': campo,
            'stage': stage,
            'is_finished': False
        })

    # Finali 1º-2º e 3º-4º → 17:00, senza squadre
    start_time_17 = make_aware(datetime.combine(torneo.start_date.date(), time(hour=17, minute=0)))
    partite_finali = [
        ('FINAL_1_2', None, None),
        ('FINAL_3_4', None, None),
    ]
    for stage, t1, t2 in partite_finali:
        campo = scegli_campo(t1, t2, [m['field'] for m in nuove_partite])
        nuove_partite.append({
            'tournament': torneo,
            'team1': t1,
            'team2': t2,
            'start_time': start_time_17,
            'field': campo,
            'stage': stage,
            'is_finished': False
        })

    # Salva nel DB
    for match_data in nuove_partite:
        Match.objects.create(**match_data)

    torneo.status = 'KNOCKOUT'
    torneo.save()

    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/home-torneo.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})
 
def gestisci_partite_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)

    # 🔁 GESTIONE SALVATAGGIO RISULTATI
    if request.method == 'POST':
        match_id = request.POST.get("match_id")
        score_team1 = request.POST.get("score_team1")
        score_team2 = request.POST.get("score_team2")

        if match_id and score_team1 is not None and score_team2 is not None:
            try:
                match = Match.objects.get(id=match_id, tournament=torneo)
                match.score_team1 = int(score_team1)
                match.score_team2 = int(score_team2)
                match.is_finished = True
                match.save()
            except (Match.DoesNotExist, ValueError):
                messages.error(request, "Qualcosa è andato storto.")
                response = HttpResponse(status=400)
                response['HX-Trigger'] = 'refreshMessages'
                return response

    matches = torneo.matches.filter(stage='GROUP').order_by('start_time')

    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_partite.html', {
            'torneo': torneo,
            'matches': matches
        })
    else:
        return render(request, 'base.html', {
            'torneo': torneo,
            'matches': matches
        })

def tabellone_finale_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    matches = torneo.matches.filter(stage__in=['SEMI_FINAL', 'FINAL_1_2', 'FINAL_3_4', 'FINAL_5_6', 'FINAL_7_8'])
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/tabellone_finale.html', {'torneo': torneo, 'matches': matches})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'matches': matches})

def gestisci_finali_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)

    if request.method == 'POST':
        match_id = request.POST.get("match_id")

        if match_id:
            try:
                with transaction.atomic():
                    match = Match.objects.get(id=match_id, tournament=torneo)

                    # 🏁 Salvataggio risultati
                    if match.stage in ['FINAL_1_2', 'FINAL_3_4']:
                        s1t1 = request.POST.get("set1_team1")
                        s1t2 = request.POST.get("set1_team2")
                        s2t1 = request.POST.get("set2_team1")
                        s2t2 = request.POST.get("set2_team2")

                        set1_team1 = int(s1t1) if s1t1 else None
                        set1_team2 = int(s1t2) if s1t2 else None
                        set2_team1 = int(s2t1) if s2t1 else None
                        set2_team2 = int(s2t2) if s2t2 else None

                        match.set1_team1 = set1_team1 or 0
                        match.set1_team2 = set1_team2 or 0
                        match.set2_team1 = set2_team1 or 0
                        match.set2_team2 = set2_team2 or 0

                        # ⚖️ Calcolo del punteggio virtuale per definire il vincitore
                        set_wins_team1 = 0
                        set_wins_team2 = 0
                        total_points_team1 = 0
                        total_points_team2 = 0

                        if set1_team1 is not None and set1_team2 is not None:
                            if set1_team1 > set1_team2:
                                set_wins_team1 += 1
                            elif set1_team2 > set1_team1:
                                set_wins_team2 += 1
                            total_points_team1 += set1_team1
                            total_points_team2 += set1_team2

                        if set2_team1 is not None and set2_team2 is not None:
                            if set2_team1 > set2_team2:
                                set_wins_team1 += 1
                            elif set2_team2 > set2_team1:
                                set_wins_team2 += 1
                            total_points_team1 += set2_team1
                            total_points_team2 += set2_team2

                        # Determina il vincitore
                        if set_wins_team1 > set_wins_team2:
                            match.score_team1 = 2
                            match.score_team2 = 0
                        elif set_wins_team2 > set_wins_team1:
                            match.score_team1 = 0
                            match.score_team2 = 2
                        else:
                            # Parità di set, decidi con differenza punti
                            if total_points_team1 > total_points_team2:
                                match.score_team1 = 2
                                match.score_team2 = 1
                            else:
                                match.score_team1 = 1
                                match.score_team2 = 2

                    else:
                        match.score_team1 = int(request.POST.get("score_team1", 0))
                        match.score_team2 = int(request.POST.get("score_team2", 0))

                    match.is_finished = True
                    match.save()

                    # ⚔️ Se è SEMI_FINAL → aggiorna FINAL_1_2 e FINAL_3_4
                    if match.stage == 'SEMI_FINAL' and match.team1 and match.team2:
                        team_winner = match.team1 if match.score_team1 > match.score_team2 else match.team2
                        team_loser = match.team2 if team_winner == match.team1 else match.team1

                        semi_finals = list(Match.objects.filter(tournament=torneo, stage='SEMI_FINAL').order_by('start_time'))
                        index = semi_finals.index(match)

                        finale_1_2 = Match.objects.filter(tournament=torneo, stage='FINAL_1_2').first()
                        finale_3_4 = Match.objects.filter(tournament=torneo, stage='FINAL_3_4').first()

                        if index == 0:
                            if finale_1_2:
                                finale_1_2.team1 = team_winner
                                finale_1_2.save()
                            if finale_3_4:
                                finale_3_4.team1 = team_loser
                                finale_3_4.save()
                        elif index == 1:
                            if finale_1_2:
                                finale_1_2.team2 = team_winner
                                finale_1_2.save()
                            if finale_3_4:
                                finale_3_4.team2 = team_loser
                                finale_3_4.save()

            except (Match.DoesNotExist, ValueError, IndexError):
                messages.error(request, "Qualcosa è andato storto.")
                response = HttpResponse(status=400)
                response['HX-Trigger'] = 'refreshMessages'
                return response

    matches = torneo.matches.filter(stage__in=[
        'SEMI_FINAL', 'FINAL_1_2', 'FINAL_3_4', 'FINAL_5_6', 'FINAL_7_8'
    ]).order_by('start_time')

    context = {
        'torneo': torneo,
        'matches': matches
    }

    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_finali.html', context)
    else:
        return render(request, 'base.html', context)

def classifica_finale_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all().order_by('-group_points', 'name')
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/classifica_finale.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})
