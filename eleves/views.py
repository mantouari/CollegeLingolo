"""
=============================================================================
VUES (VIEWS) - Application "eleves"
=============================================================================
Les vues sont le "cerveau" de l'application. Elles :
1. Reçoivent une requête HTTP (GET, POST...) de l'utilisateur
2. Traitent la logique métier (récupérer des données, sauvegarder...)
3. Retournent une réponse HTTP (page HTML, redirection...)

SÉCURITÉ : Toutes les vues sont protégées par @login_required.
=============================================================================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404

from .models import Eleve, Classe, Professeur, Matiere, Note, Bulletin
from .forms import (
    EleveForm, ClasseForm, ProfesseurForm, MatiereForm, NoteForm, BulletinForm
)


# =============================================================================
# TABLEAU DE BORD (page d'accueil)
# =============================================================================

@login_required
def dashboard(request):
    """
    Page d'accueil avec les statistiques générales du collège.
    """
    total_eleves = Eleve.objects.count()
    total_classes = Classe.objects.count()
    total_professeurs = Professeur.objects.count()
    total_matieres = Matiere.objects.count()
    total_bulletins = Bulletin.objects.count()

    moyenne_generale = Note.objects.aggregate(
        moyenne=Avg('valeur')
    )['moyenne']

    derniers_eleves = Eleve.objects.select_related('classe').order_by(
        '-date_inscription'
    )[:5]

    classes_stats = Classe.objects.annotate(
        nb_eleves=Count('eleves')
    ).order_by('niveau', 'lettre')

    dernieres_notes = Note.objects.select_related(
        'eleve', 'matiere'
    ).order_by('-date_evaluation')[:10]

    derniers_bulletins = Bulletin.objects.select_related(
        'eleve', 'classe'
    ).order_by('-date_bulletin')[:5]

    context = {
        'total_eleves': total_eleves,
        'total_classes': total_classes,
        'total_professeurs': total_professeurs,
        'total_matieres': total_matieres,
        'total_bulletins': total_bulletins,
        'moyenne_generale': moyenne_generale,
        'derniers_eleves': derniers_eleves,
        'classes_stats': classes_stats,
        'dernieres_notes': dernieres_notes,
        'derniers_bulletins': derniers_bulletins,
    }

    return render(request, 'eleves/dashboard.html', context)


# =============================================================================
# VUES ÉLÈVES (CRUD)
# =============================================================================

@login_required
def liste_eleves(request):
    """Affiche la liste de tous les élèves avec recherche et filtrage."""
    query = request.GET.get('q', '')
    classe_id = request.GET.get('classe', '')

    eleves = Eleve.objects.select_related('classe')

    if query:
        eleves = eleves.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query)
        )

    if classe_id:
        eleves = eleves.filter(classe_id=classe_id)

    classes = Classe.objects.all()

    context = {
        'eleves': eleves,
        'classes': classes,
        'query': query,
        'classe_id': classe_id,
    }

    return render(request, 'eleves/liste_eleves.html', context)


@login_required
def detail_eleve(request, pk):
    """Affiche les détails d'un élève, ses notes et ses bulletins."""
    eleve = get_object_or_404(Eleve, pk=pk)

    notes = eleve.notes.select_related('matiere').order_by(
        'trimestre', 'matiere__nom'
    )

    moyenne = notes.aggregate(moyenne=Avg('valeur'))['moyenne']

    bulletins_par_trimestre = []
    for numero, libelle in Note.TRIMESTRES:
        bulletins_par_trimestre.append({
            'numero': numero,
            'libelle': libelle,
            'bulletin': eleve.bulletins.filter(trimestre=numero).first(),
            'a_des_notes': notes.filter(trimestre=numero).exists(),
        })

    context = {
        'eleve': eleve,
        'notes': notes,
        'moyenne': moyenne,
        'bulletins_par_trimestre': bulletins_par_trimestre,
    }

    return render(request, 'eleves/detail_eleve.html', context)


@login_required
def ajouter_eleve(request):
    """Affiche et traite le formulaire d'ajout d'un élève."""
    if request.method == 'POST':
        form = EleveForm(request.POST)
        if form.is_valid():
            eleve = form.save()
            return redirect('detail_eleve', pk=eleve.pk)
    else:
        form = EleveForm()

    return render(request, 'eleves/formulaire_eleve.html', {
        'form': form,
        'titre': 'Inscrire un nouvel élève',
        'bouton': 'Inscrire',
    })


@login_required
def modifier_eleve(request, pk):
    """Modifie un élève existant."""
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        form = EleveForm(request.POST, instance=eleve)
        if form.is_valid():
            form.save()
            return redirect('detail_eleve', pk=eleve.pk)
    else:
        form = EleveForm(instance=eleve)

    return render(request, 'eleves/formulaire_eleve.html', {
        'form': form,
        'titre': f'Modifier {eleve.prenom} {eleve.nom}',
        'bouton': 'Enregistrer les modifications',
    })


@login_required
def supprimer_eleve(request, pk):
    """Supprime un élève après confirmation."""
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        eleve.delete()
        return redirect('liste_eleves')

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
    eleves = classe.eleves.all()
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


# =============================================================================
# VUES NOTES
# =============================================================================

@login_required
def liste_notes(request):
    """Liste toutes les notes avec filtrage par élève, matière et trimestre."""
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
# VUES BULLETINS
# =============================================================================

@login_required
def liste_bulletins_eleve(request, eleve_pk):
    """
    Affiche la liste des bulletins déjà générés pour un élève,
    ainsi que les trimestres pour lesquels il n'y a pas encore de bulletin.
    """
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    bulletins = eleve.bulletins.all()

    trimestres_existants = bulletins.values_list('trimestre', flat=True)
    trimestres_manquants = [
        t for t, _ in Note.TRIMESTRES if t not in trimestres_existants
    ]

    context = {
        'eleve': eleve,
        'bulletins': bulletins,
        'trimestres_manquants': trimestres_manquants,
    }
    return render(request, 'eleves/liste_bulletins.html', context)


@login_required
def generer_bulletin(request, eleve_pk, trimestre):
    """
    Crée (ou met à jour) le bulletin d'un élève pour un trimestre donné,
    calcule la moyenne, génère l'appréciation et produit le PDF.
    """
    eleve = get_object_or_404(Eleve, pk=eleve_pk)

    if not eleve.notes.filter(trimestre=trimestre).exists():
        messages.error(
            request,
            f"Impossible de générer le bulletin : aucune note enregistrée "
            f"pour {eleve} au trimestre {trimestre}."
        )
        return redirect('liste_bulletins_eleve', eleve_pk=eleve.pk)

    bulletin, created = Bulletin.objects.get_or_create(
        eleve=eleve,
        trimestre=trimestre,
        defaults={'classe': eleve.classe}
    )

    if not created:
        bulletin.classe = eleve.classe

    bulletin.generer_pdf()

    if created:
        messages.success(request, f"Bulletin du trimestre {trimestre} généré avec succès.")
    else:
        messages.success(request, f"Bulletin du trimestre {trimestre} régénéré avec succès.")

    return redirect('detail_bulletin', pk=bulletin.pk)


@login_required
def detail_bulletin(request, pk):
    """
    Affiche le détail d'un bulletin : infos élève, moyenne,
    appréciation générale et tableau des notes par matière.
    """
    bulletin = get_object_or_404(Bulletin, pk=pk)
    notes = bulletin.eleve.notes.filter(trimestre=bulletin.trimestre)

    notes_avec_appreciation = [
        {'note': note, 'appreciation': Bulletin.generer_appreciation(note.valeur)}
        for note in notes
    ]

    context = {
        'bulletin': bulletin,
        'notes_avec_appreciation': notes_avec_appreciation,
    }
    return render(request, 'eleves/detail_bulletin.html', context)


@login_required
def telecharger_bulletin(request, pk):
    """
    Envoie le fichier PDF du bulletin au navigateur pour téléchargement.
    Si le PDF n'existe pas encore, on le génère à la volée.
    """
    bulletin = get_object_or_404(Bulletin, pk=pk)

    if not bulletin.fichier_pdf:
        bulletin.generer_pdf()

    try:
        return FileResponse(
            bulletin.fichier_pdf.open('rb'),
            as_attachment=True,
            filename=f"bulletin_{bulletin.eleve.nom}_{bulletin.eleve.prenom}_T{bulletin.trimestre}.pdf"
        )
    except FileNotFoundError:
        raise Http404("Le fichier PDF du bulletin est introuvable.")


@login_required
def supprimer_bulletin(request, pk):
    """
    Supprime un bulletin (et son fichier PDF associé).
    """
    bulletin = get_object_or_404(Bulletin, pk=pk)
    eleve_pk = bulletin.eleve.pk

    if request.method == 'POST':
        if bulletin.fichier_pdf:
            bulletin.fichier_pdf.delete(save=False)
        bulletin.delete()
        messages.success(request, "Bulletin supprimé avec succès.")
        return redirect('liste_bulletins_eleve', eleve_pk=eleve_pk)

    return render(request, 'eleves/confirmer_suppression_bulletin.html', {'bulletin': bulletin})


@login_required
def ajouter_bulletin(request):
    """
    Formulaire manuel de création d'un bulletin.
    Alternative à generer_bulletin() pour choisir librement
    l'élève et le trimestre depuis une page dédiée.
    """
    if request.method == 'POST':
        form = BulletinForm(request.POST)
        if form.is_valid():
            bulletin = form.save()
            bulletin.generer_pdf()
            return redirect('detail_bulletin', pk=bulletin.pk)
    else:
        form = BulletinForm()

    return render(request, 'eleves/formulaire_bulletin.html', {
        'form': form,
        'titre': 'Créer un bulletin',
        'bouton': 'Générer le bulletin',
    })