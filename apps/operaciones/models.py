from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo
from datetime import date, timedelta
from django.utils import timezone  # <- AGREGAR ESTA LÍNEA

class ProcedimientoOperativo(models.Model):
    AREA_CHOICES = [
        ('soldadura', 'Soldadura'),
        ('maquinado', 'Maquinado'),
        ('fundicion', 'Fundición'),
        ('calidad', 'Control de Calidad'),
        ('seguridad', 'Seguridad Industrial'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pendiente_aprobacion', 'Pendiente Aprobación'),
        ('en_capacitacion', 'En Capacitación'),
        ('validado_campo', 'Validado en Campo'),
        ('vencido', 'Vencido'),
        ('obsoleto', 'Obsoleto'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    TIPO_CHOICES = [
        ('operativo', 'Operativo'),
        ('seguridad', 'Seguridad'),
        ('calidad', 'Calidad'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    NORMATIVAS_CHOICES = [
        ('ISO 9001', 'ISO 9001 - Sistema de Gestión de Calidad'),
        ('ISO 45001', 'ISO 45001 - Seguridad y Salud Ocupacional'),
        ('ISO 14001', 'ISO 14001 - Gestión Ambiental'),
        ('AWS D1.6', 'AWS D1.6 - Soldadura de Acero Inoxidable'),
        ('ASME BPVC', 'ASME BPVC - Código de Calderas y Recipientes'),
        ('OSHA 1910.146', 'OSHA 1910.146 - Espacios Confinados'),
        ('ASTM A48', 'ASTM A48 - Fundición de Hierro Gris'),
        ('ISO 17025', 'ISO 17025 - Competencia de Laboratorios'),
        ('ISO 55000', 'ISO 55000 - Gestión de Activos'),
        ('otra', 'Otra normativa'),
    ]

    # Información básica
    codigo = models.CharField("Código POP", max_length=20, unique=True)
    titulo = models.CharField("Título del Procedimiento", max_length=200)
    descripcion = models.TextField("Descripción")
    version = models.CharField("Versión", max_length=10, default="v1.0")
    
    # Clasificación
    area = models.CharField("Área", max_length=20, choices=AREA_CHOICES)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES)
    prioridad = models.CharField("Prioridad", max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField("Estado", max_length=25, choices=ESTADO_CHOICES, default='pendiente_aprobacion')
    
    # Personal
    responsable = models.CharField("Responsable Principal", max_length=100)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pops_creados')
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pops_aprobados')
    
    # Equipo asociado
    equipo_asociado = models.CharField("Código de Equipo", max_length=50, blank=True, null=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True, related_name='procedimientos')
    
    # Normativa
    normativa = models.CharField("Normativa Aplicable", max_length=50, choices=NORMATIVAS_CHOICES)
    normativa_especifica = models.CharField("Normativa Específica", max_length=200, blank=True, null=True,
                                          help_text="Especificar si seleccionó 'Otra normativa'")
    
    # Tiempos y frecuencia
    tiempo_estimado = models.PositiveIntegerField("Tiempo Estimado (minutos)", default=30,
                                                 validators=[MinValueValidator(1), MaxValueValidator(1440)])
    frecuencia_aplicacion = models.CharField("Frecuencia de Aplicación", max_length=15, 
                                           choices=FRECUENCIA_CHOICES, default='mensual')
    
    # Fechas
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_ultima_revision = models.DateField("Última Revisión")
    fecha_proxima_revision = models.DateField("Próxima Revisión")
    fecha_vencimiento = models.DateField("Fecha de Vencimiento", blank=True, null=True)
    fecha_aprobacion = models.DateTimeField("Fecha de Aprobación", blank=True, null=True)
    
    # Contenido del procedimiento
    objetivo = models.TextField("Objetivo del Procedimiento")
    alcance = models.TextField("Alcance", blank=True, null=True)
    materiales_herramientas = models.TextField("Materiales y Herramientas Necesarios", blank=True, null=True)
    epp_requerido = models.TextField("Equipos de Protección Personal", blank=True, null=True)
    procedimiento_paso_a_paso = models.TextField("Procedimiento Paso a Paso")
    precauciones_seguridad = models.TextField("Precauciones de Seguridad", blank=True, null=True)
    criterios_aceptacion = models.TextField("Criterios de Aceptación", blank=True, null=True)
    registros_documentos = models.TextField("Registros y Documentos Relacionados", blank=True, null=True)
    
    # Archivos adjuntos
    documento_pdf = models.FileField("Documento PDF", upload_to='procedimientos/documentos/', blank=True, null=True)
    diagrama_flujo = models.ImageField("Diagrama de Flujo", upload_to='procedimientos/diagramas/', blank=True, null=True)
    fotos_referencia = models.ImageField("Fotos de Referencia", upload_to='procedimientos/fotos/', blank=True, null=True)
    
    # Control y seguimiento
    es_critico = models.BooleanField("Procedimiento Crítico", default=False)
    requiere_certificacion = models.BooleanField("Requiere Certificación", default=False)
    numero_ejecuciones = models.PositiveIntegerField("Número de Ejecuciones", default=0)
    eficiencia_promedio = models.DecimalField("Eficiencia Promedio (%)", max_digits=5, decimal_places=2, 
                                            default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Observaciones
    observaciones = models.TextField("Observaciones", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Procedimiento Operativo Estándar"
        verbose_name_plural = "Procedimientos Operativos Estándar"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    def get_absolute_url(self):
        return reverse('operaciones:detalle-pop', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Generar código automático si no existe
        if not self.codigo:
            last_pop = ProcedimientoOperativo.objects.filter(
                codigo__startswith='POP'
            ).order_by('codigo').last()
            
            if last_pop:
                last_number = int(last_pop.codigo.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            # Formato: POP-XXX-001 donde XXX es las primeras 3 letras del área
            area_code = self.area.upper()[:3]
            self.codigo = f"POP-{area_code}-{new_number:03d}"
        
        # Asignar fecha de vencimiento si no existe
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.fecha_proxima_revision
        
        super().save(*args, **kwargs)

    def dias_hasta_vencimiento(self):
        """Calcula los días hasta el vencimiento"""
        if self.fecha_vencimiento:
            diferencia = self.fecha_vencimiento - date.today()
            return diferencia.days
        return 0  # Retornar 0 en lugar de None

    def dias_vencimiento_absoluto(self):
        """Retorna el valor absoluto de días hasta vencimiento"""
        dias = self.dias_hasta_vencimiento()
        return abs(dias) if dias is not None else 0

    def esta_vencido(self):
        """Verifica si el procedimiento está vencido"""
        return self.dias_hasta_vencimiento() < 0

    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'activo': 'bg-success',
            'pendiente_aprobacion': 'bg-warning',
            'en_capacitacion': 'bg-info',
            'validado_campo': 'bg-primary',
            'vencido': 'bg-danger',
            'obsoleto': 'bg-secondary',
        }
        return clases.get(self.estado, 'bg-secondary')

    def get_prioridad_badge_class(self):
        """Retorna la clase CSS para el badge de prioridad"""
        clases = {
            'baja': 'bg-secondary',
            'media': 'bg-info',
            'alta': 'bg-warning',
            'urgente': 'bg-danger',
        }
        return clases.get(self.prioridad, 'bg-secondary')

class AnalisisRiesgo(models.Model):
    """Modelo para la gestión de análisis de riesgos industriales"""
    
    TIPO_RIESGO_CHOICES = [
        ('mecanico', 'Mecánico'),
        ('electrico', 'Eléctrico'),
        ('quimico', 'Químico'),
        ('termico', 'Térmico'),
        ('ergonomico', 'Ergonómico'),
        ('psicosocial', 'Psicosocial'),
        ('fisico', 'Físico'),
        ('biologico', 'Biológico'),
        ('ambiental', 'Ambiental'),
    ]
    
    AREA_CHOICES = [
        ('soldadura', 'Soldadura'),
        ('maquinado', 'Maquinado'),
        ('fundicion', 'Fundición'),
        ('calidad', 'Control de Calidad'),
        ('mantenimiento', 'Mantenimiento'),
        ('almacen', 'Almacén'),
        ('oficinas', 'Oficinas'),
        ('laboratorio', 'Laboratorio'),
    ]
    
    ESTADO_CHOICES = [
        ('identificado', 'Identificado'),
        ('en_tratamiento', 'En Tratamiento'),
        ('controlado', 'Controlado'),
        ('en_revision', 'En Revisión'),
        ('cerrado', 'Cerrado'),
    ]
    
    NIVEL_RIESGO_CHOICES = [
        ('trivial', 'Trivial'),
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('extremo', 'Extremo'),
    ]
    
    # Información básica
    codigo = models.CharField("Código de Riesgo", max_length=20, unique=True)
    descripcion = models.TextField("Descripción del Riesgo")
    area = models.CharField("Área", max_length=20, choices=AREA_CHOICES)
    tipo = models.CharField("Tipo de Riesgo", max_length=20, choices=TIPO_RIESGO_CHOICES)
    
    # Evaluación de riesgo
    probabilidad = models.IntegerField(
        "Probabilidad (1-5)", 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Muy Baja, 2=Baja, 3=Media, 4=Alta, 5=Muy Alta"
    )
    severidad = models.IntegerField(
        "Severidad (1-5)", 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Insignificante, 2=Menor, 3=Moderada, 4=Mayor, 5=Catastrófica"
    )
    riesgo_actual = models.IntegerField("Riesgo Actual", editable=False)
    nivel_riesgo = models.CharField("Nivel de Riesgo", max_length=10, 
                                  choices=NIVEL_RIESGO_CHOICES, editable=False)
    
    # Gestión y control
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default='identificado')
    responsable = models.CharField("Responsable", max_length=100)
    fecha_identificacion = models.DateField("Fecha de Identificación", default=date.today)
    fecha_revision = models.DateField("Fecha de Revisión")
    
    # Medidas de control
    medidas_control = models.TextField("Medidas de Control Implementadas", blank=True)
    recursos_necesarios = models.TextField("Recursos Necesarios", blank=True)
    plazo_implementacion = models.IntegerField("Plazo de Implementación (días)", null=True, blank=True)
    
    # Seguimiento
    fecha_ultima_revision = models.DateField("Última Revisión", null=True, blank=True)
    observaciones = models.TextField("Observaciones", blank=True)
    
    # Relaciones
    equipo_asociado = models.ForeignKey(Equipo, on_delete=models.SET_NULL, 
                                      null=True, blank=True, 
                                      verbose_name="Equipo Asociado")
    identificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                       null=True, blank=True,
                                       related_name='riesgos_identificados')
    
    # Metadatos
    fecha_creacion = models.DateTimeField("Fecha de Creación", default=timezone.now)
    fecha_actualizacion = models.DateTimeField("Última Actualización", default=timezone.now)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Análisis de Riesgo"
        verbose_name_plural = "Análisis de Riesgos"
        ordering = ['-riesgo_actual', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}..."
    
    def save(self, *args, **kwargs):
        # Si no tiene fecha_creacion, asignarla con timezone
        if not self.pk and not self.fecha_creacion:
            self.fecha_creacion = timezone.now()
        
        # Siempre actualizar fecha_actualizacion con timezone
        self.fecha_actualizacion = timezone.now()
        
        # Generar código automático si no existe
        if not self.codigo:
            last_risk = AnalisisRiesgo.objects.filter(
                codigo__startswith='R'
            ).order_by('codigo').last()
            
            if last_risk:
                try:
                    last_number = int(last_risk.codigo.split('-')[-1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            
            # Formato: R[TIPO]-[AREA]-001
            area_code = self.area.upper()[:3]
            tipo_code = self.tipo.upper()[:2]
            self.codigo = f"R{tipo_code}-{area_code}-{new_number:03d}"
        
        # Calcular riesgo actual y nivel
        self.riesgo_actual = self.probabilidad * self.severidad
        self.nivel_riesgo = self.calcular_nivel_riesgo()
        
        super().save(*args, **kwargs)
    
    def calcular_nivel_riesgo(self):
        """Calcula el nivel de riesgo basado en la matriz 5x5"""
        valor = self.riesgo_actual
        if valor >= 20:
            return 'extremo'
        elif valor >= 15:
            return 'alto'
        elif valor >= 10:
            return 'medio'
        elif valor >= 5:
            return 'bajo'
        else:
            return 'trivial'
    
    def get_color_riesgo(self):
        """Retorna el color asociado al nivel de riesgo"""
        colores = {
            'extremo': 'danger',
            'alto': 'warning',
            'medio': 'info',
            'bajo': 'secondary',
            'trivial': 'success',
        }
        return colores.get(self.nivel_riesgo, 'secondary')
    
    def esta_vencido_revision(self):
        """Verifica si está vencida la fecha de revisión"""
        return date.today() > self.fecha_revision
    
    def dias_hasta_revision(self):
        """Calcula días hasta la próxima revisión"""
        diferencia = self.fecha_revision - date.today()
        return diferencia.days
    
    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'identificado': 'bg-warning',
            'en_tratamiento': 'bg-info',
            'controlado': 'bg-success',
            'en_revision': 'bg-primary',
            'cerrado': 'bg-secondary',
        }
        return clases.get(self.estado, 'bg-secondary')


class MedidaControl(models.Model):
    """Modelo para medidas de control específicas de un riesgo"""
    
    TIPO_MEDIDA_CHOICES = [
        ('eliminacion', 'Eliminación'),
        ('sustitucion', 'Sustitución'),
        ('ingenieria', 'Controles de Ingeniería'),
        ('administrativo', 'Controles Administrativos'),
        ('epp', 'Equipos de Protección Personal'),
    ]
    
    ESTADO_MEDIDA_CHOICES = [
        ('planificada', 'Planificada'),
        ('en_implementacion', 'En Implementación'),
        ('implementada', 'Implementada'),
        ('verificada', 'Verificada'),
        ('no_efectiva', 'No Efectiva'),
    ]
    
    riesgo = models.ForeignKey(AnalisisRiesgo, on_delete=models.CASCADE, 
                             related_name='medidas_control_detalle')
    descripcion = models.TextField("Descripción de la Medida")
    tipo_medida = models.CharField("Tipo de Medida", max_length=20, choices=TIPO_MEDIDA_CHOICES)
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_MEDIDA_CHOICES, 
                            default='planificada')
    
    fecha_planificada = models.DateField("Fecha Planificada")
    fecha_implementacion = models.DateField("Fecha de Implementación", null=True, blank=True)
    responsable = models.CharField("Responsable", max_length=100)
    costo_estimado = models.DecimalField("Costo Estimado", max_digits=10, 
                                       decimal_places=2, null=True, blank=True)
    
    eficacia_esperada = models.IntegerField(
        "Eficacia Esperada (%)", 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=80
    )
    
    observaciones = models.TextField("Observaciones", blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Medida de Control"
        verbose_name_plural = "Medidas de Control"
        ordering = ['fecha_planificada']
    
    def __str__(self):
        return f"{self.riesgo.codigo} - {self.descripcion[:30]}..."