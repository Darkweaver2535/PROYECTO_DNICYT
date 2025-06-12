from django import forms
from .models import RegistroFalla, SeguimientoFalla
from apps.equipos.models import Equipo
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class RegistroFallaForm(forms.ModelForm):
    class Meta:
        model = RegistroFalla
        fields = [
            'equipo', 'descripcion_falla', 'fecha_ocurrencia', 'severidad', 
            'estado', 'tipo_falla', 'causa_inmediata', 'condiciones_operacion',
            'tiempo_parada', 'asignado_a', 'supervisor', 'observaciones',
            'foto_falla', 'requiere_seguimiento', 'fecha_seguimiento'
        ]
        
        widgets = {
            'equipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'descripcion_falla': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa detalladamente la falla observada...',
                'required': True
            }),
            'fecha_ocurrencia': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'severidad': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_falla': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'causa_inmediata': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa la causa inmediata identificada...'
            }),
            'condiciones_operacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Condiciones en las que operaba el equipo...'
            }),
            'tiempo_parada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Tiempo en horas'
            }),
            'asignado_a': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supervisor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del supervisor responsable'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'foto_falla': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'requiere_seguimiento': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fecha_seguimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para equipos (solo operativos y en mantenimiento)
        self.fields['equipo'].queryset = Equipo.objects.filter(
            estado__in=['OPERATIVO', 'MANTENIMIENTO']
        ).order_by('codigo_interno')
        self.fields['equipo'].empty_label = "Seleccionar equipo"
        
        # Configurar usuarios activos para asignación
        self.fields['asignado_a'].queryset = User.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
        self.fields['asignado_a'].empty_label = "Sin asignar"
        
        # Configurar fechas por defecto
        if not self.instance.pk:
            self.fields['fecha_ocurrencia'].initial = timezone.now()
            self.fields['estado'].initial = 'identificada'
            self.fields['severidad'].initial = 'media'
        
        # Hacer obligatorios los campos esenciales
        self.fields['equipo'].required = True
        self.fields['descripcion_falla'].required = True
        self.fields['fecha_ocurrencia'].required = True
        self.fields['severidad'].required = True
        self.fields['tipo_falla'].required = True

    def clean_fecha_ocurrencia(self):
        fecha = self.cleaned_data.get('fecha_ocurrencia')
        if fecha and fecha > timezone.now():
            raise forms.ValidationError('La fecha de ocurrencia no puede ser futura.')
        return fecha

    def clean_tiempo_parada(self):
        tiempo = self.cleaned_data.get('tiempo_parada')
        if tiempo is not None and tiempo < 0:
            raise forms.ValidationError('El tiempo de parada no puede ser negativo.')
        if tiempo is not None and tiempo > 168:  # Más de una semana
            raise forms.ValidationError('El tiempo de parada parece excesivo. Verifique el valor.')
        return tiempo

    def clean(self):
        cleaned_data = super().clean()
        requiere_seguimiento = cleaned_data.get('requiere_seguimiento')
        fecha_seguimiento = cleaned_data.get('fecha_seguimiento')
        
        # Si requiere seguimiento, debe tener fecha
        if requiere_seguimiento and not fecha_seguimiento:
            raise forms.ValidationError({
                'fecha_seguimiento': 'Debe especificar una fecha de seguimiento.'
            })
        
        # La fecha de seguimiento no puede ser pasada
        if fecha_seguimiento and fecha_seguimiento < date.today():
            raise forms.ValidationError({
                'fecha_seguimiento': 'La fecha de seguimiento debe ser hoy o futura.'
            })
        
        return cleaned_data

class SeguimientoFallaForm(forms.ModelForm):
    class Meta:
        model = SeguimientoFalla
        fields = [
            'tipo_accion', 'descripcion_accion', 'tiempo_empleado', 
            'costo_accion', 'resultado', 'observaciones'
        ]
        
        widgets = {
            'tipo_accion': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'descripcion_accion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa la acción realizada...',
                'required': True
            }),
            'tiempo_empleado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Tiempo en horas'
            }),
            'costo_accion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Costo en moneda local'
            }),
            'resultado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Resultado obtenido...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer obligatorios los campos esenciales
        self.fields['tipo_accion'].required = True
        self.fields['descripcion_accion'].required = True

    def clean_tiempo_empleado(self):
        tiempo = self.cleaned_data.get('tiempo_empleado')
        if tiempo is not None and tiempo < 0:
            raise forms.ValidationError('El tiempo empleado no puede ser negativo.')
        return tiempo

    def clean_costo_accion(self):
        costo = self.cleaned_data.get('costo_accion')
        if costo is not None and costo < 0:
            raise forms.ValidationError('El costo no puede ser negativo.')
        return costo