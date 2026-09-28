from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, ManagerDetails, Poste, CandidatPoste, Entretien, User

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin): 
    pass


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profils'


class ManagerDetailsInline(admin.StackedInline):
    model = ManagerDetails
    can_delete = False
    verbose_name_plural = 'Détails professionnels'


class CandidatPosteInline(admin.TabularInline):
    model = CandidatPoste
    fk_name = 'candidat'
    extra = 0
    verbose_name = 'Candidature'
    verbose_name_plural = 'Candidatures'


class EntretienManagerInline(admin.TabularInline):
    model = Entretien
    fk_name = 'manager'
    extra = 0
    verbose_name = 'Entretien'
    verbose_name_plural = 'Entretiens (manager)'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (
        ProfileInline,
        ManagerDetailsInline,
        CandidatPosteInline,
        EntretienManagerInline,
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
    )
    list_filter = ('role', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Profil & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )


# On essaie de désenregistrer l’ancien User si présent
from django.contrib.admin.sites import NotRegistered
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)


@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'manager')
    search_fields = ('titre', 'manager__username')


@admin.register(CandidatPoste)
class CandidatPosteAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'poste', 'status', 'date_affectation')
    list_filter = ('status',)
    search_fields = ('candidat__username', 'poste__titre')


@admin.register(Entretien)
class EntretienAdmin(admin.ModelAdmin):
    list_display = ('id', 'manager', 'candidat_poste', 'date', 'rappels_envoyes')
    list_filter = ('rappels_envoyes',)
    search_fields = ('manager__username', 'candidat_poste__candidat__username')



admin.site.site_header = "InterViewPro Administration"
admin.site.site_title  = "InterViewPro Admin Portal"
admin.site.index_title = "Tableau de Bord InterViewPro"

User = get_user_model()