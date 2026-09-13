"""
=============================================================================
FORMULAIRES - Application "eleves"
=============================================================================
Les formulaires Django permettent de :
1. Générer automatiquement le HTML des champs de saisie
2. Valider les données envoyées par l'utilisateur
3. Sauvegarder les données en base de données

ModelForm : un formulaire généré automatiquement à partir d'un modèle.
Django lit les champs du modèle et crée les champs de formulaire correspondants.
C'est beaucoup plus rapide que de créer chaque champ manuellement !

L'attribut 'widgets' permet de personnaliser l'apparence HTML des champs
(ajouter des classes CSS, changer le type d'input, etc.)
=============================================================================
"""
'''from django.contrib import admin
from django import forms
from .models import Eleve, Classe, Professeur, Matiere, Note


class ClasseForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une Classe.

    La classe Meta indique :
    - model : quel modèle utiliser
    - fields : quels champs inclure ('__all__' = tous les champs)
    - widgets : personnalisation de l'apparence HTML de chaque champ
    """

    class Meta:
        model = Classe
        fields = '__all__'   # Inclut tous les champs du modèle
        widgets = {
            # 'form-control' est une classe CSS de Bootstrap qui stylise les inputs
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'lettre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: A, B, C...'
            }),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

@admin.register(Eleve)
class EleveForm(forms.BaseModelForm):
    """
    Formulaire pour créer/modifier un Élève.

    On utilise 'fields' avec une liste explicite pour contrôler
    l'ordre d'affichage et exclure les champs auto-gérés
    comme 'date_inscription' (qui a auto_now_add=True).
    """

    class Meta:
        model = Eleve
        # Liste explicite des champs (dans l'ordre d'affichage souhaité)
        # On n'inclut PAS 'date_inscription' car il est auto-généré
        fields = [
            'nom', 'prenom', 'date_naissance', 'sexe',
            'classe', 'statut', 'adresse',
            'nom_parent', 'telephone_parent',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            # DateInput avec type='date' affiche un sélecteur de date natif
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'           # Affiche le calendrier du navigateur
            }),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,               # Hauteur du textarea
                'placeholder': 'Adresse complète'
            }),
            'nom_parent': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet du parent ou tuteur'
            }),
            'telephone_parent': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+242 06 xxx xx xx'
            }),
        }

@admin.register(Professeur)
class ProfesseurForm(forms.ModelForm):
    """Formulaire pour créer/modifier un Professeur."""

    class Meta:
        model = Professeur
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nom'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Prénom'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+242 06 xxx xx xx'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'email@exemple.com'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Mathématiques'
            }),
        }

@admin.register(Matiere)
class MatiereForm(forms.ModelForm):
    """Formulaire pour créer/modifier une Matière."""

    class Meta:
        model = Matiere
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nom de la matière'
            }),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control'}),
            # SelectMultiple permet de sélectionner plusieurs professeurs
            # (car c'est un ManyToManyField)
            'professeurs': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'             # Affiche 5 lignes visibles
            }),
        }

@admin.register(Note)
class NoteForm(forms.ModelForm):
    """
    Formulaire pour saisir une Note.

    On ajoute une validation personnalisée avec clean_valeur()
    pour s'assurer que la note est entre 0 et 20.
    """

    class Meta:
        model = Note
        fields = ['eleve', 'matiere', 'valeur', 'trimestre',
                  'date_evaluation', 'commentaire']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'valeur': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',          # Permet les quarts de points
                'min': '0',
                'max': '20'
            }),
            'trimestre': forms.Select(attrs={'class': 'form-select'}),
            'date_evaluation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Commentaire optionnel...'
            }),
        }

    def clean_valeur(self):
        """
        Validation personnalisée du champ 'valeur'.

        Les méthodes clean_<nom_du_champ>() sont appelées automatiquement
        par Django lors de la validation du formulaire.
        Si la valeur n'est pas valide, on lève une ValidationError
        qui sera affichée à l'utilisateur sous le champ.
        """
        valeur = self.cleaned_data.get('valeur')
        if valeur is not None:
            if valeur < 0 or valeur > 20:
                raise forms.ValidationError(
                    "La note doit être comprise entre 0 et 20."
                )
        return valeur'''

from django.contrib import admin
from .models import Classe, Eleve, Professeur, Matiere, Note


# =============================================================================
# ADMIN CLASSE
# =============================================================================

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Classe."""
    
    list_display = ('__str__', 'niveau', 'lettre', 'capacite', 'nombre_eleves')
    list_filter = ('niveau',)
    search_fields = ('niveau', 'lettre')
    ordering = ('niveau', 'lettre')
    
    def nombre_eleves(self, obj):
        """Affiche le nombre d'élèves dans la classe."""
        return obj.eleves.count()
    nombre_eleves.short_description = 'Nombre d\'élèves'


# =============================================================================
# ADMIN ÉLÈVE
# =============================================================================

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Élève."""
    
    list_display = ('nom', 'prenom', 'classe', 'sexe', 'statut', 'date_inscription')
    list_filter = ('classe', 'sexe', 'statut', 'date_inscription')
    search_fields = ('nom', 'prenom', 'nom_parent')
    date_hierarchy = 'date_inscription'
    ordering = ('classe', 'nom', 'prenom')
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'sexe')
        }),
        ('Scolarité', {
            'fields': ('classe', 'statut')
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'nom_parent', 'telephone_parent'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# ADMIN PROFESSEUR
# =============================================================================

@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Professeur."""
    
    list_display = ('nom', 'prenom', 'specialite', 'telephone', 'email')
    search_fields = ('nom', 'prenom', 'specialite')
    list_filter = ('specialite',)
    ordering = ('nom', 'prenom')


# =============================================================================
# ADMIN MATIÈRE
# =============================================================================

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Matière."""
    
    list_display = ('nom', 'coefficient', 'liste_professeurs')
    search_fields = ('nom',)
    list_filter = ('coefficient',)
    filter_horizontal = ('professeurs',)
    ordering = ('nom',)
    
    def liste_professeurs(self, obj):
        """Affiche la liste des professeurs de la matière."""
        return ", ".join([str(p) for p in obj.professeurs.all()]) or "Aucun"
    liste_professeurs.short_description = 'Professeurs'


# =============================================================================
# ADMIN NOTE
# =============================================================================

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Note."""
    
    list_display = ('eleve', 'matiere', 'valeur', 'trimestre', 'date_evaluation')
    list_filter = ('trimestre', 'matiere', 'date_evaluation')
    search_fields = ('eleve__nom', 'eleve__prenom', 'matiere__nom')
    date_hierarchy = 'date_evaluation'
    ordering = ('-date_evaluation',)
    
    fieldsets = (
        ('Évaluation', {
            'fields': ('eleve', 'matiere', 'valeur', 'trimestre')
        }),
        ('Détails', {
            'fields': ('date_evaluation', 'commentaire')
        }),
    )

