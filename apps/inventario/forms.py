from django import forms
from .models import Repuesto, CategoriaRepuesto, Proveedor, MovimientoStock
from django.contrib.auth.models import User
from datetime import date

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        exclude = [
            'creado_por', 'fecha_creacion', 'fecha_actualizacion', 'activo', 'codigo',
            'precio_promedio', 'costo_ultima_compra'  # EXCLUIR ESTOS CAMPOS PROBLEMÁTICOS
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del repuesto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del repuesto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'codigo_activo_iso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código ISO 14224 (opcional)'
            }),
            'seccion_trabajo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'aplicacion_principal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Aplicación principal del repuesto'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fabricante del repuesto'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'codigo_fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código del fabricante'
            }),
            'numero_parte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parte'
            }),
            'material_construccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Material de construcción'
            }),
            'dimensiones': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dimensiones (ej: 100x50x25 mm)'
            }),
            'peso_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Peso en kg'
            }),
            'especificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Especificaciones técnicas'
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
            'stock_seguridad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0'
            }),
            'costo_almacenamiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'value': '0'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-select'
            }),
            'criticidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'proveedor_principal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tiempo_entrega': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Días de entrega'
            }),
            'responsable_tecnico': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsable_almacen': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ubicacion_almacen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación en almacén'
            }),
            'pasillo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pasillo'
            }),
            'estante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estante'
            }),
            'nivel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nivel'
            }),
            'bin_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación bin (ej: A1-B2-C3)'
            }),
            'normas_aplicables': forms.Select(attrs={
                'class': 'form-select'
            }),
            'certificaciones_requeridas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Certificaciones requeridas'
            }),
            'es_consumible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'es_activo_critico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_refrigeracion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requiere_manejo_especial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'vida_util_estimada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Días de vida útil'
            }),
            'frecuencia_uso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Frecuencia de uso'
            }),
            'condiciones_almacenamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Condiciones especiales de almacenamiento'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultima_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultimo_uso': forms.DateInput(attrs={
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
            'certificado_calidad': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,image/*'
            }),
            'msds': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
            'notas_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas técnicas específicas'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar opciones para proveedores
        self.fields['proveedor_principal'].queryset = Proveedor.objects.filter(activo=True)
        self.fields['proveedor_principal'].empty_label = "Seleccionar proveedor..."
        
        # Configurar opciones para responsables
        usuarios_activos = User.objects.filter(is_active=True)
        self.fields['responsable_tecnico'].queryset = usuarios_activos
        self.fields['responsable_tecnico'].empty_label = "Seleccionar responsable..."
        self.fields['responsable_almacen'].queryset = usuarios_activos
        self.fields['responsable_almacen'].empty_label = "Seleccionar responsable..."
        
        # Configurar categorías
        self.fields['categoria'].queryset = CategoriaRepuesto.objects.filter(activo=True)
        
        # CONFIGURAR CHOICES PARA NORMAS APLICABLES
        NORMAS_CHOICES = [
            ('', 'Seleccionar norma...'),
            ('ISO 9001:2015', 'ISO 9001:2015 - Sistema de Gestión de Calidad'),
            ('ISO 45001:2018', 'ISO 45001:2018 - Seguridad y Salud Ocupacional'),
            ('ISO 14001:2015', 'ISO 14001:2015 - Gestión Ambiental'),
            ('AWS D1.1', 'AWS D1.1 - Código de Soldadura Estructural - Acero'),
            ('AWS D1.6', 'AWS D1.6 - Código de Soldadura Estructural - Acero Inoxidable'),
            ('ASME BPVC', 'ASME BPVC - Código de Calderas y Recipientes a Presión'),
            ('ASME B31.3', 'ASME B31.3 - Código de Tuberías de Proceso'),
            ('ASTM A36', 'ASTM A36 - Especificación para Acero Estructural de Carbono'),
            ('ASTM A240', 'ASTM A240 - Especificación para Planchas de Acero Inoxidable'),
            ('ASTM A48', 'ASTM A48 - Especificación para Fundición de Hierro Gris'),
            ('ASTM A536', 'ASTM A536 - Especificación para Fundición de Hierro Dúctil'),
            ('ISO 17025:2017', 'ISO 17025:2017 - Competencia de Laboratorios de Ensayo'),
            ('ISO 55000:2014', 'ISO 55000:2014 - Gestión de Activos'),
            ('API 570', 'API 570 - Inspección de Tuberías en Servicio'),
            ('API 580', 'API 580 - Inspección Basada en Riesgo'),
            ('NORSOK Z-008', 'NORSOK Z-008 - Análisis de Criticidad y Riesgo'),
            ('OSHA 1910.146', 'OSHA 1910.146 - Espacios Confinados'),
            ('ANSI/AISC 360', 'ANSI/AISC 360 - Especificación para Construcciones de Acero'),
            ('DIN EN 1090', 'DIN EN 1090 - Ejecución de Estructuras de Acero'),
            ('otra', 'Otra norma específica'),
        ]
        
        self.fields['normas_aplicables'].widget = forms.Select(choices=NORMAS_CHOICES, attrs={
            'class': 'form-select'
        })
        
        # Hacer campos opcionales
        self.fields['stock_seguridad'].required = False
        self.fields['costo_almacenamiento'].required = False
        self.fields['codigo_activo_iso'].required = False
        self.fields['aplicacion_principal'].required = False
        
        # Campos realmente obligatorios
        self.fields['nombre'].required = True
        self.fields['descripcion'].required = True
        self.fields['categoria'].required = True
        self.fields['stock_actual'].required = True
        self.fields['stock_minimo'].required = True
        self.fields['precio_unitario'].required = True

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is None or precio < 0:
            raise forms.ValidationError('El precio unitario debe ser mayor o igual a 0.')
        return precio

    def clean_stock_seguridad(self):
        """Asegurar que stock_seguridad tenga un valor por defecto"""
        stock_seguridad = self.cleaned_data.get('stock_seguridad')
        if stock_seguridad is None:
            return 0
        return stock_seguridad

    def clean_costo_almacenamiento(self):
        """Asegurar que costo_almacenamiento tenga un valor por defecto"""
        costo_almacenamiento = self.cleaned_data.get('costo_almacenamiento')
        if costo_almacenamiento is None:
            return 0
        return costo_almacenamiento

    def clean(self):
        cleaned_data = super().clean()
        
        # Validación de stocks
        stock_actual = cleaned_data.get('stock_actual')
        stock_minimo = cleaned_data.get('stock_minimo')
        stock_maximo = cleaned_data.get('stock_maximo')
        punto_reorden = cleaned_data.get('punto_reorden')
        
        if stock_actual is not None and stock_minimo is not None:
            if stock_actual < 0:
                self.add_error('stock_actual', 'El stock actual no puede ser negativo.')
            
            if stock_minimo < 0:
                self.add_error('stock_minimo', 'El stock mínimo no puede ser negativo.')
            
            if stock_maximo and stock_maximo < stock_minimo:
                self.add_error('stock_maximo', 'El stock máximo debe ser mayor o igual al stock mínimo.')
            
            if punto_reorden and punto_reorden < stock_minimo:
                self.add_error('punto_reorden', 'El punto de reorden debe ser mayor o igual al stock mínimo.')
        
        # Asegurar valores por defecto para campos problemáticos
        if not cleaned_data.get('stock_seguridad'):
            cleaned_data['stock_seguridad'] = 0
        
        if not cleaned_data.get('costo_almacenamiento'):
            cleaned_data['costo_almacenamiento'] = 0
        
        return cleaned_data

class CategoriaRepuestoForm(forms.ModelForm):
    class Meta:
        model = CategoriaRepuesto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único'
            }),
            'tipo_categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seccion_aplicable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sección aplicable'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        exclude = ['codigo', 'fecha_registro', 'fecha_actualizacion', 'total_ordenes', 
                  'total_comprado', 'porcentaje_cumplimiento']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Razón social completa'
            }),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial (opcional)'
            }),
            'tipo_proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NIT del proveedor'
            }),
            'registro_comercio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de registro comercial'
            }),
            'licencia_funcionamiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de licencia'
            }),
            'contacto_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto principal'
            }),
            'cargo_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo del contacto'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+591 2 1234567'
            }),
            'telefono_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono alternativo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@proveedor.com'
            }),
            'email_secundario': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo.alternativo@proveedor.com'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.proveedor.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departamento'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Bolivia'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'condiciones_pago': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 30 días, Contado, etc.'
            }),
            'dias_credito': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '365'
            }),
            'descuento_general': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'moneda_principal': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('BOB', 'Bolivianos (BOB)'),
                ('USD', 'Dólares (USD)'),
                ('EUR', 'Euros (EUR)'),
            ]),
            'limite_credito': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'calificacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '5',
                'step': '0.1'
            }),
            'tiempo_entrega_promedio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '365'
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ISO 9001, API, ASME, etc.'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_ultima_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultima_evaluacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
            'notas_internas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas internas (no visibles para el proveedor)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer obligatorios los campos esenciales
        self.fields['nombre'].required = True
        self.fields['tipo_proveedor'].required = True
        self.fields['categoria'].required = True
        self.fields['contacto_principal'].required = True
        self.fields['telefono'].required = True
        self.fields['email'].required = True
        self.fields['direccion'].required = True
        self.fields['ciudad'].required = True
        self.fields['departamento'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar que no existe otro proveedor con el mismo email
            queryset = Proveedor.objects.filter(email=email)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un proveedor con este email.')
        return email

    def clean_nit(self):
        nit = self.cleaned_data.get('nit')
        if nit:
            # Verificar que no existe otro proveedor con el mismo NIT
            queryset = Proveedor.objects.filter(nit=nit)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError('Ya existe un proveedor con este NIT.')
        return nit

    def clean_calificacion(self):
        calificacion = self.cleaned_data.get('calificacion')
        if calificacion is not None:
            if calificacion < 0 or calificacion > 5:
                raise forms.ValidationError('La calificación debe estar entre 0 y 5.')
        return calificacion

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar fechas
        fecha_ultima_compra = cleaned_data.get('fecha_ultima_compra')
        fecha_ultima_evaluacion = cleaned_data.get('fecha_ultima_evaluacion')
        
        if fecha_ultima_compra and fecha_ultima_compra > date.today():
            raise forms.ValidationError({
                'fecha_ultima_compra': 'La fecha de última compra no puede ser futura.'
            })
        
        if fecha_ultima_evaluacion and fecha_ultima_evaluacion > date.today():
            raise forms.ValidationError({
                'fecha_ultima_evaluacion': 'La fecha de última evaluación no puede ser futura.'
            })
        
        return cleaned_data