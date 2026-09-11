# =============================================================================
# DOCKERFILE - Collège Lingolo
# =============================================================================
# Un Dockerfile est une "recette" pour construire une image Docker.
# L'image contient : Python + Django + le code du projet + les dépendances.
#
# Avec docker-compose (recommandé) :
#   docker-compose up --build
# =============================================================================

# --------------------------------------------------------------------------
# ÉTAPE 1 : Image de base
# --------------------------------------------------------------------------
# python:3.11-slim = Python 3.11 sur Debian allégé (petite taille d'image)
FROM python:3.11-slim

# --------------------------------------------------------------------------
# ÉTAPE 2 : Variables d'environnement
# --------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --------------------------------------------------------------------------
# ÉTAPE 3 : Installer les dépendances système pour PostgreSQL
# --------------------------------------------------------------------------
# libpq-dev et gcc sont nécessaires pour compiler psycopg2 (driver PostgreSQL)
# On installe puis on nettoie le cache apt pour réduire la taille de l'image
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# ÉTAPE 4 : Dossier de travail
# --------------------------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------------------------
# ÉTAPE 5 : Installer les dépendances Python
# --------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------------------
# ÉTAPE 6 : Copier le code du projet
# --------------------------------------------------------------------------
COPY . .

# --------------------------------------------------------------------------
# ÉTAPE 7 : Collecter les fichiers statiques
# --------------------------------------------------------------------------
# On fournit une DJANGO_SECRET_KEY temporaire juste pour cette commande
# car collectstatic n'a pas besoin de la vraie clé mais Django la requiert
RUN DJANGO_SECRET_KEY=temp-key-for-collectstatic \
    POSTGRES_HOST=none \
    python manage.py collectstatic --noinput 2>/dev/null || true

# --------------------------------------------------------------------------
# ÉTAPE 8 : Exposer le port et lancer
# --------------------------------------------------------------------------
EXPOSE 8000

#CMD ["gunicorn", "CollegeLingolo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--graceful-timeout", "120", "CollegeLingolo.wsgi:application"]