from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User

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
    """Modelo para gestión de proveedores de repuestos"""
    
    TIPO_PROVEEDOR_CHOICES = [
        ('nacional', 'Nacional'),
        ('internacional', 'Internacional'),
        ('local', 'Local'),
        ('distribuidor', 'Distribuidor'),
        ('fabricante', 'Fabricante'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('evaluacion', 'En Evaluación'),
        ('suspendido', 'Suspendido'),
        ('bloqueado', 'Bloqueado'),
    ]
    
    CATEGORIA_CHOICES = [
        ('repuestos_mecanicos', 'Repuestos Mecánicos'),
        ('componentes_electronicos', 'Componentes Electrónicos'),
        ('herramientas', 'Herramientas'),
        ('materiales_soldadura', 'Materiales de Soldadura'),
        ('lubricantes', 'Lubricantes y Aceites'),
        ('elementos_seguridad', 'Elementos de Seguridad'),
        ('consumibles', 'Consumibles Generales'),
        ('servicios_especializados', 'Servicios Especializados'),
    ]
    
    # Información básica
    codigo = models.CharField("Código de Proveedor", max_length=20, unique=True)
    nombre = models.CharField("Nombre/Razón Social", max_length=200)
    nombre_comercial = models.CharField("Nombre Comercial", max_length=200, blank=True)
    tipo_proveedor = models.CharField("Tipo de Proveedor", max_length=20, choices=TIPO_PROVEEDOR_CHOICES)
    categoria = models.CharField("Categoría Principal", max_length=30, choices=CATEGORIA_CHOICES)
    
    # Información legal
    nit = models.CharField("NIT", max_length=20, blank=True)
    registro_comercio = models.CharField("Registro de Comercio", max_length=50, blank=True)
    licencia_funcionamiento = models.CharField("Licencia de Funcionamiento", max_length=50, blank=True)
    
    # Contacto principal
    contacto_principal = models.CharField("Contacto Principal", max_length=100)
    cargo_contacto = models.CharField("Cargo", max_length=100, blank=True)
    telefono = models.CharField("Teléfono", max_length=20)
    telefono_secundario = models.CharField("Teléfono Secundario", max_length=20, blank=True)
    email = models.EmailField("Email Principal")
    email_secundario = models.EmailField("Email Secundario", blank=True)
    sitio_web = models.URLField("Sitio Web", blank=True)
    
    # Dirección
    direccion = models.TextField("Dirección")
    ciudad = models.CharField("Ciudad", max_length=100)
    departamento = models.CharField("Departamento", max_length=100)
    pais = models.CharField("País", max_length=100, default="Bolivia")
    codigo_postal = models.CharField("Código Postal", max_length=10, blank=True)
    
    # Información comercial
    condiciones_pago = models.CharField("Condiciones de Pago", max_length=100, blank=True)
    dias_credito = models.PositiveIntegerField("Días de Crédito", default=0)
    descuento_general = models.DecimalField("Descuento General (%)", max_digits=5, decimal_places=2, default=0)
    moneda_principal = models.CharField("Moneda Principal", max_length=20, default="BOB")
    limite_credito = models.DecimalField("Límite de Crédito", max_digits=12, decimal_places=2, default=0)
    
    # Evaluación y calificación
    calificacion = models.DecimalField("Calificación (1-5)", max_digits=3, decimal_places=2, default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(5)])
    tiempo_entrega_promedio = models.PositiveIntegerField("Tiempo Entrega Promedio (días)", default=15)
    certificaciones = models.TextField("Certificaciones", blank=True,
                                     help_text="ISO, API, ASME, etc.")
    
    # Estado y seguimiento
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default='evaluacion')
    fecha_registro = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    fecha_ultima_compra = models.DateField("Última Compra", null=True, blank=True)
    fecha_ultima_evaluacion = models.DateField("Última Evaluación", null=True, blank=True)
    
    # Métricas comerciales
    total_ordenes = models.PositiveIntegerField("Total de Órdenes", default=0)
    total_comprado = models.DecimalField("Total Comprado", max_digits=15, decimal_places=2, default=0)
    porcentaje_cumplimiento = models.DecimalField("% Cumplimiento", max_digits=5, decimal_places=2, default=0)
    
    # Observaciones y notas
    observaciones = models.TextField("Observaciones", blank=True)
    notas_internas = models.TextField("Notas Internas", blank=True)
    
    # Control
    activo = models.BooleanField("Activo", default=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        # Generar código automático si no existe
        if not self.codigo:
            ultimo_proveedor = Proveedor.objects.filter(
                codigo__startswith='PROV'
            ).order_by('codigo').last()
            
            if ultimo_proveedor:
                try:
                    ultimo_numero = int(ultimo_proveedor.codigo.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo = f"PROV-{nuevo_numero:04d}"
        
        super().save(*args, **kwargs)

    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'activo': 'bg-success',
            'inactivo': 'bg-secondary',
            'evaluacion': 'bg-warning',
            'suspendido': 'bg-danger',
            'bloqueado': 'bg-dark',
        }
        return clases.get(self.estado, 'bg-secondary')

    def get_calificacion_estrellas(self):
        """Retorna el número de estrellas basado en la calificación"""
        return int(self.calificacion) if self.calificacion else 0

    def get_tiempo_entrega_categoria(self):
        """Categoriza el tiempo de entrega"""
        if self.tiempo_entrega_promedio <= 5:
            return {'texto': 'Rápido', 'color': 'bg-success'}
        elif self.tiempo_entrega_promedio <= 10:
            return {'texto': 'Normal', 'color': 'bg-info'}
        elif self.tiempo_entrega_promedio <= 20:
            return {'texto': 'Lento', 'color': 'bg-warning'}
        else:
            return {'texto': 'Muy Lento', 'color': 'bg-danger'}

    def dias_sin_comprar(self):
        """Calcula los días sin realizar compras"""
        if self.fecha_ultima_compra:
            return (date.today() - self.fecha_ultima_compra).days
        return None

    def get_calificacion_display(self):
        """Retorna la calificación en formato de estrellas"""
        if self.calificacion:
            return "★" * int(self.calificacion) + "☆" * (5 - int(self.calificacion))
        return "Sin calificar"

    def get_estado_color(self):
        """Retorna el color del estado para mostrar en el frontend"""
        colores = {
            'activo': '#28a745',      # Verde
            'inactivo': '#6c757d',    # Gris
            'evaluacion': '#ffc107',  # Amarillo
            'suspendido': '#dc3545',  # Rojo
            'bloqueado': '#343a40',   # Negro
        }
        return colores.get(self.estado, '#6c757d')

    def es_proveedor_confiable(self):
        """Determina si es un proveedor confiable basado en métricas"""
        criterios_cumplidos = 0
        
        # Calificación >= 4.0
        if self.calificacion >= 4.0:
            criterios_cumplidos += 1
        
        # Cumplimiento >= 90%
        if self.porcentaje_cumplimiento >= 90:
            criterios_cumplidos += 1
        
        # Tiempo de entrega <= 15 días
        if self.tiempo_entrega_promedio <= 15:
            criterios_cumplidos += 1
        
        # Al menos 5 órdenes completadas
        if self.total_ordenes >= 5:
            criterios_cumplidos += 1
        
        # Estado activo
        if self.estado == 'activo':
            criterios_cumplidos += 1
        
        # Debe cumplir al menos 4 de 5 criterios
        return criterios_cumplidos >= 4

    def necesita_evaluacion(self):
        """Verifica si el proveedor necesita ser evaluado"""
        if not self.fecha_ultima_evaluacion:
            return True
        
        # Evaluación cada 6 meses
        fecha_limite = self.fecha_ultima_evaluacion + timedelta(days=180)
        return date.today() > fecha_limite

    def get_resumen_comercial(self):
        """Retorna un resumen de la relación comercial"""
        return {
            'total_comprado': self.total_comprado,
            'promedio_por_orden': self.total_comprado / max(self.total_ordenes, 1),
            'dias_sin_comprar': self.dias_sin_comprar(),
            'es_confiable': self.es_proveedor_confiable(),
            'necesita_evaluacion': self.necesita_evaluacion(),
        }

    def actualizar_metricas(self):
        """Actualiza las métricas comerciales del proveedor"""
        # Este método se puede llamar cuando se complete una orden
        # Por ahora solo actualiza la fecha de última evaluación
        self.fecha_ultima_evaluacion = date.today()
        self.save()

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
                try:
                    ultimo_numero = int(ultimo_repuesto.codigo.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except (ValueError, IndexError):
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo = f"REP-{nuevo_numero:05d}"
        
        # Actualizar estado basado en stock
        self.actualizar_estado_stock()
        
        super().save(*args, **kwargs)
    
    def actualizar_estado_stock(self):
        """Actualiza el estado basado en el nivel de stock"""
        if self.stock_actual <= 0:
            self.estado = 'agotado'
        elif self.esta_vencido():
            self.estado = 'por_vencer'
        elif self.stock_actual <= self.punto_reorden:
            self.estado = 'disponible'  # Pero necesita reposición
        else:
            self.estado = 'disponible'
    
    def necesita_reposicion(self):
        """Verifica si el repuesto necesita reposición"""
        return self.stock_actual <= self.punto_reorden
    
    def es_stock_critico(self):
        """Verifica si está en nivel crítico"""
        return self.stock_actual <= self.stock_minimo
    
    def dias_hasta_vencimiento(self):
        """Calcula los días hasta vencimiento"""
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
        """Calcula el valor total del stock actual"""
        return self.stock_actual * self.precio_unitario
    
    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
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
        """Retorna la clase CSS para el badge de criticidad"""
        clases = {
            'CRITICA': 'bg-danger',
            'IMPORTANTE': 'bg-warning',
            'MODERADA': 'bg-info',
            'BAJA': 'bg-secondary',
        }
        return clases.get(self.criticidad, 'bg-secondary')
    
    def get_seccion_display_completo(self):
        """Retorna el nombre completo de la sección"""
        secciones = {
            'S1': 'S1 - Soldadura, Corte y Perforación',
            'S2': 'S2 - Maquinado y Mecanizado',
            'S3': 'S3 - Prototipado',
            'S4': 'S4 - Plásticos',
            'S5': 'S5 - Fundición',
            'S6': 'S6 - Sujeción y Doblado',
            'S7': 'S7 - Transporte y Elevación',
            'A9': 'A9 - Tecnología de la Información',
            'ALM': 'Almacén General',
            'MAN': 'Mantenimiento',
            'CAL': 'Control de Calidad',
            'SEG': 'Seguridad Industrial',
        }
        return secciones.get(self.seccion_trabajo, self.seccion_trabajo)

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ['-fecha_creacion']

class MovimientoStock(models.Model):
    """Modelo para registrar movimientos de stock de repuestos"""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste_positivo', 'Ajuste Positivo'),
        ('ajuste_negativo', 'Ajuste Negativo'),
        ('transferencia_entrada', 'Transferencia Entrada'),
        ('transferencia_salida', 'Transferencia Salida'),
        ('devolucion', 'Devolución'),
        ('merma', 'Merma'),
        ('inventario_inicial', 'Inventario Inicial'),
    ]
    
    MOTIVO_CHOICES = [
        ('compra', 'Compra'),
        ('produccion', 'Producción'),
        ('devolucion_proveedor', 'Devolución a Proveedor'),
        ('devolucion_cliente', 'Devolución de Cliente'),
        ('uso_mantenimiento', 'Uso en Mantenimiento'),
        ('uso_produccion', 'Uso en Producción'),
        ('venta', 'Venta'),
        ('regalo', 'Regalo/Donación'),
        ('perdida', 'Pérdida'),
        ('robo', 'Robo'),
        ('vencimiento', 'Vencimiento'),
        ('dano', 'Daño'),
        ('conteo_fisico', 'Conteo Físico'),
        ('correccion_error', 'Corrección de Error'),
        ('transferencia_interna', 'Transferencia Interna'),
        ('prestamo', 'Préstamo'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
        ('cancelado', 'Cancelado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Información básica
    numero_movimiento = models.CharField("Número de Movimiento", max_length=20, unique=True)
    repuesto = models.ForeignKey(
        Repuesto, 
        on_delete=models.CASCADE, 
        related_name='movimientos',
        verbose_name="Repuesto"
    )
    
    # Tipo y motivo del movimiento
    tipo_movimiento = models.CharField("Tipo de Movimiento", max_length=25, choices=TIPO_MOVIMIENTO_CHOICES)
    motivo = models.CharField("Motivo", max_length=25, choices=MOTIVO_CHOICES)
    motivo_detalle = models.TextField("Detalle del Motivo", blank=True, null=True)
    
    # Cantidades
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField("Stock Anterior", max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField("Stock Nuevo", max_digits=10, decimal_places=2)
    
    # Costos
    costo_unitario = models.DecimalField("Costo Unitario", max_digits=12, decimal_places=2, default=0)
    costo_total = models.DecimalField("Costo Total", max_digits=15, decimal_places=2, default=0)
    
    # Responsables y fechas
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='movimientos_inventario',
        verbose_name="Usuario Responsable"
    )
    fecha_movimiento = models.DateTimeField("Fecha del Movimiento", default=timezone.now)
    fecha_procesamiento = models.DateTimeField("Fecha de Procesamiento", null=True, blank=True)
    
    # Documentos relacionados
    documento_referencia = models.CharField("Documento de Referencia", max_length=100, blank=True, null=True)
    numero_factura = models.CharField("Número de Factura", max_length=50, blank=True, null=True)
    numero_orden = models.CharField("Número de Orden", max_length=50, blank=True, null=True)
    
    # Ubicaciones y referencias adicionales
    ubicacion_origen = models.CharField("Ubicación Origen", max_length=100, blank=True, null=True)
    ubicacion_destino = models.CharField("Ubicación Destino", max_length=100, blank=True, null=True)
    
    # Proveedor (para entradas)
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor",
        help_text="Proveedor para movimientos de entrada"
    )
    
    # Estado y control
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_CHOICES, default='procesado')
    
    # Metadatos
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_movimiento']

    def __str__(self):
        return f"{self.numero_movimiento} - {self.repuesto.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular costo total
        self.costo_total = self.cantidad * self.costo_unitario
        
        super().save(*args, **kwargs)
    
    def get_tipo_display_color(self):
        """Retorna el color para el tipo de movimiento"""
        colores = {
            'entrada': 'success',
            'salida': 'danger',
            'ajuste_positivo': 'info',
            'ajuste_negativo': 'warning',
            'transferencia_entrada': 'primary',
            'transferencia_salida': 'primary',
            'devolucion': 'secondary',
            'merma': 'danger',
            'inventario_inicial': 'dark',
        }
        return colores.get(self.tipo_movimiento, 'secondary')
    
    def get_estado_display_color(self):
        """Retorna el color para el estado"""
        colores = {
            'pendiente': 'warning',
            'procesado': 'success',
            'cancelado': 'secondary',
            'rechazado': 'danger',
        }
        return colores.get(self.estado, 'secondary')
    
    def is_entrada(self):
        """Verifica si es un movimiento de entrada"""
        tipos_entrada = ['entrada', 'ajuste_positivo', 'transferencia_entrada', 'devolucion']
        return self.tipo_movimiento in tipos_entrada
    
    def is_salida(self):
        """Verifica si es un movimiento de salida"""
        tipos_salida = ['salida', 'ajuste_negativo', 'transferencia_salida', 'merma']
        return self.tipo_movimiento in tipos_salida
    
    def get_impacto_stock(self):
        """Retorna el impacto en el stock (+, - o =)"""
        if self.is_entrada():
            return f"+{self.cantidad}"
        elif self.is_salida():
            return f"-{self.cantidad}"
        else:
            return f"±{self.cantidad}"