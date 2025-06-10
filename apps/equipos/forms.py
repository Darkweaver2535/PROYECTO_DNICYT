from django import forms
from .models import Equipo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            # Campos básicos - solo incluir los necesarios para fichas técnicas
            'numero_serie', 'peso', 'voltaje', 'amperaje', 'fases', 
            'frecuencia', 'consumo_electrico', 'temperatura_min', 
            'temperatura_max', 'humedad_max', 'presion_trabajo', 
            'caudal_aire', 'epp_requerido', 'esquema_electrico', 
            'manual_operacion', 'frecuencia_mantenimiento', 
            'tiempo_mantenimiento', 'procedimientos_mantenimiento', 
            'ubicacion_especifica'
        ]
        
        widgets = {
            'numero_serie': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Número de serie del fabricante'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Peso en kg',
                'min': '0',
                'step': '0.01'
            }),
            'voltaje': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'amperaje': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Amperaje de operación'
            }),
            'fases': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'consumo_electrico': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Consumo eléctrico en kW',
                'min': '0',
                'step': '0.01'
            }),
            'temperatura_min': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Temperatura mínima de operación',
                'min': '-50',
                'max': '100'
            }),
            'temperatura_max': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Temperatura máxima de operación',
                'min': '-50',
                'max': '100'
            }),
            'humedad_max': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Humedad máxima permitida',
                'min': '0',
                'max': '100'
            }),
            'presion_trabajo': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Presión de trabajo en Bar',
                'min': '0',
                'step': '0.01'
            }),
            'caudal_aire': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Caudal de aire en L/min',
                'min': '0'
            }),
            'epp_requerido': forms.Textarea(attrs={
                'class': 'ficha-form-control ficha-form-textarea',
                'rows': 3,
                'placeholder': 'Equipos de protección personal requeridos'
            }),
            'esquema_electrico': forms.FileInput(attrs={
                'class': 'ficha-form-control'
            }),
            'manual_operacion': forms.FileInput(attrs={
                'class': 'ficha-form-control'
            }),
            'frecuencia_mantenimiento': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'tiempo_mantenimiento': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Tiempo estimado en horas',
                'min': '0',
                'step': '0.5'
            }),
            'procedimientos_mantenimiento': forms.Textarea(attrs={
                'class': 'ficha-form-control ficha-form-textarea',
                'rows': 4,
                'placeholder': 'Procedimientos detallados de mantenimiento'
            }),
            'ubicacion_especifica': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Ubicación específica del equipo'
            }),
        }

# Crear un formulario específico para fichas técnicas
class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            # Solo campos de ficha técnica
            'numero_serie', 'peso', 'voltaje', 'amperaje', 'fases', 
            'frecuencia', 'consumo_electrico', 'temperatura_min', 
            'temperatura_max', 'humedad_max', 'presion_trabajo', 
            'caudal_aire', 'epp_requerido', 'esquema_electrico', 
            'manual_operacion', 'frecuencia_mantenimiento', 
            'tiempo_mantenimiento', 'procedimientos_mantenimiento', 
            'ubicacion_especifica'
        ]
        
        widgets = {
            'numero_serie': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Número de serie del fabricante'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Peso en kg',
                'min': '0',
                'step': '0.01'
            }),
            'voltaje': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'amperaje': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Amperaje de operación'
            }),
            'fases': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'consumo_electrico': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Consumo eléctrico en kW',
                'min': '0',
                'step': '0.01'
            }),
            'temperatura_min': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Temperatura mínima de operación',
                'min': '-50',
                'max': '100'
            }),
            'temperatura_max': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Temperatura máxima de operación',
                'min': '-50',
                'max': '100'
            }),
            'humedad_max': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Humedad máxima permitida',
                'min': '0',
                'max': '100'
            }),
            'presion_trabajo': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Presión de trabajo en Bar',
                'min': '0',
                'step': '0.01'
            }),
            'caudal_aire': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Caudal de aire en L/min',
                'min': '0'
            }),
            'epp_requerido': forms.Textarea(attrs={
                'class': 'ficha-form-control ficha-form-textarea',
                'rows': 3,
                'placeholder': 'Equipos de protección personal requeridos'
            }),
            'esquema_electrico': forms.FileInput(attrs={
                'class': 'ficha-form-control'
            }),
            'manual_operacion': forms.FileInput(attrs={
                'class': 'ficha-form-control'
            }),
            'frecuencia_mantenimiento': forms.Select(attrs={
                'class': 'ficha-form-control ficha-form-select'
            }),
            'tiempo_mantenimiento': forms.NumberInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Tiempo estimado en horas',
                'min': '0',
                'step': '0.5'
            }),
            'procedimientos_mantenimiento': forms.Textarea(attrs={
                'class': 'ficha-form-control ficha-form-textarea',
                'rows': 4,
                'placeholder': 'Procedimientos detallados de mantenimiento'
            }),
            'ubicacion_especifica': forms.TextInput(attrs={
                'class': 'ficha-form-control',
                'placeholder': 'Ubicación específica del equipo'
            }),
        }