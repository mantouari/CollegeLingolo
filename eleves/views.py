"""
=============================================================================
VUES (VIEWS) - Application "eleves"
=============================================================================
Les vues sont le "cerveau" de l'application. Elles :
1. Reçoivent une requête HTTP (GET, POST...) de l'utilisateur
2. Traitent la logique métier (récupérer des données, sauvegarder...)
3. Retournent une réponse HTTP (page HTML, redirection...)

On utilise ici des VUES BASÉES SUR DES FONCTIONS (FBV = Function-Based Views).
Chaque vue est une fonction Python qui prend 'request' en paramètre
et retourne un objet HttpResponse (souvent via render() ou redirect()).

SÉCURITÉ : Toutes les vues sont protégées par @login_required.
Si un utilisateur non connecté tente d'accéder à une page,
il est automatiquement redirigé vers /login/.

Concepts clés :
- render(request, template, context) : génère une page HTML à partir d'un template
- redirect(url) : redirige l'utilisateur vers une autre page
- get_object_or_404(Model, pk=id) : récupère un objet ou affiche une erreur 404
- request.method == 'POST' : l'utilisateur a soumis un formulaire
- request.method == 'GET' : l'utilisateur veut afficher une page
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q
from django.contrib.auth.decorators import login_required
# =============================================================================
# @login_required est un DÉCORATEUR Python.
# Un décorateur "enveloppe" une fonction pour ajouter un comportement.
# Ici, il vérifie que l'utilisateur est connecté AVANT d'exécuter la vue.
#
# Sans @login_required : tout le monde peut accéder à la page
# Avec @login_required : seuls les utilisateurs connectés y accèdent
#
# Si l'utilisateur n'est pas connecté, Django le redirige vers LOGIN_URL
# (défini dans settings.py = '/login/'). Après connexion, il revient
# automatiquement à la page qu'il voulait voir.
# =============================================================================

from .models import Eleve, Classe, Professeur, Matiere, Note
from .forms import EleveForm, ClasseForm, ProfesseurForm, MatiereForm, NoteForm


# =============================================================================
# TABLEAU DE BORD (page d'accueil)
# =============================================================================

@login_required  # ← L'utilisateur DOIT être connecté pour voir le dashboard
def dashboard(request):
    """
    Page d'accueil avec les statistiques générales du collège.

    On utilise les méthodes d'agrégation de Django ORM :
    - count() : compte le nombre d'objets
    - aggregate(Avg('champ')) : calcule la moyenne d'un champ
    - annotate() : ajoute des calculs à chaque objet d'un QuerySet

    Le dictionnaire 'context' contient toutes les variables
    accessibles dans le template HTML.
    """
    # Compter les objets en base de données
    total_eleves = Eleve.objects.count()
    total_classes = Classe.objects.count()
    total_professeurs = Professeur.objects.count()
    total_matieres = Matiere.objects.count()

    # Calculer la moyenne générale de toutes les notes
    # aggregate() retourne un dictionnaire : {'valeur__avg': 12.5}
    moyenne_generale = Note.objects.aggregate(
        moyenne=Avg('valeur')
    )['moyenne']

    # Les 5 derniers élèves inscrits (tri par date décroissante)
    derniers_eleves = Eleve.objects.select_related('classe').order_by(
        '-date_inscription'
    )[:5]
    # select_related('classe') : charge la classe en même temps que l'élève
    # pour éviter une requête SQL supplémentaire par élève (optimisation)
    # [:5] : équivalent de LIMIT 5 en SQL

    # Nombre d'élèves par classe (pour le graphique)
    # annotate() ajoute un champ calculé 'nb_eleves' à chaque classe
    classes_stats = Classe.objects.annotate(
        nb_eleves=Count('eleves')        # 'eleves' = related_name défini dans le modèle
    ).order_by('niveau', 'lettre')

    # Les 10 dernières notes saisies
    dernieres_notes = Note.objects.select_related(
        'eleve', 'matiere'
    ).order_by('-date_evaluation')[:10]

    # Le context : dictionnaire envoyé au template
    context = {
        'total_eleves': total_eleves,
        'total_classes': total_classes,
        'total_professeurs': total_professeurs,
        'total_matieres': total_matieres,
        'moyenne_generale': moyenne_generale,
        'derniers_eleves': derniers_eleves,
        'classes_stats': classes_stats,
        'dernieres_notes': dernieres_notes,
    }

    return render(request, 'eleves/dashboard.html', context)
    # render() combine le template HTML avec les données du context
    # et retourne la page HTML complète


# =============================================================================
# VUES ÉLÈVES (CRUD = Create, Read, Update, Delete)
# =============================================================================

@login_required
def liste_eleves(request):
    """
    Affiche la liste de tous les élèves avec recherche et filtrage.

    request.GET.get('q') récupère le paramètre 'q' dans l'URL.
    Exemple : /eleves/?q=dupont  →  q = 'dupont'
    Exemple : /eleves/?classe=1  →  classe_id = '1'

    Q() permet de faire des recherches avec OR (|) ou AND (&).
    Par défaut, .filter(a=x, b=y) fait un AND.
    """
    # Récupérer les paramètres de recherche/filtrage depuis l'URL
    query = request.GET.get('q', '')              # Texte de recherche
    classe_id = request.GET.get('classe', '')     # Filtre par classe

    # Commencer avec tous les élèves
    eleves = Eleve.objects.select_related('classe')

    # Appliquer la recherche textuelle si présente
    if query:
        # Q(champ__icontains=texte) : recherche insensible à la casse
        # Le | (pipe) signifie OR : cherche dans le nom OU le prénom
        eleves = eleves.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query)
        )

    # Appliquer le filtre par classe si sélectionné
    if classe_id:
        eleves = eleves.filter(classe_id=classe_id)

    # Récupérer toutes les classes pour le menu déroulant de filtrage
    classes = Classe.objects.all()

    context = {
        'eleves': eleves,
        'classes': classes,
        'query': query,                  # Pour pré-remplir le champ de recherche
        'classe_id': classe_id,          # Pour garder le filtre sélectionné
    }

    return render(request, 'eleves/liste_eleves.html', context)


@login_required
def detail_eleve(request, pk):
    """
    Affiche les détails d'un élève et ses notes.

    Paramètres :
    - pk (Primary Key) : l'identifiant unique de l'élève, récupéré
      depuis l'URL (ex: /eleves/5/ → pk=5)

    get_object_or_404() : cherche l'élève avec cet ID.
    Si l'élève n'existe pas, affiche automatiquement une page 404.
    C'est mieux que Eleve.objects.get(pk=pk) qui lèverait une exception.
    """
    eleve = get_object_or_404(Eleve, pk=pk)

    # Récupérer les notes de cet élève, triées par trimestre puis matière
    notes = eleve.notes.select_related('matiere').order_by(
        'trimestre', 'matiere__nom'
    )

    # Calculer la moyenne de l'élève
    moyenne = notes.aggregate(moyenne=Avg('valeur'))['moyenne']

    context = {
        'eleve': eleve,
        'notes': notes,
        'moyenne': moyenne,
    }

    return render(request, 'eleves/detail_eleve.html', context)


@login_required
def ajouter_eleve(request):
    """
    Affiche et traite le formulaire d'ajout d'un élève.

    Le pattern est toujours le même pour les formulaires Django :
    1. GET  → Afficher le formulaire vide
    2. POST → Valider et sauvegarder les données

    if form.is_valid() vérifie toutes les contraintes :
    - Les champs obligatoires sont remplis
    - Les types de données sont corrects
    - Les validations personnalisées passent (clean_xxx)
    """
    if request.method == 'POST':
        # Créer le formulaire avec les données soumises
        form = EleveForm(request.POST)
        if form.is_valid():
            # save() crée l'objet en base de données et le retourne
            eleve = form.save()
            # Rediriger vers la page de détail du nouvel élève
            return redirect('detail_eleve', pk=eleve.pk)
        # Si le formulaire n'est pas valide, il sera ré-affiché
        # avec les messages d'erreur automatiquement
    else:
        # GET : créer un formulaire vide
        form = EleveForm()

    return render(request, 'eleves/formulaire_eleve.html', {
        'form': form,
        'titre': 'Inscrire un nouvel élève',
        'bouton': 'Inscrire',
    })


@login_required
def modifier_eleve(request, pk):
    """
    Modifie un élève existant.

    La différence avec ajouter_eleve() :
    - On récupère d'abord l'élève existant
    - On passe instance=eleve au formulaire pour pré-remplir les champs
    """
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        # instance=eleve : met à jour l'élève existant au lieu d'en créer un nouveau
        form = EleveForm(request.POST, instance=eleve)
        if form.is_valid():
            form.save()
            return redirect('detail_eleve', pk=eleve.pk)
    else:
        # Pré-remplir le formulaire avec les données actuelles
        form = EleveForm(instance=eleve)

    return render(request, 'eleves/formulaire_eleve.html', {
        'form': form,
        'titre': f'Modifier {eleve.prenom} {eleve.nom}',
        'bouton': 'Enregistrer les modifications',
    })


@login_required
def supprimer_eleve(request, pk):
    """
    Supprime un élève après confirmation.

    On utilise une page de confirmation (GET) avant la suppression (POST).
    Cela évite les suppressions accidentelles (ex: clic par erreur).

    IMPORTANT : Ne jamais supprimer sur un GET ! C'est une faille de sécurité.
    Un robot ou un lien malveillant pourrait déclencher des suppressions.
    """
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        # L'utilisateur a confirmé → supprimer
        eleve.delete()
        return redirect('liste_eleves')

    # GET → afficher la page de confirmation
    return render(request, 'eleves/confirmer_suppression.html', {
        'objet': eleve,
        'type_objet': 'élève',
        'url_retour': 'liste_eleves',
    })


# =============================================================================
# VUES CLASSES
# =============================================================================

@login_required
def liste_classes(request):
    """Liste toutes les classes avec le nombre d'élèves par classe."""
    classes = Classe.objects.annotate(nb_eleves=Count('eleves'))
    return render(request, 'eleves/liste_classes.html', {'classes': classes})


@login_required
def detail_classe(request, pk):
    """Affiche le détail d'une classe et ses élèves."""
    classe = get_object_or_404(Classe, pk=pk)
    eleves = classe.eleves.all()  # Grâce au related_name='eleves'
    return render(request, 'eleves/detail_classe.html', {
        'classe': classe,
        'eleves': eleves,
    })


@login_required
def ajouter_classe(request):
    """Formulaire d'ajout d'une classe."""
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_classes')
    else:
        form = ClasseForm()

    return render(request, 'eleves/formulaire_classe.html', {
        'form': form,
        'titre': 'Ajouter une classe',
        'bouton': 'Ajouter',
    })


@login_required
def modifier_classe(request, pk):
    """Modification d'une classe existante."""
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            return redirect('liste_classes')
    else:
        form = ClasseForm(instance=classe)

    return render(request, 'eleves/formulaire_classe.html', {
        'form': form,
        'titre': f'Modifier {classe}',
        'bouton': 'Enregistrer',
    })


@login_required
def supprimer_classe(request, pk):
    """Suppression d'une classe après confirmation."""
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        classe.delete()
        return redirect('liste_classes')
    return render(request, 'eleves/confirmer_suppression.html', {
        'objet': classe,
        'type_objet': 'classe',
        'url_retour': 'liste_classes',
    })


# =============================================================================
# VUES PROFESSEURS
# =============================================================================

@login_required
def liste_professeurs(request):
    """Liste tous les professeurs."""
    professeurs = Professeur.objects.prefetch_related('matieres')
    # prefetch_related() : optimise les requêtes pour les relations ManyToMany
    # Sans ça, Django ferait une requête SQL par professeur pour charger ses matières
    return render(request, 'eleves/liste_professeurs.html', {
        'professeurs': professeurs,
    })


@login_required
def detail_professeur(request, pk):
    """Détail d'un professeur avec ses matières."""
    professeur = get_object_or_404(Professeur, pk=pk)
    return render(request, 'eleves/detail_professeur.html', {
        'professeur': professeur,
    })


@login_required
def ajouter_professeur(request):
    """Formulaire d'ajout d'un professeur."""
    if request.method == 'POST':
        form = ProfesseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_professeurs')
    else:
        form = ProfesseurForm()

    return render(request, 'eleves/formulaire_professeur.html', {
        'form': form,
        'titre': 'Ajouter un professeur',
        'bouton': 'Ajouter',
    })


@login_required
def modifier_professeur(request, pk):
    """Modification d'un professeur existant."""
    professeur = get_object_or_404(Professeur, pk=pk)
    if request.method == 'POST':
        form = ProfesseurForm(request.POST, instance=professeur)
        if form.is_valid():
            form.save()
            return redirect('liste_professeurs')
    else:
        form = ProfesseurForm(instance=professeur)

    return render(request, 'eleves/formulaire_professeur.html', {
        'form': form,
        'titre': f'Modifier {professeur}',
        'bouton': 'Enregistrer',
    })


@login_required
def supprimer_professeur(request, pk):
    """Suppression d'un professeur après confirmation."""
    professeur = get_object_or_404(Professeur, pk=pk)
    if request.method == 'POST':
        professeur.delete()
        return redirect('liste_professeurs')
    return render(request, 'eleves/confirmer_suppression.html', {
        'objet': professeur,
        'type_objet': 'professeur',
        'url_retour': 'liste_professeurs',
    })


# =============================================================================
# VUES NOTES
# =============================================================================

@login_required
def liste_notes(request):
    """
    Liste toutes les notes avec filtrage par élève, matière et trimestre.
    """
    eleve_id = request.GET.get('eleve', '')
    matiere_id = request.GET.get('matiere', '')
    trimestre = request.GET.get('trimestre', '')

    notes = Note.objects.select_related('eleve', 'matiere')

    if eleve_id:
        notes = notes.filter(eleve_id=eleve_id)
    if matiere_id:
        notes = notes.filter(matiere_id=matiere_id)
    if trimestre:
        notes = notes.filter(trimestre=trimestre)

    context = {
        'notes': notes,
        'eleves': Eleve.objects.all(),
        'matieres': Matiere.objects.all(),
        'eleve_id': eleve_id,
        'matiere_id': matiere_id,
        'trimestre': trimestre,
    }

    return render(request, 'eleves/liste_notes.html', context)


@login_required
def ajouter_note(request):
    """Formulaire d'ajout d'une note."""
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_notes')
    else:
        form = NoteForm()

    return render(request, 'eleves/formulaire_note.html', {
        'form': form,
        'titre': 'Saisir une note',
        'bouton': 'Enregistrer la note',
    })


@login_required
def modifier_note(request, pk):
    """Modification d'une note existante."""
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('liste_notes')
    else:
        form = NoteForm(instance=note)

    return render(request, 'eleves/formulaire_note.html', {
        'form': form,
        'titre': 'Modifier la note',
        'bouton': 'Enregistrer',
    })


@login_required
def supprimer_note(request, pk):
    """Suppression d'une note après confirmation."""
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        return redirect('liste_notes')
    return render(request, 'eleves/confirmer_suppression.html', {
        'objet': note,
        'type_objet': 'note',
        'url_retour': 'liste_notes',
    })

# =============================================================================
# VUES MATIÈRES
# =============================================================================

@login_required
def liste_matieres(request):
    """Liste toutes les matières avec leurs professeurs."""
    matieres = Matiere.objects.prefetch_related('professeurs')
    return render(request, 'eleves/liste_matieres.html', {
        'matieres': matieres,
    })


@login_required
def detail_matiere(request, pk):
    """Détail d'une matière avec ses professeurs."""
    matiere = get_object_or_404(Matiere, pk=pk)
    return render(request, 'eleves/detail_matiere.html', {
        'matiere': matiere,
    })


@login_required
def ajouter_matiere(request):
    """Formulaire d'ajout d'une matière."""
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_matieres')
    else:
        form = MatiereForm()

    return render(request, 'eleves/formulaire_matiere.html', {
        'form': form,
        'titre': 'Ajouter une matière',
        'bouton': 'Ajouter',
    })


@login_required
def modifier_matiere(request, pk):
    """Modification d'une matière existante."""
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            return redirect('liste_matieres')
    else:
        form = MatiereForm(instance=matiere)

    return render(request, 'eleves/formulaire_matiere.html', {
        'form': form,
        'titre': f'Modifier {matiere}',
        'bouton': 'Enregistrer',
    })


@login_required
def supprimer_matiere(request, pk):
    """Suppression d'une matière après confirmation."""
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        matiere.delete()
        return redirect('liste_matieres')
    return render(request, 'eleves/confirmer_suppression.html', {
        'objet': matiere,
        'type_objet': 'matière',
        'url_retour': 'liste_matieres',
    })