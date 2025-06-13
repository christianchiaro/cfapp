from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db import IntegrityError
from django.db.models import Q
from datetime import datetime
from main.models import Tournament, Team, Player, Match

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

def gestisci_squadre_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all()
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_squadre.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})

def gestisci_squadre_manage_teams(request, tournament_id):
    """View per gestire le squadre di un torneo"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    teams = Team.objects.filter(tournament=tournament).select_related('player1', 'player2')
    players = Player.objects.all()

    context = {
        'tournament': tournament,
        'teams': teams,
        'players': players,
    }
    return render(request, 'main/partials/torneo/gestisci_squadre.html', context)

def gestisci_squadre_create_team(request, torneo_id):
    """View per creare una nuova squadra"""
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        player1_name = request.POST.get('player1')
        player2_name = request.POST.get('player2')
        group = request.POST.get('group') or None
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

            # Crea la squadra
            team = Team.objects.create(
                name=team_name,
                tournament=tournament,
                player1=player1,
                player2=player2,
                group=group
            )

            messages.success(request, f'Squadra "{team_name}" creata con successo!')

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
        return render(request, 'main/partials/torneo/home-torneo.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})

def avvia_torneo_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    torneo.status = 'GROUP_STAGE'
    torneo.save()
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/home-torneo.html', {'torneo': torneo})
    else:
        return render(request, 'base.html', {'torneo': torneo})

def classifica_gironi_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all().order_by('-group_points', 'name')
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/classifica_gironi.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})

def gestisci_partite_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    matches = torneo.matches.filter(stage='GROUP')
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_partite.html', {'torneo': torneo, 'matches': matches})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'matches': matches})

def tabellone_finale_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    matches = torneo.matches.filter(stage__in=['SEMI_FINAL', 'FINAL_1_2', 'FINAL_3_4', 'FINAL_5_6', 'FINAL_7_8'])
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/tabellone_finale.html', {'torneo': torneo, 'matches': matches})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'matches': matches})

def gestisci_finali_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    matches = torneo.matches.filter(stage__in=['SEMI_FINAL', 'FINAL_1_2', 'FINAL_3_4', 'FINAL_5_6', 'FINAL_7_8'])
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/gestisci_finali.html', {'torneo': torneo, 'matches': matches})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'matches': matches})

def classifica_finale_partial(request, torneo_id):
    torneo = get_object_or_404(Tournament, id=torneo_id)
    teams = torneo.teams.all().order_by('-group_points', 'name')
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/torneo/classifica_finale.html', {'torneo': torneo, 'teams': teams})
    else:
        return render(request, 'base.html', {'torneo': torneo, 'teams': teams})
