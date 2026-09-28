
# Ce fichier définit toutes les URLs de l'application InterViewPro
# Chaque URL est mappée vers une vue spécifique avec un nom unique

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# =============================================================================
# CONFIGURATION DES PATTERNS D'URLS DE L'APPLICATION
# =============================================================================

urlpatterns = [
    # =============================================================================
    # PAGES PUBLIQUES (ACCESSIBLES SANS CONNEXION)
    # =============================================================================
    
    # Page d'accueil publique
    path('', views.home, name='home'),
    
    # Authentification
    path('login/', views.user_login, name='login'),           # Connexion utilisateur
    path('register/', views.user_register, name='register'), # Inscription utilisateur
    path('logout/', views.user_logout, name='logout'),        # Déconnexion utilisateur
    
    # =============================================================================
    # PAGES PROTÉGÉES (NÉCESSITENT UNE CONNEXION)
    # =============================================================================
    
    # Complétion des détails manager (première connexion)
    path('complete-manager/', views.complete_manager_details, name='complete_manager_details'),
    
    # Tableau de bord principal (adaptatif selon le rôle)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # =============================================================================
    # GESTION DES POSTES (CRUD)
    # =============================================================================
    
    # Liste des postes (filtrée selon le rôle)
    path('postes/', views.poste_list, name='poste_list'),
    
    # Création d'un nouveau poste (managers uniquement)
    path('postes/create/', views.poste_create, name='poste_create'),
    
    # Modification d'un poste existant (managers uniquement)
    path('postes/<int:pk>/edit/', views.poste_edit, name='poste_edit'),
    
    # Suppression d'un poste (managers uniquement)
    path('postes/<int:pk>/delete/', views.poste_delete, name='poste_delete'),
    
    # Liste des candidats pour un poste spécifique (managers uniquement)
    path('postes/<int:pk>/candidats/', views.candidats_du_poste, name='post_candidats'),
    
    
    # GESTION DES CANDIDATURES
    
    # Postuler à un poste (participants uniquement)
    path('postuler/<int:pk>/', views.postuler, name='postuler'),
    
    # Liste des candidatures du participant connecté
    path('mes-candidatures/', views.mes_candidatures, name='mes_candidatures'),
    
    # Refuser une candidature (managers uniquement)
    path('candidature/<int:pk>/refuser/', views.refuser_candidature, name='candidature_refuser'),
    
    # Annuler une candidature (participants uniquement)
    path('candidature/<int:pk>/delete/', views.candidature_delete, name='candidature_delete'),
    
    
    
    
    # Planification d'un entretien (managers uniquement)
    path('planifier/<int:cp_pk>/', views.planifier_entretien, name='planifier_entretien'),
    
    # Liste des entretiens (filtrée selon le rôle)
    path('entretiens/', views.entretien_list, name='entretien_list'),
    
    # Modification d'un entretien existant
    path('entretiens/<int:pk>/edit/', views.entretien_edit, name='entretien_edit'),
    
    # Suppression d'un entretien (managers uniquement)
    path('entretiens/<int:pk>/delete/', views.entretien_delete, name='entretien_delete'),
]


# CONFIGURATION DES FICHIERS MÉDIA (DÉVELOPPEMENT UNIQUEMENT)

# Configuration pour servir les fichiers média en mode développement
# En production, ces fichiers doivent être servis par le serveur web (Apache/Nginx)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)