from django import forms
from .models import Material, MovimientoMaterial, CategoriaMaterial
from apps.inventario.models import Proveedor
from django.contrib.auth.models import User
from datetime import date

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        exclude = ['fecha_creacion', 'fecha_actualizacion', 'codigo', 'activo']
        widgets = {
            # Información básica
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo del material',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del material',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estado': forms.Select(attrs={  # <- AGREGAR ESTE WIDGET QUE FALTABA
                'class': 'form-select',
                'required': True
            }),
            'criticidad': forms.Select(attrs={  # <- AGREGAR ESTE WIDGET
                'class': 'form-select'
            }),
            
            # Identificación
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del material'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo o referencia específica'
            }),
            'numero_parte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parte del fabricante'
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras (opcional)'
            }),
            
            # Inventario
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0',
                'required': True
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '1',
                'required': True
            }),
            'stock_maximo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '100'
            }),
            'punto_reorden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '5'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0'
            }),
            
            # Ubicación y proveedor - CORREGIR ESTE WIDGET
            'ubicacion': forms.TextInput(attrs={  # <- CAMBIAR DE Textarea A TextInput
                'class': 'form-control',
                'placeholder': 'Ubicación específica en el almacén (ej: Estante A-3, Nivel 2)'
            }),
            'proveedor_principal': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            # Fechas importantes
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultima_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            
            # Características especiales
            'requiere_refrigeracion': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_requiere_refrigeracion'
            }),
            'requiere_manejo_especial': forms.CheckboxInput(attrs={
                'class': 'form-check-input', 
                'id': 'id_requiere_manejo_especial'
            }),
            
            # Documentos
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ficha_tecnica': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para categorías
        self.fields['categoria'].queryset = CategoriaMaterial.objects.filter(
            activo=True
        ).order_by('nombre')
        self.fields['categoria'].empty_label = "Seleccionar categoría"
        
        # Configurar queryset para proveedores
        self.fields['proveedor_principal'].queryset = Proveedor.objects.filter(
            activo=True
        ).order_by('nombre')
        self.fields['proveedor_principal'].empty_label = "Seleccionar proveedor (opcional)"
        
        # CAMBIAR ESTA LÍNEA - quitar 'criticidad' de los campos obligatorios
        campos_obligatorios = ['nombre', 'descripcion', 'tipo', 'categoria', 'stock_actual', 'stock_minimo', 'unidad_medida', 'estado']
        
        for campo in campos_obligatorios:
            if campo in self.fields:
                self.fields[campo].required = True
        
        # Configurar valores por defecto SOLO para nuevos materiales
        if not self.instance.pk:
            self.fields['stock_actual'].initial = 0
            self.fields['stock_minimo'].initial = 1
            self.fields['stock_maximo'].initial = 100
            self.fields['punto_reorden'].initial = 5
            self.fields['precio_unitario'].initial = 0
            self.fields['criticidad'].initial = 'media'  # <- MANTENER ESTE DEFAULT
            self.fields['estado'].initial = 'disponible'

    def clean_estado(self):  # <- AGREGAR VALIDACIÓN PARA ESTADO
        estado = self.cleaned_data.get('estado')
        if not estado:
            raise forms.ValidationError('El estado del material es obligatorio.')
        return estado

    def clean_ubicacion(self):  # <- AGREGAR VALIDACIÓN PARA UBICACIÓN
        ubicacion = self.cleaned_data.get('ubicacion')
        # La ubicación puede ser opcional, pero si se proporciona debe ser válida
        if ubicacion:
            ubicacion = ubicacion.strip()
            if len(ubicacion) < 3:
                raise forms.ValidationError('La ubicación debe tener al menos 3 caracteres.')
            return ubicacion
        return ubicacion  # Puede ser None o vacío

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError('El nombre del material es obligatorio.')
        nombre = nombre.strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if not descripcion:
            raise forms.ValidationError('La descripción es obligatoria.')
        descripcion = descripcion.strip()
        if len(descripcion) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
        return descripcion

    def clean_stock_actual(self):
        stock = self.cleaned_data.get('stock_actual')
        if stock is None:
            return 0  # Valor por defecto
        if stock < 0:
            raise forms.ValidationError('El stock actual no puede ser negativo.')
        return stock

    def clean_stock_minimo(self):
        stock_min = self.cleaned_data.get('stock_minimo')
        if stock_min is None:
            return 1  # Valor por defecto
        if stock_min < 0:
            raise forms.ValidationError('El stock mínimo no puede ser negativo.')
        return stock_min

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is None:
            return 0  # Valor por defecto
        if precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean(self):
        cleaned_data = super().clean()
        
        # Debug para ver qué datos llegan
        print(f"DEBUG FORM: cleaned_data = {cleaned_data}")
        
        stock_actual = cleaned_data.get('stock_actual', 0)
        stock_minimo = cleaned_data.get('stock_minimo', 1)
        stock_maximo = cleaned_data.get('stock_maximo')
        punto_reorden = cleaned_data.get('punto_reorden', 5)
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        # Validar lógica de stocks solo si tenemos valores
        if stock_minimo and stock_maximo and stock_maximo <= stock_minimo:
            raise forms.ValidationError({
                'stock_maximo': 'El stock máximo debe ser mayor al stock mínimo.'
            })
        
        if punto_reorden and stock_minimo and punto_reorden > stock_minimo:
            raise forms.ValidationError({
                'punto_reorden': 'El punto de reorden no puede ser mayor al stock mínimo.'
            })
        
        # Validar fecha de vencimiento
        if fecha_vencimiento and fecha_vencimiento <= date.today():
            raise forms.ValidationError({
                'fecha_vencimiento': 'La fecha de vencimiento debe ser posterior a hoy.'
            })
        
        return cleaned_data

class MovimientoMaterialForm(forms.ModelForm):
    class Meta:
        model = MovimientoMaterial
        exclude = ['numero_movimiento', 'usuario', 'stock_anterior', 'stock_nuevo']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'costo_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fecha_movimiento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }