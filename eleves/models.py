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


# =============================================================================
# MODÈLE BULLETIN
# =============================================================================
# Représente le bulletin scolaire trimestriel d'un élève.
# Il agrège les notes de l'élève pour un trimestre donné, calcule sa
# moyenne générale, génère une appréciation automatique et peut produire
# un fichier PDF téléchargeable.

class Bulletin(models.Model):
    """
    Bulletin scolaire d'un élève pour un trimestre donné.

    ForeignKey vers Eleve : un élève peut avoir plusieurs bulletins
    (un par trimestre), mais un bulletin appartient à un seul élève.
    """

    # -------------------------------------------------------------------------
    # CHAMPS
    # -------------------------------------------------------------------------
    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.CASCADE,        # Si l'élève est supprimé, ses bulletins aussi
        related_name='bulletins',        # eleve.bulletins.all()
        verbose_name="Élève"
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulletins',
        verbose_name="Classe"
    )

    trimestre = models.IntegerField(
        choices=Note.TRIMESTRES,         # On réutilise les choix définis dans Note
        default=1,
        verbose_name="Trimestre"
    )

    date_bulletin = models.DateField(
        auto_now_add=True,
        verbose_name="Date de génération"
    )

    moyenne_generale = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Moyenne générale"
    )

    appreciation_generale = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Appréciation générale"
    )

    # FileField : stocke le PDF généré dans MEDIA_ROOT/bulletins/
    fichier_pdf = models.FileField(
        upload_to='bulletins/',
        blank=True,
        null=True,
        verbose_name="Fichier PDF"
    )

    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering = ['-date_bulletin']
        # Un seul bulletin par élève et par trimestre
        unique_together = ['eleve', 'trimestre']

    def __str__(self):
        return f"Bulletin de {self.eleve} - {self.get_trimestre_display()}"

    def get_absolute_url(self):
        return reverse('detail_bulletin', kwargs={'pk': self.pk})

    # -------------------------------------------------------------------------
    # MÉTHODES MÉTIER
    # -------------------------------------------------------------------------
    @staticmethod
    def generer_appreciation(note):
        """
        Génère une appréciation textuelle à partir d'une note sur 20.

        Args:
            note (float/Decimal): la note à évaluer

        Returns:
            str: l'appréciation correspondante
        """
        if note >= 18:
            return "Excellent"
        elif note >= 16:
            return "Très bien"
        elif note >= 14:
            return "Bien"
        elif note >= 12:
            return "Satisfaisant"
        elif note >= 10:
            return "Passable"
        elif note >= 8:
            return "Faible"
        else:
            return "Très faible"

    def calculer_moyenne(self):
        """
        Calcule la moyenne générale du bulletin à partir des notes
        de l'élève pour ce trimestre, puis l'enregistre sur l'instance.
        """
        notes = self.eleve.notes.filter(trimestre=self.trimestre)
        if not notes.exists():
            self.moyenne_generale = 0
            return 0

        total = sum(n.valeur for n in notes)
        moyenne = total / notes.count()
        self.moyenne_generale = round(moyenne, 2)
        return self.moyenne_generale

    def generer_appreciation_generale(self):
        """
        Génère l'appréciation générale du bulletin à partir de la moyenne,
        puis l'enregistre sur l'instance.
        """
        moyenne = self.moyenne_generale
        if moyenne is None:
            moyenne = self.calculer_moyenne()

        if moyenne >= 16:
            appreciation = "Excellent travail ! Continuez ainsi."
        elif moyenne >= 14:
            appreciation = "Très bon résultat. Bravo !"
        elif moyenne >= 12:
            appreciation = "Bons résultats. À maintenir."
        elif moyenne >= 10:
            appreciation = "Résultats satisfaisants."
        else:
            appreciation = "À améliorer. Des efforts supplémentaires sont nécessaires."

        self.appreciation_generale = appreciation
        return appreciation

    def generer_pdf(self, save=True):
        """
        Génère le bulletin au format PDF (via reportlab) et l'enregistre
        dans le champ fichier_pdf.

        Args:
            save (bool): si True, sauvegarde l'instance en base après génération
        """
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from django.core.files.base import ContentFile

        # Mise à jour des valeurs calculées
        self.calculer_moyenne()
        self.generer_appreciation_generale()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1
        )
        story.append(Paragraph("BULLETIN SCOLAIRE", title_style))
        story.append(Spacer(1, 0.5 * cm))

        info_style = ParagraphStyle(
            'Info', parent=styles['Normal'], fontSize=11, spaceAfter=10
        )
        story.append(Paragraph(f"<b>Élève :</b> {self.eleve}", info_style))
        story.append(Paragraph(f"<b>Classe :</b> {self.classe}", info_style))
        story.append(
            Paragraph(f"<b>Trimestre :</b> {self.get_trimestre_display()}", info_style)
        )
        story.append(
            Paragraph(
                f"<b>Date :</b> {self.date_bulletin.strftime('%d/%m/%Y')}",
                info_style
            )
        )
        story.append(Spacer(1, 0.8 * cm))

        # Tableau des notes
        notes = self.eleve.notes.filter(trimestre=self.trimestre)
        data = [["Matières", "Notes / 20", "Appréciations"]]
        for note in notes:
            appreciation = self.generer_appreciation(note.valeur)
            data.append([note.matiere.nom, str(note.valeur), appreciation])

        data.append(["MOYENNE", f"{self.moyenne_generale:.2f}", "---"])

        t = Table(data, colWidths=[6 * cm, 3 * cm, 5 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6e6e6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        story.append(t)
        story.append(Spacer(1, 1 * cm))

        appreciation_style = ParagraphStyle(
            'Appreciation',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor("#ff0000"),
            spaceAfter=10
        )
        story.append(
            Paragraph(
                f"<b>Appréciation générale :</b> <i>{self.appreciation_generale}</i>",
                appreciation_style
            )
        )

        doc.build(story)
        buffer.seek(0)

        nom_fichier = f"bulletin_{self.eleve.nom}_{self.eleve.prenom}_T{self.trimestre}.pdf"
        self.fichier_pdf.save(nom_fichier, ContentFile(buffer.read()), save=False)

        if save:
            self.save()
 