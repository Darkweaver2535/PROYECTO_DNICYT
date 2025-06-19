from django import forms
from django.contrib.auth.models import User
from .models import PlanMantenimiento, TareaMantenimiento, RepuestoCritico, OrdenTrabajo
from apps.equipos.models import Equipo

class PlanMantenimientoForm(forms.ModelForm):
    class Meta:
        model = PlanMantenimiento
        fields = [
            # Información básica
            'nombre', 'descripcion', 'equipo', 
            # Tipo y frecuencia
            'tipo_mantenimiento', 'frecuencia', 'duracion_estimada_rango',
            # Prioridad y estado
            'prioridad', 'estado', 
            # Responsables
            'responsable_principal', 'responsables_secundarios',
            # Fechas
            'fecha_inicio',
            # Costos
            'costo_estimado',
            # Documentos
            'procedimiento_documento', 'lista_verificacion',
            # Control de calidad
            'requiere_parada_equipo', 'materiales_requeridos',
            # Normativas técnicas (simplificado)
            'norma_aplicable', 'norma_especifica',
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
            'duracion_estimada_rango': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select',
                'required': True
            }),
            
            # Prioridad y estado
            'prioridad': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'estado': forms.Select(attrs={
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
            'materiales_requeridos': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Ej: Aceite hidráulico ISO VG 46, Filtros de aire, Sellos mecánicos'
            }),
            
            # Normativas técnicas
            'norma_aplicable': forms.Select(attrs={
                'class': 'plan-form-control plan-form-select'
            }),
            'norma_especifica': forms.TextInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Especificar norma si seleccionó "Otra norma específica"'
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
        
        # *** CORRECCIÓN: Filtrar equipos correctamente ***
        from apps.equipos.models import Equipo
        # Mostrar todos los equipos excepto los fuera de servicio
        self.fields['equipo'].queryset = Equipo.objects.exclude(estado='FUERA_SERVICIO').order_by('codigo_interno')
        
        # Mejorar el display del equipo en el select
        self.fields['equipo'].empty_label = "Seleccione un equipo..."
        
        # Configurar campos requeridos
        self.fields['nombre'].required = True
        self.fields['equipo'].required = True
        self.fields['tipo_mantenimiento'].required = True
        self.fields['frecuencia'].required = True
        self.fields['duracion_estimada_rango'].required = True
        self.fields['fecha_inicio'].required = True
        
        # *** MEJORAR LOS WIDGETS PARA MEJOR EXPERIENCIA ***
        self.fields['equipo'].widget.attrs.update({
            'class': 'plan-form-control plan-form-select',
            'data-placeholder': 'Buscar equipo por código o nombre...'
        })

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
        
        # Validación específica para mantenimiento correctivo
        tipo_mantenimiento = cleaned_data.get('tipo_mantenimiento')
        requiere_parada = cleaned_data.get('requiere_parada_equipo')
        
        if tipo_mantenimiento == 'correctivo' and not requiere_parada:
            # Forzar el valor a True para mantenimiento correctivo
            cleaned_data['requiere_parada_equipo'] = True
        
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


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = [
            'titulo', 'descripcion', 'equipo', 'plan_mantenimiento',
            'tipo_orden', 'prioridad', 'asignado_a', 'supervisado_por',
            'fecha_programada', 'fecha_fin_programada', 'horas_estimadas',
            'costo_estimado', 'materiales_necesarios', 'herramientas_necesarias',
            'procedimientos_seguir', 'observaciones_iniciales', 'requiere_pruebas',
            'documentos_adjuntos', 'fotos_antes'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo de la orden de trabajo'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del trabajo a realizar'
            }),
            'equipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'plan_mantenimiento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_orden': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'asignado_a': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supervisado_por': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_fin_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'horas_estimadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'costo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'materiales_necesarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista de materiales necesarios'
            }),
            'herramientas_necesarias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Herramientas requeridas para el trabajo'
            }),
            'procedimientos_seguir': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Procedimientos y pasos a seguir'
            }),
            'observaciones_iniciales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones iniciales importantes'
            }),
            'requiere_pruebas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'documentos_adjuntos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
            'fotos_antes': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar equipos operativos
        self.fields['equipo'].queryset = Equipo.objects.exclude(estado='FUERA_SERVICIO')
        
        # Filtrar planes activos
        self.fields['plan_mantenimiento'].queryset = PlanMantenimiento.objects.filter(estado='activo')
        self.fields['plan_mantenimiento'].required = False
        
        # Filtrar usuarios activos para asignación
        self.fields['asignado_a'].queryset = User.objects.filter(is_active=True)
        self.fields['supervisado_por'].queryset = User.objects.filter(is_active=True)
        
        # Campos no requeridos
        self.fields['asignado_a'].required = False
        self.fields['supervisado_por'].required = False


class OrdenTrabajoUpdateForm(forms.ModelForm):
    """Formulario para actualizar el progreso de una orden de trabajo"""
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'estado', 'fecha_inicio_real', 'horas_reales', 'costo_real',
            'trabajo_realizado', 'observaciones_finales', 'repuestos_utilizados',
            'pruebas_realizadas', 'resultado_satisfactorio', 'fotos_despues',
            'comentarios_adicionales', 'requiere_seguimiento', 'fecha_proximo_seguimiento',
            'calificacion_trabajo'
        ]
        
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio_real': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'horas_reales': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'costo_real': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'trabajo_realizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del trabajo realizado'
            }),
            'observaciones_finales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones finales y recomendaciones'
            }),
            'repuestos_utilizados': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista de repuestos utilizados'
            }),
            'pruebas_realizadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de las pruebas realizadas'
            }),
            'resultado_satisfactorio': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fotos_despues': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'comentarios_adicionales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comentarios adicionales'
            }),
            'requiere_seguimiento': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fecha_proximo_seguimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'calificacion_trabajo': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializaciones específicas si es necesario


class CompletarMantenimientoForm(forms.ModelForm):
    class Meta:
        model = PlanMantenimiento
        fields = ['duracion_real', 'observaciones']
        
        widgets = {
            'duracion_real': forms.NumberInput(attrs={
                'class': 'plan-form-control',
                'placeholder': 'Horas reales',
                'min': '0.1',
                'step': '0.1',
                'required': True
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'plan-form-control plan-form-textarea',
                'rows': 3,
                'placeholder': 'Observaciones sobre la ejecución del mantenimiento'
            }),
        }