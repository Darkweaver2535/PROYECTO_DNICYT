from django import forms
from django.contrib.auth.models import User
from .models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico
from apps.equipos.models import Equipo

class PlanMantenimientoForm(forms.ModelForm):
    class Meta:
        model = PlanMantenimiento
        fields = [
            # Información básica
            'nombre', 'descripcion', 'equipo', 
            # Tipo y frecuencia
            'tipo_mantenimiento', 'frecuencia', 'duracion_estimada',
            # Prioridad y estado
            'prioridad', 'estado', 'nivel_criticidad',
            # Responsables
            'responsable_principal', 'responsables_secundarios',
            # Fechas
            'fecha_inicio',
            # Costos
            'costo_estimado',
            # Documentos
            'procedimiento_documento', 'lista_verificacion',
            # Control de calidad
            'requiere_parada_equipo', 'herramientas_especiales', 'materiales_requeridos',
            # Repuestos críticos
            'repuestos_criticos',
            # Normativas técnicas
            'norma_aplicable', 'norma_especifica',
            # Cumplimiento normativo
            'cumple_iso', 'cumple_api', 'cumple_asme', 'certificacion_vigente', 'fecha_ultima_auditoria',
            # Análisis de fallas
            'mtbf', 'mttr', 'disponibilidad_objetivo',
            # Observaciones
            'observaciones'
        ]
        
        widgets = {
            # Información básica
            'nombre': forms.TextInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Ej: Mantenimiento preventivo bomba centrífuga BP-001'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Descripción detallada del plan de mantenimiento según normativas ISO 55000'
            }),
            'equipo': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            
            # Tipo y frecuencia
            'tipo_mantenimiento': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'duracion_estimada': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Horas estimadas',
                'min': '0.1',
                'step': '0.5'
            }),
            
            # Prioridad y estado
            'prioridad': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'nivel_criticidad': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            
            # Responsables
            'responsable_principal': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'responsables_secundarios': forms.SelectMultiple(attrs={
                'class': 'plan-form-control plan-form-select-multiple',
                'size': '4'
            }),
            
            # Fechas
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'plan-form-control',
                'type': 'date'
            }),
            'fecha_ultima_auditoria': forms.DateInput(attrs={
                'class': 'plan-form-control',
                'type': 'date'
            }),
            
            # Costos
            'costo_estimado': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Costo estimado en Bs.',
                'min': '0',
                'step': '0.01'
            }),
            
            # Documentos
            'procedimiento_documento': forms.FileInput(attrs={
                'class': 'plan-form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'lista_verificacion': forms.FileInput(attrs={
                'class': 'plan-form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            
            # Control de calidad
            'requiere_parada_equipo': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'herramientas_especiales': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Ej: Llave de torque 50-100 Nm, Multímetro Fluke 87V, Analizador de vibraciones'
            }),
            'materiales_requeridos': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Ej: Aceite hidráulico ISO VG 46, Filtros de aire, Sellos mecánicos'
            }),
            
            # Repuestos críticos
            'repuestos_criticos': forms.SelectMultiple(attrs={
                'class': 'plan-form-control plan-form-select-multiple',
                'size': '6'
            }),
            
            # Normativas técnicas
            'norma_aplicable': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'norma_especifica': forms.TextInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Especificar norma si seleccionó "Otra norma específica"'
            }),
            
            # Cumplimiento normativo
            'cumple_iso': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'cumple_api': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'cumple_asme': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'certificacion_vigente': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            
            # Análisis de fallas
            'mtbf': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Tiempo medio entre fallas (horas)',
                'min': '0',
                'step': '0.1'
            }),
            'mttr': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Tiempo medio de reparación (horas)',
                'min': '0',
                'step': '0.1'
            }),
            'disponibilidad_objetivo': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': '95.0',
                'min': '0',
                'max': '100',
                'step': '0.1'
            }),
            
            # Observaciones
            'observaciones': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 4,
                'placeholder': 'Observaciones adicionales, consideraciones especiales, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios activos para responsables
        self.fields['responsable_principal'].queryset = User.objects.filter(is_active=True)
        self.fields['responsables_secundarios'].queryset = User.objects.filter(is_active=True)
        # Filtrar equipos activos
        self.fields['equipo'].queryset = Equipo.objects.exclude(estado='FUERA_SERVICIO')
        # Cargar repuestos críticos
        self.fields['repuestos_criticos'].queryset = RepuestoCritico.objects.all()
        
        # Configurar campos requeridos
        self.fields['nombre'].required = True
        self.fields['equipo'].required = True
        self.fields['tipo_mantenimiento'].required = True
        self.fields['frecuencia'].required = True
        self.fields['duracion_estimada'].required = True
        self.fields['fecha_inicio'].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validación de norma específica
        norma_aplicable = cleaned_data.get('norma_aplicable')
        norma_especifica = cleaned_data.get('norma_especifica')
        
        if norma_aplicable == 'otra' and not norma_especifica:
            raise forms.ValidationError({
                'norma_especifica': 'Debe especificar la norma si seleccionó "Otra norma específica"'
            })
        
        # Validación de MTBF y MTTR
        mtbf = cleaned_data.get('mtbf')
        mttr = cleaned_data.get('mttr')
        
        if mtbf and mttr and mttr >= mtbf:
            raise forms.ValidationError({
                'mttr': 'El MTTR debe ser menor que el MTBF'
            })
        
        return cleaned_data


class TareaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TareaMantenimiento
        fields = [
            'nombre', 'descripcion', 'orden', 'duracion_estimada',
            'es_critica', 'requiere_verificacion', 'responsable',
            'instrucciones', 'herramientas_necesarias'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Nombre de la tarea'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 2,
                'placeholder': 'Descripción de la tarea'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'min': '1'
            }),
            'duracion_estimada': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Minutos',
                'min': '1'
            }),
            'es_critica': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'requiere_verificacion': forms.CheckboxInput(attrs={
                'class': 'plan-form-check'
            }),
            'responsable': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'instrucciones': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Instrucciones específicas para esta tarea'
            }),
            'herramientas_necesarias': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 2,
                'placeholder': 'Herramientas específicas para esta tarea'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].queryset = User.objects.filter(is_active=True)