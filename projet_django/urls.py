# =============================================================================
# ROUTAGE PRINCIPAL DU PROJET DJANGO - INTERVIEWPRO
# =============================================================================
# Ce fichier définit les URLs principales du projet
# Il redirige les requêtes vers les applications appropriées

"""
URL configuration for projet_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Imports Django pour le routage
from django.contrib import admin
from django.urls import path, include

# =============================================================================
# CONFIGURATION DES PATTERNS D'URLS
# =============================================================================

urlpatterns = [
    # Interface d'administration Django (accessible via /admin/)
    # Permet aux administrateurs de gérer les données via l'interface Django
    path('admin/', admin.site.urls),
    
    # Redirection de toutes les autres URLs vers notre application principale
    # Toutes les URLs commençant par '' (racine) sont dirigées vers my_app.urls
    path('', include('my_app.urls')),
]
