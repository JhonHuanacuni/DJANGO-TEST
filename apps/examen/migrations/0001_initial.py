# Generated by Django 5.2 on 2025-05-01 16:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cursos', to='examen.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Examen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True)),
                ('tipo', models.IntegerField(choices=[(40, '40 preguntas'), (100, '100 preguntas')])),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('tiempo_limite', models.IntegerField(help_text='Tiempo límite en minutos')),
                ('visible', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examenes', to='examen.categoria')),
                ('creado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='examenes_creados', to=settings.AUTH_USER_MODEL)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examenes', to='examen.curso')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('area', models.CharField(choices=[('act', 'ACT'), ('hm', 'Habilidad Matemática'), ('hv', 'Habilidad Verbal'), ('arit', 'Aritmética'), ('geo', 'Geometría'), ('alge', 'Álgebra'), ('trigo', 'Trigonometría'), ('lengua', 'Lenguaje'), ('lit', 'Literatura'), ('psi', 'Psicología'), ('civ', 'Cívica'), ('hp', 'Historia del Perú'), ('hu', 'Historia Universal'), ('geo_l', 'Geografía'), ('eco', 'Economía'), ('filo', 'Filosofía'), ('fis', 'Física'), ('qui', 'Química'), ('bio', 'Biología')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas', to='examen.examen')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Alternativa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=255)),
                ('es_correcta', models.BooleanField(default=False)),
                ('puntaje', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('orden', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alternativas', to='examen.pregunta')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje', models.DecimalField(decimal_places=2, max_digits=5)),
                ('porcentaje', models.DecimalField(decimal_places=2, max_digits=5)),
                ('correctas', models.IntegerField()),
                ('incorrectas', models.IntegerField()),
                ('no_respuesta', models.IntegerField()),
                ('detalle_areas', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas_examen', to=settings.AUTH_USER_MODEL)),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notas', to='examen.examen')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('estudiante', 'examen')},
            },
        ),
    ]
