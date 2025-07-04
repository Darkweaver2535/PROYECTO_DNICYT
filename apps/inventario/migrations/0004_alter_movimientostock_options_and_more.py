# Generated by Django 4.2.20 on 2025-06-11 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventario', '0003_hacer_campos_opcionales'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movimientostock',
            options={'ordering': ['-fecha_movimiento', '-fecha_creacion'], 'verbose_name': 'Movimiento de Stock', 'verbose_name_plural': 'Movimientos de Stock'},
        ),
        migrations.RemoveField(
            model_name='movimientostock',
            name='numero_lote',
        ),
        migrations.RemoveField(
            model_name='movimientostock',
            name='orden_trabajo',
        ),
        migrations.RemoveField(
            model_name='movimientostock',
            name='responsable_movimiento',
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='activo',
            field=models.BooleanField(default=True, verbose_name='Activo'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='aprobado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimientos_aprobados', to=settings.AUTH_USER_MODEL, verbose_name='Aprobado Por'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='costo_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Costo Total'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='documento_referencia',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Documento de Referencia'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('procesado', 'Procesado'), ('cancelado', 'Cancelado'), ('rechazado', 'Rechazado')], default='procesado', max_length=15, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True, verbose_name='Última Actualización'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='fecha_aprobacion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Aprobación'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Fecha de Creación'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='fecha_procesamiento',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Procesamiento'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='motivo_detalle',
            field=models.TextField(blank=True, null=True, verbose_name='Detalle del Motivo'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='notas_internas',
            field=models.TextField(blank=True, null=True, verbose_name='Notas Internas'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='numero_factura',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Número de Factura'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='numero_movimiento',
            field=models.CharField(default=1, max_length=20, unique=True, verbose_name='Número de Movimiento'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='numero_orden',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Número de Orden'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='requiere_aprobacion',
            field=models.BooleanField(default=False, verbose_name='Requiere Aprobación'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='ubicacion_destino',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ubicación Destino'),
        ),
        migrations.AddField(
            model_name='movimientostock',
            name='ubicacion_origen',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ubicación Origen'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='costo_unitario',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Costo Unitario'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='motivo',
            field=models.CharField(choices=[('compra', 'Compra'), ('produccion', 'Producción'), ('devolucion_proveedor', 'Devolución a Proveedor'), ('devolucion_cliente', 'Devolución de Cliente'), ('uso_mantenimiento', 'Uso en Mantenimiento'), ('uso_produccion', 'Uso en Producción'), ('venta', 'Venta'), ('regalo', 'Regalo/Donación'), ('perdida', 'Pérdida'), ('robo', 'Robo'), ('vencimiento', 'Vencimiento'), ('dano', 'Daño'), ('conteo_fisico', 'Conteo Físico'), ('correccion_error', 'Corrección de Error'), ('transferencia_interna', 'Transferencia Interna'), ('prestamo', 'Préstamo'), ('otro', 'Otro')], max_length=25, verbose_name='Motivo'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='observaciones',
            field=models.TextField(blank=True, null=True, verbose_name='Observaciones'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='proveedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.proveedor', verbose_name='Proveedor'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='repuesto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='inventario.repuesto', verbose_name='Repuesto'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='tipo_movimiento',
            field=models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste_positivo', 'Ajuste Positivo'), ('ajuste_negativo', 'Ajuste Negativo'), ('transferencia_entrada', 'Transferencia Entrada'), ('transferencia_salida', 'Transferencia Salida'), ('devolucion', 'Devolución'), ('merma', 'Merma'), ('inventario_inicial', 'Inventario Inicial')], max_length=25, verbose_name='Tipo de Movimiento'),
        ),
        migrations.AlterField(
            model_name='movimientostock',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimientos_inventario', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Responsable'),
        ),
        migrations.AddIndex(
            model_name='movimientostock',
            index=models.Index(fields=['repuesto', 'tipo_movimiento'], name='inventario__repuest_714020_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientostock',
            index=models.Index(fields=['fecha_movimiento'], name='inventario__fecha_m_8591d3_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientostock',
            index=models.Index(fields=['usuario'], name='inventario__usuario_522127_idx'),
        ),
        migrations.AddIndex(
            model_name='movimientostock',
            index=models.Index(fields=['estado'], name='inventario__estado_c5ff8f_idx'),
        ),
    ]
