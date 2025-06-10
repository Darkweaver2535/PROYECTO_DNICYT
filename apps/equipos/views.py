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
from weasyprint import HTML, CSS
from django.conf import settings
import os

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
        return context

class EquipoUpdateView(UpdateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'sistema_interno/editar_equipo.html'
    context_object_name = 'equipo'
    success_url = reverse_lazy('equipos:equipo-lista')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'El equipo "{form.instance.nombre}" ha sido actualizado exitosamente.'
        )
        return super().form_valid(form)

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
    
    # Renderizar el template HTML
    html_string = render_to_string('sistema_interno/ficha_pdf_template.html', {
        'equipo': equipo,
        'completitud': equipo.calcular_completitud_ficha(),
    })
    
    # Convertir a PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Crear la respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ficha_Tecnica_{equipo.codigo_interno}.pdf"'
    
    return response

@login_required
def imprimir_ficha_view(request, pk):
    # Misma funcionalidad pero para mostrar en el navegador (inline)
    equipo = get_object_or_404(Equipo, pk=pk)
    
    html_string = render_to_string('sistema_interno/ficha_pdf_template.html', {
        'equipo': equipo,
        'completitud': equipo.calcular_completitud_ficha(),
    })
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Ficha_Tecnica_{equipo.codigo_interno}.pdf"'
    
    return response

@login_required
def ficha_detallada_view(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    context = {
        'equipo': equipo,
    }
    return render(request, 'sistema_interno/ficha_detallada.html', context)