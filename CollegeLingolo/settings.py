"""
=============================================================================
SETTINGS - Configuration du projet Django "college_lingolo"
=============================================================================
Ce fichier contient TOUTE la configuration du projet Django.
C'est le premier fichier que Django lit au démarrage.

IMPORTANT pour la production :
- SECRET_KEY doit être dans une variable d'environnement (jamais en dur !)
- DEBUG doit être False
- ALLOWED_HOSTS doit contenir le nom de domaine du serveur

os.environ.get('VARIABLE', 'valeur_par_defaut') :
  → Cherche la variable d'environnement VARIABLE
  → Si elle n'existe pas, utilise 'valeur_par_defaut'
  → Cela permet d'avoir des configs différentes en dev et en prod
=============================================================================
"""

import os
from pathlib import Path

# BASE_DIR = le dossier racine du projet (là où se trouve manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SÉCURITÉ
# =============================================================================

# SECRET_KEY : clé secrète utilisée pour le chiffrement (sessions, CSRF, etc.)
# En production, la définir comme variable d'environnement !
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-bjp)349!a*6g#sczf3qj7hp6zg1cbt3-jz-bnx1j*lmvw$mp)a'
)

# DEBUG = True : affiche les erreurs détaillées (utile en développement)
# DEBUG = False : affiche des pages d'erreur génériques (obligatoire en production)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS : liste des noms de domaine autorisés à accéder au site
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# =============================================================================
# APPLICATIONS INSTALLÉES
# =============================================================================

INSTALLED_APPS = [
    # Applications Django par défaut
    'django.contrib.admin',          # Interface d'administration
    'django.contrib.auth',           # Authentification utilisateurs
    'django.contrib.contenttypes',   # Types de contenu (utilisé par l'admin)
    'django.contrib.sessions',       # Gestion des sessions
    'django.contrib.messages',       # Messages flash (succès, erreur...)
    'django.contrib.staticfiles',    # Gestion des fichiers statiques (CSS, JS...)

    # Nos applications
    'eleves',                        # L'application principale du collège
]


# =============================================================================
# MIDDLEWARE
# =============================================================================
# Les middleware sont des "couches" qui traitent chaque requête/réponse.
# Ils s'exécutent dans l'ordre pour les requêtes, et en ordre inverse
# pour les réponses (comme un oignon).

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',         # Sécurité HTTP
    'whitenoise.middleware.WhiteNoiseMiddleware',             # Fichiers statiques en prod
    'django.contrib.sessions.middleware.SessionMiddleware',   # Sessions
    'django.middleware.common.CommonMiddleware',              # Fonctionnalités communes
    'django.middleware.csrf.CsrfViewMiddleware',              # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Auth
    'django.contrib.messages.middleware.MessageMiddleware',    # Messages flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protection clickjacking
]


# =============================================================================
# CONFIGURATION DES URLS ET TEMPLATES
# =============================================================================

ROOT_URLCONF = 'CollegeLingolo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',      # Dossier de templates global
        ],
        'APP_DIRS': True,    # Cherche aussi dans <app>/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CollegeLingolo.wsgi.application'


# =============================================================================
# BASE DE DONNÉES - PostgreSQL
# =============================================================================
# On utilise PostgreSQL PARTOUT (local avec Docker ET production).
# Cela garantit un comportement identique en dev et en prod.
#
# Les paramètres de connexion sont lus depuis les variables d'environnement
# définies dans docker-compose.yml. Si elles n'existent pas, on utilise
# les valeurs par défaut (utiles pour le développement local avec Docker).
#
# Pourquoi PostgreSQL plutôt que SQLite ?
# - SQLite = fichier local, limité à 1 seul utilisateur à la fois
# - PostgreSQL = vrai serveur de BDD, gère plusieurs connexions simultanées,
#   plus fiable, plus performant, et c'est ce qu'on utilise en production.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',   # Le driver PostgreSQL
        'NAME': BASE_DIR / 'db.sqlite3',       # Nom de la base 
        'Hostname' : 'dpg-dail49h594qs7396vh00-a.frankfurt-postgres.render.com',
        'Port' : '5432',
        'Database' : 'college_lingolo_db',
        'Username' : 'college_lingolo_db_user',
        'Password' : '8GMBmMQCWdgWYhODBpidYkjrIwZ24ZY3' 
    }
}


# =============================================================================
# VALIDATION DES MOTS DE PASSE
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNATIONALISATION
# =============================================================================

LANGUAGE_CODE = 'fr-fr'       # Interface en français
TIME_ZONE = 'Africa/Brazzaville'  # Fuseau horaire du Congo
USE_I18N = True                # Activer la traduction
USE_TZ = True                  # Utiliser les fuseaux horaires


# =============================================================================
# FICHIERS STATIQUES (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',        # Dossier static/ à la racine du projet
]

# Dossier où collectstatic rassemble tous les fichiers statiques pour la production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise : sert les fichiers statiques de manière efficace en production
"""STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}"""

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# =============================================================================
# AUTHENTIFICATION
# =============================================================================
# LOGIN_URL : l'URL vers laquelle Django redirige les utilisateurs non connectés
# quand ils tentent d'accéder à une page protégée par @login_required
#
# LOGIN_REDIRECT_URL : où aller après une connexion réussie
# LOGOUT_REDIRECT_URL : où aller après une déconnexion

LOGIN_URL = '/login/'                  # Page de connexion
LOGIN_REDIRECT_URL = '/'               # Après login → dashboard
LOGOUT_REDIRECT_URL = '/login/'        # Après logout → page de connexion


# =============================================================================
# AUTRES
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
