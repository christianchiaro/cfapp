from main.models import Tournament
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime

def aggiorna_messages(request):
    html = render_to_string('main/partials/components/toasts/toast.html', request=request)
    return HttpResponse(html)

def homepage(request):
    context = {}
    return render(request, 'base.html', context)

def homepage_partial(request):
    tornei = Tournament.objects.all().order_by('-start_date')
    return render(request, 'main/partials/homepage/home.html', {'tornei': tornei})

def crea_torneo_partial(request):
    if request.method == "GET":
        # Ritorna solo il template del form
        return render(request, 'main/partials/torneo/home.html')
    
    elif request.method == "POST":
        # Processa il form
        name = request.POST.get('name')
        start_date_raw = request.POST.get('start_date')
        # Validazione
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
            tournament = Tournament.objects.create(
                name=name,
                start_date=start_date,
            )
            messages.success(request, f"Torneo {tournament.name} creato correttamente")
            html = render_to_string('main/partials/torneo/home-torneo.html', {
                'torneo': tournament
            }, request=request)

            response = HttpResponse(html)
            response['HX-Trigger'] = 'refreshMessages'
            return response
            
        except Exception as e:
            return render(request, 'main/partials/crea_torneo_form.html', {
                'error': f'Errore durante la creazione: {str(e)}'
            })