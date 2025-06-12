from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages

def aggiorna_messages(request):
    html = render_to_string('main/partials/components/toasts/toast.html', request=request)
    return HttpResponse(html)

def homepage(request):
    context = {}
    return render(request, 'base.html', context)

def homepage_partial(request):
    return render(request, 'main/partials/homepage/home.html')

def crea_torneo_partial(request):
    if request.method == "GET":
        # Ritorna solo il template del form
        return render(request, 'main/partials/torneo/home.html')
    
    elif request.method == "POST":
        # Processa il form
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        status = request.POST.get('status', 'SETUP')
        
        # Validazione
        if not name or not start_date:
            messages.error(request, "Nome e data di inizio sono obbligatori!")
            response = HttpResponse(status=400)
            response['HX-Trigger'] = 'refreshMessages'
            return response
        
        try:
            # Crea il torneo
            tournament = Tournament.objects.create(
                name=name,
                start_date=start_date,
                status=status
            )
            
            # Ritorna il template di successo
            return render(request, 'main/partials/torneo_creato.html', {
                'tournament': tournament
            })
            
        except Exception as e:
            return render(request, 'main/partials/crea_torneo_form.html', {
                'error': f'Errore durante la creazione: {str(e)}'
            })