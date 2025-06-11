from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo
from datetime import date, timedelta
from django.utils import timezone

class CategoriaRepuesto(models.Model):
    """Categorías para clasificar repuestos según el laboratorio industrial"""
    
    TIPO_CATEGORIA_CHOICES = [
        ('equipos', 'Equipos'),
        ('repuestos', 'Repuestos'),
        ('consumibles', 'Consumibles'),
        ('herramientas', 'Herramientas'),
        ('epp', 'EPP'),
        ('lubricantes', 'Lubricantes y Fluidos'),
    ]
    
    nombre = models.CharField("Nombre de Categoría", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    codigo = models.CharField("Código", max_length=10, unique=True)
    tipo_categoria = models.CharField("Tipo de Categoría", max_length=15, choices=TIPO_CATEGORIA_CHOICES, default='repuestos')
    seccion_aplicable = models.CharField("Sección Aplicable", max_length=50, blank=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Categoría de Repuesto"
        verbose_name_plural = "Categorías de Repuestos"
        ordering = ['tipo_categoria', 'nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Proveedor(models.Model):
    """Proveedores de repuestos"""
    nombre = models.CharField("Nombre del Proveedor", max_length=200)
    codigo = models.CharField("Código", max_length=20, unique=True)
    contacto_principal = models.CharField("Contacto Principal", max_length=100, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    direccion = models.TextField("Dirección", blank=True)
    ciudad = models.CharField("Ciudad", max_length=100, blank=True)
    pais = models.CharField("País", max_length=100, default="Bolivia")
    nit = models.CharField("NIT", max_length=20, blank=True)
    calificacion = models.IntegerField(
        "Calificación (1-5)", 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )
    tiempo_entrega_promedio = models.IntegerField("Tiempo Entrega Promedio (días)", default=30)
    es_proveedor_critico = models.BooleanField("Proveedor Crítico", default=False)
    certificaciones = models.TextField("Certificaciones", blank=True, help_text="ISO, API, ASME, etc.")
    activo = models.BooleanField("Activo", default=True)
    fecha_registro = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Repuesto(models.Model):
    """Modelo principal para repuestos e insumos industriales"""
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('por_vencer', 'Por Vencer'),
        ('descontinuado', 'Descontinuado'),
        ('en_pedido', 'En Pedido'),
        ('en_transito', 'En Tránsito'),
        ('retenido_calidad', 'Retenido por Calidad'),
    ]
    
    CRITICIDAD_CHOICES = [
        ('CRITICA', 'Crítica - Parada de producción'),
        ('IMPORTANTE', 'Importante - Afecta calidad'),
        ('MODERADA', 'Moderada - Afecta eficiencia'),
        ('BAJA', 'Baja - Sin impacto operacional'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('metro', 'Metro'),
        ('kilogramo', 'Kilogramo'),
        ('litro', 'Litro'),
        ('caja', 'Caja'),
        ('rollo', 'Rollo'),
        ('paquete', 'Paquete'),
        ('galón', 'Galón'),
        ('par', 'Par'),
        ('juego', 'Juego'),
        ('metros_lineales', 'Metros Lineales'),
        ('metros_cuadrados', 'Metros Cuadrados'),
        ('gramo', 'Gramo'),
        ('onza', 'Onza'),
        ('barra', 'Barra'),
        ('plancha', 'Plancha'),
        ('tubo', 'Tubo'),
    ]
    
    SECCION_TRABAJO_CHOICES = [
        ('S1', 'S1 - Soldadura, Corte y Perforación'),
        ('S2', 'S2 - Maquinado y Mecanizado'),
        ('S3', 'S3 - Prototipado'),
        ('S4', 'S4 - Plásticos'),
        ('S5', 'S5 - Fundición'),
        ('S6', 'S6 - Sujeción y Doblado'),
        ('S7', 'S7 - Transporte y Elevación'),
        ('A9', 'A9 - Tecnología de la Información'),
        ('ALM', 'Almacén General'),
        ('MAN', 'Mantenimiento'),
        ('CAL', 'Control de Calidad'),
        ('SEG', 'Seguridad Industrial'),
    ]
    
    # Información básica
    codigo = models.CharField("Código Interno", max_length=30, unique=True)
    codigo_activo_iso = models.CharField("Código de Activo ISO 14224", max_length=50, blank=True, 
                                       help_text="Código según norma ISO 14224 para activos industriales")
    nombre = models.CharField("Nombre del Repuesto", max_length=200)
    descripcion = models.TextField("Descripción Detallada")
    categoria = models.ForeignKey(CategoriaRepuesto, on_delete=models.PROTECT, related_name='repuestos')
    
    # Códigos de identificación
    codigo_fabricante = models.CharField("Código del Fabricante", max_length=100, blank=True)
    codigo_proveedor = models.CharField("Código del Proveedor", max_length=100, blank=True)
    numero_parte = models.CharField("Número de Parte", max_length=100, blank=True)
    codigo_barras = models.CharField("Código de Barras", max_length=50, blank=True)
    codigo_qr = models.CharField("Código QR", max_length=100, blank=True)
    
    # Información técnica
    fabricante = models.CharField("Fabricante", max_length=100, blank=True)
    modelo = models.CharField("Modelo", max_length=100, blank=True)
    especificaciones = models.TextField("Especificaciones Técnicas", blank=True)
    material_construccion = models.CharField("Material de Construcción", max_length=100, blank=True)
    dimensiones = models.CharField("Dimensiones", max_length=200, blank=True)
    peso_unitario = models.DecimalField("Peso Unitario (kg)", max_digits=8, decimal_places=3, blank=True, null=True)
    
    # Inventario
    stock_actual = models.DecimalField("Stock Actual", max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField("Stock Mínimo", max_digits=10, decimal_places=2, default=1)
    stock_maximo = models.DecimalField("Stock Máximo", max_digits=10, decimal_places=2, default=100)
    punto_reorden = models.DecimalField("Punto de Reorden", max_digits=10, decimal_places=2, default=5)
    stock_seguridad = models.DecimalField("Stock de Seguridad", max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField("Unidad de Medida", max_length=20, choices=UNIDAD_MEDIDA_CHOICES, default='unidad')
    
    # Ubicación física mejorada
    ubicacion_almacen = models.CharField("Ubicación en Almacén", max_length=100, blank=True)
    seccion_trabajo = models.CharField("Sección/Área de Trabajo", max_length=5, choices=SECCION_TRABAJO_CHOICES, blank=True)
    pasillo = models.CharField("Pasillo", max_length=10, blank=True)
    estante = models.CharField("Estante", max_length=10, blank=True)
    nivel = models.CharField("Nivel", max_length=10, blank=True)
    bin_location = models.CharField("Ubicación Bin", max_length=20, blank=True, help_text="Ubicación específica tipo bin")
    
    # Costos mejorados
    precio_unitario = models.DecimalField("Precio Unitario", max_digits=12, decimal_places=2, default=0)
    precio_promedio = models.DecimalField("Precio Promedio", max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    costo_ultima_compra = models.DecimalField("Costo Última Compra", max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    costo_almacenamiento = models.DecimalField("Costo de Almacenamiento Anual", max_digits=10, decimal_places=2, default=0)
    
    # Gestión de proveedores
    proveedor_principal = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='repuestos_principales')
    proveedores_alternativos = models.ManyToManyField(Proveedor, blank=True, related_name='repuestos_alternativos')
    tiempo_entrega = models.IntegerField("Tiempo de Entrega (días)", default=30)
    
    # Clasificación industrial
    criticidad = models.CharField("Criticidad Operacional", max_length=15, choices=CRITICIDAD_CHOICES, default='MODERADA')
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default='disponible')
    es_consumible = models.BooleanField("Es Consumible", default=True)
    es_activo_critico = models.BooleanField("Activo Crítico", default=False)
    requiere_refrigeracion = models.BooleanField("Requiere Refrigeración", default=False)
    requiere_manejo_especial = models.BooleanField("Requiere Manejo Especial", default=False)
    
    # Responsables técnicos
    responsable_tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='repuestos_responsable_tecnico',
                                          help_text="Responsable técnico del repuesto")
    responsable_almacen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='repuestos_responsable_almacen',
                                          help_text="Responsable de almacén")
    
    # Equipos compatibles y aplicación
    equipos_compatibles = models.ManyToManyField(Equipo, blank=True, related_name='repuestos_compatibles')
    aplicacion_principal = models.TextField("Aplicación Principal", blank=True, 
                                          help_text="Descripción de la aplicación principal del repuesto")
    
    # Fechas importantes
    fecha_vencimiento = models.DateField("Fecha de Vencimiento", null=True, blank=True)
    fecha_ultima_compra = models.DateField("Fecha Última Compra", null=True, blank=True)
    fecha_ultimo_uso = models.DateField("Fecha Último Uso", null=True, blank=True)
    fecha_ultimo_inventario = models.DateField("Fecha Último Inventario", null=True, blank=True)
    
    # Normas y certificaciones
    normas_aplicables = models.CharField("Normas Aplicables", max_length=200, blank=True,
                                       help_text="ISO, ASTM, ASME, AWS, etc.")
    certificaciones_requeridas = models.TextField("Certificaciones Requeridas", blank=True)
    
    # Documentos
    foto = models.ImageField("Foto del Repuesto", upload_to='repuestos/fotos/', blank=True, null=True)
    ficha_tecnica = models.FileField("Ficha Técnica", upload_to='repuestos/fichas/', blank=True, null=True)
    certificado_calidad = models.FileField("Certificado de Calidad", upload_to='repuestos/certificados/', blank=True, null=True)
    msds = models.FileField("Hoja de Datos de Seguridad (MSDS)", upload_to='repuestos/msds/', blank=True, null=True)
    
    # Mantenimiento y vida útil
    vida_util_estimada = models.IntegerField("Vida Útil Estimada (días)", null=True, blank=True)
    frecuencia_uso = models.CharField("Frecuencia de Uso", max_length=50, blank=True)
    condiciones_almacenamiento = models.TextField("Condiciones de Almacenamiento", blank=True)
    
    # Metadatos
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='repuestos_creados')
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    observaciones = models.TextField("Observaciones", blank=True)
    notas_tecnicas = models.TextField("Notas Técnicas", blank=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['codigo_activo_iso']),
            models.Index(fields=['seccion_trabajo', 'criticidad']),
            models.Index(fields=['categoria', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_absolute_url(self):
        return reverse('inventario:repuesto-detalle', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Generar código automático si no existe
        if not self.codigo:
            ultimo_repuesto = Repuesto.objects.filter(
                codigo__startswith='REP'
            ).order_by('codigo').last()
            
            if ultimo_repuesto:
                ultimo_numero = int(ultimo_repuesto.codigo[3:])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            self.codigo = f"REP{nuevo_numero:05d}"
        
        # Generar código de activo ISO si no existe y es crítico
        if not self.codigo_activo_iso and self.es_activo_critico:
            seccion_code = self.seccion_trabajo or 'GEN'
            categoria_code = self.categoria.codigo if self.categoria else 'REP'
            self.codigo_activo_iso = f"{seccion_code}-{categoria_code}-{self.codigo}"
        
        # Actualizar estado según stock
        self.actualizar_estado_stock()
        
        super().save(*args, **kwargs)
    
    def actualizar_estado_stock(self):
        """Actualiza el estado basado en el stock actual"""
        if self.stock_actual <= 0:
            self.estado = 'agotado'
        elif self.stock_actual <= self.punto_reorden:
            self.estado = 'en_pedido'
        elif self.fecha_vencimiento and self.fecha_vencimiento <= date.today() + timedelta(days=30):
            self.estado = 'por_vencer'
        else:
            self.estado = 'disponible'
    
    def necesita_reposicion(self):
        """Verifica si necesita reposición"""
        return self.stock_actual <= self.punto_reorden
    
    def es_stock_critico(self):
        """Verifica si está en stock crítico"""
        return self.stock_actual <= self.stock_minimo
    
    def dias_hasta_vencimiento(self):
        """Calcula días hasta vencimiento"""
        if self.fecha_vencimiento:
            diferencia = self.fecha_vencimiento - date.today()
            return diferencia.days
        return None
    
    def esta_vencido(self):
        """Verifica si está vencido"""
        if self.fecha_vencimiento:
            return date.today() > self.fecha_vencimiento
        return False
    
    def valor_stock_actual(self):
        """Calcula el valor del stock actual"""
        return self.stock_actual * self.precio_unitario
    
    def get_estado_badge_class(self):
        """Retorna clase CSS para el badge de estado"""
        clases = {
            'disponible': 'bg-success',
            'agotado': 'bg-danger',
            'por_vencer': 'bg-warning',
            'descontinuado': 'bg-secondary',
            'en_pedido': 'bg-info',
            'en_transito': 'bg-primary',
            'retenido_calidad': 'bg-warning',
        }
        return clases.get(self.estado, 'bg-secondary')
    
    def get_criticidad_badge_class(self):
        """Retorna clase CSS para el badge de criticidad"""
        clases = {
            'BAJA': 'bg-light text-dark',
            'MODERADA': 'bg-info',
            'IMPORTANTE': 'bg-warning',
            'CRITICA': 'bg-danger',
        }
        return clases.get(self.criticidad, 'bg-secondary')
    
    def get_seccion_display_completo(self):
        """Retorna el display completo de la sección"""
        return dict(self.SECCION_TRABAJO_CHOICES).get(self.seccion_trabajo, 'No asignado')

class MovimientoStock(models.Model):
    """Registro de movimientos de stock"""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
        ('transferencia', 'Transferencia'),
        ('perdida', 'Pérdida'),
        ('inventario', 'Ajuste por Inventario'),
        ('merma', 'Merma'),
        ('rechazo_calidad', 'Rechazo por Calidad'),
    ]
    
    repuesto = models.ForeignKey(Repuesto, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField("Tipo de Movimiento", max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField("Stock Anterior", max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField("Stock Nuevo", max_digits=10, decimal_places=2)
    
    motivo = models.CharField("Motivo", max_length=200)
    observaciones = models.TextField("Observaciones", blank=True)
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_movimiento = models.DateTimeField("Fecha del Movimiento", default=timezone.now)
    
    # Referencias externas
    orden_trabajo = models.CharField("Orden de Trabajo", max_length=50, blank=True)
    numero_lote = models.CharField("Número de Lote", max_length=50, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información adicional
    costo_unitario = models.DecimalField("Costo Unitario del Movimiento", max_digits=12, decimal_places=2, blank=True, null=True)
    responsable_movimiento = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='movimientos_responsable')
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.repuesto.codigo} - {self.tipo_movimiento} - {self.cantidad}"