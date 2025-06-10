from django import forms
from .models import Equipo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante',
            'año_fabricacion', 'potencia', 'capacidad', 'ubicacion_fisica',
            'seccion', 'tipo_equipo', 'estado', 'responsable', 'observaciones',
            'udb_unidad', 'udb_numero', 'foto'  # <-- Agregar este campo
        ]
        
        widgets = {
            'codigo_interno': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Ej: EQ-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Nombre del equipo'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Modelo del equipo'
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Número de serie'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Fabricante'
            }),
            'año_fabricacion': forms.NumberInput(attrs={
                'class': 'form-control edit-equipment-container',
                'min': '1900',
                'max': '2030'
            }),
            'potencia': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Ej: 220V, 1.5kW'
            }),
            'capacidad': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Capacidad del equipo'
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Ubicación física'
            }),
            'seccion': forms.Select(attrs={
                'class': 'form-select edit-equipment-container'
            }),
            'tipo_equipo': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Tipo de equipo'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select edit-equipment-container'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Responsable del equipo'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control edit-equipment-container',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'udb_unidad': forms.Select(attrs={
                'class': 'form-select edit-equipment-container'
            }),
            'udb_numero': forms.TextInput(attrs={
                'class': 'form-control edit-equipment-container',
                'placeholder': 'Ej: 1-22386'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control edit-equipment-container',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer obligatorios los campos esenciales
        self.fields['codigo_interno'].required = True
        self.fields['nombre'].required = True
        self.fields['seccion'].required = True
        self.fields['estado'].required = True

class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            # Información técnica básica
            'numero_serie', 'peso',
            # Especificaciones eléctricas
            'voltaje', 'amperaje', 'fases', 'frecuencia', 'consumo_electrico',
            # Condiciones de operación
            'temperatura_min', 'temperatura_max', 'humedad_max', 'presion_trabajo', 'caudal_aire',
            # Seguridad
            'epp_requerido',
            # Documentos
            'esquema_electrico', 'manual_operacion',
            # Mantenimiento
            'frecuencia_mantenimiento', 'tiempo_mantenimiento', 'procedimientos_mantenimiento',
            # Ubicación
            'ubicacion_especifica',
        ]
        
        widgets = {
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie del fabricante'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Peso en kilogramos'
            }),
            'voltaje': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amperaje': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 10A, 15-20A'
            }),
            'fases': forms.Select(attrs={
                'class': 'form-select'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'consumo_electrico': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Consumo en kW'
            }),
            'temperatura_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Temperatura mínima en °C'
            }),
            'temperatura_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Temperatura máxima en °C'
            }),
            'humedad_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Humedad máxima en %'
            }),
            'presion_trabajo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Presión en Bar'
            }),
            'caudal_aire': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Caudal en L/min'
            }),
            'epp_requerido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Equipos de protección personal requeridos'
            }),
            'esquema_electrico': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'manual_operacion': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'frecuencia_mantenimiento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tiempo_mantenimiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Tiempo en horas'
            }),
            'procedimientos_mantenimiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Procedimientos específicos de mantenimiento'
            }),
            'ubicacion_especifica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación específica del equipo'
            }),
        }