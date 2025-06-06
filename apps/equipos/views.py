from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Equipo
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime

class EquipoListView(ListView):
    model = Equipo
    template_name = 'sistema_interno/inventario_equipos.html'  # Cambiado para usar tu ubicación personalizada
    context_object_name = 'equipos'
    paginate_by = 10

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
    fields = '__all__'  # O especifica los campos que quieres editar
    template_name = 'sistema_interno/editar.html'
    success_url = reverse_lazy('equipos:equipo-lista')

class EquipoDeleteView(DeleteView):
    model = Equipo
    template_name = 'sistema_interno/eliminar.html'
    success_url = reverse_lazy('equipos:equipo-lista')