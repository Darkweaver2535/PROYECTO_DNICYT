from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Equipo
from .forms import EquipoForm
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime

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
    template_name = 'sistema_interno/detalle.html'  # Cambiado para usar tu ubicación personalizada
    context_object_name = 'equipo'

class EquipoCreateView(CreateView):
    model = Equipo
    template_name = 'sistema_interno/crear.html'
    fields = [
        'codigo_interno', 'nombre', 'modelo', 'serie', 'fabricante', 'año_fabricacion',
        'potencia', 'capacidad', 'ubicacion_fisica', 'seccion', 'tipo_equipo',
        'estado', 'foto', 'responsable', 'observaciones',
        'udb_unidad', 'udb_numero'  # asegúrate de incluir estos campos
    ]
    success_url = reverse_lazy('equipos:equipo-lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context

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
def mi_vista(request):
    messages.success(request, '¡Inicio de sesión exitoso!')
    messages.error(request, 'Usuario o contraseña incorrectos')

def mi_ajax_view(request):
    return JsonResponse({'success': True, 'message': 'OK'})

def crear_equipo(request):
    form = EquipoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('equipos:equipo-lista')
    context = {
        'form': form,
        'current_year': datetime.now().year,
    }
    return render(request, 'sistema_interno/crear.html', context)

from datetime import datetime
def tu_vista_crear_equipo(request):
    # ...
    context = {
        'form': form,
        'current_year': datetime.now().year,
        # ...
    }
    return render(request, 'sistema_interno/crear.html', context)

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
        # Redirigir directamente a la eliminación sin mostrar template
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

@login_required
def codigo_qr_view(request):
    """
    Vista para mostrar todos los códigos QR de los equipos en formato galería
    """
    equipos = Equipo.objects.all().order_by('-fecha_ingreso')
    
    # Estadísticas para el header
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