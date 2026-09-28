# my_app/migrations/000X_remove_entretien_nullable.py

from django.db import migrations, models


def clean_null_candidat_poste(apps, schema_editor):
    """
    Supprime ou traite les Entretien dont candidat_poste est NULL 
    pour éviter l'erreur lors de la suppression de null=True.
    Ici, on supprime simplement ces entretiens orphelins.
    """
    Entretien = apps.get_model('my_app', 'Entretien')
    Entretien.objects.filter(candidat_poste__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0002_alter_candidatposte_status_and_more'),
    ]

    operations = [
        # 1) On nettoie d'abord les enregistrements orphelins
        migrations.RunPython(clean_null_candidat_poste, reverse_code=migrations.RunPython.noop),

        # 2) Puis on modifie le champ pour le rendre non-nullable
        migrations.AlterField(
            model_name='entretien',
            name='candidat_poste',
            field=models.ForeignKey(
                to='my_app.CandidatPoste',
                on_delete=models.CASCADE,
                related_name='entretiens',
            ),
        ),
    ]
