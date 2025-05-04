from django.db import migrations, models
import django.db.models.deletion

def asignar_curso_por_defecto(apps, schema_editor):
    Examen = apps.get_model('examen', 'Examen')
    Curso = apps.get_model('examen', 'Curso')
    
    # Obtener o crear un curso por defecto
    curso_por_defecto, _ = Curso.objects.get_or_create(
        nombre='Curso por Defecto',
        defaults={'descripcion': 'Curso temporal para exámenes existentes'}
    )
    
    # Asignar el curso por defecto a todos los exámenes que no tengan curso
    Examen.objects.filter(curso__isnull=True).update(curso=curso_por_defecto)

class Migration(migrations.Migration):

    dependencies = [
        ('examen', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examen',
            name='curso',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='examenes',
                to='examen.curso',
                null=True,
                blank=True
            ),
        ),
        migrations.RunPython(asignar_curso_por_defecto),
        migrations.AlterField(
            model_name='examen',
            name='curso',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='examenes',
                to='examen.curso'
            ),
        ),
    ] 