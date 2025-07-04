# Generated by Django 4.2.20 on 2025-06-11 03:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('equipos', '0005_equipo_amperaje_equipo_caudal_aire_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaRepuesto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre de Categoría')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('codigo', models.CharField(max_length=10, unique=True, verbose_name='Código')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Categoría de Repuesto',
                'verbose_name_plural': 'Categorías de Repuestos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre del Proveedor')),
                ('codigo', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('contacto_principal', models.CharField(blank=True, max_length=100, verbose_name='Contacto Principal')),
                ('telefono', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('direccion', models.TextField(blank=True, verbose_name='Dirección')),
                ('ciudad', models.CharField(blank=True, max_length=100, verbose_name='Ciudad')),
                ('pais', models.CharField(default='Bolivia', max_length=100, verbose_name='País')),
                ('nit', models.CharField(blank=True, max_length=20, verbose_name='NIT')),
                ('calificacion', models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Calificación (1-5)')),
                ('tiempo_entrega_promedio', models.IntegerField(default=30, verbose_name='Tiempo Entrega Promedio (días)')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Repuesto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True, verbose_name='Código Interno')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre del Repuesto')),
                ('descripcion', models.TextField(verbose_name='Descripción Detallada')),
                ('codigo_fabricante', models.CharField(blank=True, max_length=100, verbose_name='Código del Fabricante')),
                ('codigo_proveedor', models.CharField(blank=True, max_length=100, verbose_name='Código del Proveedor')),
                ('numero_parte', models.CharField(blank=True, max_length=100, verbose_name='Número de Parte')),
                ('fabricante', models.CharField(blank=True, max_length=100, verbose_name='Fabricante')),
                ('modelo', models.CharField(blank=True, max_length=100, verbose_name='Modelo')),
                ('especificaciones', models.TextField(blank=True, verbose_name='Especificaciones Técnicas')),
                ('stock_actual', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Stock Actual')),
                ('stock_minimo', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Stock Mínimo')),
                ('stock_maximo', models.DecimalField(decimal_places=2, default=100, max_digits=10, verbose_name='Stock Máximo')),
                ('punto_reorden', models.DecimalField(decimal_places=2, default=5, max_digits=10, verbose_name='Punto de Reorden')),
                ('unidad_medida', models.CharField(choices=[('unidad', 'Unidad'), ('metro', 'Metro'), ('kilogramo', 'Kilogramo'), ('litro', 'Litro'), ('caja', 'Caja'), ('rollo', 'Rollo'), ('paquete', 'Paquete'), ('galón', 'Galón'), ('par', 'Par'), ('juego', 'Juego')], default='unidad', max_length=20, verbose_name='Unidad de Medida')),
                ('ubicacion_almacen', models.CharField(blank=True, max_length=100, verbose_name='Ubicación en Almacén')),
                ('pasillo', models.CharField(blank=True, max_length=10, verbose_name='Pasillo')),
                ('estante', models.CharField(blank=True, max_length=10, verbose_name='Estante')),
                ('nivel', models.CharField(blank=True, max_length=10, verbose_name='Nivel')),
                ('precio_unitario', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Precio Unitario')),
                ('precio_promedio', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Precio Promedio')),
                ('costo_ultima_compra', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Costo Última Compra')),
                ('tiempo_entrega', models.IntegerField(default=30, verbose_name='Tiempo de Entrega (días)')),
                ('criticidad', models.CharField(choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('critica', 'Crítica')], default='media', max_length=10, verbose_name='Criticidad')),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('agotado', 'Agotado'), ('por_vencer', 'Por Vencer'), ('descontinuado', 'Descontinuado'), ('en_pedido', 'En Pedido')], default='disponible', max_length=15, verbose_name='Estado')),
                ('es_consumible', models.BooleanField(default=True, verbose_name='Es Consumible')),
                ('requiere_refrigeracion', models.BooleanField(default=False, verbose_name='Requiere Refrigeración')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('fecha_ultima_compra', models.DateField(blank=True, null=True, verbose_name='Fecha Última Compra')),
                ('fecha_ultimo_uso', models.DateField(blank=True, null=True, verbose_name='Fecha Último Uso')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='repuestos/fotos/', verbose_name='Foto del Repuesto')),
                ('ficha_tecnica', models.FileField(blank=True, null=True, upload_to='repuestos/fichas/', verbose_name='Ficha Técnica')),
                ('certificado_calidad', models.FileField(blank=True, null=True, upload_to='repuestos/certificados/', verbose_name='Certificado de Calidad')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='repuestos', to='inventario.categoriarepuesto')),
                ('creado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repuestos_creados', to=settings.AUTH_USER_MODEL)),
                ('equipos_compatibles', models.ManyToManyField(blank=True, related_name='repuestos_compatibles', to='equipos.equipo')),
                ('proveedor_principal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repuestos_principales', to='inventario.proveedor')),
                ('proveedores_alternativos', models.ManyToManyField(blank=True, related_name='repuestos_alternativos', to='inventario.proveedor')),
            ],
            options={
                'verbose_name': 'Repuesto',
                'verbose_name_plural': 'Repuestos',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='MovimientoStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_movimiento', models.CharField(choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste'), ('devolucion', 'Devolución'), ('transferencia', 'Transferencia'), ('perdida', 'Pérdida')], max_length=15, verbose_name='Tipo de Movimiento')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Cantidad')),
                ('stock_anterior', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Stock Anterior')),
                ('stock_nuevo', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Stock Nuevo')),
                ('motivo', models.CharField(max_length=200, verbose_name='Motivo')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('fecha_movimiento', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha del Movimiento')),
                ('orden_trabajo', models.CharField(blank=True, max_length=50, verbose_name='Orden de Trabajo')),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.proveedor')),
                ('repuesto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='inventario.repuesto')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Movimiento de Stock',
                'verbose_name_plural': 'Movimientos de Stock',
                'ordering': ['-fecha_movimiento'],
            },
        ),
    ]
