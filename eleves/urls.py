"""
=============================================================================
URLS - Application "eleves"
=============================================================================
Ce fichier définit les routes (URLs) de l'application.

Chaque route associe :
- Un chemin URL (ex: 'eleves/5/')
- Une vue (fonction dans views.py)
- Un nom (pour référencer l'URL dans les templates avec {% url 'nom' %})

Convention REST-like :
- Liste :    GET  /eleves/
- Détail :   GET  /eleves/5/
- Ajout :    GET/POST /eleves/ajouter/
- Modifier : GET/POST /eleves/5/modifier/
- Supprimer: GET/POST /eleves/5/supprimer/

<int:pk> capture un nombre entier depuis l'URL et le passe
comme argument 'pk' à la vue.
=============================================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------------------------------------------------
    # Dashboard (page d'accueil)
    # -------------------------------------------------------------------------
    path('', views.dashboard, name='dashboard'),

    # -------------------------------------------------------------------------
    # URLs Élèves - CRUD complet
    # -------------------------------------------------------------------------
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    path('eleves/<int:pk>/', views.detail_eleve, name='detail_eleve'),
    path('eleves/ajouter/', views.ajouter_eleve, name='ajouter_eleve'),
    path('eleves/<int:pk>/modifier/', views.modifier_eleve, name='modifier_eleve'),
    path('eleves/<int:pk>/supprimer/', views.supprimer_eleve, name='supprimer_eleve'),

    # -------------------------------------------------------------------------
    # URLs Classes
    # -------------------------------------------------------------------------
    path('classes/', views.liste_classes, name='liste_classes'),
    path('classes/<int:pk>/', views.detail_classe, name='detail_classe'),
    path('classes/ajouter/', views.ajouter_classe, name='ajouter_classe'),
    path('classes/<int:pk>/modifier/', views.modifier_classe, name='modifier_classe'),
    path('classes/<int:pk>/supprimer/', views.supprimer_classe, name='supprimer_classe'),

    # -------------------------------------------------------------------------
    # URLs Professeurs
    # -------------------------------------------------------------------------
    path('professeurs/', views.liste_professeurs, name='liste_professeurs'),
    path('professeurs/<int:pk>/', views.detail_professeur, name='detail_professeur'),
    path('professeurs/ajouter/', views.ajouter_professeur, name='ajouter_professeur'),
    path('professeurs/<int:pk>/modifier/', views.modifier_professeur, name='modifier_professeur'),
    path('professeurs/<int:pk>/supprimer/', views.supprimer_professeur, name='supprimer_professeur'),

    # -------------------------------------------------------------------------
    # URLs Notes
    # -------------------------------------------------------------------------
    path('notes/', views.liste_notes, name='liste_notes'),
    path('notes/ajouter/', views.ajouter_note, name='ajouter_note'),
    path('notes/<int:pk>/modifier/', views.modifier_note, name='modifier_note'),
    path('notes/<int:pk>/supprimer/', views.supprimer_note, name='supprimer_note'),
]
