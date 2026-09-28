# =============================================================================
# MODÈLES DE DONNÉES - INTERVIEWPRO
# =============================================================================
# Ce fichier définit la structure de la base de données SQLite
# Chaque classe représente une table dans la base de données
# Django ORM traduit automatiquement ces modèles en requêtes SQL

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# =============================================================================
# MODÈLE UTILISATEUR PERSONNALISÉ
# =============================================================================
class User(AbstractUser):
    """
    Modèle utilisateur personnalisé qui étend AbstractUser de Django.
    
    Hérite de AbstractUser qui fournit :
    - username, email, password
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login
    
    Ajoute des champs spécifiques à notre application d'entretiens.
    """
    
    # Définition des rôles disponibles dans l'application
    ROLE_CHOICES = [
        ('administrateur', 'Administrateur'),  # Gère tout le système
        ('manager',        'Manager'),          # Crée des postes et planifie des entretiens
        ('participant',    'Participant'),      # Postule aux postes et participe aux entretiens
    ]
    
    # Champ rôle : définit le type d'utilisateur avec des choix prédéfinis
    role = models.CharField(
        max_length=15, 
        choices=ROLE_CHOICES, 
        default='participant'  # Nouvel utilisateur = participant par défaut
    )
    
    # Champ d'activation : contrôle si l'utilisateur peut se connecter
    # Les managers doivent être activés par un administrateur
    is_active = models.BooleanField(default=False)

    def __str__(self):
        """
        Représentation textuelle de l'utilisateur.
        Format : "nom_utilisateur (Rôle)"
        Exemple : "john_doe (Manager)"
        """
        return f"{self.username} ({self.get_role_display()})"


# =============================================================================
# MODÈLE PROFIL UTILISATEUR
# =============================================================================
class Profile(models.Model):
    """
    Profil étendu pour tous les utilisateurs.
    
    Relation OneToOne avec User :
    - Un utilisateur = Un profil
    - Stocke des informations personnelles supplémentaires
    - Créé automatiquement lors de l'inscription
    """
    
    # Relation un-à-un avec le modèle User personnalisé
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Référence vers notre modèle User personnalisé
        on_delete=models.CASCADE,   # Si l'utilisateur est supprimé, son profil aussi
        related_name='profile'      # Permet d'accéder au profil via user.profile
    )
    
    # Informations personnelles optionnelles
    date_naissance = models.DateField(null=True, blank=True)  # Peut être vide
    adresse         = models.CharField(max_length=255, blank=True)  # Chaîne vide autorisée
    contact         = models.CharField(max_length=50,  blank=True)  # Téléphone, etc.

    def __str__(self):
        """Représentation textuelle du profil."""
        return f"Profil de {self.user.username}"



# MODÈLE DÉTAILS MANAGER

class ManagerDetails(models.Model):
    """
    Informations professionnelles spécifiques aux managers.
    
    Relation OneToOne avec User (rôle manager uniquement) :
    - Un manager = Un profil professionnel
    - Contient des données RH (poste, contrat, service)
    """
    
    # Relation un-à-un avec les utilisateurs ayant le rôle 'manager'
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'manager'},  # Seuls les managers peuvent avoir ce profil
        on_delete=models.CASCADE
    )
    
    # Informations professionnelles
    poste_interne   = models.CharField(max_length=100, blank=True)  # Poste occupé par le manager
    date_embauche   = models.DateField(null=True, blank=True)       # Date d'embauche
    numero_contrat  = models.CharField(max_length=50, blank=True)   # Numéro de contrat
    service         = models.CharField(max_length=100, blank=True) # Service/département

    def __str__(self):
        """Représentation textuelle des détails manager."""
        return f"Détails pro de {self.manager.username}"



# MODÈLE POSTE

class Poste(models.Model):
    """
    Représente un poste à pourvoir dans l'entreprise.
    
    Relation Many-to-One avec User (manager) :
    - Un manager peut créer plusieurs postes
    - Un poste appartient à un seul manager
    """
    
    # Informations du poste
    titre       = models.CharField(max_length=100)  # Titre du poste (ex: "Développeur Python")
    description = models.TextField(blank=True)       # Description détaillée du poste
    
    # Relation avec le manager qui crée le poste
    manager     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'manager'},  # Seuls les managers peuvent créer des postes
        on_delete=models.CASCADE,               # Si le manager est supprimé, ses postes aussi
        related_name='postes_crees'             # Permet d'accéder aux postes via manager.postes_crees
    )

    def __str__(self):
        """Représentation textuelle du poste."""
        return self.titre



# MODÈLE CANDIDATURE

class CandidatPoste(models.Model):
    """
    Représente une candidature d'un participant à un poste.
    
    Relations :
    - Many-to-One avec User (candidat)
    - Many-to-One avec Poste
    - Un participant peut postuler à plusieurs postes
    - Un poste peut recevoir plusieurs candidatures
    """
    
    # Définition des statuts de candidature
    STATUS_CHOICES = [
        ('en cours de planification', 'En cours de planification'),  # Candidature reçue, en attente
        ('planifié',                   'Planifié'),                   # Entretien planifié
        ('refusé',                     'Refusé'),                      # Candidature refusée
    ]
    
    # Relation avec le candidat (participant uniquement)
    candidat         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'participant'},  # Seuls les participants peuvent postuler
        on_delete=models.CASCADE,
        related_name='candidatures'                 # Permet d'accéder aux candidatures via candidat.candidatures
    )
    
    # Relation avec le poste
    poste            = models.ForeignKey(
        Poste,
        on_delete=models.CASCADE,
        related_name='candidats_poste'             # Permet d'accéder aux candidats via poste.candidats_poste
    )
    
    # Informations de la candidature
    date_affectation = models.DateField(auto_now_add=True)  # Date automatique de candidature
    status           = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='en cours de planification'       # Statut par défaut
    )

    class Meta:
        """
        Métadonnées du modèle.
        Contraintes et configurations spéciales.
        """
        # Empêche qu'un candidat postule plusieurs fois au même poste
        unique_together = ('candidat', 'poste')

    def __str__(self):
        """Représentation textuelle de la candidature."""
        return f"{self.candidat.username} → {self.poste.titre} ({self.status})"



# MODÈLE ENTRETIEN

class Entretien(models.Model):
    """
    Représente un entretien planifié entre un manager et un candidat.
    
    Relations :
    - Many-to-One avec User (manager)
    - Many-to-One avec CandidatPoste
    - Un manager peut avoir plusieurs entretiens
    - Une candidature peut avoir plusieurs entretiens (suivi)
    """
    
    # Relation avec le manager qui mène l'entretien
    manager         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'manager'},  # Seuls les managers peuvent mener des entretiens
        related_name='entretiens_manager',     # Permet d'accéder aux entretiens via manager.entretiens_manager
        on_delete=models.CASCADE
    )
    
    # Relation avec la candidature concernée
    candidat_poste  = models.ForeignKey(
        CandidatPoste,
        related_name='entretiens',             # Permet d'accéder aux entretiens via candidat_poste.entretiens
        on_delete=models.CASCADE
    )
    
    # Informations de l'entretien
    date            = models.DateTimeField()   # Date et heure de l'entretien
    compte_rendu    = models.TextField(blank=True)  # Notes de l'entretien (peut être vide)
    rappels_envoyes = models.BooleanField(default=False)  # Suivi des rappels par email

    def __str__(self):
        """
        Représentation textuelle de l'entretien.
        Format : "Entretien ID — candidat / poste"
        Exemple : "Entretien 1 — john_doe / Développeur Python"
        """
        return f"Entretien {self.id} — {self.candidat_poste.candidat.username} / {self.candidat_poste.poste.titre}"
