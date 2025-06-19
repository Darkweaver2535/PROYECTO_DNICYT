from django import forms
from .models import Material, CategoriaMaterial, MovimientoMaterial
from apps.inventario.models import Proveedor
from datetime import date, timedelta

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        exclude = ['codigo', 'fecha_creacion', 'fecha_actualizacion']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del material o herramienta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del producto'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'numero_parte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parte'
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras'
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'punto_reorden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'criticidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación en almacén'
            }),
            'proveedor_principal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'requiere_refrigeracion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_manejo_especial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'es_herramienta_critica': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_calibracion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fecha_ultima_calibracion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'frecuencia_calibracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Días entre calibraciones'
            }),
            'requiere_mantenimiento': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'fecha_ultimo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'frecuencia_mantenimiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Días entre mantenimientos'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultima_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ficha_tecnica': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para proveedores
        self.fields['proveedor_principal'].queryset = Proveedor.objects.filter(activo=True).order_by('nombre')
        self.fields['proveedor_principal'].empty_label = "Seleccionar proveedor (opcional)"
        
        # Configurar queryset para categorías
        self.fields['categoria'].queryset = CategoriaMaterial.objects.filter(activo=True).order_by('nombre')
        
        # Hacer obligatorios solo los campos esenciales
        self.fields['nombre'].required = True
        self.fields['descripcion'].required = True
        self.fields['tipo'].required = True
        self.fields['categoria'].required = True
        self.fields['estado'].required = True  # ✅ AGREGAR ESTA LÍNEA

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or not nombre.strip():
            raise forms.ValidationError('El nombre es obligatorio.')
        if len(nombre.strip()) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre.strip()

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if not descripcion or not descripcion.strip():
            raise forms.ValidationError('La descripción es obligatoria.')
        if len(descripcion.strip()) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
        return descripcion.strip()

    def clean(self):
        cleaned_data = super().clean()
        
        # Solo validar calibración si se requiere y se proporcionan datos
        requiere_calibracion = cleaned_data.get('requiere_calibracion')
        fecha_ultima_calibracion = cleaned_data.get('fecha_ultima_calibracion')
        frecuencia_calibracion = cleaned_data.get('frecuencia_calibracion')
        
        if requiere_calibracion and fecha_ultima_calibracion and frecuencia_calibracion:
            if fecha_ultima_calibracion > date.today():
                raise forms.ValidationError({
                    'fecha_ultima_calibracion': 'La fecha de última calibración no puede ser futura.'
                })
        
        return cleaned_data

class HerramientaForm(MaterialForm):
    """Formulario específico para herramientas (hereda de MaterialForm)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Eliminar el campo de fecha_vencimiento para herramientas
        if 'fecha_vencimiento' in self.fields:
            del self.fields['fecha_vencimiento']
        
        # Filtrar tipos solo para herramientas
        tipos_herramientas = [
            ('herramienta_manual', 'Herramienta Manual'),
            ('herramienta_electrica', 'Herramienta Eléctrica'),
            ('herramienta_precision', 'Herramienta de Precisión'),
            ('herramienta_soldadura', 'Herramienta de Soldadura'),
            ('herramienta_corte', 'Herramienta de Corte'),
            ('herramienta_medicion', 'Herramienta de Medición'),
            ('herramienta_seguridad', 'Herramienta de Seguridad'),
            ('instrumento_laboratorio', 'Instrumento de Laboratorio'),
            ('herramienta_neumatica', 'Herramienta Neumática'),
            ('herramienta_hidraulica', 'Herramienta Hidráulica'),
            ('equipo_calibracion', 'Equipo de Calibración'),
            ('instrumento_medicion_digital', 'Instrumento de Medición Digital'),
            ('herramienta_especial', 'Herramienta Especializada'),
        ]
        
        self.fields['tipo'].choices = tipos_herramientas
        
        # Actualizar las opciones de estado con estados más específicos para herramientas
        estados_herramientas = [
            ('disponible', 'Disponible'),
            ('en_uso', 'En Uso'),
            ('mantenimiento', 'En Mantenimiento'),
            ('calibracion', 'En Calibración'),
            ('defectuoso', 'Defectuoso'),
            ('quebrado', 'Quebrado/Roto'),
            ('desgastado', 'Desgastado'),
            ('obsoleto', 'Obsoleto'),
            ('prestado', 'Prestado'),
            ('extraviado', 'Extraviado'),
            ('descontinuado', 'Descontinuado'),
        ]
        
        self.fields['estado'].choices = estados_herramientas
        
        # Filtrar categorías solo para herramientas
        self.fields['categoria'].queryset = CategoriaMaterial.objects.filter(
            tipo_categoria__in=[
                'herramientas_manuales', 'herramientas_electricas', 'instrumentos_medicion',
                'herramientas_precision', 'herramientas_corte', 'equipos_laboratorio',
                'herramientas_soldadura_eq', 'herramientas_neumaticas', 'herramientas_hidraulicas',
                'instrumentos_calibracion', 'herramientas_seguridad', 'herramientas_especiales'
            ],
            activo=True
        ).order_by('nombre')

class MovimientoMaterialForm(forms.ModelForm):
    class Meta:
        model = MovimientoMaterial
        exclude = ['numero_movimiento', 'stock_anterior', 'stock_nuevo', 'usuario', 'costo_total']
        
        widgets = {
            'material': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'motivo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'costo_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'fecha_movimiento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'documento_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento o referencia'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para materiales
        self.fields['material'].queryset = Material.objects.filter(activo=True).order_by('nombre')
        
        # Hacer obligatorios los campos esenciales
        self.fields['material'].required = True
        self.fields['tipo_movimiento'].required = True
        self.fields['motivo'].required = True
        self.fields['cantidad'].required = True

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a cero.')
        return cantidad