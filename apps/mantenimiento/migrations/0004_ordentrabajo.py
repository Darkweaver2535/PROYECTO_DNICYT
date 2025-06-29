# Generated by Django 4.2.20 on 2025-06-10 22:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipos', '0005_equipo_amperaje_equipo_caudal_aire_and_more'),
        ('mantenimiento', '0003_alter_planmantenimiento_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenTrabajo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_orden', models.CharField(max_length=20, unique=True, verbose_name='Número de Orden')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título de la Orden')),
                ('descripcion', models.TextField(verbose_name='Descripción del Trabajo')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('asignada', 'Asignada'), ('en_progreso', 'En Progreso'), ('pausada', 'Pausada'), ('completada', 'Completada'), ('cancelada', 'Cancelada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=20, verbose_name='Estado')),
                ('prioridad', models.CharField(choices=[('baja', 'Baja'), ('normal', 'Normal'), ('alta', 'Alta'), ('urgente', 'Urgente'), ('critica', 'Crítica')], default='normal', max_length=20, verbose_name='Prioridad')),
                ('tipo_orden', models.CharField(choices=[('preventivo', 'Mantenimiento Preventivo'), ('correctivo', 'Mantenimiento Correctivo'), ('predictivo', 'Mantenimiento Predictivo'), ('emergencia', 'Emergencia'), ('mejora', 'Mejora'), ('instalacion', 'Instalación'), ('inspeccion', 'Inspección')], max_length=20, verbose_name='Tipo de Orden')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_programada', models.DateTimeField(blank=True, null=True, verbose_name='Fecha Programada')),
                ('fecha_inicio_real', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Inicio Real')),
                ('fecha_fin_programada', models.DateTimeField(blank=True, null=True, verbose_name='Fecha Fin Programada')),
                ('fecha_completada', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Completación')),
                ('horas_estimadas', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Horas Estimadas')),
                ('horas_reales', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Horas Reales')),
                ('costo_estimado', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Costo Estimado')),
                ('costo_real', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Costo Real')),
                ('materiales_necesarios', models.TextField(blank=True, null=True, verbose_name='Materiales Necesarios')),
                ('herramientas_necesarias', models.TextField(blank=True, null=True, verbose_name='Herramientas Necesarias')),
                ('procedimientos_seguir', models.TextField(blank=True, null=True, verbose_name='Procedimientos a Seguir')),
                ('observaciones_iniciales', models.TextField(blank=True, null=True, verbose_name='Observaciones Iniciales')),
                ('trabajo_realizado', models.TextField(blank=True, null=True, verbose_name='Trabajo Realizado')),
                ('observaciones_finales', models.TextField(blank=True, null=True, verbose_name='Observaciones Finales')),
                ('repuestos_utilizados', models.TextField(blank=True, null=True, verbose_name='Repuestos Utilizados')),
                ('requiere_pruebas', models.BooleanField(default=False, verbose_name='Requiere Pruebas')),
                ('pruebas_realizadas', models.TextField(blank=True, null=True, verbose_name='Pruebas Realizadas')),
                ('resultado_satisfactorio', models.BooleanField(default=False, verbose_name='Resultado Satisfactorio')),
                ('documentos_adjuntos', models.FileField(blank=True, null=True, upload_to='ordenes_trabajo/documentos/', verbose_name='Documentos Adjuntos')),
                ('fotos_antes', models.ImageField(blank=True, null=True, upload_to='ordenes_trabajo/fotos_antes/', verbose_name='Fotos Antes del Trabajo')),
                ('fotos_despues', models.ImageField(blank=True, null=True, upload_to='ordenes_trabajo/fotos_despues/', verbose_name='Fotos Después del Trabajo')),
                ('comentarios_adicionales', models.TextField(blank=True, null=True, verbose_name='Comentarios Adicionales')),
                ('requiere_seguimiento', models.BooleanField(default=False, verbose_name='Requiere Seguimiento')),
                ('fecha_proximo_seguimiento', models.DateField(blank=True, null=True, verbose_name='Próximo Seguimiento')),
                ('calificacion_trabajo', models.PositiveIntegerField(blank=True, help_text='Calificación de 1 a 5 estrellas', null=True, verbose_name='Calificación del Trabajo (1-5)')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('asignado_a', models.ForeignKey(blank=True, help_text='Técnico o responsable asignado', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_asignadas', to=settings.AUTH_USER_MODEL)),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordenes_trabajo', to='equipos.equipo')),
                ('plan_mantenimiento', models.ForeignKey(blank=True, help_text='Plan de mantenimiento que generó esta orden (si aplica)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_trabajo', to='mantenimiento.planmantenimiento')),
                ('solicitante', models.ForeignKey(help_text='Usuario que solicita el trabajo', on_delete=django.db.models.deletion.CASCADE, related_name='ordenes_solicitadas', to=settings.AUTH_USER_MODEL)),
                ('supervisado_por', models.ForeignKey(blank=True, help_text='Supervisor a cargo', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_supervisadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Orden de Trabajo',
                'verbose_name_plural': 'Órdenes de Trabajo',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
