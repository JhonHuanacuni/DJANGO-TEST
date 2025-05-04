from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('notas', '0002_initial'),
        ('membresias', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='importacionnotas',
            name='salon',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='membresias.salon',
                help_text='Salón donde se tomó el examen'
            ),
        ),
    ] 