# =============================================================================
# VUES - LOGIQUE MÉTIER INTERVIEWPRO
# =============================================================================
# Ce fichier contient toute la logique métier de l'application
# Chaque fonction représente une action que l'utilisateur peut effectuer
# Les vues gèrent les requêtes HTTP et retournent des réponses

from datetime import timedelta

# Imports Django pour la gestion des requêtes et réponses
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail

# Imports des modèles et formulaires de l'application
from .models import Profile, ManagerDetails, Poste, CandidatPoste, Entretien
from .forms import (
    UserRegistrationForm, ProfileForm, ManagerDetailsForm,
    PosteForm, CandidatureForm, EntretienPlanForm
)

# Récupération du modèle User personnalisé
User = get_user_model()


# =============================================================================
# VUES PUBLIQUES (ACCESSIBLES SANS CONNEXION)
# =============================================================================

def home(request):
    """
    Page d'accueil publique de l'application.
    
    Cette vue est accessible à tous les utilisateurs (connectés ou non).
    Affiche les informations générales sur InterViewPro.
    
    Args:
        request: Objet HttpRequest contenant les données de la requête
        
    Returns:
        HttpResponse: Rendu du template home.html
    """
    return render(request, 'entretiens/home.html')


def user_login(request):
    """
    Gestion de la connexion utilisateur avec authentification sécurisée.
    
    Cette vue gère le processus de connexion avec :
    - Vérification des identifiants (username/password)
    - Contrôle du statut actif de l'utilisateur
    - Messages d'erreur détaillés
    - Redirection vers le dashboard après connexion
    
    Args:
        request: Objet HttpRequest (GET pour affichage, POST pour traitement)
        
    Returns:
        HttpResponse: Template de connexion ou redirection vers dashboard
    """
    # Traitement du formulaire de connexion (méthode POST)
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST['username']
        password = request.POST['password']
        
        # Authentification Django (vérifie username/password)
        user = authenticate(request, username=username, password=password)
        
        if user:
            # Utilisateur trouvé et mot de passe correct
            if user.is_active:
                # Compte actif : connexion autorisée
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name() or user.username}!")
                return redirect('dashboard')
            else:
                # Compte inactif : connexion refusée
                error = "Votre compte n'est pas actif. Contactez l'administrateur."
        else:
            # Identifiants incorrects : vérification détaillée
            try:
                existing_user = User.objects.get(username=username)
                if not existing_user.is_active:
                    error = "Votre compte n'est pas actif. Contactez l'administrateur."
                else:
                    error = 'Mot de passe incorrect'
            except User.DoesNotExist:
                error = 'Utilisateur non trouvé'
        
        # Retour du formulaire avec message d'erreur
        return render(request, 'entretiens/login.html', {'error': error})
    
    # Affichage du formulaire de connexion (méthode GET)
    return render(request, 'entretiens/login.html')


def user_register(request):
    """
    Gestion de l'inscription de nouveaux utilisateurs avec activation conditionnelle.
    
    Cette vue gère le processus d'inscription avec :
    - Validation du formulaire d'inscription
    - Création automatique du profil utilisateur
    - Attribution des groupes selon le rôle
    - Activation conditionnelle (participants = actifs, managers = en attente)
    - Connexion automatique pour les participants
    
    Args:
        request: Objet HttpRequest (GET pour affichage, POST pour traitement)
        
    Returns:
        HttpResponse: Template d'inscription ou redirection vers dashboard/login
    """
    # Traitement du formulaire d'inscription (méthode POST)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarde de l'utilisateur sans commit pour modification
            user = form.save(commit=False)
            
            # Activation conditionnelle selon le rôle
            if user.role == 'participant':
                user.is_active = True  # Participants actifs immédiatement
            
            # Sauvegarde définitive de l'utilisateur
            user.save()
            
            # Création automatique du profil utilisateur
            Profile.objects.create(user=user)
            
            # Attribution du groupe correspondant au rôle
            grp, _ = Group.objects.get_or_create(name=user.role)
            user.groups.add(grp)
            
            # Gestion selon le rôle
            if user.role == 'manager':
                # Managers : compte en attente d'activation
                messages.info(request, "Compte manager en attente d'activation")
                return redirect('login')
            
            # Participants : connexion automatique
            login(request, user)
            return redirect('dashboard')
    else:
        # Affichage du formulaire d'inscription (méthode GET)
        form = UserRegistrationForm()
    
    return render(request, 'entretiens/register.html', {'form': form})


# =============================================================================
# VUES PROTÉGÉES (NÉCESSITENT UNE CONNEXION)
# =============================================================================

@login_required
def user_logout(request):
    """
    Déconnexion sécurisée de l'utilisateur.
    
    Cette vue gère la déconnexion en :
    - Supprimant la session utilisateur
    - Redirigeant vers la page de connexion
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Redirection vers la page de connexion
    """
    logout(request)
    return redirect('login')


@login_required
def complete_manager_details(request):
    """
    Formulaire pour compléter les informations professionnelles du manager.
    
    Cette vue permet aux managers de renseigner leurs détails professionnels :
    - Poste interne occupé
    - Date d'embauche
    - Numéro de contrat
    - Service/département
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Template du formulaire ou redirection vers dashboard
    """
    # Récupération ou création des détails manager
    md, _ = ManagerDetails.objects.get_or_create(manager=request.user)
    
    # Traitement du formulaire (méthode POST)
    if request.method == 'POST':
        form = ManagerDetailsForm(request.POST, instance=md)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Affichage du formulaire (méthode GET)
        form = ManagerDetailsForm(instance=md)
    
    return render(request, 'entretiens/complete_manager_details.html', {'form': form})


@login_required
def dashboard(request):
    """
    Tableau de bord principal adaptatif selon le rôle utilisateur.
    
    Cette vue centrale affiche différentes informations selon le rôle :
    
    ADMINISTRATEUR :
    - Vue globale de tous les utilisateurs
    - Liste de tous les postes
    - Vue de tous les entretiens
    
    MANAGER :
    - Ses postes créés uniquement
    - Candidatures pour ses postes
    - Entretiens qu'il mène
    - Vérification des détails professionnels
    
    PARTICIPANT :
    - Tous les postes disponibles
    - Ses candidatures personnelles
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Template dashboard spécifique au rôle
    """
    role = request.user.role
    
    # Vérification spéciale pour les managers : détails professionnels requis
    if role == 'manager':
        try:
            _ = request.user.managerdetails
        except ManagerDetails.DoesNotExist:
            # Redirection vers le formulaire de complétion des détails
            return redirect('complete_manager_details')

    # Préparation du contexte selon le rôle
    context = {}
    
    if role == 'administrateur':
        # Vue globale pour l'administrateur
        context.update({
            'users': User.objects.all(),           # Tous les utilisateurs
            'postes': Poste.objects.all(),         # Tous les postes
            'entretiens': Entretien.objects.all(), # Tous les entretiens
        })
    elif role == 'manager':
        # Vue managériale : données liées au manager connecté
        context.update({
            'postes': Poste.objects.filter(manager=request.user),                    # Postes créés par ce manager
            'candidats': CandidatPoste.objects.filter(poste__manager=request.user), # Candidatures pour ses postes
            'entretiens': Entretien.objects.filter(manager=request.user),           # Entretiens menés par ce manager
        })
    else:  # participant
        # Vue participante : postes disponibles + candidatures personnelles
        context.update({
            'postes': Poste.objects.all(),                                    # Tous les postes disponibles
            'mes_candidatures': CandidatPoste.objects.filter(candidat=request.user), # Candidatures du participant
        })
    
    # Rendu du template spécifique au rôle
    return render(request, f"entretiens/dashboard_{role}.html", context)


# =============================================================================
# GESTION DES POSTES (CRUD - Create, Read, Update, Delete)
# =============================================================================

@login_required
def poste_list(request):
    """
    Affichage de la liste des postes selon le rôle utilisateur.
    
    Cette vue filtre les postes selon le rôle :
    - MANAGER : Affiche uniquement ses propres postes
    - AUTRES : Affiche tous les postes disponibles
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Template de liste des postes
    """
    if request.user.role == 'manager':
        # Managers : seulement leurs postes
        qs = Poste.objects.filter(manager=request.user)
    else:
        # Participants et administrateurs : tous les postes
        qs = Poste.objects.all()
    
    return render(request, 'entretiens/poste_list.html', {'postes': qs})


@login_required
def poste_create(request):
    """
    Création d'un nouveau poste par un manager.
    
    Cette vue permet aux managers de créer des postes avec :
    - Validation du formulaire
    - Attribution automatique du manager connecté
    - Redirection vers la liste des postes
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Template du formulaire ou redirection vers la liste
    """
    # Traitement du formulaire de création (méthode POST)
    if request.method == 'POST':
        form = PosteForm(request.POST)
        if form.is_valid():
            # Sauvegarde sans commit pour attribution du manager
            p = form.save(commit=False)
            p.manager = request.user  # Attribution automatique du manager connecté
            p.save()
            return redirect('poste_list')
    else:
        # Affichage du formulaire vide (méthode GET)
        form = PosteForm()
    
    return render(request, 'entretiens/poste_form.html', {'form': form})


@login_required
def poste_edit(request, pk):
    """Modification d’un poste existant (manager)."""
    p = get_object_or_404(Poste, pk=pk, manager=request.user)
    if request.method == 'POST':
        form = PosteForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect('poste_list')
    else:
        form = PosteForm(instance=p)
    return render(request, 'entretiens/poste_form.html', {'form': form})


@login_required
def poste_delete(request, pk):
    """Suppression d’un poste par le manager."""
    p = get_object_or_404(Poste, pk=pk, manager=request.user)
    p.delete()
    return redirect('poste_list')


# --- Candidatures (participant) ---

@login_required
def postuler(request, pk):
    """Postuler à un poste (participant)."""
    poste = get_object_or_404(Poste, pk=pk)
    obj, created = CandidatPoste.objects.get_or_create(candidat=request.user, poste=poste)
    if not created:
        messages.warning(request, "Vous avez déjà postulé à ce poste.")
    else:
        messages.success(request, "Votre candidature a été enregistrée.")
    return redirect('mes_candidatures')


@login_required
def mes_candidatures(request):
    """Liste des candidatures du participant."""
    candidatures = CandidatPoste.objects.filter(candidat=request.user) \
                                        .prefetch_related('entretiens', 'poste__manager')
    return render(request, 'entretiens/mes_candidatures.html', {'candidatures': candidatures})


@login_required
def candidature_delete(request, pk):
    """
    Annulation d’une candidature par le participant.
    Gestion propre si introuvable ou non accessible.
    """
    try:
        cp = CandidatPoste.objects.get(pk=pk, candidat=request.user)
    except CandidatPoste.DoesNotExist:
        messages.error(request, "Candidature introuvable ou non accessible.")
        return redirect('mes_candidatures')

    cp.delete()
    messages.success(request, "Votre candidature a bien été annulée.")
    return redirect('mes_candidatures')


@login_required
def refuser_candidature(request, pk):
    """
    Permet au manager de refuser une candidature :
    - passe le statut à 'refusé'
    - message de confirmation
    """
    cp = get_object_or_404(
        CandidatPoste,
        pk=pk,
        poste__manager=request.user,
        status='en cours de planification'
    )
    cp.status = 'refusé'
    cp.save()
    messages.success(
        request,
        f"Candidature de {cp.candidat.username} pour « {cp.poste.titre} » refusée."
    )
    return redirect('dashboard')


# --- Planification des entretiens ---

@login_required
def candidats_du_poste(request, pk):
    """Liste des candidatures pour un poste (manager)."""
    candidats = CandidatPoste.objects.filter(poste_id=pk)
    return render(request, 'entretiens/poste_candidats.html', {'candidats': candidats})


# =============================================================================
# GESTION DES ENTRETIENS - PLANIFICATION INTELLIGENTE
# =============================================================================

@login_required
def planifier_entretien(request, cp_pk):
    """
    Planification intelligente d'un entretien avec gestion des conflits.
    
    Cette vue gère la planification d'entretiens avec des vérifications avancées :
    
    1. EMPÊCHE LA DOUBLE-PLANIFICATION :
       - Vérifie qu'aucun entretien n'existe déjà pour cette candidature
    
    2. GESTION DES CONFLITS MANAGER :
       - Vérifie qu'aucun entretien n'est prévu ±2h pour le manager
    
    3. GESTION DES CONFLITS CANDIDAT :
       - Vérifie qu'aucun entretien n'est prévu le même jour pour le candidat
    
    4. CRÉATION DE L'ENTRETIEN :
       - Met à jour le statut de candidature en 'planifié'
       - Envoie un email automatique au candidat
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        cp_pk: ID de la candidature (CandidatPoste) concernée
        
    Returns:
        HttpResponse: Template de planification ou redirection vers dashboard
    """
    # Récupération de la candidature avec vérification des permissions
    cp = get_object_or_404(CandidatPoste, pk=cp_pk, poste__manager=request.user)

    # 1. VÉRIFICATION : Empêche la re-planification
    if Entretien.objects.filter(candidat_poste=cp).exists():
        messages.warning(request, "Un entretien est déjà planifié pour ce candidat et ce poste.")
        return redirect('dashboard')

    # Traitement du formulaire de planification (méthode POST)
    if request.method == 'POST':
        form = EntretienPlanForm(request.POST)
        if form.is_valid():
            date_heure = form.cleaned_data['date']

            # 2. VÉRIFICATION CONFLIT MANAGER : ±2h
            start = date_heure - timedelta(hours=2)
            end   = date_heure + timedelta(hours=2)
            conflit_mgr = Entretien.objects.filter(
                manager=request.user,
                date__range=(start, end)
            ).exists()

            # 3. VÉRIFICATION CONFLIT CANDIDAT : même jour
            day = date_heure.date()
            conflit_cand = Entretien.objects.filter(
                candidat_poste__candidat=cp.candidat,
                date__date=day
            ).exists()

            # Gestion des conflits détectés
            if conflit_mgr:
                messages.error(request, "Vous avez déjà un entretien dans un créneau proche (±2h).")
            if conflit_cand:
                messages.error(request, "Ce candidat a déjà un entretien prévu le même jour.")

            # 4. CRÉATION DE L'ENTRETIEN si aucun conflit
            if not (conflit_mgr or conflit_cand):
                # Création de l'entretien
                entretien = form.save(commit=False)
                entretien.manager = request.user
                entretien.candidat_poste = cp
                entretien.save()

                # Mise à jour du statut de candidature
                cp.status = 'planifié'
                cp.save()

                # 5. ENVOI D'EMAIL AUTOMATIQUE au candidat
                subject = f"[InterViewPro] Entretien planifié pour le poste « {cp.poste.titre} »"
                message = (
                   f"Bonjour {cp.candidat.first_name},\n\n"
                   f"Votre entretien a été planifié avec succès.\n\n"
                   f"- Poste       : {cp.poste.titre}\n"
                   f"- Manager     : {request.user.get_full_name()} ({request.user.email})\n"
                   f"- Date & heure: {date_heure.strftime('%d/%m/%Y à %H:%M')}\n\n"
                   "Merci et à bientôt sur InterViewPro."
                )
                send_mail(subject, message, None, [cp.candidat.email], fail_silently=False)

                messages.success(request, "Entretien planifié et email envoyé au candidat.")
                return redirect('dashboard')
    else:
        # Affichage du formulaire de planification (méthode GET)
        form = EntretienPlanForm()

    return render(request, 'entretiens/planifier_entretien.html', {'form': form, 'cp': cp})


# --- Liste / édition / suppression des entretiens ---

@login_required
def entretien_list(request):
    """Liste des entretiens selon le rôle."""
    if request.user.role == 'manager':
        qs = Entretien.objects.filter(manager=request.user)
    else:
        qs = Entretien.objects.filter(candidat_poste__candidat=request.user)
    return render(request, 'entretiens/entretiens_list.html', {'entretiens': qs})


@login_required
def entretien_edit(request, pk):
    """Modification d’un entretien existant."""
    e = get_object_or_404(Entretien, pk=pk)
    if request.method == 'POST':
        form = EntretienPlanForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            return redirect('entretien_list')
    else:
        form = EntretienPlanForm(instance=e)
    return render(request, 'entretiens/entretien_form.html', {'form': form})


@login_required
def entretien_delete(request, pk):
    entretien = get_object_or_404(Entretien, pk=pk, manager=request.user)
    cp = entretien.candidat_poste
    # Suppression de l’entretien
    entretien.delete()

    # Refus automatique de la candidature
    cp.status = 'refusé'
    cp.save()

    messages.success(
        request,
        f"Entretien annulé et candidature de {cp.candidat.username} pour « {cp.poste.titre} » refusée."
    )
    return redirect('dashboard')
