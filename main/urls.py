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
    # Home torneo
    path('home-torneo/<int:torneo_id>/', views.home_torneo_partial, name='home_torneo'),
    # Elimina torneo
    path('elimina-torneo/<int:torneo_id>/', views.elimina_torneo_partial, name='elimina_torneo'),
    # Manage teams
    path('gestisci-squadre/<int:torneo_id>/', views.gestisci_squadre_partial, name='gestisci_squadre'),
    # Generate groups
    path('genera-gironi/<int:torneo_id>/', views.genera_gironi_partial, name='genera_gironi'),
    # Start tournament
    path('avvia-torneo/<int:torneo_id>/', views.avvia_torneo_partial, name='avvia_torneo'),
    # Group standings
    path('classifica-gironi/<int:torneo_id>/', views.classifica_gironi_partial, name='classifica_gironi'),
    # Manage matches
    path('gestisci-partite/<int:torneo_id>/', views.gestisci_partite_partial, name='gestisci_partite'),
    # Final bracket
    path('tabellone-finale/<int:torneo_id>/', views.tabellone_finale_partial, name='tabellone_finale'),
    # Manage finals
    path('gestisci-finali/<int:torneo_id>/', views.gestisci_finali_partial, name='gestisci_finali'),
    # Final standings
    path('classifica-finale/<int:torneo_id>/', views.classifica_finale_partial, name='classifica_finale'),
]