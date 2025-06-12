# urls.py

from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from . import views  # Importiamo le viste dal modulo corrente

urlpatterns = [
    # richieste varie tramite htmx
    path('aggiorna-messages/', views.aggiorna_messages, name='aggiorna_messages'),

    # Homepage
    path('', views.homepage, name='homepage'),
    # Homepage tramite htmx
    path('v2/', views.homepage_partial, name='homepage2'),
    # Crea torneo
    path('crea-torneo/', views.crea_torneo_partial, name='crea_torneo'),
]