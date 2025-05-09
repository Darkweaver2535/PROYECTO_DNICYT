# equipos/models.py
from django.db import models

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