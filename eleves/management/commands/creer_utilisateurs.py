"""
=============================================================================
COMMANDE PERSONNALISÉE - Créer les 3 utilisateurs du collège
=============================================================================
Cette commande crée automatiquement les comptes utilisateurs du système.
Elle s'exécute avec : python manage.py creer_utilisateurs

Django permet de créer des commandes personnalisées en plaçant un fichier
Python dans le dossier management/commands/ d'une application.

La classe Command doit hériter de BaseCommand et implémenter la méthode
handle() qui contient la logique de la commande.

Les 3 utilisateurs créés :
1. directeur  → Superutilisateur (accès total, y compris l'admin Django)
2. secretaire → Staff (peut gérer les élèves, classes, profs, notes)
3. professeur → Utilisateur normal (peut consulter et saisir des notes)
=============================================================================
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    # help : texte affiché quand on tape "python manage.py creer_utilisateurs --help"
    help = 'Crée les 3 utilisateurs par défaut du Collège Lingolo'

    def handle(self, *args, **options):
        """
        Méthode principale exécutée quand on lance la commande.

        Pour chaque utilisateur, on vérifie d'abord s'il existe déjà
        (avec User.objects.filter().exists()) pour éviter les doublons.

        User.objects.create_superuser() : crée un superutilisateur
            → Accès TOTAL : admin Django, toutes les permissions

        User.objects.create_user() : crée un utilisateur normal
            → is_staff=True : peut accéder à l'interface admin Django
            → is_staff=False : accès uniquement au site principal
        """

        # =====================================================================
        # UTILISATEUR 1 : Le Directeur (superutilisateur)
        # =====================================================================
        # Le superuser a TOUTES les permissions automatiquement.
        # Il peut : tout faire dans l'admin, gérer les autres utilisateurs,
        # supprimer des données, etc.
        if not User.objects.filter(username='directeur').exists():
            User.objects.create_superuser(
                username='directeur',
                email='directeur@CollegeLingolo.cg',
                password='lingolo2026',
                first_name='Directeur',
                last_name='Collège Lingolo',
            )
            self.stdout.write(self.style.SUCCESS(
                '  [OK] Utilisateur "directeur" créé (superadmin)'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '  [--] Utilisateur "directeur" existe déjà'
            ))

        # =====================================================================
        # UTILISATEUR 2 : Le/La Secrétaire (staff)
        # =====================================================================
        # is_staff=True lui donne accès à l'interface admin Django
        # mais il/elle n'a pas toutes les permissions (contrairement au directeur)
        if not User.objects.filter(username='secretaire').exists():
            User.objects.create_user(
                username='secretaire',
                email='secretaire@CollegeLingolo.cg',
                password='lingolo2026',
                first_name='Secrétaire',
                last_name='Collège Lingolo',
                is_staff=True,           # Peut accéder à /admin/
            )
            self.stdout.write(self.style.SUCCESS(
                '  [OK] Utilisateur "secretaire" créé (staff)'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '  [--] Utilisateur "secretaire" existe déjà'
            ))

        # =====================================================================
        # UTILISATEUR 3 : Le Professeur (utilisateur standard)
        # =====================================================================
        # Utilisateur normal : accès au site, mais PAS à l'admin Django
        if not User.objects.filter(username='professeur').exists():
            User.objects.create_user(
                username='professeur',
                email='professeur@CollegeLingolo.cg',
                password='lingolo2026',
                first_name='Professeur',
                last_name='Collège Lingolo',
                is_staff=False,          # PAS d'accès à /admin/
            )
            self.stdout.write(self.style.SUCCESS(
                '  [OK] Utilisateur "professeur" créé (standard)'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                '  [--] Utilisateur "professeur" existe déjà'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            '=== Utilisateurs prêts ! ==='
        ))
        self.stdout.write('  Mot de passe commun : lingolo2026')
        self.stdout.write('  Pensez à changer les mots de passe en production !')