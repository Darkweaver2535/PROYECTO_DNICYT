# equipos/models.py
from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    identificador = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=200)
    responsable = models.CharField(max_length=100)
    colaborador = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

UDB_UNIDADES = [
    ('LPZ', 'LPZ'),
    ('SCZ', 'SCZ'),
    ('CBAA', 'CBAA'),
    ('RIB', 'RIB'),
    ('TROP', 'TROP'),
]

class Equipo(models.Model):
    SECCION_CHOICES = [
        ('SOLDADURA', 'Soldadura'),
        ('MAQUINADO', 'Maquinado'),
        ('PROTOTIPADO', 'Prototipado'),
        ('PLASTICOS', 'Plásticos'),
        ('FUNDICION', 'Fundición'),
        ('SUJECION', 'Sujeción'),
        ('TRANSPORTE', 'Transporte'),
    ]
    ESTADO_CHOICES = [
        ('OPERATIVO', 'Operativo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('FUERA_SERVICIO', 'Fuera de Servicio'),
    ]
    
    VOLTAJE_CHOICES = [
        ('110V', '110V'),
        ('220V', '220V'),
        ('380V', '380V'),
        ('440V', '440V'),
        ('110V/220V', '110V/220V'),
        ('220V/380V', '220V/380V'),
        ('otro', 'Otro'),
    ]
    
    FASES_CHOICES = [
        ('Monofásico', 'Monofásico'),
        ('Bifásico', 'Bifásico'),
        ('Trifásico', 'Trifásico'),
    ]
    
    FRECUENCIA_CHOICES = [
        ('50Hz', '50 Hz'),
        ('60Hz', '60 Hz'),
        ('50/60Hz', '50/60 Hz'),
    ]
    
    FRECUENCIA_MANTENIMIENTO_CHOICES = [
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    # Campos básicos del equipo
    codigo_interno = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    año_fabricacion = models.IntegerField(null=True, blank=True)
    potencia = models.CharField(max_length=50, null=True, blank=True)
    capacidad = models.CharField(max_length=100, null=True, blank=True)
    ubicacion_fisica = models.CharField(max_length=100)
    seccion = models.CharField(max_length=20, choices=SECCION_CHOICES)
    tipo_equipo = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    foto = models.ImageField(upload_to='equipos/', blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    responsable = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(null=True, blank=True)
    
    # Campos UDB
    codigo_udb = models.CharField(
        "Código Unidad de Disposición de Bienes",
        max_length=100,
        blank=True,
        null=True,
        help_text="Formato: EMI - LPZ [NÚMERO] [AÑO] - Ejemplo: EMI - LPZ 1-22386 2025"
    )
    udb_unidad = models.CharField(
        "Unidad EMI",
        max_length=5,
        choices=UDB_UNIDADES,
        default='LPZ'
    )
    udb_numero = models.CharField(
        "Número de Disposición",
        max_length=20,
        blank=True,
        null=True,
        help_text="Ejemplo: 1-22386",
        validators=[
            RegexValidator(
                regex=r'^\d-\d{5}$',
                message='El número debe tener el formato 1-12345 (un dígito, guion, cinco dígitos)'
            )
        ]
    )
    
    # NUEVOS CAMPOS PARA FICHA TÉCNICA
    
    # Información técnica básica
    numero_serie = models.CharField("Número de Serie", max_length=100, blank=True, null=True)
    peso = models.DecimalField("Peso (kg)", max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Especificaciones eléctricas
    voltaje = models.CharField("Voltaje", max_length=20, choices=VOLTAJE_CHOICES, blank=True, null=True)
    amperaje = models.CharField("Amperaje", max_length=50, blank=True, null=True)
    fases = models.CharField("Tipo de Alimentación", max_length=20, choices=FASES_CHOICES, blank=True, null=True)
    frecuencia = models.CharField("Frecuencia", max_length=20, choices=FRECUENCIA_CHOICES, blank=True, null=True)
    consumo_electrico = models.DecimalField("Consumo Eléctrico (kW)", max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Condiciones de operación
    temperatura_min = models.IntegerField("Temperatura Mínima (°C)", blank=True, null=True)
    temperatura_max = models.IntegerField("Temperatura Máxima (°C)", blank=True, null=True)
    humedad_max = models.IntegerField("Humedad Máxima (%)", blank=True, null=True)
    presion_trabajo = models.DecimalField("Presión de Trabajo (Bar)", max_digits=6, decimal_places=2, blank=True, null=True)
    caudal_aire = models.IntegerField("Caudal de Aire (L/min)", blank=True, null=True)
    
    # Seguridad industrial (por ahora como texto, después se puede expandir)
    epp_requerido = models.TextField("Equipos de Protección Personal", blank=True, null=True)
    
    # Documentos técnicos
    esquema_electrico = models.FileField("Esquema Eléctrico", upload_to='documentos/esquemas/', blank=True, null=True)
    manual_operacion = models.FileField("Manual de Operación", upload_to='documentos/manuales/', blank=True, null=True)
    
    # Mantenimiento
    frecuencia_mantenimiento = models.CharField("Frecuencia de Mantenimiento", max_length=20, choices=FRECUENCIA_MANTENIMIENTO_CHOICES, blank=True, null=True)
    tiempo_mantenimiento = models.DecimalField("Tiempo Estimado Mantenimiento (horas)", max_digits=4, decimal_places=1, blank=True, null=True)
    procedimientos_mantenimiento = models.TextField("Procedimientos de Mantenimiento", blank=True, null=True)
    
    # Ubicación específica
    ubicacion_especifica = models.CharField("Ubicación Específica", max_length=200, blank=True, null=True)
    
    # Campo para indicar si la ficha técnica está completa
    ficha_tecnica_completa = models.BooleanField("Ficha Técnica Completa", default=False)
    fecha_actualizacion_ficha = models.DateTimeField("Última Actualización Ficha", auto_now=True)

    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('equipos:equipo-detalle', kwargs={'pk': self.pk})
    
    def calcular_completitud_ficha(self):
        """Calcula el porcentaje de completitud de la ficha técnica"""
        campos_totales = 25  # Total de campos importantes para la ficha
        campos_completos = 0
        
        # Campos básicos (peso 2 cada uno por ser fundamentales)
        campos_basicos = [
            self.nombre, self.modelo, self.fabricante, self.numero_serie,
            self.año_fabricacion, self.potencia, self.capacidad
        ]
        for campo in campos_basicos:
            if campo:
                campos_completos += 2
        
        # Campos eléctricos (peso 1.5 cada uno)
        campos_electricos = [
            self.voltaje, self.amperaje, self.fases, self.frecuencia
        ]
        for campo in campos_electricos:
            if campo:
                campos_completos += 1.5
        
        # Campos operacionales (peso 1 cada uno)
        campos_operacionales = [
            self.temperatura_min, self.temperatura_max, self.humedad_max,
            self.presion_trabajo, self.peso
        ]
        for campo in campos_operacionales:
            if campo:
                campos_completos += 1
        
        # Documentos (peso 2 cada uno por ser importantes)
        if self.foto:
            campos_completos += 2
        if self.esquema_electrico:
            campos_completos += 2
        if self.manual_operacion:
            campos_completos += 2
        
        # Campos de texto (peso 1 cada uno)
        if self.observaciones:
            campos_completos += 1
        if self.ubicacion_especifica:
            campos_completos += 1
        if self.responsable:
            campos_completos += 1
        
        porcentaje = min(int((campos_completos / campos_totales) * 100), 100)
        
        # Actualizar el campo de ficha completa
        self.ficha_tecnica_completa = porcentaje >= 80
        
        return porcentaje
    
    def tiene_ficha_tecnica(self):
        """Determina si el equipo tiene ficha técnica con datos significativos"""
        # Verificar si tiene al menos algunos campos técnicos completos
        campos_tecnicos = [
            self.numero_serie, self.voltaje, self.peso, self.amperaje, 
            self.temperatura_min, self.temperatura_max, self.epp_requerido,
            self.frecuencia_mantenimiento, self.ubicacion_especifica
        ]
        
        campos_completos = sum(1 for campo in campos_tecnicos if campo)
        
        # Si tiene al menos 2 campos técnicos completos, consideramos que tiene ficha
        return campos_completos >= 2

    def save(self, *args, **kwargs):
        # Actualizar completitud y estado de ficha al guardar
        completitud = self.calcular_completitud_ficha()
        # Cambiar la lógica: si tiene más del 30% de completitud O tiene datos técnicos significativos
        self.ficha_tecnica_completa = completitud >= 30 or self.tiene_ficha_tecnica()
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        
        # Solo validar si estamos en un contexto de ficha técnica
        # Remover la validación estricta por ahora
        
        # Comentar estas validaciones que están causando problemas
        # if not self.numero_serie:
        #     errors['numero_serie'] = 'El número de serie es requerido'
        # 
        # if not self.voltaje:
        #     errors['voltaje'] = 'El voltaje es requerido'
    
        if errors:
            raise ValidationError(errors)