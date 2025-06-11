from django import forms
from .models import ProcedimientoOperativo
from apps.equipos.models import Equipo
from datetime import date, timedelta

class ProcedimientoOperativoForm(forms.ModelForm):
    class Meta:
        model = ProcedimientoOperativo
        exclude = ['creado_por', 'aprobado_por', 'fecha_aprobacion', 'numero_ejecuciones', 'eficiencia_promedio', 'codigo']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo del procedimiento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción breve del procedimiento'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'v1.0'
            }),
            'area': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable principal'
            }),
            'equipo_asociado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código del equipo (ej: SLD-001)'
            }),
            'equipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'normativa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'normativa_especifica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especificar si seleccionó "Otra normativa"'
            }),
            'tiempo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1440',
                'placeholder': 'Tiempo en minutos'
            }),
            'frecuencia_aplicacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_ultima_revision': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_proxima_revision': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'objetivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objetivo principal del procedimiento'
            }),
            'alcance': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Definir el alcance del procedimiento'
            }),
            'materiales_herramientas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Listar materiales y herramientas necesarios'
            }),
            'epp_requerido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Equipos de protección personal requeridos'
            }),
            'procedimiento_paso_a_paso': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describir el procedimiento paso a paso de manera detallada'
            }),
            'precauciones_seguridad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Precauciones y medidas de seguridad'
            }),
            'criterios_aceptacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Criterios para considerar el trabajo como aceptable'
            }),
            'registros_documentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Registros y documentos relacionados'
            }),
            'documento_pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'diagrama_flujo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'fotos_referencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'es_critico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_certificacion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para equipos
        self.fields['equipo'].queryset = Equipo.objects.filter(estado='OPERATIVO').order_by('codigo_interno')
        self.fields['equipo'].empty_label = "Seleccionar equipo (opcional)"
        
        # Configurar fechas por defecto para nuevos procedimientos
        if not self.instance.pk:
            self.fields['fecha_ultima_revision'].initial = date.today()
            self.fields['fecha_proxima_revision'].initial = date.today() + timedelta(days=365)
            self.fields['fecha_vencimiento'].initial = date.today() + timedelta(days=365)
            self.fields['version'].initial = 'v1.0'
        
        # Hacer obligatorios los campos esenciales
        self.fields['titulo'].required = True
        self.fields['descripcion'].required = True
        self.fields['area'].required = True
        self.fields['tipo'].required = True
        self.fields['responsable'].required = True
        self.fields['objetivo'].required = True
        self.fields['procedimiento_paso_a_paso'].required = True
        self.fields['fecha_ultima_revision'].required = True
        self.fields['fecha_proxima_revision'].required = True

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if not titulo or not titulo.strip():
            raise forms.ValidationError('El título del procedimiento es obligatorio.')
        if len(titulo.strip()) < 5:
            raise forms.ValidationError('El título debe tener al menos 5 caracteres.')
        return titulo.strip()

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if not descripcion or not descripcion.strip():
            raise forms.ValidationError('La descripción es obligatoria.')
        if len(descripcion.strip()) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
        return descripcion.strip()

    def clean_responsable(self):
        responsable = self.cleaned_data.get('responsable')
        if not responsable or not responsable.strip():
            raise forms.ValidationError('El responsable es obligatorio.')
        return responsable.strip()

    def clean_objetivo(self):
        objetivo = self.cleaned_data.get('objetivo')
        if not objetivo or not objetivo.strip():
            raise forms.ValidationError('El objetivo del procedimiento es obligatorio.')
        return objetivo.strip()

    def clean_procedimiento_paso_a_paso(self):
        procedimiento = self.cleaned_data.get('procedimiento_paso_a_paso')
        if not procedimiento or not procedimiento.strip():
            raise forms.ValidationError('El procedimiento paso a paso es obligatorio.')
        return procedimiento.strip()

    def clean(self):
        cleaned_data = super().clean()
        fecha_ultima = cleaned_data.get('fecha_ultima_revision')
        fecha_proxima = cleaned_data.get('fecha_proxima_revision')
        normativa = cleaned_data.get('normativa')
        normativa_especifica = cleaned_data.get('normativa_especifica')
        
        # Validar fechas
        if fecha_ultima and fecha_proxima:
            if fecha_proxima <= fecha_ultima:
                raise forms.ValidationError("La fecha de próxima revisión debe ser posterior a la última revisión.")
        
        # Validar normativa específica
        if normativa == 'otra' and not normativa_especifica:
            raise forms.ValidationError({
                'normativa_especifica': 'Debe especificar la normativa si seleccionó "Otra normativa".'
            })
        
        return cleaned_data