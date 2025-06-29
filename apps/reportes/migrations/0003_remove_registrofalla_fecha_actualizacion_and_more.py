# Generated by Django 4.2.20 on 2025-06-12 05:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reportes', '0002_registrofalla_alter_reportegenerado_tipo_reporte_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrofalla',
            name='fecha_actualizacion',
        ),
        migrations.RemoveField(
            model_name='registrofalla',
            name='reporte_tecnico',
        ),
        migrations.AddField(
            model_name='registrofalla',
            name='documento_analisis',
            field=models.FileField(blank=True, null=True, upload_to='fallas/documentos/', verbose_name='Documento de Análisis'),
        ),
        migrations.AlterField(
            model_name='seguimientofalla',
            name='fecha_accion',
            field=models.DateTimeField(verbose_name='Fecha de la Acción'),
        ),
        migrations.AlterField(
            model_name='seguimientofalla',
            name='responsable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seguimientos_realizados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='seguimientofalla',
            name='tipo_accion',
            field=models.CharField(choices=[('diagnostico', 'Diagnóstico'), ('reparacion', 'Reparación'), ('analisis', 'Análisis'), ('seguimiento', 'Seguimiento'), ('cierre_falla', 'Cierre de Falla'), ('asignacion', 'Asignación'), ('escalamiento', 'Escalamiento'), ('validacion', 'Validación')], max_length=20, verbose_name='Tipo de Acción'),
        ),
    ]
