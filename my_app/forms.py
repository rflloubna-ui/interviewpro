# =============================================================================
# FORMULAIRES DJANGO CRISPY FORMS - INTERVIEWPRO
# =============================================================================
# Ce fichier définit tous les formulaires de l'application
# Django Crispy Forms améliore l'apparence et la fonctionnalité des formulaires
# Chaque formulaire est lié à un modèle Django pour la validation automatique

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, ManagerDetails, Poste, CandidatPoste, Entretien

# =============================================================================
# FORMULAIRE D'INSCRIPTION UTILISATEUR
# =============================================================================
class UserRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé basé sur UserCreationForm.
    
    Hérite de UserCreationForm qui fournit :
    - username, password1, password2
    - Validation automatique des mots de passe
    - Vérification d'unicité du nom d'utilisateur
    
    Ajoute des champs spécifiques à notre application :
    - role : choix entre manager et participant
    - email : adresse email obligatoire
    - Styling Bootstrap avec classes CSS
    """
    
    # Champ rôle avec choix limités (pas d'administrateur via inscription)
    role = forms.ChoiceField(
        choices=[('manager','Manager'),('participant','Participant')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})  # Styling Bootstrap
    )
    
    # Email obligatoire avec validation automatique
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Nom d'utilisateur avec styling
    username = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        """
        Configuration du formulaire :
        - model : modèle User personnalisé
        - fields : champs à afficher dans l'ordre
        - widgets : personnalisation des champs de mot de passe
        """
        model = User
        fields = ['username','email','password1','password2','role']
        widgets = {
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

# =============================================================================
# FORMULAIRE PROFIL UTILISATEUR
# =============================================================================
class ProfileForm(forms.ModelForm):
    """
    Formulaire pour les informations personnelles du profil utilisateur.
    
    Ce formulaire permet de modifier :
    - date_naissance : date de naissance (widget date HTML5)
    - adresse : adresse personnelle
    - contact : informations de contact (téléphone, etc.)
    
    Utilise ModelForm pour la liaison automatique avec le modèle Profile.
    """
    
    class Meta:
        """
        Configuration du formulaire profil :
        - model : modèle Profile
        - fields : champs modifiables
        - widgets : personnalisation du champ date
        """
        model = Profile
        fields = ['date_naissance','adresse','contact']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type':'date'}),  # Widget date HTML5
        }


# =============================================================================
# FORMULAIRE DÉTAILS MANAGER
# =============================================================================
class ManagerDetailsForm(forms.ModelForm):
    """
    Formulaire pour les informations professionnelles des managers.
    
    Ce formulaire permet aux managers de renseigner :
    - poste_interne : poste occupé dans l'entreprise
    - date_embauche : date d'embauche (widget date HTML5)
    - numero_contrat : numéro de contrat
    - service : service/département
    
    Utilise ModelForm pour la liaison automatique avec le modèle ManagerDetails.
    """
    
    class Meta:
        """
        Configuration du formulaire détails manager :
        - model : modèle ManagerDetails
        - fields : tous les champs du modèle
        - widgets : personnalisation du champ date
        """
        model = ManagerDetails
        fields = ['poste_interne','date_embauche','numero_contrat','service']
        widgets = {
            'date_embauche': forms.DateInput(attrs={'type':'date'})  # Widget date HTML5
        }


# =============================================================================
# FORMULAIRE CRÉATION/MODIFICATION POSTE
# =============================================================================
class PosteForm(forms.ModelForm):
    """
    Formulaire pour la création et modification des postes.
    
    Ce formulaire permet aux managers de :
    - Définir le titre du poste avec placeholder explicatif
    - Rédiger une description détaillée du poste
    - Utiliser des widgets stylés avec Bootstrap
    
    Le champ manager est automatiquement attribué dans la vue.
    """
    
    class Meta:
        """
        Configuration du formulaire poste :
        - model : modèle Poste
        - fields : champs modifiables par l'utilisateur
        - widgets : personnalisation avec placeholders et styling
        """
        model = Poste
        fields = ['titre','description']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Développeur Python Senior'  # Aide à la saisie
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez les responsabilités et exigences du poste...'  # Aide à la saisie
            })
        }

# =============================================================================
# FORMULAIRE CANDIDATURE (PLACEHOLDER)
# =============================================================================
class CandidatureForm(forms.ModelForm):
    """
    Formulaire de candidature (actuellement vide).
    
    Ce formulaire est préparé pour de futures fonctionnalités :
    - Lettre de motivation
    - CV upload
    - Informations complémentaires
    
    Actuellement, la candidature se fait par simple clic sur "Postuler".
    """
    
    class Meta:
        """
        Configuration du formulaire candidature :
        - model : modèle CandidatPoste
        - fields : vide pour l'instant (candidature par clic)
        """
        model = CandidatPoste
        fields = []  # Pas de champs supplémentaires pour l'instant


# =============================================================================
# FORMULAIRE PLANIFICATION ENTRETIEN
# =============================================================================
class EntretienPlanForm(forms.ModelForm):
    """
    Formulaire pour la planification des entretiens.
    
    Ce formulaire permet aux managers de :
    - Sélectionner la date et heure de l'entretien (widget datetime-local HTML5)
    - Ajouter des notes/compte-rendu préliminaire
    
    Utilise ModelForm pour la liaison automatique avec le modèle Entretien.
    """
    
    class Meta:
        """
        Configuration du formulaire planification :
        - model : modèle Entretien
        - fields : champs modifiables par le manager
        - widgets : personnalisation du champ datetime
        """
        model = Entretien
        fields = ['date','compte_rendu']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type':'datetime-local'})  # Widget datetime HTML5
        }
