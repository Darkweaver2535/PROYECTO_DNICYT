from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo

class RepuestoCritico(models.Model):
    """Modelo para repuestos críticos asociados a planes de mantenimiento"""
    nombre = models.CharField("Nombre del Repuesto", max_length=200)
    codigo_fabricante = models.CharField("Código del Fabricante", max_length=100, blank=True)
    descripcion = models.TextField("Descripción", blank=True)
    stock_minimo = models.PositiveIntegerField("Stock Mínimo", default=1)
    tiempo_entrega = models.PositiveIntegerField("Tiempo de Entrega (días)", default=30)
    proveedor = models.CharField("Proveedor", max_length=200, blank=True)
    costo_unitario = models.DecimalField("Costo Unitario", max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Repuesto Crítico"
        verbose_name_plural = "Repuestos Críticos"
    
    def __str__(self):
        return self.nombre

class PlanMantenimiento(models.Model):
    TIPO_MANTENIMIENTO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('predictivo', 'Predictivo'),
        ('autonomo', 'Autónomo'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    NORMAS_APLICABLES_CHOICES = [
        ('iso_14224', 'ISO 14224 - Industrias de petróleo, petroquímica y gas natural'),
        ('iso_55000', 'ISO 55000 - Gestión de activos'),
        ('iso_13374', 'ISO 13374 - Monitoreo de condición y diagnóstico de máquinas'),
        ('iec_60300', 'IEC 60300 - Gestión de la confiabilidad'),
        ('din_31051', 'DIN 31051 - Fundamentos del mantenimiento'),
        ('norsok_z008', 'NORSOK Z-008 - Criticidad y análisis de riesgo'),
        ('api_580', 'API 580 - Inspección basada en riesgo'),
        ('asme_pcc', 'ASME PCC - Códigos de construcción y soldadura'),
        ('otra', 'Otra norma específica'),
    ]

    # Información básica
    codigo_plan = models.CharField("Código del Plan", max_length=20, unique=True)
    nombre = models.CharField("Nombre del Plan", max_length=200)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='planes_mantenimiento')
    
    # Tipo y frecuencia
    tipo_mantenimiento = models.CharField("Tipo de Mantenimiento", max_length=20, choices=TIPO_MANTENIMIENTO_CHOICES)
    frecuencia = models.CharField("Frecuencia", max_length=20, choices=FRECUENCIA_CHOICES)
    duracion_estimada = models.DecimalField("Duración Estimada (horas)", max_digits=5, decimal_places=2, 
                                          validators=[MinValueValidator(0.1)])
    
    # Prioridad y estado
    prioridad = models.CharField("Prioridad", max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador',  # Asegurar que tenga un default
        help_text="Estado actual del plan de mantenimiento"
    )
    
    # Responsables
    responsable_principal = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='planes_responsable')
    responsables_secundarios = models.ManyToManyField(User, blank=True, related_name='planes_colaborador')
    
    # Fechas
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_inicio = models.DateField("Fecha de Inicio")
    proxima_ejecucion = models.DateField("Próxima Ejecución", null=True, blank=True)
    ultima_ejecucion = models.DateField("Última Ejecución", null=True, blank=True)
    
    # Costos estimados
    costo_estimado = models.DecimalField("Costo Estimado", max_digits=10, decimal_places=2, 
                                       validators=[MinValueValidator(0)], default=0)
    
    # Documentos
    procedimiento_documento = models.FileField("Documento de Procedimiento", 
                                             upload_to='mantenimiento/procedimientos/', 
                                             blank=True, null=True)
    lista_verificacion = models.FileField("Lista de Verificación", 
                                        upload_to='mantenimiento/listas/', 
                                        blank=True, null=True)
    
    # Control de calidad
    requiere_parada_equipo = models.BooleanField("Requiere Parada de Equipo", default=False)
    herramientas_especiales = models.TextField("Herramientas Especiales", blank=True, null=True)
    materiales_requeridos = models.TextField("Materiales Requeridos", blank=True, null=True)
    
    # *** NUEVOS CAMPOS SEGÚN RECOMENDACIONES ***
    # Repuestos críticos
    repuestos_criticos = models.ManyToManyField(RepuestoCritico, blank=True, 
                                              verbose_name="Repuestos Críticos")
    
    # Normativas técnicas
    norma_aplicable = models.CharField("Norma Técnica Aplicable", max_length=20, 
                                     choices=NORMAS_APLICABLES_CHOICES, 
                                     default='iso_55000')
    norma_especifica = models.CharField("Norma Específica", max_length=200, blank=True,
                                      help_text="Especificar si seleccionó 'Otra norma específica'")
    
    # Cumplimiento normativo
    cumple_iso = models.BooleanField("Cumple ISO 55000", default=False)
    cumple_api = models.BooleanField("Cumple API 580", default=False)
    cumple_asme = models.BooleanField("Cumple ASME", default=False)
    certificacion_vigente = models.BooleanField("Certificación Vigente", default=False)
    fecha_ultima_auditoria = models.DateField("Última Auditoría", null=True, blank=True)
    
    # Métricas de eficiencia
    numero_ejecuciones = models.PositiveIntegerField("Número de Ejecuciones", default=0)
    tiempo_promedio_ejecucion = models.DecimalField("Tiempo Promedio (horas)", max_digits=5, 
                                                   decimal_places=2, default=0)
    eficiencia_promedio = models.DecimalField("Eficiencia Promedio (%)", max_digits=5, 
                                            decimal_places=2, default=0,
                                            validators=[MinValueValidator(0), MaxValueValidator(100)])
    tasa_cumplimiento = models.DecimalField("Tasa de Cumplimiento (%)", max_digits=5, 
                                          decimal_places=2, default=0,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Análisis de fallas
    mtbf = models.DecimalField("MTBF - Tiempo Medio Entre Fallas (horas)", max_digits=10, 
                             decimal_places=2, default=0, null=True, blank=True)
    mttr = models.DecimalField("MTTR - Tiempo Medio de Reparación (horas)", max_digits=8, 
                             decimal_places=2, default=0, null=True, blank=True)
    disponibilidad_objetivo = models.DecimalField("Disponibilidad Objetivo (%)", max_digits=5, 
                                                decimal_places=2, default=95.0,
                                                validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Criticidad del equipo
    nivel_criticidad = models.CharField("Nivel de Criticidad", max_length=20, 
                                      choices=[
                                          ('muy_baja', 'Muy Baja'),
                                          ('baja', 'Baja'),
                                          ('media', 'Media'),
                                          ('alta', 'Alta'),
                                          ('muy_alta', 'Muy Alta'),
                                          ('critica', 'Crítica')
                                      ], default='media')
    
    # Observaciones
    observaciones = models.TextField("Observaciones", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Plan de Mantenimiento"
        verbose_name_plural = "Planes de Mantenimiento"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo_plan} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('mantenimiento:plan-detalle', kwargs={'pk': self.pk})

    def calcular_siguiente_mantenimiento(self):
        """Calcula la fecha del próximo mantenimiento basado en la frecuencia"""
        from datetime import timedelta
        
        # Usar última ejecución como base, o fecha de inicio si no hay
        fecha_base = self.ultima_ejecucion or self.fecha_inicio
        
        dias_frecuencia = {
            'diario': 1,
            'semanal': 7,
            'quincenal': 15,
            'mensual': 30,
            'bimestral': 60,
            'trimestral': 90,
            'semestral': 180,
            'anual': 365,
        }
        
        dias = dias_frecuencia.get(self.frecuencia, 30)
        return fecha_base + timedelta(days=dias)

    def esta_atrasado(self):
        """Verifica si el mantenimiento está atrasado"""
        from datetime import date
        
        if not self.proxima_ejecucion:
            return False
        
        return date.today() > self.proxima_ejecucion

    def dias_hasta_mantenimiento(self):
        """Calcula los días hasta el próximo mantenimiento"""
        from datetime import date
        
        if not self.proxima_ejecucion:
            return None
        
        diferencia = self.proxima_ejecucion - date.today()
        return diferencia.days

    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'activo': 'bg-success',
            'pausado': 'bg-warning',
            'inactivo': 'bg-secondary',
            'revision': 'bg-info',
        }
        return clases.get(self.estado, 'bg-secondary')

    def get_prioridad_badge_class(self):
        """Retorna la clase CSS para el badge de prioridad"""
        clases = {
            'baja': 'bg-secondary',
            'media': 'bg-info',
            'alta': 'bg-warning',
            'critica': 'bg-danger',
        }
        return clases.get(self.prioridad, 'bg-secondary')

    def get_criticidad_badge_class(self):
        """Retorna la clase CSS para el badge de criticidad"""
        clases = {
            'muy_baja': 'bg-light text-dark',
            'baja': 'bg-secondary',
            'media': 'bg-info',
            'alta': 'bg-warning',
            'muy_alta': 'bg-danger',
            'critica': 'bg-dark',
        }
        return clases.get(self.nivel_criticidad, 'bg-secondary')

    def calcular_eficiencia_actual(self):
        """Calcula la eficiencia actual basada en las métricas"""
        if self.numero_ejecuciones == 0:
            return 0
        
        # Formula básica de eficiencia considerando cumplimiento y tiempo
        factor_cumplimiento = self.tasa_cumplimiento or 0
        factor_tiempo = 100 if self.tiempo_promedio_ejecucion <= self.duracion_estimada else 80
        
        eficiencia = (factor_cumplimiento + factor_tiempo) / 2
        return min(eficiencia, 100)

    def save(self, *args, **kwargs):
        print(f"🔧 DEBUG: Guardando plan {self.nombre}")
        
        # Generar código automático si no existe
        if not self.codigo_plan:
            last_plan = PlanMantenimiento.objects.filter(
                codigo_plan__startswith='PM'
            ).order_by('codigo_plan').last()
            
            if last_plan:
                last_number = int(last_plan.codigo_plan[2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.codigo_plan = f"PM{new_number:04d}"
        
        # MEJORAR: Calcular próxima ejecución
        if not self.proxima_ejecucion:
            if self.ultima_ejecucion:
                self.proxima_ejecucion = self.calcular_siguiente_mantenimiento()
                print(f"🔧 DEBUG: Próxima ejecución calculada desde última: {self.proxima_ejecucion}")
            elif self.fecha_inicio:
                # Si es un plan nuevo, la próxima ejecución es la fecha de inicio
                self.proxima_ejecucion = self.fecha_inicio
                print(f"🔧 DEBUG: Próxima ejecución asignada como fecha inicio: {self.proxima_ejecucion}")
        
        # Actualizar eficiencia promedio
        self.eficiencia_promedio = self.calcular_eficiencia_actual()
        
        print(f"🔧 DEBUG: Plan guardado - Código: {self.codigo_plan}, Próxima: {self.proxima_ejecucion}")
        
        super().save(*args, **kwargs)

    def get_equipo_info(self):
        """Retorna información completa del equipo asociado"""
        if self.equipo:
            return {
                'codigo': self.equipo.codigo_interno,
                'nombre': self.equipo.nombre,
                'seccion': self.equipo.get_seccion_display(),
                'estado': self.equipo.get_estado_display(),
                'ubicacion': self.equipo.ubicacion_fisica,
                'responsable': self.equipo.responsable,
            }
        return None

    def puede_ejecutarse(self):
        """Verifica si el plan puede ejecutarse (equipo operativo)"""
        return self.equipo and self.equipo.estado == 'OPERATIVO' and self.estado == 'activo'


class TareaMantenimiento(models.Model):
    ESTADO_TAREA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    plan = models.ForeignKey(PlanMantenimiento, on_delete=models.CASCADE, related_name='tareas')
    nombre = models.CharField("Nombre de la Tarea", max_length=200)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    orden = models.PositiveIntegerField("Orden", default=1)
    duracion_estimada = models.DecimalField("Duración Estimada (minutos)", max_digits=5, 
                                          decimal_places=0, default=30)
    es_critica = models.BooleanField("Tarea Crítica", default=False)
    requiere_verificacion = models.BooleanField("Requiere Verificación", default=False)
    estado = models.CharField("Estado", max_length=15, choices=ESTADO_TAREA_CHOICES, default='pendiente')
    
    # Responsable específico para la tarea
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Instrucciones específicas
    instrucciones = models.TextField("Instrucciones Específicas", blank=True, null=True)
    herramientas_necesarias = models.TextField("Herramientas Necesarias", blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarea de Mantenimiento"
        verbose_name_plural = "Tareas de Mantenimiento"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.plan.codigo_plan} - {self.nombre}"
