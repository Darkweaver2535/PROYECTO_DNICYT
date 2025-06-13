from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import CursoTaller, CategoriaCapacitacion, InscripcionCurso, DocumentoTecnico, ValoracionDocumento
import re

# ✅ FORMULARIOS ESPECÍFICOS PARA DOCUMENTOS TÉCNICOS

class DocumentoTecnicoForm(forms.ModelForm):
    class Meta:
        model = DocumentoTecnico
        fields = [
            'titulo', 'descripcion', 'tipo', 'categoria', 'archivo_principal',
            'formato', 'contenido_html', 'resumen_ejecutivo', 'palabras_clave',
            'autor_documento', 'revisor', 'version', 'dificultad', 'confidencialidad',
            'fecha_creacion_documento', 'fecha_revision', 'fecha_vencimiento',
            'estado', 'requiere_actualizacion', 'es_obligatorio',
            'objetivos', 'aplicacion', 'prerequisitos', 'documentos_relacionados'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'documento-form-control',
                'placeholder': 'Título del documento técnico'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del contenido del documento...'
            }),
            'tipo': forms.Select(attrs={'class': 'documento-form-select'}),
            'categoria': forms.Select(attrs={
                'class': 'documento-form-select',
                'data-placeholder': 'Seleccione una categoría'
            }),
            'archivo_principal': forms.FileInput(attrs={
                'class': 'documento-form-control',
                'accept': '.pdf,.docx,.xlsx,.pptx,.txt,.dwg,.zip'
            }),
            'formato': forms.Select(attrs={'class': 'documento-form-select'}),
            'contenido_html': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 6,
                'placeholder': 'Contenido HTML renderizable (opcional)...'
            }),
            'resumen_ejecutivo': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 3,
                'placeholder': 'Resumen ejecutivo del documento...'
            }),
            'palabras_clave': forms.TextInput(attrs={
                'class': 'documento-form-control',
                'placeholder': 'palabra1, palabra2, palabra3...'
            }),
            'autor_documento': forms.TextInput(attrs={
                'class': 'documento-form-control',
                'placeholder': 'Autor/es del documento'
            }),
            'revisor': forms.TextInput(attrs={
                'class': 'documento-form-control',
                'placeholder': 'Revisor o aprobador (opcional)'
            }),
            'version': forms.TextInput(attrs={
                'class': 'documento-form-control',
                'placeholder': '1.0'
            }),
            'dificultad': forms.Select(attrs={'class': 'documento-form-select'}),
            'confidencialidad': forms.Select(attrs={'class': 'documento-form-select'}),
            'fecha_creacion_documento': forms.DateInput(attrs={
                'class': 'documento-form-control',
                'type': 'date'
            }),
            'fecha_revision': forms.DateInput(attrs={
                'class': 'documento-form-control',
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'documento-form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={'class': 'documento-form-select'}),
            'requiere_actualizacion': forms.CheckboxInput(attrs={'class': 'documento-form-check'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'documento-form-check'}),
            'objetivos': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 3,
                'placeholder': 'Un objetivo por línea...'
            }),
            'aplicacion': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 3,
                'placeholder': 'Áreas donde se aplica este documento...'
            }),
            'prerequisitos': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 3,
                'placeholder': 'Un prerequisito por línea...'
            }),
            'documentos_relacionados': forms.SelectMultiple(attrs={
                'class': 'documento-form-select-multiple',
                'size': 5
            }),
        }
        
        labels = {
            'titulo': 'Título del Documento',
            'descripcion': 'Descripción',
            'tipo': 'Tipo de Documento',
            'categoria': 'Categoría',
            'archivo_principal': 'Archivo Principal',
            'formato': 'Formato del Archivo',
            'contenido_html': 'Contenido Web (HTML)',
            'resumen_ejecutivo': 'Resumen Ejecutivo',
            'palabras_clave': 'Palabras Clave',
            'autor_documento': 'Autor del Documento',
            'revisor': 'Revisor/Aprobador',
            'version': 'Versión',
            'dificultad': 'Nivel de Complejidad',
            'confidencialidad': 'Nivel de Confidencialidad',
            'fecha_creacion_documento': 'Fecha de Creación',
            'fecha_revision': 'Fecha de Revisión',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'estado': 'Estado del Documento',
            'requiere_actualizacion': 'Requiere Actualización',
            'es_obligatorio': 'Lectura Obligatoria',
            'objetivos': 'Objetivos',
            'aplicacion': 'Área de Aplicación',
            'prerequisitos': 'Prerequisitos',
            'documentos_relacionados': 'Documentos Relacionados',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar categorías activas
        self.fields['categoria'].queryset = CategoriaCapacitacion.objects.filter(
            activo=True
        ).order_by('orden', 'nombre')
        
        # Filtrar documentos relacionados (excluir el actual si está editando)
        documentos_qs = DocumentoTecnico.objects.filter(estado='publicado')
        if self.instance.pk:
            documentos_qs = documentos_qs.exclude(pk=self.instance.pk)
        self.fields['documentos_relacionados'].queryset = documentos_qs
        
        self.fields['categoria'].empty_label = "-- Seleccione una categoría --"
    
    def clean_archivo_principal(self):
        archivo = self.cleaned_data.get('archivo_principal')
        if archivo:
            # Validar tamaño del archivo (50MB máximo)
            if archivo.size > 50 * 1024 * 1024:  # 50MB
                raise ValidationError('El archivo no puede superar los 50MB.')
            
            # Validar extensión según el formato seleccionado
            formato = self.cleaned_data.get('formato')
            if formato:
                extension = archivo.name.split('.')[-1].lower()
                if formato != extension:
                    raise ValidationError(f'El archivo debe tener extensión .{formato}')
        
        return archivo
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_creacion = cleaned_data.get('fecha_creacion_documento')
        fecha_revision = cleaned_data.get('fecha_revision')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        # Validar fechas lógicas
        if fecha_creacion and fecha_revision:
            if fecha_revision < fecha_creacion:
                raise ValidationError({
                    'fecha_revision': 'La fecha de revisión no puede ser anterior a la fecha de creación.'
                })
        
        if fecha_vencimiento and fecha_creacion:
            if fecha_vencimiento < fecha_creacion:
                raise ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento no puede ser anterior a la fecha de creación.'
                })
        
        return cleaned_data

class FiltrosDocumentosForm(forms.Form):
    ORDENAR_CHOICES = [
        ('', 'Ordenar por...'),
        ('-fecha_modificacion', 'Más recientes'),
        ('fecha_modificacion', 'Más antiguos'),
        ('titulo', 'Título A-Z'),
        ('-titulo', 'Título Z-A'),
        ('-vistas', 'Más vistos'),
        ('-descargas', 'Más descargados'),
        ('version', 'Versión'),
        ('fecha_vencimiento', 'Próximos a vencer'),
    ]
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'documento-form-control',
            'placeholder': 'Buscar documentos técnicos...'
        })
    )
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaCapacitacion.objects.filter(activo=True),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + DocumentoTecnico.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    formato = forms.ChoiceField(
        choices=[('', 'Todos los formatos')] + DocumentoTecnico.FORMATO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    dificultad = forms.ChoiceField(
        choices=[('', 'Todas las dificultades')] + DocumentoTecnico.DIFICULTAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    confidencialidad = forms.ChoiceField(
        choices=[('', 'Todos los niveles')] + DocumentoTecnico.CONFIDENCIALIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + DocumentoTecnico.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    ordenar = forms.ChoiceField(
        choices=ORDENAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'documento-form-select'})
    )
    
    solo_obligatorios = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'documento-form-check'})
    )
    
    solo_vigentes = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'documento-form-check'})
    )

class ValoracionDocumentoForm(forms.ModelForm):
    class Meta:
        model = ValoracionDocumento
        fields = ['valoracion', 'comentario']
        
        widgets = {
            'valoracion': forms.Select(
                choices=[(i, f'{i} estrellas') for i in range(1, 6)],
                attrs={'class': 'documento-form-select'}
            ),
            'comentario': forms.Textarea(attrs={
                'class': 'documento-form-control',
                'rows': 3,
                'placeholder': 'Comparta su opinión sobre este documento...'
            })
        }

# ✅ MANTENER FORMULARIOS ORIGINALES DE CURSOS/TALLERES
class CursoTallerForm(forms.ModelForm):
    class Meta:
        model = CursoTaller
        fields = [
            'titulo', 'descripcion', 'tipo', 'categoria', 'instructor',
            'duracion_horas', 'duracion_minutos', 'dificultad', 'modalidad',
            'enlace_youtube', 'objetivos', 'requisitos', 'contenido_temas',
            'fecha_programada', 'fecha_limite_inscripcion', 'max_participantes',
            'certificacion_disponible', 'puntos_capacitacion', 'estado',
            'destacado', 'etiquetas'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del curso o taller'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del contenido...'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Seleccione una categoría'
            }),
            'instructor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del instructor'
            }),
            'duracion_horas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'value': 1
            }),
            'duracion_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 59,
                'value': 0
            }),
            'dificultad': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'enlace_youtube': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=VIDEO_ID'
            }),
            'objetivos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Un objetivo por línea...'
            }),
            'requisitos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Un requisito por línea...'
            }),
            'contenido_temas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Un tema por línea...'
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_limite_inscripcion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'max_participantes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 20
            }),
            'puntos_capacitacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 1
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'etiquetas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'etiqueta1, etiqueta2, etiqueta3...'
            }),
            'certificacion_disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'tipo': 'Tipo de contenido',
            'categoria': 'Categoría',
            'instructor': 'Instructor/Facilitador',
            'duracion_horas': 'Duración (horas)',
            'duracion_minutos': 'Minutos adicionales',
            'dificultad': 'Nivel de dificultad',
            'modalidad': 'Modalidad',
            'enlace_youtube': 'Enlace de YouTube',
            'objetivos': 'Objetivos de aprendizaje',
            'requisitos': 'Requisitos previos',
            'contenido_temas': 'Temas del contenido',
            'fecha_programada': 'Fecha programada',
            'fecha_limite_inscripcion': 'Límite de inscripción',
            'max_participantes': 'Máximo de participantes',
            'certificacion_disponible': 'Otorga certificación',
            'puntos_capacitacion': 'Puntos de capacitación',
            'estado': 'Estado de publicación',
            'destacado': 'Contenido destacado',
            'etiquetas': 'Etiquetas (separadas por comas)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ FILTRAR SOLO CATEGORÍAS ACTIVAS Y ORDENAR
        self.fields['categoria'].queryset = CategoriaCapacitacion.objects.filter(
            activo=True
        ).order_by('orden', 'nombre')
        
        # Mejorar el label del select de categoría
        self.fields['categoria'].empty_label = "-- Seleccione una categoría --"
        
        # Agregar ayuda contextual
        self.fields['categoria'].help_text = "Si no encuentra la categoría adecuada, contacte al administrador"

    def clean_enlace_youtube(self):
        enlace = self.cleaned_data.get('enlace_youtube')
        if enlace:
            # Validar que sea una URL de YouTube válida
            youtube_patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
                r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            ]
            
            valid_youtube = False
            for pattern in youtube_patterns:
                if re.search(pattern, enlace):
                    valid_youtube = True
                    break
            
            if not valid_youtube:
                raise ValidationError('Por favor, ingresa una URL válida de YouTube.')
        
        return enlace
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_programada = cleaned_data.get('fecha_programada')
        fecha_limite = cleaned_data.get('fecha_limite_inscripcion')
        
        # Validar fechas
        if fecha_programada and fecha_limite:
            if fecha_limite >= fecha_programada:
                raise ValidationError({
                    'fecha_limite_inscripcion': 'La fecha límite debe ser anterior a la fecha programada.'
                })
        
        return cleaned_data

class CategoriaCapacitacionForm(forms.ModelForm):
    class Meta:
        model = CategoriaCapacitacion
        fields = ['nombre', 'descripcion', 'color_hex', 'icono', 'orden', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría...'
            }),
            'color_hex': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'icono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ej: bi-mortarboard'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FiltrosCursosForm(forms.Form):
    ORDENAR_CHOICES = [
        ('', 'Ordenar por...'),
        ('-fecha_creacion', 'Más recientes'),
        ('fecha_creacion', 'Más antiguos'),
        ('titulo', 'Título A-Z'),
        ('-titulo', 'Título Z-A'),
        ('-vistas', 'Más vistos'),
        ('duracion_horas', 'Duración (menor)'),
        ('-duracion_horas', 'Duración (mayor)'),
    ]
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar cursos o talleres...'
        })
    )
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaCapacitacion.objects.filter(activo=True),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + CursoTaller.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    dificultad = forms.ChoiceField(
        choices=[('', 'Todas las dificultades')] + CursoTaller.DIFICULTAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    modalidad = forms.ChoiceField(
        choices=[('', 'Todas las modalidades')] + CursoTaller.MODALIDAD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + CursoTaller.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ordenar = forms.ChoiceField(
        choices=ORDENAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    solo_destacados = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class InscripcionCursoForm(forms.ModelForm):
    class Meta:
        model = InscripcionCurso
        fields = ['comentario']
        
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Por qué te interesa este curso? (opcional)'
            })
        }