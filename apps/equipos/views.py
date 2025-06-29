from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Equipo
from .forms import EquipoForm, FichaTecnicaForm
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
# COMENTAR TEMPORALMENTE ESTAS LÍNEAS:
# from weasyprint import HTML, CSS
from django.conf import settings
import os
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class EquipoListView(ListView):
    model = Equipo
    template_name = 'sistema_interno/inventario_equipos.html'
    context_object_name = 'equipos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        seccion = self.request.GET.get('seccion')
        
        if seccion:
            queryset = queryset.filter(seccion=seccion)
        
        return queryset.order_by('-fecha_ingreso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar estadísticas dinámicas
        all_equipos = Equipo.objects.all()
        seccion_filtro = self.request.GET.get('seccion')
        
        if seccion_filtro:
            equipos_filtrados = all_equipos.filter(seccion=seccion_filtro)
        else:
            equipos_filtrados = all_equipos
        
        context.update({
            'total_equipos': equipos_filtrados.count(),
            'equipos_operativos': equipos_filtrados.filter(estado='OPERATIVO').count(),
            'equipos_mantenimiento': equipos_filtrados.filter(estado='MANTENIMIENTO').count(),
            'equipos_fuera_servicio': equipos_filtrados.filter(estado='FUERA_SERVICIO').count(),
            'seccion_actual': seccion_filtro,
        })
        
        return context

class EquipoDetailView(DetailView):
    model = Equipo
    template_name = 'sistema_interno/detalle.html'
    context_object_name = 'equipo'

class EquipoCreateView(CreateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'sistema_interno/crear.html'
    success_url = reverse_lazy('equipos:equipo-lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        
        # Comprobar si hay materiales y herramientas disponibles
        form = self.get_form()
        context['materiales_disponibles'] = getattr(form, 'materiales_disponibles', False)
        context['herramientas_disponibles'] = getattr(form, 'herramientas_disponibles', False)
        
        return context
    
    def form_valid(self, form):
        # Guardar los valores seleccionados de los campos ManyToMany
        materiales = form.cleaned_data.get('materiales_necesarios', [])
        herramientas = form.cleaned_data.get('herramientas_necesarias', [])
        
        # Eliminar temporalmente del cleaned_data para evitar el error
        form.cleaned_data.pop('materiales_necesarios', None)
        form.cleaned_data.pop('herramientas_necesarias', None)
        
        # Primero guardar el equipo sin las relaciones ManyToMany
        self.object = form.save()
        
        # Después de guardar, añadir las relaciones ManyToMany
        if materiales:
            self.object.materiales_necesarios.set(materiales)
            
        if herramientas:
            self.object.herramientas_necesarias.set(herramientas)
        
        # Calcular completitud ahora que tenemos el objeto guardado
        self.object.calcular_completitud_ficha()
        self.object.save()
        
        return super().form_valid(form)

class EquipoUpdateView(UpdateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'sistema_interno/editar_equipo.html'
    context_object_name = 'equipo'
    
    def get_success_url(self):
        return reverse('equipos:equipo-detalle', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context
    
    def form_valid(self, form):
        print(f"DEBUG: Formulario válido - {form.cleaned_data}")  # Debug
        messages.success(
            self.request, 
            f'El equipo "{form.instance.nombre}" ha sido actualizado exitosamente.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(f"DEBUG: Formulario inválido - {form.errors}")  # Debug
        messages.error(
            self.request, 
            'Error al actualizar el equipo. Por favor revise los campos marcados.'
        )
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        print(f"DEBUG: POST data recibido - {request.POST}")  # Debug
        return super().post(request, *args, **kwargs)

class EquipoDeleteView(DeleteView):
    model = Equipo
    success_url = reverse_lazy('equipos:equipo-lista')
    
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        messages.success(
            request, 
            f'El equipo "{self.object.nombre}" ha sido eliminado exitosamente.'
        )
        self.object.delete()
        return redirect(success_url)

def generar_qr_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    url = request.build_absolute_uri(reverse('equipos:equipo-detalle', kwargs={'pk': equipo.pk}))
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    filename = f'equipo_{equipo.pk}_qr.png'
    equipo.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)
    return redirect('equipos:equipo-detalle', pk=equipo.pk)

@login_required
def codigo_qr_view(request):
    equipos = Equipo.objects.all().order_by('-fecha_ingreso')
    
    total_equipos = equipos.count()
    equipos_con_qr = equipos.exclude(qr_code='').exclude(qr_code__isnull=True).count()
    equipos_sin_qr = total_equipos - equipos_con_qr
    
    context = {
        'equipos': equipos,
        'total_equipos': total_equipos,
        'equipos_con_qr': equipos_con_qr,
        'equipos_sin_qr': equipos_sin_qr,
    }
    
    return render(request, 'sistema_interno/codigo_qr.html', context)

@login_required
def fichas_tecnicas_view(request):
    equipos = Equipo.objects.all().order_by('-fecha_ingreso')
    
    # Calcular completitud para cada equipo
    for equipo in equipos:
        equipo.completitud_porcentaje = equipo.calcular_completitud_ficha()
    
    # Estadísticas
    total_equipos = equipos.count()
    fichas_completas = equipos.filter(ficha_tecnica_completa=True).count()
    fichas_pendientes = total_equipos - fichas_completas
    
    context = {
        'equipos': equipos,
        'total_equipos': total_equipos,
        'fichas_completas': fichas_completas,
        'fichas_pendientes': fichas_pendientes,
    }
    
    return render(request, 'sistema_interno/fichas_tecnicas.html', context)

@login_required
def crear_ficha_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug
        print("FILES data:", request.FILES)  # Debug
        
        form = FichaTecnicaForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            print("Form is valid")  # Debug
            equipo_actualizado = form.save()
            
            # Forzar la actualización del estado de la ficha
            equipo_actualizado.save()  # Esto activará el método save() personalizado
            
            messages.success(request, f'Ficha técnica creada exitosamente para {equipo_actualizado.nombre}')
            return redirect('equipos:fichas-tecnicas')
        else:
            print("Form errors:", form.errors)  # Debug
            messages.error(request, 'Error al guardar la ficha técnica. Por favor revise los campos.')
    else:
        form = FichaTecnicaForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'accion': 'crear'
    }
    return render(request, 'sistema_interno/ficha_form.html', context)

@login_required
def editar_ficha_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug
        print("FILES data:", request.FILES)  # Debug
        
        form = FichaTecnicaForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            print("Form is valid")  # Debug
            equipo_actualizado = form.save()
            
            # Forzar la actualización del estado de la ficha
            equipo_actualizado.save()  # Esto activará el método save() personalizado
            
            messages.success(request, f'Ficha técnica actualizada exitosamente para {equipo_actualizado.nombre}')
            return redirect('equipos:fichas-tecnicas')
        else:
            print("Form errors:", form.errors)  # Debug
            messages.error(request, 'Error al actualizar la ficha técnica. Por favor revise los campos.')
    else:
        form = FichaTecnicaForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'accion': 'editar'
    }
    return render(request, 'sistema_interno/ficha_form.html', context)

@login_required
def exportar_ficha_pdf_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    # Crear respuesta PDF con ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ficha_Tecnica_{equipo.codigo_interno}.pdf"'
    
    # Crear el PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph(f"Ficha Técnica - {equipo.nombre}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Datos básicos del equipo
    data = [
        ['Campo', 'Valor'],
        ['Código Interno', equipo.codigo_interno],
        ['Nombre', equipo.nombre],
        ['Modelo', equipo.modelo or '---'],
        ['Fabricante', equipo.fabricante or '---'],
        ['Año', str(equipo.año_fabricacion) if equipo.año_fabricacion else '---'],
        ['Estado', equipo.get_estado_display()],
        ['Sección', equipo.get_seccion_display()],
    ]
    
    # Añadir datos eléctricos
    if equipo.voltaje:
        data.append(['Voltaje', equipo.voltaje])
    if equipo.amperaje:
        data.append(['Amperaje', equipo.amperaje])
    if equipo.fases:
        data.append(['Tipo de Alimentación', equipo.get_fases_display()])
    if equipo.frecuencia:
        data.append(['Frecuencia', equipo.frecuencia])
    if equipo.consumo_electrico:
        data.append(['Consumo Eléctrico', f"{equipo.consumo_electrico} kW"])
        
    # Tabla principal
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Añadir sección de materiales y herramientas
    subtitle = Paragraph("Materiales y Herramientas Necesarios", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 10))
    
    # Tabla de materiales
    if equipo.materiales_necesarios.exists():
        story.append(Paragraph("Materiales:", styles['Heading3']))
        story.append(Spacer(1, 6))
        materiales_data = [['Nombre', 'Código', 'Stock Actual', 'Estado']]
        
        for material in equipo.materiales_necesarios.all():
            materiales_data.append([
                material.nombre,
                material.codigo,
                str(material.stock_actual),
                material.get_estado_display()
            ])
        
        materiales_table = Table(materiales_data, colWidths=[2.5*inch, inch, inch, 1.5*inch])
        materiales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(materiales_table)
        story.append(Spacer(1, 15))
    else:
        story.append(Paragraph("Materiales: No se han especificado", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Tabla de herramientas
    if equipo.herramientas_necesarias.exists():
        story.append(Paragraph("Herramientas:", styles['Heading3']))
        story.append(Spacer(1, 6))
        herramientas_data = [['Nombre', 'Código', 'Estado']]
        
        for herramienta in equipo.herramientas_necesarias.all():
            herramientas_data.append([
                herramienta.nombre,
                herramienta.codigo,
                herramienta.get_estado_display()
            ])
        
        herramientas_table = Table(herramientas_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        herramientas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(herramientas_table)
    else:
        story.append(Paragraph("Herramientas: No se han especificado", styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    
    return response

@login_required
def imprimir_ficha_view(request, pk):
    # TEMPORALMENTE DESHABILITAR ESTA FUNCIÓN
    equipo = get_object_or_404(Equipo, pk=pk)
    messages.error(request, 'La funcionalidad de impresión PDF está temporalmente deshabilitada.')
    return redirect('equipos:fichas-tecnicas')
    
    # TODO: Habilitar cuando WeasyPrint esté configurado
    # # Misma funcionalidad pero para mostrar en el navegador (inline)
    # equipo = get_object_or_404(Equipo, pk=pk)
    # 
    # html_string = render_to_string('sistema_interno/ficha_pdf_template.html', {
    #     'equipo': equipo,
    #     'completitud': equipo.calcular_completitud_ficha(),
    # })
    # 
    # html = HTML(string=html_string)
    # pdf = html.write_pdf()
    # 
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = f'inline; filename="Ficha_Tecnica_{equipo.codigo_interno}.pdf"'
    # 
    # return response

@login_required
def ficha_detallada_view(request, pk):
    # Usar select_related y prefetch_related para optimizar consultas
    equipo = get_object_or_404(
        Equipo.objects.prefetch_related('materiales_necesarios', 'herramientas_necesarias'),
        pk=pk
    )
    
    # Calcular completitud explícitamente para asegurar que esté actualizada
    completitud = equipo.calcular_completitud_ficha()
    
    context = {
        'equipo': equipo,
        'completitud': completitud,
        'titulo': f'Ficha Técnica - {equipo.nombre}'
    }
    return render(request, 'sistema_interno/ficha_detallada.html', context)

# Ejemplo de uso de timezone
fecha_creacion = timezone.make_aware(datetime(2025, 4, 1))