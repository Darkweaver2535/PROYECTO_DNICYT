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

class OrdenTrabajo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_progreso', 'En Progreso'),
        ('pausada', 'Pausada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('rechazada', 'Rechazada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
        ('critica', 'Crítica'),
    ]
    
    TIPO_ORDEN_CHOICES = [
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('predictivo', 'Mantenimiento Predictivo'),
        ('emergencia', 'Emergencia'),
        ('mejora', 'Mejora'),
        ('instalacion', 'Instalación'),
        ('inspeccion', 'Inspección'),
    ]

    # Información básica
    numero_orden = models.CharField("Número de Orden", max_length=20, unique=True)
    titulo = models.CharField("Título de la Orden", max_length=200)
    descripcion = models.TextField("Descripción del Trabajo")
    
    # Relaciones
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='ordenes_trabajo')
    plan_mantenimiento = models.ForeignKey(
        PlanMantenimiento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_trabajo',
        help_text="Plan de mantenimiento que generó esta orden (si aplica)"
    )
    
    # Estado y clasificación
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField("Prioridad", max_length=20, choices=PRIORIDAD_CHOICES, default='normal')
    tipo_orden = models.CharField("Tipo de Orden", max_length=20, choices=TIPO_ORDEN_CHOICES)
    
    # Responsables
    solicitante = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ordenes_solicitadas',
        help_text="Usuario que solicita el trabajo"
    )
    asignado_a = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_asignadas',
        help_text="Técnico o responsable asignado"
    )
    supervisado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ordenes_supervisadas',
        help_text="Supervisor a cargo"
    )
    
    # Fechas
    fecha_creacion = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    fecha_programada = models.DateTimeField("Fecha Programada", null=True, blank=True)
    fecha_inicio_real = models.DateTimeField("Fecha de Inicio Real", null=True, blank=True)
    fecha_fin_programada = models.DateTimeField("Fecha Fin Programada", null=True, blank=True)
    fecha_completada = models.DateTimeField("Fecha de Completación", null=True, blank=True)
    
    # Estimaciones y control
    horas_estimadas = models.DecimalField("Horas Estimadas", max_digits=6, decimal_places=2, default=0)
    horas_reales = models.DecimalField("Horas Reales", max_digits=6, decimal_places=2, default=0)
    costo_estimado = models.DecimalField("Costo Estimado", max_digits=10, decimal_places=2, default=0)
    costo_real = models.DecimalField("Costo Real", max_digits=10, decimal_places=2, default=0)
    
    # Detalles técnicos
    materiales_necesarios = models.TextField("Materiales Necesarios", blank=True, null=True)
    herramientas_necesarias = models.TextField("Herramientas Necesarias", blank=True, null=True)
    procedimientos_seguir = models.TextField("Procedimientos a Seguir", blank=True, null=True)
    observaciones_iniciales = models.TextField("Observaciones Iniciales", blank=True, null=True)
    
    # Resultados
    trabajo_realizado = models.TextField("Trabajo Realizado", blank=True, null=True)
    observaciones_finales = models.TextField("Observaciones Finales", blank=True, null=True)
    repuestos_utilizados = models.TextField("Repuestos Utilizados", blank=True, null=True)
    
    # Control de calidad
    requiere_pruebas = models.BooleanField("Requiere Pruebas", default=False)
    pruebas_realizadas = models.TextField("Pruebas Realizadas", blank=True, null=True)
    resultado_satisfactorio = models.BooleanField("Resultado Satisfactorio", default=False)
    
    # Documentos
    documentos_adjuntos = models.FileField(
        "Documentos Adjuntos", 
        upload_to='ordenes_trabajo/documentos/', 
        blank=True, 
        null=True
    )
    fotos_antes = models.ImageField(
        "Fotos Antes del Trabajo", 
        upload_to='ordenes_trabajo/fotos_antes/', 
        blank=True, 
        null=True
    )
    fotos_despues = models.ImageField(
        "Fotos Después del Trabajo", 
        upload_to='ordenes_trabajo/fotos_despues/', 
        blank=True, 
        null=True
    )
    
    # Seguimiento
    comentarios_adicionales = models.TextField("Comentarios Adicionales", blank=True, null=True)
    requiere_seguimiento = models.BooleanField("Requiere Seguimiento", default=False)
    fecha_proximo_seguimiento = models.DateField("Próximo Seguimiento", null=True, blank=True)
    
    # Evaluación
    calificacion_trabajo = models.PositiveIntegerField(
        "Calificación del Trabajo (1-5)", 
        null=True, 
        blank=True,
        help_text="Calificación de 1 a 5 estrellas"
    )
    
    # Metadatos
    fecha_actualizacion = models.DateTimeField("Última Actualización", auto_now=True)
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.numero_orden} - {self.titulo}"

    def save(self, *args, **kwargs):
        # Generar número de orden automático
        if not self.numero_orden:
            ultimo_numero = OrdenTrabajo.objects.filter(
                numero_orden__startswith='OT'
            ).order_by('numero_orden').last()
            
            if ultimo_numero:
                numero = int(ultimo_numero.numero_orden[2:]) + 1
            else:
                numero = 1
            
            self.numero_orden = f"OT{numero:05d}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mantenimiento:orden-detalle', kwargs={'pk': self.pk})

    def calcular_duracion(self):
        """Calcula la duración real del trabajo"""
        if self.fecha_inicio_real and self.fecha_completada:
            return self.fecha_completada - self.fecha_inicio_real
        return None

    def esta_atrasada(self):
        """Verifica si la orden está atrasada"""
        from datetime import datetime
        if self.fecha_programada and self.estado not in ['completada', 'cancelada']:
            return datetime.now() > self.fecha_programada
        return False

    def get_estado_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        clases = {
            'pendiente': 'bg-secondary',
            'asignada': 'bg-info',
            'en_progreso': 'bg-warning',
            'pausada': 'bg-dark',
            'completada': 'bg-success',
            'cancelada': 'bg-danger',
            'rechazada': 'bg-danger',
        }
        return clases.get(self.estado, 'bg-secondary')

    def get_prioridad_badge_class(self):
        """Retorna la clase CSS para el badge de prioridad"""
        clases = {
            'baja': 'bg-light text-dark',
            'normal': 'bg-secondary',
            'alta': 'bg-warning',
            'urgente': 'bg-danger',
            'critica': 'bg-dark',
        }
        return clases.get(self.prioridad, 'bg-secondary')

    def get_eficiencia(self):
        """Calcula la eficiencia de la orden"""
        if self.horas_estimadas and self.horas_reales:
            return min((self.horas_estimadas / self.horas_reales) * 100, 100)
        return 0
