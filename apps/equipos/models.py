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

    codigo_interno = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100)
    serie = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100)
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
    responsable = models.CharField(max_length=100)
    observaciones = models.TextField(null=True, blank=True)
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
        help_text="Ejemplo: 1-22386",
        validators=[
            RegexValidator(
                regex=r'^\d-\d{5}$',
                message='El número debe tener el formato 1-12345 (un dígito, guion, cinco dígitos)'
            )
        ]
    )

    def __str__(self):
        return f"{self.codigo_interno} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('equipos:equipo-detalle', kwargs={'pk': self.pk})