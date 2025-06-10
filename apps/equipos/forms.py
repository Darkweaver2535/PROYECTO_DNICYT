from django import forms
from .models import Equipo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante', 
            'año_fabricacion', 'potencia', 'capacidad', 'ubicacion_fisica', 
            'seccion', 'tipo_equipo', 'estado', 'responsable', 'observaciones',
            'udb_unidad', 'udb_numero'
        ]
        
        widgets = {
            'codigo_interno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: EQ-001, TOR-002'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo del equipo'
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabricante'
            }),
            'año_fabricacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2024',
                'min': '1900',
                'max': '2030'
            }),
            'potencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 220V, 1.5kW'
            }),
            'capacidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Capacidad del equipo'
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación física del equipo'
            }),
            'seccion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_equipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de equipo'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones adicionales'
            }),
            'udb_unidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'udb_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1-22386'
            }),
        }
        
        labels = {
            'codigo_interno': 'Código Interno',
            'nombre': 'Nombre del Equipo',
            'modelo': 'Modelo',
            'serie': 'Número de Serie',
            'fabricante': 'Fabricante',
            'año_fabricacion': 'Año de Fabricación',
            'potencia': 'Potencia',
            'capacidad': 'Capacidad',
            'ubicacion_fisica': 'Ubicación Física',
            'seccion': 'Sección',
            'tipo_equipo': 'Tipo de Equipo',
            'estado': 'Estado',
            'responsable': 'Responsable',
            'observaciones': 'Observaciones',
            'udb_unidad': 'Unidad EMI',
            'udb_numero': 'Número de Disposición',
        }