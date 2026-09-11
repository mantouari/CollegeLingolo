"""
=============================================================================
MODÈLES DE DONNÉES - Application "eleves" du Collège Lingolo
=============================================================================
Ce fichier définit la structure de la base de données.
Chaque classe Python = une table dans la base de données.
Chaque attribut de classe = une colonne dans cette table.

Django utilise un ORM (Object-Relational Mapping) qui permet de manipuler
la base de données avec du Python au lieu d'écrire du SQL directement.

Après avoir modifié ce fichier, il faut toujours exécuter :
    python manage.py makemigrations   (crée le fichier de migration)
    python manage.py migrate          (applique les changements à la BDD)
=============================================================================
"""

from django.db import models
from django.urls import reverse


""" =============================================================================
# MODÈLE CLASSE
# =============================================================================
# Représente une classe du collège (ex: 6ème A, 5ème B, etc.)
# On la sépare du modèle Eleve pour éviter la répétition et permettre
# de gérer les classes indépendamment (capacité, titulaire, etc.)"""

class Classe(models.Model):
    """
    Une classe du collège (6ème A, 5ème B, etc.).

    Pourquoi un modèle séparé ?
    - Évite de taper "6ème A" à la main pour chaque élève (risque de fautes)
    - Permet d'ajouter des infos sur la classe (capacité, titulaire...)
    - Crée une liste déroulante automatique dans les formulaires
    """

    # -------------------------------------------------------------------------
    # CHOIX PRÉDÉFINIS (constantes)
    # -------------------------------------------------------------------------
    # On définit les niveaux possibles sous forme de tuples :
    # ('valeur_stockée_en_bdd', 'texte_affiché_à_l_utilisateur')
    NIVEAUX = [
        ('6eme', '6ème'),
        ('5eme', '5ème'),
        ('4eme', '4ème'),
        ('3eme', '3ème'),
    ]

    # -------------------------------------------------------------------------
    # CHAMPS (colonnes de la table)
    # -------------------------------------------------------------------------
    # CharField = texte court (obligatoire : max_length)
    # choices= limite les valeurs possibles à la liste NIVEAUX
    niveau = models.CharField(
        max_length=10,
        choices=NIVEAUX,
        verbose_name="Niveau",           # Nom affiché dans l'admin et les forms
        help_text="Niveau scolaire"      # Texte d'aide sous le champ
    )

    # La lettre de la classe (A, B, C...)
    lettre = models.CharField(
        max_length=5,
        verbose_name="Lettre",
        help_text="Ex: A, B, C..."
    )

    # IntegerField = nombre entier
    capacite = models.IntegerField(
        default=50,                      # Valeur par défaut si non renseignée
        verbose_name="Capacité maximale",
        help_text="Nombre maximum d'élèves"
    )

    # -------------------------------------------------------------------------
    # META : options du modèle
    # -------------------------------------------------------------------------
    class Meta:
        # verbose_name : nom affiché au singulier dans l'admin
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        # ordering : tri par défaut quand on récupère les classes
        ordering = ['niveau', 'lettre']
        # unique_together : empêche d'avoir deux fois "6ème A"
        unique_together = ['niveau', 'lettre']

    # -------------------------------------------------------------------------
    # __str__ : ce qui s'affiche quand on fait print(classe)
    # Aussi utilisé dans les listes déroulantes des formulaires
    # -------------------------------------------------------------------------
    def __str__(self):
        return f"{self.get_niveau_display()} {self.lettre}"
        # get_niveau_display() retourne le texte lisible (ex: "6ème")
        # au lieu de la valeur stockée ("6eme")


# =============================================================================
# MODÈLE ÉLÈVE
# =============================================================================
# Le modèle principal : chaque ligne = un élève inscrit au collège.

class Eleve(models.Model):
    """
    Un élève inscrit au Collège Lingolo.

    ForeignKey vers Classe : chaque élève appartient à UNE classe,
    mais une classe peut avoir PLUSIEURS élèves (relation 1-N).
    """

    # -------------------------------------------------------------------------
    # CHOIX pour le statut
    # -------------------------------------------------------------------------
    STATUTS = [
        ('nouveau', 'Nouveau'),
        ('redoublant', 'Redoublant'),
    ]

    SEXES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    # -------------------------------------------------------------------------
    # CHAMPS
    # -------------------------------------------------------------------------
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de famille"
    )

    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )

    date_naissance = models.DateField(
        verbose_name="Date de naissance",
        help_text="Format : AAAA-MM-JJ (ex: 2010-05-15)"
    )

    sexe = models.CharField(
        max_length=1,
        choices=SEXES,
        default='M',
        verbose_name="Sexe"
    )

    # -------------------------------------------------------------------------
    # ForeignKey = relation "plusieurs-à-un"
    # -------------------------------------------------------------------------
    # Un élève appartient à UNE classe. Si la classe est supprimée,
    # on_delete=models.SET_NULL met la valeur à NULL (l'élève reste mais
    # n'a plus de classe). Alternatives :
    #   - CASCADE : supprime aussi l'élève (dangereux !)
    #   - PROTECT : empêche la suppression de la classe tant qu'il y a des élèves
    classe = models.ForeignKey(
        Classe,
        on_delete=models.SET_NULL,       # Si la classe est supprimée → NULL
        null=True,                       # Autorise NULL en base de données
        blank=True,                      # Autorise le champ vide dans les forms
        related_name='eleves',           # classe.eleves.all() pour avoir les élèves
        verbose_name="Classe"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='nouveau',
        verbose_name="Statut"
    )

    # TextField = texte long (pas de max_length obligatoire)
    adresse = models.TextField(
        blank=True,                      # blank=True = champ optionnel dans les forms
        default='',                      # Valeur par défaut vide
        verbose_name="Adresse"
    )

    nom_parent = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name="Nom du parent/tuteur"
    )

    telephone_parent = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name="Téléphone du parent",
        help_text="Ex: +242 06 xxx xx xx"
    )

    # auto_now_add=True : la date est automatiquement mise à la création
    # Ce champ n'apparaît pas dans les formulaires (il est auto-géré)
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        ordering = ['classe', 'nom', 'prenom']  # Tri par classe puis nom

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_absolute_url(self):
        """
        Retourne l'URL de la page de détail de cet élève.
        Utilisé par Django dans les redirections après création/modification.
        reverse() construit l'URL à partir du nom de la route (défini dans urls.py).
        """
        return reverse('detail_eleve', kwargs={'pk': self.pk})
        # pk = primary key (identifiant unique auto-généré par Django)


# =============================================================================
# MODÈLE PROFESSEUR
# =============================================================================

class Professeur(models.Model):
    """Un enseignant du collège."""

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(
        max_length=20, blank=True, default='',
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        blank=True, default='',
        verbose_name="Email"
    )
    specialite = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name="Spécialité",
        help_text="Ex: Mathématiques, Français..."
    )

    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"Prof. {self.prenom} {self.nom}"

    def get_absolute_url(self):
        return reverse('detail_professeur', kwargs={'pk': self.pk})


# =============================================================================
# MODÈLE MATIÈRE
# =============================================================================

class Matiere(models.Model):
    """
    Une matière enseignée (Maths, Français, etc.).

    ManyToManyField vers Professeur : une matière peut être enseignée
    par plusieurs professeurs, et un professeur peut enseigner
    plusieurs matières (relation N-N).
    """

    nom = models.CharField(
        max_length=100,
        unique=True,                     # Pas deux matières avec le même nom
        verbose_name="Nom de la matière"
    )

    # coefficient : poids de la matière dans le calcul de la moyenne
    coefficient = models.IntegerField(
        default=1,
        verbose_name="Coefficient"
    )

    # -------------------------------------------------------------------------
    # ManyToManyField = relation "plusieurs-à-plusieurs"
    # -------------------------------------------------------------------------
    # Django crée automatiquement une table intermédiaire pour gérer
    # cette relation. Pas besoin de la créer manuellement.
    professeurs = models.ManyToManyField(
        Professeur,
        blank=True,                      # Une matière peut n'avoir aucun prof assigné
        related_name='matieres',         # prof.matieres.all() pour voir ses matières
        verbose_name="Professeurs"
    )

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom']

    def __str__(self):
        return self.nom


# =============================================================================
# MODÈLE NOTE
# =============================================================================

class Note(models.Model):
    """
    Une note attribuée à un élève dans une matière.

    C'est une table de liaison entre Eleve et Matiere, enrichie
    d'informations supplémentaires (la valeur de la note, la date, etc.).
    """

    TRIMESTRES = [
        (1, '1er Trimestre'),
        (2, '2ème Trimestre'),
        (3, '3ème Trimestre'),
    ]

    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.CASCADE,        # Si l'élève est supprimé, ses notes aussi
        related_name='notes',            # eleve.notes.all()
        verbose_name="Élève"
    )

    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="Matière"
    )

    # DecimalField : nombre décimal précis (mieux que FloatField pour les notes)
    # max_digits=4, decimal_places=2 permet des valeurs comme 18.50
    valeur = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Note",
        help_text="Note sur 20"
    )

    trimestre = models.IntegerField(
        choices=TRIMESTRES,
        default=1,
        verbose_name="Trimestre"
    )

    date_evaluation = models.DateField(
        verbose_name="Date de l'évaluation"
    )

    commentaire = models.TextField(
        blank=True, default='',
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-date_evaluation']  # Les plus récentes en premier (- = desc)

    def __str__(self):
        return f"{self.eleve} - {self.matiere} : {self.valeur}/20"