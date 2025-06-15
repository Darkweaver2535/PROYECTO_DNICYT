from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    NormativaSeguridad, CategoriaSeguridad, InspeccionSeguridad,
    IncidenteSeguridad, CapacitacionSeguridad
)

class NormativaSeguridadForm(forms.ModelForm):
    """Formulario para crear/editar normativas de seguridad"""
    
    class Meta:
        model = NormativaSeguridad
        fields = [
            'titulo', 'descripcion', 'tipo', 'categoria', 'prioridad', 'ambito_aplicacion',
            'contenido', 'objetivos', 'alcance', 'responsabilidades', 'procedimientos',
            'recursos_necesarios', 'archivo_principal', 'imagen_referencia',
            'version', 'fecha_vigencia_inicio',
            'fecha_vigencia_fin', 'frecuencia_revision', 'estado', 'es_obligatoria',
            'requiere_capacitacion', 'requiere_evaluacion', 'palabras_clave',
            'normativas_relacionadas'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'normativa-form-control',
                'placeholder': 'Título de la normativa de seguridad'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 4,
                'placeholder': 'Descripción general de la normativa...'
            }),
            'tipo': forms.Select(attrs={'class': 'normativa-form-select'}),
            'categoria': forms.Select(attrs={'class': 'normativa-form-select'}),
            'prioridad': forms.Select(attrs={'class': 'normativa-form-select'}),
            'ambito_aplicacion': forms.Select(attrs={'class': 'normativa-form-select'}),
            'contenido': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 8,
                'placeholder': 'Contenido detallado de la normativa...'
            }),
            'objetivos': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 3,
                'placeholder': 'Un objetivo por línea...'
            }),
            'alcance': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 3,
                'placeholder': 'Alcance y aplicabilidad...'
            }),
            'responsabilidades': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 4,
                'placeholder': 'Responsabilidades por área/cargo...'
            }),
            'procedimientos': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 5,
                'placeholder': 'Pasos específicos a seguir...'
            }),
            'recursos_necesarios': forms.Textarea(attrs={
                'class': 'normativa-form-control',
                'rows': 3,
                'placeholder': 'EPP, herramientas, equipos necesarios...'
            }),
            'archivo_principal': forms.FileInput(attrs={
                'class': 'normativa-form-control',
                'accept': '.pdf,.docx,.doc'
            }),
            'imagen_referencia': forms.FileInput(attrs={
                'class': 'normativa-form-control',
                'accept': 'image/*'
            }),
            'version': forms.TextInput(attrs={
                'class': 'normativa-form-control',
                'placeholder': '1.0'
            }),
            'fecha_vigencia_inicio': forms.DateInput(attrs={
                'class': 'normativa-form-control',
                'type': 'date'
            }),
            'fecha_vigencia_fin': forms.DateInput(attrs={
                'class': 'normativa-form-control',
                'type': 'date'
            }),
            'frecuencia_revision': forms.NumberInput(attrs={
                'class': 'normativa-form-control',
                'min': 30,
                'max': 1095,
                'value': 365
            }),
            'estado': forms.Select(attrs={'class': 'normativa-form-select'}),
            'es_obligatoria': forms.CheckboxInput(attrs={'class': 'normativa-form-check'}),
            'requiere_capacitacion': forms.CheckboxInput(attrs={'class': 'normativa-form-check'}),
            'requiere_evaluacion': forms.CheckboxInput(attrs={'class': 'normativa-form-check'}),
            'palabras_clave': forms.TextInput(attrs={
                'class': 'normativa-form-control',
                'placeholder': 'palabra1, palabra2, palabra3...'
            }),
            'normativas_relacionadas': forms.SelectMultiple(attrs={
                'class': 'normativa-form-select-multiple',
                'size': 5
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar categorías activas
        self.fields['categoria'].queryset = CategoriaSeguridad.objects.filter(
            activo=True
        ).order_by('orden', 'nombre')
        
        # Filtrar normativas relacionadas (excluir la actual si está editando)
        normativas_qs = NormativaSeguridad.objects.filter(estado='vigente')
        if self.instance.pk:
            normativas_qs = normativas_qs.exclude(pk=self.instance.pk)
        self.fields['normativas_relacionadas'].queryset = normativas_qs
        
        self.fields['categoria'].empty_label = "-- Seleccione una categoría --"
        
        # Establecer fecha de vigencia por defecto
        if not self.instance.pk:
            self.fields['fecha_vigencia_inicio'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_vigencia_inicio')
        fecha_fin = cleaned_data.get('fecha_vigencia_fin')
        
        # Validar fechas
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise ValidationError({
                    'fecha_vigencia_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
        
        return cleaned_data

class CategoriaSeguridadForm(forms.ModelForm):
    """Formulario para categorías de seguridad"""
    
    class Meta:
        model = CategoriaSeguridad
        fields = ['nombre', 'descripcion', 'color_hex', 'icono', 'orden', 'es_critica', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'color_hex': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bi-shield-exclamation'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'es_critica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FiltrosNormativasForm(forms.Form):
    """Formulario para filtros de normativas"""
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar normativas...'
        })
    )
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaSeguridad.objects.filter(activo=True),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + NormativaSeguridad.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    prioridad = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + NormativaSeguridad.PRIORIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + NormativaSeguridad.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class InspeccionSeguridadForm(forms.ModelForm):
    """Formulario para inspecciones de seguridad"""
    
    class Meta:
        model = InspeccionSeguridad
        fields = [
            'normativa', 'tipo_inspeccion', 'area_inspeccionada', 'resultado',
            'puntuacion', 'observaciones', 'acciones_correctivas',
            'fecha_limite_correccion', 'fotos_evidencia'
        ]
        
        widgets = {
            'normativa': forms.Select(attrs={'class': 'form-select'}),
            'tipo_inspeccion': forms.Select(attrs={'class': 'form-select'}),
            'area_inspeccionada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área donde se realizó la inspección'
            }),
            'resultado': forms.Select(attrs={'class': 'form-select'}),
            'puntuacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones y hallazgos...'
            }),
            'acciones_correctivas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Acciones correctivas requeridas...'
            }),
            'fecha_limite_correccion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fotos_evidencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.pdf'
            }),
        }

class IncidenteSeguridadForm(forms.ModelForm):
    """Formulario para reportar incidentes"""
    
    class Meta:
        model = IncidenteSeguridad
        fields = [
            'fecha_incidente', 'tipo_incidente', 'gravedad', 'area_afectada',
            'descripcion_lugar', 'personas_involucradas', 'testigos',
            'descripcion_incidente', 'causas_inmediatas', 'acciones_inmediatas',
            'normativas_incumplidas', 'fotos_evidencia'
        ]
        
        widgets = {
            'fecha_incidente': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo_incidente': forms.Select(attrs={'class': 'form-select'}),
            'gravedad': forms.Select(attrs={'class': 'form-select'}),
            'area_afectada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área donde ocurrió el incidente'
            }),
            'descripcion_lugar': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción detallada del lugar...'
            }),
            'personas_involucradas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nombres y roles de personas involucradas...'
            }),
            'testigos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Nombres de testigos...'
            }),
            'descripcion_incidente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descripción detallada del incidente...'
            }),
            'causas_inmediatas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Causas inmediatas identificadas...'
            }),
            'acciones_inmediatas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Acciones inmediatas tomadas...'
            }),
            'normativas_incumplidas': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'fotos_evidencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
        }

class CapacitacionSeguridadForm(forms.ModelForm):
    """Formulario para capacitaciones de seguridad"""
    
    class Meta:
        model = CapacitacionSeguridad
        fields = [
            'titulo', 'descripcion', 'normativas_cubiertas', 'fecha_inicio',
            'fecha_fin', 'modalidad', 'lugar', 'instructor', 'max_participantes',
            'es_obligatoria', 'certificacion', 'material_capacitacion'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la capacitación'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la capacitación...'
            }),
            'normativas_cubiertas': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 6
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de la capacitación'
            }),
            'instructor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del instructor'
            }),
            'max_participantes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 20
            }),
            'es_obligatoria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'certificacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'material_capacitacion': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.pptx'
            }),
        }