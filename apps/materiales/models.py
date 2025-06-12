from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal

class CategoriaMaterial(models.Model):
    """Categorías para clasificar materiales y herramientas"""
    
    TIPO_CATEGORIA_CHOICES = [
        # ✅ CATEGORÍAS PARA MATERIALES
        ('materiales_construccion', 'Materiales de Construcción'),
        ('materiales_soldadura', 'Materiales de Soldadura'),
        ('consumibles_laboratorio', 'Consumibles de Laboratorio'),
        ('quimicos_reactivos', 'Químicos y Reactivos'),
        ('lubricantes_fluidos', 'Lubricantes y Fluidos'),
        ('materiales_electricos', 'Materiales Eléctricos'),
        ('materiales_metalicos', 'Materiales Metálicos'),
        ('combustibles_gases', 'Combustibles y Gases'),
        ('pinturas_recubrimientos', 'Pinturas y Recubrimientos'),
        ('adhesivos_sellantes', 'Adhesivos y Sellantes'),
        ('abrasivos_pulimentos', 'Abrasivos y Pulimentos'),
        ('materiales_proteccion', 'Materiales de Protección'),
        
        # ✅ CATEGORÍAS ESPECÍFICAS PARA HERRAMIENTAS
        ('herramientas_manuales', 'Herramientas Manuales'),
        ('herramientas_electricas', 'Herramientas Eléctricas'),
        ('instrumentos_medicion', 'Instrumentos de Medición'),
        ('herramientas_precision', 'Herramientas de Precisión'),
        ('herramientas_corte', 'Herramientas de Corte'),
        ('equipos_laboratorio', 'Equipos de Laboratorio'),
        ('herramientas_soldadura_eq', 'Herramientas de Soldadura'),
        ('herramientas_neumaticas', 'Herramientas Neumáticas'),
        ('herramientas_hidraulicas', 'Herramientas Hidráulicas'),
        ('instrumentos_calibracion', 'Instrumentos de Calibración'),
        ('herramientas_seguridad', 'Herramientas de Seguridad'),
        ('herramientas_especiales', 'Herramientas Especializadas'),
    ]
    
    nombre = models.CharField("Nombre de Categoría", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    codigo = models.CharField("Código", max_length=10, unique=True)
    tipo_categoria = models.CharField("Tipo de Categoría", max_length=30, choices=TIPO_CATEGORIA_CHOICES, default='materiales_construccion')
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Categoría de Material"
        verbose_name_plural = "Categorías de Materiales"
        ordering = ['tipo_categoria', 'nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Material(models.Model):
    """Modelo principal para materiales y herramientas"""
    
    TIPO_CHOICES = [
        # ✅ TIPOS DE MATERIALES
        ('material_construccion', 'Material de Construcción'),
        ('material_soldadura', 'Material de Soldadura'),
        ('consumible_general', 'Consumible General'),
        ('quimico_laboratorio', 'Químico de Laboratorio'),
        ('lubricante', 'Lubricante'),
        ('adhesivo_sellante', 'Adhesivo/Sellante'),
        ('material_abrasivo', 'Material Abrasivo'),
        ('material_electrico', 'Material Eléctrico'),
        ('material_metalico', 'Material Metálico'),
        ('combustible', 'Combustible'),
        ('gas_industrial', 'Gas Industrial'),
        ('pintura_recubrimiento', 'Pintura/Recubrimiento'),
        
        # ✅ TIPOS ESPECÍFICOS DE HERRAMIENTAS
        ('herramienta_manual', 'Herramienta Manual'),
        ('herramienta_electrica', 'Herramienta Eléctrica'),
        ('herramienta_precision', 'Herramienta de Precisión'),
        ('herramienta_soldadura', 'Herramienta de Soldadura'),
        ('herramienta_corte', 'Herramienta de Corte'),
        ('herramienta_medicion', 'Herramienta de Medición'),
        ('herramienta_seguridad', 'Herramienta de Seguridad'),
        ('instrumento_laboratorio', 'Instrumento de Laboratorio'),
        ('herramienta_neumatica', 'Herramienta Neumática'),
        ('herramienta_hidraulica', 'Herramienta Hidráulica'),
        ('equipo_calibracion', 'Equipo de Calibración'),
        ('instrumento_medicion_digital', 'Instrumento de Medición Digital'),
        ('herramienta_especial', 'Herramienta Especializada'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('bajo_stock', 'Stock Bajo'),
        ('en_pedido', 'En Pedido'),
        ('descontinuado', 'Descontinuado'),
        ('en_uso', 'En Uso'),
        ('mantenimiento', 'En Mantenimiento'),
        ('calibracion', 'En Calibración'),
    ]
    
    CRITICIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('metro', 'Metro'),
        ('kilogramo', 'Kilogramo'),
        ('litro', 'Litro'),
        ('caja', 'Caja'),
        ('paquete', 'Paquete'),
        ('rollo', 'Rollo'),
        ('par', 'Par'),
        ('juego', 'Juego'),
        ('kit', 'Kit'),
        ('set', 'Set'),
        ('pieza', 'Pieza'),
    ]
    
    # Información básica
    codigo = models.CharField("Código Interno", max_length=30, unique=True)
    nombre = models.CharField("Nombre del Material/Herramienta", max_length=200)
    descripcion = models.TextField("Descripción Detallada")
    tipo = models.CharField("Tipo", max_length=30, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(CategoriaMaterial, on_delete=models.PROTECT, related_name='materiales')
    
    # Identificación
    marca = models.CharField("Marca", max_length=100, blank=True)
    modelo = models.CharField("Modelo", max_length=100, blank=True)
    numero_parte = models.CharField("Número de Parte", max_length=100, blank=True)
    codigo_barras = models.CharField("Código de Barras", max_length=50, blank=True)
    
    # Inventario
    stock_actual = models.DecimalField("Stock Actual", max_digits=10, decimal_places=2, default=Decimal('0'))
    stock_minimo = models.DecimalField("Stock Mínimo", max_digits=10, decimal_places=2, default=Decimal('1'))
    stock_maximo = models.DecimalField("Stock Máximo", max_digits=10, decimal_places=2, default=Decimal('100'))
    punto_reorden = models.DecimalField("Punto de Reorden", max_digits=10, decimal_places=2, default=Decimal('5'))
    unidad_medida = models.CharField("Unidad de Medida", max_length=20, choices=UNIDAD_MEDIDA_CHOICES, default='unidad')
    
    # Costos
    precio_unitario = models.DecimalField("Precio Unitario", max_digits=12, decimal_places=2, default=Decimal('0'))
    
    # Clasificación
    criticidad = models.CharField("Criticidad", max_length=10, choices=CRITICIDAD_CHOICES, default='media')
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default='disponible')
    
    # Ubicación física
    ubicacion = models.CharField("Ubicación en Almacén", max_length=200, blank=True, null=True)
    
    # Proveedor
    proveedor_principal = models.ForeignKey(
        'inventario.Proveedor',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='materiales_principales'
    )
    
    # Características especiales para materiales
    requiere_refrigeracion = models.BooleanField("Requiere Refrigeración", default=False)
    requiere_manejo_especial = models.BooleanField("Requiere Manejo Especial", default=False)
    
    # ✅ CAMPOS ESPECÍFICOS PARA HERRAMIENTAS (SIN VALIDACIONES ESTRICTAS)
    es_herramienta_critica = models.BooleanField("Herramienta Crítica", default=False)
    requiere_calibracion = models.BooleanField("Requiere Calibración", default=False)
    fecha_ultima_calibracion = models.DateField("Última Calibración", null=True, blank=True)
    frecuencia_calibracion = models.IntegerField("Frecuencia Calibración (días)", null=True, blank=True)
    
    # Mantenimiento (SIN VALIDACIONES OBLIGATORIAS)
    requiere_mantenimiento = models.BooleanField("Requiere Mantenimiento", default=False)
    fecha_ultimo_mantenimiento = models.DateField("Último Mantenimiento", null=True, blank=True)
    frecuencia_mantenimiento = models.IntegerField("Frecuencia Mantenimiento (días)", null=True, blank=True)
    
    # Fechas importantes
    fecha_vencimiento = models.DateField("Fecha de Vencimiento", null=True, blank=True)
    fecha_ultima_compra = models.DateField("Fecha Última Compra", null=True, blank=True)
    
    # Documentos
    foto = models.ImageField("Foto", upload_to='materiales/fotos/', blank=True, null=True)
    ficha_tecnica = models.FileField("Ficha Técnica", upload_to='materiales/fichas/', blank=True, null=True)
    
    # Control
    activo = models.BooleanField("Activo", default=True)
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Material/Herramienta"
        verbose_name_plural = "Materiales y Herramientas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_absolute_url(self):
        return reverse('materiales:material-detalle', kwargs={'pk': self.pk})
    
    def es_herramienta(self):
        """Determina si el item es una herramienta"""
        tipos_herramientas = [
            'herramienta_manual', 'herramienta_electrica', 'herramienta_precision',
            'herramienta_soldadura', 'herramienta_corte', 'herramienta_medicion',
            'herramienta_seguridad', 'instrumento_laboratorio', 'herramienta_neumatica',
            'herramienta_hidraulica', 'equipo_calibracion', 'instrumento_medicion_digital',
            'herramienta_especial'
        ]
        return self.tipo in tipos_herramientas
    
    def necesita_calibracion_check(self):
        """Verifica si necesita calibración (para herramientas)"""
        if not self.requiere_calibracion or not self.fecha_ultima_calibracion or not self.frecuencia_calibracion:
            return False
        
        proxima_calibracion = self.fecha_ultima_calibracion + timedelta(days=self.frecuencia_calibracion)
        return date.today() >= proxima_calibracion
    
    def save(self, *args, **kwargs):
        # Generar código automático si no existe
        if not self.codigo:
            if self.es_herramienta():
                prefijo = 'HERR'
            else:
                prefijo = 'MAT'
                
            ultimo_item = Material.objects.filter(
                codigo__startswith=prefijo
            ).order_by('codigo').last()
            
            if ultimo_item:
                try:
                    ultimo_numero = int(ultimo_item.codigo.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo = f"{prefijo}-{nuevo_numero:04d}"
        
        # Actualizar estado según stock
        self.actualizar_estado_stock()
        
        super().save(*args, **kwargs)
    
    def actualizar_estado_stock(self):
        """Actualiza el estado basado en el nivel de stock"""
        if self.stock_actual <= 0:
            self.estado = 'agotado'
        elif self.esta_vencido():
            self.estado = 'descontinuado'
        elif self.stock_actual <= self.stock_minimo:
            self.estado = 'bajo_stock'
        else:
            self.estado = 'disponible'
    
    def necesita_reposicion(self):
        """Verifica si necesita reposición"""
        return self.stock_actual <= self.punto_reorden
    
    def esta_vencido(self):
        """Verifica si está vencido"""
        if self.fecha_vencimiento:
            return date.today() > self.fecha_vencimiento
        return False
    
    def dias_hasta_vencimiento(self):
        """Calcula los días hasta vencimiento"""
        if self.fecha_vencimiento:
            diferencia = self.fecha_vencimiento - date.today()
            return diferencia.days
        return None
    
    def valor_stock_actual(self):
        """Calcula el valor total del stock actual"""
        return self.stock_actual * self.precio_unitario
    
    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'disponible': 'bg-success',
            'agotado': 'bg-danger',
            'bajo_stock': 'bg-warning',
            'en_pedido': 'bg-info',
            'descontinuado': 'bg-secondary',
            'en_uso': 'bg-primary',
            'mantenimiento': 'bg-warning',
            'calibracion': 'bg-info',
        }
        return clases.get(self.estado, 'bg-secondary')
    
    def get_criticidad_badge_class(self):
        """Retorna la clase CSS para el badge de criticidad"""
        clases = {
            'critica': 'bg-danger',
            'alta': 'bg-warning',
            'media': 'bg-info',
            'baja': 'bg-secondary',
        }
        return clases.get(self.criticidad, 'bg-secondary')

class MovimientoMaterial(models.Model):
    """Modelo para registrar movimientos de materiales"""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste_positivo', 'Ajuste Positivo'),
        ('ajuste_negativo', 'Ajuste Negativo'),
        ('transferencia', 'Transferencia'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma'),
    ]
    
    MOTIVO_CHOICES = [
        ('compra', 'Compra'),
        ('uso_proyecto', 'Uso en Proyecto'),
        ('mantenimiento', 'Mantenimiento'),
        ('calibracion', 'Calibración'),
        ('prestamo', 'Préstamo'),
        ('devolucion_cliente', 'Devolución de Cliente'),
        ('inventario_fisico', 'Inventario Físico'),
        ('daño', 'Daño'),
        ('vencimiento', 'Vencimiento'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Información básica
    numero_movimiento = models.CharField("Número de Movimiento", max_length=20, unique=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField("Tipo de Movimiento", max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    motivo = models.CharField("Motivo", max_length=20, choices=MOTIVO_CHOICES)
    
    # Cantidades
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField("Stock Anterior", max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField("Stock Nuevo", max_digits=10, decimal_places=2)
    
    # Costos
    costo_unitario = models.DecimalField("Costo Unitario", max_digits=12, decimal_places=2, default=0)
    costo_total = models.DecimalField("Costo Total", max_digits=15, decimal_places=2, default=0)
    
    # Responsables y fechas
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='movimientos_materiales')
    fecha_movimiento = models.DateTimeField("Fecha del Movimiento", default=timezone.now)
    
    # Documentos
    documento_referencia = models.CharField("Documento de Referencia", max_length=100, blank=True, null=True)
    observaciones = models.TextField("Observaciones", blank=True)
    
    # Control
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default='procesado')
    
    class Meta:
        verbose_name = "Movimiento de Material"
        verbose_name_plural = "Movimientos de Materiales"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.numero_movimiento} - {self.material.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar número automático si no existe
        if not self.numero_movimiento:
            ultimo_movimiento = MovimientoMaterial.objects.filter(
                numero_movimiento__startswith='MOV'
            ).order_by('numero_movimiento').last()
            
            if ultimo_movimiento:
                try:
                    ultimo_numero = int(ultimo_movimiento.numero_movimiento.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.numero_movimiento = f"MOV-{nuevo_numero:06d}"
        
        super().save(*args, **kwargs)