"""
=============================================================================
URLS PRINCIPALES - Projet college_lingolo
=============================================================================
Ce fichier est le point d'entrée de TOUTES les URLs du projet.
Il inclut les URLs de chaque application avec include().

Les URLs d'authentification (login/logout) sont définies ici car elles
concernent le projet entier, pas juste l'application "eleves".
=============================================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
# auth_views : vues d'authentification fournies par Django.
# LoginView et LogoutView gèrent tout automatiquement :
# - Afficher le formulaire de connexion
# - Vérifier le nom d'utilisateur et le mot de passe
# - Créer la session utilisateur
# - Rediriger après connexion/déconnexion

urlpatterns = [
    # -------------------------------------------------------------------------
    # Authentification (connexion / déconnexion)
    # -------------------------------------------------------------------------
    # LoginView : affiche le formulaire de connexion
    # template_name : chemin vers notre template personnalisé
    path('login/', auth_views.LoginView.as_view(
        template_name='eleves/login.html'
    ), name='login'),

    # LogoutView : déconnecte l'utilisateur et le redirige
    # (la redirection est définie par LOGOUT_REDIRECT_URL dans settings.py)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # -------------------------------------------------------------------------
    # Interface d'administration Django
    # -------------------------------------------------------------------------
    path('admin/', admin.site.urls),

    # -------------------------------------------------------------------------
    # Application "eleves" (toutes les pages du collège)
    # -------------------------------------------------------------------------
    # Le dashboard est défini comme path('') dans eleves/urls.py
    # donc la page d'accueil '/' affiche directement le tableau de bord
    path('', include('eleves.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)